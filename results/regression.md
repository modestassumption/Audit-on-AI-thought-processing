# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 56 | 40 | 71.4% |
| gpt-oss-20b | hi | 150 | 130 | 86.7% |
| gpt-oss-20b | ml | 81 | 56 | 69.1% |
| gpt-oss-20b | zh | 88 | 68 | 77.3% |
| qwen3.8-27b | en | 72 | 69 | 95.8% |
| qwen3.8-27b | hi | 132 | 130 | 98.5% |
| qwen3.8-27b | ml | 154 | 143 | 92.9% |
| qwen3.8-27b | zh | 124 | 121 | 97.6% |
| r1-distill-llama-8b | en | 18 | 5 | 27.8% |
| r1-distill-llama-8b | hi | 45 | 28 | 62.2% |
| r1-distill-llama-8b | ml | 36 | 12 | 33.3% |
| r1-distill-llama-8b | zh | 14 | 5 | 35.7% |

## H1-H3: main-effects GEE, grouped by question

970 traces, 169 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 3.25 | 1.86-5.68 | <0.001 | <0.001 |
| H2 language vs. English | ml vs. en | 0.88 | 0.50-1.56 | 0.664 | 0.664 |
| H2 language vs. English | zh vs. en | 1.60 | 0.91-2.79 | 0.101 | 0.201 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 7.50 | 4.40-12.78 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.24 | 0.13-0.45 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 30.76 | 13.90-68.08 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.43 | 0.25-0.73 | 0.002 | 0.004 |
| H3 hint pairs | metadata vs. leaked | 1.18 | 0.73-1.88 | 0.501 | 0.501 |
| H3 hint pairs | expert vs. metadata | 0.36 | 0.21-0.62 | <0.001 | <0.001 |
| subject area | humanities vs. stem | 1.82 | 1.10-3.00 | 0.020 | 0.020 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 2.79, p = 0.835.
