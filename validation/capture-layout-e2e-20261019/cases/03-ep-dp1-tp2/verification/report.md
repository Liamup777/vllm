# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 5184, 'ALLTOALL': 192}
Matched layer calls: 5376

- boundary-15: PASS, shape=[22, 48, 8], seconds=1.791
- boundary-16: PASS, shape=[23, 48, 8], seconds=1.764
- boundary-17: PASS, shape=[24, 48, 8], seconds=1.793
- long: PASS, shape=[2056, 48, 8], seconds=1.872
- short-1: PASS, shape=[8, 48, 8], seconds=1.795
- short-5: PASS, shape=[12, 48, 8], seconds=1.746
- short-7: PASS, shape=[14, 48, 8], seconds=1.752

Strict selection events: 112; layout events: 5376

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 1) | 1 | MC2 | MC2 | 50 |
| (0, 0) | 1 | MC2 | MC2 | 50 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (0, 1) | 15 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 0) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| MC2 | (0, 1) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| MC2 | (0, 1) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| MC2 | (0, 0) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| ALLTOALL | (0, 1) | 2049 | 1024 | [1025, 1024] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 0) | 2049 | 1025 | [1025, 1024] | [[0, 2049]] | 48 |
| MC2 | (0, 0) | 15 | 8 | [8, 8] | [[0, 15]] | 48 |
| MC2 | (0, 1) | 15 | 8 | [8, 8] | [[0, 15]] | 48 |
| MC2 | (0, 0) | 16 | 8 | [8, 8] | [[0, 16]] | 48 |
| MC2 | (0, 1) | 16 | 8 | [8, 8] | [[0, 16]] | 48 |
| ALLTOALL | (0, 0) | 17 | 9 | [9, 8] | [[0, 17]] | 48 |
| ALLTOALL | (0, 1) | 17 | 8 | [9, 8] | [[0, 17]] | 48 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
