# Capture-layout validation on current upstream main

- Upstream base: `852989f580820849113d67d13fd8053e279d0444`
- Implementation: `bfed1cb65d2ae8c37b9ada7b45191bbb01224679`
- Capturer SHA256: `daf2eea480ed8af351fe4f9eca8a8b5bf4105c6ca8853f683a2b7a11db5ceb39` (checked against every NPU worker).

## Results

- Full capture regression module: **64 passed in 10.36s**, macOS arm64, Python 3.12.2 / torch 2.14.0.
- Full pre-commit on four changed files: **PASS**, including mypy.
- Ascend A3, HCCL, torch 2.10.0+cpu / torch-npu 2.10.0.post4: **216 per-rank checks, 2,760 captured expert IDs, zero differences**.
- DP=1/TP=2 and DP=2/TP=2; six component cases each in eager and actual ACL graph replay. Each mode checks three changed routing inputs after warmup/capture.

Cases: ALLGATHER prepare; uneven ALLTOALL prepare; ALLTOALL prepare with SP inputs; MC2 prepare without SP; MC2 prepare with SP and internal padding; empty capture ranges that still join the HCCL collective. No mocks replace prepare, router, capturer, HCCL or graph execution. The last case explicitly replaces only the supplied layout with empty source ranges to exercise collective participation.

The harness calls actual Ascend prepare methods, a BaseRouter subclass using NPU torch.topk, and the unmodified proposed upstream capturer. The test constructs deterministic input logits with no ties. Its expected rows come from independent CPU top-k over original local inputs, never from capture_layout/shard_sizes/source_ranges. A +100 mapping makes post-EPLB IDs observably different; capture must retain pre-mapping IDs. Sentinel assertions check the other layer and unused buffer rows. The MC2+SP DP=2 case has local token counts (5,13): physical shards (7,7), DP0 valid offsets (0,1,2,7,8), including graph replay.

## Reproduce

The existing downstream layout adapter is needed to exercise its prepare producers. Its prepare source at public fork commit `5d0665fbaf1270745d04d94907c6e81784dc8584` is byte-identical to the remote adapter base `e8824e648be0407cc5bee8a976d195716fc2336e` (prepare SHA256 `4d227d75d4f7cd6617d5b286981d89caaf943a02abf201b9757fbedfd33ec31a`). `ascend-prepare.diff` records the subsequent prepare changes used here. `npu-summary.json` records tested downstream source hashes.

```bash
# In an Ascend CANN / torch-npu environment; use an isolated venv.
export PYTHONPATH=/path/to/vllm:/path/to/vllm-ascend
export HCCL_EXEC_TIMEOUT=120
ASCEND_RT_VISIBLE_DEVICES=0,1 .venv/bin/python -m torch.distributed.run \
  --standalone --nproc_per_node=2 validate_npu_capture.py --dp=1 --output=results-dp1
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3 .venv/bin/python -m torch.distributed.run \
  --standalone --nproc_per_node=4 validate_npu_capture.py --dp=2 --output=results-dp2
.venv/bin/python -m pytest --confcutdir=tests/model_executor \
  tests/model_executor/test_routed_experts_capture.py -q
```

## Scope

This is real-device **component integration**, not a fresh model-serving/API test. It does not validate the communication selector or native MC2/FUSED_MC2 expert kernels. A fresh serving attempt is blocked before capture: the existing Ascend runner imports `vllm.transformers_utils.configs.deepseek_v4`, a path removed from current upstream. The earlier October 15 model-serving numbers are deliberately not counted in these results. No PP, PCP, multi-node, TP=4, LoRA, other accelerator or throughput claim.

Initial harness setup failed because EXTRA_CTX was assigned outside a forward context; the corrected run installs a real ForwardContext. The initial log is retained locally, and only completed passing runs are summarized here. AI assistance was used.
