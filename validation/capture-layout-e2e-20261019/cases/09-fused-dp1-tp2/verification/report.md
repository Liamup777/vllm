# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'FUSED_MC2': 3072}
Matched layer calls: 3072

- long: PASS, shape=[2056, 48, 8], seconds=1.544
- short-1: PASS, shape=[8, 48, 8], seconds=1.582
- short-5: PASS, shape=[12, 48, 8], seconds=1.406
- short-7: PASS, shape=[14, 48, 8], seconds=1.411

Strict selection events: 64; layout events: 3072

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 1 | FUSED_MC2 | FUSED_MC2 | 29 |
| (0, 1) | 1 | FUSED_MC2 | FUSED_MC2 | 29 |
| (0, 0) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 5 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 7 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 1) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |
| (0, 0) | 2049 | FUSED_MC2 | FUSED_MC2 | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| FUSED_MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 1392 |
| FUSED_MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 1392 |
| FUSED_MC2 | (0, 0) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| FUSED_MC2 | (0, 1) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| FUSED_MC2 | (0, 1) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| FUSED_MC2 | (0, 0) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| FUSED_MC2 | (0, 1) | 2049 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| FUSED_MC2 | (0, 0) | 2049 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
