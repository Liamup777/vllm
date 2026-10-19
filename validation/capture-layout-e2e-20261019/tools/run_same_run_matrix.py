"""Same-run raw-router to API capture validation matrix."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import socket
import subprocess
import sys
import time
import urllib.request


CASES = {
    "01-ag-dp1-tp2": dict(dp=1, tp=2, ep=False, sp=False, fused=0),
    "02-ag-dp2-tp2": dict(dp=2, tp=2, ep=False, sp=False, fused=0),
    "03-ep-dp1-tp2": dict(dp=1, tp=2, ep=True, sp=False, fused=0),
    "04-ep-dp2-tp2": dict(dp=2, tp=2, ep=True, sp=False, fused=0),
    "05-ep-dp2-tp2-sp": dict(dp=2, tp=2, ep=True, sp=True, fused=0),
    "06-ag-dp1-tp1": dict(dp=1, tp=1, ep=False, sp=False, fused=0),
    "07-ep-dp2-tp1": dict(dp=2, tp=1, ep=True, sp=False, fused=0),
    "08-ep-dp1-tp4": dict(dp=1, tp=4, ep=True, sp=False, fused=0),
    "09-fused-dp1-tp2": dict(dp=1, tp=2, ep=True, sp=False, fused=1),
    "10-fused-dp2-tp2": dict(dp=2, tp=2, ep=True, sp=False, fused=1),
    "11-fused-dp2-tp2-sp": dict(dp=2, tp=2, ep=True, sp=True, fused=1),
    "12-graph-ag-dp1-tp2": dict(dp=1, tp=2, ep=False, sp=False, fused=0, graph=True),
    "13-graph-ep-dp2-tp2-sp": dict(dp=2, tp=2, ep=True, sp=True, fused=0, graph=True),
    "14-reference-old-patch": dict(dp=1, tp=2, ep=False, sp=False, fused=0, legacy=True),
    "15-lora-ep-dp1-tp2": dict(dp=1, tp=2, ep=True, sp=False, fused=0, lora=True),
    "16-sp-internal-padding": dict(dp=2, tp=2, ep=True, sp=True, fused=0, internal=True),
    "17-graph-sp-internal-padding": dict(dp=2, tp=2, ep=True, sp=True, fused=0, internal=True, graph=True),
    "18-graph-fused-dp2-tp2-sp": dict(dp=2, tp=2, ep=True, sp=True, fused=1, graph=True),
    "19-sp-controlled-eager": dict(dp=2, tp=2, ep=True, sp=True, fused=0, internal=True, controlled=True),
    "20-sp-controlled-graph": dict(dp=2, tp=2, ep=True, sp=True, fused=0, internal=True, controlled=True, graph=True),
    "21-fused-graph-capture-off": dict(dp=2, tp=2, ep=True, sp=True, fused=1, graph=True, capture_off=True),
    "22-fused-eager-capture-off": dict(dp=2, tp=2, ep=True, sp=True, fused=1, capture_off=True),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cases", default="01-ag-dp1-tp2")
    args = parser.parse_args()
    root = args.root
    root.mkdir(parents=True, exist_ok=True)
    client = Path(__file__).resolve().parent
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for name in args.cases.split(","):
        port = 18262 + list(CASES).index(name)
        cfg = CASES[name]
        out = root / name
        out.mkdir(exist_ok=False)
        result = dict(case=name, configuration=cfg, start=datetime.datetime.now().isoformat())

        def save(stage):
            result["stage"] = stage
            (out / "status.json").write_text(json.dumps(result, indent=2))
            print(name, stage, flush=True)

        use_quantized = cfg["fused"] or (cfg["tp"] == 1 and not cfg["ep"])
        model = "/mnt/weight/Qwen3-30B-A3B-W8A8" if use_quantized else "/mnt/weight/Qwen3-30B-A3B"
        devices = list(range(int(os.environ.get("CAPTURE_DEVICE_BASE", "12")), int(os.environ.get("CAPTURE_DEVICE_BASE", "12")) + cfg["dp"] * cfg["tp"]))
        extra = dict(enable_flashcomm1=cfg["sp"], enable_fused_mc2=cfg["fused"],
                     runtime_config={"ascend_log": {"level": "INFO", "debug": [
                         "vllm.logger", "vllm.model_executor.layers.fused_moe.routed_experts_capturer"]}})
        cmd = ["vllm", "serve", model, "--served-model-name", "moe", "--host", "127.0.0.1",
               "--port", str(port), "--enable-return-routed-experts", "--enable-prefix-caching",
               "--max-model-len", "4096", "--max-num-batched-tokens", "4096", "--max-num-seqs", "16",
               "--gpu-memory-utilization", "0.75", "--tensor-parallel-size", str(cfg["tp"]),
               "--additional-config", json.dumps(extra)]
        if not cfg.get("graph"):
            cmd += ["--enforce-eager"]
        else:
            cmd += ["--cudagraph-metrics"]
        if cfg["dp"] > 1:
            cmd += ["--data-parallel-size", str(cfg["dp"]), "--data-parallel-size-local", str(cfg["dp"])]
        if cfg["ep"]:
            cmd += ["--enable-expert-parallel"]
        if cfg.get("lora"):
            cmd += ["--enable-lora", "--max-loras", "1"]
        if cfg["sp"]:
            cmd += ["--all2all-backend", "allgather_reducescatter"]
        if False:
            cmd = [sys.executable, str(client / "reference_cli.py")] + cmd[1:]
        if cfg.get("capture_off"):
            cmd.remove("--enable-return-routed-experts")
        env = dict(os.environ, ASCEND_RT_VISIBLE_DEVICES=",".join(map(str, devices)),
                   VLLM_USE_V2_MODEL_RUNNER="1", VLLM_LOGGING_LEVEL="DEBUG",
                   VLLM_LOGGING_CONFIG_PATH=str(client / "capture_logging.json"))
        cmd = [sys.executable, str(client / "same_run_cli.py")] + cmd[1:]
        (client / "same-run-active.json").write_text(json.dumps({"trace": str(out / "raw-router")}))
        result.update(model=model, devices=devices, command=cmd)
        (out / "launch.sh").write_text("#!/bin/bash\nenv " + " ".join(shlex.quote(k + "=" + env[k]) for k in (
            "ASCEND_RT_VISIBLE_DEVICES", "VLLM_USE_V2_MODEL_RUNNER", "VLLM_LOGGING_LEVEL", "VLLM_LOGGING_CONFIG_PATH"))
            + " " + shlex.join(cmd) + "\n")
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        finally:
            sock.close()
        runtime = Path(os.environ["CAPTURE_ASCEND_ROOT"])
        source_state = dict(upstream="bfed1cb65d2ae8c37b9ada7b45191bbb01224679",
            capture_sha256=hashlib.sha256(Path("/home/lingmutian/capture-main-20261019/vllm/vllm/model_executor/layers/fused_moe/routed_experts_capturer.py").read_bytes()).hexdigest(),
            ascend_root=str(runtime),
            python_sha256={str(p.relative_to(runtime)):hashlib.sha256(p.read_bytes()).hexdigest() for p in runtime.rglob("*.py")})
        (out / "runtime-source-state.json").write_text(json.dumps(source_state, indent=2))
        process = None
        try:
            with (out / "server.log").open("w") as log:
                process = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                result["server_pid"] = process.pid
                save("starting")
                deadline = time.monotonic() + 900
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise RuntimeError(f"Server exited during startup: {process.returncode}")
                    try:
                        with opener.open(f"http://127.0.0.1:{port}/v1/models", timeout=2) as response:
                            if response.status == 200:
                                break
                    except Exception:
                        time.sleep(2)
                else:
                    raise TimeoutError("Startup exceeded 900 seconds")
                save("ready")
                plan = dict(dp=cfg["dp"], tp=cfg["tp"], sp=cfg["sp"], ep=cfg["ep"],
                            ep_world=cfg["dp"] * cfg["tp"], lora=cfg.get("lora", False), fused=cfg["fused"],
                            policy="FUSED_OR_CAPACITY", capacity=16)
                (out / "scenario.json").write_text(json.dumps(plan, indent=2))
                expected = "FUSED_MC2" if cfg["fused"] else "MC2,ALLTOALL" if cfg["ep"] else "ALLGATHER"
                if cfg.get("lora"):
                    expected = "ALLTOALL"
                check = [sys.executable, str(client / "verify_capture.py"), "--model", model,
                         "--url", f"http://127.0.0.1:{port}", "--log-file", str(out / "server.log"),
                         "--dp", str(cfg["dp"]), "--tp", str(cfg["tp"]), "--sp", "on" if cfg["sp"] else "off",
                         "--expect-comm", expected, "--output", str(out / "verification"),
                         "--scenario", str(out / "scenario.json")]
                if False:
                    reference_name = "19-sp-controlled-eager" if cfg.get("controlled") else "11-fused-dp2-tp2-sp" if cfg["fused"] else "16-sp-internal-padding" if cfg.get("internal") else "05-ep-dp2-tp2-sp" if cfg["ep"] else "01-ag-dp1-tp2"
                    reference = root / reference_name / "verification"
                    if reference.exists():
                        check += ["--reference-dir", str(reference)]
                if cfg.get("internal"):
                    check += ["--require-internal-padding"]
                if cfg.get("controlled"):
                    check += ["--skip-general-concurrency"]
                if cfg.get("capture_off"):
                    reference_name = "18-graph-fused-dp2-tp2-sp" if cfg.get("graph") else "11-fused-dp2-tp2-sp"
                    check = [sys.executable, str(client / "check_generation_control.py"),
                             "--url", f"http://127.0.0.1:{port}", "--output", str(out / "verification"),
                             "--reference", str(root / reference_name / "verification")]
                (out / "check.sh").write_text(shlex.join(check) + "\n")
                with (out / "client.log").open("w") as client_log:
                    completed = subprocess.run(check, stdout=client_log, stderr=subprocess.STDOUT, timeout=900)
                result["check_exit"] = completed.returncode
                if cfg.get("graph"):
                    # Let the standard graph dispatch statistics reach the log.
                    time.sleep(12)
                report = out / "verification/report.json"
                if report.exists():
                    result["verification"] = json.loads(report.read_text())["status"]
                with (out / "same-run-check.log").open("w") as audit_log:
                    audit = subprocess.run([sys.executable, str(client / "check_same_run.py"), str(out)], stdout=audit_log, stderr=subprocess.STDOUT, timeout=300)
                result["same_run_exit"] = audit.returncode
                save("verified")
        except Exception as exc:
            result["error"] = repr(exc)
            save("error")
        finally:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
            result["end"] = datetime.datetime.now().isoformat()
            save("stopped")
            time.sleep(4)


if __name__ == "__main__":
    main()
