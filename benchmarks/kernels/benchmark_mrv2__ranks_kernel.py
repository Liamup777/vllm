# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.sample.logprob import _ranks_kernel


def case_ranks(device):
    for batch, vocab in ((16, 32000), (64, 32000)):
        logits = torch.randn((batch, vocab), device=device)
        token_ids = torch.randint(0, vocab, (batch,), device=device, dtype=torch.int64)
        out = torch.empty(batch, device=device, dtype=torch.int64)
        yield f"batch_size={batch} vocab_size={vocab}", lambda: _ranks_kernel[(batch,)](out, logits, logits.stride(0), token_ids, vocab, BLOCK_SIZE=8192), lambda: int(out.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_ranks(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_ranks_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
