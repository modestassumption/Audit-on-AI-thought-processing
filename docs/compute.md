# Compute: limits, shards, usage

## Groq free-tier limits (from Settings → Limits; fill in, with the date checked)

| Model | RPM | RPD | TPM | TPD | Checked by / date |
|---|---|---|---|---|---|
| openai/gpt-oss-20b |30|1K|8K|200K|28-10-2026|
| qwen/qwen3.8-27b |30|1K|8K|200K|28-10-2026|
| openai/gpt-oss-120b (judge) |30|1K|8K|200K|28-10-2026|
| meta-llama/llama-prompt-guard-2-86m (2nd judge) |30|14.4K|15K|500K|28-10-2026|

After the pilot, project the quota with the TPD values:

```bash
uv run python scripts/report_runs.py --tpd gpt-oss-20b=<TPD> qwen3-32b=<TPD> --keys <n> --out results/pilot.md
```

## Shards

| Shard | Member | Key ready | Smoke test passed |
|---|---|---|---|
| 1/7 | Visakh V Menon | | |
| 2/7 | Yash Agarwal | | |
| 3/7 | Sanjay Rajkumar | | |
| 4/7 | Shreyas Ghosh | | |
| 5/7 | Shreyas Khunteta | | |
| 6/7 | Jayant M. M. Sundaram | | |
| 7/7 | Sashwath Swaminathan | | |

If someone can't run their shard, another member runs it with the same `--shard i/7`; the logs
resume across machines once pushed.

## Kaggle GPU hours

| Date | Account | Hours | Runs logged | Notes |
|---|---|---|---|---|
