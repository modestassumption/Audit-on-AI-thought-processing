# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 1500 | 300 | 100% | 100% | 0% | 89% | 94% | 4% |
| gpt-oss-20b | hi | 1800 | 300 | 100% | 99% | 0% | 83% | 90% | 7% |
| gpt-oss-20b | ml | 1800 | 300 | 100% | 100% | 0% | 78% | 85% | 8% |
| gpt-oss-20b | zh | 1800 | 300 | 100% | 100% | 0% | 84% | 92% | 5% |
| qwen3.8-27b | en | 1465 | 294 | 100% | 100% | 0% | 91% | 97% | 3% |
| qwen3.8-27b | hi | 1763 | 295 | 100% | 99% | 1% | 87% | 96% | 4% |
| qwen3.8-27b | ml | 1762 | 294 | 100% | 99% | 1% | 83% | 90% | 6% |
| qwen3.8-27b | zh | 1765 | 295 | 100% | 99% | 1% | 89% | 97% | 3% |
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
| qwen3.8-27b | en | expert | 293 | 289 | 5% | 9 | 3% | 2%-6% | 9 |
| qwen3.8-27b | en | leaked | 293 | 289 | 11% | 21 | 7% | 5%-11% | 22 |
| qwen3.8-27b | en | metadata | 294 | 287 | 39% | 103 | 36% | 31%-42% | 105 |
| qwen3.8-27b | hi | expert | 294 | 289 | 10% | 19 | 7% | 4%-10% | 22 |
| qwen3.8-27b | hi | expert(en) | 293 | 288 | 10% | 18 | 6% | 4%-10% | 22 |
| qwen3.8-27b | hi | leaked | 294 | 290 | 21% | 48 | 17% | 13%-21% | 52 |
| qwen3.8-27b | hi | metadata | 294 | 288 | 61% | 166 | 58% | 52%-63% | 170 |
| qwen3.8-27b | ml | expert | 294 | 288 | 13% | 22 | 8% | 5%-11% | 24 |
| qwen3.8-27b | ml | expert(en) | 293 | 290 | 12% | 17 | 6% | 4%-9% | 21 |
| qwen3.8-27b | ml | leaked | 293 | 289 | 27% | 60 | 21% | 16%-26% | 62 |
| qwen3.8-27b | ml | metadata | 294 | 290 | 72% | 185 | 64% | 58%-69% | 192 |
| qwen3.8-27b | zh | expert | 294 | 290 | 8% | 14 | 5% | 3%-8% | 15 |
| qwen3.8-27b | zh | expert(en) | 293 | 288 | 7% | 11 | 4% | 2%-7% | 13 |
| qwen3.8-27b | zh | leaked | 295 | 290 | 28% | 70 | 24% | 20%-29% | 73 |
| qwen3.8-27b | zh | metadata | 295 | 289 | 50% | 134 | 46% | 41%-52% | 137 |
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
| qwen3.8-27b | en | expert | 293 | 4 | 3 | 9 |
| qwen3.8-27b | en | leaked | 293 | 4 | 3 | 21 |
| qwen3.8-27b | en | metadata | 294 | 7 | 5 | 103 |
| qwen3.8-27b | hi | expert | 294 | 5 | 4 | 19 |
| qwen3.8-27b | hi | expert(en) | 293 | 5 | 5 | 18 |
| qwen3.8-27b | hi | leaked | 294 | 4 | 6 | 48 |
| qwen3.8-27b | hi | metadata | 294 | 6 | 7 | 166 |
| qwen3.8-27b | ml | expert | 294 | 6 | 8 | 22 |
| qwen3.8-27b | ml | expert(en) | 293 | 3 | 8 | 17 |
| qwen3.8-27b | ml | leaked | 293 | 4 | 8 | 60 |
| qwen3.8-27b | ml | metadata | 294 | 4 | 15 | 185 |
| qwen3.8-27b | zh | expert | 294 | 4 | 1 | 14 |
| qwen3.8-27b | zh | expert(en) | 293 | 5 | 1 | 11 |
| qwen3.8-27b | zh | leaked | 295 | 5 | 2 | 70 |
| qwen3.8-27b | zh | metadata | 295 | 6 | 2 | 134 |
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
| qwen3.8-27b | en | 280 | 1 | 0% |
| qwen3.8-27b | hi | 280 | 4 | 1% |
| qwen3.8-27b | ml | 274 | 7 | 3% |
| qwen3.8-27b | zh | 282 | 2 | 1% |
| r1-distill-llama-8b | en | 236 | 8 | 3% |
| r1-distill-llama-8b | hi | 220 | 22 | 10% |
| r1-distill-llama-8b | ml | 225 | 31 | 14% |
| r1-distill-llama-8b | zh | 203 | 17 | 8% |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 6900 | 446 | 1226 | 669 | 4.6M | - | - |
| qwen3.8-27b | 6755 | 997 | 2139 | 1215 | 8.4M | - | - |
| r1-distill-llama-8b | 6900 | 1552 | 4608 | 1902 | 13.1M | - | - |
