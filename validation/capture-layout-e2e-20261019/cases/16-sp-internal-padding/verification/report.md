# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 20928, 'ALLTOALL': 576}
Matched layer calls: 21504

- boundary-15: PASS, shape=[22, 48, 8], seconds=2.075
- boundary-16: PASS, shape=[23, 48, 8], seconds=2.076
- boundary-17: PASS, shape=[24, 48, 8], seconds=2.076
- concurrent-129: PASS, shape=[136, 48, 8], seconds=2.15
- concurrent-3: PASS, shape=[10, 48, 8], seconds=2.152
- concurrent-385: PASS, shape=[392, 48, 8], seconds=2.15
- concurrent-7: PASS, shape=[14, 48, 8], seconds=2.151
- long: PASS, shape=[2056, 48, 8], seconds=2.143
- short-1: PASS, shape=[8, 48, 8], seconds=1.9
- short-5: PASS, shape=[12, 48, 8], seconds=2.079
- short-7: PASS, shape=[14, 48, 8], seconds=2.065
- small-dp0-round0: PASS, shape=[12, 48, 8], seconds=2.317
- small-dp0-round1: PASS, shape=[12, 48, 8], seconds=2.257
- small-dp0-round2: PASS, shape=[12, 48, 8], seconds=2.247
- small-dp1-round0: PASS, shape=[20, 48, 8], seconds=2.317
- small-dp1-round1: PASS, shape=[20, 48, 8], seconds=2.257
- small-dp1-round2: PASS, shape=[20, 48, 8], seconds=2.247

Strict selection events: 448; layout events: 21504

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 1) | 1 | MC2 | MC2 | 95 |
| (0, 0) | 1 | MC2 | MC2 | 95 |
| (1, 0) | 1 | MC2 | MC2 | 95 |
| (1, 1) | 1 | MC2 | MC2 | 95 |
| (1, 0) | 5 | MC2 | MC2 | 1 |
| (1, 1) | 5 | MC2 | MC2 | 1 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 5 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (0, 1) | 7 | MC2 | MC2 | 1 |
| (1, 0) | 7 | MC2 | MC2 | 1 |
| (1, 1) | 7 | MC2 | MC2 | 1 |
| (1, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 15 | MC2 | MC2 | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (1, 1) | 15 | MC2 | MC2 | 1 |
| (1, 0) | 15 | MC2 | MC2 | 1 |
| (1, 0) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (1, 1) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 2 | MC2 | MC2 | 7 |
| (0, 1) | 2 | MC2 | MC2 | 7 |
| (1, 0) | 2 | MC2 | MC2 | 7 |
| (0, 0) | 2 | MC2 | MC2 | 7 |
| (0, 0) | 13 | MC2 | MC2 | 3 |
| (1, 0) | 13 | MC2 | MC2 | 3 |
| (0, 1) | 13 | MC2 | MC2 | 3 |
| (1, 1) | 13 | MC2 | MC2 | 3 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 4560 |
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 4560 |
| MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 4560 |
| MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 4560 |
| MC2 | (1, 0) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| MC2 | (1, 1) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| MC2 | (0, 0) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| MC2 | (0, 1) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| MC2 | (0, 0) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| MC2 | (0, 1) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| MC2 | (1, 0) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| MC2 | (1, 1) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| ALLTOALL | (1, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 1) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 0) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| MC2 | (0, 1) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (0, 0) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (1, 1) | 8 | 8 | [8, 8] | [[0, 8], [8, 7]] | 48 |
| MC2 | (1, 0) | 8 | 8 | [8, 8] | [[0, 8], [8, 7]] | 48 |
| MC2 | (1, 0) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (0, 0) | 8 | 8 | [8, 8] | [[0, 8], [8, 8]] | 48 |
| MC2 | (1, 1) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (0, 1) | 8 | 8 | [8, 8] | [[0, 8], [8, 8]] | 48 |
| ALLTOALL | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 1) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (1, 0) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (1, 0) | 257 | 257 | [257, 257] | [[0, 514]] | 48 |
| ALLTOALL | (1, 1) | 257 | 257 | [257, 257] | [[0, 514]] | 48 |
| ALLTOALL | (0, 1) | 5 | 5 | [5, 5] | [[0, 10]] | 48 |
| ALLTOALL | (0, 0) | 5 | 5 | [5, 5] | [[0, 10]] | 48 |
| MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (0, 0) | 3 | 7 | [7, 7] | [[0, 3], [7, 2]] | 144 |
| MC2 | (1, 0) | 7 | 7 | [7, 7] | [[0, 7], [7, 6]] | 144 |
| MC2 | (0, 1) | 3 | 7 | [7, 7] | [[0, 3], [7, 2]] | 144 |
| MC2 | (1, 1) | 7 | 7 | [7, 7] | [[0, 7], [7, 6]] | 144 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
