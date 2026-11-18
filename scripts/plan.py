#!/usr/bin/env python3
"""Draft micro-situation plans so each generated sentence has a concrete intent."""

import argparse
import json
import re
import sys
import time
import tomllib
from difflib import SequenceMatcher
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenes.toml"

SYSTEM = "You plan content for bilingual flashcards. Output only valid JSON."

TEMPLATE = """Scene: $scene_zh ($scene_en)
Micro-situation: $micro_zh

List the $count MOST COMMON, everyday sub-situations a customer or traveler may face within this exact micro-situation.
Prioritize what ordinary people actually say. Avoid rare edge cases, legal details, financial procedures, and formal steps unless they are very common.
They must cover different communication goals and be clearly different from each other. Do not repeat the same idea with different wording.
Cover a range of goals such as asking for information, making a request, comparing options, describing a problem, confirming details, asking for a recommendation, and asking for an alternative.
Do not use generic items such as 礼貌结束对话, 表达偏好, or bare topic labels. Every item must be a concrete situation.
Stay strictly inside this micro-situation. Do not include these neighboring micro-situations: $forbidden.

Write each item as a short Chinese intention phrase (4-18 characters), not a full sentence, with no ending punctuation.

Output JSON only:
{"items":["...","..."]}"""


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scene", required=True)
    p.add_argument("--micros", nargs="*")
    p.add_argument("--items", type=int, default=10)
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    p.add_argument("--out-dir", default=str(ROOT / "data" / "plans"))
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def load_scene(scene_id):
    with open(CONFIG, "rb") as f:
        scenes = tomllib.load(f)["scenes"]
    for scene in scenes:
        if scene["id"] == scene_id:
            return scene
    raise SystemExit(f"Unknown scene id: {scene_id}")


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def clean_item(text):
    text = str(text).strip().splitlines()[0]
    text = re.sub(r"^\s*\d+\s*[.、)）]\s*", "", text)
    text = text.strip().strip("\"'“”")
    text = re.sub(r"[。．.；;，,]+$", "", text)
    return text.strip()


def ollama(args, prompt):
    payload = {
        "model": args.model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": args.temperature,
            "num_predict": max(400, args.items * 45 + 150),
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
    items = parsed.get("items") if isinstance(parsed, dict) else parsed
    if not isinstance(items, list):
        raise ValueError("JSON does not contain an items list")
    return items


def main():
    args = parse_args()
    scene = load_scene(args.scene)
    micros = scene["micros"]
    if args.micros:
        wanted = set(args.micros)
        micros = [m for m in micros if m["id"] in wanted]
        if not micros:
            raise SystemExit("No matching micro ids")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{scene['id']}.json"
    plan = {"scene": scene["id"], "micros": {}}
    if out_path.exists():
        plan = json.loads(out_path.read_text(encoding="utf-8"))
        plan.setdefault("micros", {})

    other_names = [m["zh"] for m in scene["micros"]]
    for micro in micros:
        if plan["micros"].get(micro["id"]) and not args.force:
            print(f"  {micro['id']:<22} exists ({len(plan['micros'][micro['id']])} items), skip")
            continue
        forbidden = "、".join(n for n in other_names if n != micro["zh"])
        prompt = (
            TEMPLATE.replace("$scene_zh", scene["zh"])
            .replace("$scene_en", scene["en"])
            .replace("$micro_zh", micro["zh"])
            .replace("$count", str(args.items))
            .replace("$forbidden", forbidden)
        )
        if args.dry_run:
            print(f"  {micro['id']:<22} would generate {args.items} items")
            continue

        seen = set()
        items = []
        attempts = 0
        while len(items) < args.items and attempts <= args.retries:
            attempts += 1
            try:
                raw = ollama(args, prompt)
            except (error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                print(f"    retry {micro['id']}: {type(exc).__name__}: {exc}", file=sys.stderr)
                time.sleep(2)
                continue
            for entry in raw:
                text = clean_item(entry.get("zh") or entry.get("item") or entry) if isinstance(entry, dict) else clean_item(entry)
                key = normalize(text)
                if not text or not key or key in seen:
                    continue
                if len(text) > 24:
                    continue
                if any(term in text for term in ("礼貌结束", "结束对话")) or text == "表达偏好":
                    continue
                if any(SequenceMatcher(None, key, normalize(x)).ratio() >= 0.75 for x in items):
                    continue
                seen.add(key)
                items.append(text)
                if len(items) >= args.items:
                    break
            if len(items) < args.items and attempts <= args.retries:
                prompt += (
                    f"\n\nYou already listed: {'、'.join(items)}.\n"
                    f"Add {args.items - len(items)} more items that are different from those."
                )
        if len(items) < args.items:
            print(f"  WARNING: {micro['id']} only got {len(items)}/{args.items} items", file=sys.stderr)
        plan["micros"][micro["id"]] = items
        out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {micro['id']:<22} {len(items)} items")
        for i, item in enumerate(items, 1):
            print(f"      {i:>2}. {item}")

    if not args.dry_run:
        print(f"Plan: {out_path}")


if __name__ == "__main__":
    main()
