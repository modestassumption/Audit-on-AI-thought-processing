# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 78 | 57 | 73.1% |
| gpt-oss-20b | hi | 207 | 174 | 84.1% |
| gpt-oss-20b | ml | 112 | 82 | 73.2% |
| gpt-oss-20b | zh | 136 | 103 | 75.7% |
| qwen3.8-27b | en | 99 | 96 | 97.0% |
| qwen3.8-27b | hi | 175 | 170 | 97.1% |
| qwen3.8-27b | ml | 200 | 184 | 92.0% |
| qwen3.8-27b | zh | 164 | 159 | 97.0% |
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 123 | 52.3% |
| r1-distill-llama-8b | ml | 266 | 77 | 28.9% |
| r1-distill-llama-8b | zh | 86 | 20 | 23.3% |

## H1-H3: main-effects GEE, grouped by question

1845 traces, 267 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.60 | 1.04-2.46 | 0.034 | 0.103 |
| H2 language vs. English | ml vs. en | 0.63 | 0.41-0.97 | 0.036 | 0.103 |
| H2 language vs. English | zh vs. en | 0.72 | 0.46-1.11 | 0.134 | 0.134 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 6.63 | 4.37-10.06 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.13-0.23 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 38.93 | 24.98-60.67 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.97 | 0.70-1.35 | 0.844 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 0.99 | 0.76-1.31 | 0.964 | 1.000 |
| H3 hint pairs | expert vs. metadata | 0.97 | 0.69-1.38 | 0.880 | 1.000 |
| subject area | humanities vs. stem | 1.50 | 1.09-2.06 | 0.012 | 0.012 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 10.69, p = 0.098.
