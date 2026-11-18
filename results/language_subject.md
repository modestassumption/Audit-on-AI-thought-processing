# Reasoning language and subject area

## Which language is the reasoning in? (all runs with reasoning; a trace counts as one language when 60% of its words are in that script, otherwise mixed)

| model | lang | traces | in en | in hi | in zh | in ml | in mixed | own language | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 1500 | 1500 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| gpt-oss-20b | hi | 1800 | 1637 | 20 | 0 | 0 | 143 | 1.1% | 0.6%-1.7% |
| gpt-oss-20b | ml | 1800 | 1759 | 0 | 0 | 0 | 41 | 0.0% | 0.0%-0.0% |
| gpt-oss-20b | zh | 1800 | 1381 | 0 | 67 | 0 | 352 | 3.7% | 2.7%-4.8% |
| qwen3.8-27b | en | 1292 | 1292 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| qwen3.8-27b | hi | 1548 | 1538 | 0 | 0 | 0 | 10 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | ml | 1548 | 1547 | 0 | 0 | 0 | 1 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | zh | 1548 | 1251 | 0 | 279 | 0 | 18 | 18.0% | 15.8%-20.3% |
| r1-distill-llama-8b | en | 1500 | 1500 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| r1-distill-llama-8b | hi | 1800 | 1376 | 8 | 416 | 0 | 0 | 0.4% | 0.1%-1.1% |
| r1-distill-llama-8b | ml | 1800 | 1781 | 0 | 1 | 18 | 0 | 1.0% | 0.4%-1.7% |
| r1-distill-llama-8b | zh | 1800 | 0 | 0 | 1800 | 0 | 0 | 100.0% | 100.0%-100.0% |

## Is the hint admitted less often when the reasoning switches language? (judge gpt-oss-120b; faithful = level 2; same-language hints)

| model | lang | stayed in question language | switched | difference, points (stayed - switched) | 95% CI, points | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | hi | 6/6 (100.0%) | 167/200 (83.5%) | +16.5 | +11.4 to +21.6 | 0.278 | 0.833 |
| gpt-oss-20b | ml | 0/0 | 82/112 (73.2%) | - | - | - | - |
| gpt-oss-20b | zh | 10/10 (100.0%) | 93/126 (73.8%) | +26.2 | +18.5 to +33.9 | 0.063 | 0.315 |
| qwen3.8-27b | hi | 0/0 | 169/174 (97.1%) | - | - | - | - |
| qwen3.8-27b | ml | 0/0 | 183/199 (92.0%) | - | - | - | - |
| qwen3.8-27b | zh | 10/10 (100.0%) | 148/153 (96.7%) | +3.3 | +0.5 to +6.1 | 0.561 | 0.833 |
| r1-distill-llama-8b | hi | 0/1 (0.0%) | 84/159 (52.8%) | -52.8 | -60.6 to -45.1 | 0.292 | 0.833 |
| r1-distill-llama-8b | ml | 2/3 (66.7%) | 47/160 (29.4%) | +37.3 | -16.5 to +91.1 | 0.163 | 0.651 |
| r1-distill-llama-8b | zh | 19/58 (32.8%) | 0/0 | - | - | - | - |

Adjusted for model, language, hint type and subject area (GEE, grouped by question; 1371 traces, 1283 switched, 255 questions): odds ratio of being faithful when the reasoning switches = 0.84 (95% CI 0.47-1.50), p = 0.560.

## Influence per subject area (determined runs, same-language hints)

| model | subject_category | questions | influenced | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 40 | 101 | 474 | 21.3% | 17.9%-25.2% | 15.4%-27.0% |
| gpt-oss-20b | STEM | 150 | 233 | 1780 | 13.1% | 11.6%-14.7% | 10.7%-15.5% |
| gpt-oss-20b | Social Sciences | 110 | 290 | 1308 | 22.2% | 20.0%-24.5% | 18.5%-26.0% |
| qwen3.8-27b | Humanities | 37 | 144 | 441 | 32.7% | 28.4%-37.2% | 27.2%-38.3% |
| qwen3.8-27b | STEM | 126 | 260 | 1470 | 17.7% | 15.8%-19.7% | 14.4%-21.4% |
| qwen3.8-27b | Social Sciences | 95 | 341 | 1137 | 30.0% | 27.4%-32.7% | 25.8%-34.7% |
| r1-distill-llama-8b | Humanities | 40 | 125 | 427 | 29.3% | 25.2%-33.8% | 23.1%-35.5% |
| r1-distill-llama-8b | STEM | 142 | 249 | 1281 | 19.4% | 17.4%-21.7% | 16.2%-22.7% |
| r1-distill-llama-8b | Social Sciences | 110 | 307 | 1110 | 27.7% | 25.1%-30.4% | 24.5%-31.2% |

## Faithfulness per subject area (judge gpt-oss-120b; faithful = level 2)

| model | subject_category | questions | faithful | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 27 | 66 | 86 | 76.7% | 66.8%-84.4% | 68.8%-85.7% |
| gpt-oss-20b | STEM | 81 | 150 | 210 | 71.4% | 65.0%-77.1% | 64.0%-78.3% |
| gpt-oss-20b | Social Sciences | 78 | 199 | 236 | 84.3% | 79.1%-88.4% | 79.4%-89.1% |
| qwen3.8-27b | Humanities | 28 | 108 | 114 | 94.7% | 89.0%-97.6% | 90.2%-98.4% |
| qwen3.8-27b | STEM | 71 | 224 | 237 | 94.5% | 90.8%-96.8% | 91.3%-97.2% |
| qwen3.8-27b | Social Sciences | 70 | 274 | 284 | 96.5% | 93.6%-98.1% | 94.3%-98.5% |
| r1-distill-llama-8b | Humanities | 30 | 34 | 90 | 37.8% | 28.5%-48.1% | 25.0%-50.0% |
| r1-distill-llama-8b | STEM | 73 | 56 | 163 | 34.4% | 27.5%-41.9% | 26.7%-42.1% |
| r1-distill-llama-8b | Social Sciences | 84 | 87 | 189 | 46.0% | 39.1%-53.1% | 38.1%-53.5% |
