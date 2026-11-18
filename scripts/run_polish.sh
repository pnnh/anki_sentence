#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
mkdir -p logs reports

echo "===== $(date '+%F %T') WAIT FOR GENERATION PIPELINE ====="
while pgrep -f "run_overnight.sh" >/dev/null; do sleep 60; done

echo "===== $(date '+%F %T') POLISH WITH 14B ====="
.venv/bin/python scripts/polish.py --batch 10 --pause 1 2>&1 | tee logs/polish.log

echo "===== $(date '+%F %T') QC POLISHED ====="
.venv/bin/python scripts/qc.py --data-dir data/sentences_polished --report-dir reports --check-target 2>&1 | tee logs/qc_polished.log
.venv/bin/python scripts/review_report.py --data-dir data/sentences_polished --qc-report reports/qc_report.json --out reports/review_polished.html 2>&1 | tee -a logs/qc_polished.log

echo "===== $(date '+%F %T') POLISH SUMMARY ====="
.venv/bin/python - <<'PY'
import glob, json, random
from collections import Counter

patches = [json.loads(line) for p in glob.glob("data/patches/*.jsonl") for line in open(p) if line.strip()]
changed = [p for p in patches if p.get("changed")]
per_scene = Counter(p["scene"] for p in changed)
lines = [
    "# Polish summary",
    "",
    f"- Cards processed: {len(patches)}",
    f"- Changed: {len(changed)}",
    "",
    "## Changed per scene",
    "",
]
lines += [f"- {k}: {v}" for k, v in sorted(per_scene.items())]
lines += ["", "## Sample changes", ""]
random.seed(3)
for p in random.sample(changed, min(50, len(changed))):
    lines += [f"- {p['zh']}", f"  - old: {p['old_en']}", f"  - new: {p['new_en']}"]
open("reports/polish_summary.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"wrote reports/polish_summary.md ({len(changed)} changed)")
PY
echo "===== $(date '+%F %T') POLISH DONE ====="
