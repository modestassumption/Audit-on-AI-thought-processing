# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 885 | 177 | 100% | 100% | 0% | 87% | 93% | 4% |
| gpt-oss-20b | hi | 1060 | 177 | 100% | 99% | 0% | 84% | 90% | 5% |
| gpt-oss-20b | ml | 1056 | 176 | 100% | 100% | 0% | 80% | 84% | 7% |
| gpt-oss-20b | zh | 1056 | 176 | 100% | 99% | 0% | 82% | 92% | 5% |
| qwen3.8-27b | en | 865 | 173 | 100% | 99% | 1% | 90% | 98% | 2% |
| qwen3.8-27b | hi | 1037 | 173 | 100% | 99% | 1% | 89% | 94% | 2% |
| qwen3.8-27b | ml | 1032 | 172 | 100% | 99% | 1% | 86% | 91% | 5% |
| qwen3.8-27b | zh | 1032 | 172 | 100% | 99% | 1% | 89% | 97% | 2% |
| r1-distill-llama-8b | en | 225 | 45 | 100% | 96% | 5% | 86% | 95% | 2% |
| r1-distill-llama-8b | hi | 270 | 45 | 100% | 98% | 2% | 53% | 66% | 17% |
| r1-distill-llama-8b | ml | 270 | 45 | 100% | 98% | 2% | 44% | 51% | 13% |
| r1-distill-llama-8b | zh | 270 | 45 | 100% | 85% | 15% | 67% | 86% | 2% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 177 | 176 | 10% | 10 | 6% | 3%-10% | 12 |
| gpt-oss-20b | en | leaked | 177 | 176 | 22% | 29 | 16% | 12%-23% | 32 |
| gpt-oss-20b | en | metadata | 177 | 176 | 15% | 18 | 10% | 7%-16% | 20 |
| gpt-oss-20b | hi | expert | 177 | 175 | 19% | 22 | 13% | 8%-18% | 23 |
| gpt-oss-20b | hi | expert(en) | 176 | 173 | 16% | 17 | 10% | 6%-15% | 19 |
| gpt-oss-20b | hi | leaked | 176 | 169 | 52% | 81 | 48% | 41%-55% | 83 |
| gpt-oss-20b | hi | metadata | 177 | 174 | 36% | 51 | 29% | 23%-36% | 52 |
| gpt-oss-20b | ml | expert | 176 | 176 | 15% | 12 | 7% | 4%-12% | 17 |
| gpt-oss-20b | ml | expert(en) | 176 | 176 | 16% | 14 | 8% | 5%-13% | 18 |
| gpt-oss-20b | ml | leaked | 176 | 174 | 19% | 18 | 10% | 7%-16% | 24 |
| gpt-oss-20b | ml | metadata | 176 | 176 | 40% | 54 | 31% | 24%-38% | 60 |
| gpt-oss-20b | zh | expert | 176 | 173 | 16% | 17 | 10% | 6%-15% | 20 |
| gpt-oss-20b | zh | expert(en) | 176 | 173 | 15% | 16 | 9% | 6%-14% | 18 |
| gpt-oss-20b | zh | leaked | 176 | 168 | 27% | 36 | 21% | 16%-28% | 39 |
| gpt-oss-20b | zh | metadata | 176 | 173 | 26% | 36 | 21% | 15%-27% | 39 |
| qwen3.8-27b | en | expert | 173 | 170 | 5% | 4 | 2% | 1%-6% | 4 |
| qwen3.8-27b | en | leaked | 173 | 170 | 10% | 11 | 6% | 4%-11% | 12 |
| qwen3.8-27b | en | metadata | 173 | 168 | 38% | 59 | 35% | 28%-43% | 60 |
| qwen3.8-27b | hi | expert | 173 | 170 | 8% | 10 | 6% | 3%-10% | 12 |
| qwen3.8-27b | hi | expert(en) | 172 | 169 | 8% | 8 | 5% | 2%-9% | 11 |
| qwen3.8-27b | hi | leaked | 173 | 170 | 18% | 25 | 15% | 10%-21% | 28 |
| qwen3.8-27b | hi | metadata | 173 | 169 | 60% | 97 | 57% | 50%-65% | 100 |
| qwen3.8-27b | ml | expert | 172 | 170 | 13% | 13 | 8% | 5%-13% | 14 |
| qwen3.8-27b | ml | expert(en) | 172 | 171 | 10% | 10 | 6% | 3%-10% | 12 |
| qwen3.8-27b | ml | leaked | 172 | 171 | 26% | 35 | 20% | 15%-27% | 36 |
| qwen3.8-27b | ml | metadata | 172 | 169 | 70% | 108 | 64% | 56%-71% | 111 |
| qwen3.8-27b | zh | expert | 172 | 169 | 7% | 9 | 5% | 3%-10% | 9 |
| qwen3.8-27b | zh | expert(en) | 172 | 170 | 8% | 10 | 6% | 3%-10% | 11 |
| qwen3.8-27b | zh | leaked | 172 | 169 | 27% | 42 | 25% | 19%-32% | 43 |
| qwen3.8-27b | zh | metadata | 172 | 168 | 48% | 78 | 46% | 39%-54% | 79 |
| r1-distill-llama-8b | en | expert | 45 | 38 | 16% | 2 | 5% | 1%-17% | 4 |
| r1-distill-llama-8b | en | leaked | 45 | 39 | 40% | 14 | 36% | 23%-52% | 15 |
| r1-distill-llama-8b | en | metadata | 45 | 39 | 11% | 3 | 8% | 3%-20% | 3 |
| r1-distill-llama-8b | hi | expert | 45 | 43 | 62% | 19 | 44% | 30%-59% | 20 |
| r1-distill-llama-8b | hi | expert(en) | 45 | 43 | 38% | 9 | 21% | 11%-35% | 11 |
| r1-distill-llama-8b | hi | leaked | 45 | 42 | 49% | 17 | 40% | 27%-56% | 17 |
| r1-distill-llama-8b | hi | metadata | 45 | 44 | 36% | 10 | 23% | 13%-37% | 10 |
| r1-distill-llama-8b | ml | expert | 45 | 41 | 40% | 11 | 27% | 16%-42% | 14 |
| r1-distill-llama-8b | ml | expert(en) | 45 | 41 | 69% | 21 | 51% | 36%-66% | 24 |
| r1-distill-llama-8b | ml | leaked | 45 | 41 | 49% | 14 | 34% | 22%-49% | 18 |
| r1-distill-llama-8b | ml | metadata | 45 | 41 | 49% | 11 | 27% | 16%-42% | 15 |
| r1-distill-llama-8b | zh | expert | 45 | 32 | 22% | 6 | 19% | 9%-35% | 6 |
| r1-distill-llama-8b | zh | expert(en) | 45 | 33 | 18% | 6 | 18% | 9%-34% | 6 |
| r1-distill-llama-8b | zh | leaked | 45 | 28 | 24% | 6 | 21% | 10%-40% | 7 |
| r1-distill-llama-8b | zh | metadata | 45 | 32 | 16% | 2 | 6% | 2%-20% | 2 |

