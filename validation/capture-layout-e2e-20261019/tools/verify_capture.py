"""Validate an already-running MoE server. Never starts or changes the server."""

from __future__ import annotations

import argparse
import ast
import base64
from collections import Counter, defaultdict, deque
import concurrent.futures
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.request

from capture_expectations import LAYOUT, SELECTION, audit_expectations

MARKERS = ("Ascend routed capture prepare:", "Routed-experts capture layer=", "MoE comm method selected:", SELECTION, LAYOUT)


def wait_for_capture_logs(path, offset, quiet_seconds=1.0, timeout=30):
    """DP workers may finish synchronized dummy steps after HTTP responses."""
    deadline = time.monotonic() + timeout
    last_activity = time.monotonic()
    with path.open("rb") as stream:
        stream.seek(offset)
        while time.monotonic() < deadline:
            chunk = stream.read().decode(errors="replace")
            if chunk and any(marker in chunk for marker in MARKERS):
                last_activity = time.monotonic()
            if time.monotonic() - last_activity >= quiet_seconds:
                return
            time.sleep(0.2)


def branch_walkthrough(text):
    """Collapse repeated layer logs; do not infer request identity from row counts."""
    groups = {}
    pending = defaultdict(deque)
    for line in text.splitlines():
        match = re.search(
            r"Ascend routed capture prepare: layer=(\S+) dp=(\d+) tp=(\d+) sp=(True|False) "
            r"graph=(\S+) comm=(\w+) rows=(\d+) shards=(.*?) ranges=(\(.*\))\s*$", line,
        )
        if match:
            layer, d, t, sp, graph, comm, rows, shards, ranges = match.groups()
            layer_id = re.search(r"(?:^|\.)layers\.(\d+)(?:\.|$)", layer)
            if layer_id is None:
                continue
            key = (d, t, sp, graph, comm, rows, shards, ranges)
            entry = groups.setdefault(key, {"prepare": 0, "paired": 0, "sample": []})
            entry["prepare"] += 1
            pending[(d, t, layer_id.group(1))].append((key, line))
            continue
        match = re.search(r"Routed-experts capture layer=(\d+) dp_rank=(\d+) tp_rank=(\d+) .*?rows=(\d+) rows=(\d+)", line)
        if match:
            layer, d, t, _, output_rows = match.groups()
            queue = pending[(d, t, layer)]
            if queue:
                key, prepare_line = queue.popleft()
                entry = groups[key]
                entry["paired"] += 1
                if not entry["sample"]:
                    entry["sample"] = [prepare_line, line]
                    entry["output_rows"] = output_rows
    lines = ["# 分支与布局摘要", "",
             "仅汇总本轮新增日志；同一布局跨层重复折叠。没有 request ID，不能仅凭行数将日志严格归属于某个请求或 prefill/decode 阶段。", "",
             "| DP/TP | SP/图模式 | 通信方案 | router 输入行 | capture 的 TP 分片 | 选取范围 | prepare/配对次数 |",
             "|---|---|---|---:|---|---|---:|"]
    for key, entry in groups.items():
        d, t, sp, graph, comm, rows, shards, ranges = key
        lines.append(f"| {d}/{t} | {sp}/{graph} | {comm} | {rows} | `{shards}` | `{ranges}` | {entry['prepare']}/{entry['paired']} |")
    for number, (key, entry) in enumerate(groups.items(), 1):
        d, t, sp, graph, comm, rows, shards, ranges = key
        spans = ast.literal_eval(ranges)
        sizes = ast.literal_eval(shards)
        lines += ["", f"## 布局 {number}：DP{d}/TP{t}，{comm}，输入 {rows} 行", ""]
        if comm == "ALLGATHER":
            path = "_prepare_with_ep_group" if sp == "True" else "_prepare_with_dp_group"
            lines.append(f"按当前源码与 SP 标志对应：PrepareAndFinalizeWithAllGather.prepare → {path}。")
        else:
            lines.append(f"观察到 {comm}；请对应检查该通信方案的 prepare 实现。")
        if sizes:
            lines.append(f"layout 要求 capture 在 TP 组收集分片 {sizes}，拼接容量 {sum(sizes)} 行。")
        else:
            lines.append("layout 不要求 capture 额外做 TP all-gather；这不表示 MoE 其他阶段没有通信。")
        lines.append("随后依次选取：" + "；".join(f"从第 {start} 行取 {count} 行" for start, count in spans) + "。")
        lines.append(f"layout 要求输出 {sum(count for _, count in spans)} 行；代表性 capture 日志输出 {entry.get('output_rows', '未观察到')} 行。")
        lines += ["", "代表性日志（其他层的同类日志已折叠）：", "", "```text", *entry["sample"], "```"]
    if not groups:
        lines += ["", "没有可解析的 prepare 日志，无法判断执行分支。"]
    lines += ["", "以上用于追踪执行路径；整体 PASS/FAIL 请看 report.md。行数匹配不能独立证明 token 顺序或专家编号与参考实现一致。"]
    return "\n".join(lines) + "\n"


