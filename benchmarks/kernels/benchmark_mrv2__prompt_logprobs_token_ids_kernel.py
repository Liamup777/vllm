# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.sample.prompt_logprob import get_prompt_logprobs_token_ids


def case_prompt_logprobs_token_ids(device):
    for num_reqs, qlen in ((16, 8), (128, 4)):
        num_tokens = num_reqs * qlen
        qsl = torch.arange(num_reqs + 1, device=device, dtype=torch.int32) * qlen
        idx = torch.arange(num_reqs, device=device, dtype=torch.int32)
        num_comp = torch.zeros(num_reqs, device=device, dtype=torch.int32)
        all_ids = torch.randint(0, 32000, (num_reqs, qlen + 4), device=device, dtype=torch.int32)
        holder = {}
        def fn():
            holder['out'] = get_prompt_logprobs_token_ids(num_tokens, qsl, idx, num_comp, all_ids)
            return holder['out']
        yield f"num_reqs={num_reqs} query_len={qlen}", fn, lambda: int(holder['out'].sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_prompt_logprobs_token_ids(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_prompt_logprobs_token_ids_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
