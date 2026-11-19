#!/usr/bin/env python3
"""Polish generated English translations with a larger local model."""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")
DIGIT_RE = re.compile(r"\d+")
BRANDS = {
    "alipay", "wechat", "weixin", "didi", "taobao", "tmall", "starbucks", "mcdonald's",
    "mcdonalds", "kfc", "uber", "airbnb", "google", "apple", "iphone", "facebook",
    "instagram", "whatsapp", "netflix", "amazon",
}

SYSTEM = "You edit English translations for bilingual flashcards. Output only valid JSON."

TEMPLATE = """You are polishing English translations for a Chinese learner's everyday spoken English deck.
For every item below you get the scene, the micro-situation, the Chinese front, and the current English translation.

Rewrite the English so it is natural, accurate, and conversational, suitable for A1-B2 learners.
Rules:
- Keep the exact same meaning and function. A question stays a question, a request stays a request.
- Keep every number, amount, currency, time, and place exactly as in the Chinese.
- Do not leave out information. If the current English omits a time, place, reason, contrast, or number from the Chinese, add it back naturally.
- 4-{max_words} words, one complete sentence, no fragments.
- No brand names and no proper nouns. Use generic words instead.
- Use common everyday vocabulary. Avoid rare or formal words.
- If the current translation is already good, return it unchanged.

{items}

Return JSON only: {"pairs":[{"id":1,"en":"..."}]}"""


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenes", nargs="*", help="scene ids (default: all files)")
    p.add_argument("--model", default="qwen2.5:14b")
    p.add_argument("--batch", type=int, default=10)
    p.add_argument("--max-words", type=int, default=16)
    p.add_argument("--limit", type=int, help="max cards per scene")
    p.add_argument("--pause", type=float, default=1.0)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences"))
    p.add_argument("--out-dir", default=str(ROOT / "data" / "sentences_polished"))
    p.add_argument("--patch-dir", default=str(ROOT / "data" / "patches"))
    return p.parse_args()


def has_cjk(text):
    return bool(CJK_RE.search(text))


def load_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def validate_en(old_en, new_en, zh, max_words=16):
    if not isinstance(new_en, str):
        return None
    en = normalize(new_en).strip("\"'")
    if not en or has_cjk(en):
        return None
    for full, half in (("？", "?"), ("！", "!"), ("。", "."), ("，", ","), ("；", ";"), ("：", ":")):
        en = en.replace(full, half)
    if en[-1] not in ".?!":
        en += "."
    en = en[0].upper() + en[1:]
    n = len(WORD_RE.findall(en))
    if n < 4 or n > max_words:
        return None
    if any(w.lower().strip("'") in BRANDS for w in WORD_RE.findall(en)):
        return None
    if any(d not in en for d in DIGIT_RE.findall(zh)):
        return None
    if DIGIT_RE.search(en) and not re.search(r"[0-9零一二三四五六七八九十百千万亿两]", zh):
        return None
    return en


def call_ollama(args, prompt):
    payload = {
        "model": args.model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": args.temperature,
            "num_predict": max(400, args.batch * 60 + 300),
        },
        "messages": [
            {"role": "system", "content": SYSTEM},
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
    content = data.get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        parsed = json.loads(content[start : end + 1])
    return parsed.get("pairs", [])


def write_atomic(path, records):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def polish_scene(args, scene_path, out_dir, patch_dir):
    scene_id = load_jsonl(scene_path)[0]["scene"]
    out_path = out_dir / f"{scene_id}.jsonl"
    patch_path = patch_dir / f"{scene_id}.jsonl"
    patches = {p["uid"]: p for p in load_jsonl(patch_path)}
    records = load_jsonl(out_path) if out_path.exists() else load_jsonl(scene_path)
    for rec in records:
        if rec["uid"] in patches:
            rec["en"] = patches[rec["uid"]]["new_en"]
    if not records:
        return 0, 0
    pending = [r for r in records if r["uid"] not in patches]
    if args.limit:
        pending = pending[: args.limit]
    print(f"{scene_id}: {len(records)} cards, {len(pending)} to polish, {len(patches)} resumed", flush=True)
    if not pending:
        write_atomic(out_path, records)
        return len(records), 0
    changed_total = 0
    for start in range(0, len(pending), args.batch):
        batch = pending[start : start + args.batch]
        lines = []
        for i, rec in enumerate(batch, 1):
            lines.append(
                f'{i}. [{rec["scene_zh"]} / {rec["micro_zh"]}] zh: {rec["zh"]} | current en: {rec["en"]}'
            )
        prompt = TEMPLATE.replace("{max_words}", str(args.max_words)).replace(
            "{items}", "\n".join(lines)
        )
        pairs = None
        for attempt in range(args.retries + 1):
            try:
                pairs = call_ollama(args, prompt)
                break
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"  retry {scene_id}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
        if not pairs:
            continue

        accepted = 0
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        by_id = {}
        for p in pairs:
            if isinstance(p, dict) and isinstance(p.get("id"), int):
                by_id[p["id"]] = p.get("en", "")
        for i, rec in enumerate(batch, 1):
            new_en = validate_en(rec["en"], by_id.get(i), rec["zh"], args.max_words) or rec["en"]
            if new_en != rec["en"]:
                accepted += 1
            patch = {
                "uid": rec["uid"],
                "scene": rec["scene"],
                "zh": rec["zh"],
                "micro": rec["micro"],
                "old_en": rec["en"],
                "new_en": new_en,
                "changed": new_en != rec["en"],
                "model": args.model,
                "created_at": now,
            }
            patches[rec["uid"]] = patch
            with open(patch_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(patch, ensure_ascii=False) + "\n")
            rec["en"] = new_en
        changed_total += accepted
        write_atomic(out_path, records)
        done = len(patches)
        print(
            f"  {done:>4}/{len(records)} polished | changed {accepted} | total changed {changed_total}",
            flush=True,
        )
        if args.pause:
            time.sleep(args.pause)
    return len(records), changed_total


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    patch_dir = Path(args.patch_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(data_dir.glob("*.jsonl"))
    if args.scenes:
        wanted = set(args.scenes)
        paths = [p for p in paths if p.stem in wanted]
    if not paths:
        raise SystemExit("No sentence files found")

    total, changed = 0, 0
    for path in paths:
        n, c = polish_scene(args, path, out_dir, patch_dir)
        total += n
        changed += c
    print(f"Done. Polished {total} cards, changed {changed}.")


if __name__ == "__main__":
    main()
