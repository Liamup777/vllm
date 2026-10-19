# Same-run capture: PASS

Worker comparisons: 64; elements: 1605120
API comparisons: 4; elements: 802560

| Request | Shape | Elements compared | Result |
|---|---|---:|---|
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
