# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import time

import torch

from vllm.platforms import current_platform
from vllm.triton_utils import tl, triton
from vllm.v1.worker.gpu.sample.gumbel import tl_rand32


@triton.jit
def _bench_kernel(out, seed, numel, INCLUDES_ZERO: tl.constexpr,
                  BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < numel
    values = tl_rand32(seed, offsets, includes_zero=INCLUDES_ZERO)
    tl.store(out + offsets, values, mask=mask)


def bench(fn, warmup: int, repeat: int):
    for _ in range(warmup):
        fn()
    torch.accelerator.synchronize()
    start = time.perf_counter()
    for _ in range(repeat):
        fn()
    torch.accelerator.synchronize()
    return (time.perf_counter() - start) * 1e6 / repeat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for numel in [1024, 65536]:
        block_size = 256
        out = torch.empty(numel, device=args.device)
        fn = lambda: _bench_kernel[(triton.cdiv(numel, block_size),)](
            out, 12345, numel, INCLUDES_ZERO=False, BLOCK_SIZE=block_size)
        latency_us = bench(fn, args.warmup, args.repeat)
        print(f"op=tl_rand32 numel={numel} latency_us={latency_us:.2f} "
              f"checksum={float(out.sum().item()):.3f}")


if __name__ == "__main__":
    main()
