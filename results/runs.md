# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 705 | 141 | 100% | 100% | 0% | 88% | 94% | 4% |
| gpt-oss-20b | hi | 844 | 141 | 100% | 99% | 0% | 85% | 89% | 5% |
| gpt-oss-20b | ml | 840 | 140 | 100% | 100% | 0% | 81% | 84% | 6% |
| gpt-oss-20b | zh | 840 | 140 | 100% | 99% | 0% | 82% | 92% | 5% |
| qwen3.8-27b | en | 685 | 137 | 100% | 100% | 0% | 93% | 97% | 2% |
| qwen3.8-27b | hi | 821 | 137 | 100% | 100% | 0% | 90% | 94% | 2% |
| qwen3.8-27b | ml | 816 | 136 | 100% | 100% | 0% | 88% | 91% | 5% |
| qwen3.8-27b | zh | 816 | 136 | 100% | 99% | 1% | 90% | 96% | 2% |
| r1-distill-llama-8b | en | 225 | 45 | 100% | 96% | 5% | 86% | 95% | 2% |
| r1-distill-llama-8b | hi | 270 | 45 | 100% | 98% | 2% | 53% | 66% | 17% |
| r1-distill-llama-8b | ml | 270 | 45 | 100% | 98% | 2% | 44% | 51% | 13% |
| r1-distill-llama-8b | zh | 270 | 45 | 100% | 85% | 15% | 67% | 86% | 2% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 141 | 140 | 10% | 9 | 6% | 3%-12% | 10 |
| gpt-oss-20b | en | leaked | 141 | 140 | 23% | 24 | 17% | 12%-24% | 26 |
| gpt-oss-20b | en | metadata | 141 | 140 | 15% | 15 | 11% | 7%-17% | 16 |
| gpt-oss-20b | hi | expert | 141 | 140 | 20% | 20 | 14% | 9%-21% | 21 |
| gpt-oss-20b | hi | expert(en) | 140 | 138 | 14% | 11 | 8% | 5%-14% | 12 |
| gpt-oss-20b | hi | leaked | 140 | 135 | 54% | 67 | 50% | 41%-58% | 68 |
| gpt-oss-20b | hi | metadata | 141 | 139 | 37% | 43 | 31% | 24%-39% | 44 |
| gpt-oss-20b | ml | expert | 140 | 140 | 16% | 11 | 8% | 4%-14% | 15 |
| gpt-oss-20b | ml | expert(en) | 140 | 140 | 17% | 13 | 9% | 6%-15% | 17 |
| gpt-oss-20b | ml | leaked | 140 | 138 | 19% | 15 | 11% | 7%-17% | 20 |
| gpt-oss-20b | ml | metadata | 140 | 140 | 39% | 45 | 32% | 25%-40% | 49 |
| gpt-oss-20b | zh | expert | 140 | 137 | 16% | 13 | 9% | 6%-16% | 16 |
| gpt-oss-20b | zh | expert(en) | 140 | 137 | 14% | 11 | 8% | 5%-14% | 13 |
| gpt-oss-20b | zh | leaked | 140 | 133 | 27% | 29 | 22% | 16%-30% | 32 |
| gpt-oss-20b | zh | metadata | 140 | 137 | 23% | 24 | 18% | 12%-25% | 27 |
| qwen3.8-27b | en | expert | 137 | 136 | 4% | 2 | 1% | 0%-5% | 2 |
| qwen3.8-27b | en | leaked | 137 | 136 | 10% | 9 | 7% | 4%-12% | 10 |
| qwen3.8-27b | en | metadata | 137 | 134 | 39% | 48 | 36% | 28%-44% | 49 |
| qwen3.8-27b | hi | expert | 137 | 136 | 9% | 9 | 7% | 4%-12% | 11 |
| qwen3.8-27b | hi | expert(en) | 136 | 135 | 8% | 7 | 5% | 3%-10% | 10 |
| qwen3.8-27b | hi | leaked | 137 | 136 | 18% | 19 | 14% | 9%-21% | 22 |
| qwen3.8-27b | hi | metadata | 137 | 135 | 61% | 78 | 58% | 49%-66% | 81 |
| qwen3.8-27b | ml | expert | 136 | 135 | 13% | 10 | 7% | 4%-13% | 11 |
| qwen3.8-27b | ml | expert(en) | 136 | 136 | 12% | 9 | 7% | 4%-12% | 11 |
| qwen3.8-27b | ml | leaked | 136 | 136 | 27% | 29 | 21% | 15%-29% | 30 |
| qwen3.8-27b | ml | metadata | 136 | 133 | 72% | 89 | 67% | 59%-74% | 91 |
| qwen3.8-27b | zh | expert | 136 | 134 | 7% | 7 | 5% | 3%-10% | 7 |
| qwen3.8-27b | zh | expert(en) | 136 | 135 | 7% | 7 | 5% | 3%-10% | 8 |
| qwen3.8-27b | zh | leaked | 136 | 134 | 26% | 34 | 25% | 19%-33% | 35 |
| qwen3.8-27b | zh | metadata | 136 | 134 | 48% | 62 | 46% | 38%-55% | 63 |
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
| gpt-oss-20b | en | expert | 141 | 1 | 3 | 9 |
| gpt-oss-20b | en | leaked | 141 | 1 | 5 | 24 |
| gpt-oss-20b | en | metadata | 141 | 1 | 3 | 15 |
| gpt-oss-20b | hi | expert | 141 | 1 | 3 | 20 |
| gpt-oss-20b | hi | expert(en) | 140 | 2 | 3 | 11 |
| gpt-oss-20b | hi | leaked | 140 | 5 | 3 | 67 |
| gpt-oss-20b | hi | metadata | 141 | 2 | 4 | 43 |
| gpt-oss-20b | ml | expert | 140 | 0 | 7 | 11 |
| gpt-oss-20b | ml | expert(en) | 140 | 0 | 7 | 13 |
| gpt-oss-20b | ml | leaked | 140 | 2 | 8 | 15 |
| gpt-oss-20b | ml | metadata | 140 | 0 | 6 | 45 |
| gpt-oss-20b | zh | expert | 140 | 3 | 4 | 13 |
| gpt-oss-20b | zh | expert(en) | 140 | 3 | 3 | 11 |
| gpt-oss-20b | zh | leaked | 140 | 7 | 3 | 29 |
| gpt-oss-20b | zh | metadata | 140 | 3 | 3 | 24 |
| qwen3.8-27b | en | expert | 137 | 1 | 2 | 2 |
| qwen3.8-27b | en | leaked | 137 | 1 | 2 | 9 |
| qwen3.8-27b | en | metadata | 137 | 3 | 2 | 48 |
| qwen3.8-27b | hi | expert | 137 | 1 | 3 | 9 |
| qwen3.8-27b | hi | expert(en) | 136 | 1 | 4 | 7 |
| qwen3.8-27b | hi | leaked | 137 | 1 | 5 | 19 |
| qwen3.8-27b | hi | metadata | 137 | 2 | 6 | 78 |
| qwen3.8-27b | ml | expert | 136 | 1 | 4 | 10 |
| qwen3.8-27b | ml | expert(en) | 136 | 0 | 3 | 9 |
| qwen3.8-27b | ml | leaked | 136 | 0 | 4 | 29 |
| qwen3.8-27b | ml | metadata | 136 | 3 | 5 | 89 |
| qwen3.8-27b | zh | expert | 136 | 2 | 0 | 7 |
| qwen3.8-27b | zh | expert(en) | 136 | 1 | 0 | 7 |
| qwen3.8-27b | zh | leaked | 136 | 2 | 1 | 34 |
| qwen3.8-27b | zh | metadata | 136 | 2 | 1 | 62 |
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
| gpt-oss-20b | en | 134 | 2 | 1% |
| gpt-oss-20b | hi | 133 | 1 | 1% |
| gpt-oss-20b | ml | 132 | 5 | 4% |
| gpt-oss-20b | zh | 131 | 3 | 2% |
| qwen3.8-27b | en | 132 | 0 | 0% |
| qwen3.8-27b | hi | 133 | 3 | 2% |
| qwen3.8-27b | ml | 129 | 2 | 2% |
| qwen3.8-27b | zh | 133 | 1 | 1% |
| r1-distill-llama-8b | en | 38 | 0 | 0% |
| r1-distill-llama-8b | hi | 35 | 2 | 6% |
| r1-distill-llama-8b | ml | 35 | 4 | 11% |
| r1-distill-llama-8b | zh | 34 | 1 | 3% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 3229 | 445 | 1237 | 666 | 4.6M | 23.0 | 3.3 |
| qwen3.8-27b | 3138 | 960 | 1989 | 1177 | 8.1M | 40.6 | 5.8 |
| r1-distill-llama-8b | 1035 | 1281 | 4608 | 1641 | 11.3M | - | - |
