# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 78 | 57 | 73.1% |
| gpt-oss-20b | hi | 206 | 173 | 84.0% |
| gpt-oss-20b | ml | 112 | 82 | 73.2% |
| gpt-oss-20b | zh | 136 | 103 | 75.7% |
| qwen3.8-27b | en | 99 | 96 | 97.0% |
| qwen3.8-27b | hi | 174 | 169 | 97.1% |
| qwen3.8-27b | ml | 199 | 183 | 92.0% |
| qwen3.8-27b | zh | 163 | 158 | 96.9% |
| r1-distill-llama-8b | en | 61 | 25 | 41.0% |
| r1-distill-llama-8b | hi | 160 | 84 | 52.5% |
| r1-distill-llama-8b | ml | 163 | 49 | 30.1% |
| r1-distill-llama-8b | zh | 58 | 19 | 32.8% |

## H1-H3: main-effects GEE, grouped by question

1609 traces, 260 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.74 | 1.11-2.72 | 0.015 | 0.046 |
| H2 language vs. English | ml vs. en | 0.71 | 0.45-1.11 | 0.136 | 0.271 |
| H2 language vs. English | zh vs. en | 0.97 | 0.60-1.59 | 0.910 | 0.910 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 6.40 | 4.21-9.74 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.20 | 0.14-0.27 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 32.64 | 20.53-51.90 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.76 | 0.51-1.12 | 0.169 | 0.377 |
| H3 hint pairs | metadata vs. leaked | 1.04 | 0.76-1.41 | 0.809 | 0.809 |
| H3 hint pairs | expert vs. metadata | 0.73 | 0.49-1.09 | 0.126 | 0.377 |
| subject area | humanities vs. stem | 1.62 | 1.17-2.25 | 0.004 | 0.004 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 4.51, p = 0.608.
