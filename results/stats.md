# Statistics report

## Do the hints change answers? (McNemar vs. no-hint run 1, Holm over all cells)

| model | lang | hint | pairs | picked with hint | picked without hint | only with hint | only without hint | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | expert | 298 | 22 | 11 | 13 | 2 | 0.007 | 0.026 |
| gpt-oss-20b | en | leaked | 299 | 61 | 11 | 51 | 1 | <0.001 | <0.001 |
| gpt-oss-20b | en | metadata | 299 | 45 | 11 | 36 | 2 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert | 298 | 50 | 22 | 32 | 4 | <0.001 | <0.001 |
| gpt-oss-20b | hi | expert(en) | 297 | 41 | 22 | 25 | 6 | <0.001 | 0.009 |
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
| qwen3.8-27b | en | expert | 256 | 15 | 9 | 8 | 2 | 0.109 | 0.219 |
| qwen3.8-27b | en | leaked | 256 | 27 | 9 | 19 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | en | metadata | 254 | 100 | 9 | 92 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | expert | 254 | 26 | 10 | 19 | 3 | <0.001 | 0.009 |
| qwen3.8-27b | hi | expert(en) | 254 | 27 | 10 | 20 | 3 | <0.001 | 0.006 |
| qwen3.8-27b | hi | leaked | 254 | 56 | 10 | 47 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | hi | metadata | 253 | 159 | 10 | 150 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | ml | expert | 254 | 35 | 18 | 21 | 4 | <0.001 | 0.009 |
| qwen3.8-27b | ml | expert(en) | 255 | 32 | 18 | 19 | 5 | 0.007 | 0.026 |
| qwen3.8-27b | ml | leaked | 255 | 72 | 18 | 56 | 2 | <0.001 | <0.001 |
| qwen3.8-27b | ml | metadata | 254 | 185 | 18 | 167 | 0 | <0.001 | <0.001 |
| qwen3.8-27b | zh | expert | 256 | 21 | 9 | 12 | 0 | <0.001 | 0.006 |
| qwen3.8-27b | zh | expert(en) | 256 | 21 | 9 | 13 | 1 | 0.002 | 0.009 |
| qwen3.8-27b | zh | leaked | 255 | 73 | 9 | 65 | 1 | <0.001 | <0.001 |
| qwen3.8-27b | zh | metadata | 254 | 130 | 9 | 121 | 0 | <0.001 | <0.001 |
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
| qwen3.8-27b | 258 | 3048 | 745 | 24.4% | 22.9%-26.0% | 21.9%-27.2% |
| r1-distill-llama-8b | 292 | 2818 | 681 | 24.2% | 22.6%-25.8% | 21.9%-26.5% |

## Influence per model and language

| model | lang | questions | determined | influenced | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 299 | 896 | 91 | 10.2% | 8.3%-12.3% | 7.8%-12.7% |
| gpt-oss-20b | hi | 297 | 882 | 240 | 27.2% | 24.4%-30.2% | 23.7%-30.8% |
| gpt-oss-20b | ml | 300 | 898 | 140 | 15.6% | 13.4%-18.1% | 12.9%-18.4% |
| gpt-oss-20b | zh | 297 | 886 | 153 | 17.3% | 14.9%-19.9% | 14.0%-20.6% |
| qwen3.8-27b | en | 255 | 763 | 116 | 15.2% | 12.8%-17.9% | 12.3%-18.1% |
| qwen3.8-27b | hi | 255 | 761 | 205 | 26.9% | 23.9%-30.2% | 23.7%-30.2% |
| qwen3.8-27b | ml | 257 | 763 | 233 | 30.5% | 27.4%-33.9% | 27.2%-34.2% |
| qwen3.8-27b | zh | 254 | 761 | 191 | 25.1% | 22.1%-28.3% | 21.5%-28.8% |
| r1-distill-llama-8b | en | 248 | 688 | 89 | 12.9% | 10.6%-15.7% | 10.4%-15.8% |
| r1-distill-llama-8b | hi | 261 | 767 | 238 | 31.0% | 27.9%-34.4% | 26.7%-35.1% |
| r1-distill-llama-8b | ml | 268 | 788 | 267 | 33.9% | 30.7%-37.3% | 29.4%-38.5% |
| r1-distill-llama-8b | zh | 219 | 575 | 87 | 15.1% | 12.4%-18.3% | 11.6%-18.8% |
