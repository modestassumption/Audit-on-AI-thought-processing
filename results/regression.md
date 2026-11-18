# Regression (judge gpt-oss-120b; faithful = level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 12 | 9 | 75.0% |
| gpt-oss-20b | hi | 38 | 34 | 89.5% |
| gpt-oss-20b | ml | 19 | 14 | 73.7% |
| gpt-oss-20b | zh | 21 | 18 | 85.7% |
| qwen3.8-27b | en | 16 | 16 | 100.0% |
| qwen3.8-27b | hi | 32 | 31 | 96.9% |
| qwen3.8-27b | ml | 39 | 36 | 92.3% |
| qwen3.8-27b | zh | 29 | 27 | 93.1% |
| r1-distill-llama-8b | hi | 2 | 2 | 100.0% |
| r1-distill-llama-8b | ml | 4 | 0 | 0.0% |

## H1-H3: main-effects GEE, grouped by question

212 traces, 39 questions. Odds ratio > 1: more often faithful than the comparison level.

| family | comparison | odds ratio | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H2 language vs. English | hi vs. en | 2.79 | 0.22-35.95 | 0.431 | 0.970 |
| H2 language vs. English | ml vs. en | 0.29 | 0.02-3.42 | 0.323 | 0.970 |
| H2 language vs. English | zh vs. en | 0.98 | 0.08-11.63 | 0.988 | 0.988 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 3.59 | 0.82-15.72 | 0.089 | 0.178 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.20 | 0.02-2.41 | 0.206 | 0.206 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 17.83 | 1.36-233.44 | 0.028 | 0.084 |
| H3 hint pairs | expert vs. leaked | 0.83 | 0.21-3.28 | 0.792 | 0.792 |
| H3 hint pairs | metadata vs. leaked | 8.85 | 2.10-37.30 | 0.003 | 0.006 |
| H3 hint pairs | expert vs. metadata | 0.09 | 0.02-0.36 | <0.001 | 0.002 |
| subject area | humanities vs. stem | 1.09 | 0.44-2.68 | 0.857 | 0.857 |

## Model x language interaction

Interaction model not fitted: regression did not converge: some level (or model x language cell) has all or no faithful traces, or no traces at all.
