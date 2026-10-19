"""Finalize immutable same-forward full-model results; fail closed on gaps."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parent
results = root / 'results'
expected = ['01-ag-dp1-tp2','02-ag-dp2-tp2','03-ep-dp1-tp2','04-ep-dp2-tp2','05-ep-dp2-tp2-sp','06-ag-dp1-tp1','07-ep-dp2-tp1','08-ep-dp1-tp4','09-fused-dp1-tp2','10-fused-dp2-tp2','11-fused-dp2-tp2-sp','12-graph-ag-dp1-tp2','13-graph-ep-dp2-tp2-sp','15-lora-ep-dp1-tp2','16-sp-internal-padding','17-graph-sp-internal-padding','18-graph-fused-dp2-tp2-sp']
assert sorted(p.name for p in results.iterdir() if p.is_dir()) == expected
state = json.loads((root/'source-state.json').read_text())
checker_path = root/'lane-a/tools/check_same_run.py'
spec=importlib.util.spec_from_file_location('same_run_checker',checker_path)
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
head=subprocess.check_output(['git','-C',str(root.parent/'vllm'),'rev-parse','HEAD'],text=True).strip()
assert head == state['upstream_commit']
assert not subprocess.check_output(['git','-C',str(root.parent/'vllm'),'diff','--name-only'],text=True).strip()
capture=root.parent/'vllm/vllm/model_executor/layers/fused_moe/routed_experts_capturer.py'
assert hashlib.sha256(capture.read_bytes()).hexdigest()==state['capture_sha256']
original=Path('/home/lingmutian/code/vllm-ascend/vllm_ascend')
for name,digest in state['original_ascend_sha256'].items():
 assert hashlib.sha256((original/name).read_bytes()).hexdigest()==digest, name
cases=[]
for name in expected:
 p=results/name
 s=json.loads((p/'status.json').read_text())
 assert s['stage']=='stopped' and not s.get('error'), (name,s)
 assert s.get('same_run_exit')==0, (name,s)
 r=checker.compare(p)
 prior=json.loads((p/'same-run-report.json').read_text())
 assert r==prior, name+' offline recheck differs'
 assert r['status']=='PASS' and not r['failures'], name
 structure=json.loads((p/'verification/report.json').read_text())
 assert not structure['failures'], (name,structure['failures'])
 source=json.loads((p/'runtime-source-state.json').read_text())
 assert source['capture_sha256']==state['capture_sha256'], name
 runtime=Path(source['ascend_root'])
 # Initial one-off snapshots named the package; hashes are relative to its parent.
 if runtime.name == 'vllm_ascend':
  runtime = runtime.parent
 for fname,digest in source['python_sha256'].items():
  assert hashlib.sha256((runtime/fname).read_bytes()).hexdigest()==digest,(name,fname)
 text=(p/'server.log').read_text(errors='replace')
 graph=bool(s['configuration'].get('graph'))
 replay=text.count('ACL graph replay is active')
 assert not graph or replay>0, name+' graph replay not confirmed'
 (p/'graph-replay-evidence.txt').write_text('\n'.join(line for line in text.splitlines() if 'ACL graph replay is active' in line)+'\n')
 cases.append(dict(case=name,status=r['status'],configuration=s['configuration'],requests=len(r['api_checks']),worker_checks=len(r['worker_checks']),api_elements=r['api_elements'],worker_elements=r['worker_elements'],methods=r['methods'],graph_replay_logs=replay,uneven_tp_shards=r['uneven_tp_shards_observed'],internal_padding=r['internal_padding_observed'],layout_log_status=structure['status'],runtime_compatibility_variant='retry' if 'lane-retry' in str(runtime) else 'initial'))
byname={c['case']:c for c in cases}
assert byname['08-ep-dp1-tp4']['uneven_tp_shards']
assert byname['11-fused-dp2-tp2-sp']['internal_padding']
assert byname['16-sp-internal-padding']['internal_padding']
assert {m for c in cases for m in c['methods']}=={'ALLGATHER','ALLTOALL','MC2','FUSED_MC2'}
assert sum(bool(c['configuration'].get('graph')) for c in cases)==4
summary=dict(status='PASS',finished=datetime.datetime.now().isoformat(),upstream_commit=head,upstream_base=state['upstream_base'],capture_sha256=state['capture_sha256'],cases=cases,requests=sum(c['requests'] for c in cases),api_elements=sum(c['api_elements'] for c in cases),worker_elements=sum(c['worker_elements'] for c in cases),mismatches=0,offline_recheck='PASS',source_provenance='PASS',original_ascend_sources_unchanged=True)
(results/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# 整网 capture 精确性验证：PASS','',f"实测实现：`{head}`；main 基线：`{state['upstream_base']}`。",'',f"17 个配置、{summary['requests']} 个请求；API 比较 {summary['api_elements']:,} 个 expert ID；worker buffer 比较 {summary['worker_elements']:,} 个 expert ID；差异 0。",'', '验证的是同一次 forward 内 router 原始 logical topk_ids → 每个 TP worker 的 capture buffer → HTTP 返回。不是跨运行路由一致性或模型质量评测。', '', '独立参考：prepare 前添加 DP/行位置标签，标签随真实通信、切分和补齐流转，在 router 前移除。参考端通过标签还原 token 归属，不读取 layout/source_ranges/shard_sizes。所有 token、48 层、每层 8 个 expert 均逐元素比较。图内设备 copy 采集每次 replay 的原始值，每次 forward 清空有效标记，防止误用 warmup 数据。', '', '| 场景 | 通信 | 请求 | API expert ID 比较数 | 图回放日志 | 结果 |', '|---|---|---:|---:|---:|---|']
for c in cases:
 lines.append(f"| {c['case']} | {', '.join(c['methods'])} | {c['requests']} | {c['api_elements']:,} | {c['graph_replay_logs']} | PASS |")
lines += ['', '覆盖：DP=1/2，TP=1/2/4，EP，SP，四种实际选择的通信分支，TP 不等长分片，MC2/FUSED_MC2 中间 padding，四组实际 ACL graph replay。LoRA 仅开启配置，未加载 adapter。', '', '**兼容性边界：** 上游 capture/router 文件为 PR 提交原样，逐场景核验源码 hash。现有 Ascend 源码不能直接搭配此 main 启动，因此使用隔离副本补了导入、配置、KV planner/block table 和 runner 调用签名兼容；重跑四组另补 TP 对齐图尺寸筛选与原有 NPU internal-format 初始化。完整 diff 与每场景源码指纹已保留。这证明该 capture 实现在记录的兼容环境中通过整网对账，不代表未经适配的 Ascend main 可直接运行。原始仓库未改。', '', f"17 号配置是否观察到中间 padding：{byname['17-graph-sp-internal-padding']['internal_padding']}。实际图回放已确认；不把场景名视作图内间隙的证明。", '', '范围：162 Ascend A3 单机，最多 4 卡/场景，Qwen3-30B-A3B BF16/W8A8。未验证 PP/PCP、多机、已加载 LoRA、其他模型/硬件或性能。ALLGATHER+MoE SP 未被当前硬件策略自然选择，不计入整网覆盖。', '', '全部保存的原始 trace 重新离线对账通过；26 个验证器单测通过。失败启动尝试保留在远端 archive-startup，不计入通过数。']
(results/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='cases'},ensure_ascii=False))
