# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'MC2': 7392, 'ALLTOALL': 288}
Matched layer calls: 7680

- boundary-15: PASS, shape=[22, 48, 8], seconds=1.756
- boundary-16: PASS, shape=[23, 48, 8], seconds=1.757
- boundary-17: PASS, shape=[24, 48, 8], seconds=1.801
- concurrent-129: PASS, shape=[136, 48, 8], seconds=1.872
- concurrent-3: PASS, shape=[10, 48, 8], seconds=1.87
- concurrent-385: PASS, shape=[392, 48, 8], seconds=1.872
- concurrent-7: PASS, shape=[14, 48, 8], seconds=1.869
- long: PASS, shape=[2056, 48, 8], seconds=1.874
- short-1: PASS, shape=[8, 48, 8], seconds=1.63
- short-5: PASS, shape=[12, 48, 8], seconds=1.76
- short-7: PASS, shape=[14, 48, 8], seconds=1.702

Strict selection events: 160; layout events: 7680

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (1, 0) | 1 | MC2 | MC2 | 66 |
| (0, 0) | 1 | MC2 | MC2 | 66 |
| (0, 0) | 5 | MC2 | MC2 | 1 |
| (1, 0) | 5 | MC2 | MC2 | 1 |
| (1, 0) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 7 | MC2 | MC2 | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 15 | MC2 | MC2 | 1 |
| (1, 0) | 15 | MC2 | MC2 | 1 |
| (1, 0) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 16 | MC2 | MC2 | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 514 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2 | MC2 | MC2 | 7 |
| (1, 0) | 2 | MC2 | MC2 | 7 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| MC2 | (1, 0) | 1 | 1 | [] | [[0, 1]] | 3168 |
| MC2 | (0, 0) | 1 | 1 | [] | [[0, 1]] | 3168 |
| MC2 | (0, 0) | 1 | 5 | [] | [[0, 1]] | 48 |
| MC2 | (1, 0) | 5 | 5 | [] | [[0, 5]] | 48 |
| MC2 | (0, 0) | 7 | 7 | [] | [[0, 7]] | 48 |
| MC2 | (1, 0) | 1 | 7 | [] | [[0, 1]] | 48 |
| ALLTOALL | (0, 0) | 1 | 1 | [] | [[0, 1]] | 96 |
| ALLTOALL | (1, 0) | 2049 | 2049 | [] | [[0, 2049]] | 48 |
| MC2 | (0, 0) | 1 | 15 | [] | [[0, 1]] | 48 |
| MC2 | (1, 0) | 15 | 15 | [] | [[0, 15]] | 48 |
| MC2 | (1, 0) | 1 | 16 | [] | [[0, 1]] | 48 |
| MC2 | (0, 0) | 16 | 16 | [] | [[0, 16]] | 48 |
| ALLTOALL | (1, 0) | 17 | 17 | [] | [[0, 17]] | 48 |
| ALLTOALL | (1, 0) | 514 | 514 | [] | [[0, 514]] | 48 |
| ALLTOALL | (0, 0) | 10 | 10 | [] | [[0, 10]] | 48 |
| MC2 | (0, 0) | 2 | 2 | [] | [[0, 2]] | 336 |
| MC2 | (1, 0) | 2 | 2 | [] | [[0, 2]] | 336 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
