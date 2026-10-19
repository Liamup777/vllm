# Same-run capture: PASS

Worker comparisons: 112; elements: 1658112
API comparisons: 7; elements: 829056

| Request | Shape | Elements compared | Result |
|---|---|---:|---|
| boundary-15 | [22, 48, 8] | 8448 | PASS |
| boundary-16 | [23, 48, 8] | 8832 | PASS |
| boundary-17 | [24, 48, 8] | 9216 | PASS |
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
        48
      ],
      "returned": [
        53,
        5,
        85,
        110,
        55,
        59,
        9,
        48
      ]
    },
    {
      "token_position": 11,
      "layer": 47,
      "router": [
        70,
        40,
        56,
        75,
        81,
        51,
        29,
        13
      ],
      "returned": [
        70,
        40,
        56,
        75,
        81,
        51,
        29,
        13
      ]
    }
  ]
}
```

Uneven TP shards observed: True
Internal padding observed: False

Failures:
