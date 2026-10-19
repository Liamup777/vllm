# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 14784, 'ALLTOALL': 576}
Matched layer calls: 15360

- boundary-15: PASS, shape=[22, 48, 8], seconds=2.039
- boundary-16: PASS, shape=[23, 48, 8], seconds=2.058
- boundary-17: PASS, shape=[24, 48, 8], seconds=2.081
- concurrent-129: PASS, shape=[136, 48, 8], seconds=2.131
- concurrent-3: PASS, shape=[10, 48, 8], seconds=2.132
- concurrent-385: PASS, shape=[392, 48, 8], seconds=2.132
- concurrent-7: PASS, shape=[14, 48, 8], seconds=2.133
- long: PASS, shape=[2056, 48, 8], seconds=2.17
- short-1: PASS, shape=[8, 48, 8], seconds=2.001
- short-5: PASS, shape=[12, 48, 8], seconds=2.087
- short-7: PASS, shape=[14, 48, 8], seconds=2.087

Strict selection events: 320; layout events: 15360

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 1 | MC2 | MC2 | 66 |
| (0, 1) | 1 | MC2 | MC2 | 66 |
| (1, 0) | 1 | MC2 | MC2 | 66 |
| (1, 1) | 1 | MC2 | MC2 | 66 |
| (1, 0) | 5 | MC2 | MC2 | 1 |
| (1, 1) | 5 | MC2 | MC2 | 1 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 5 | MC2 | MC2 | 1 |
| (1, 1) | 7 | MC2 | MC2 | 1 |
| (1, 0) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (0, 1) | 7 | MC2 | MC2 | 1 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 15 | MC2 | MC2 | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (1, 1) | 15 | MC2 | MC2 | 1 |
| (0, 1) | 15 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (1, 0) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 16 | MC2 | MC2 | 1 |
| (1, 1) | 16 | MC2 | MC2 | 1 |
| (1, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 2 | MC2 | MC2 | 7 |
| (1, 1) | 2 | MC2 | MC2 | 7 |
| (1, 0) | 2 | MC2 | MC2 | 7 |
| (0, 0) | 2 | MC2 | MC2 | 7 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 3168 |
| MC2 | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 3168 |
| MC2 | (1, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 3168 |
| MC2 | (1, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 3168 |
| MC2 | (1, 0) | 1 | 3 | [3, 3] | [[0, 1]] | 48 |
| MC2 | (1, 1) | 1 | 3 | [3, 3] | [[0, 1]] | 48 |
| MC2 | (0, 0) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| MC2 | (0, 1) | 5 | 3 | [3, 3] | [[0, 5]] | 48 |
| MC2 | (1, 0) | 1 | 4 | [4, 4] | [[0, 1]] | 48 |
| MC2 | (1, 1) | 1 | 4 | [4, 4] | [[0, 1]] | 48 |
| MC2 | (0, 0) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| MC2 | (0, 1) | 7 | 4 | [4, 4] | [[0, 7]] | 48 |
| ALLTOALL | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 1) | 2049 | 1024 | [1025, 1024] | [[0, 2049]] | 48 |
| ALLTOALL | (1, 0) | 2049 | 1025 | [1025, 1024] | [[0, 2049]] | 48 |
| MC2 | (1, 0) | 1 | 8 | [8, 8] | [[0, 1]] | 48 |
| MC2 | (0, 0) | 15 | 8 | [8, 8] | [[0, 15]] | 48 |
| MC2 | (1, 1) | 1 | 8 | [8, 8] | [[0, 1]] | 48 |
| MC2 | (0, 1) | 15 | 8 | [8, 8] | [[0, 15]] | 48 |
| MC2 | (0, 0) | 1 | 8 | [8, 8] | [[0, 1]] | 48 |
| MC2 | (1, 0) | 16 | 8 | [8, 8] | [[0, 16]] | 48 |
| MC2 | (0, 1) | 1 | 8 | [8, 8] | [[0, 1]] | 48 |
| MC2 | (1, 1) | 16 | 8 | [8, 8] | [[0, 16]] | 48 |
| ALLTOALL | (1, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (0, 1) | 17 | 8 | [9, 8] | [[0, 17]] | 48 |
| ALLTOALL | (0, 0) | 17 | 9 | [9, 8] | [[0, 17]] | 48 |
| ALLTOALL | (0, 0) | 514 | 257 | [257, 257] | [[0, 514]] | 48 |
| ALLTOALL | (1, 0) | 10 | 5 | [5, 5] | [[0, 10]] | 48 |
| ALLTOALL | (0, 1) | 514 | 257 | [257, 257] | [[0, 514]] | 48 |
| ALLTOALL | (1, 1) | 10 | 5 | [5, 5] | [[0, 10]] | 48 |
| MC2 | (0, 1) | 2 | 1 | [1, 1] | [[0, 2]] | 336 |
| MC2 | (1, 1) | 2 | 1 | [1, 1] | [[0, 2]] | 336 |
| MC2 | (1, 0) | 2 | 1 | [1, 1] | [[0, 2]] | 336 |
| MC2 | (0, 0) | 2 | 1 | [1, 1] | [[0, 2]] | 336 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
