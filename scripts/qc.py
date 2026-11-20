#!/usr/bin/env python3
"""Validate generated sentence cards and write a QC report."""

import argparse
import json
import re
import sys
import tomllib
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.toml"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z']*")

STOPWORDS = set(
    "the a an and or but if to of in on at for with from by is are was were be been am "
    "i you he she it we they my your his her our their this that these those there here "
    "what where when who how why can could would should will shall may might must do does "
    "did have has had not no yes please thanks thank hello hi okay ok".split()
)

FORMAL_WORDS = {
    "commence", "utilize", "utilise", "inquire", "purchase", "assistance", "regarding",
    "nevertheless", "furthermore", "consequently", "approximately", "sufficient",
    "obtain", "require", "ensure", "assist", "reside", "vehicle", "prior", "subsequently",
}

BRANDS = {
    "alipay", "wechat", "weixin", "didi", "taobao", "tmall", "starbucks", "mcdonald's",
    "mcdonalds", "kfc", "uber", "airbnb", "google", "apple", "iphone", "facebook",
    "instagram", "whatsapp", "netflix", "amazon",
}

try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences"))
    p.add_argument("--report-dir", default=str(ROOT / "reports"))
    p.add_argument("--near-dup-threshold", type=float, default=0.92)
    p.add_argument("--check-target", action="store_true")
    p.add_argument("--fail-on-error", action="store_true")
    return p.parse_args()


def load_scenes():
    with open(CONFIG, "rb") as f:
        return tomllib.load(f)["scenes"]


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def cjk_len(text):
    return len(CJK_RE.findall(text))


def add_issue(issues, level, kind, record, detail):
    issues.append(
        {
            "level": level,
            "type": kind,
            "uid": record.get("uid"),
            "scene": record.get("scene"),
            "micro": record.get("micro"),
            "zh": record.get("zh"),
            "en": record.get("en"),
            "detail": detail,
        }
    )


