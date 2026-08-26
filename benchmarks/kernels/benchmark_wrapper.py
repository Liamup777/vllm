#!/usr/bin/env python3
"""Benchmark a CUDA wrapper or raw Triton kernel with JSON tensor inputs.

The input can be one JSON object, a JSON array, or JSON Lines. Tensor values
are specified by shape, dtype, device, and an optional initializer.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import math
import statistics
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import torch


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Load benchmark cases from JSON or JSON Lines."""
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Input file is empty: {path}")
    try:
        document = json.loads(content)
    except json.JSONDecodeError:
        document = [json.loads(line) for line in content.splitlines() if line.strip()]

    if isinstance(document, dict):
        return [document]
    if isinstance(document, list) and all(isinstance(case, dict) for case in document):
        return document
    raise ValueError("Input must be a JSON object, an array of objects, or JSONL objects")


def select_cases(
    cases: list[dict[str, Any]], kernel: str | None, max_cases: int | None
) -> list[dict[str, Any]]:
    """Select cases for one kernel from a capture."""
    if max_cases is not None and max_cases <= 0:
        raise ValueError("max-cases must be a positive integer")
    selected = cases if kernel is None else [case for case in cases if case.get("kernel") == kernel]
    if not selected:
        raise ValueError(f"No input records found for kernel: {kernel}")
    return selected[:max_cases]


