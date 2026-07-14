# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.triton_utils import tl, triton
from vllm.v1.worker.gpu.sample.gumbel import tl_rand64


@triton.jit
def _rand64_bench_kernel(out, seed, numel, INCLUDES_ZERO: tl.constexpr,
                         BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    block = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = block < numel
    vals = tl_rand64(seed, block, includes_zero=INCLUDES_ZERO)
    tl.store(out + block, vals, mask=mask)


def case_tl_rand64(device):
    for numel in (1024, 65536):
        out = torch.empty(numel, device=device, dtype=torch.float64)
        grid = (triton.cdiv(numel, 256),)
        yield f"numel={numel}", lambda: _rand64_bench_kernel[grid](out, 123, numel, INCLUDES_ZERO=False, BLOCK_SIZE=256), lambda: float(out.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_tl_rand64(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=tl_rand64 {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
