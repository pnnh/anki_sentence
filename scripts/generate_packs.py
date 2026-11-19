#!/usr/bin/env python3
"""Generate the grammar/narrative packs: plan Chinese, translate, finalize.

Stages:
  --stage plan        write 20 Chinese seeds per pack scene (10 per micro)
  --stage sentences   translate the seeds into English cards
  --finalize          merge 14B polish, reverting rewrites that lose the pattern
  --verify-dir DIR    check English pattern compliance for a directory
"""

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

from pack_patterns import (
    ANGLES,
    CJK_RE,
    LABELS,
    MAX_WORDS,
    MIN_WORDS,
    passes_en,
    passes_zh,
    word_count,
)

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.toml"
TEMPLATE = ROOT / "prompts" / "generate_pack.txt"
DECK_DIR = ROOT / "data" / "sentences_polished"

PACK_DIR = ROOT / "data" / "packs"
PLAN_DIR = PACK_DIR / "plans"
SENT_DIR = PACK_DIR / "sentences"
POLISHED_DIR = PACK_DIR / "polished"
FINAL_DIR = PACK_DIR / "final"
OVERRIDES = PACK_DIR / "overrides.json"
SEED_DIR = PACK_DIR / "seeds"

ZH_SYSTEM = "You write Chinese example sentences for bilingual flashcards. Output only valid JSON."

PROPER_ZH_RE = re.compile(
    r"(北京|上海|广州|深圳|杭州|成都|重庆|西安|南京|武汉|天津|苏州|香港|澳门|台北|东京|纽约|伦敦|巴黎|首尔|新加坡|"
    r"中国|美国|英国|日本|韩国|法国|德国|泰国|加拿大|澳大利亚|微信|支付宝|淘宝|京东|滴滴|美团|星巴克|麦当劳|肯德基|苹果|华为|小米)"
)
EN_SYSTEM = "You write English translations for bilingual flashcards. Output only valid JSON."

ZH_TEMPLATE = """You write Chinese example sentences for a Chinese learner's English flashcard deck.

Scene: $scene_zh ($scene_en)
Target structure: $target
Micro-situation: $micro_zh

Each numbered angle below is one concrete everyday situation. For every angle write exactly two different Chinese sentences, so you must return $expected items in total.
Rules:
1. Each sentence is 8-26 Chinese characters, natural spoken Mandarin, one complete statement or question.
2. Every sentence must naturally use the target structure.
3. Describe one main event with at most one supporting detail. Stay on the exact angle; do not replace it with a different situation. Do not chain three or more clauses.
4. The two sentences for one angle must differ in their details (who, when, where, what).
5. Use A1-B2 everyday words. No brand names and no proper nouns such as cities, companies, or people's names.
6. Do not repeat or paraphrase another sentence in the list. Use Chinese numerals instead of digits.
7. Do not add meta text or labels. Output sentences only.

Angles:
$angles

Return JSON only:
{"items":[{"angle":1,"zh":"中文句子。"},{"angle":1,"zh":"另一个中文句子。"}]}"""


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=["plan", "sentences"], help="generation stage")
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--scenes", nargs="*", help="only these pack scene ids")
    p.add_argument("--limit", type=int, help="max cards per scene (testing)")
    p.add_argument("--batch", type=int, default=6)
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--pause", type=float, default=2.0)
    p.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--finalize", action="store_true")
    p.add_argument("--final-dir", default=str(FINAL_DIR))
    p.add_argument("--raw-dir", default=str(SENT_DIR))
    p.add_argument("--polished-dir", default=str(POLISHED_DIR))
    p.add_argument("--verify-dir")
    return p.parse_args()


def load_scenes():
    with open(CONFIG, "rb") as f:
        return tomllib.load(f)["scenes"]


def pack_scenes(only=None):
    scenes = []
    for scene in load_scenes():
        if scene.get("mode") not in ("grammar", "narrative"):
            continue
        scene = dict(scene)
        if scene["pack"] == "narrative" and not scene["pattern"].startswith("narrative_"):
            scene["pattern"] = "narrative_" + scene["pattern"]
        scenes.append(scene)
    if only:
        wanted = set(only)
        scenes = [s for s in scenes if s["id"] in wanted]
    return scenes


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def make_uid(scene, zh):
    return f"{scene}-{hashlib.sha1(normalize(zh).encode('utf-8')).hexdigest()[:10]}"


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def load_reference_sets():
    zh, en = set(), set()
    for path in DECK_DIR.glob("*.jsonl"):
        for rec in load_jsonl(path):
            zh.add(normalize(rec["zh"]))
            en.add(normalize(rec["en"]))
    return zh, en


def call_ollama(args, system, prompt, count, temperature):
    payload = {
        "model": args.model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
            "top_p": args.top_p,
            "num_predict": max(400, count * 90 + 250),
            "seed": random.randint(0, 2**31 - 1),
        },
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
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