def check_proper_nouns(en):
    hits = []
    for match in TOKEN_RE.finditer(en):
        token = match.group(0)
        before = en[: match.start()].rstrip()
        at_start = not before or before[-1] in ".?!:"
        if at_start:
            continue
        if token in {
            "I", "I'm", "I'd", "I'll", "I've", "Mr", "Mrs", "Ms", "Dr",
            "S", "M", "L", "XL", "XXL", "OK", "App", "SIM", "ATM", "ID", "PIN", "Wi", "Fi",
            "AM", "PM", "RMB",
        }:
            continue
        if token[0].isupper():
            hits.append(token)
    return hits


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    scenes = load_scenes()
    scene_by_id = {s["id"]: s for s in scenes}
    micro_by_scene = {s["id"]: {m["id"]: m for m in s["micros"]} for s in scenes}

    records = []
    parse_errors = []
    for path in sorted(data_dir.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    parse_errors.append({"file": path.name, "line": lineno, "error": str(exc)})

    issues = []
    seen_uid = {}
    seen_zh = defaultdict(list)
    seen_en = defaultdict(list)
    counts = Counter()
    micro_counts = Counter()

    for rec in records:
        missing = [k for k in ("uid", "scene", "micro", "zh", "en") if not rec.get(k)]
        if missing:
            add_issue(issues, "error", "missing_fields", rec, ",".join(missing))
            continue

        scene = scene_by_id.get(rec["scene"])
        if not scene:
            add_issue(issues, "error", "unknown_scene", rec, rec["scene"])
        elif rec["micro"] not in micro_by_scene[rec["scene"]]:
            add_issue(issues, "error", "unknown_micro", rec, rec["micro"])

        if rec["uid"] in seen_uid:
            add_issue(issues, "error", "duplicate_uid", rec, f"also used by {seen_uid[rec['uid']]}")
        seen_uid[rec["uid"]] = rec["uid"]

        zh, en = rec["zh"], rec["en"]
        if not CJK_RE.search(zh):
            add_issue(issues, "error", "zh_missing_chinese", rec, zh)
        if CJK_RE.search(en):
            add_issue(issues, "error", "en_contains_chinese", rec, en)
        if cjk_len(zh) < 4:
            add_issue(issues, "warn", "zh_too_short", rec, str(cjk_len(zh)))
        group = scene.get("group") if scene else ""
        if cjk_len(zh) > (100 if group == "多轮对话" else 45):
            add_issue(issues, "warn", "zh_too_long", rec, str(cjk_len(zh)))
        words = WORD_RE.findall(en)
        max_words = {
            "个人叙事": 24, "语法句型": 18, "短语动词": 18, "口语衔接": 20,
            "功能语言": 20, "搭配词族": 18, "语法进阶": 18, "易混词族": 18,
            "角色反转": 20, "多轮对话": 70, "短语动词补全": 18, "高频补全": 16, "新生活场景": 20,
            "语域礼貌": 24, "语法补充": 18,
        }.get(group, 16)
        if len(words) < 4 or len(words) > max_words:
            add_issue(issues, "warn", "en_word_count", rec, str(len(words)))
        if en and en[-1] not in ".?!":
            add_issue(issues, "warn", "en_no_end_punctuation", rec, en[-1])

        proper = check_proper_nouns(en)
        if proper:
            add_issue(issues, "warn", "proper_noun", rec, ", ".join(proper))
        brands = sorted({w for w in words if w.lower().strip("'") in BRANDS})
        if brands:
            add_issue(issues, "warn", "brand_name", rec, ", ".join(brands))

        formal = sorted({w.lower() for w in words if w.lower() in FORMAL_WORDS})
        if formal and group != "语域礼貌":
            add_issue(issues, "warn", "formal_word", rec, ", ".join(formal))
        if zipf_frequency is not None:
            rare = sorted(
                {
                    w.lower()
                    for w in words
                    if len(w) >= 4
                    and w.lower() not in STOPWORDS
                    and zipf_frequency(w.lower(), "en") < 3.2
                }
            )
            if rare:
                add_issue(issues, "warn", "rare_word", rec, ", ".join(rare))

        seen_zh[normalize(zh)].append(rec)
        seen_en[normalize(en)].append(rec)
        counts[rec["scene"]] += 1
        micro_counts[(rec["scene"], rec["micro"])] += 1

    for norm, group in seen_zh.items():
        if norm and len(group) > 1:
            first = group[0]
            for rec in group[1:]:
                if rec["scene"] == first["scene"]:
                    add_issue(issues, "error", "duplicate_zh", rec, f"same as {first['uid']}")
                else:
                    add_issue(issues, "warn", "cross_scene_duplicate", rec, f"zh same as {first['uid']}")
    for norm, group in seen_en.items():
        if norm and len(group) > 1:
            first = group[0]
            for rec in group[1:]:
                if rec["scene"] == first["scene"]:
                    add_issue(issues, "error", "duplicate_en", rec, f"same as {first['uid']}")
                else:
                    add_issue(issues, "warn", "cross_scene_duplicate", rec, f"en same as {first['uid']}")

    for scene in scenes:
        group = [r for r in records if r.get("scene") == scene["id"]]
        compared = set()
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                key = tuple(sorted((a["uid"], b["uid"])))
                if key in compared:
                    continue
                compared.add(key)
                sim_zh = SequenceMatcher(None, normalize(a["zh"]), normalize(b["zh"])).ratio()
                sim_en = SequenceMatcher(None, normalize(a["en"]), normalize(b["en"])).ratio()
                if sim_zh >= args.near_dup_threshold or sim_en >= args.near_dup_threshold:
                    add_issue(
                        issues,
                        "warn",
                        "near_duplicate",
                        b,
                        f"similar to {a['uid']} (zh={sim_zh:.2f}, en={sim_en:.2f})",
                    )

    if args.check_target:
        for scene in scenes:
            if scene["id"] not in counts:
                continue
            have = counts.get(scene["id"], 0)
            if have < scene["target"]:
                issues.append(
                    {
                        "level": "warn",
                        "type": "target_not_reached",
                        "uid": None,
                        "scene": scene["id"],
                        "micro": None,
                        "zh": None,
                        "en": None,
                        "detail": f"{have}/{scene['target']}",
                    }
                )
            for micro in scene["micros"]:
                if micro_counts.get((scene["id"], micro["id"]), 0) == 0:
                    issues.append(
                        {
                            "level": "info",
                            "type": "empty_micro",
                            "uid": None,
                            "scene": scene["id"],
                            "micro": micro["id"],
                            "zh": None,
                            "en": None,
                            "detail": micro["zh"],
                        }
                    )

    errors = sum(1 for i in issues if i["level"] == "error")
    warnings = sum(1 for i in issues if i["level"] == "warn")
    by_type = Counter(i["type"] for i in issues)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "score": {
            "records": len(records),
            "scenes": len({r.get("scene") for r in records}),
            "errors": errors,
            "warnings": warnings,
            "parse_errors": len(parse_errors),
            "vocab_check": "wordfreq" if zipf_frequency else "heuristic",
        },
        "counts": dict(counts),
        "micro_counts": {f"{k[0]}/{k[1]}": v for k, v in sorted(micro_counts.items())},
        "issues_by_type": dict(by_type),
        "issues": issues,
        "parse_errors": parse_errors,
    }
    json_path = report_dir / "qc_report.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# QC Report", ""]
    lines.append(f"- Records: **{len(records)}**")
    lines.append(f"- Errors: **{errors}**")
    lines.append(f"- Warnings: **{warnings}**")
    lines.append(f"- Vocab check: **{report['score']['vocab_check']}**")
    if parse_errors:
        lines.append(f"- JSON parse errors: **{len(parse_errors)}**")
    lines.append("")
    lines.append("## By scene")
    lines.append("")
    lines.append("| Scene | Target | Count | Coverage | Errors | Warnings |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for scene in scenes:
        n = counts.get(scene["id"], 0)
        if n == 0:
            continue
        e = sum(1 for i in issues if i["scene"] == scene["id"] and i["level"] == "error")
        w = sum(1 for i in issues if i["scene"] == scene["id"] and i["level"] == "warn")
        lines.append(
            f"| {scene['zh']} | {scene['target']} | {n} | {n / scene['target']:.0%} | {e} | {w} |"
        )
    lines.append("")
    lines.append("## Issues by type")
    lines.append("")
    for kind, n in by_type.most_common():
        lines.append(f"- `{kind}`: {n}")
    lines.append("")
    flagged = [i for i in issues if i["level"] in {"error", "warn"}][:40]
    if flagged:
        lines.append("## First flagged items")
        lines.append("")
        for i in flagged:
            lines.append(f"- **{i['type']}** `{i['uid']}`: {i['zh']} / {i['en']} ({i['detail']})")
    md_path = report_dir / "qc_report.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Records: {len(records)} | errors: {errors} | warnings: {warnings}")
    print(f"Issues: {', '.join(f'{k}={v}' for k, v in by_type.most_common()) or 'none'}")
    print(f"Report: {md_path}")
    if args.fail_on_error and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
