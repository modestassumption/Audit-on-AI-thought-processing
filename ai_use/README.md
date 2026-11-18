# AI use: Claude's faithfulness check (declared)

Claude (Anthropic, through Claude Code) made every label in this folder by reading traces against
`docs/scoring_guide.md`. These are AI labels, not human labels. They were used only to check the
gpt-oss-120b judge. No script or result reads this folder. All study numbers come from
`labels/gpt-oss-120b/`.

## Files

| File | What it is |
|---|---|
| `qwen3.8-27b/2026-11-18-shard6-claude.jsonl` | One label per influenced qwen3.8-27b trace from `runs/qwen3.8-27b/2026-11-18-laptop-vqoqn10r.jsonl`, shard 6/7 (`int(sha256(qid), 16) % 7 == 5`) |
| `code/select_traces.py` | Picks the traces using the rule in `src/cotaudit/analysis/influence.py`: current prompt hash, one row per `run_id`, both no-hint baselines present, and neither baseline chose the hinted option. It also writes a reading view for each trace (passages near hint words plus the last 300 characters) |
| `code/labels.txt` | Claude's labels as `index\|level\|restate_only\|answer_mentions_hint\|note`, in the selection order |
| `code/build_labels.py` | Builds the JSONL from `labels.txt` and compares it with the judge (read-only) |

## Counts (2026-11-18-shard6-claude.jsonl)

| Traces | Level 0 | Level 1 | Level 2 | Marked unsure | `restate_only` | `answer_mentions_hint` |
|---|---|---|---|---|---|---|
| 110 | 0 | 4 | 106 | 2 | 1 | 17 |

No traces were excluded. Every trace finished with `stop` and had non-empty reasoning.

**Agreement with the judge:** all 110 traces have a current gpt-oss-120b label in
`labels/gpt-oss-120b/2026-11-18-sashwath-s6-deepinfra.jsonl`. Claude and the judge gave the same
level on 98 of 110. In 6 of the 12 disagreements the judge gave Level 0 to a trace that, on
reading, says outright that it goes with the hinted answer.
