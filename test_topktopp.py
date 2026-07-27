import random

import pytest
import torch

from vllm_ascend.worker.v2.sample.topk_topp_triton import apply_top_k_top_p_triton
# Common vocab sizes from mainstream models
VOCAB_SIZES = [
    32000,  # LLaMA / LLaMA2 / Mistral
   50257,  # GPT-2
   65024,  # ChatGLM
   128256,  # LLaMA3
   151936,  # Qwen2
]



@pytest.mark.parametrize(
    "num_tokens, vocab_size",
    [(random.randint(1, 64), vocab_size) for vocab_size in VOCAB_SIZES],
)
def test_topktopp_kernel(num_tokens, vocab_size):
    torch.manual_seed(42)

    # Build input tensors
    logits_triton = torch.randn((num_tokens, vocab_size), dtype=torch.float32).npu()

    num_requests = num_tokens
    topk = torch.randint(low=1, high=10, size=(num_requests,), dtype=torch.int32).npu()
    topp = torch.rand(size=(num_requests,), dtype=torch.float32).npu()
    

    # ========== Run Triton kernel ==========
    apply_top_k_top_p_triton(logits_triton, topk, topp)

