#!/usr/bin/env python3
"""Report question ratio, sentence-type mix, structure counts, and vocabulary bands."""

import argparse
import json
import re
import tomllib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.toml"

WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")
NEG_RE = re.compile(r"\b(?:not|never|no|nothing|nobody)\b|\w+n't\b", re.I)

IMPERATIVE_VERBS = set(
    "add ask avoid be book bring buy call cancel change check choose clean close come confirm "
    "consider contact cut decide do don't drink drive eat empty enter explain fill find finish "
    "follow get give go grab hand hang have help hold hurry keep leave let listen look make "
    "meet move open order pack pay pick place please prepare put read remember rent repeat "
    "reply reserve return run save say see send set show sit speak spend stand start stay stop "
    "take talk tell think try turn use wait wake walk want wash watch wear work write".split()
)

STRUCTURES = {
    "there is/are": re.compile(r"\bthere(?:'s| is| are| was| were)\b", re.I),
    "I'd like / I want": re.compile(r"\b(?:i'd like|i would like|i want)\b", re.I),
    "can/could I": re.compile(r"\b(?:can|could|may) i\b", re.I),
    "could/would you": re.compile(r"\b(?:could|would|can) you\b", re.I),
    "have to / need to": re.compile(r"\b(?:have|has|had|need|needs|needed) to\b", re.I),
    "going to": re.compile(r"\b(?:am|is|are|was|were) going to\b", re.I),
    "used to": re.compile(r"\bused to\b", re.I),
    "present perfect": re.compile(r"\b(?:have|has) (?:[a-z]+ed|been|gone|done|seen|had|made|taken|got|gotten|bought|found|told|thought|knew|known)\b", re.I),
    "if-clause": re.compile(r"\bif\b", re.I),
    "should": re.compile(r"\bshould(?:n't)?\b", re.I),
    "let's / let me": re.compile(r"\blet(?:'s| me| us)\b", re.I),
}

try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", action="append", help="repeatable; defaults to base + packs")
    p.add_argument("--report-dir", default=str(ROOT / "reports"))
    p.add_argument("--gate-group", action="append", default=[], help="group whose question ratio is gated")
    p.add_argument("--max-question-ratio", type=float, default=0.4)
    p.add_argument("--fail-on-gate", action="store_true")
    return p.parse_args()


def load_scenes():
    with open(CONFIG, "rb") as f:
        return tomllib.load(f)["scenes"]


def load_records(dirs):
    records = []
    for d in dirs:
        path = Path(d)
        if not path.exists():
            continue
        for f in sorted(path.glob("*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
    return records


def sentence_type(en):
    text = en.strip()
    if text.endswith("?"):
        return "question"
    words = [w.lower() for w in WORD_RE.findall(text)]
    words = [w for w in words if w not in {"please", "so", "and", "but", "oh", "well"}]
    if words and words[0] in IMPERATIVE_VERBS and not re.match(r"\b(?:i|you|he|she|it|we|they|this|that|these|those|my|your|our)\b", text, re.I):
        return "imperative"
    return "statement"


def vocab_band(word):
    if zipf_frequency is None:
        return "unknown"
    z = zipf_frequency(word.lower(), "en")
    if z >= 5.0:
        return "high"
    if z >= 4.0:
        return "mid"
    return "low"


def main():
    args = parse_args()
    dirs = args.data_dir or [str(ROOT / "data" / "sentences_polished"), str(ROOT / "data" / "packs" / "final")]
    scenes = {s["id"]: s for s in load_scenes()}
    records = load_records(dirs)

    by_group = defaultdict(list)
    for rec in records:
        scene = scenes.get(rec.get("scene"), {})
        by_group[scene.get("group", "未分组")].append(rec)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "records": len(records),
        "groups": {},
        "overall": {},
    }

    def summarize(recs):
        types = Counter(sentence_type(r["en"]) for r in recs)
        tokens = [w.lower() for r in recs for w in WORD_RE.findall(r["en"])]
        bands = Counter(vocab_band(w) for w in tokens)
        low_words = Counter(w for w in tokens if vocab_band(w) == "low")
        structures = {
            name: sum(1 for r in recs if rx.search(r["en"])) for name, rx in STRUCTURES.items()
        }
        negations = sum(1 for r in recs if NEG_RE.search(r["en"]))
        total = len(recs) or 1
        return {
            "cards": len(recs),
            "question_ratio": round(types["question"] / total, 3),
            "types": dict(types),
            "negation_ratio": round(negations / total, 3),
            "avg_words": round(sum(len(WORD_RE.findall(r["en"])) for r in recs) / total, 1),
            "vocab_share": {k: round(v / (len(tokens) or 1), 3) for k, v in sorted(bands.items())},
            "low_vocab_words": [w for w, _ in low_words.most_common(15)],
            "structures": structures,
        }

    for group, recs in sorted(by_group.items()):
        report["groups"][group] = summarize(recs)
    report["overall"] = summarize(records)

    out_dir = Path(args.report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [f"# Coverage ({report['records']} cards)", ""]
    lines.append("| 分组 | 卡片 | 问句占比 | 问句 | 祈使句 | 陈述句 | 否定占比 | 平均词数 | 高频词≥5.0 | 低频词<4.0 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for group, s in report["groups"].items():
        types = s["types"]
        share = s["vocab_share"]
        lines.append(
            f"| {group} | {s['cards']} | {s['question_ratio']:.0%} | {types.get('question', 0)} | "
            f"{types.get('imperative', 0)} | {types.get('statement', 0)} | {s['negation_ratio']:.0%} | "
            f"{s['avg_words']} | {share.get('high', 0):.0%} | {share.get('low', 0):.0%} |"
        )
    o = report["overall"]
    lines.append(
        f"| **合计** | {o['cards']} | {o['question_ratio']:.0%} | {o['types'].get('question', 0)} | "
        f"{o['types'].get('imperative', 0)} | {o['types'].get('statement', 0)} | {o['negation_ratio']:.0%} | "
        f"{o['avg_words']} | {o['vocab_share'].get('high', 0):.0%} | {o['vocab_share'].get('low', 0):.0%} |"
    )
    lines += ["", "## 结构计数（全库）", ""]
    for name, count in sorted(o["structures"].items(), key=lambda kv: -kv[1]):
        lines.append(f"- {name}: {count}")
    lines += ["", "## 低频词（<4.0，出现最多）", "", ", ".join(o["low_vocab_words"]) or "-"]
    (out_dir / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines[: len(report["groups"]) + 5]))
    print(f"Report: {out_dir / 'coverage.md'}")

    if args.gate_group:
        failed = []
        for group in args.gate_group:
            s = report["groups"].get(group)
            if s is None:
                print(f"gate: group '{group}' not found", file=__import__("sys").stderr)
                failed.append(group)
            elif s["question_ratio"] > args.max_question_ratio:
                print(
                    f"gate: {group} question ratio {s['question_ratio']:.0%} > "
                    f"{args.max_question_ratio:.0%}",
                    file=__import__("sys").stderr,
                )
                failed.append(group)
        if failed and args.fail_on_gate:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
