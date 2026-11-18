#!/usr/bin/env python3
"""Generate Chinese -> English sentence cards with a local Ollama model."""

import argparse
import hashlib
import json
import random
import re
import sys
import time
import tomllib
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.toml"
BENCHMARK = ROOT / "data" / "benchmark.jsonl"
SYSTEM_PROMPT = ROOT / "prompts" / "system.txt"
USER_TEMPLATE = ROOT / "prompts" / "generate.txt"
PLANNED_TEMPLATE = ROOT / "prompts" / "generate_planned.txt"

ANGLES = [
    "ask for information",
    "ask for a recommendation",
    "ask to see or try something",
    "say something is too big, small, or expensive",
    "ask for an alternative",
    "ask about availability",
    "confirm a detail",
    "explain what you need",
    "respond to a suggestion",
    "refuse politely",
    "ask for help",
    "describe a problem",
    "compare two options",
    "ask about time",
    "ask about location",
    "thank and close the conversation",
]

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scene", required=True, help="scene id from config/scenes.toml")
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--micro", nargs="*", help="only these micro ids")
    p.add_argument("--max-micros", type=int, help="only the first N micros")
    p.add_argument("--per-micro", type=int, help="override target count per micro")
    p.add_argument("--target", type=int, help="override total target for the scene")
    p.add_argument("--per-call", type=int, default=8)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--pause", type=float, default=0, help="seconds to sleep between model calls")
    p.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    p.add_argument("--out-dir", default=str(ROOT / "data" / "sentences"))
    p.add_argument("--plans-dir", default=str(ROOT / "data" / "plans"))
    p.add_argument("--no-plan", action="store_true", help="ignore micro-situation plans")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def load_jsonl(path):
    if not Path(path).exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_scene(scene_id):
    with open(CONFIG, "rb") as f:
        scenes = tomllib.load(f)["scenes"]
    for scene in scenes:
        if scene["id"] == scene_id:
            return scene
    ids = ", ".join(s["id"] for s in scenes)
    raise SystemExit(f"Unknown scene id: {scene_id}\nAvailable: {ids}")


def load_examples(scene_id, micro_id):
    rows = load_jsonl(BENCHMARK)
    same_micro = [r for r in rows if r["scene"] == scene_id and r["micro"] == micro_id]
    same_scene = [r for r in rows if r["scene"] == scene_id and r["micro"] != micro_id]
    picked = same_micro[:3]
    picked += same_scene[: max(0, 3 - len(picked))]
    if not picked:
        picked = rows[:5]
    return "\n".join(f"- {r['zh']} / {r['en']}" for r in picked)


def load_plan(scene_id, plans_dir):
    path = Path(plans_dir) / f"{scene_id}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("micros", {})


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def word_count(text):
    return len(WORD_RE.findall(text))


def has_cjk(text):
    return bool(CJK_RE.search(text))


def choose_angles(offset):
    picked = [ANGLES[(offset + i) % len(ANGLES)] for i in range(4)]
    return ", ".join(picked)


def build_messages(scene, micro, count, angle_text, avoid, examples, subs=None, round_note=""):
    if subs:
        template = PLANNED_TEMPLATE.read_text(encoding="utf-8")
        sub_block = "\n".join(f"{i}. {s}" for i, s in enumerate(subs, 1))
    else:
        template = USER_TEMPLATE.read_text(encoding="utf-8")
        sub_block = ""
    avoid_block = "\n".join(f"- {a}" for a in avoid[-10:]) if avoid else "None yet."
    user = template
    replacements = {
        "$scene_zh": scene["zh"],
        "$scene_en": scene["en"],
        "$micro_zh": micro["zh"],
        "$angles": angle_text,
        "$count": str(count),
        "$subs": sub_block,
        "$round_note": round_note,
        "$avoid": avoid_block,
        "$examples": examples,
    }
    for key, value in replacements.items():
        user = user.replace(key, value)
    return [
        {"role": "system", "content": SYSTEM_PROMPT.read_text(encoding="utf-8").strip()},
        {"role": "user", "content": user},
    ]


