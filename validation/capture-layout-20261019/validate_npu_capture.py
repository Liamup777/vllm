"""Real Ascend prepare -> router -> capture checks against independent CPU routes.

Run under torchrun with --nproc_per_node=2*DP, --dp=DP. This is a component
integration test; it does not load a model or simulate an HTTP serving test.
"""

import argparse
import datetime
import functools
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import torch
import torch.distributed as dist
import torch_npu

from vllm.forward_context import DPMetadata, ForwardContext, override_forward_context
from vllm.model_executor.layers.fused_moe.config import RoutingMethodType
from vllm.model_executor.layers.fused_moe.routed_experts_capturer import (
    RoutedExpertsCaptureLayout,
    RoutedExpertsCapturer,
)
from vllm.model_executor.layers.fused_moe.router.base_router import BaseRouter
from vllm_ascend.ascend_forward_context import _EXTRA_CTX
from vllm_ascend.ops.fused_moe.prepare_finalize import (
    PrepareAndFinalizeWithAll2All,
    PrepareAndFinalizeWithAllGather,
    PrepareAndFinalizeWithMC2,
)


class Group:
    def __init__(self, group):
        self.device_group = group

    def all_gather(self, value, dim=0):
        outputs = [torch.empty_like(value) for _ in range(dist.get_world_size(self.device_group))]
        dist.all_gather(outputs, value.contiguous(), group=self.device_group)
        return torch.cat(outputs, dim=dim)


class Router(BaseRouter):
    @property
    def routing_method_type(self):
        return RoutingMethodType.FUSED_TOPK

    def _compute_routing(self, hidden_states, router_logits, indices_type, *, input_ids=None):
        weights, ids = torch.topk(router_logits, 2, dim=-1)
        self.raw.copy_(ids)
        return weights, ids

    def _apply_eplb_mapping(self, ids):
        return ids + 100


def logits(rows, dp, version):
    token = torch.arange(rows).view(-1, 1)
    expert = torch.arange(16).view(1, -1)
    # Distinct logits within each row, so CPU and NPU tie-breaking is irrelevant.
    return ((token * 31 + expert * 7 + dp * 17 + version * 11) % 97).float()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dp', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rank = int(os.environ['RANK'])
    local_rank = int(os.environ['LOCAL_RANK'])
    torch.npu.set_device(local_rank)
    dist.init_process_group('hccl', timeout=datetime.timedelta(seconds=180))
    assert dist.get_world_size() == args.dp * 2
    tp_rank, dp_rank = rank % 2, rank // 2
    tp_group = dp_group = None
    for d in range(args.dp):
        group = dist.new_group([2*d, 2*d+1], backend='hccl')
        if d == dp_rank:
            tp_group = Group(group)
    for t in range(2):
        group = dist.new_group([2*d+t for d in range(args.dp)], backend='hccl')
        if t == tp_rank:
            dp_group = Group(group)
    counts = [5] if args.dp == 1 else [5, 13]
    n = counts[dp_rank]
    padded = (max(counts) + 1) // 2 * 2
    metadata = DPMetadata(torch.tensor(counts, dtype=torch.int32))
    context = ForwardContext({}, {}, {}, dp_metadata=metadata)
    config = SimpleNamespace(dp_rank=dp_rank, dp_size=args.dp, tp_group=tp_group,
                             dp_group=dp_group, pcp_size=1, is_sequence_parallel=False)
    results = []
    for name in ['allgather', 'alltoall', 'alltoall_sp', 'mc2', 'mc2_sp', 'empty_capture']:
        for mode in ['eager', 'graph']:
            classes = {'allgather': PrepareAndFinalizeWithAllGather,
                       'alltoall': PrepareAndFinalizeWithAll2All,
                       'mc2': PrepareAndFinalizeWithMC2}
            cls = classes[name.split('_')[0]] if name != 'empty_capture' else PrepareAndFinalizeWithAll2All
            prepare = cls.__new__(cls)
            prepare.moe_config = config
            prepare.tp_size, prepare.tp_rank, prepare.lora_context = 2, tp_rank, None
            sp = name.endswith('_sp')
            shard = (n + 1) // 2
            def local_input(version):
                full = logits(n, dp_rank, version)
                if sp:
                    full = torch.nn.functional.pad(full, (0, 0, 0, 2*shard-n))
                    full = full[tp_rank*shard:(tp_rank+1)*shard]
                return full
            input_logits = local_input(0).npu()
            hidden = torch.zeros((len(input_logits), 4), device='npu')
            with override_forward_context(context):
                _EXTRA_CTX.num_tokens = n
                _EXTRA_CTX.max_tokens_across_dp = max(counts)
                _EXTRA_CTX.padded_num_tokens = padded
                _EXTRA_CTX.mc2_mask = (torch.arange(padded, device='npu') < n)
            capturer = RoutedExpertsCapturer.__new__(RoutedExpertsCapturer)
            capturer.dp_rank, capturer.tp_size = dp_rank, 2
            capturer.device_buffer = torch.full((max(counts)+8, 2, 2), -1, device='npu', dtype=torch.int32)
            router = Router(top_k=2, global_num_experts=16, eplb_state=None)
            router.set_capture_fn(functools.partial(capturer.capture, 1))
            with override_forward_context(context):
                first = prepare.prepare(hidden, input_logits, replace_allreduce=sp, capture_enabled=True)
            router.raw = torch.empty((len(first.router_logits), 2), device='npu', dtype=torch.int64)
            def run():
                out = prepare.prepare(hidden, input_logits, replace_allreduce=sp, capture_enabled=True)
                layout = out.capture_layout
                if name == 'empty_capture':
                    layout = RoutedExpertsCaptureLayout((), layout.gather_group, layout.shard_sizes)
                return router.select_experts(out.hidden_states, out.router_logits, capture_layout=layout)
            with override_forward_context(context):
                run()
                run()
                torch.npu.synchronize()
                dist.barrier()
                if mode == 'graph':
                    graph = torch.npu.NPUGraph()
                    with torch.npu.graph(graph):
                        _, physical_ids = run()
                for version in [1, 2, 3]:
                    input_logits.copy_(local_input(version))
                    capturer.device_buffer.fill_(-1)
                    if mode == 'graph':
                        graph.replay()
                    else:
                        _, physical_ids = run()
                    torch.npu.synchronize()
                    torch.testing.assert_close(physical_ids.cpu(), router.raw.cpu()+100)
                    expected = torch.topk(logits(n, dp_rank, version), 2, dim=-1).indices.to(torch.int32)
                    actual = capturer.device_buffer.cpu()
                    rows = 0 if name == 'empty_capture' else n
                    if rows:
                        torch.testing.assert_close(actual[:rows, 1], expected)
                    assert bool((actual[:, 0] == -1).all())
                    assert bool((actual[rows:, 1] == -1).all())
                    results.append(dict(case=name, mode=mode, dp=dp_rank, tp=tp_rank,
                                        version=version, rows=rows, raw_rows=len(router.raw),
                                        expert_ids=rows*2, status='PASS'))
            dist.barrier()
            print(f'PASS dp={dp_rank} tp={tp_rank} {name} {mode}', flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    source = Path(__import__('inspect').getfile(RoutedExpertsCapturer))
    report = dict(rank=rank, dp=args.dp, tp=2, source=str(source),
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  torch=torch.__version__, torch_npu=torch_npu.__version__, results=results)
    (args.output/f'rank-{rank}.json').write_text(json.dumps(report, indent=2))
    dist.barrier()
    dist.destroy_process_group()


if __name__ == '__main__':
    main()
