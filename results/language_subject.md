# Reasoning language and subject area

## Which language is the reasoning in? (all runs with reasoning; a trace counts as one language when 60% of its words are in that script, otherwise mixed)

| model | lang | traces | in en | in hi | in zh | in ml | in mixed | own language | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | en | 705 | 705 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| gpt-oss-20b | hi | 844 | 758 | 12 | 0 | 0 | 74 | 1.4% | 0.6%-2.4% |
| gpt-oss-20b | ml | 840 | 816 | 0 | 0 | 0 | 24 | 0.0% | 0.0%-0.0% |
| gpt-oss-20b | zh | 840 | 633 | 0 | 34 | 0 | 173 | 4.0% | 2.4%-6.0% |
| qwen3.8-27b | en | 685 | 685 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| qwen3.8-27b | hi | 821 | 815 | 0 | 0 | 0 | 6 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | ml | 816 | 815 | 0 | 0 | 0 | 1 | 0.0% | 0.0%-0.0% |
| qwen3.8-27b | zh | 816 | 644 | 0 | 160 | 0 | 12 | 19.6% | 16.5%-22.8% |
| r1-distill-llama-8b | en | 225 | 225 | 0 | 0 | 0 | 0 | 100.0% | 100.0%-100.0% |
| r1-distill-llama-8b | hi | 270 | 220 | 0 | 50 | 0 | 0 | 0.0% | 0.0%-0.0% |
| r1-distill-llama-8b | ml | 270 | 270 | 0 | 0 | 0 | 0 | 0.0% | 0.0%-0.0% |
| r1-distill-llama-8b | zh | 270 | 0 | 0 | 270 | 0 | 0 | 100.0% | 100.0%-100.0% |

## Is the hint admitted less often when the reasoning switches language? (judge gpt-oss-120b; faithful = level 2; same-language hints)

| model | lang | stayed in question language | switched | difference, points (stayed - switched) | 95% CI, points | p | p (Holm) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | hi | 1/1 (100.0%) | 33/37 (89.2%) | +10.8 | +0.8 to +20.8 | 0.728 | 1.000 |
| gpt-oss-20b | ml | 0/0 | 14/19 (73.7%) | - | - | - | - |
| gpt-oss-20b | zh | 3/3 (100.0%) | 15/18 (83.3%) | +16.7 | -0.6 to +33.9 | 0.445 | 1.000 |
| qwen3.8-27b | hi | 0/0 | 31/32 (96.9%) | - | - | - | - |
| qwen3.8-27b | ml | 0/0 | 36/39 (92.3%) | - | - | - | - |
| qwen3.8-27b | zh | 1/1 (100.0%) | 26/28 (92.9%) | +7.1 | -2.4 to +16.7 | 0.782 | 1.000 |
| r1-distill-llama-8b | hi | 0/0 | 2/2 (100.0%) | - | - | - | - |
| r1-distill-llama-8b | ml | 0/0 | 0/4 (0.0%) | - | - | - | - |

Adjusted odds ratio not fitted: regression did not converge: some level (or model x language cell) has all or no faithful traces, or no traces at all.

## Influence per subject area (determined runs, same-language hints)

| model | subject_category | questions | influenced | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 16 | 47 | 189 | 24.9% | 19.2%-31.5% | 13.8%-36.2% |
| gpt-oss-20b | STEM | 73 | 119 | 856 | 13.9% | 11.7%-16.4% | 10.2%-17.8% |
| gpt-oss-20b | Social Sciences | 52 | 149 | 614 | 24.3% | 21.0%-27.8% | 18.5%-30.0% |
| qwen3.8-27b | Humanities | 16 | 62 | 192 | 32.3% | 26.1%-39.2% | 23.4%-41.1% |
| qwen3.8-27b | STEM | 71 | 168 | 833 | 20.2% | 17.6%-23.0% | 15.6%-25.2% |
| qwen3.8-27b | Social Sciences | 50 | 166 | 594 | 27.9% | 24.5%-31.7% | 22.3%-34.5% |
| r1-distill-llama-8b | Humanities | 5 | 27 | 53 | 50.9% | 37.9%-63.9% | 38.0%-68.8% |
| r1-distill-llama-8b | STEM | 24 | 51 | 250 | 20.4% | 15.9%-25.8% | 13.2%-28.4% |
| r1-distill-llama-8b | Social Sciences | 16 | 37 | 157 | 23.6% | 17.6%-30.8% | 15.4%-32.5% |

## Faithfulness per subject area (judge gpt-oss-120b; faithful = level 2)

| model | subject_category | questions | faithful | n | rate | 95% Wilson | 95% bootstrap (questions) |
|---|---|---|---|---|---|---|---|
| gpt-oss-20b | Humanities | 3 | 12 | 13 | 92.3% | 66.7%-98.6% | 75.0%-100.0% |
| gpt-oss-20b | STEM | 15 | 30 | 38 | 78.9% | 63.7%-88.9% | 62.9%-96.2% |
| gpt-oss-20b | Social Sciences | 11 | 33 | 39 | 84.6% | 70.3%-92.8% | 76.5%-92.3% |
| qwen3.8-27b | Humanities | 3 | 11 | 13 | 84.6% | 57.8%-95.7% | 66.7%-100.0% |
| qwen3.8-27b | STEM | 18 | 62 | 65 | 95.4% | 87.3%-98.4% | 89.1%-100.0% |
| qwen3.8-27b | Social Sciences | 13 | 37 | 38 | 97.4% | 86.5%-99.5% | 91.7%-100.0% |
| r1-distill-llama-8b | STEM | 2 | 2 | 3 | 66.7% | 20.8%-93.9% | 0.0%-100.0% |
| r1-distill-llama-8b | Social Sciences | 1 | 0 | 3 | 0.0% | 0.0%-56.2% | - |