def resolve_wrapper(path: str) -> Callable[..., Any]:
    """Resolve a ``file.py:function`` or ``module.path:function`` callable."""
    if ":" not in path:
        raise ValueError(f"Wrapper must use 'file.py:function' syntax, got: {path!r}")
    source, attribute_path = path.rsplit(":", 1)
    source_path = Path(source)
    if source_path.suffix == ".py" or source_path.exists():
        source_path = source_path.expanduser().resolve()
        spec = importlib.util.spec_from_file_location(
            f"_operator_benchmark_{source_path.stem}", source_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import wrapper file: {source_path}")
        value: Any = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(value)
    else:
        value = importlib.import_module(source)
    for attribute in attribute_path.split("."):
        value = getattr(value, attribute)
    if not callable(value):
        raise TypeError(f"Resolved wrapper is not callable: {path}")
    return value


def make_tensor(spec: dict[str, Any], default_device: str) -> torch.Tensor:
    """Materialize one tensor specification on CUDA."""
    shape = spec.get("shape")
    if not isinstance(shape, list) or not all(isinstance(size, int) and size >= 0 for size in shape):
        raise ValueError(f"Tensor shape must be a list of non-negative integers: {shape!r}")
    dtype_name = spec.get("dtype", "torch.float32").removeprefix("torch.")
    dtype = getattr(torch, dtype_name, None)
    if not isinstance(dtype, torch.dtype):
        raise ValueError(f"Unsupported torch dtype: {spec.get('dtype')}")

    device = spec.get("device", default_device)
    initializer = spec.get("initializer", "zeros")
    if initializer == "zeros":
        return torch.zeros(shape, dtype=dtype, device=device)
    if initializer == "ones":
        return torch.ones(shape, dtype=dtype, device=device)
    if initializer == "full":
        return torch.full(shape, spec["value"], dtype=dtype, device=device)
    if initializer == "rand":
        return torch.rand(shape, dtype=dtype, device=device)
    if initializer == "randn":
        return torch.randn(shape, dtype=dtype, device=device)
    if initializer == "randint":
        return torch.randint(spec.get("low", 0), spec["high"], shape, dtype=dtype, device=device)
    if initializer == "arange":
        return torch.arange(math.prod(shape), dtype=dtype, device=device).reshape(shape)
    raise ValueError(f"Unsupported tensor initializer: {initializer!r}")


def materialize(value: Any, default_device: str) -> Any:
    """Recursively materialize tensor specifications."""
    if isinstance(value, dict) and "shape" in value:
        return make_tensor(value, default_device)
    if isinstance(value, dict):
        return {key: materialize(item, default_device) for key, item in value.items()}
    if isinstance(value, list):
        return [materialize(item, default_device) for item in value]
    return value


def normalize_triton_arguments(target: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    """Map captured names such as ``logits`` to Triton ``logits_ptr`` names."""
    arg_names = getattr(target, "arg_names", None)
    if not isinstance(arg_names, (list, tuple)):
        return arguments
    normalized = dict(arguments)
    for arg_name in arg_names:
        if arg_name.endswith("_ptr") and arg_name not in normalized:
            captured_name = arg_name.removesuffix("_ptr")
            if captured_name in normalized:
                normalized[arg_name] = normalized.pop(captured_name)
    return normalized


def percentile(values: Sequence[float], percent: float) -> float:
    """Return an interpolated percentile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(latencies_ms: Sequence[float]) -> dict[str, float]:
    """Summarize CUDA event latencies."""
    return {
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "mean_ms": statistics.fmean(latencies_ms),
        "p50_ms": percentile(latencies_ms, 50),
        "p90_ms": percentile(latencies_ms, 90),
        "p99_ms": percentile(latencies_ms, 99),
    }


def benchmark_case(case: dict[str, Any]) -> dict[str, Any]:
    """Benchmark one wrapper or raw Triton kernel case."""
    wrapper_path = case.get("wrapper")
    if not isinstance(wrapper_path, str):
        raise ValueError("Each case must define a string 'wrapper'")
    device = case.get("device", "cuda:0")
    warmup = case.get("warmup", 10)
    profiling_rounds = case.get("profiling_rounds", 100)
    mode = case.get("mode", "wrapper")
    if not str(device).startswith("cuda"):
        raise ValueError(f"This benchmark requires a CUDA device, got: {device}")
    if not isinstance(warmup, int) or warmup < 0:
        raise ValueError("warmup must be a non-negative integer")
    if not isinstance(profiling_rounds, int) or profiling_rounds <= 0:
        raise ValueError("profiling-rounds must be a positive integer")

    torch.cuda.set_device(device)
    target = resolve_wrapper(wrapper_path)
    args = materialize(case.get("args", []), device)
    kwargs = materialize(case.get("kwargs", case.get("arguments", {})), device)
    if not isinstance(args, list) or not isinstance(kwargs, dict):
        raise ValueError("args must be a list and kwargs must be an object")

    if mode == "wrapper":
        invoke = lambda: target(*args, **kwargs)
    elif mode == "triton":
        grid = case.get("grid")
        if not isinstance(grid, list) or not grid or not all(isinstance(size, int) and size > 0 for size in grid):
            raise ValueError(f"Triton mode requires a non-empty positive grid, got: {grid!r}")
        launcher = target[tuple(grid)]
        triton_kwargs = normalize_triton_arguments(target, kwargs)
        invoke = lambda: launcher(*args, **triton_kwargs)
    else:
        raise ValueError(f"Unsupported benchmark mode: {mode}")

    for _ in range(warmup):
        invoke()
    torch.cuda.synchronize()

    events: list[tuple[Any, Any]] = []
    for _ in range(profiling_rounds):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        invoke()
        end.record()
        events.append((start, end))
    torch.cuda.synchronize()
    latencies_ms = [start.elapsed_time(end) for start, end in events]
    return {
        "name": case.get("name", wrapper_path),
        "wrapper": wrapper_path,
        "mode": mode,
        "kernel": case.get("kernel"),
        "grid": case.get("grid") if mode == "triton" else None,
        "device": device,
        "warmup": warmup,
        "profiling_rounds": profiling_rounds,
        "latencies_ms": latencies_ms,
        "summary": summarize(latencies_ms),
    }


def replace_tensor_devices(value: Any, device: str) -> Any:
    """Apply a command-line device override to every tensor specification."""
    if isinstance(value, dict) and "shape" in value:
        return {**value, "device": device}
    if isinstance(value, dict):
        return {key: replace_tensor_devices(item, device) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_tensor_devices(item, device) for item in value]
    return value


def override_case(case: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Apply command-line overrides to one case."""
    result = dict(case)
    for key in ("wrapper", "mode", "device", "warmup", "profiling_rounds"):
        value = getattr(args, key)
        if value is not None:
            result[key] = value
    if args.device is not None:
        for key in ("args", "kwargs", "arguments"):
            if key in result:
                result[key] = replace_tensor_devices(result[key], args.device)
    return result


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, required=True)
    parser.add_argument("--wrapper", required=True, help="Wrapper or Triton kernel (file.py:function)")
    parser.add_argument("--mode", choices=("wrapper", "triton"), default="wrapper")
    parser.add_argument("--kernel", help="Select this kernel from a mixed capture")
    parser.add_argument("--max-cases", type=int, help="Benchmark only the first N selected records")
    parser.add_argument("--device", default="cuda:0", help="CUDA device")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup rounds")
    parser.add_argument("--profiling-rounds", type=int, default=100, help="Measured rounds")
    parser.add_argument("--output", type=Path, help="Write full JSON results to this path")
    return parser.parse_args()


def main() -> None:
    """Run selected benchmark cases."""
    args = parse_args()
    cases = select_cases(load_cases(args.input_file), args.kernel, args.max_cases)
    results = [benchmark_case(override_case(case, args)) for case in cases]
    encoded = json.dumps(results, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