def extract_pairs(content):
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            start, end = text.find("["), text.rfind("]")
        if start == -1 or end <= start:
            raise
        data = json.loads(text[start : end + 1])
    if isinstance(data, dict):
        data = data.get("pairs") or data.get("sentences") or []
    if not isinstance(data, list):
        raise ValueError("JSON root is not a list of pairs")
    return data


def call_ollama(args, messages, count, seed):
    payload = {
        "model": args.model,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_predict": max(300, count * 90 + 200),
            "seed": seed,
        },
    }
    req = request.Request(
        args.ollama_url.rstrip("/") + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=args.timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("message", {}).get("content", "")


def clean_pair(raw):
    if not isinstance(raw, dict):
        return None
    zh = raw.get("zh") or raw.get("chinese") or raw.get("cn")
    en = raw.get("en") or raw.get("english")
    sub = raw.get("sub") or raw.get("situation") or ""
    if not isinstance(zh, str) or not isinstance(en, str):
        return None
    zh = zh.strip().strip("\"'")
    en = en.strip().strip("\"'")
    zh = re.sub(r"\s+", "", zh)
    en = re.sub(r"\s+", " ", en)
    for full, half in (("？", "?"), ("！", "!"), ("。", "."), ("，", ","), ("；", ";"), ("：", ":")):
        en = en.replace(full, half)
    if en and en[-1] not in ".?!":
        en += "."
    if en:
        en = en[0].upper() + en[1:]
    sub = re.sub(r"^\s*\d+\s*[.、)）]\s*", "", str(sub)).strip()
    return zh, en, sub


def validate_pair(zh, en):
    if not zh or not en:
        return "empty"
    if not has_cjk(zh):
        return "zh_missing_chinese"
    if len(zh) > 45:
        return "zh_too_long"
    if has_cjk(en):
        return "en_contains_chinese"
    n = word_count(en)
    if n < 4 or n > 16:
        return f"en_word_count_{n}"
    return None


def make_uid(scene_id, zh):
    digest = hashlib.sha1(normalize(zh).encode("utf-8")).hexdigest()[:10]
    return f"{scene_id}-{digest}"


def is_near_dup(zh, en, seen_zh, seen_en, records, other_zh=frozenset(), other_en=frozenset()):
    nz, ne = normalize(zh), normalize(en)
    if nz in seen_zh or ne in seen_en or nz in other_zh or ne in other_en:
        return True
    for r in records:
        if SequenceMatcher(None, nz, normalize(r["zh"])).ratio() >= 0.9:
            return True
        if SequenceMatcher(None, ne, normalize(r["en"])).ratio() >= 0.9:
            return True
    return False


def split_counts(micros, total):
    base, extra = divmod(total, len(micros))
    return {m["id"]: base + (1 if i < extra else 0) for i, m in enumerate(micros)}


def main():
    args = parse_args()
    scene = load_scene(args.scene)
    plans = {} if args.no_plan else load_plan(scene["id"], args.plans_dir)

    micros = scene["micros"]
    if args.micro:
        wanted = set(args.micro)
        micros = [m for m in micros if m["id"] in wanted]
        if not micros:
            raise SystemExit("No matching micro ids")
    if args.max_micros:
        micros = micros[: args.max_micros]

    total = args.target or scene["target"]
    if args.per_micro:
        desired = {m["id"]: args.per_micro for m in micros}
    else:
        desired = split_counts(micros, total)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{scene['id']}.jsonl"
    records = load_jsonl(out_path)
    seen_zh = {normalize(r["zh"]) for r in records}
    seen_en = {normalize(r["en"]) for r in records}
    other_zh, other_en = set(), set()
    for p in out_dir.glob("*.jsonl"):
        if p.name == out_path.name:
            continue
        for r in load_jsonl(p):
            other_zh.add(normalize(r["zh"]))
            other_en.add(normalize(r["en"]))
    have = {}
    for r in records:
        have[r["micro"]] = have.get(r["micro"], 0) + 1

    print(f"Scene: {scene['zh']} ({scene['id']}) | model: {args.model}")
    print(f"Output: {out_path}")
    for m in micros:
        plan_n = len(plans.get(m["id"], []))
        plan_info = f" | plan {plan_n}" if plan_n else " | no plan"
        print(
            f"  {m['id']:<22} need {max(0, desired[m['id']] - have.get(m['id'], 0)):>3} / "
            f"{desired[m['id']]}{plan_info}"
        )
    if args.dry_run:
        return

    rejected = {}
    generated = 0
    for m in micros:
        need = max(0, desired[m["id"]] - have.get(m["id"], 0))
        if need == 0:
            continue
        attempts = 0
        max_attempts = (need + args.per_call - 1) // args.per_call + args.retries + 2
        while need > 0 and attempts < max_attempts:
            attempts += 1
            batch = min(args.per_call, need)
            angle_text = choose_angles(len(records) + attempts)
            avoid = [f"{r['zh']} / {r['en']}" for r in records if r["micro"] == m["id"]]
            examples = load_examples(scene["id"], m["id"])
            micro_plan = plans.get(m["id"], [])
            if micro_plan:
                covered = {
                    r.get("sub") for r in records if r["micro"] == m["id"] and r.get("sub")
                }
                if attempts == 1:
                    batch_subs = micro_plan[:batch]
                else:
                    uncovered = [s for s in micro_plan if s not in covered]
                    if uncovered:
                        batch_subs = uncovered[:batch]
                    else:
                        start = ((attempts - 1) * args.per_call) % len(micro_plan)
                        batch_subs = [
                            micro_plan[(start + i) % len(micro_plan)]
                            for i in range(min(batch, len(micro_plan)))
                        ]
                batch = len(batch_subs)
                if attempts == 1:
                    round_note = "This is round 1. Write one fresh sentence for each sub-situation."
                else:
                    round_note = (
                        f"This is round {attempts}. Write a new and different sentence for each "
                        "sub-situation. Use a different sentence pattern and angle from earlier rounds."
                    )
            else:
                batch_subs = None
                round_note = ""
            messages = build_messages(
                scene, m, batch, angle_text, avoid, examples, subs=batch_subs, round_note=round_note
            )
            seed = random.randint(0, 2**31 - 1)
            try:
                content = call_ollama(args, messages, batch, seed)
                pairs = extract_pairs(content)
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"    retry {m['id']}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
                continue

            accepted = 0
            for raw in pairs:
                cleaned = clean_pair(raw)
                if not cleaned:
                    rejected["malformed"] = rejected.get("malformed", 0) + 1
                    continue
                zh, en, sub = cleaned
                reason = validate_pair(zh, en)
                if reason:
                    rejected[reason] = rejected.get(reason, 0) + 1
                    continue
                if is_near_dup(zh, en, seen_zh, seen_en, records, other_zh, other_en):
                    rejected["duplicate"] = rejected.get("duplicate", 0) + 1
                    continue
                uid = make_uid(scene["id"], zh)
                if any(r["uid"] == uid for r in records):
                    rejected["duplicate"] = rejected.get("duplicate", 0) + 1
                    continue
                record = {
                    "uid": uid,
                    "scene": scene["id"],
                    "scene_zh": scene["zh"],
                    "scene_en": scene["en"],
                    "group": scene["group"],
                    "phase": scene["phase"],
                    "micro": m["id"],
                    "micro_zh": m["zh"],
                    "zh": zh,
                    "en": en,
                    "sub": sub,
                    "angle": angle_text,
                    "model": args.model,
                    "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                records.append(record)
                seen_zh.add(normalize(zh))
                seen_en.add(normalize(en))
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                accepted += 1
                generated += 1
            need -= accepted
            print(
                f"  {m['id']:<22} +{accepted:<2} accepted | {max(0, need):>3} left | "
                f"total {len(records)}",
                flush=True,
            )
            if accepted == 0:
                time.sleep(1)
            if args.pause:
                time.sleep(args.pause)
        if need > 0:
            print(f"  WARNING: {m['id']} still needs {need} sentences", file=sys.stderr)

    print(f"Done. Added {generated} sentences, scene total {len(records)}.")
    if rejected:
        print("Rejected:", ", ".join(f"{k}={v}" for k, v in sorted(rejected.items())))


if __name__ == "__main__":
    main()
