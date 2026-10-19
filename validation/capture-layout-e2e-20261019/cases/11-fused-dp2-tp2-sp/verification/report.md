# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'FUSED_MC2': 9216}
Matched layer calls: 9216

- concurrent-129: PASS, shape=[136, 48, 8], seconds=1.515
- concurrent-3: PASS, shape=[10, 48, 8], seconds=1.516
- concurrent-385: PASS, shape=[392, 48, 8], seconds=1.514
- concurrent-7: PASS, shape=[14, 48, 8], seconds=1.513
- long: PASS, shape=[2056, 48, 8], seconds=1.574
- short-1: PASS, shape=[8, 48, 8], seconds=1.391
- short-5: PASS, shape=[12, 48, 8], seconds=1.581
- short-7: PASS, shape=[14, 48, 8], seconds=1.458

Strict selection events: 192; layout events: 9216

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (1, 0) | 1 | FUSED_MC2 | FUSED_MC2 | 37 |
| (1, 1) | 1 | FUSED_MC2 | FUSED_MC2 | 37 |
| (0, 1) | 1 | FUSED_MC2 | FUSED_MC2 | 37 |
| (0, 0) | 1 | FUSED_MC2 | FUSED_MC2 | 37 |
| (0, 0) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 388 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 388 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 388 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 388 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 2 | FUSED_MC2 | FUSED_MC2 | 7 |
| (1, 1) | 2 | FUSED_MC2 | FUSED_MC2 | 7 |
| (0, 0) | 2 | FUSED_MC2 | FUSED_MC2 | 7 |
| (1, 0) | 2 | FUSED_MC2 | FUSED_MC2 | 7 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| FUSED_MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 1776 |
| FUSED_MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 1776 |
| FUSED_MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 1776 |
| FUSED_MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 1776 |
| FUSED_MC2 | (0, 0) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| FUSED_MC2 | (0, 1) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| FUSED_MC2 | (1, 0) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| FUSED_MC2 | (1, 1) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| FUSED_MC2 | (1, 0) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| FUSED_MC2 | (0, 0) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| FUSED_MC2 | (1, 1) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| FUSED_MC2 | (0, 1) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| FUSED_MC2 | (0, 0) | 1 | 1025 | [1025, 1025] | [[0, 1], [1025, 0]] | 48 |
| FUSED_MC2 | (1, 0) | 1025 | 1025 | [1025, 1025] | [[0, 1025], [1025, 1024]] | 48 |
| FUSED_MC2 | (0, 1) | 1 | 1025 | [1025, 1025] | [[0, 1], [1025, 0]] | 48 |
| FUSED_MC2 | (1, 1) | 1025 | 1025 | [1025, 1025] | [[0, 1025], [1025, 1024]] | 48 |
| FUSED_MC2 | (1, 0) | 194 | 194 | [194, 194] | [[0, 194], [194, 194]] | 48 |
| FUSED_MC2 | (0, 0) | 68 | 194 | [194, 194] | [[0, 68], [194, 68]] | 48 |
| FUSED_MC2 | (1, 1) | 194 | 194 | [194, 194] | [[0, 194], [194, 194]] | 48 |
| FUSED_MC2 | (0, 1) | 68 | 194 | [194, 194] | [[0, 68], [194, 68]] | 48 |
| FUSED_MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| FUSED_MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| FUSED_MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| FUSED_MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
