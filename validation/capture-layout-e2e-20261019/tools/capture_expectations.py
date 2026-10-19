"""Offline acceptance rules. Never import the selector/prepare implementation."""

import json
import re
from collections import Counter


SELECTION = "MoE capture selection audit: "
LAYOUT = "MoE capture layout audit: "


def expected_method(plan, tokens, capacity):
    if not plan["ep"] or plan["ep_world"] == 1 or plan["policy"] == "ALLGATHER":
        # LoRA overrides hardware policy, but not disabled EP.
        if plan["ep"] and plan["ep_world"] > 1 and plan["lora"]:
            return "ALLTOALL"
        return "ALLGATHER"
    if plan["lora"]:
        return "ALLTOALL"
    if plan["fused"] == 1 and plan["policy"] == "FUSED_OR_CAPACITY" and plan["ep_world"] <= 32:
        return "FUSED_MC2"
    if plan["fused"] != 0:
        raise NotImplementedError("Fused selection needs a hardware/quantization acceptance rule")
    small = tokens is None or tokens <= capacity
    policy = plan["policy"]
    if policy == "FUSED_OR_CAPACITY":
        return "MC2" if small else "ALLTOALL"
    if policy == "CAPACITY_AND_EXPERT_DENSITY":
        return "MC2" if small and plan["ep_world"] >= 16 and plan["experts"] // plan["ep_world"] <= 24 else "ALLGATHER"
    if policy == "CAPACITY_AND_WORLD_SIZE":
        world = plan["dp"] * plan["tp"]  # This acceptance plan supports PP=PCP=1.
        if small and world > 1:
            return "MC2"
        return "ALLGATHER" if world <= plan["topk"] else "ALLTOALL"
    raise NotImplementedError(f"Unknown policy: {policy}")


