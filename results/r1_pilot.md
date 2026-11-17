# Run report

## Run health

| model | lang | runs | questions | reasoning returned | answer extracted | truncated | baseline accuracy | baseline reps agree | picked hint, no hint |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | 250 | 50 | 100% | 90% | 10% | 81% | 95% | 2% |
| r1-distill-llama-8b | hi | 300 | 50 | 100% | 96% | 4% | 52% | 64% | 16% |
| r1-distill-llama-8b | ml | 300 | 50 | 100% | 96% | 4% | 41% | 52% | 13% |
| r1-distill-llama-8b | zh | 300 | 50 | 100% | 83% | 17% | 61% | 84% | 4% |

## Influence (hint picked, neither baseline picked it)

| model | lang | hint | runs | determined | picked hint, with hint | influenced | influence rate | 95% CI | influenced (rep1 only) |
|---|---|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | en | expert | 50 | 39 | 16% | 3 | 8% | 3%-20% | 5 |
| r1-distill-llama-8b | en | leaked | 50 | 39 | 36% | 14 | 36% | 23%-52% | 15 |
| r1-distill-llama-8b | en | metadata | 50 | 40 | 12% | 3 | 8% | 3%-20% | 3 |
| r1-distill-llama-8b | hi | expert | 50 | 46 | 60% | 20 | 43% | 30%-58% | 21 |
| r1-distill-llama-8b | hi | expert(en) | 50 | 46 | 36% | 9 | 20% | 11%-33% | 11 |
| r1-distill-llama-8b | hi | leaked | 50 | 45 | 48% | 19 | 42% | 29%-57% | 19 |
| r1-distill-llama-8b | hi | metadata | 50 | 47 | 34% | 10 | 21% | 12%-35% | 10 |
| r1-distill-llama-8b | ml | expert | 50 | 44 | 44% | 13 | 30% | 18%-44% | 17 |
| r1-distill-llama-8b | ml | expert(en) | 50 | 43 | 66% | 22 | 51% | 37%-65% | 25 |
| r1-distill-llama-8b | ml | leaked | 50 | 43 | 50% | 15 | 35% | 22%-50% | 20 |
| r1-distill-llama-8b | ml | metadata | 50 | 44 | 52% | 13 | 30% | 18%-44% | 18 |
| r1-distill-llama-8b | zh | expert | 50 | 33 | 22% | 7 | 21% | 11%-38% | 7 |
| r1-distill-llama-8b | zh | expert(en) | 50 | 35 | 20% | 6 | 17% | 8%-33% | 6 |
| r1-distill-llama-8b | zh | leaked | 50 | 30 | 26% | 7 | 23% | 12%-41% | 8 |
| r1-distill-llama-8b | zh | metadata | 50 | 34 | 16% | 2 | 6% | 2%-19% | 2 |

## Token use and quota

| model | runs | completion tokens mean | completion tokens p95 | total tokens / run | projected tokens, full grid | key-days needed | days with 7 keys |
|---|---|---|---|---|---|---|---|
| r1-distill-llama-8b | 1150 | 1418 | 4608 | 1783 | 12.3M | - | - |
