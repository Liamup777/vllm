# Capture verification: INCONCLUSIVE

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'FUSED_MC2': 384}
Matched layer calls: 384

- concurrent-129: PASS, shape=[136, 48, 8], seconds=0.579
- concurrent-3: PASS, shape=[10, 48, 8], seconds=0.541
- concurrent-385: PASS, shape=[392, 48, 8], seconds=0.581
- concurrent-7: PASS, shape=[14, 48, 8], seconds=0.541
- long: PASS, shape=[2056, 48, 8], seconds=0.577
- short-1: PASS, shape=[8, 48, 8], seconds=0.466
- short-5: PASS, shape=[12, 48, 8], seconds=0.422
- short-7: PASS, shape=[14, 48, 8], seconds=0.39

Strict selection events: 24; layout events: 384

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 2 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 2 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 2 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 2 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 8 | FUSED_MC2 | FUSED_MC2 | 3 |
| (1, 0) | 8 | FUSED_MC2 | FUSED_MC2 | 3 |
| (0, 0) | 8 | FUSED_MC2 | FUSED_MC2 | 3 |
| (0, 1) | 8 | FUSED_MC2 | FUSED_MC2 | 3 |
| (0, 1) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 386 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 0) | 386 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 386 | FUSED_MC2 | FUSED_MC2 | 1 |
| (1, 1) | 386 | FUSED_MC2 | FUSED_MC2 | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| FUSED_MC2 | (1, 1) | 1025 | 1025 | [1025, 1025] | [[0, 1025], [1025, 1024]] | 48 |
| FUSED_MC2 | (1, 0) | 1025 | 1025 | [1025, 1025] | [[0, 1025], [1025, 1024]] | 48 |
| FUSED_MC2 | (0, 1) | 1 | 1025 | [1025, 1025] | [[0, 1], [1025, 0]] | 48 |
| FUSED_MC2 | (0, 0) | 1 | 1025 | [1025, 1025] | [[0, 1], [1025, 0]] | 48 |
| FUSED_MC2 | (0, 0) | 65 | 193 | [193, 193] | [[0, 65], [193, 65]] | 48 |
| FUSED_MC2 | (1, 0) | 193 | 193 | [193, 193] | [[0, 193], [193, 193]] | 48 |
| FUSED_MC2 | (1, 1) | 193 | 193 | [193, 193] | [[0, 193], [193, 193]] | 48 |
| FUSED_MC2 | (0, 1) | 65 | 193 | [193, 193] | [[0, 65], [193, 65]] | 48 |

Failures:

Coverage missing:
- Incomplete forward rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(1, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(1, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]

分支、布局与代表性日志：见 branch-walkthrough.md
