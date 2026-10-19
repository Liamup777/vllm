# Capture verification: INCONCLUSIVE

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'ALLTOALL': 768}
Matched layer calls: 768

- boundary-15: PASS, shape=[22, 48, 8], seconds=0.383
- boundary-16: PASS, shape=[23, 48, 8], seconds=0.366
- boundary-17: PASS, shape=[24, 48, 8], seconds=0.555
- concurrent-129: PASS, shape=[136, 48, 8], seconds=0.887
- concurrent-3: PASS, shape=[10, 48, 8], seconds=0.847
- concurrent-385: PASS, shape=[392, 48, 8], seconds=0.845
- concurrent-7: PASS, shape=[14, 48, 8], seconds=0.928
- long: PASS, shape=[2056, 48, 8], seconds=0.621
- short-1: PASS, shape=[8, 48, 8], seconds=0.481
- short-5: PASS, shape=[12, 48, 8], seconds=0.411
- short-7: PASS, shape=[14, 48, 8], seconds=0.361
- small-dp0-round0: PASS, shape=[12, 48, 8], seconds=0.352
- small-dp0-round1: PASS, shape=[12, 48, 8], seconds=0.362
- small-dp0-round2: PASS, shape=[12, 48, 8], seconds=0.352
- small-dp1-round0: PASS, shape=[20, 48, 8], seconds=0.351
- small-dp1-round1: PASS, shape=[20, 48, 8], seconds=0.403
- small-dp1-round2: PASS, shape=[20, 48, 8], seconds=0.353

Strict selection events: 56; layout events: 768

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (1, 0) | 2 | MC2 | MC2 | 1 |
| (1, 1) | 2 | MC2 | MC2 | 1 |
| (0, 0) | 2 | MC2 | MC2 | 1 |
| (0, 1) | 2 | MC2 | MC2 | 1 |
| (0, 0) | 8 | MC2 | MC2 | 4 |
| (0, 1) | 8 | MC2 | MC2 | 4 |
| (1, 0) | 8 | MC2 | MC2 | 4 |
| (1, 1) | 8 | MC2 | MC2 | 4 |
| (0, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 2049 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 16 | MC2 | MC2 | 5 |
| (1, 0) | 16 | MC2 | MC2 | 5 |
| (0, 1) | 16 | MC2 | MC2 | 5 |
| (0, 0) | 16 | MC2 | MC2 | 5 |
| (1, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 17 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 17 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 385 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 385 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 385 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 385 | ALLTOALL | ALLTOALL | 1 |
| (0, 1) | 130 | ALLTOALL | ALLTOALL | 1 |
| (0, 0) | 130 | ALLTOALL | ALLTOALL | 1 |
| (1, 0) | 130 | ALLTOALL | ALLTOALL | 1 |
| (1, 1) | 130 | ALLTOALL | ALLTOALL | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| ALLTOALL | (1, 0) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| ALLTOALL | (1, 1) | 1025 | 1025 | [1025, 1025] | [[0, 2049]] | 48 |
| ALLTOALL | (0, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 96 |
| ALLTOALL | (0, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 96 |
| ALLTOALL | (0, 0) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (0, 1) | 9 | 9 | [9, 9] | [[0, 17]] | 48 |
| ALLTOALL | (1, 1) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 0) | 1 | 1 | [1, 1] | [[0, 1]] | 48 |
| ALLTOALL | (1, 1) | 2 | 2 | [2, 2] | [[0, 3]] | 48 |
| ALLTOALL | (0, 1) | 193 | 193 | [193, 193] | [[0, 385]] | 48 |
| ALLTOALL | (1, 0) | 2 | 2 | [2, 2] | [[0, 3]] | 48 |
| ALLTOALL | (0, 0) | 193 | 193 | [193, 193] | [[0, 385]] | 48 |
| ALLTOALL | (1, 0) | 65 | 65 | [65, 65] | [[0, 130]] | 48 |
| ALLTOALL | (1, 1) | 65 | 65 | [65, 65] | [[0, 130]] | 48 |

Failures:

Coverage missing:
- Requested communication branch not observed: MC2
- Final forward log incomplete rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Final forward log incomplete rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Final forward log incomplete rank=(1, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Final forward log incomplete rank=(1, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(1, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(1, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Selector boundary inputs not observed: [15]
- Skipping internal padding was not observed

分支、布局与代表性日志：见 branch-walkthrough.md
