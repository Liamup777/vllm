# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 14784, 'ALLTOALL': 576}
Matched layer calls: 15360

- boundary-15: PASS, shape=[22, 48, 8], seconds=2.111
- boundary-16: PASS, shape=[23, 48, 8], seconds=2.133
- boundary-17: PASS, shape=[24, 48, 8], seconds=2.144
- concurrent-129: PASS, shape=[136, 48, 8], seconds=2.193
- concurrent-3: PASS, shape=[10, 48, 8], seconds=2.194
- concurrent-385: PASS, shape=[392, 48, 8], seconds=2.195
- concurrent-7: PASS, shape=[14, 48, 8], seconds=2.196
- long: PASS, shape=[2056, 48, 8], seconds=2.135
- short-1: PASS, shape=[8, 48, 8], seconds=1.921
- short-5: PASS, shape=[12, 48, 8], seconds=2.001
- short-7: PASS, shape=[14, 48, 8], seconds=2.015

Strict selection events: 320; layout events: 15360

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 1 | MC2 | MC2 | 66 |
| (0, 1) | 1 | MC2 | MC2 | 66 |
| (1, 1) | 1 | MC2 | MC2 | 66 |
| (1, 0) | 1 | MC2 | MC2 | 66 |
| (1, 1) | 5 | MC2 | MC2 | 1 |
| (1, 0) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 5 | MC2 | MC2 | 1 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (1, 1) | 7 | MC2 | MC2 | 1 |
| (1, 0) | 7 | MC2 | MC2 | 1 |
| (1, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (1, 0) | 15 | MC2 | MC2 | 1 |
| (0, 1) | 15 | MC2 | MC2 | 1 |
| (1, 1) | 15 | MC2 | MC2 | 1 |
| (1, 1) | 16 | MC2 | MC2 | 1 |
| (1, 0) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 2 | MC2 | MC2 | 7 |
| (1, 1) | 2 | MC2 | MC2 | 7 |
| (0, 0) | 2 | MC2 | MC2 | 7 |
| (1, 0) | 2 | MC2 | MC2 | 7 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 3168 |
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 3168 |
| MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 3168 |
| MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 0]] | 3168 |
| MC2 | (1, 1) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| MC2 | (1, 0) | 1 | 3 | [3, 3] | [[0, 1], [3, 0]] | 48 |
| MC2 | (0, 1) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| MC2 | (0, 0) | 3 | 3 | [3, 3] | [[0, 3], [3, 2]] | 48 |
| MC2 | (0, 1) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| MC2 | (0, 0) | 1 | 4 | [4, 4] | [[0, 1], [4, 0]] | 48 |
| MC2 | (1, 1) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| MC2 | (1, 0) | 4 | 4 | [4, 4] | [[0, 4], [4, 3]] | 48 |
| ALLTOALL | (1, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 1) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 0) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| MC2 | (0, 0) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (1, 0) | 8 | 8 | [8, 8] | [[0, 8], [8, 7]] | 48 |
| MC2 | (0, 1) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (1, 1) | 8 | 8 | [8, 8] | [[0, 8], [8, 7]] | 48 |
| MC2 | (1, 1) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (1, 0) | 1 | 8 | [8, 8] | [[0, 1], [8, 0]] | 48 |
| MC2 | (0, 0) | 8 | 8 | [8, 8] | [[0, 8], [8, 8]] | 48 |
| MC2 | (0, 1) | 8 | 8 | [8, 8] | [[0, 8], [8, 8]] | 48 |
| ALLTOALL | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 0) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (1, 1) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (0, 0) | 5 | 5 | [5, 5] | [[0, 10]] | 48 |
| ALLTOALL | (1, 1) | 257 | 257 | [257, 257] | [[0, 514]] | 48 |
| ALLTOALL | (0, 1) | 5 | 5 | [5, 5] | [[0, 10]] | 48 |
| ALLTOALL | (1, 0) | 257 | 257 | [257, 257] | [[0, 514]] | 48 |
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |
| MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1], [1, 1]] | 336 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
