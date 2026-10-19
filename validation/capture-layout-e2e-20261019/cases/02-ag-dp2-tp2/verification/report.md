# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'ALLGATHER': 9216}
Matched layer calls: 9216

- concurrent-129: PASS, shape=[136, 48, 8], seconds=1.672
- concurrent-3: PASS, shape=[10, 48, 8], seconds=1.674
- concurrent-385: PASS, shape=[392, 48, 8], seconds=1.673
- concurrent-7: PASS, shape=[14, 48, 8], seconds=1.67
- long: PASS, shape=[2056, 48, 8], seconds=1.77
- short-1: PASS, shape=[8, 48, 8], seconds=1.518
- short-5: PASS, shape=[12, 48, 8], seconds=1.563
- short-7: PASS, shape=[14, 48, 8], seconds=1.621

Strict selection events: 192; layout events: 9216

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 0) | 1 | ALLGATHER | ALLGATHER | 37 |
| (0, 1) | 1 | ALLGATHER | ALLGATHER | 37 |
| (1, 0) | 1 | ALLGATHER | ALLGATHER | 37 |
| (1, 1) | 1 | ALLGATHER | ALLGATHER | 37 |
| (1, 0) | 5 | ALLGATHER | ALLGATHER | 1 |
| (1, 1) | 5 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 5 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 5 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 7 | ALLGATHER | ALLGATHER | 1 |
| (1, 0) | 7 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 7 | ALLGATHER | ALLGATHER | 1 |
| (1, 1) | 7 | ALLGATHER | ALLGATHER | 1 |
| (1, 0) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (1, 1) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (1, 0) | 388 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 388 | ALLGATHER | ALLGATHER | 1 |
| (1, 1) | 388 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 388 | ALLGATHER | ALLGATHER | 1 |
| (1, 1) | 2 | ALLGATHER | ALLGATHER | 7 |
| (0, 1) | 2 | ALLGATHER | ALLGATHER | 7 |
| (1, 0) | 2 | ALLGATHER | ALLGATHER | 7 |
| (0, 0) | 2 | ALLGATHER | ALLGATHER | 7 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| ALLGATHER | (0, 0) | 1 | 2 | [] | [[0, 1]] | 1776 |
| ALLGATHER | (0, 1) | 1 | 2 | [] | [[0, 1]] | 1776 |
| ALLGATHER | (1, 0) | 1 | 2 | [] | [[1, 1]] | 1776 |
| ALLGATHER | (1, 1) | 1 | 2 | [] | [[1, 1]] | 1776 |
| ALLGATHER | (1, 0) | 1 | 10 | [] | [[5, 1]] | 48 |
| ALLGATHER | (1, 1) | 1 | 10 | [] | [[5, 1]] | 48 |
| ALLGATHER | (0, 0) | 5 | 10 | [] | [[0, 5]] | 48 |
| ALLGATHER | (0, 1) | 5 | 10 | [] | [[0, 5]] | 48 |
| ALLGATHER | (1, 0) | 7 | 14 | [] | [[7, 7]] | 48 |
| ALLGATHER | (0, 0) | 1 | 14 | [] | [[0, 1]] | 48 |
| ALLGATHER | (1, 1) | 7 | 14 | [] | [[7, 7]] | 48 |
| ALLGATHER | (0, 1) | 1 | 14 | [] | [[0, 1]] | 48 |
| ALLGATHER | (1, 0) | 1 | 4098 | [] | [[2049, 1]] | 48 |
| ALLGATHER | (0, 0) | 2049 | 4098 | [] | [[0, 2049]] | 48 |
| ALLGATHER | (1, 1) | 1 | 4098 | [] | [[2049, 1]] | 48 |
| ALLGATHER | (0, 1) | 2049 | 4098 | [] | [[0, 2049]] | 48 |
| ALLGATHER | (0, 0) | 388 | 776 | [] | [[0, 388]] | 48 |
| ALLGATHER | (1, 0) | 136 | 776 | [] | [[388, 136]] | 48 |
| ALLGATHER | (0, 1) | 388 | 776 | [] | [[0, 388]] | 48 |
| ALLGATHER | (1, 1) | 136 | 776 | [] | [[388, 136]] | 48 |
| ALLGATHER | (1, 1) | 2 | 4 | [] | [[2, 2]] | 336 |
| ALLGATHER | (0, 1) | 2 | 4 | [] | [[0, 2]] | 336 |
| ALLGATHER | (1, 0) | 2 | 4 | [] | [[2, 2]] | 336 |
| ALLGATHER | (0, 0) | 2 | 4 | [] | [[0, 2]] | 336 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
