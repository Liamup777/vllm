# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.buffer_utils import _apply_write_kernel


def case_apply_write(device):
    for writes, width in ((16, 8), (128, 16)):
        out = torch.zeros((writes, width + 4), device=device, dtype=torch.int32)
        indices = torch.arange(writes, device=device, dtype=torch.int32)
        starts = torch.ones(writes, device=device, dtype=torch.int32)
        cu = torch.arange(1, writes + 1, device=device, dtype=torch.int32) * width
        contents = torch.arange(writes * width, device=device, dtype=torch.int32)
        yield f"writes={writes} width={width}", lambda: _apply_write_kernel[(writes,)](out, out.stride(0), indices, starts, contents, cu, None, BLOCK_SIZE=64, MULTI_GROUP=False), lambda: int(out.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_apply_write(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_apply_write_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
