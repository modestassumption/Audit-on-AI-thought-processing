# Compute: limits, shards, usage

## Groq free-tier limits (from Settings → Limits; fill in, with the date checked)

| Model | RPM | RPD | TPM | TPD | Checked by / date |
|---|---|---|---|---|---|
| openai/gpt-oss-20b | | | | | |
| qwen/qwen3.8-27b (tested model + 2nd judge) | | | | | |
| openai/gpt-oss-120b (judge) | | | | | |

After the pilot, project the quota with the TPD values:

```bash
uv run python scripts/report_runs.py --tpd gpt-oss-20b=<TPD> qwen3.8-27b=<TPD> --keys <n> --out results/pilot.md
```

Groq's model list changes. To check what your key can use:

```bash
uv run python -c "from dotenv import load_dotenv; load_dotenv(); import groq; from cotaudit.runners.groq_runner import keys_from_env; k = next(iter(keys_from_env().values())); print(sorted(m.id for m in groq.Groq(api_key=k).models.list().data))"
```

On 2026-10-28 Qwen3-32B and Llama-3.3-70B were gone; see `configs/experiment.yaml` for the replacements.

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
