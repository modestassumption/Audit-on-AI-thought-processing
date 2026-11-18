# AI use declaration (sub-team D, Sashwath Swaminathan)

**The material in this folder was made with an AI assistant: Claude (Anthropic), used through
Claude Code.**

## What Claude did

- Read the 226 influenced shard 7/7 traces (gpt-oss-20b 92, qwen3.8-27b 134) and gave each a
  faithfulness level (0, 1 or 2) using `docs/scoring_guide.md`, as a check on the team judge
  (gpt-oss-120b).
- Wrote the code in `code/` and the comparison in `shard7_report.md`.

## Labels removed

The AI labels were deleted from this folder on 2026-11-18:

- `gpt-oss-20b/2026-11-18-sashwath-claude.jsonl`
- `qwen3.8-27b/2026-11-18-sashwath-claude.jsonl`
- `claude_scores.csv`
- `code/labels.txt`

They remain in the git history (commit 9df9a9d, folder `ai_use/`). `shard7_report.md` and `code/`
still describe them.

## What uses them

Nothing. No script in `scripts/` or `src/` read these labels, and every number in `results/` and
the report comes from the gpt-oss-120b judge (`labels/gpt-oss-120b/`). They were AI labels, not
human labels.

Other AI-assisted work in the repository is listed in [`docs/ai_use.md`](../docs/ai_use.md).