## Influence status counts

split = picked the hint, both baselines answered, exactly one baseline also picked it (not influenced).

| model | lang | condition | hinted_runs | undetermined | split | influenced |
|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 177 | 1 | 4 | 10 |
| gpt-oss-20b | en | leaked | 177 | 1 | 6 | 29 |
| gpt-oss-20b | en | metadata | 177 | 1 | 4 | 18 |
| gpt-oss-20b | hi | expert | 177 | 2 | 4 | 22 |
| gpt-oss-20b | hi | expert(en) | 176 | 3 | 5 | 17 |
| gpt-oss-20b | hi | leaked | 176 | 7 | 4 | 81 |
| gpt-oss-20b | hi | metadata | 177 | 3 | 5 | 51 |
| gpt-oss-20b | ml | expert | 176 | 0 | 9 | 12 |
| gpt-oss-20b | ml | expert(en) | 176 | 0 | 8 | 14 |
| gpt-oss-20b | ml | leaked | 176 | 2 | 9 | 18 |
| gpt-oss-20b | ml | metadata | 176 | 0 | 10 | 54 |
| gpt-oss-20b | zh | expert | 176 | 3 | 4 | 17 |
| gpt-oss-20b | zh | expert(en) | 176 | 3 | 3 | 16 |
| gpt-oss-20b | zh | leaked | 176 | 8 | 3 | 36 |
| gpt-oss-20b | zh | metadata | 176 | 3 | 3 | 36 |
| qwen3.8-27b | en | expert | 173 | 3 | 2 | 4 |
| qwen3.8-27b | en | leaked | 173 | 3 | 2 | 11 |
| qwen3.8-27b | en | metadata | 173 | 5 | 2 | 59 |
| qwen3.8-27b | hi | expert | 173 | 3 | 3 | 10 |
| qwen3.8-27b | hi | expert(en) | 172 | 3 | 4 | 8 |
| qwen3.8-27b | hi | leaked | 173 | 3 | 5 | 25 |
| qwen3.8-27b | hi | metadata | 173 | 4 | 6 | 97 |
| qwen3.8-27b | ml | expert | 172 | 2 | 4 | 13 |
| qwen3.8-27b | ml | expert(en) | 172 | 1 | 3 | 10 |
| qwen3.8-27b | ml | leaked | 172 | 1 | 4 | 35 |
| qwen3.8-27b | ml | metadata | 172 | 3 | 6 | 108 |
| qwen3.8-27b | zh | expert | 172 | 3 | 0 | 9 |
| qwen3.8-27b | zh | expert(en) | 172 | 2 | 0 | 10 |
| qwen3.8-27b | zh | leaked | 172 | 3 | 1 | 42 |
| qwen3.8-27b | zh | metadata | 172 | 4 | 1 | 78 |
| r1-distill-llama-8b | en | expert | 45 | 7 | 1 | 2 |
| r1-distill-llama-8b | en | leaked | 45 | 6 | 1 | 14 |
| r1-distill-llama-8b | en | metadata | 45 | 6 | 1 | 3 |
| r1-distill-llama-8b | hi | expert | 45 | 2 | 6 | 19 |
| r1-distill-llama-8b | hi | expert(en) | 45 | 2 | 4 | 9 |
| r1-distill-llama-8b | hi | leaked | 45 | 3 | 2 | 17 |
| r1-distill-llama-8b | hi | metadata | 45 | 1 | 3 | 10 |
| r1-distill-llama-8b | ml | expert | 45 | 4 | 6 | 11 |
| r1-distill-llama-8b | ml | expert(en) | 45 | 4 | 7 | 21 |
| r1-distill-llama-8b | ml | leaked | 45 | 4 | 6 | 14 |
| r1-distill-llama-8b | ml | metadata | 45 | 4 | 8 | 11 |
| r1-distill-llama-8b | zh | expert | 45 | 13 | 1 | 6 |
| r1-distill-llama-8b | zh | expert(en) | 45 | 12 | 0 | 6 |
| r1-distill-llama-8b | zh | leaked | 45 | 17 | 2 | 6 |
| r1-distill-llama-8b | zh | metadata | 45 | 13 | 0 | 2 |

## Baseline noise rate

Among questions with both baselines answered and baseline 1 not on the hinted option, the share where baseline 2 picked it.

| model | lang | questions | base2_hinted | noise_rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 169 | 3 | 2% |
| gpt-oss-20b | hi | 165 | 2 | 1% |
| gpt-oss-20b | ml | 163 | 7 | 4% |
| gpt-oss-20b | zh | 165 | 3 | 2% |
| qwen3.8-27b | en | 165 | 0 | 0% |
| qwen3.8-27b | hi | 167 | 3 | 2% |
| qwen3.8-27b | ml | 163 | 3 | 2% |
| qwen3.8-27b | zh | 167 | 1 | 1% |
| r1-distill-llama-8b | en | 38 | 0 | 0% |
| r1-distill-llama-8b | hi | 35 | 2 | 6% |
| r1-distill-llama-8b | ml | 35 | 4 | 11% |
| r1-distill-llama-8b | zh | 34 | 1 | 3% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 4057 | 457 | 1316 | 678 | 4.7M | - | - |
| qwen3.8-27b | 3966 | 998 | 2164 | 1210 | 8.4M | - | - |
| r1-distill-llama-8b | 1035 | 1281 | 4608 | 1641 | 11.3M | - | - |
