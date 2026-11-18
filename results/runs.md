# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 1500 | 300 | 100% | 100% | 0% | 89% | 94% | 4% |
| gpt-oss-20b | hi | 1800 | 300 | 100% | 99% | 0% | 83% | 90% | 7% |
| gpt-oss-20b | ml | 1800 | 300 | 100% | 100% | 0% | 78% | 85% | 8% |
| gpt-oss-20b | zh | 1800 | 300 | 100% | 100% | 0% | 84% | 92% | 5% |
| qwen3.8-27b | en | 1292 | 259 | 100% | 99% | 0% | 91% | 96% | 3% |
| qwen3.8-27b | hi | 1548 | 258 | 100% | 99% | 1% | 88% | 96% | 4% |
| qwen3.8-27b | ml | 1548 | 258 | 100% | 99% | 1% | 84% | 90% | 7% |
| qwen3.8-27b | zh | 1548 | 258 | 100% | 99% | 1% | 89% | 98% | 4% |
| r1-distill-llama-8b | en | 1500 | 300 | 100% | 88% | 13% | 72% | 89% | 6% |
| r1-distill-llama-8b | hi | 1800 | 300 | 100% | 92% | 7% | 50% | 61% | 14% |
| r1-distill-llama-8b | ml | 1800 | 300 | 100% | 94% | 6% | 38% | 44% | 15% |
| r1-distill-llama-8b | zh | 1800 | 300 | 100% | 81% | 19% | 56% | 77% | 9% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 300 | 298 | 7% | 11 | 4% | 2%-6% | 13 |
| gpt-oss-20b | en | leaked | 300 | 299 | 21% | 47 | 16% | 12%-20% | 51 |
| gpt-oss-20b | en | metadata | 300 | 299 | 15% | 33 | 11% | 8%-15% | 36 |
| gpt-oss-20b | hi | expert | 300 | 297 | 17% | 30 | 10% | 7%-14% | 32 |
| gpt-oss-20b | hi | expert(en) | 300 | 296 | 14% | 22 | 7% | 5%-11% | 25 |
| gpt-oss-20b | hi | leaked | 300 | 289 | 52% | 130 | 45% | 39%-51% | 134 |
| gpt-oss-20b | hi | metadata | 300 | 296 | 34% | 80 | 27% | 22%-32% | 82 |
| gpt-oss-20b | ml | expert | 300 | 300 | 15% | 19 | 6% | 4%-10% | 26 |
| gpt-oss-20b | ml | expert(en) | 300 | 300 | 18% | 26 | 9% | 6%-12% | 32 |
| gpt-oss-20b | ml | leaked | 300 | 298 | 20% | 32 | 11% | 8%-15% | 41 |
| gpt-oss-20b | ml | metadata | 300 | 300 | 40% | 89 | 30% | 25%-35% | 100 |
| gpt-oss-20b | zh | expert | 300 | 297 | 17% | 34 | 11% | 8%-16% | 37 |
| gpt-oss-20b | zh | expert(en) | 300 | 297 | 12% | 24 | 8% | 5%-12% | 27 |
| gpt-oss-20b | zh | leaked | 300 | 292 | 25% | 60 | 21% | 16%-26% | 64 |
| gpt-oss-20b | zh | metadata | 300 | 297 | 25% | 59 | 20% | 16%-25% | 62 |
| qwen3.8-27b | en | expert | 258 | 255 | 6% | 8 | 3% | 2%-6% | 8 |
| qwen3.8-27b | en | leaked | 258 | 255 | 11% | 18 | 7% | 5%-11% | 19 |
| qwen3.8-27b | en | metadata | 258 | 253 | 39% | 90 | 36% | 30%-42% | 92 |
| qwen3.8-27b | hi | expert | 258 | 254 | 10% | 16 | 6% | 4%-10% | 19 |
| qwen3.8-27b | hi | expert(en) | 258 | 254 | 10% | 16 | 6% | 4%-10% | 20 |
| qwen3.8-27b | hi | leaked | 258 | 254 | 22% | 43 | 17% | 13%-22% | 47 |
| qwen3.8-27b | hi | metadata | 258 | 253 | 62% | 146 | 58% | 52%-64% | 150 |
| qwen3.8-27b | ml | expert | 258 | 254 | 14% | 19 | 7% | 5%-11% | 21 |
| qwen3.8-27b | ml | expert(en) | 258 | 255 | 12% | 15 | 6% | 4%-9% | 19 |
| qwen3.8-27b | ml | leaked | 258 | 255 | 28% | 54 | 21% | 17%-27% | 56 |
| qwen3.8-27b | ml | metadata | 258 | 254 | 72% | 160 | 63% | 57%-69% | 167 |
| qwen3.8-27b | zh | expert | 258 | 254 | 8% | 11 | 4% | 2%-8% | 12 |
| qwen3.8-27b | zh | expert(en) | 258 | 255 | 8% | 11 | 4% | 2%-8% | 13 |
| qwen3.8-27b | zh | leaked | 258 | 254 | 29% | 62 | 24% | 20%-30% | 65 |
| qwen3.8-27b | zh | metadata | 258 | 253 | 51% | 118 | 47% | 41%-53% | 121 |
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
| gpt-oss-20b | en | expert | 300 | 2 | 5 | 11 |
| gpt-oss-20b | en | leaked | 300 | 1 | 8 | 47 |
| gpt-oss-20b | en | metadata | 300 | 1 | 6 | 33 |
| gpt-oss-20b | hi | expert | 300 | 3 | 8 | 30 |
| gpt-oss-20b | hi | expert(en) | 300 | 4 | 9 | 22 |
| gpt-oss-20b | hi | leaked | 300 | 11 | 11 | 130 |
| gpt-oss-20b | hi | metadata | 300 | 4 | 10 | 80 |
| gpt-oss-20b | ml | expert | 300 | 0 | 14 | 19 |
| gpt-oss-20b | ml | expert(en) | 300 | 0 | 15 | 26 |
| gpt-oss-20b | ml | leaked | 300 | 2 | 15 | 32 |
| gpt-oss-20b | ml | metadata | 300 | 0 | 20 | 89 |
| gpt-oss-20b | zh | expert | 300 | 3 | 5 | 34 |
| gpt-oss-20b | zh | expert(en) | 300 | 3 | 4 | 24 |
| gpt-oss-20b | zh | leaked | 300 | 8 | 5 | 60 |
| gpt-oss-20b | zh | metadata | 300 | 3 | 4 | 59 |
| qwen3.8-27b | en | expert | 258 | 3 | 3 | 8 |
| qwen3.8-27b | en | leaked | 258 | 3 | 3 | 18 |
| qwen3.8-27b | en | metadata | 258 | 5 | 5 | 90 |
| qwen3.8-27b | hi | expert | 258 | 4 | 4 | 16 |
| qwen3.8-27b | hi | expert(en) | 258 | 4 | 5 | 16 |
| qwen3.8-27b | hi | leaked | 258 | 4 | 6 | 43 |
| qwen3.8-27b | hi | metadata | 258 | 5 | 7 | 146 |
| qwen3.8-27b | ml | expert | 258 | 4 | 8 | 19 |
| qwen3.8-27b | ml | expert(en) | 258 | 3 | 8 | 15 |
| qwen3.8-27b | ml | leaked | 258 | 3 | 8 | 54 |
| qwen3.8-27b | ml | metadata | 258 | 4 | 15 | 160 |
| qwen3.8-27b | zh | expert | 258 | 4 | 1 | 11 |
| qwen3.8-27b | zh | expert(en) | 258 | 3 | 1 | 11 |
| qwen3.8-27b | zh | leaked | 258 | 4 | 2 | 62 |
| qwen3.8-27b | zh | metadata | 258 | 5 | 2 | 118 |
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
| gpt-oss-20b | en | 288 | 4 | 1% |
| gpt-oss-20b | hi | 275 | 5 | 2% |
| gpt-oss-20b | ml | 274 | 12 | 4% |
| gpt-oss-20b | zh | 284 | 6 | 2% |
| qwen3.8-27b | en | 247 | 1 | 0% |
| qwen3.8-27b | hi | 245 | 4 | 2% |
| qwen3.8-27b | ml | 239 | 7 | 3% |
| qwen3.8-27b | zh | 246 | 2 | 1% |
| r1-distill-llama-8b | en | 236 | 8 | 3% |
| r1-distill-llama-8b | hi | 220 | 22 | 10% |
| r1-distill-llama-8b | ml | 225 | 31 | 14% |
| r1-distill-llama-8b | zh | 203 | 17 | 8% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 6900 | 446 | 1226 | 669 | 4.6M | - | - |
| qwen3.8-27b | 5936 | 982 | 2071 | 1203 | 8.3M | - | - |
| r1-distill-llama-8b | 6900 | 1552 | 4608 | 1902 | 13.1M | - | - |
