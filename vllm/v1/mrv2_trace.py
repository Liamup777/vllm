# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Debug helpers for tracing MRv2 request flow across scheduler/worker/runner."""

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import torch
from vllm.logger import logger


def log(stage: str, message: str, *args: Any) -> None:
    logger.info("[MRv2 trace][%s] " + message, stage, *args)


def describe_value(value: Any, *, max_items: int = 6) -> Any:
    if isinstance(value, torch.Tensor):
        return {
            "type": "Tensor",
            "shape": tuple(value.shape),
            "dtype": str(value.dtype),
            "device": str(value.device),
            "numel": value.numel(),
            "data_ptr": hex(value.data_ptr()) if value.device.type != "meta" else None,
        }
    if isinstance(value, np.ndarray):
        flat = value.reshape(-1)
        return {
            "type": "ndarray",
            "shape": value.shape,
            "dtype": str(value.dtype),
            "sample": flat[:max_items].tolist(),
        }
    if isinstance(value, Mapping):
        return {
            "type": type(value).__name__,
            "len": len(value),
            "sample": list(value.items())[:max_items],
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return {
            "type": type(value).__name__,
            "len": len(value),
            "sample": list(value[:max_items]),
        }
    return value


def describe_attrs(obj: Any, attrs: Sequence[str], *, max_items: int = 6) -> dict[str, Any]:
    return {
        attr: describe_value(getattr(obj, attr, None), max_items=max_items)
        for attr in attrs
    }


def summarize_scheduler_output(scheduler_output: Any) -> dict[str, Any]:
    scheduled_cached_reqs = getattr(scheduler_output, "scheduled_cached_reqs", None)
    return {
        "new_reqs": [
            {
                "req_id": req.req_id,
                "prompt_tokens": len(req.prompt_token_ids or []),
                "prefill_tokens": len(req.prefill_token_ids or []),
                "num_computed_tokens": req.num_computed_tokens,
                "block_ids": describe_value(req.block_ids),
                "max_tokens": getattr(req.sampling_params, "max_tokens", None)
                if req.sampling_params is not None
                else None,
            }
            for req in getattr(scheduler_output, "scheduled_new_reqs", [])[:6]
        ],
        "cached_reqs": {
            "req_ids": getattr(scheduled_cached_reqs, "req_ids", [])[:6],
            "num_computed_tokens": describe_value(
                getattr(scheduled_cached_reqs, "num_computed_tokens", [])
            ),
            "new_block_ids": describe_value(
                getattr(scheduled_cached_reqs, "new_block_ids", [])
            ),
        },
        "num_scheduled_tokens": describe_value(
            getattr(scheduler_output, "num_scheduled_tokens", {})
        ),
        "total_num_scheduled_tokens": getattr(
            scheduler_output, "total_num_scheduled_tokens", None
        ),
        "spec_decode_reqs": list(
            getattr(scheduler_output, "scheduled_spec_decode_tokens", {}).keys()
        )[:6],
        "encoder_reqs": list(
            getattr(scheduler_output, "scheduled_encoder_inputs", {}).keys()
        )[:6],
        "finished_req_ids": list(getattr(scheduler_output, "finished_req_ids", []))[:6],
        "preempted_req_ids": list(getattr(scheduler_output, "preempted_req_ids", []) or [])[:6],
        "new_block_ids_to_zero": describe_value(
            getattr(scheduler_output, "new_block_ids_to_zero", None)
        ),
    }


def summarize_model_runner_output(output: Any) -> dict[str, Any]:
    if output is None:
        return {"type": "None"}
    return {
        "type": type(output).__name__,
        **describe_attrs(
            output,
            (
                "req_ids",
                "req_id_to_index",
                "sampled_token_ids",
                "spec_token_ids",
                "logprobs",
                "prompt_logprobs_dict",
                "finished_sending",
                "num_nans_in_logits",
            ),
        ),
    }
