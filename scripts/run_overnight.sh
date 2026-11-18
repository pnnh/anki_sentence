#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
mkdir -p logs reports

echo "===== $(date '+%F %T') WAIT FOR CORE GENERATION ====="
while pgrep -f "run_generate_core.sh" >/dev/null; do sleep 60; done

echo "===== $(date '+%F %T') QC CORE ====="
.venv/bin/python scripts/qc.py --check-target 2>&1 | tee logs/qc_core.log
.venv/bin/python scripts/review_report.py 2>&1 | tee -a logs/qc_core.log

.venv/bin/python - <<'PY'
import json, sys
score = json.load(open("reports/qc_report.json"))["score"]
print(f"gate: errors={score['errors']} parse_errors={score['parse_errors']} warnings={score['warnings']}")
sys.exit(0 if score["errors"] == 0 and score["parse_errors"] == 0 else 1)
PY
if [ $? -ne 0 ]; then
  echo "===== $(date '+%F %T') GATE FAILED, STOPPING ====="
  exit 2
fi

echo "===== $(date '+%F %T') GENERATE REMAINING SCENES ====="
bash scripts/run_generate_remaining.sh 2>&1 | tee -a logs/generate_remaining.log

echo "===== $(date '+%F %T') QC ALL SCENES ====="
.venv/bin/python scripts/qc.py --check-target 2>&1 | tee logs/qc_all.log
.venv/bin/python scripts/review_report.py 2>&1 | tee -a logs/qc_all.log
echo "===== $(date '+%F %T') OVERNIGHT DONE ====="
