# Sample-size check

## Planning table (influence 25%, faithfulness near 50%, 80% power)

| questions | comparison | influenced runs per group | alpha split over | smallest detectable difference |
|---|---|---|---|---|
| 250 | two languages, all models together | 562 | 3 | 9.6 points |
| 250 | two models, all languages together | 750 | 3 | 8.4 points |
| 250 | two languages within one model | 188 | 1 | 14.5 points |
| 250 | one model, language and hint type | 62 | - | +/-12.4 points (95% CI, descriptive) |
| 300 | two languages, all models together | 675 | 3 | 8.8 points |
| 300 | two models, all languages together | 900 | 3 | 7.6 points |
| 300 | two languages within one model | 225 | 1 | 13.2 points |
| 300 | one model, language and hint type | 75 | - | +/-11.3 points (95% CI, descriptive) |
| 450 | two languages, all models together | 1012 | 3 | 7.2 points |
| 450 | two models, all languages together | 1350 | 3 | 6.2 points |
| 450 | two languages within one model | 338 | 1 | 10.8 points |
| 450 | one model, language and hint type | 112 | - | +/-9.2 points (95% CI, descriptive) |

## Pilot rule on the logged runs (D:\Code\Audit-on-AI-thought-processing\runs)

Same-language hints, determined runs only. A model below 15% influence is raised to 450 questions.

| model | questions so far | determined hinted runs | influenced | influence rate (95% CI) | questions needed | influenced per language (projected) | detectable difference within the model | note |
|---|---|---|---|---|---|---|---|---|
| gpt-oss-20b | 141 | 1659 | 315 | 19.0% (17.2%-20.9%) | 300 | 168 | 15.3 points |  |
| qwen3.8-27b | 137 | 1619 | 396 | 24.5% (22.4%-26.6%) | 300 | 218 | 13.4 points |  |
| r1-distill-llama-8b | 45 | 460 | 115 | 25.0% (21.3%-29.2%) | 300 | 192 | 14.3 points |  |
