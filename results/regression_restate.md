# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 78 | 59 | 75.6% |
| gpt-oss-20b | hi | 207 | 175 | 84.5% |
| gpt-oss-20b | ml | 112 | 85 | 75.9% |
| gpt-oss-20b | zh | 136 | 107 | 78.7% |
| qwen3.8-27b | en | 99 | 96 | 97.0% |
| qwen3.8-27b | hi | 175 | 170 | 97.1% |
| qwen3.8-27b | ml | 200 | 186 | 93.0% |
| qwen3.8-27b | zh | 164 | 159 | 97.0% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 126 | 53.6% |
| r1-distill-llama-8b | ml | 266 | 88 | 33.1% |
| r1-distill-llama-8b | zh | 86 | 23 | 26.7% |

## H1-H3: main-effects GEE, grouped by question

1845 traces, 267 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.54 | 1.00-2.37 | 0.048 | 0.145 |
| H2 language vs. English | ml vs. en | 0.71 | 0.46-1.08 | 0.112 | 0.224 |
| H2 language vs. English | zh vs. en | 0.75 | 0.48-1.19 | 0.222 | 0.224 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 6.36 | 4.14-9.78 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.16 | 0.12-0.22 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 39.51 | 25.22-61.91 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 1.22 | 0.89-1.69 | 0.219 | 0.658 |
| H3 hint pairs | metadata vs. leaked | 0.99 | 0.75-1.31 | 0.954 | 0.954 |
| H3 hint pairs | expert vs. metadata | 1.23 | 0.87-1.76 | 0.247 | 0.658 |
| subject area | humanities vs. stem | 1.52 | 1.12-2.05 | 0.007 | 0.007 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 8.98, p = 0.175.