def audit_log(text, expected_methods, expected_sp, dp, tp):
    errors, missing = [], []
    prepared = defaultdict(deque)
    methods, ranks, sp_values = Counter(), set(), set()
    paired = 0
    uneven = internal_padding = False
    for line in text.splitlines():
        if "Ascend routed capture prepare:" in line:
            match = re.search(
                r"layer=(\S+) dp=(\d+) tp=(\d+) sp=(True|False).*?comm=(\w+) "
                r"rows=(\d+) shards=(.*?) ranges=(\(.*\))\s*$", line,
            )
            if not match:
                errors.append("Cannot parse prepare log: " + line)
                continue
            layer_name, d, t, sp, method, rows, shards, ranges = match.groups()
            layer = re.search(r"(?:^|\.)layers\.(\d+)(?:\.|$)", layer_name)
            if layer is None:
                missing.append("Cannot associate layer name: " + layer_name)
                continue
            d, t, rows = int(d), int(t), int(rows)
            shards, ranges = ast.literal_eval(shards), ast.literal_eval(ranges)
            methods[method] += 1
            if method not in expected_methods:
                errors.append(f"Unexpected communication branch: {method}")
            ranks.add((d, t))
            sp_values.add(sp == "True")
            if not (0 <= d < dp and 0 <= t < tp):
                errors.append(f"Unexpected rank dp={d} tp={t}")
            if shards and (len(shards) != tp or rows != shards[t]):
                errors.append(f"Input rows mismatch dp={d} tp={t}: rows={rows}, shards={shards}")
            capacity = sum(shards) if shards else rows
            if any(start < 0 or count < 0 or start + count > capacity for start, count in ranges):
                errors.append(f"Out-of-bounds ranges: {ranges}, capacity={capacity}")
            uneven |= bool(shards and len(set(shards)) > 1)
            positive = [(start, count) for start, count in ranges if count]
            internal_padding |= any(
                right[0] > left[0] + left[1] for left, right in zip(positive, positive[1:])
            )
            prepared[(d, t, int(layer.group(1)))].append((sum(count for _, count in ranges), rows))
        elif "Routed-experts capture layer=" in line:
            match = re.search(
                r"layer=(\d+) dp_rank=(\d+) tp_rank=(\d+) input_rows=(\d+) rows=(\d+)", line
            )
            if not match:
                missing.append("Capture log lacks rank/row fields")
                continue
            layer, d, t, input_rows, rows = map(int, match.groups())
            queue = prepared[(d, t, layer)]
            if not queue:
                missing.append(f"Capture has no matching prepare: dp={d} tp={t} layer={layer}")
                continue
            wanted, prepared_rows = queue.popleft()
            paired += 1
            if input_rows != prepared_rows:
                errors.append(f"Capture input rows={input_rows}, prepare router rows={prepared_rows}: dp={d} tp={t} layer={layer}")
            if rows != wanted:
                errors.append(f"Captured rows={rows}, layout selects {wanted}: dp={d} tp={t} layer={layer}")
    if not methods:
        missing.append("No prepare logs from this test run; enable capture DEBUG logging")
    if not paired:
        missing.append("No matched prepare/capture log pairs")
    if any(prepared.values()):
        missing.append("Some prepare logs have no matching capture log")
    for method in expected_methods:
        if method not in methods:
            missing.append(f"Requested communication branch not observed: {method}")
    if sp_values and sp_values != {expected_sp}:
        missing.append(f"Expected sp={expected_sp}, observed={sorted(sp_values)}")
    absent = sorted({(d, t) for d in range(dp) for t in range(tp)} - ranks)
    if absent:
        missing.append(f"Ranks not observed: {absent}")
    return {
        "errors": errors, "coverage_missing": sorted(set(missing)),
        "methods": dict(methods), "ranks": sorted(ranks), "matched_layer_calls": paired,
        "uneven_tp_shards_observed": uneven,
        "internal_padding_skip_observed": internal_padding,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Local checkpoint directory")
    parser.add_argument("--served-model", default="moe")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--log-file", required=True, type=Path, help="Live server log file")
    parser.add_argument("--dp", required=True, type=int)
    parser.add_argument("--tp", required=True, type=int)
    parser.add_argument("--sp", required=True, choices=("on", "off"))
    parser.add_argument("--expect-comm", required=True, help="Comma-separated required branches, e.g. MC2,ALLTOALL")
    parser.add_argument("--long-tokens", type=int, default=2049)
    parser.add_argument("--max-tokens", type=int, default=8)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reference-dir", type=Path, help="Optional earlier run with the same model and inputs")
    parser.add_argument("--scenario", type=Path, help="Independent expected runtime configuration; enables strict selection/layout checks")
    parser.add_argument("--require-uneven-shards", action="store_true")
    parser.add_argument("--require-internal-padding", action="store_true")
    parser.add_argument("--skip-general-concurrency", action="store_true", help="Use only controlled DP-targeted concurrent pairs")
    args = parser.parse_args(argv)
    if min(args.dp, args.tp, args.long_tokens, args.max_tokens) < 1:
        parser.error("Sizes must be positive")
    expected_methods = set(args.expect_comm.upper().split(","))
    if not expected_methods <= {"ALLGATHER", "ALLTOALL", "MC2", "FUSED_MC2"}:
        parser.error("Invalid --expect-comm")
    import numpy as np

    config = json.loads((Path(args.model) / "config.json").read_text())
    config = config.get("text_config", config)
    layers = config["num_hidden_layers"]
    experts = config.get("num_experts") or config.get("n_routed_experts") or config.get("num_local_experts")
    topk = config.get("num_experts_per_tok") or config.get("top_k_experts")
    if not experts or not topk:
        parser.error("Cannot read expert count/top-k from checkpoint config")
    plan = json.loads(args.scenario.read_text()) if args.scenario else None
    if plan is not None:
        required = {"dp", "tp", "sp", "ep", "ep_world", "lora", "fused", "policy", "capacity"}
        if required - plan.keys():
            parser.error(f"Scenario missing fields: {sorted(required - plan.keys())}")
        if (plan["dp"], plan["tp"], plan["sp"]) != (args.dp, args.tp, args.sp == "on"):
            parser.error("Scenario DP/TP/SP differs from command line")
        plan.update(experts=experts, topk=topk, layers=layers)
    out = args.output or Path("capture-results") / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out.mkdir(parents=True, exist_ok=False)
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(args.url + "/v1/models", timeout=10) as response:
        models = json.load(response)
    selected = [model for model in models["data"] if model["id"] == args.served_model]
    if not selected:
        raise RuntimeError(f"Server does not expose {args.served_model}")
    (out / "server-models.json").write_text(json.dumps(models, indent=2))
    log_stat = args.log_file.stat()
    log_offset = log_stat.st_size
    log_inode = log_stat.st_ino
    records, failures, reference_missing = [], [], []
    lock = threading.Lock()

    def request(case, length, token, dp_rank=None, barrier=None):
        body = {
            "model": args.served_model, "prompt": [token] * length,
            "max_tokens": args.max_tokens, "temperature": 0, "ignore_eos": True,
            "return_token_ids": True, "routed_experts_prompt_start": 0,
        }
        record = {"case": case, "requested_prompt_tokens": length, "config_hash": config_hash,
                  "input_hash": hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()}
        started = time.monotonic()
        try:
            if barrier is not None:
                barrier.wait(timeout=10)
            headers = {"Content-Type": "application/json"}
            if dp_rank is not None:
                headers["X-data-parallel-rank"] = str(dp_rank)
                record["target_dp_rank"] = dp_rank
            req = urllib.request.Request(args.url + "/v1/completions", json.dumps(body).encode(),
                                         headers)
            # One opener per thread; bypass http_proxy for local services.
            client = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with client.open(req, timeout=300) as response:
                payload = json.load(response)
                record["http"] = response.status
            (out / f"{case}.response.json").write_text(json.dumps(payload))
            choice = payload["choices"][0]
            encoded = choice.get("routed_experts")
            if not encoded:
                raise ValueError("Missing routed_experts")
            routes = np.load(io.BytesIO(base64.b64decode(encoded)), allow_pickle=False)
            generated = choice["token_ids"]
            prompt_tokens = payload["usage"]["prompt_tokens"]
            expected_shape = (prompt_tokens + len(generated) - 1, layers, topk)
            if routes.shape != expected_shape:
                raise ValueError(f"Route shape {routes.shape} != expected {expected_shape}")
            if prompt_tokens != length or len(generated) != args.max_tokens:
                raise ValueError(f"Unexpected prompt/generated lengths: {prompt_tokens}/{len(generated)}")
            if routes.dtype.kind not in "iu" or not np.all((routes >= 0) & (routes < experts)):
                raise ValueError(f"Invalid route dtype/IDs: {routes.dtype}")
            np.save(out / f"{case}.npy", routes, allow_pickle=False)
            record.update(status="PASS", shape=list(routes.shape), generated_ids=generated,
                          expert_min=int(routes.min()), expert_max=int(routes.max()), dtype=str(routes.dtype),
                          response_validated=True)
            if args.reference_dir:
                ref = json.loads((args.reference_dir / f"{case}.json").read_text())
                if ref.get("config_hash") != config_hash or ref.get("input_hash") != record["input_hash"]:
                    raise ValueError("Reference model config or request differs")
                if ref.get("generated_ids") != generated:
                    reference_missing.append(f"{case}: generated tokens differ; complete route comparison is not equivalent")
                    record["reference"] = "INCONCLUSIVE"
                else:
                    reference = np.load(args.reference_dir / f"{case}.npy", allow_pickle=False)
                    if reference.shape != routes.shape or not np.array_equal(reference, routes):
                        raise ValueError("Routing array differs from reference")
                    record["reference"] = "MATCH"
        except Exception as exc:
            record.update(status="FAIL", error=f"{type(exc).__name__}: {exc}")
            if isinstance(exc, urllib.error.HTTPError):
                record["response_error"] = exc.read().decode(errors="replace")
            with lock:
                failures.append(f"{case}: {record['error']}")
        record["seconds"] = round(time.monotonic() - started, 3)
        (out / f"{case}.json").write_text(json.dumps(record, indent=2))
        with lock:
            records.append(record)
            print(f"{record['status']} {case}: {record.get('shape', record.get('error'))}", flush=True)

    # Four serial requests cover short, uneven and large prefill; decode is included in each.
    cases = [("short-1", 1, 101), ("short-5", 5, 105),
             ("short-7", 7, 107), ("long", args.long_tokens, 201)]
    if plan is not None and plan["ep"] and plan["ep_world"] > 1 and not plan["lora"] and plan["fused"] == 0:
        boundary = sorted({max(1, plan["capacity"] - 1), plan["capacity"], plan["capacity"] + 1})
        cases.extend((f"boundary-{n}", n, 401 + i) for i, n in enumerate(boundary))
        plan["required_selector_tokens"] = boundary
    for case, length, token in cases:
        case_offset = args.log_file.stat().st_size
        request(case, length, token)
        if plan is not None:
            time.sleep(0.1)
            with args.log_file.open("rb") as stream:
                stream.seek(case_offset)
                case_text = stream.read().decode(errors="replace")
            (out / f"{case}.trace.log").write_text(case_text)
            # DP>1 can mix workers; global coverage remains checked after all requests.
            if args.dp == 1:
                case_plan = {key: value for key, value in plan.items() if key != "required_selector_tokens"}
                check = audit_expectations(case_text, case_plan)
                records[-1]["selection_layout"] = check
                (out / f"{case}.json").write_text(json.dumps(records[-1], indent=2))
                failures.extend(f"{case}: {error}" for error in check["errors"])
        if any(r["status"] == "FAIL" and not r.get("response_validated") for r in records):
            break  # EngineCore may have exited: preserve the first failure.
    response_failed = any(r["status"] == "FAIL" and not r.get("response_validated") for r in records)
    if args.dp > 1 and not response_failed and not args.skip_general_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            jobs = [pool.submit(request, f"concurrent-{n}", n, 300 + n) for n in (3, 7, 129, 385)]
            for job in jobs:
                job.result()
    response_failed = any(r["status"] == "FAIL" and not r.get("response_validated") for r in records)
    if args.dp > 1 and args.require_internal_padding and not response_failed:
        for round_id in range(3):
            barrier = threading.Barrier(2)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(request, f"small-dp{rank}-round{round_id}", length,
                                    501 + round_id * 2 + rank, rank, barrier)
                        for rank, length in ((0, 5), (1, 13))]
                for job in jobs:
                    job.result()
    wait_for_capture_logs(args.log_file, log_offset)
    current_stat = args.log_file.stat()
    if current_stat.st_ino != log_inode or current_stat.st_size < log_offset:
        text = ""
        log_problem = ["Server log rotated/truncated during test"]
    else:
        with args.log_file.open("rb") as f:
            f.seek(log_offset)
            text = f.read().decode(errors="replace")
        log_problem = []
    relevant = "\n".join(line for line in text.splitlines()
                           if any(marker in line for marker in MARKERS) or "ERROR" in line or "Traceback" in line)
    (out / "capture.log").write_text(relevant + "\n")
    (out / "branch-walkthrough.md").write_text(branch_walkthrough(text))
    audit = audit_log(text, expected_methods, args.sp == "on", args.dp, args.tp)
    strict = audit_expectations(text, plan) if plan is not None else None
    if strict is not None:
        audit["errors"].extend(strict["errors"])
        audit["coverage_missing"].extend(strict["coverage_missing"])
        for record in records:
            check = record.get("selection_layout")
            if check:
                audit["coverage_missing"].extend(f"{record['case']}: {value}" for value in check["coverage_missing"])
    audit["coverage_missing"].extend(log_problem + reference_missing)
    if args.require_uneven_shards and not audit["uneven_tp_shards_observed"]:
        audit["coverage_missing"].append("Uneven TP shards were not observed")
    if args.require_internal_padding and not audit["internal_padding_skip_observed"]:
        audit["coverage_missing"].append("Skipping internal padding was not observed")
    failures.extend(audit["errors"])
    status = "FAIL" if failures else "INCONCLUSIVE" if audit["coverage_missing"] else "PASS"
    report = {"status": status, "scope": "Response invariants and logged layout consistency; token ownership equivalence needs a reference run",
              "arguments": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
              "requests": sorted(records, key=lambda r: r["case"]), "log_audit": audit, "failures": failures}
    report["selection_layout_audit"] = strict
    if strict is not None:
        report["scope"] = "Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run"
    (out / "report.json").write_text(json.dumps(report, indent=2))
    lines = [f"# Capture verification: {status}", "", report["scope"], "",
             f"Observed methods: {audit['methods']}", f"Matched layer calls: {audit['matched_layer_calls']}", ""]
    lines += [f"- {r['case']}: {r['status']}, shape={r.get('shape')}, seconds={r['seconds']}" for r in report["requests"]]
    if strict is not None:
        lines += ["", f"Strict selection events: {strict['selection_events']}; layout events: {strict['layout_events']}", "",
                  "| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |",
                  "|---|---:|---|---|---:|"]
        for item in strict["selections"]:
            lines.append(f"| {item['rank']} | {item['tokens']} | {item['expected']} | {item['actual']} | {item['calls']} |")
        lines += ["",
                  "Expected layouts calculated from scenario and input sizes:", "",
                  "| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |",
                  "|---|---|---:|---:|---|---|---:|"]
        for item in strict["layouts"]:
            lines.append(f"| {item['method']} | {item['rank']} | {item['before_rows']} | {item['expected_router_rows']} | {item['expected_shards']} | {item['expected_ranges']} | {item['calls']} |")
    else:
        lines += ["", "Communication selection correctness: NOT CHECKED (use --scenario)."]
    lines += ["", "Failures:"] + [f"- {value}" for value in failures]
    lines += ["", "Coverage missing:"] + [f"- {value}" for value in audit["coverage_missing"]]
    lines += ["", "分支、布局与代表性日志：见 branch-walkthrough.md"]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    print(f"{status}: {out.resolve()}/report.md", flush=True)
    return 1 if status == "FAIL" else 2 if status == "INCONCLUSIVE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
