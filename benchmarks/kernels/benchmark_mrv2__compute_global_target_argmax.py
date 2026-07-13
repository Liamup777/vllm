# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import time

import torch

from vllm.platforms import current_platform
from vllm.triton_utils import tl, triton
from vllm.v1.worker.gpu.spec_decode.rejection_sampler_utils import (
    _compute_global_target_argmax,
)


@triton.jit
def _bench_kernel(out, target_local_max, target_local_max_stride,
                  target_local_argmax, target_local_argmax_stride,
                  vocab_num_blocks, PADDED_VOCAB_NUM_BLOCKS: tl.constexpr):
    row = tl.program_id(0)
    token = _compute_global_target_argmax(
        target_local_max, target_local_max_stride, target_local_argmax,
        target_local_argmax_stride, row, vocab_num_blocks,
        PADDED_VOCAB_NUM_BLOCKS)
    tl.store(out + row, token)


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

    for num_logits, num_blocks in [(64, 4), (64, 19)]:
        padded = triton.next_power_of_2(num_blocks)
        out = torch.empty(num_logits, device=args.device, dtype=torch.int64)
        target_local_max = torch.randn((num_logits, num_blocks), device=args.device)
        target_local_argmax = torch.randint(
            0, num_blocks * 8192, (num_logits, num_blocks),
            device=args.device, dtype=torch.int64)
        fn = lambda: _bench_kernel[(num_logits,)](
            out, target_local_max, target_local_max.stride(0), target_local_argmax,
            target_local_argmax.stride(0), num_blocks,
            PADDED_VOCAB_NUM_BLOCKS=padded)
        latency_us = bench(fn, args.warmup, args.repeat)
        print(f"op=_compute_global_target_argmax num_logits={num_logits} "
              f"num_blocks={num_blocks} latency_us={latency_us:.2f} "
              f"checksum={int(out.sum().item())}")


if __name__ == "__main__":
    main()
