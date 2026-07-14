# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.sample.logprob import compute_token_logprobs


def case_topk_log_softmax(device):
    for batch, vocab, topk in ((16, 32000, 5), (64, 32000, 5)):
        logits = torch.randn((batch, vocab), device=device)
        token_ids = torch.randint(0, vocab, (batch, topk), device=device, dtype=torch.int64)
        holder = {}
        def fn():
            holder['out'] = compute_token_logprobs(logits, token_ids)
            return holder['out']
        yield f"batch_size={batch} vocab_size={vocab} topk={topk}", fn, lambda: float(holder['out'].sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_topk_log_softmax(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_topk_log_softmax_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
