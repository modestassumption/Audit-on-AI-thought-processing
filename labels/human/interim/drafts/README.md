# Claude draft labels for the interim set (not human labels)

`Visakh-draft.csv` holds tentative levels for the 60 items in `../items.csv`, written by Claude
on 2026-11-18 following `docs/scoring_guide.md`. The team asked for them as a starting point to
read and correct.

- **They are not human labels.** They sit in this subfolder so that `agreement.py` and
  `--human interim` never read them as a labeller. Don't copy them into `labels/human/interim/`,
  and don't report them as human agreement.
- **How they were made:** each trace was read at its start and end, plus every passage where the
  hint or its source is mentioned (searched in all four languages). Every Level 0 should be
  confirmed by reading the full trace; the notes say which.
- **`answer_mentions_hint` is blank,** because the final answer section is not in `items.csv`.
- **Totals:** 52 Level 2, 3 Level 1 (all `restate_only`), 5 Level 0.
- **Against the judge:** 18 of the 60 items have a judge label so far, and the draft agrees on 15
  of them.

To label for real, each labeller copies `../items.csv` to `../<name>.csv` and fills it in.
