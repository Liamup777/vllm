# Full-model routed-expert capture validation, 2026-10-19

Result: **17/17 configurations PASS**, 144 HTTP requests, **16,048,896 API expert IDs** and **31,912,320 worker-buffer expert IDs**, zero mismatches. All archived traces were independently rechecked after serving, and source fingerprints verified.

Tested upstream head: `bfed1cb65d2ae8c37b9ada7b45191bbb01224679`. Main snapshot: `852989f580820849113d67d13fd8053e279d0444`. PR: https://github.com/vllm-project/vllm/pull/62441 . Production capturer SHA256: `daf2eea480ed8af351fe4f9eca8a8b5bf4105c6ca8853f683a2b7a11db5ceb39`.

## What this checks

A real Qwen3-30B-A3B model serves HTTP requests on Ascend A3. Test-only labels follow the actual prepare communication; the labels are removed before routing. Raw logical router IDs and labels are copied on-device before production capture, including inside ACL graph replay. An independent offline checker reconstructs token ownership from those labels, without consuming capture layout metadata, then compares every TP worker buffer and every returned API element by request/token/layer/top-k. Flags are cleared before each forward to prevent stale warmup/replay data. Cross-run routing equality is not required.

Coverage: DP 1/2, TP 1/2/4, EP and SP, actual ALLGATHER/ALLTOALL/MC2/FUSED_MC2 selection, uneven TP shards, eager MC2 and FUSED_MC2 interior padding, four configurations with confirmed ACL graph replay. LoRA is the enable flag only; no adapter was loaded. BF16 and W8A8 models were used. This is capture correctness, not model-quality or performance evaluation. No PP/PCP, multi-node, other hardware/model, loaded-adapter or naturally unselected ALLGATHER+MoE-SP claim.

## Runtime compatibility is separate from the PR

The existing Ascend checkout cannot serve against this main snapshot without compatibility changes unrelated to capture. Testing used copied packages, leaving original repositories untouched. `ascend-integration-from-base.diff` is the existing downstream layout adapter relative to Ascend `e8824e648be0407cc5bee8a976d195716fc2336e`. Apply `runtime-compatibility.diff` after that for moved imports/config/planner/runner signatures. Cases 06/13/17/18 additionally used `retry-runtime-compatibility.diff`: restore the internal-NPU-format initialization previously supplied by an eager-runner import, and locally filter graph sizes divisible by TP after upstream removed the helper. The earlier failed startups are preserved remotely and are not counted as capture passes.

The submitted four upstream files were not modified to make these runs pass. Per-case runtime-source-state.json files record exact loaded-source fingerprints; 01/09 initial one-off snapshots name the package directory while their hash keys are relative to its parent, handled explicitly by the finalizer. Original Ascend Python source hashes were verified unchanged. This result establishes capture correctness in the recorded adapted runtime, not stock Ascend compatibility with this main snapshot.

## Read the evidence

- `SUMMARY.md` / `summary.json`: per-case coverage and exact element counts.
- `cases/*/same-run-report.md` and JSON: full-content worker/API comparison results plus concrete router/returned samples.
- `cases/*/verification/report.md`: independent selector/layout and response-shape assertions. Graph replay does not re-emit Python prepare/capture logging, so some log-only coverage reports remain INCONCLUSIVE; those are distinct from the raw device/API comparisons, which all PASS. All checked selector/layout assertions have zero failures.
- `cases/*/graph-replay-evidence.txt`: actual replay confirmation, not merely a graph-enabled command.
- `cases/*/raw-router`, API response JSON and .npy files: raw arrays are included in the local/remote full delivery archive. The public compact Git evidence omits raw tensors and very large server logs.
- `tools/`: actual same-forward oracle, test wrapper, matrix launcher and the 26 passing validator unit tests.
- `environment.json`, source/native SHA manifests and compatibility diffs: reproducibility boundaries.
- `cleanup.json`: no remaining test servers/ports. NPU-smi also confirmed no NPU processes after cleanup.

Full delivery archive and all original server/startup logs remain on host 162, container vllm_liam, under `/home/lingmutian/capture-main-20261019/e2e/`.

## Recheck stored traces

From the extracted delivery directory with Python/numpy available:

```bash
for run in cases/*; do python tools/check_same_run.py "$run"; done
python -m pytest tools/test_capture_expectations.py tools/test_same_run.py tools/test_verify_capture.py -q
```

The matrix launcher and source-provenance finalizer retain the recorded 162 paths. Re-running serving needs the matching built Ascend package, weights, vendor environment, and pinned source/compatibility variants; this archive does not include model weights or compiled native binaries. AI assistance was used.

Full archive SHA256: `3efd2df640dcd43cb5d446b8dc79ae6a3812c8ff1230baff372461f45db51f3d` (15,359,158 bytes). Raw arrays remain in the full local/remote archive; this public directory is compact evidence.
