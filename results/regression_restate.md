# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 78 | 59 | 75.6% |
| gpt-oss-20b | hi | 206 | 174 | 84.5% |
| gpt-oss-20b | ml | 112 | 85 | 75.9% |
| gpt-oss-20b | zh | 136 | 107 | 78.7% |
| qwen3.8-27b | en | 99 | 96 | 97.0% |
| qwen3.8-27b | hi | 174 | 169 | 97.1% |
| qwen3.8-27b | ml | 199 | 185 | 93.0% |
| qwen3.8-27b | zh | 163 | 158 | 96.9% |
| r1-distill-llama-8b | en | 61 | 25 | 41.0% |
| r1-distill-llama-8b | hi | 160 | 87 | 54.4% |
| r1-distill-llama-8b | ml | 163 | 57 | 35.0% |
| r1-distill-llama-8b | zh | 58 | 21 | 36.2% |

## H1-H3: main-effects GEE, grouped by question

1609 traces, 260 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.67 | 1.07-2.62 | 0.024 | 0.073 |
| H2 language vs. English | ml vs. en | 0.80 | 0.51-1.26 | 0.330 | 0.660 |
| H2 language vs. English | zh vs. en | 1.01 | 0.62-1.66 | 0.967 | 0.967 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 6.19 | 4.02-9.54 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.19 | 0.13-0.26 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 33.11 | 20.79-52.74 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 1.00 | 0.67-1.48 | 0.989 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.01 | 0.74-1.37 | 0.949 | 1.000 |
| H3 hint pairs | expert vs. metadata | 0.99 | 0.65-1.49 | 0.951 | 1.000 |
| subject area | humanities vs. stem | 1.63 | 1.19-2.24 | 0.002 | 0.002 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 3.42, p = 0.755.
