# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import torch

T = TypeVar("T")


def bench_gpu(fn: Callable[[], T], warmup: int, repeat: int) -> tuple[float, T | None]:
    out = None
    for _ in range(warmup):
        out = fn()
    torch.accelerator.synchronize()

    start = time.perf_counter()
    for _ in range(repeat):
        out = fn()
    torch.accelerator.synchronize()
    return (time.perf_counter() - start) * 1e6 / repeat, out
