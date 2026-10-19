# Same-run capture: PASS

Worker comparisons: 96; elements: 2029056
API comparisons: 8; elements: 1014528

| Request | Shape | Elements compared | Result |
|---|---|---:|---|
| concurrent-129 | [136, 48, 8] | 52224 | PASS |
| concurrent-3 | [10, 48, 8] | 3840 | PASS |
| concurrent-385 | [392, 48, 8] | 150528 | PASS |
| concurrent-7 | [14, 48, 8] | 5376 | PASS |
| long | [2056, 48, 8] | 789504 | PASS |
| short-1 | [8, 48, 8] | 3072 | PASS |
| short-5 | [12, 48, 8] | 4608 | PASS |
| short-7 | [14, 48, 8] | 5376 | PASS |

Example from the fully compared arrays:

```json
{
  "case": "short-5",
  "samples": [
    {
      "token_position": 0,
      "layer": 0,
      "router": [
        53,
        5,
        85,
        110,
        55,
        59,
        9,
        89
      ],
      "returned": [
        53,
        5,
        85,
        110,
        55,
        59,
        9,
        89
      ]
    },
    {
      "token_position": 11,
      "layer": 47,
      "router": [
        112,
        12,
        30,
        10,
        105,
        60,
        115,
        19
      ],
      "returned": [
        112,
        12,
        30,
        10,
        105,
        60,
        115,
        19
      ]
    }
  ]
}
```

Uneven TP shards observed: False
Internal padding observed: False

Failures:
