# Same-run capture: PASS

Worker comparisons: 148; elements: 2082048
API comparisons: 11; elements: 1041024

| Request | Shape | Elements compared | Result |
|---|---|---:|---|
| boundary-15 | [22, 48, 8] | 8448 | PASS |
| boundary-16 | [23, 48, 8] | 8832 | PASS |
| boundary-17 | [24, 48, 8] | 9216 | PASS |
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

Uneven TP shards observed: False
Internal padding observed: False

Failures:
