# AI-use declaration

This page lists the work in this repository that an AI assistant (Claude, Anthropic, via Claude
Code) drafted or carried out, so it can be copied into the report's AI-use declaration. It covers
sub-team A's commits from 11 to 18 November 2026 (Visakh V Menon) and the files below that say
they were Claude-drafted. **Each member should add any other AI use in
their own work before submission.** The LLM judge (gpt-oss-120b) and the tested models are part
of the method, not assistance, and are described in the methods section.

## Drafted by Claude, checked and accepted by a team member

| Work | Where | Checked by |
|---|---|---|
| Malayalam question review: verdicts and notes on the 60-question sample (13 marked bad) | `data/review/ml_review_60.csv` (`reviewer` column) | Visakh V Menon (native speaker) accepted the drafts |
| Notes on the Hindi and Malayalam prompt text (instructions, hints, subject names) | `docs/translation_review.md` | Hindi: Yash Agarwal reviewed the text directly. Malayalam: Visakh V Menon accepted the notes |
| Chinese prompt check by back-translation | `docs/translation_review.md` | Compared against the English source text |
| Review of the traces flagged by the keyword filter (F1/F2) | `labels/gpt-oss-120b/flag_review.csv` | Draft verdicts; a team member must confirm them |
| Faithfulness levels for the 226 influenced shard 7/7 traces (gpt-oss-20b, qwen3.8-27b), scored for sub-team D. **AI labels, not human labels:** kept outside `labels/`, so no result uses them | `results/shard7_claude_scoring/` | Spot-checked by Sashwath Swaminathan (sub-team D): 16 of 20 random traces match the judge's level, and the 4 disagreements were re-read in full (`README.md` there). On the 5 traces Jayant hand-audited, all agree. Still AI labels |
| Tentative levels for the 60-item interim labelling set, as a reading aid. **Not human labels:** never used by `agreement.py` or any result | was `labels/human/interim/drafts/Visakh-draft.csv` | Never checked; removed from the repository on 18 November 2026 |

## Code, runs and analysis carried out with Claude

All by Visakh V Menon's sub-team A, committed under his name with Claude's assistance (11–18 November 2026):

- **Malayalam data quality:** a structural screen for passages, premises and formulas dropped in
  translation (`src/cotaudit/data/screen.py`), and review verdicts kept across dataset rebuilds
  (`src/cotaudit/data/review.py`).
- **Pipeline maintenance:**
  - merging the sub-team branches (on 18 November: Team-B's R1-Distill runs and labels and the
    shard 4/7 runs, after checking that no run file was lost and that the renamed shard 3/7 logs
    match the earlier ones field for field);
  - removing 134 duplicate judge labels from `labels/gpt-oss-120b/2026-11-18-hpomenv.jsonl`
    (traces already judged in other label files);
  - counting only judge and human labels that belong to current traces (`analysis/influence.py`,
    `scripts/agreement.py`, `analysis/regression.py`);
  - the "human labels only" robustness check;
  - a test fix in `run_vllm`.
- **Shard 1/7:** smoke test, gpt-oss-20b and qwen3.8-27b runs (805 each), and judge labels. The
  runs and labels themselves come from the models; Claude ran the scripts.
- **Results and documents:**
  - generating `results/` with sub-team D's scripts;
  - the changes-from-proposal list in `README.md`;
  - the Kaggle hours log;
  - the final work plan that split the remaining judging and reporting between sub-teams (18 November);
  - this page.
- **Final judging:** gpt-oss-120b labels for r1-distill-llama-8b shard 6/7, gpt-oss-20b and
  qwen3.8-27b shard 2/7, and qwen3.8-27b shard 3/7 (`*-visakh-final*.jsonl`). Claude ran the
  judge script; the labels come from the judge model.

## Sub-team C (Shreyas Khunteta)

Claude (via Claude Code) helped draft sub-team C's scoring and judging code and documents and ran
the shard 5/7 and judge scripts; all of it was reviewed and committed by Shreyas Khunteta.
