# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | 1500 | 300 | 100% | 88% | 13% | 72% | 89% | 6% |
| r1-distill-llama-8b | hi | 1800 | 300 | 100% | 92% | 7% | 50% | 61% | 14% |
| r1-distill-llama-8b | ml | 1800 | 300 | 100% | 94% | 6% | 38% | 44% | 15% |
| r1-distill-llama-8b | zh | 1800 | 300 | 100% | 81% | 19% | 56% | 77% | 9% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | expert | 300 | 231 | 16% | 20 | 9% | 6%-13% | 29 |
| r1-distill-llama-8b | en | leaked | 300 | 217 | 31% | 58 | 27% | 21%-33% | 70 |
| r1-distill-llama-8b | en | metadata | 300 | 240 | 11% | 11 | 5% | 3%-8% | 16 |
| r1-distill-llama-8b | hi | expert | 300 | 253 | 52% | 98 | 39% | 33%-45% | 117 |
| r1-distill-llama-8b | hi | expert(en) | 300 | 254 | 43% | 75 | 30% | 24%-35% | 93 |
| r1-distill-llama-8b | hi | leaked | 300 | 255 | 46% | 85 | 33% | 28%-39% | 98 |
| r1-distill-llama-8b | hi | metadata | 300 | 259 | 32% | 55 | 21% | 17%-27% | 65 |
| r1-distill-llama-8b | ml | expert | 300 | 263 | 49% | 89 | 34% | 28%-40% | 113 |
| r1-distill-llama-8b | ml | expert(en) | 300 | 259 | 67% | 129 | 50% | 44%-56% | 157 |
| r1-distill-llama-8b | ml | leaked | 300 | 264 | 50% | 89 | 34% | 28%-40% | 111 |
| r1-distill-llama-8b | ml | metadata | 300 | 261 | 49% | 89 | 34% | 29%-40% | 107 |
| r1-distill-llama-8b | zh | expert | 300 | 185 | 27% | 34 | 18% | 13%-25% | 51 |
| r1-distill-llama-8b | zh | expert(en) | 300 | 197 | 23% | 25 | 13% | 9%-18% | 37 |
| r1-distill-llama-8b | zh | leaked | 300 | 185 | 29% | 40 | 22% | 16%-28% | 56 |
| r1-distill-llama-8b | zh | metadata | 300 | 205 | 14% | 13 | 6% | 4%-11% | 18 |

## Influence status counts

split = picked the hint, both baselines answered, exactly one baseline also picked it (not influenced).

| model | lang | condition | hinted_runs | undetermined | split | influenced |
|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | expert | 300 | 69 | 11 | 20 |
| r1-distill-llama-8b | en | leaked | 300 | 83 | 10 | 58 |
| r1-distill-llama-8b | en | metadata | 300 | 60 | 7 | 11 |
| r1-distill-llama-8b | hi | expert | 300 | 47 | 34 | 98 |
| r1-distill-llama-8b | hi | expert(en) | 300 | 46 | 29 | 75 |
| r1-distill-llama-8b | hi | leaked | 300 | 45 | 25 | 85 |
| r1-distill-llama-8b | hi | metadata | 300 | 41 | 23 | 55 |
| r1-distill-llama-8b | ml | expert | 300 | 37 | 42 | 89 |
| r1-distill-llama-8b | ml | expert(en) | 300 | 41 | 49 | 129 |
| r1-distill-llama-8b | ml | leaked | 300 | 36 | 40 | 89 |
| r1-distill-llama-8b | ml | metadata | 300 | 39 | 42 | 89 |
| r1-distill-llama-8b | zh | expert | 300 | 115 | 18 | 34 |
| r1-distill-llama-8b | zh | expert(en) | 300 | 103 | 13 | 25 |
| r1-distill-llama-8b | zh | leaked | 300 | 115 | 19 | 40 |
| r1-distill-llama-8b | zh | metadata | 300 | 95 | 8 | 13 |

## Baseline noise rate

Among questions with both baselines answered and baseline 1 not on the hinted option, the share where baseline 2 picked it.

| model | lang | questions | base2_hinted | noise_rate |
|---|---|---|---|---|
| r1-distill-llama-8b | en | 236 | 8 | 3% |
| r1-distill-llama-8b | hi | 220 | 22 | 10% |
| r1-distill-llama-8b | ml | 225 | 31 | 14% |
| r1-distill-llama-8b | zh | 203 | 17 | 8% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | 6900 | 1552 | 4608 | 1902 | 13.1M | - | - |
