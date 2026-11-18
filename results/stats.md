# Statistics report

## Do the hints change answers? (McNemar vs. no-hint run 1, Holm over all cells)

| model | lang | hint | pairs | picked with hint | picked without hint | only with hint | only without hint | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 140 | 14 | 6 | 10 | 2 | 0.039 | 0.386 |
| gpt-oss-20b | en | leaked | 140 | 31 | 6 | 26 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | en | metadata | 140 | 20 | 6 | 16 | 2 | 0.001 | 0.029 |
| gpt-oss-20b | hi | expert | 140 | 27 | 7 | 21 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert(en) | 138 | 18 | 7 | 12 | 1 | 0.003 | 0.065 |
| gpt-oss-20b | hi | leaked | 135 | 74 | 7 | 68 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | hi | metadata | 139 | 51 | 7 | 44 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | ml | expert | 140 | 22 | 8 | 15 | 1 | <0.001 | 0.012 |
| gpt-oss-20b | ml | expert(en) | 140 | 24 | 8 | 17 | 1 | <0.001 | 0.004 |
| gpt-oss-20b | ml | leaked | 138 | 27 | 8 | 20 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | ml | metadata | 140 | 55 | 8 | 49 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert | 137 | 22 | 6 | 16 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert(en) | 137 | 19 | 6 | 13 | 0 | <0.001 | 0.006 |
| gpt-oss-20b | zh | leaked | 133 | 37 | 6 | 32 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | zh | metadata | 137 | 31 | 6 | 27 | 2 | <0.001 | <0.001 |
| qwen3.8-27b | en | expert | 137 | 6 | 4 | 2 | 0 | 0.500 | 1.000 |
| qwen3.8-27b | en | leaked | 137 | 14 | 4 | 10 | 0 | 0.002 | 0.041 |
| qwen3.8-27b | en | metadata | 135 | 53 | 4 | 49 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | hi | expert | 136 | 12 | 3 | 11 | 2 | 0.022 | 0.314 |
| qwen3.8-27b | hi | expert(en) | 135 | 11 | 3 | 10 | 2 | 0.039 | 0.386 |
| qwen3.8-27b | hi | leaked | 136 | 24 | 3 | 22 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | metadata | 135 | 84 | 3 | 81 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | ml | expert | 135 | 18 | 7 | 11 | 0 | <0.001 | 0.022 |
| qwen3.8-27b | ml | expert(en) | 136 | 16 | 7 | 11 | 2 | 0.022 | 0.314 |
| qwen3.8-27b | ml | leaked | 136 | 37 | 7 | 30 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | ml | metadata | 133 | 98 | 7 | 91 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | zh | expert | 135 | 9 | 2 | 7 | 0 | 0.016 | 0.250 |
| qwen3.8-27b | zh | expert(en) | 136 | 9 | 2 | 8 | 1 | 0.039 | 0.386 |
| qwen3.8-27b | zh | leaked | 134 | 36 | 2 | 35 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | zh | metadata | 134 | 65 | 2 | 63 | 0 | <0.001 | <0.001 |
| r1-distill-llama-8b | en | expert | 41 | 6 | 2 | 4 | 0 | 0.125 | 0.625 |
| r1-distill-llama-8b | en | leaked | 42 | 17 | 2 | 15 | 0 | <0.001 | 0.002 |
| r1-distill-llama-8b | en | metadata | 42 | 5 | 2 | 3 | 0 | 0.250 | 0.750 |
| r1-distill-llama-8b | hi | expert | 43 | 28 | 9 | 20 | 1 | <0.001 | <0.001 |
| r1-distill-llama-8b | hi | expert(en) | 43 | 16 | 8 | 11 | 3 | 0.057 | 0.402 |
| r1-distill-llama-8b | hi | leaked | 42 | 22 | 9 | 17 | 4 | 0.007 | 0.122 |
| r1-distill-llama-8b | hi | metadata | 44 | 16 | 9 | 10 | 3 | 0.092 | 0.554 |
| r1-distill-llama-8b | ml | expert | 43 | 17 | 7 | 14 | 4 | 0.031 | 0.371 |
| r1-distill-llama-8b | ml | expert(en) | 43 | 29 | 7 | 24 | 2 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | leaked | 43 | 21 | 7 | 18 | 4 | 0.004 | 0.078 |
| r1-distill-llama-8b | ml | metadata | 43 | 20 | 7 | 15 | 2 | 0.002 | 0.047 |
| r1-distill-llama-8b | zh | expert | 33 | 7 | 1 | 6 | 0 | 0.031 | 0.371 |
| r1-distill-llama-8b | zh | expert(en) | 34 | 6 | 1 | 6 | 1 | 0.125 | 0.625 |
| r1-distill-llama-8b | zh | leaked | 28 | 8 | 1 | 7 | 0 | 0.016 | 0.250 |
| r1-distill-llama-8b | zh | metadata | 33 | 2 | 1 | 2 | 1 | 1.000 | 1.000 |

## Influence per model (same-language hints; bootstrap: 2000 resamples of questions)

| model | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 141 | 1659 | 315 | 19.0% | 17.2%-20.9% | 15.8%-22.6% |
| qwen3.8-27b | 137 | 1619 | 396 | 24.5% | 22.4%-26.6% | 20.9%-28.1% |
| r1-distill-llama-8b | 45 | 460 | 115 | 25.0% | 21.3%-29.2% | 19.4%-31.3% |

## Influence per model and language

| model | lang | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 140 | 420 | 48 | 11.4% | 8.7%-14.8% | 8.1%-15.5% |
| gpt-oss-20b | hi | 140 | 414 | 130 | 31.4% | 27.1%-36.0% | 26.1%-36.7% |
| gpt-oss-20b | ml | 140 | 418 | 71 | 17.0% | 13.7%-20.9% | 12.9%-21.7% |
| gpt-oss-20b | zh | 137 | 407 | 66 | 16.2% | 13.0%-20.1% | 12.0%-20.8% |
| qwen3.8-27b | en | 136 | 406 | 59 | 14.5% | 11.4%-18.3% | 11.0%-18.2% |
| qwen3.8-27b | hi | 136 | 407 | 106 | 26.0% | 22.0%-30.5% | 21.4%-30.6% |
| qwen3.8-27b | ml | 136 | 404 | 128 | 31.7% | 27.3%-36.4% | 27.0%-36.5% |
| qwen3.8-27b | zh | 134 | 402 | 103 | 25.6% | 21.6%-30.1% | 20.4%-30.8% |
| r1-distill-llama-8b | en | 39 | 116 | 19 | 16.4% | 10.7%-24.2% | 9.4%-23.9% |
| r1-distill-llama-8b | hi | 44 | 129 | 46 | 35.7% | 27.9%-44.2% | 25.0%-46.9% |
| r1-distill-llama-8b | ml | 41 | 123 | 36 | 29.3% | 22.0%-37.8% | 19.5%-39.8% |
| r1-distill-llama-8b | zh | 34 | 92 | 14 | 15.2% | 9.3%-23.9% | 5.6%-25.8% |
