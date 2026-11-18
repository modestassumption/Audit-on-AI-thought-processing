# Compute: limits, shards, usage

## Groq free-tier limits (from Settings → Limits; fill in, with the date checked)

| Model | RPM | RPD | TPM | TPD | Checked by / date |
|---|---|---|---|---|---|
| openai/gpt-oss-20b |30|1K|8K|200K|28-10-2026|
| qwen/qwen3.8-27b |30|1K|8K|200K|28-10-2026|
| openai/gpt-oss-120b (judge) |30|1K|8K|200K|28-10-2026|
| meta-llama/llama-prompt-guard-2-86m |30|14.4K|15K|500K|28-10-2026|

After the pilot, project the quota with the TPD values:

```bash
uv run python scripts/report_runs.py --tpd gpt-oss-20b=<TPD> qwen3-32b=<TPD> --keys <n> --out results/pilot.md
```

## Shards

| Shard | Member | Key ready | Smoke test passed |
|---|---|---|---|
| 1/7 | Visakh V Menon | yes | yes (17-11-2026) |
| 2/7 | Yash Agarwal | yes | yes |
| 3/7 | Sanjay Rajkumar | yes (runs logged 11-11-2026) | |
| 4/7 | Shreyas Ghosh | yes | yes |
| 5/7 | Shreyas Khunteta | | |
| 6/7 | Jayant M. M. Sundaram | | |
| 7/7 | Sashwath Swaminathan | ✓ | ✓ (16-11-2026) |

If someone can't run their shard, another member runs it with the same `--shard i/7`; the logs
resume across machines once pushed.

### Final run coverage (Groq runs frozen 18-11-2026, 19:30 IST)

Current runs per shard (conditions with a run on the current prompt; `load_runs()`):

| Shard | Conditions | gpt-oss-20b | qwen3.8-27b | r1-distill-llama-8b (Kaggle) |
|---|---|---|---|---|
| 1/7 | 805 | 805 | 805 | 805 |
| 2/7 | 1,035 | 1,035 | 1,035 | 1,035 |
| 3/7 | 1,219 | 1,219 | 1,219 | 1,219 |
| 4/7 | 966 | 966 | 966 | 966 |
| 5/7 | 943 | 943 | 943 | 943 |
| 6/7 | 1,012 | 1,012 | **48** | 1,012 |
| 7/7 | 920 | 920 | 920 | 920 |
| **Total** | **6,900** | **6,900** | **5,936** | **6,900** |

qwen3.8-27b shard 6/7 was not finished before the freeze (964 runs missing); every other
model × shard is complete. Shard 6/7 gpt-oss-20b runs are in `runs/gpt-oss-20b/2026-11-18-jayant.jsonl`.

## Kaggle GPU hours

| Date | Account | Hours | Runs logged | Notes |
|---|---|---|---|---|
| 2026-11-16 | Sanjay Rajkumar (Team B) | 2.24 | 1,150 | R1-Distill pilot, 50 questions, T4 x2 (`docs/runs.md`); hours of the earlier unusable attempt not recorded |
| 2026-11-16 | Sanjay Rajkumar (Team B) | 5.9 | 2,750 | R1-Distill main run A (en + hi), T4 x2 |
| 2026-11-16 | Sanjay Rajkumar (Team B) | 7.1 | 3,000 | R1-Distill main run B (zh + ml), T4 x2, in parallel with A |
| 2026-11-17 | Sanjay Rajkumar (Team B) | not recorded | 437 | R1-Distill top-up for the 19 questions changed by the Malayalam review |
