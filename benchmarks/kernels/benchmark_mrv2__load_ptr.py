# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import time

import torch

from vllm.platforms import current_platform
from vllm.triton_utils import tl, triton
from vllm.v1.worker.gpu.buffer_utils import _load_ptr


@triton.jit
def _bench_load_ptr_kernel(ptrs, value):
    out = _load_ptr(ptrs, tl.int32)
    tl.store(out, value)


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
    out = torch.empty(1, device=args.device, dtype=torch.int32)
    ptrs = torch.tensor([out.data_ptr()], device=args.device, dtype=torch.uint64)
    fn = lambda: _bench_load_ptr_kernel[(1,)](ptrs, 123)
    latency_us = bench(fn, args.warmup, args.repeat)
    print(f"op=_load_ptr latency_us={latency_us:.2f} checksum={int(out.item())}")


if __name__ == "__main__":
    main()
