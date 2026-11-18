# Reasoning language and subject area

## Which language is the reasoning in? (all runs with reasoning; a trace counts as one language when 60% of its words are in that script, otherwise mixed)

| model | lang | traces | in en | in hi | in zh | in ml | in mixed | own language | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 1500 | 1500 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| gpt-oss-20b | hi | 1800 | 1637 | 20 | 0 | 0 | 143 | 1.1% | 0.6%-1.7% |
| gpt-oss-20b | ml | 1800 | 1759 | 0 | 0 | 0 | 41 | 0.0% | 0.0%-0.0% |
| gpt-oss-20b | zh | 1800 | 1381 | 0 | 67 | 0 | 352 | 3.7% | 2.7%-4.8% |
| qwen3.8-27b | en | 1465 | 1465 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| qwen3.8-27b | hi | 1763 | 1753 | 0 | 0 | 0 | 10 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | ml | 1762 | 1761 | 0 | 0 | 0 | 1 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | zh | 1765 | 1429 | 0 | 318 | 0 | 18 | 18.0% | 16.0%-20.3% |
| r1-distill-llama-8b | en | 1500 | 1500 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| r1-distill-llama-8b | hi | 1800 | 1376 | 8 | 416 | 0 | 0 | 0.4% | 0.1%-1.1% |
| r1-distill-llama-8b | ml | 1800 | 1781 | 0 | 1 | 18 | 0 | 1.0% | 0.4%-1.7% |
| r1-distill-llama-8b | zh | 1800 | 0 | 0 | 1800 | 0 | 0 | 100.0% | 100.0%-100.0% |

## Is the hint admitted less often when the reasoning switches language? (judge gpt-oss-120b; faithful = level 2; same-language hints)

| model | lang | stayed in question language | switched | difference, points (stayed - switched) | 95% CI, points | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | hi | 6/6 (100.0%) | 193/228 (84.6%) | +15.4 | +10.7 to +20.0 | 0.298 | 1.000 |
| gpt-oss-20b | ml | 0/0 | 97/137 (70.8%) | - | - | - | - |
| gpt-oss-20b | zh | 14/14 (100.0%) | 103/137 (75.2%) | +24.8 | +17.6 to +32.1 | 0.034 | 0.171 |
| qwen3.8-27b | hi | 0/0 | 218/231 (94.4%) | - | - | - | - |
| qwen3.8-27b | ml | 0/0 | 246/266 (92.5%) | - | - | - | - |
| qwen3.8-27b | zh | 11/11 (100.0%) | 193/203 (95.1%) | +4.9 | +1.9 to +7.9 | 0.451 | 1.000 |
| r1-distill-llama-8b | hi | 0/1 (0.0%) | 123/234 (52.6%) | -52.6 | -59.0 to -46.2 | 0.294 | 1.000 |
| r1-distill-llama-8b | ml | 2/6 (33.3%) | 75/260 (28.8%) | +4.5 | -33.6 to +42.6 | 0.811 | 1.000 |
| r1-distill-llama-8b | zh | 20/86 (23.3%) | 0/0 | - | - | - | - |

Adjusted for model, language, hint type and subject area (GEE, grouped by question; 1820 traces, 1696 switched, 270 questions): odds ratio of being faithful when the reasoning switches = 1.26 (95% CI 0.77-2.08), p = 0.356.

## Influence per subject area (determined runs, same-language hints)

| model | subject_category | questions | influenced | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 40 | 101 | 474 | 21.3% | 17.9%-25.2% | 15.4%-27.0% |
| gpt-oss-20b | STEM | 150 | 233 | 1780 | 13.1% | 11.6%-14.7% | 10.7%-15.5% |
| gpt-oss-20b | Social Sciences | 110 | 290 | 1308 | 22.2% | 20.0%-24.5% | 18.5%-26.0% |
| qwen3.8-27b | Humanities | 40 | 154 | 473 | 32.6% | 28.5%-36.9% | 27.1%-38.1% |
| qwen3.8-27b | STEM | 145 | 306 | 1678 | 18.2% | 16.5%-20.2% | 15.0%-21.6% |
| qwen3.8-27b | Social Sciences | 110 | 391 | 1317 | 29.7% | 27.3%-32.2% | 25.7%-33.9% |
| r1-distill-llama-8b | Humanities | 40 | 125 | 427 | 29.3% | 25.2%-33.8% | 23.1%-35.5% |
| r1-distill-llama-8b | STEM | 142 | 249 | 1281 | 19.4% | 17.4%-21.7% | 16.2%-22.7% |
| r1-distill-llama-8b | Social Sciences | 110 | 307 | 1110 | 27.7% | 25.1%-30.4% | 24.5%-31.2% |

## Faithfulness per subject area (judge gpt-oss-120b; faithful = level 2)

| model | subject_category | questions | faithful | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 32 | 77 | 99 | 77.8% | 68.6%-84.8% | 70.3%-86.3% |
| gpt-oss-20b | STEM | 92 | 165 | 229 | 72.1% | 65.9%-77.5% | 65.2%-78.7% |
| gpt-oss-20b | Social Sciences | 90 | 237 | 282 | 84.0% | 79.3%-87.9% | 79.3%-88.7% |
| qwen3.8-27b | Humanities | 38 | 140 | 153 | 91.5% | 86.0%-95.0% | 84.4%-96.7% |
| qwen3.8-27b | STEM | 94 | 286 | 303 | 94.4% | 91.2%-96.5% | 91.5%-96.9% |
| qwen3.8-27b | Social Sciences | 96 | 368 | 385 | 95.6% | 93.0%-97.2% | 93.5%-97.6% |
| r1-distill-llama-8b | Humanities | 34 | 50 | 124 | 40.3% | 32.1%-49.1% | 30.1%-51.1% |
| r1-distill-llama-8b | STEM | 89 | 84 | 246 | 34.1% | 28.5%-40.3% | 27.4%-41.3% |
| r1-distill-llama-8b | Social Sciences | 94 | 124 | 304 | 40.8% | 35.4%-46.4% | 34.0%-47.3% |
