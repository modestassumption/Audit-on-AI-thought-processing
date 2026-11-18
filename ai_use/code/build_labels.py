"""Turn Claude's manual labels (labels.txt) into ai_use/qwen3.8-27b/2026-11-18-shard6-claude.jsonl.

Usage (repo root, stdlib only):
  python -I ai_use/code/select_traces.py . <scratch_dir>          # writes <scratch_dir>/selected.jsonl + reading views
  python -I ai_use/code/build_labels.py . <scratch_dir>/selected.jsonl

labels.txt rows are index|level|restate_only|answer_mentions_hint|note, where index is the position in
selected.jsonl (sorted by lang, qid, condition_id). Prints level counts and, where labels/gpt-oss-120b/
already has a current judge label for a trace, the agreement with it. Nothing outside ai_use/ is written.
"""
import collections, json, sys
from pathlib import Path

root, selected = Path(sys.argv[1]), Path(sys.argv[2])
here = root / "ai_use"
rows = [json.loads(ln) for ln in selected.read_text(encoding="utf-8").splitlines() if ln.strip()]

labels = {}
for ln in (here / "code" / "labels.txt").read_text(encoding="utf-8").splitlines():
    if not ln.strip() or ln.startswith("#"):
        continue
    idx, level, restate, ans, note = ln.split("|", 4)
    labels[int(idx)] = (int(level), restate == "yes", ans == "yes", note.strip())
assert sorted(labels) == list(range(len(rows))), (len(labels), len(rows))

out_path = here / "qwen3.8-27b" / "2026-11-18-shard6-claude.jsonl"
out_path.parent.mkdir(parents=True, exist_ok=True)
recs = []
for i, r in enumerate(rows):
    level, restate, ans, note = labels[i]
    recs.append({
        "judge": "claude-manual",
        "judge_model_id": "claude (manual reading against docs/scoring_guide.md)",
        "trace_run_id": r["run_id"], "trace_prompt_sha256": r["prompt_sha256"], "model": r["model"],
        "qid": r["qid"], "lang": r["lang"], "hint_type": r["hint_type"], "hint_lang": r["hint_lang"],
        "hinted": r["hinted"], "gold": r["gold"], "influenced": True, "level": level,
        "restate_only": restate, "answer_mentions_hint": ans,
        "flags": ["unsure"] if note.startswith("unsure") else [], "notes": note,
    })
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    for rec in recs:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

lv = collections.Counter(r["level"] for r in recs)
print(f"traces {len(recs)}  L0 {lv[0]}  L1 {lv[1]}  L2 {lv[2]}  unsure {sum(bool(r['flags']) for r in recs)}  "
      f"restate_only {sum(r['restate_only'] for r in recs)}  answer_mentions {sum(r['answer_mentions_hint'] for r in recs)}")

# Agreement with current gpt-oss-120b judge labels (same trace and prompt hash), read-only.
judge = collections.defaultdict(list)
for p in sorted((root / "labels" / "gpt-oss-120b").glob("20*.jsonl")):
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            d = json.loads(ln)
            judge[d.get("trace_run_id")].append((p.name, d))
pairs, multi, diffs = [], 0, []
for rec in recs:
    cands = [d for _, d in judge.get(rec["trace_run_id"], [])
             if d.get("trace_prompt_sha256") == rec["trace_prompt_sha256"] and d.get("level") in (0, 1, 2)]
    if not cands:
        continue
    multi += len(cands) > 1
    j = cands[-1]["level"]                     # last current label for the trace
    pairs.append((rec["level"], j))
    if j != rec["level"]:
        diffs.append((rec["trace_run_id"], rec["lang"], rec["hint_type"], rec["level"], j))
same = sum(a == b for a, b in pairs)
print(f"judge-labelled {len(pairs)} (traces with >1 current label: {multi}); same level {same} of {len(pairs)}")
conf = collections.Counter(pairs)
print("confusion (claude, judge): " + ", ".join(f"{k}:{v}" for k, v in sorted(conf.items())))
for d in diffs:
    print("differs:", *d)
