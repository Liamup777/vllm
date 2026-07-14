# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.input_batch import post_update


def case_post_update(device):
    for num_reqs, steps in ((16, 2), (128, 4)):
        max_len = 4096
        idx = torch.arange(num_reqs, device=device, dtype=torch.int32)
        num_comp = torch.zeros(num_reqs, device=device, dtype=torch.int32)
        last = torch.zeros(num_reqs, device=device, dtype=torch.int64)
        sampled = torch.randint(0, 32000, (num_reqs, steps + 1), device=device, dtype=torch.int64)
        num_sampled = torch.full((num_reqs,), steps + 1, device=device, dtype=torch.int32)
        num_rejected = torch.zeros(num_reqs, device=device, dtype=torch.int32)
        qsl = torch.arange(num_reqs + 1, device=device, dtype=torch.int32) * (steps + 1)
        all_ids = torch.zeros((num_reqs, max_len), device=device, dtype=torch.int32)
        total_len = torch.zeros(num_reqs, device=device, dtype=torch.int32)
        yield f"num_reqs={num_reqs} steps={steps}", lambda: post_update(idx, num_comp, last, None, sampled, num_sampled, num_rejected, qsl, all_ids, total_len), lambda: int(total_len.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_post_update(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_post_update_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
