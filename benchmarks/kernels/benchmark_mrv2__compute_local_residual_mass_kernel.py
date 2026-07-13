# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import time

import torch

from vllm.platforms import current_platform
from vllm.triton_utils import triton
from vllm.v1.worker.gpu.spec_decode.rejection_sampler_utils import (
    _compute_local_residual_mass_kernel,
)


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

    for num_reqs, steps, vocab_size in [(16, 3, 32_000), (64, 3, 32_000)]:
        num_logits = num_reqs * (steps + 1)
        block_size = 8192
        num_blocks = triton.cdiv(vocab_size, block_size)
        padded = triton.next_power_of_2(num_blocks)
        shape = (num_logits, num_blocks)
        local_residual_mass = torch.zeros(shape, device=args.device)
        cumulative_log_p = torch.zeros(num_logits, device=args.device)
        target_logits = torch.randn((num_logits, vocab_size), device=args.device)
        draft_logits = torch.randn((num_reqs, steps, vocab_size), device=args.device)
        target_local_max = torch.randn(shape, device=args.device)
        target_local_sumexp = torch.rand(shape, device=args.device) + 1
        draft_local_max = torch.randn(shape, device=args.device)
        draft_local_sumexp = torch.rand(shape, device=args.device) + 1
        expanded_idx = torch.arange(num_reqs, device=args.device,
                                    dtype=torch.int32).repeat_interleave(steps + 1)
        expanded_pos = torch.arange(steps + 1, device=args.device,
                                    dtype=torch.int32).repeat(num_reqs)
        temp = torch.ones(num_reqs, device=args.device)
        fn = lambda: _compute_local_residual_mass_kernel[(num_logits, num_blocks)](
            local_residual_mass, local_residual_mass.stride(0), cumulative_log_p,
            target_logits, target_logits.stride(0), target_local_max,
            target_local_max.stride(0), target_local_sumexp,
            target_local_sumexp.stride(0), draft_logits, draft_logits.stride(0),
            draft_logits.stride(1), draft_local_max, draft_local_max.stride(0),
            draft_local_sumexp, draft_local_sumexp.stride(0), expanded_idx,
            expanded_pos, temp, vocab_size, steps, num_blocks,
            BLOCK_SIZE=block_size, PADDED_VOCAB_NUM_BLOCKS=padded)
        latency_us = bench(fn, args.warmup, args.repeat)
        print(f"op=_compute_local_residual_mass_kernel num_reqs={num_reqs} "
              f"steps={steps} vocab_size={vocab_size} latency_us={latency_us:.2f} "
              f"checksum={float(local_residual_mass.sum().item()):.3f}")


if __name__ == "__main__":
    main()
