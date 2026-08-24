# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Best-effort shape tracing for selected Triton kernel launches."""

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch


_DEFAULT_DUMP_PATH = "/tmp/vllm_triton_kernel_shapes.txt"


def dump_triton_kernel_shapes(
    kernel: str,
    grid: tuple[int, ...],
    arguments: Mapping[str, Any],
    launch_config: Mapping[str, Any],
) -> None:
    """Append tensor metadata and launch configuration for one Triton launch.

    Set ``VLLM_TRITON_SHAPE_DUMP_PATH`` to choose a different output file.
    """
    serialized_args: dict[str, Any] = {}
    for name, value in arguments.items():
        if isinstance(value, torch.Tensor):
            serialized_args[name] = {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "device": str(value.device),
            }
        elif value is None:
            serialized_args[name] = None
        else:
            serialized_args[name] = value

    record = {
        "kernel": kernel,
        "grid": grid,
        "launch_config": launch_config,
        "arguments": serialized_args,
    }
    dump_path = Path(os.getenv("VLLM_TRITON_SHAPE_DUMP_PATH", _DEFAULT_DUMP_PATH))
    try:
        with dump_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, default=str) + "\n")
    except OSError:
        # Shape tracing must not interrupt serving when the dump path is unavailable.
        pass
