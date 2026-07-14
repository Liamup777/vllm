# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse

import torch

from mrv2_bench_utils import bench_gpu
from vllm.platforms import current_platform
from vllm.v1.worker.gpu.input_batch import combine_sampled_and_draft_tokens


def case_combine_sampled_and_draft_tokens(device):
    for num_reqs, steps in ((16, 2), (128, 4)):
        num_logits = num_reqs * (steps + 1)
        input_ids = torch.zeros(num_logits, device=device, dtype=torch.int32)
        idx = torch.arange(num_reqs, device=device, dtype=torch.int32)
        last = torch.randint(0, 32000, (num_reqs,), device=device, dtype=torch.int64)
        qsl = torch.arange(num_reqs + 1, device=device, dtype=torch.int32) * (steps + 1)
        seq = torch.full((num_reqs,), steps + 1, device=device, dtype=torch.int32)
        prefill = torch.zeros(num_reqs, device=device, dtype=torch.int32)
        draft = torch.randint(0, 32000, (num_reqs, steps), device=device, dtype=torch.int32)
        cu = qsl
        yield f"num_reqs={num_reqs} steps={steps}", lambda: combine_sampled_and_draft_tokens(input_ids, idx, last, qsl, seq, prefill, draft, cu, num_logits), lambda: int(input_ids.sum().item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=f"{current_platform.device_type}:0")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--repeat", type=int, default=100)
    args = parser.parse_args()
    if not current_platform.is_cuda_alike():
        raise RuntimeError("This benchmark requires CUDA/ROCm.")

    for spec, fn, checksum in case_combine_sampled_and_draft_tokens(args.device):
        latency_us, _ = bench_gpu(fn, args.warmup, args.repeat)
        print(f"op=_combine_sampled_and_draft_tokens_kernel {spec} latency_us={latency_us:.2f} "
              f"checksum={checksum():.3f}")


if __name__ == "__main__":
    main()
