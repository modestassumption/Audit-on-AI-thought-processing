# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 88 | 66 | 75.0% |
| gpt-oss-20b | hi | 234 | 199 | 85.0% |
| gpt-oss-20b | ml | 137 | 97 | 70.8% |
| gpt-oss-20b | zh | 151 | 117 | 77.5% |
| qwen3.8-27b | en | 113 | 109 | 96.5% |
| qwen3.8-27b | hi | 205 | 196 | 95.6% |
| qwen3.8-27b | ml | 232 | 214 | 92.2% |
| qwen3.8-27b | zh | 187 | 181 | 96.8% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 123 | 52.3% |
| r1-distill-llama-8b | ml | 266 | 77 | 28.9% |
| r1-distill-llama-8b | zh | 86 | 20 | 23.3% |

## H1-H3: main-effects GEE, grouped by question

2021 traces, 270 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.54 | 1.01-2.34 | 0.043 | 0.086 |
| H2 language vs. English | ml vs. en | 0.60 | 0.40-0.91 | 0.015 | 0.045 |
| H2 language vs. English | zh vs. en | 0.75 | 0.50-1.15 | 0.188 | 0.188 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 5.62 | 3.80-8.30 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.13-0.23 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 32.44 | 21.27-49.49 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.93 | 0.67-1.28 | 0.650 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.09 | 0.84-1.41 | 0.536 | 1.000 |
| H3 hint pairs | expert vs. metadata | 0.86 | 0.61-1.20 | 0.367 | 1.000 |
| subject area | humanities vs. stem | 1.43 | 1.06-1.94 | 0.021 | 0.021 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 12.43, p = 0.053.
