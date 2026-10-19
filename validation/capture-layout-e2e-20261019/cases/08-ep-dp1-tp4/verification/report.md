# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 10368, 'ALLTOALL': 384}
Matched layer calls: 10752

- boundary-15: PASS, shape=[22, 48, 8], seconds=1.939
- boundary-16: PASS, shape=[23, 48, 8], seconds=1.975
- boundary-17: PASS, shape=[24, 48, 8], seconds=1.966
- long: PASS, shape=[2056, 48, 8], seconds=1.976
- short-1: PASS, shape=[8, 48, 8], seconds=2.055
- short-5: PASS, shape=[12, 48, 8], seconds=1.923
- short-7: PASS, shape=[14, 48, 8], seconds=1.915

Strict selection events: 224; layout events: 10752

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 3) | 1 | MC2 | MC2 | 50 |
| (0, 2) | 1 | MC2 | MC2 | 50 |
| (0, 0) | 1 | MC2 | MC2 | 50 |
| (0, 1) | 1 | MC2 | MC2 | 50 |
| (0, 3) | 5 | MC2 | MC2 | 1 |
| (0, 1) | 5 | MC2 | MC2 | 1 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (0, 2) | 5 | MC2 | MC2 | 1 |
| (0, 2) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (0, 1) | 7 | MC2 | MC2 | 1 |
| (0, 3) | 7 | MC2 | MC2 | 1 |
| (0, 3) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 2) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 3) | 15 | MC2 | MC2 | 1 |
| (0, 1) | 15 | MC2 | MC2 | 1 |
| (0, 2) | 15 | MC2 | MC2 | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (0, 2) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 16 | MC2 | MC2 | 1 |
| (0, 3) | 16 | MC2 | MC2 | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 3) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 2) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (0, 3) | 1 | 1 | [1, 1, 1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 0) | 1 | 1 | [1, 1, 1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 2) | 1 | 1 | [1, 1, 1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 1) | 1 | 1 | [1, 1, 1, 1] | [[0, 1]] | 2400 |
| MC2 | (0, 3) | 5 | 2 | [2, 2, 2, 2] | [[0, 5]] | 48 |
| MC2 | (0, 1) | 5 | 2 | [2, 2, 2, 2] | [[0, 5]] | 48 |
| MC2 | (0, 0) | 5 | 2 | [2, 2, 2, 2] | [[0, 5]] | 48 |
| MC2 | (0, 2) | 5 | 2 | [2, 2, 2, 2] | [[0, 5]] | 48 |
| MC2 | (0, 2) | 7 | 2 | [2, 2, 2, 2] | [[0, 7]] | 48 |
| MC2 | (0, 0) | 7 | 2 | [2, 2, 2, 2] | [[0, 7]] | 48 |
| MC2 | (0, 1) | 7 | 2 | [2, 2, 2, 2] | [[0, 7]] | 48 |
| MC2 | (0, 3) | 7 | 2 | [2, 2, 2, 2] | [[0, 7]] | 48 |
| ALLTOALL | (0, 3) | 2049 | 512 | [513, 512, 512, 512] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 2) | 2049 | 512 | [513, 512, 512, 512] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 1) | 2049 | 512 | [513, 512, 512, 512] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 0) | 2049 | 513 | [513, 512, 512, 512] | [[0, 2049]] | 48 |
| MC2 | (0, 3) | 15 | 4 | [4, 4, 4, 4] | [[0, 15]] | 48 |
| MC2 | (0, 1) | 15 | 4 | [4, 4, 4, 4] | [[0, 15]] | 48 |
| MC2 | (0, 2) | 15 | 4 | [4, 4, 4, 4] | [[0, 15]] | 48 |
| MC2 | (0, 0) | 15 | 4 | [4, 4, 4, 4] | [[0, 15]] | 48 |
| MC2 | (0, 2) | 16 | 4 | [4, 4, 4, 4] | [[0, 16]] | 48 |
| MC2 | (0, 0) | 16 | 4 | [4, 4, 4, 4] | [[0, 16]] | 48 |
| MC2 | (0, 1) | 16 | 4 | [4, 4, 4, 4] | [[0, 16]] | 48 |
| MC2 | (0, 3) | 16 | 4 | [4, 4, 4, 4] | [[0, 16]] | 48 |
| ALLTOALL | (0, 1) | 17 | 4 | [5, 4, 4, 4] | [[0, 17]] | 48 |
| ALLTOALL | (0, 3) | 17 | 4 | [5, 4, 4, 4] | [[0, 17]] | 48 |
| ALLTOALL | (0, 2) | 17 | 4 | [5, 4, 4, 4] | [[0, 17]] | 48 |
| ALLTOALL | (0, 0) | 17 | 5 | [5, 4, 4, 4] | [[0, 17]] | 48 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
