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
| r1-distill-llama-8b | en | 87 | 38 | 43.7% |
| r1-distill-llama-8b | hi | 235 | 123 | 52.3% |
| r1-distill-llama-8b | ml | 266 | 77 | 28.9% |
| r1-distill-llama-8b | zh | 86 | 20 | 23.3% |

## H1-H3: main-effects GEE, grouped by question

1841 traces, 266 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 1.59 | 1.03-2.45 | 0.035 | 0.105 |
| H2 language vs. English | ml vs. en | 0.63 | 0.41-0.97 | 0.035 | 0.105 |
| H2 language vs. English | zh vs. en | 0.72 | 0.46-1.11 | 0.134 | 0.134 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 6.61 | 4.35-10.03 | <0.001 | <0.001 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.13-0.23 | <0.001 | <0.001 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 38.73 | 24.85-60.36 | <0.001 | <0.001 |
| H3 hint pairs | expert vs. leaked | 0.97 | 0.70-1.35 | 0.851 | 1.000 |
| H3 hint pairs | metadata vs. leaked | 1.00 | 0.76-1.31 | 0.974 | 1.000 |
| H3 hint pairs | expert vs. metadata | 0.97 | 0.69-1.38 | 0.879 | 1.000 |
| subject area | humanities vs. stem | 1.49 | 1.09-2.05 | 0.013 | 0.013 |

## Model x language interaction

Joint Wald test of the 6 model x language terms: chi2 = 10.72, p = 0.097.