def extract_json(text, key):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise
        data = json.loads(text[start : end + 1])
    if isinstance(data, list):
        return data
    return data.get(key) or []


def clean_zh(text):
    text = str(text).strip().strip("\"'“”")
    text = re.sub(r"^\s*\d+\s*[.、)）]\s*", "", text)
    text = re.sub(r"\s+", "", text)
    question = text.endswith(("？", "?"))
    text = re.sub(r"[。．.；;，,？！?!]+$", "", text)
    if not text:
        return ""
    return text + ("？" if question else "。")


def clean_en(text):
    en = str(text).strip().strip("\"'")
    en = re.sub(r"\s+", " ", en)
    for full, half in (("？", "?"), ("！", "!"), ("。", "."), ("，", ","), ("；", ";"), ("：", ":")):
        en = en.replace(full, half)
    if en and en[-1] not in ".?!":
        en += "."
    if en:
        en = en[0].upper() + en[1:]
    return en


def near_dup(text, others, threshold):
    key = normalize(text)
    return any(SequenceMatcher(None, key, normalize(o)).ratio() >= threshold for o in others)


def plan_path(scene_id):
    return PLAN_DIR / f"{scene_id}.json"


def plan_zh_for_scene(args, scene, ref_zh, done_zh):
    path = plan_path(scene["id"])
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"items": []}
    items = data.get("items", [])
    pattern = scene["pattern"]
    want = args.limit or scene["target"]
    if len(items) >= want:
        print(f"  {scene['id']}: plan already has {len(items)} items, skip")
        return items

    micros = scene["micros"]
    angles = ANGLES[pattern]
    per_angle = 2
    angle_total = max(1, (want + per_angle - 1) // per_angle)
    angle_total = min(angle_total, len(angles))

    seen = [it["zh"] for it in items]
    covered = {it["angle"] for it in items}
    attempts = 0
    while len(items) < want and attempts < 20:
        attempts += 1
        uncovered = [i for i in range(len(angles)) if (i + 1) not in covered]
        if uncovered:
            chosen_idx = uncovered[:4]
        else:
            start = (attempts - 1) % len(angles)
            chosen_idx = [(start + i) % len(angles) for i in range(min(4, angle_total))]
        chosen = [angles[i] for i in chosen_idx]
        angle_lines = "\n".join(f"{i}. {a}" for i, a in enumerate(chosen, 1))
        micro = micros[0] if chosen_idx[0] < 5 else micros[-1]
        prompt = (
            ZH_TEMPLATE.replace("$scene_zh", scene["zh"])
            .replace("$scene_en", scene["en"])
            .replace("$target", LABELS[pattern])
            .replace("$micro_zh", micro["zh"])
            .replace("$angles", angle_lines)
            .replace("$expected", str(len(chosen) * per_angle))
        )
        if seen:
            prompt += "\n\nAlready used, do not repeat or paraphrase:\n" + "\n".join(f"- {s}" for s in seen[-12:])
        try:
            raw = extract_json(call_ollama(args, ZH_SYSTEM, prompt, len(chosen) * per_angle, 0.7), "items")
        except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            print(f"    retry {scene['id']}: {type(exc).__name__}: {exc}", file=sys.stderr)
            time.sleep(2)
            continue

        for entry in raw:
            if not isinstance(entry, dict):
                continue
            zh = clean_zh(entry.get("zh", ""))
            if not zh or len(CJK_RE.findall(zh)) < 8 or len(CJK_RE.findall(zh)) > 26:
                continue
            if re.search(r"[A-Za-z]", zh) or PROPER_ZH_RE.search(zh):
                continue
            try:
                slot = int(entry.get("angle", 1))
            except (TypeError, ValueError):
                slot = 1
            if not 1 <= slot <= len(chosen_idx):
                slot = 1
            angle = chosen_idx[slot - 1] + 1
            if not passes_zh(pattern, zh):
                continue
            key = normalize(zh)
            if key in done_zh or near_dup(zh, seen, 0.86):
                continue
            if any(normalize(r["zh"]) == key for r in items):
                continue
            micro_cfg = micros[0] if angle <= 5 else micros[-1]
            item = {
                "zh": zh,
                "angle": angle,
                "angle_zh": angles[angle - 1],
                "micro": micro_cfg["id"],
                "micro_zh": micro_cfg["zh"],
            }
            items.append(item)
            seen.append(zh)
            covered.add(angle)
            if len(items) >= want:
                break
        if args.pause:
            time.sleep(args.pause)
        print(f"  {scene['id']:<26} plan {len(items):>2}/{want}", flush=True)

    data = {"scene": scene["id"], "pattern": pattern, "items": items}
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if len(items) < want:
        print(f"  WARNING: {scene['id']} plan only {len(items)}/{want}")


def seeds_for(scene):
    path = SEED_DIR / f"{scene['id']}.jsonl"
    if path.exists():
        rows = load_jsonl(path)
    else:
        rows = []
        for name in ("grammar.jsonl", "narrative.jsonl"):
            p = SEED_DIR / name
            if p.exists():
                rows += [r for r in load_jsonl(p) if r.get("scene") == scene["id"]]
    if not rows:
        return None
    micros = scene["micros"]
    items = []
    for row in rows:
        zh = clean_zh(row["zh"])
        angle = int(row.get("angle", 1))
        micro_cfg = micros[0] if angle <= 5 else micros[-1]
        items.append({
            "zh": zh,
            "angle": angle,
            "angle_zh": ANGLES[scene["pattern"]][angle - 1],
            "micro": micro_cfg["id"],
            "micro_zh": micro_cfg["zh"],
        })
    return items


def stage_plan(args):
    ref_zh, _ = load_reference_sets()
    for scene in pack_scenes(args.scenes):
        seed_items = seeds_for(scene)
        if seed_items is not None:
            want = args.limit or scene["target"]
            items = seed_items[:want]
            bad = [it["zh"] for it in items if not passes_zh(scene["pattern"], it["zh"])]
            data = {"scene": scene["id"], "pattern": scene["pattern"], "items": items, "source": "seed"}
            plan_path(scene["id"]).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            note = f" | {len(bad)} fail zh check" if bad else ""
            print(f"  {scene['id']:<26} seed {len(items)}/{want}{note}")
            for zh in bad[:3]:
                print(f"    zh check: {zh}", file=sys.stderr)
            continue
        done_zh = set(ref_zh)
        for other in PLAN_DIR.glob("*.json") if PLAN_DIR.exists() else []:
            for it in json.loads(other.read_text(encoding="utf-8")).get("items", []):
                done_zh.add(normalize(it["zh"]))
        plan_zh_for_scene(args, scene, ref_zh, done_zh)


def build_en_prompt(scene, batch):
    lines = []
    for i, item in enumerate(batch, 1):
        lines.append(f'{i}. zh: {item["zh"]} | target: {LABELS[scene["pattern"]]}')
    return TEMPLATE.read_text(encoding="utf-8").replace("{items}", "\n".join(lines))


def record_for(scene, item, en, model):
    tags = [f"pack::{scene['pack']}", f"pattern::{scene['pattern']}"]
    if scene["pack"] == "narrative":
        tags.append(f"topic::{scene['pattern'].replace('narrative_', '')}")
    return {
        "uid": make_uid(scene["id"], item["zh"]),
        "scene": scene["id"],
        "scene_zh": scene["zh"],
        "scene_en": scene["en"],
        "group": scene["group"],
        "phase": scene.get("phase", 3),
        "micro": item["micro"],
        "micro_zh": item["micro_zh"],
        "zh": item["zh"],
        "en": en,
        "sub": item["angle_zh"],
        "angle": LABELS[scene["pattern"]],
        "pack": scene["pack"],
        "pattern": scene["pattern"],
        "topic": scene["pattern"].replace("narrative_", "") if scene["pack"] == "narrative" else None,
        "tags": tags,
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def validate_en(scene, zh, en, known_en):
    if not en or CJK_RE.search(en):
        return "en_invalid"
    n = word_count(en)
    limit = MAX_WORDS[scene["pack"]]
    if n < MIN_WORDS or n > limit:
        return f"word_count_{n}"
    if re.search(r"[0-9]", en) and not re.search(r"[0-9零一二三四五六七八九十百千万亿两]", zh):
        return "invented_number"
    if not passes_en(scene["pattern"], en):
        return "pattern_miss"
    if normalize(en) in known_en:
        return "duplicate"
    return None


def translate_scene(args, scene, ref_en):
    out_path = SENT_DIR / f"{scene['id']}.jsonl"
    records = load_jsonl(out_path)
    if args.limit:
        records = records[: args.limit]
    done = {r["uid"] for r in records}
    plan = json.loads(plan_path(scene["id"]).read_text(encoding="utf-8"))
    items = plan["items"][: args.limit] if args.limit else plan["items"]
    pending = [it for it in items if make_uid(scene["id"], it["zh"]) not in done]
    if not pending:
        print(f"  {scene['id']:<26} {len(records)} cards, nothing pending")
        return

    local_en = {normalize(r["en"]) for r in records}
    known_en = ref_en | local_en
    print(f"  {scene['id']:<26} {len(records)} cards, {len(pending)} pending")
    failures = []
    for start in range(0, len(pending), args.batch):
        batch = pending[start : start + args.batch]
        prompt = build_en_prompt(scene, batch)
        pairs = None
        for attempt in range(args.retries + 1):
            try:
                pairs = extract_json(call_ollama(args, EN_SYSTEM, prompt, len(batch), args.temperature), "pairs")
                break
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"    retry {scene['id']}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
        if not pairs:
            failures.extend(batch)
            continue
        by_id = {}
        for p in pairs:
            if isinstance(p, dict):
                pid = p.get("id")
                if isinstance(pid, str) and pid.isdigit():
                    pid = int(pid)
                if isinstance(pid, int):
                    by_id[pid] = p.get("en", "")
        for i, item in enumerate(batch, 1):
            en = clean_en(by_id.get(i, "") or "")
            reason = validate_en(scene, item["zh"], en, known_en) if en else "missing"
            if reason:
                failures.append(item)
                continue
            rec = record_for(scene, item, en, args.model)
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
            known_en.add(normalize(en))
            print(f"    + {en}")
        if args.pause:
            time.sleep(args.pause)

    for item in failures:
        retry_prompt = build_en_prompt(scene, [item])
        retry_prompt += (
            "\n\nThe previous attempt for this item was rejected by the quality check. "
            f"You MUST use this target structure: {LABELS[scene['pattern']]}. "
            "Keep every detail of the Chinese sentence and do not leave anything out."
        )
        for attempt in range(args.retries + 1):
            try:
                pairs = extract_json(
                    call_ollama(
                        args,
                        EN_SYSTEM,
                        retry_prompt,
                        1,
                        min(1.0, 0.75 + 0.1 * attempt),
                    ),
                    "pairs",
                )
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
                time.sleep(2)
                continue
            en = clean_en((pairs[0] or {}).get("en", "")) if pairs else ""
            reason = validate_en(scene, item["zh"], en, known_en) if en else "missing"
            if reason:
                print(f"    reject {item['zh']} {reason}: {en}", file=sys.stderr)
                continue
            rec = record_for(scene, item, en, args.model)
            with open(out_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
            known_en.add(normalize(en))
            print(f"    + {en}")
            break
        else:
            print(f"  WARNING: {scene['id']} missing card for {item['zh']}", file=sys.stderr)


def stage_sentences(args):
    _, ref_en = load_reference_sets()
    for scene in pack_scenes(args.scenes):
        if not plan_path(scene["id"]).exists():
            print(f"  {scene['id']:<26} no plan, skip")
            continue
        translate_scene(args, scene, ref_en)


def finalize(args):
    raw = {}
    for path in Path(args.raw_dir).glob("*.jsonl"):
        for rec in load_jsonl(path):
            raw[rec["uid"]] = rec
    polished = {}
    for path in Path(args.polished_dir).glob("*.jsonl"):
        for rec in load_jsonl(path):
            polished[rec["uid"]] = rec
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    scenes = {s["id"]: s for s in pack_scenes()}

    out_dir = Path(args.final_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("*.jsonl"):
        p.unlink()
    reverted = 0
    for uid, rec in raw.items():
        scene = scenes.get(rec["scene"])
        if not scene:
            continue
        new = polished.get(uid, {}).get("en", rec["en"])
        if not passes_en(scene["pattern"], new) and passes_en(scene["pattern"], rec["en"]):
            rec["polished_en"] = new
            rec["polish_reverted"] = True
            reverted += 1
        else:
            rec["en"] = new
            rec["polish_reverted"] = False
        override = overrides.get(uid)
        if override:
            rec["en"] = override
            rec["manual_override"] = True
        path = out_dir / f"{rec['scene']}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Finalized {len(raw)} cards -> {out_dir} | reverted {reverted} polished rewrites")


def verify(args):
    records = []
    for path in sorted(Path(args.verify_dir).glob("*.jsonl")):
        records.extend(load_jsonl(path))
    failed = 0
    for rec in records:
        ok = passes_en(rec["pattern"], rec["en"]) and passes_zh(rec["pattern"], rec["zh"])
        if not ok:
            failed += 1
            print(f"FAIL {rec['pattern']:<28} {rec['zh']} | {rec['en']}")
    print(f"{len(records) - failed}/{len(records)} pass pattern checks")
    return 1 if failed else 0


def main():
    args = parse_args()
    for d in (PLAN_DIR, SENT_DIR):
        d.mkdir(parents=True, exist_ok=True)
    if args.verify_dir:
        raise SystemExit(verify(args))
    if args.finalize:
        finalize(args)
        return
    if args.dry_run:
        for scene in pack_scenes(args.scenes):
            print(f"{scene['id']:<26} {scene['zh']} | plan {len(json.loads(plan_path(scene['id']).read_text())['items']) if plan_path(scene['id']).exists() else 0}")
        return
    if args.stage == "plan":
        stage_plan(args)
    elif args.stage == "sentences":
        stage_sentences(args)
    else:
        raise SystemExit("Specify --stage plan|sentences, --finalize, or --verify-dir")


if __name__ == "__main__":
    main()
