# Capture verification: INCONCLUSIVE

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'ALLGATHER': 96}
Matched layer calls: 96

- long: PASS, shape=[2056, 48, 8], seconds=0.545
- short-1: PASS, shape=[8, 48, 8], seconds=0.406
- short-5: PASS, shape=[12, 48, 8], seconds=0.335
- short-7: PASS, shape=[14, 48, 8], seconds=0.311

Strict selection events: 8; layout events: 96

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 1 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 1 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 8 | ALLGATHER | ALLGATHER | 2 |
| (0, 0) | 8 | ALLGATHER | ALLGATHER | 2 |
| (0, 1) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 2049 | ALLGATHER | ALLGATHER | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| ALLGATHER | (0, 1) | 2049 | 2049 | [] | [[0, 2049]] | 48 |
| ALLGATHER | (0, 0) | 2049 | 2049 | [] | [[0, 2049]] | 48 |

Failures:

Coverage missing:
- Incomplete forward rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- Incomplete forward rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-1: Final forward log incomplete rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-1: Final forward log incomplete rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-1: Layout ranks missing: [(0, 0), (0, 1)]
- short-5: Final forward log incomplete rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-5: Final forward log incomplete rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-5: Layout ranks missing: [(0, 0), (0, 1)]
- short-7: Final forward log incomplete rank=(0, 0): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-7: Final forward log incomplete rank=(0, 1): missing layers [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
- short-7: Layout ranks missing: [(0, 0), (0, 1)]

分支、布局与代表性日志：见 branch-walkthrough.md
