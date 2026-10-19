# 整网 capture 精确性验证：PASS

实测实现：`bfed1cb65d2ae8c37b9ada7b45191bbb01224679`；main 基线：`852989f580820849113d67d13fd8053e279d0444`。

17 个配置、144 个请求；API 比较 16,048,896 个 expert ID；worker buffer 比较 31,912,320 个 expert ID；差异 0。

验证的是同一次 forward 内 router 原始 logical topk_ids → 每个 TP worker 的 capture buffer → HTTP 返回。不是跨运行路由一致性或模型质量评测。

独立参考：prepare 前添加 DP/行位置标签，标签随真实通信、切分和补齐流转，在 router 前移除。参考端通过标签还原 token 归属，不读取 layout/source_ranges/shard_sizes。所有 token、48 层、每层 8 个 expert 均逐元素比较。图内设备 copy 采集每次 replay 的原始值，每次 forward 清空有效标记，防止误用 warmup 数据。

| 场景 | 通信 | 请求 | API expert ID 比较数 | 图回放日志 | 结果 |
|---|---|---:|---:|---:|---|
| 01-ag-dp1-tp2 | ALLGATHER | 4 | 802,560 | 0 | PASS |
| 02-ag-dp2-tp2 | ALLGATHER | 8 | 1,014,528 | 0 | PASS |
| 03-ep-dp1-tp2 | MC2, ALLTOALL | 7 | 829,056 | 0 | PASS |
| 04-ep-dp2-tp2 | MC2, ALLTOALL | 11 | 1,041,024 | 0 | PASS |
| 05-ep-dp2-tp2-sp | MC2, ALLTOALL | 11 | 1,041,024 | 0 | PASS |
| 06-ag-dp1-tp1 | ALLGATHER | 4 | 802,560 | 0 | PASS |
| 07-ep-dp2-tp1 | MC2, ALLTOALL | 11 | 1,041,024 | 0 | PASS |
| 08-ep-dp1-tp4 | MC2, ALLTOALL | 7 | 829,056 | 0 | PASS |
| 09-fused-dp1-tp2 | FUSED_MC2 | 4 | 802,560 | 0 | PASS |
| 10-fused-dp2-tp2 | FUSED_MC2 | 8 | 1,014,528 | 0 | PASS |
| 11-fused-dp2-tp2-sp | FUSED_MC2 | 8 | 1,014,528 | 0 | PASS |
| 12-graph-ag-dp1-tp2 | ALLGATHER | 4 | 802,560 | 1 | PASS |
| 13-graph-ep-dp2-tp2-sp | MC2, ALLTOALL | 11 | 1,041,024 | 2 | PASS |
| 15-lora-ep-dp1-tp2 | ALLTOALL | 4 | 802,560 | 0 | PASS |
| 16-sp-internal-padding | MC2, ALLTOALL | 17 | 1,077,888 | 0 | PASS |
| 17-graph-sp-internal-padding | MC2, ALLTOALL | 17 | 1,077,888 | 2 | PASS |
| 18-graph-fused-dp2-tp2-sp | FUSED_MC2 | 8 | 1,014,528 | 2 | PASS |

覆盖：DP=1/2，TP=1/2/4，EP，SP，四种实际选择的通信分支，TP 不等长分片，MC2/FUSED_MC2 中间 padding，四组实际 ACL graph replay。LoRA 仅开启配置，未加载 adapter。

**兼容性边界：** 上游 capture/router 文件为 PR 提交原样，逐场景核验源码 hash。现有 Ascend 源码不能直接搭配此 main 启动，因此使用隔离副本补了导入、配置、KV planner/block table 和 runner 调用签名兼容；重跑四组另补 TP 对齐图尺寸筛选与原有 NPU internal-format 初始化。完整 diff 与每场景源码指纹已保留。这证明该 capture 实现在记录的兼容环境中通过整网对账，不代表未经适配的 Ascend main 可直接运行。原始仓库未改。

17 号配置是否观察到中间 padding：False。实际图回放已确认；不把场景名视作图内间隙的证明。

范围：162 Ascend A3 单机，最多 4 卡/场景，Qwen3-30B-A3B BF16/W8A8。未验证 PP/PCP、多机、已加载 LoRA、其他模型/硬件或性能。ALLGATHER+MoE SP 未被当前硬件策略自然选择，不计入整网覆盖。

全部保存的原始 trace 重新离线对账通过；26 个验证器单测通过。失败启动尝试保留在远端 archive-startup，不计入通过数。
