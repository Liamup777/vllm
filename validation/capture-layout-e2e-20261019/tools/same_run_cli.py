"""Test-only CLI: trace raw router IDs and independently transported row labels.

Never consumes capture_layout. Extra logits columns carry exact base-64 labels
through the real prepare, then are removed before the router sees its logits.
Device copies execute inside captured graphs; CPU dumps happen after forward.
"""
from dataclasses import replace
from pathlib import Path
import json
import logging
import re

import numpy as np
import torch

from vllm.model_executor.layers.fused_moe.routed_experts_capturer import RoutedExpertsCapturer
from vllm_ascend.ops.fused_moe.moe_comm_method import MoECommMethod
from vllm_ascend.ops.fused_moe.routed_experts import AscendRoutedExperts
from vllm_ascend.worker.v2.model_runner import NPUModelRunner
from vllm_ascend.ascend_forward_context import _EXTRA_CTX

ROOT = Path(__file__).with_name('same-run-active.json')
SETTINGS = json.loads(ROOT.read_text())
TRACE = Path(SETTINGS['trace'])
TRACE.mkdir(parents=True, exist_ok=True)
STATE = {'slots': {}, 'tags': None, 'capturer': None, 'step': 0}
_original_prepare = MoECommMethod.prepare
_original_capture = RoutedExpertsCapturer.capture
_original_execute = NPUModelRunner.execute_model
_original_select = AscendRoutedExperts._select_experts


def prepare(self, hidden_states, router_logits, replace_allreduce=False, **kwargs):
    n, width = router_logits.shape
    # SP input is already a contiguous TP shard of the local padded token table.
    tp = self.moe_config.tp_group.rank_in_group
    offset = tp * n if replace_allreduce else 0
    rows = torch.arange(offset, offset + n, device=router_logits.device, dtype=torch.int32)
    labels = torch.stack((torch.full_like(rows, self.moe_config.dp_rank + 1),
                          rows // 64 + 1, rows % 64 + 1), dim=1).to(router_logits.dtype)
    out = _original_prepare(self, hidden_states, torch.cat((router_logits, labels), dim=1),
                            replace_allreduce=replace_allreduce, **kwargs)
    STATE['tags'] = out.router_logits[:, width:].contiguous()
    STATE['method'] = _EXTRA_CTX.moe_comm_type.name
    return replace(out, router_logits=out.router_logits[:, :width].contiguous())


def select(self, *args, **kwargs):
    match = re.search(r"(?:^|\.)layers\.(\d+)(?:\.|$)", self.layer_name)
    if match is None:
        raise RuntimeError(f'Cannot independently identify MoE layer: {self.layer_name}')
    STATE['logical_layer'] = int(match.group(1))
    return _original_select(self, *args, **kwargs)


def capture(self, layer_id, topk_ids, *, layout=None):
    if layer_id != STATE['logical_layer']:
        raise RuntimeError(f"Capture layer {layer_id} != actual MoE layer {STATE['logical_layer']}")
    tags = STATE['tags']
    if tags is None or tags.shape != (len(topk_ids), 3):
        raise RuntimeError('Missing independent token labels at raw router boundary')
    key = (layer_id, len(topk_ids), STATE['method'])
    slot = STATE['slots'].get(key)
    if slot is None:
        slot = {'raw': torch.empty_like(topk_ids), 'tags': torch.empty_like(tags),
                'active': torch.zeros((), device=topk_ids.device, dtype=torch.int32),
                'layer': layer_id, 'method': STATE['method']}
        STATE['slots'][key] = slot
    # These are accelerator operations, including during actual graph replay.
    slot['raw'].copy_(topk_ids)
    slot['tags'].copy_(tags)
    slot['active'].fill_(1)
    STATE['capturer'] = self
    result = _original_capture(self, layer_id, topk_ids, layout=layout)
    if layout is not None:
        from vllm.distributed import get_tp_group
        logging.getLogger("vllm.model_executor.layers.fused_moe.routed_experts_capturer").debug(
            "Routed-experts capture layer=%s dp_rank=%s tp_rank=%s input_rows=%s rows=%s shards=%s ranges=%s",
            layer_id, self.dp_rank, get_tp_group().rank_in_group, len(topk_ids),
            sum(length for _, length in layout.source_ranges), layout.shard_sizes, layout.source_ranges)
    return result


@torch.inference_mode()
def execute(self, scheduler_output, *args, **kwargs):
    for slot in STATE['slots'].values():
        slot['active'].zero_()
    STATE['step'] += 1
    output = _original_execute(self, scheduler_output, *args, **kwargs)
    state = self.execute_model_state
    if kwargs.get('dummy_run', False) or kwargs.get('is_profile', False) or state is None:
        return output
    batch = state.input_batch
    if not batch.req_ids or not scheduler_output.total_num_scheduled_tokens:
        return output
    capturer = STATE['capturer']
    if capturer is None:
        raise RuntimeError('No raw router tracing installed')
    tp = self.parallel_config.tensor_parallel_size
    from vllm.distributed import get_tp_group
    rank = get_tp_group().rank_in_group
    dp = self.parallel_config.data_parallel_rank
    stem = f'dp{dp}-tp{rank}-step{STATE["step"]:06d}'
    arrays = {}
    slots = []
    for slot in STATE['slots'].values():
        if not int(slot['active'].cpu().item()):
            continue
        i = len(slots)
        arrays[f'raw_{i}'] = slot['raw'].cpu().numpy()
        arrays[f'tags_{i}'] = slot['tags'].float().cpu().numpy()
        slots.append({'layer': slot['layer'], 'method': slot['method']})
    n = int(batch.query_start_loc_np[len(batch.req_ids)])
    arrays['captured'] = capturer.device_buffer[:n].cpu().numpy()
    metadata = dict(instrumentation_version=2, dp=dp, tp=rank, tp_size=tp, step=STATE['step'], slots=slots,
                    request_ids=list(batch.req_ids),
                    starts=batch.num_computed_tokens_np[:len(batch.req_ids)].tolist(),
                    boundaries=batch.query_start_loc_np[:len(batch.req_ids)+1].tolist())
    np.savez_compressed(TRACE / f'{stem}.npz', **arrays)
    (TRACE / f'{stem}.json').write_text(json.dumps(metadata))
    return output


AscendRoutedExperts._select_experts = select
MoECommMethod.prepare = prepare
RoutedExpertsCapturer.capture = capture
NPUModelRunner.execute_model = execute

if __name__ == '__main__':
    from vllm.entrypoints.cli.main import main
    main()
