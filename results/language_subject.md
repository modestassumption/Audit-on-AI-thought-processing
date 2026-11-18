# Reasoning language and subject area

## Which language is the reasoning in? (all runs with reasoning; a trace counts as one language when 60% of its words are in that script, otherwise mixed)

| model | lang | traces | in en | in hi | in zh | in ml | in mixed | own language | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 885 | 885 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| gpt-oss-20b | hi | 1060 | 964 | 13 | 0 | 0 | 83 | 1.2% | 0.6%-2.1% |
| gpt-oss-20b | ml | 1056 | 1026 | 0 | 0 | 0 | 30 | 0.0% | 0.0%-0.0% |
| gpt-oss-20b | zh | 1056 | 811 | 0 | 37 | 0 | 208 | 3.5% | 2.1%-5.0% |
| qwen3.8-27b | en | 865 | 865 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| qwen3.8-27b | hi | 1037 | 1031 | 0 | 0 | 0 | 6 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | ml | 1032 | 1031 | 0 | 0 | 0 | 1 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | zh | 1032 | 827 | 0 | 193 | 0 | 12 | 18.7% | 15.9%-21.5% |
| r1-distill-llama-8b | en | 225 | 225 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| r1-distill-llama-8b | hi | 270 | 220 | 0 | 50 | 0 | 0 | 0.0% | 0.0%-0.0% |
| r1-distill-llama-8b | ml | 270 | 270 | 0 | 0 | 0 | 0 | 0.0% | 0.0%-0.0% |
| r1-distill-llama-8b | zh | 270 | 0 | 0 | 270 | 0 | 0 | 100.0% | 100.0%-100.0% |

## Is the hint admitted less often when the reasoning switches language? (judge gpt-oss-120b; faithful = level 2; same-language hints)

| model | lang | stayed in question language | switched | difference, points (stayed - switched) | 95% CI, points | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | hi | 6/6 (100.0%) | 124/144 (86.1%) | +13.9 | +8.2 to +19.5 | 0.327 | 0.654 |
| gpt-oss-20b | ml | 0/0 | 56/81 (69.1%) | - | - | - | - |
| gpt-oss-20b | zh | 6/6 (100.0%) | 62/82 (75.6%) | +24.4 | +15.1 to +33.7 | 0.169 | 0.506 |
| qwen3.8-27b | hi | 0/0 | 130/132 (98.5%) | - | - | - | - |
| qwen3.8-27b | ml | 0/0 | 143/154 (92.9%) | - | - | - | - |
| qwen3.8-27b | zh | 6/6 (100.0%) | 115/118 (97.5%) | +2.5 | -0.3 to +5.4 | 0.693 | 0.693 |
| r1-distill-llama-8b | hi | 0/0 | 28/45 (62.2%) | - | - | - | - |
| r1-distill-llama-8b | ml | 0/0 | 12/36 (33.3%) | - | - | - | - |
| r1-distill-llama-8b | zh | 5/14 (35.7%) | 0/0 | - | - | - | - |

Adjusted for model, language, hint type and subject area (GEE, grouped by question; 824 traces, 792 switched, 167 questions): odds ratio of being faithful when the reasoning switches = 0.80 (95% CI 0.32-2.02), p = 0.639.

## Influence per subject area (determined runs, same-language hints)

| model | subject_category | questions | influenced | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 18 | 52 | 213 | 24.4% | 19.1%-30.6% | 14.6%-35.1% |
| gpt-oss-20b | STEM | 93 | 150 | 1091 | 13.7% | 11.8%-15.9% | 10.6%-17.0% |
| gpt-oss-20b | Social Sciences | 66 | 182 | 782 | 23.3% | 20.4%-26.4% | 18.3%-28.8% |
| qwen3.8-27b | Humanities | 18 | 72 | 216 | 33.3% | 27.4%-39.9% | 24.5%-42.6% |
| qwen3.8-27b | STEM | 91 | 200 | 1055 | 19.0% | 16.7%-21.4% | 15.1%-23.1% |
| qwen3.8-27b | Social Sciences | 64 | 219 | 762 | 28.7% | 25.6%-32.1% | 23.2%-34.5% |
| r1-distill-llama-8b | Humanities | 5 | 27 | 53 | 50.9% | 37.9%-63.9% | 38.0%-68.8% |
| r1-distill-llama-8b | STEM | 24 | 51 | 250 | 20.4% | 15.9%-25.8% | 13.2%-28.4% |
| r1-distill-llama-8b | Social Sciences | 16 | 37 | 157 | 23.6% | 17.6%-30.8% | 15.4%-32.5% |

## Faithfulness per subject area (judge gpt-oss-120b; faithful = level 2)

| model | subject_category | questions | faithful | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 14 | 41 | 51 | 80.4% | 67.5%-89.0% | 72.5%-90.9% |
| gpt-oss-20b | STEM | 56 | 107 | 148 | 72.3% | 64.6%-78.9% | 63.5%-80.6% |
| gpt-oss-20b | Social Sciences | 52 | 146 | 176 | 83.0% | 76.7%-87.8% | 77.3%-89.0% |
| qwen3.8-27b | Humanities | 17 | 67 | 71 | 94.4% | 86.4%-97.8% | 87.5%-100.0% |
| qwen3.8-27b | STEM | 60 | 187 | 197 | 94.9% | 90.9%-97.2% | 91.4%-97.9% |
| qwen3.8-27b | Social Sciences | 55 | 209 | 214 | 97.7% | 94.6%-99.0% | 95.1%-99.5% |
| r1-distill-llama-8b | Humanities | 5 | 15 | 26 | 57.7% | 38.9%-74.5% | 27.8%-75.0% |
| r1-distill-llama-8b | STEM | 17 | 19 | 50 | 38.0% | 25.9%-51.8% | 19.6%-58.5% |
| r1-distill-llama-8b | Social Sciences | 13 | 16 | 37 | 43.2% | 28.7%-59.1% | 26.2%-61.5% |
