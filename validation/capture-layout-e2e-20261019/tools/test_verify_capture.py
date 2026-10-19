"""HTTP fixtures exercise the verifier; these are not NPU/model tests."""

import base64
from contextlib import redirect_stdout
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

import numpy as np

from verify_capture import audit_log, main
from capture_expectations import LAYOUT, SELECTION


class VerifierTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.model = self.root / "model"
        self.model.mkdir()
        (self.model / "config.json").write_text(json.dumps({
            "num_hidden_layers": 3, "num_experts": 4, "num_experts_per_tok": 2,
        }))
        self.log = self.root / "server.log"
        self.log.write_text("startup logs must not count\n")
        self.mode = "good"
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                body = json.dumps({"data": [{"id": "moe"}]}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                n = len(body["prompt"])
                generated = body["max_tokens"]
                rows = n + generated - (2 if fixture.mode == "bad_shape" else 1)
                routes = np.full((rows, 3, 2), 4 if fixture.mode == "bad_id" else 1, dtype=np.uint8)
                encoded = io.BytesIO()
                np.save(encoded, routes, allow_pickle=False)
                if fixture.mode != "no_logs":
                    with fixture.log.open("a") as f:
                        if fixture.mode in {"strict", "bad_layout"}:
                            selection = dict(dp=0, tp=0, policy="FUSED_OR_CAPACITY", tokens=n,
                                             capacity=16, ep=False, ep_world=1, lora=False, fused=0,
                                             method="ALLGATHER", draft=False)
                            layout = dict(dp=0, tp=0, sp=False, graph="NONE", method="ALLGATHER",
                                          layer="model.layers.0.mlp", prepare="PrepareAndFinalizeWithAllGather",
                                          before_rows=n, router_rows=n, dp_tokens=[n], dp_local_sizes=None,
                                          padded_rows=n, shards=[], ranges=[[0, n - 1 if fixture.mode == "bad_layout" else n]], gather=False)
                            f.write(SELECTION + json.dumps(selection) + "\n")
                            for layer in range(3):
                                layout["layer"] = f"model.layers.{layer}.mlp"
                                f.write(LAYOUT + json.dumps(layout) + "\n")
                        f.write(f"Ascend routed capture prepare: layer=model.layers.0.mlp dp=0 tp=0 sp=False graph=NONE comm=ALLGATHER rows={n} shards=() ranges=((0, {n}),)\n")
                        f.write(f"Routed-experts capture layer=0 dp_rank=0 tp_rank=0 input_rows={n} rows={n} shards=() ranges=((0, {n}),)\n")
                payload = {"usage": {"prompt_tokens": n}, "choices": [{
                    "token_ids": [3] * generated,
                    "routed_experts": base64.b64encode(encoded.getvalue()).decode(),
                }]}
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def run_verifier(self, name, *extra):
        output = self.root / name
        arguments = ["--model", str(self.model), "--url", f"http://127.0.0.1:{self.server.server_port}",
                     "--log-file", str(self.log), "--dp", "1", "--tp", "1", "--sp", "off",
                     "--expect-comm", "ALLGATHER", "--long-tokens", "17", "--output", str(output)]
        with redirect_stdout(io.StringIO()):
            code = main(arguments + list(extra))
        return code, json.loads((output / "report.json").read_text()), output

    def test_good_responses_and_layout_pass(self):
        code, report, output = self.run_verifier("pass")
        self.assertEqual(code, 0)
        self.assertEqual(report["log_audit"]["matched_layer_calls"], 4)
        walkthrough = (output / "branch-walkthrough.md").read_text()
        self.assertIn("_prepare_with_dp_group", walkthrough)
        self.assertIn("从第 0 行取 17 行", walkthrough)
        self.assertIn("| 0/0 | False/NONE | ALLGATHER | 17 | `()` | `((0, 17),)` | 1/1 |", walkthrough)

    def test_missing_branch_is_inconclusive(self):
        code, report, _ = self.run_verifier("branch", "--expect-comm", "ALLGATHER,MC2")
        self.assertEqual(code, 2)
        self.assertIn("MC2", " ".join(report["log_audit"]["coverage_missing"]))

    def test_strict_scenario_checks_selection_and_layout(self):
        scenario = self.root / "scenario.json"
        scenario.write_text(json.dumps(dict(dp=1, tp=1, sp=False, ep=False, ep_world=1,
                                           lora=False, fused=0, policy="FUSED_OR_CAPACITY", capacity=16)))
        self.mode = "strict"
        code, report, _ = self.run_verifier("strict", "--scenario", str(scenario))
        self.assertEqual(code, 0)
        self.assertEqual(report["selection_layout_audit"]["selection_events"], 4)
        self.mode = "bad_layout"
        self.assertEqual(self.run_verifier("bad-layout", "--scenario", str(scenario))[0], 1)
        self.mode = "good"
        self.assertEqual(self.run_verifier("missing-audit", "--scenario", str(scenario))[0], 2)

    def test_no_logs_does_not_pass(self):
        self.mode = "no_logs"
        self.assertEqual(self.run_verifier("logs")[0], 2)

    def test_invalid_expert_id_fails(self):
        self.mode = "bad_id"
        self.assertEqual(self.run_verifier("id")[0], 1)

    def test_wrong_route_length_fails(self):
        self.mode = "bad_shape"
        self.assertEqual(self.run_verifier("shape")[0], 1)

    def test_reference_comparison_detects_route_changes(self):
        _, _, reference = self.run_verifier("reference")
        self.assertEqual(self.run_verifier("match", "--reference-dir", str(reference))[0], 0)
        routes = np.load(reference / "short-1.npy")
        routes[0, 0, 0] = 2
        np.save(reference / "short-1.npy", routes)
        code, report, _ = self.run_verifier("mismatch", "--reference-dir", str(reference))
        self.assertEqual(code, 1)
        self.assertEqual(len(report["requests"]), 4)
        self.assertTrue(all(record["response_validated"] for record in report["requests"]))

    def test_internal_padding_layout_and_row_mismatch(self):
        text = (
            "Ascend routed capture prepare: layer=model.layers.0.mlp dp=0 tp=1 sp=True graph=NONE comm=MC2 rows=7 shards=(7, 7) ranges=((0, 3), (7, 2))\n"
            "Routed-experts capture layer=0 dp_rank=0 tp_rank=1 input_rows=7 rows=5\n"
        )
        report = audit_log(text, {"MC2"}, True, 1, 2)
        self.assertTrue(report["internal_padding_skip_observed"])
        self.assertEqual(report["errors"], [])
        report = audit_log(text.replace("input_rows=7 rows=5", "input_rows=7 rows=4"), {"MC2"}, True, 1, 2)
        self.assertTrue(report["errors"])


if __name__ == "__main__":
    unittest.main()
