# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 88 | 68 | 77.3% |
| gpt-oss-20b | hi | 234 | 200 | 85.5% |
| gpt-oss-20b | ml | 137 | 101 | 73.7% |
| gpt-oss-20b | zh | 151 | 121 | 80.1% |
| qwen3.8-27b | en | 113 | 109 | 96.5% |
| qwen3.8-27b | hi | 205 | 196 | 95.6% |
| qwen3.8-27b | ml | 232 | 216 | 93.1% |
| qwen3.8-27b | zh | 187 | 181 | 96.8% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 126 | 53.6% |
| r1-distill-llama-8b | ml | 266 | 88 | 33.1% |
| r1-distill-llama-8b | zh | 86 | 23 | 26.7% |

## H1-H3: main-effects GEE, grouped by question

2021 traces, 270 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.49 | 0.98-2.25 | 0.059 | 0.175 |
| H2 language vs. English | ml vs. en | 0.67 | 0.45-1.01 | 0.058 | 0.175 |
| H2 language vs. English | zh vs. en | 0.79 | 0.51-1.23 | 0.297 | 0.297 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 5.32 | 3.57-7.93 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.16 | 0.12-0.22 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 32.26 | 21.01-49.53 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 1.16 | 0.84-1.58 | 0.366 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.07 | 0.82-1.40 | 0.601 | 1.000 |
| H3 hint pairs | expert vs. metadata | 1.08 | 0.76-1.53 | 0.675 | 1.000 |
| subject area | humanities vs. stem | 1.43 | 1.07-1.92 | 0.015 | 0.015 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 11.01, p = 0.088.
