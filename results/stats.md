# Statistics report

## Do the hints change answers? (McNemar vs. no-hint run 1, Holm over all cells)

| model | lang | hint | pairs | picked with hint | picked without hint | only with hint | only without hint | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 176 | 17 | 7 | 12 | 2 | 0.013 | 0.181 |
| gpt-oss-20b | en | leaked | 176 | 38 | 7 | 32 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | en | metadata | 176 | 25 | 7 | 20 | 2 | <0.001 | 0.003 |
| gpt-oss-20b | hi | expert | 176 | 32 | 10 | 23 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert(en) | 174 | 27 | 10 | 19 | 2 | <0.001 | 0.005 |
| gpt-oss-20b | hi | leaked | 170 | 91 | 10 | 83 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | hi | metadata | 175 | 62 | 10 | 52 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | ml | expert | 176 | 27 | 13 | 17 | 3 | 0.003 | 0.049 |
| gpt-oss-20b | ml | expert(en) | 176 | 28 | 13 | 18 | 3 | 0.001 | 0.031 |
| gpt-oss-20b | ml | leaked | 174 | 33 | 13 | 24 | 4 | <0.001 | 0.004 |
| gpt-oss-20b | ml | metadata | 176 | 70 | 13 | 60 | 3 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert | 173 | 28 | 8 | 20 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert(en) | 173 | 26 | 8 | 18 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | zh | leaked | 168 | 46 | 8 | 39 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | zh | metadata | 173 | 45 | 8 | 39 | 2 | <0.001 | <0.001 |
| qwen3.8-27b | en | expert | 171 | 8 | 5 | 4 | 1 | 0.375 | 0.750 |
| qwen3.8-27b | en | leaked | 171 | 17 | 5 | 12 | 0 | <0.001 | 0.011 |
| qwen3.8-27b | en | metadata | 169 | 64 | 5 | 60 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | expert | 170 | 13 | 4 | 12 | 3 | 0.035 | 0.340 |
| qwen3.8-27b | hi | expert(en) | 169 | 13 | 4 | 11 | 2 | 0.022 | 0.270 |
| qwen3.8-27b | hi | leaked | 170 | 31 | 4 | 28 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | metadata | 169 | 104 | 4 | 100 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | ml | expert | 170 | 22 | 9 | 14 | 1 | <0.001 | 0.021 |
| qwen3.8-27b | ml | expert(en) | 171 | 18 | 9 | 12 | 3 | 0.035 | 0.340 |
| qwen3.8-27b | ml | leaked | 171 | 45 | 9 | 36 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | ml | metadata | 169 | 120 | 9 | 111 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | zh | expert | 170 | 12 | 3 | 9 | 0 | 0.004 | 0.070 |
| qwen3.8-27b | zh | expert(en) | 171 | 13 | 3 | 11 | 1 | 0.006 | 0.102 |
| qwen3.8-27b | zh | leaked | 169 | 45 | 3 | 43 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | zh | metadata | 168 | 82 | 3 | 79 | 0 | <0.001 | <0.001 |
| r1-distill-llama-8b | en | expert | 41 | 6 | 2 | 4 | 0 | 0.125 | 0.625 |
| r1-distill-llama-8b | en | leaked | 42 | 17 | 2 | 15 | 0 | <0.001 | 0.002 |
| r1-distill-llama-8b | en | metadata | 42 | 5 | 2 | 3 | 0 | 0.250 | 0.750 |
| r1-distill-llama-8b | hi | expert | 43 | 28 | 9 | 20 | 1 | <0.001 | <0.001 |
| r1-distill-llama-8b | hi | expert(en) | 43 | 16 | 8 | 11 | 3 | 0.057 | 0.402 |
| r1-distill-llama-8b | hi | leaked | 42 | 22 | 9 | 17 | 4 | 0.007 | 0.108 |
| r1-distill-llama-8b | hi | metadata | 44 | 16 | 9 | 10 | 3 | 0.092 | 0.554 |
| r1-distill-llama-8b | ml | expert | 43 | 17 | 7 | 14 | 4 | 0.031 | 0.340 |
| r1-distill-llama-8b | ml | expert(en) | 43 | 29 | 7 | 24 | 2 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | leaked | 43 | 21 | 7 | 18 | 4 | 0.004 | 0.074 |
| r1-distill-llama-8b | ml | metadata | 43 | 20 | 7 | 15 | 2 | 0.002 | 0.047 |
| r1-distill-llama-8b | zh | expert | 33 | 7 | 1 | 6 | 0 | 0.031 | 0.340 |
| r1-distill-llama-8b | zh | expert(en) | 34 | 6 | 1 | 6 | 1 | 0.125 | 0.625 |
| r1-distill-llama-8b | zh | leaked | 28 | 8 | 1 | 7 | 0 | 0.016 | 0.203 |
| r1-distill-llama-8b | zh | metadata | 33 | 2 | 1 | 2 | 1 | 1.000 | 1.000 |

## Influence per model (same-language hints; bootstrap: 2000 resamples of questions)

| model | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 177 | 2086 | 384 | 18.4% | 16.8%-20.1% | 15.6%-21.4% |
| qwen3.8-27b | 173 | 2033 | 491 | 24.2% | 22.3%-26.1% | 20.8%-27.5% |
| r1-distill-llama-8b | 45 | 460 | 115 | 25.0% | 21.3%-29.2% | 19.4%-31.3% |

## Influence per model and language

| model | lang | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 176 | 528 | 57 | 10.8% | 8.4%-13.7% | 7.8%-14.2% |
| gpt-oss-20b | hi | 175 | 518 | 154 | 29.7% | 26.0%-33.8% | 24.8%-34.5% |
| gpt-oss-20b | ml | 176 | 526 | 84 | 16.0% | 13.1%-19.3% | 12.2%-20.0% |
| gpt-oss-20b | zh | 173 | 514 | 89 | 17.3% | 14.3%-20.8% | 13.3%-21.7% |
| qwen3.8-27b | en | 170 | 508 | 74 | 14.6% | 11.8%-17.9% | 11.3%-18.1% |
| qwen3.8-27b | hi | 171 | 509 | 132 | 25.9% | 22.3%-29.9% | 22.0%-30.1% |
| qwen3.8-27b | ml | 172 | 510 | 156 | 30.6% | 26.7%-34.7% | 26.4%-34.8% |
| qwen3.8-27b | zh | 169 | 506 | 129 | 25.5% | 21.9%-29.5% | 20.9%-30.2% |
| r1-distill-llama-8b | en | 39 | 116 | 19 | 16.4% | 10.7%-24.2% | 9.4%-23.9% |
| r1-distill-llama-8b | hi | 44 | 129 | 46 | 35.7% | 27.9%-44.2% | 25.0%-46.9% |
| r1-distill-llama-8b | ml | 41 | 123 | 36 | 29.3% | 22.0%-37.8% | 19.5%-39.8% |
| r1-distill-llama-8b | zh | 34 | 92 | 14 | 15.2% | 9.3%-23.9% | 5.6%-25.8% |
