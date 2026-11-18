# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 88 | 68 | 77.3% |
| gpt-oss-20b | hi | 234 | 200 | 85.5% |
| gpt-oss-20b | ml | 137 | 101 | 73.7% |
| gpt-oss-20b | zh | 151 | 121 | 80.1% |
| qwen3.8-27b | en | 130 | 126 | 96.9% |
| qwen3.8-27b | hi | 231 | 218 | 94.4% |
| qwen3.8-27b | ml | 266 | 248 | 93.2% |
| qwen3.8-27b | zh | 214 | 204 | 95.3% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 126 | 53.6% |
| r1-distill-llama-8b | ml | 266 | 88 | 33.1% |
| r1-distill-llama-8b | zh | 86 | 23 | 26.7% |

## H1-H3: main-effects GEE, grouped by question

2125 traces, 273 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.40 | 0.93-2.11 | 0.105 | 0.210 |
| H2 language vs. English | ml vs. en | 0.67 | 0.45-0.99 | 0.044 | 0.133 |
| H2 language vs. English | zh vs. en | 0.75 | 0.49-1.15 | 0.190 | 0.210 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 4.69 | 3.18-6.94 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.12-0.22 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 28.45 | 18.73-43.21 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 1.13 | 0.82-1.54 | 0.458 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.05 | 0.82-1.36 | 0.682 | 1.000 |
| H3 hint pairs | expert vs. metadata | 1.07 | 0.76-1.50 | 0.710 | 1.000 |
| subject area | humanities vs. stem | 1.42 | 1.06-1.89 | 0.018 | 0.018 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 13.06, p = 0.042.
