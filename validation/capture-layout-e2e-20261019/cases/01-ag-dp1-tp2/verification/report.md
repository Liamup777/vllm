# Capture verification: PASS

Scenario-based communication selection and layout assertions, response invariants; token ownership equivalence needs a reference run

Observed methods: {'ALLGATHER': 3072}
Matched layer calls: 3072

- long: PASS, shape=[2056, 48, 8], seconds=1.335
- short-1: PASS, shape=[8, 48, 8], seconds=1.609
- short-5: PASS, shape=[12, 48, 8], seconds=1.181
- short-7: PASS, shape=[14, 48, 8], seconds=1.192

Strict selection events: 64; layout events: 3072

| DP/TP | Selector input tokens | Expected method | Actual method | Checked selections |
|---|---:|---|---|---:|
| (0, 1) | 1 | ALLGATHER | ALLGATHER | 29 |
| (0, 0) | 1 | ALLGATHER | ALLGATHER | 29 |
| (0, 1) | 5 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 5 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 7 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 7 | ALLGATHER | ALLGATHER | 1 |
| (0, 0) | 2049 | ALLGATHER | ALLGATHER | 1 |
| (0, 1) | 2049 | ALLGATHER | ALLGATHER | 1 |

Expected layouts calculated from scenario and input sizes:

| Method | DP/TP | Before rows | Expected router rows | Expected shards | Expected ranges | Checked calls |
|---|---|---:|---:|---|---|---:|
| ALLGATHER | (0, 1) | 1 | 1 | [] | [[0, 1]] | 1392 |
| ALLGATHER | (0, 0) | 1 | 1 | [] | [[0, 1]] | 1392 |
| ALLGATHER | (0, 1) | 5 | 5 | [] | [[0, 5]] | 48 |
| ALLGATHER | (0, 0) | 5 | 5 | [] | [[0, 5]] | 48 |
| ALLGATHER | (0, 1) | 7 | 7 | [] | [[0, 7]] | 48 |
| ALLGATHER | (0, 0) | 7 | 7 | [] | [[0, 7]] | 48 |
| ALLGATHER | (0, 0) | 2049 | 2049 | [] | [[0, 2049]] | 48 |
| ALLGATHER | (0, 1) | 2049 | 2049 | [] | [[0, 2049]] | 48 |

Failures:

Coverage missing:

分支、布局与代表性日志：见 branch-walkthrough.md
