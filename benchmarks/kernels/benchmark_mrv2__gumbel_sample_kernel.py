# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.sample.gumbel import gumbel_sample


def case_gumbel_sample(device):
    for num_tokens, vocab in ((16, 32000), (64, 32000)):
        logits = torch.randn((num_tokens, vocab), device=device)
        idx = torch.arange(num_tokens, device=device, dtype=torch.int32)
        temp = torch.ones(num_tokens, device=device)
        seed = torch.arange(num_tokens, device=device, dtype=torch.int64)
        pos = torch.arange(num_tokens, device=device, dtype=torch.int32)
        holder = {}
        def fn():
            holder['out'] = gumbel_sample(logits, idx, temp, seed, pos, apply_temperature=False, use_fp64=False)
            return holder['out']
        yield f"num_tokens={num_tokens} vocab_size={vocab}", fn, lambda: int(holder['out'].sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_gumbel_sample(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_gumbel_sample_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