def expected_layout(event, plan):
    """Use input sizes and scenario config, never the emitted ranges/shards."""
    method, sp = event["method"], plan["sp"]
    dp, tp, rank = plan["dp"], plan["tp"], event["tp"]
    counts = event["dp_tokens"]
    if len(counts) != dp or any(n < 0 for n in counts):
        raise ValueError("Invalid DP token counts")
    local = counts[event["dp"]]
    before = event["before_rows"]
    if method == "ALLGATHER":
        if sp:
            sizes = event["dp_local_sizes"]
            if sizes is None:
                # No DP metadata: EP all-gather concatenates equal TP shards.
                rows = before * tp if dp == 1 else sum(counts)
                start = sum(counts[:event["dp"]])
            else:
                if len(sizes) != dp * tp:
                    raise ValueError("EP local_sizes do not match DP*TP")
                rows = sum(sizes)
                start = sum(sizes[:event["dp"] * tp])
        else:
            if before != local:
                raise ValueError(f"ALLGATHER input {before} != local tokens {local}")
            rows = max(counts) * dp if dp > 1 else before
            start = max(counts) * event["dp"] if dp > 1 else 0
        return "PrepareAndFinalizeWithAllGather", rows, [], [[start, local]]
    if method == "ALLTOALL":
        total = before * tp if sp else max(before, tp)
        sizes = [total // tp + int(i < total % tp) for i in range(tp)]
        return "PrepareAndFinalizeWithAll2All", sizes[rank], sizes if tp > 1 else [], [[0, local]]
    if method in {"MC2", "FUSED_MC2"}:
        padded = ((max(counts) + tp - 1) // tp) * tp
        if event["padded_rows"] != padded:
            raise ValueError(f"MC2 padding {event['padded_rows']} != expected {padded}")
        physical = max(before, padded // tp) if sp else max(before, padded) // tp
        ranges = [[i * physical, min(before, max(0, local - i * before))] for i in range(tp)] if sp else [[0, local]]
        return "PrepareAndFinalizeWithMC2", physical, [physical] * tp if tp > 1 else [], ranges
    raise NotImplementedError(f"Unknown layout method: {method}")


def audit_expectations(text, plan):
    errors, missing = [], []
    latest, selected_ranks, layout_ranks = {}, set(), set()
    frame_layers = {}
    summaries = Counter()
    selections = Counter()
    tokens_seen = set()
    selection_count = layout_count = 0
    for line in text.splitlines():
        marker = SELECTION if SELECTION in line else LAYOUT if LAYOUT in line else None
        if marker is None:
            continue
        try:
            event = json.loads(line.split(marker, 1)[1])
            rank = (event["dp"], event["tp"])
            if not (0 <= rank[0] < plan["dp"] and 0 <= rank[1] < plan["tp"]):
                raise ValueError(f"Unexpected rank {rank}")
            if marker == SELECTION:
                selection_count += 1
                if rank in latest and "layers" in plan:
                    absent = set(range(plan["layers"])) - frame_layers[rank]
                    if absent:
                        missing.append(f"Incomplete forward rank={rank}: missing layers {sorted(absent)}")
                frame_layers[rank] = set()
                for field in ("ep", "ep_world", "lora", "fused", "policy"):
                    if event[field] != plan[field]:
                        raise ValueError(f"Runtime {field}={event[field]} != scenario {plan[field]}")
                if event["draft"]:
                    raise NotImplementedError("Draft model acceptance is not implemented")
                if event["capacity"] != plan["capacity"]:
                    raise ValueError(f"Runtime MC2 capacity={event['capacity']} != scenario={plan['capacity']}")
                wanted = expected_method(plan, event["tokens"], plan["capacity"])
                selections[(rank, event["tokens"], wanted, event["method"])] += 1
                if event["method"] != wanted:
                    raise ValueError(f"Selection rank={rank} tokens={event['tokens']}: expected {wanted}, got {event['method']}")
                latest[rank] = event
                tokens_seen.add(event["tokens"])
                selected_ranks.add(rank)
                continue
            layout_count += 1
            layer = re.search(r"(?:^|\.)layers\.(\d+)(?:\.|$)", event["layer"])
            if layer and rank in frame_layers:
                layer_id = int(layer.group(1))
                if layer_id in frame_layers[rank]:
                    raise ValueError(f"Layer {layer_id} repeated within one forward rank={rank}")
                frame_layers[rank].add(layer_id)
            if event["sp"] != plan["sp"]:
                raise ValueError("Runtime SP differs from scenario")
            if event["graph"] != "NONE":
                raise NotImplementedError("Strict acceptance currently requires eager graph=NONE")
            selection = latest.get(rank)
            if selection is None:
                missing.append(f"No preceding selector event for rank={rank}")
            elif event["method"] != selection["method"]:
                raise ValueError("Prepare method differs from preceding selector result")
            elif selection["tokens"] != max(event["dp_tokens"]):
                raise ValueError("Selector token count differs from maximum DP token count")
            wanted = expected_layout(event, plan)
            actual = (event["prepare"], event["router_rows"], event["shards"], event["ranges"])
            if actual != wanted:
                raise ValueError(f"Layout {event['layer']} rank={rank}: expected {wanted}, got {actual}")
            if event["gather"] != bool(wanted[2]):
                raise ValueError("Capture gather group presence differs from expected shards")
            layout_ranks.add(rank)
            summaries[(event["method"], rank, event["before_rows"], wanted[1], str(wanted[2]), str(wanted[3]))] += 1
        except NotImplementedError as exc:
            missing.append(str(exc))
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(str(exc))
    required = {(d, t) for d in range(plan["dp"]) for t in range(plan["tp"])}
    if selected_ranks != required:
        missing.append(f"Selector ranks missing: {sorted(required - selected_ranks)}")
    if layout_ranks != required:
        missing.append(f"Layout ranks missing: {sorted(required - layout_ranks)}")
    if "layers" in plan:
        for rank, seen in frame_layers.items():
            absent = set(range(plan["layers"])) - seen
            if absent:
                missing.append(f"Final forward log incomplete rank={rank}: missing layers {sorted(absent)}")
    absent_tokens = set(plan.get("required_selector_tokens", [])) - tokens_seen
    if absent_tokens:
        missing.append(f"Selector boundary inputs not observed: {sorted(absent_tokens)}")
    return {"errors": sorted(set(errors)), "coverage_missing": sorted(set(missing)),
            "selection_events": selection_count, "layout_events": layout_count,
            "selections": [{"rank": k[0], "tokens": k[1], "expected": k[2], "actual": k[3], "calls": n}
                           for k, n in selections.items()],
            "layouts": [{"method": k[0], "rank": k[1], "before_rows": k[2], "expected_router_rows": k[3],
                         "expected_shards": k[4], "expected_ranges": k[5], "calls": n}
                        for k, n in summaries.items()]}
