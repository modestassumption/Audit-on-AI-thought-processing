# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | 1405 | 281 | 100% | 88% | 12% | 73% | 89% | 5% |
| r1-distill-llama-8b | hi | 1686 | 281 | 100% | 93% | 7% | 52% | 61% | 14% |
| r1-distill-llama-8b | ml | 1686 | 281 | 100% | 93% | 6% | 40% | 45% | 14% |
| r1-distill-llama-8b | zh | 1686 | 281 | 100% | 81% | 19% | 57% | 76% | 9% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | expert | 281 | 217 | 16% | 19 | 9% | 6%-13% | 28 |
| r1-distill-llama-8b | en | leaked | 281 | 204 | 30% | 55 | 27% | 21%-33% | 66 |
| r1-distill-llama-8b | en | metadata | 281 | 226 | 11% | 10 | 4% | 2%-8% | 15 |
| r1-distill-llama-8b | hi | expert | 281 | 238 | 52% | 92 | 39% | 33%-45% | 111 |
| r1-distill-llama-8b | hi | expert(en) | 281 | 238 | 43% | 70 | 29% | 24%-35% | 88 |
| r1-distill-llama-8b | hi | leaked | 281 | 239 | 46% | 81 | 34% | 28%-40% | 94 |
| r1-distill-llama-8b | hi | metadata | 281 | 243 | 32% | 53 | 22% | 17%-27% | 63 |
| r1-distill-llama-8b | ml | expert | 281 | 245 | 48% | 88 | 36% | 30%-42% | 108 |
| r1-distill-llama-8b | ml | expert(en) | 281 | 241 | 66% | 123 | 51% | 45%-57% | 148 |
| r1-distill-llama-8b | ml | leaked | 281 | 246 | 49% | 84 | 34% | 29%-40% | 105 |
| r1-distill-llama-8b | ml | metadata | 281 | 243 | 49% | 86 | 35% | 30%-42% | 102 |
| r1-distill-llama-8b | zh | expert | 281 | 173 | 27% | 31 | 18% | 13%-24% | 48 |
| r1-distill-llama-8b | zh | expert(en) | 281 | 186 | 22% | 23 | 12% | 8%-18% | 35 |
| r1-distill-llama-8b | zh | leaked | 281 | 173 | 28% | 36 | 21% | 15%-27% | 51 |
| r1-distill-llama-8b | zh | metadata | 281 | 193 | 13% | 11 | 6% | 3%-10% | 16 |

## Influence status counts

split = picked the hint, both baselines answered, exactly one baseline also picked it (not influenced).

| model | lang | condition | hinted_runs | undetermined | split | influenced |
|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | expert | 281 | 64 | 10 | 19 |
| r1-distill-llama-8b | en | leaked | 281 | 77 | 9 | 55 |
| r1-distill-llama-8b | en | metadata | 281 | 55 | 6 | 10 |
| r1-distill-llama-8b | hi | expert | 281 | 43 | 33 | 92 |
| r1-distill-llama-8b | hi | expert(en) | 281 | 43 | 29 | 70 |
| r1-distill-llama-8b | hi | leaked | 281 | 42 | 24 | 81 |
| r1-distill-llama-8b | hi | metadata | 281 | 38 | 22 | 53 |
| r1-distill-llama-8b | ml | expert | 281 | 36 | 34 | 88 |
| r1-distill-llama-8b | ml | expert(en) | 281 | 40 | 42 | 123 |
| r1-distill-llama-8b | ml | leaked | 281 | 35 | 36 | 84 |
| r1-distill-llama-8b | ml | metadata | 281 | 38 | 36 | 86 |
| r1-distill-llama-8b | zh | expert | 281 | 108 | 18 | 31 |
| r1-distill-llama-8b | zh | expert(en) | 281 | 95 | 13 | 23 |
| r1-distill-llama-8b | zh | leaked | 281 | 108 | 18 | 36 |
| r1-distill-llama-8b | zh | metadata | 281 | 88 | 8 | 11 |

## Baseline noise rate

Among questions with both baselines answered and baseline 1 not on the hinted option, the share where baseline 2 picked it.

| model | lang | questions | base2_hinted | noise_rate |
|---|---|---|---|---|
| r1-distill-llama-8b | en | 225 | 8 | 4% |
| r1-distill-llama-8b | hi | 208 | 22 | 11% |
| r1-distill-llama-8b | ml | 213 | 27 | 13% |
| r1-distill-llama-8b | zh | 190 | 16 | 8% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | 6463 | 1561 | 4608 | 1912 | 13.2M | - | - |
