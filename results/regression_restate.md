# Regression (judge gpt-oss-120b; faithful = level 2, restate-only traces counted as level 2)

## Faithful traces per model and language

| model | lang | traces | faithful | rate |
|---|---|---|---|---|
| gpt-oss-20b | en | 12 | 9 | 75.0% |
| gpt-oss-20b | hi | 38 | 34 | 89.5% |
| gpt-oss-20b | ml | 19 | 15 | 78.9% |
| gpt-oss-20b | zh | 21 | 19 | 90.5% |
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
| H2 language vs. English | hi vs. en | 2.70 | 0.22-33.19 | 0.437 | 1.000 |
| H2 language vs. English | ml vs. en | 0.38 | 0.03-4.10 | 0.423 | 1.000 |
| H2 language vs. English | zh vs. en | 1.26 | 0.11-14.44 | 0.854 | 1.000 |
| H1 model pairs | qwen3.8-27b vs. gpt-oss-20b | 2.89 | 0.64-13.01 | 0.167 | 0.333 |
| H1 model pairs | r1-distill-llama-8b vs. gpt-oss-20b | 0.17 | 0.01-2.17 | 0.171 | 0.333 |
| H1 model pairs | qwen3.8-27b vs. r1-distill-llama-8b | 17.49 | 1.23-249.55 | 0.035 | 0.105 |
| H3 hint pairs | expert vs. leaked | 0.92 | 0.23-3.64 | 0.907 | 0.907 |
| H3 hint pairs | metadata vs. leaked | 7.18 | 1.72-29.93 | 0.007 | 0.014 |
| H3 hint pairs | expert vs. metadata | 0.13 | 0.04-0.43 | <0.001 | 0.003 |
| subject area | humanities vs. stem | 1.31 | 0.49-3.52 | 0.595 | 0.595 |

## Model x language interaction

Interaction model not fitted: regression did not converge: some level (or model x language cell) has all or no faithful traces, or no traces at all.
