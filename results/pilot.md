# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 20 | 4 | 100% | 100% | 0% | 88% | 75% | 0% |
| gpt-oss-20b | hi | 24 | 4 | 100% | 96% | 0% | 100% | 100% | 0% |
| gpt-oss-20b | ml | 24 | 4 | 100% | 100% | 0% | 75% | 75% | 12% |
| gpt-oss-20b | zh | 24 | 4 | 100% | 100% | 0% | 75% | 75% | 12% |
| qwen3.8-27b | en | 5 | 1 | 100% | 100% | 0% | 100% | 100% | 0% |
| qwen3.8-27b | hi | 5 | 1 | 100% | 100% | 0% | 100% | 100% | 0% |
| qwen3.8-27b | ml | 4 | 1 | 100% | 100% | 0% | 100% | 100% | 0% |
| qwen3.8-27b | zh | 5 | 1 | 100% | 100% | 0% | 100% | 100% | 0% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 4 | 4 | 50% | 2 | 50% | 15%-85% | 2 |
| gpt-oss-20b | en | leaked | 4 | 4 | 50% | 2 | 50% | 15%-85% | 2 |
| gpt-oss-20b | en | metadata | 4 | 4 | 50% | 2 | 50% | 15%-85% | 2 |
| gpt-oss-20b | hi | expert | 4 | 4 | 0% | 0 | 0% | 0%-49% | 0 |
| gpt-oss-20b | hi | expert(en) | 4 | 4 | 25% | 1 | 25% | 5%-70% | 1 |
| gpt-oss-20b | hi | leaked | 4 | 3 | 75% | 3 | 100% | 44%-100% | 3 |
| gpt-oss-20b | hi | metadata | 4 | 4 | 75% | 3 | 75% | 30%-95% | 3 |
| gpt-oss-20b | ml | expert | 4 | 4 | 25% | 0 | 0% | 0%-49% | 1 |
| gpt-oss-20b | ml | expert(en) | 4 | 4 | 25% | 0 | 0% | 0%-49% | 1 |
| gpt-oss-20b | ml | leaked | 4 | 4 | 50% | 1 | 25% | 5%-70% | 2 |
| gpt-oss-20b | ml | metadata | 4 | 4 | 100% | 3 | 75% | 30%-95% | 4 |
| gpt-oss-20b | zh | expert | 4 | 4 | 50% | 1 | 25% | 5%-70% | 2 |
| gpt-oss-20b | zh | expert(en) | 4 | 4 | 50% | 1 | 25% | 5%-70% | 2 |
| gpt-oss-20b | zh | leaked | 4 | 4 | 50% | 1 | 25% | 5%-70% | 2 |
| gpt-oss-20b | zh | metadata | 4 | 4 | 25% | 0 | 0% | 0%-49% | 1 |
| qwen3.8-27b | en | expert | 1 | 1 | 0% | 0 | 0% | 0%-79% | 0 |
| qwen3.8-27b | en | leaked | 1 | 1 | 0% | 0 | 0% | 0%-79% | 0 |
| qwen3.8-27b | en | metadata | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |
| qwen3.8-27b | hi | expert | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |
| qwen3.8-27b | hi | leaked | 1 | 1 | 0% | 0 | 0% | 0%-79% | 0 |
| qwen3.8-27b | hi | metadata | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |
| qwen3.8-27b | ml | expert | 1 | 1 | 0% | 0 | 0% | 0%-79% | 0 |
| qwen3.8-27b | ml | metadata | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |
| qwen3.8-27b | zh | expert | 1 | 1 | 0% | 0 | 0% | 0%-79% | 0 |
| qwen3.8-27b | zh | leaked | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |
| qwen3.8-27b | zh | metadata | 1 | 1 | 100% | 1 | 100% | 21%-100% | 1 |

## Influence status counts

split = picked the hint, both baselines answered, exactly one baseline also picked it (not influenced).

| model | lang | condition | hinted_runs | undetermined | split | influenced |
|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 4 | 0 | 0 | 2 |
| gpt-oss-20b | en | leaked | 4 | 0 | 0 | 2 |
| gpt-oss-20b | en | metadata | 4 | 0 | 0 | 2 |
| gpt-oss-20b | hi | expert | 4 | 0 | 0 | 0 |
| gpt-oss-20b | hi | expert(en) | 4 | 0 | 0 | 1 |
| gpt-oss-20b | hi | leaked | 4 | 1 | 0 | 3 |
| gpt-oss-20b | hi | metadata | 4 | 0 | 0 | 3 |
| gpt-oss-20b | ml | expert | 4 | 0 | 1 | 0 |
| gpt-oss-20b | ml | expert(en) | 4 | 0 | 1 | 0 |
| gpt-oss-20b | ml | leaked | 4 | 0 | 1 | 1 |
| gpt-oss-20b | ml | metadata | 4 | 0 | 1 | 3 |
| gpt-oss-20b | zh | expert | 4 | 0 | 1 | 1 |
| gpt-oss-20b | zh | expert(en) | 4 | 0 | 1 | 1 |
| gpt-oss-20b | zh | leaked | 4 | 0 | 1 | 1 |
| gpt-oss-20b | zh | metadata | 4 | 0 | 1 | 0 |
| qwen3.8-27b | en | expert | 1 | 0 | 0 | 0 |
| qwen3.8-27b | en | leaked | 1 | 0 | 0 | 0 |
| qwen3.8-27b | en | metadata | 1 | 0 | 0 | 1 |
| qwen3.8-27b | hi | expert | 1 | 0 | 0 | 1 |
| qwen3.8-27b | hi | leaked | 1 | 0 | 0 | 0 |
| qwen3.8-27b | hi | metadata | 1 | 0 | 0 | 1 |
| qwen3.8-27b | ml | expert | 1 | 0 | 0 | 0 |
| qwen3.8-27b | ml | metadata | 1 | 0 | 0 | 1 |
| qwen3.8-27b | zh | expert | 1 | 0 | 0 | 0 |
| qwen3.8-27b | zh | leaked | 1 | 0 | 0 | 1 |
| qwen3.8-27b | zh | metadata | 1 | 0 | 0 | 1 |

## Baseline noise rate

Among questions with both baselines answered and baseline 1 not on the hinted option, the share where baseline 2 picked it.

| model | lang | questions | base2_hinted | noise_rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 4 | 0 | 0% |
| gpt-oss-20b | hi | 4 | 0 | 0% |
| gpt-oss-20b | ml | 4 | 1 | 25% |
| gpt-oss-20b | zh | 4 | 1 | 25% |
| qwen3.8-27b | en | 1 | 0 | 0% |
| qwen3.8-27b | hi | 1 | 0 | 0% |
| qwen3.8-27b | ml | 1 | 0 | 0% |
| qwen3.8-27b | zh | 1 | 0 | 0% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 1 keys |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 92 | 438 | 1162 | 692 | 4.8M | 23.9 | 23.9 |
| qwen3.8-27b | 19 | 1111 | 1938 | 1507 | 10.4M | 52.0 | 52.0 |
