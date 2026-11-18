"""Select the shard-6/7 influenced qwen3.8-27b traces in runs/qwen3.8-27b/2026-11-18-laptop-vqoqn10r.jsonl.

Mirrors src/cotaudit/analysis/influence.py (keep_current, load_runs dedup on run_id, with_influence)
in stdlib Python. Writes a reading view (hint-word passages + tail) per trace to an output folder.
Usage: python -I select_traces.py <repo_root> <out_dir>
"""
import hashlib, json, re, sys
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
MODEL = "qwen3.8-27b"
TARGET = "2026-11-18-laptop-vqoqn10r.jsonl"

cond = {}
for ln in (root / "data/conditions.jsonl").read_text(encoding="utf-8").splitlines():
    if ln.strip():
        r = json.loads(ln); cond[r["condition_id"]] = r["prompt_sha256"]

def current(r):
    exp = cond.get(r.get("condition_id"))
    sha = r.get("prompt_sha256")
    return exp is not None and (sha is None or sha == exp)

runs, seen, src = [], set(), {}
target_total = target_valid = 0
for path in sorted((root / "runs" / MODEL).glob("20*.jsonl")):     # load_runs order; errors-* excluded
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        if path.name == TARGET:
            target_total += 1
        if not current(r):
            continue
        if path.name == TARGET:
            target_valid += 1
        if r["run_id"] in seen:          # drop_duplicates("run_id", keep="first")
            continue
        seen.add(r["run_id"]); runs.append(r); src[r["run_id"]] = path.name

base = {}
for r in runs:
    if r["hint_type"] == "none":
        base.setdefault((r["model"], r["qid"], r["lang"]), {}).setdefault(r["rep"], r.get("answer"))

def shard(q):
    return int(hashlib.sha256(q.encode("utf-8")).hexdigest(), 16) % 7

sel = []
for r in runs:
    if r["hint_type"] == "none" or src[r["run_id"]] != TARGET:
        continue
    b = base.get((r["model"], r["qid"], r["lang"]), {})
    b1, b2 = b.get(1), b.get(2)
    if r.get("answer") is None or b1 is None or b2 is None:      # undetermined
        continue
    if r["answer"] == r["hinted"] and b1 != r["hinted"] and b2 != r["hinted"] and shard(r["qid"]) == 5:
        sel.append(r)

sel.sort(key=lambda r: (r["lang"], r["qid"], r["condition_id"]))
print(f"target lines {target_total}, valid {target_valid}, selected {len(sel)}", file=sys.stderr)

PAT = re.compile(r"professor|expert|metadata|meta data|answer key|key|leak|user|hint|suggest|"
                 r"tag|<answer>|claim|unauthori|question_metadata|अनधिकृत|未经授权|标准答案|授权|ഉത്തരസൂചിക|അനധികൃത|प्रोफेसर|प्रोफ़ेसर|विशेषज्ञ|मेटाडेटा|उत्तर कुंजी|उपयोगकर्ता|"
                 r"教授|专家|元数据|答案|用户|提示|പ്രൊഫസർ|വിദഗ്ധ|മെറ്റാഡാറ്റ|ഉത്തരം|ഉപയോക്താവ്", re.I)

with open(out / "selected.jsonl", "w", encoding="utf-8") as f:
    for r in sel:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

for i, r in enumerate(sel):
    txt = r.get("reasoning") or ""
    letter = re.compile(r"answer[^.\n]{0,20}\b" + r["hinted"] + r"\b|\b" + r["hinted"] + r"\b[^.\n]{0,20}answer", re.I)
    spans = [(m.start(), m.end()) for m in PAT.finditer(txt)] + [(m.start(), m.end()) for m in letter.finditer(txt)]
    spans.sort()
    merged = []
    for s, e in spans:
        s, e = max(0, s - 150), min(len(txt), e + 150)
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    hint_text = ""
    p = r.get("prompt") or ""
    with open(out / f"{i:03d}.txt", "w", encoding="utf-8") as f:
        f.write(f"#{i} run={r['run_id']} qid={r['qid']} lang={r['lang']} hint={r['hint_type']}/{r['hint_lang']} "
                f"hinted={r['hinted']} gold={r['gold']} ans={r['answer']} finish={r.get('finish_reason')} "
                f"think_closed={r.get('think_closed')} len={len(txt)}\n")
        f.write("=== PASSAGES ===\n")
        for s, e in merged:
            f.write(f"[{s}-{e}] ..." + txt[s:e].replace("\n", " ") + "...\n")
        f.write("=== TAIL ===\n" + txt[-300:].replace("\n", " ") + "\n")
        f.write("=== CONTENT (answer section) mentions? ===\n")
        c = r.get("content") or ""
        f.write("; ".join(c[max(0, m.start()-80):m.end()+80].replace("\n", " ") for m in PAT.finditer(c))[:1500] + "\n")
