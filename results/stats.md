# Statistics report

## Do the hints change answers? (McNemar vs. no-hint run 1, Holm over all cells)

| model | lang | hint | pairs | picked with hint | picked without hint | only with hint | only without hint | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 298 | 22 | 11 | 13 | 2 | 0.007 | 0.024 |
| gpt-oss-20b | en | leaked | 299 | 61 | 11 | 51 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | en | metadata | 299 | 45 | 11 | 36 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert | 298 | 50 | 22 | 32 | 4 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert(en) | 297 | 41 | 22 | 25 | 6 | <0.001 | 0.007 |
| gpt-oss-20b | hi | leaked | 290 | 154 | 22 | 134 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | hi | metadata | 297 | 102 | 22 | 82 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | ml | expert | 300 | 45 | 26 | 26 | 7 | 0.001 | 0.009 |
| gpt-oss-20b | ml | expert(en) | 300 | 53 | 26 | 32 | 5 | <0.001 | <0.001 |
| gpt-oss-20b | ml | leaked | 298 | 59 | 26 | 41 | 8 | <0.001 | <0.001 |
| gpt-oss-20b | ml | metadata | 300 | 121 | 26 | 100 | 5 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert | 297 | 50 | 13 | 37 | 0 | <0.001 | <0.001 |
| gpt-oss-20b | zh | expert(en) | 297 | 37 | 13 | 27 | 3 | <0.001 | <0.001 |
| gpt-oss-20b | zh | leaked | 292 | 75 | 13 | 64 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | zh | metadata | 297 | 73 | 13 | 62 | 2 | <0.001 | <0.001 |
| qwen3.8-27b | en | expert | 290 | 16 | 9 | 9 | 2 | 0.065 | 0.131 |
| qwen3.8-27b | en | leaked | 290 | 30 | 9 | 22 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | en | metadata | 288 | 113 | 9 | 105 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | expert | 289 | 30 | 11 | 22 | 3 | <0.001 | 0.002 |
| qwen3.8-27b | hi | expert(en) | 288 | 30 | 11 | 22 | 3 | <0.001 | 0.002 |
| qwen3.8-27b | hi | leaked | 290 | 62 | 11 | 52 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | metadata | 288 | 180 | 11 | 170 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | ml | expert | 288 | 39 | 19 | 24 | 4 | <0.001 | 0.002 |
| qwen3.8-27b | ml | expert(en) | 290 | 34 | 19 | 21 | 6 | 0.006 | 0.024 |
| qwen3.8-27b | ml | leaked | 289 | 79 | 19 | 62 | 2 | <0.001 | <0.001 |
| qwen3.8-27b | ml | metadata | 290 | 210 | 19 | 192 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | zh | expert | 292 | 24 | 9 | 15 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | zh | expert(en) | 289 | 21 | 9 | 13 | 1 | 0.002 | 0.009 |
| qwen3.8-27b | zh | leaked | 291 | 81 | 9 | 73 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | zh | metadata | 290 | 146 | 9 | 137 | 0 | <0.001 | <0.001 |
| r1-distill-llama-8b | en | expert | 245 | 43 | 16 | 29 | 2 | <0.001 | <0.001 |
| r1-distill-llama-8b | en | leaked | 232 | 84 | 16 | 70 | 2 | <0.001 | <0.001 |
| r1-distill-llama-8b | en | metadata | 255 | 28 | 14 | 16 | 2 | 0.001 | 0.009 |
| r1-distill-llama-8b | hi | expert | 262 | 149 | 41 | 117 | 9 | <0.001 | <0.001 |
| r1-distill-llama-8b | hi | expert(en) | 266 | 121 | 42 | 93 | 14 | <0.001 | <0.001 |
| r1-distill-llama-8b | hi | leaked | 262 | 130 | 43 | 98 | 11 | <0.001 | <0.001 |
| r1-distill-llama-8b | hi | metadata | 267 | 90 | 42 | 65 | 17 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | expert | 269 | 141 | 45 | 113 | 17 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | expert(en) | 265 | 191 | 43 | 157 | 9 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | leaked | 269 | 139 | 44 | 111 | 16 | <0.001 | <0.001 |
| r1-distill-llama-8b | ml | metadata | 267 | 141 | 45 | 107 | 11 | <0.001 | <0.001 |
| r1-distill-llama-8b | zh | expert | 199 | 66 | 20 | 51 | 5 | <0.001 | <0.001 |
| r1-distill-llama-8b | zh | expert(en) | 213 | 54 | 21 | 37 | 4 | <0.001 | <0.001 |
| r1-distill-llama-8b | zh | leaked | 197 | 72 | 20 | 56 | 4 | <0.001 | <0.001 |
| r1-distill-llama-8b | zh | metadata | 222 | 28 | 22 | 18 | 12 | 0.362 | 0.362 |

## Influence per model (same-language hints; bootstrap: 2000 resamples of questions)

| model | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 300 | 3562 | 624 | 17.5% | 16.3%-18.8% | 15.6%-19.5% |
| qwen3.8-27b | 295 | 3468 | 851 | 24.5% | 23.1%-26.0% | 22.1%-27.1% |
| r1-distill-llama-8b | 292 | 2818 | 681 | 24.2% | 22.6%-25.8% | 21.9%-26.5% |

## Influence per model and language

| model | lang | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 299 | 896 | 91 | 10.2% | 8.3%-12.3% | 7.8%-12.7% |
| gpt-oss-20b | hi | 297 | 882 | 240 | 27.2% | 24.4%-30.2% | 23.7%-30.8% |
| gpt-oss-20b | ml | 300 | 898 | 140 | 15.6% | 13.4%-18.1% | 12.9%-18.4% |
| gpt-oss-20b | zh | 297 | 886 | 153 | 17.3% | 14.9%-19.9% | 14.0%-20.6% |
| qwen3.8-27b | en | 289 | 865 | 133 | 15.4% | 13.1%-17.9% | 12.7%-18.3% |
| qwen3.8-27b | hi | 291 | 867 | 233 | 26.9% | 24.0%-29.9% | 23.6%-30.2% |
| qwen3.8-27b | ml | 293 | 867 | 267 | 30.8% | 27.8%-33.9% | 27.6%-34.3% |
| qwen3.8-27b | zh | 290 | 869 | 218 | 25.1% | 22.3%-28.1% | 21.7%-28.7% |
| r1-distill-llama-8b | en | 248 | 688 | 89 | 12.9% | 10.6%-15.7% | 10.4%-15.8% |
| r1-distill-llama-8b | hi | 261 | 767 | 238 | 31.0% | 27.9%-34.4% | 26.7%-35.1% |
| r1-distill-llama-8b | ml | 268 | 788 | 267 | 33.9% | 30.7%-37.3% | 29.4%-38.5% |
| r1-distill-llama-8b | zh | 219 | 575 | 87 | 15.1% | 12.4%-18.3% | 11.6%-18.8% |
