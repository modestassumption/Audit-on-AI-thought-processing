# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 56 | 41 | 73.2% |
| gpt-oss-20b | hi | 150 | 131 | 87.3% |
| gpt-oss-20b | ml | 81 | 60 | 74.1% |
| gpt-oss-20b | zh | 88 | 71 | 80.7% |
| qwen3.8-27b | en | 72 | 69 | 95.8% |
| qwen3.8-27b | hi | 132 | 130 | 98.5% |
| qwen3.8-27b | ml | 154 | 145 | 94.2% |
| qwen3.8-27b | zh | 124 | 121 | 97.6% |
| r1-distill-llama-8b | en | 18 | 5 | 27.8% |
| r1-distill-llama-8b | hi | 45 | 29 | 64.4% |
| r1-distill-llama-8b | ml | 36 | 12 | 33.3% |
| r1-distill-llama-8b | zh | 14 | 5 | 35.7% |

## H1-H3: main-effects GEE, grouped by question

970 traces, 169 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 3.26 | 1.81-5.87 | <0.001 | <0.001 |
| H2 language vs. English | ml vs. en | 1.03 | 0.56-1.89 | 0.927 | 0.927 |
| H2 language vs. English | zh vs. en | 1.69 | 0.92-3.09 | 0.090 | 0.180 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 7.35 | 4.22-12.82 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.21 | 0.11-0.38 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 35.44 | 16.17-77.67 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.56 | 0.33-0.97 | 0.039 | 0.078 |
| H3 hint pairs | metadata vs. leaked | 1.05 | 0.66-1.68 | 0.823 | 0.823 |
| H3 hint pairs | expert vs. metadata | 0.53 | 0.32-0.91 | 0.020 | 0.060 |
| subject area | humanities vs. stem | 1.84 | 1.12-3.03 | 0.017 | 0.017 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 2.75, p = 0.839.
