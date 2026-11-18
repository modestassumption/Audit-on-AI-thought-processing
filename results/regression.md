# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 88 | 66 | 75.0% |
| gpt-oss-20b | hi | 234 | 199 | 85.0% |
| gpt-oss-20b | ml | 137 | 97 | 70.8% |
| gpt-oss-20b | zh | 151 | 117 | 77.5% |
| qwen3.8-27b | en | 130 | 126 | 96.9% |
| qwen3.8-27b | hi | 231 | 218 | 94.4% |
| qwen3.8-27b | ml | 266 | 246 | 92.5% |
| qwen3.8-27b | zh | 214 | 204 | 95.3% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 123 | 52.3% |
| r1-distill-llama-8b | ml | 266 | 77 | 28.9% |
| r1-distill-llama-8b | zh | 86 | 20 | 23.3% |

## H1-H3: main-effects GEE, grouped by question

2125 traces, 273 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.45 | 0.96-2.20 | 0.078 | 0.156 |
| H2 language vs. English | ml vs. en | 0.60 | 0.40-0.89 | 0.011 | 0.033 |
| H2 language vs. English | zh vs. en | 0.72 | 0.48-1.08 | 0.114 | 0.156 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 5.02 | 3.42-7.36 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.13-0.23 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 29.00 | 19.22-43.77 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.91 | 0.66-1.25 | 0.549 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.07 | 0.83-1.37 | 0.624 | 1.000 |
| H3 hint pairs | expert vs. metadata | 0.85 | 0.61-1.19 | 0.343 | 1.000 |
| subject area | humanities vs. stem | 1.42 | 1.05-1.91 | 0.023 | 0.023 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 14.64, p = 0.023.
