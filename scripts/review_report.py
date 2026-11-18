#!/usr/bin/env python3
"""Build a static HTML review sheet from generated sentence cards."""

import argparse
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px 28px 64px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
  background: #f5f5f2; color: #1f2328;
}
h1 { font-size: 22px; margin: 0 0 6px; }
.sub { color: #667085; font-size: 13px; margin-bottom: 18px; }
.controls {
  position: sticky; top: 0; z-index: 5; display: flex; flex-wrap: wrap; gap: 10px;
  align-items: center; padding: 12px 14px; margin-bottom: 18px;
  background: rgba(245,245,242,.94); border: 1px solid #ddddd6; border-radius: 10px;
  backdrop-filter: blur(8px);
}
select, input[type=search] {
  font: inherit; font-size: 14px; padding: 7px 10px; border: 1px solid #cfcfc7;
  border-radius: 7px; background: #fff; color: inherit;
}
input[type=search] { width: 260px; }
label.check { display: flex; gap: 6px; align-items: center; font-size: 14px; }
.stats { margin-left: auto; font-size: 13px; color: #667085; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 14px; }
.card {
  background: #fff; border: 1px solid #e2e2da; border-radius: 12px; padding: 16px 18px;
  box-shadow: 0 1px 2px rgba(20,20,10,.04);
}
.card.has-issue { border-color: #e3b341; box-shadow: 0 0 0 1px #f2d58a inset; }
.scene { font-size: 12px; color: #8a8f98; margin-bottom: 8px; letter-spacing: .02em; }
.zh { font-size: 20px; line-height: 1.55; }
.en { font-size: 19px; line-height: 1.55; color: #0b5cad; margin-top: 10px; }
.meta { margin-top: 12px; font-size: 11px; color: #9aa0a8; word-break: break-all; }
.badges { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.badge {
  font-size: 11px; padding: 2px 7px; border-radius: 999px;
  background: #fff4d6; color: #7a5300; border: 1px solid #f0d48f;
}
.badge.err { background: #ffe8e6; color: #9b1c1c; border-color: #f3b4ae; }
.hidden { display: none; }
.empty { color: #667085; padding: 30px; text-align: center; }
"""

SCRIPT = """
const cards = Array.from(document.querySelectorAll('.card'));
const scene = document.getElementById('scene');
const search = document.getElementById('search');
const onlyIssues = document.getElementById('onlyIssues');
const shown = document.getElementById('shown');
function apply() {
  const q = search.value.trim().toLowerCase();
  const s = scene.value;
  let n = 0;
  for (const card of cards) {
    const okScene = !s || card.dataset.scene === s;
    const okIssue = !onlyIssues.checked || card.dataset.issue === '1';
    const okSearch = !q || card.dataset.search.includes(q);
    const ok = okScene && okIssue && okSearch;
    card.classList.toggle('hidden', !ok);
    if (ok) n++;
  }
  shown.textContent = n;
}
scene.addEventListener('change', apply);
search.addEventListener('input', apply);
onlyIssues.addEventListener('change', apply);
apply();
"""


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences"))
    p.add_argument("--qc-report", default=str(ROOT / "reports" / "qc_report.json"))
    p.add_argument("--out", default=str(ROOT / "reports" / "review.html"))
    return p.parse_args()


def load_records(data_dir):
    records = []
    for path in sorted(Path(data_dir).glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def main():
    args = parse_args()
    records = load_records(args.data_dir)
    records.sort(key=lambda r: (r["scene"], r["micro"], r["uid"]))

    issues_by_uid = {}
    qc_path = Path(args.qc_report)
    if qc_path.exists():
        report = json.loads(qc_path.read_text(encoding="utf-8"))
        for issue in report.get("issues", []):
            if issue["level"] in {"error", "warn"}:
                issues_by_uid.setdefault(issue["uid"], []).append(issue)

    scene_names = {}
    scene_counts = Counter()
    for rec in records:
        scene_names[rec["scene"]] = rec["scene_zh"]
        scene_counts[rec["scene"]] += 1

    options = "".join(
        f'<option value="{html.escape(k)}">{html.escape(v)} ({scene_counts[k]})</option>'
        for k, v in sorted(scene_names.items())
    )
    flagged = sum(1 for r in records if issues_by_uid.get(r["uid"]))

    cards = []
    for rec in records:
        issues = issues_by_uid.get(rec["uid"], [])
        badges = "".join(
            f'<span class="badge{" err" if i["level"] == "error" else ""}">'
            f'{html.escape(i["type"])}: {html.escape(str(i["detail"]))}</span>'
            for i in issues
        )
        search_blob = " ".join(
            [rec.get("zh", ""), rec.get("en", ""), rec.get("uid", ""), rec.get("micro_zh", "")]
        ).lower()
        cards.append(
            f'<article class="card{" has-issue" if issues else ""}" '
            f'data-scene="{html.escape(rec["scene"])}" '
            f'data-issue="{1 if issues else 0}" '
            f'data-search="{html.escape(search_blob)}">'
            f'<div class="scene">[{html.escape(rec["scene_zh"])}] · '
            f'{html.escape(rec.get("micro_zh", rec["micro"]))}</div>'
            f'<div class="zh">{html.escape(rec["zh"])}</div>'
            f'<div class="en">{html.escape(rec["en"])}</div>'
            f'<div class="badges">{badges}</div>'
            f'<div class="meta">{html.escape(rec["uid"])} · {html.escape(rec.get("model", ""))}</div>'
            f"</article>"
        )

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>句子卡审阅</title>
<style>{CSS}</style>
</head>
<body>
<h1>句子卡审阅</h1>
<div class="sub">共 {len(records)} 张卡 · {len(scene_names)} 个场景 · 有标记 {flagged} 张</div>
<div class="controls">
  <select id="scene"><option value="">全部场景</option>{options}</select>
  <input id="search" type="search" placeholder="搜索中文、英文、微场景或 uid">
  <label class="check"><input id="onlyIssues" type="checkbox"> 只看有标记的</label>
  <div class="stats">显示 <span id="shown">{len(records)}</span> / {len(records)}</div>
</div>
<div class="grid">
{''.join(cards) if cards else '<div class="empty">没有数据</div>'}
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"Wrote {out} ({len(records)} cards, {flagged} flagged)")


if __name__ == "__main__":
    main()
