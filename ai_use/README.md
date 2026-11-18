# AI use: Claude's faithfulness check (declared)

**Everything in this folder was produced with an AI assistant: Claude (Anthropic), used through
Claude Code.** Claude read the 226 influenced shard 7/7 traces of gpt-oss-20b and qwen3.8-27b and
gave each a faithfulness level (0, 1 or 2) using `docs/scoring_guide.md`. The labels served only
as a **checker** for the team judge (gpt-oss-120b).

- **No result uses these labels.** No script in `scripts/` or `src/` reads this folder, and every
  number in `results/` and the report comes from the gpt-oss-120b judge (`labels/gpt-oss-120b/`).
- **They are AI labels, not human labels.**
- Scored on 2026-11-18 for Sashwath Swaminathan (sub-team D).

## What is where

Laid out like `runs/`, one folder per model:

| Path | What it is |
|---|---|
| `gpt-oss-20b/2026-11-18-sashwath-claude.jsonl` | Claude's level for each of the 92 influenced gpt-oss-20b traces (`"judge": "claude-manual"`) |
| `qwen3.8-27b/2026-11-18-sashwath-claude.jsonl` | Claude's level for each of the 134 influenced qwen3.8-27b traces |
| `claude_scores.csv` | All 226 labels in one sheet, with a short note on each |
| `shard7_report.md` | Rates per model, language and hint; the Level 1 cases; the comparison with the judge |
| `code/` | How the labels were made: `extract.py` picks the traces, `labels.txt` holds the levels Claude assigned, `build.py` writes the files above. The levels come from Claude reading the traces, not from code. |

## Results at a glance

| | Claude: faithful (Level 2) | Same level as the gpt-oss-120b judge |
|---|---|---|
| gpt-oss-20b | 86 / 92 (93%) | 69 / 90 |
| qwen3.8-27b | 128 / 134 (96%) | 128 / 134 |
| both | 214 / 226 (95%) | 197 / 224 (88%), κ = 0.32 |

A random 20-trace spot-check gave the same level on 16 of the 20. Of the 4 that differed, 3 were
judge misses and 1 was a 1-vs-2 borderline. Details are in `shard7_report.md`.

The tested models and the LLM judges are part of the method, not AI assistance. Other AI-assisted
work is listed in [`docs/ai_use.md`](../docs/ai_use.md).
