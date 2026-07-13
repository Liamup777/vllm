# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import time

import torch

from vllm.platforms import current_platform
from vllm.triton_utils import tl, triton
from vllm.v1.worker.gpu.spec_decode.rejection_sampler_utils import (
    _compute_global_residual_mass,
)


@triton.jit
def _bench_kernel(out, local_residual_mass, local_residual_mass_stride,
                  prefix_joint_ratio, target_logits, target_logits_stride,
                  target_local_max, target_local_max_stride, target_local_sumexp,
                  target_local_sumexp_stride, draft_sampled, vocab_num_blocks,
                  PADDED_VOCAB_NUM_BLOCKS: tl.constexpr,
                  HAS_DRAFT_LOGITS: tl.constexpr):
    row = tl.program_id(0)
    mass = _compute_global_residual_mass(
        local_residual_mass, local_residual_mass_stride, prefix_joint_ratio,
        target_logits, target_logits_stride, target_local_max,
        target_local_max_stride, target_local_sumexp, target_local_sumexp_stride,
        draft_sampled, row, vocab_num_blocks, PADDED_VOCAB_NUM_BLOCKS,
        HAS_DRAFT_LOGITS)
    tl.store(out + row, mass)


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

    for num_logits, num_blocks, has_draft_logits in [(64, 4, True), (64, 19, False)]:
        vocab_size = num_blocks * 8192
        padded = triton.next_power_of_2(num_blocks)
        out = torch.empty(num_logits, device=args.device)
        local_residual_mass = torch.rand((num_logits, num_blocks), device=args.device)
        target_logits = torch.randn((num_logits, vocab_size), device=args.device)
        target_local_max = torch.randn((num_logits, num_blocks), device=args.device)
        target_local_sumexp = torch.rand((num_logits, num_blocks), device=args.device) + 1
        draft_sampled = torch.randint(0, vocab_size, (num_logits + 1,),
                                      device=args.device, dtype=torch.int64)
        fn = lambda: _bench_kernel[(num_logits,)](
            out, local_residual_mass, local_residual_mass.stride(0), 0.75,
            target_logits, target_logits.stride(0), target_local_max,
            target_local_max.stride(0), target_local_sumexp,
            target_local_sumexp.stride(0), draft_sampled, num_blocks,
            PADDED_VOCAB_NUM_BLOCKS=padded, HAS_DRAFT_LOGITS=has_draft_logits)
        latency_us = bench(fn, args.warmup, args.repeat)
        print(f"op=_compute_global_residual_mass num_logits={num_logits} "
              f"num_blocks={num_blocks} has_draft_logits={has_draft_logits} "
              f"latency_us={latency_us:.2f} checksum={float(out.sum().item()):.3f}")


if __name__ == "__main__":
    main()
