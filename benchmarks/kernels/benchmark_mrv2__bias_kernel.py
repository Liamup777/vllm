# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.sample.logit_bias import apply_logit_bias


def case_bias(device):
    for num_tokens, vocab, n in ((16, 32000, 4), (64, 32000, 8)):
        logits = torch.randn((num_tokens, vocab), device=device)
        idx = torch.arange(num_tokens, device=device, dtype=torch.int32)
        pos = torch.zeros(num_tokens, device=device, dtype=torch.int32)
        zeros = torch.zeros(num_tokens, device=device, dtype=torch.int32)
        num_bias = torch.full((num_tokens,), n, device=device, dtype=torch.int32)
        ids = torch.randint(0, vocab, (num_tokens, n), device=device, dtype=torch.int32)
        bias = torch.randn((num_tokens, n), device=device)
        min_lens = torch.zeros(num_tokens, device=device, dtype=torch.int32)
        yield f"num_tokens={num_tokens} vocab_size={vocab} num_bias={n}", lambda: apply_logit_bias(logits, idx, pos, zeros, ids, num_bias, ids, bias, min_lens, zeros, ids), lambda: float(logits.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_bias(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_bias_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
