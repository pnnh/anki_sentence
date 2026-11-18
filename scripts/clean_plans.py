#!/usr/bin/env python3
"""Drop generic or cross-micro duplicate items from generated plans."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def is_generic(text):
    if any(term in text for term in ("礼貌结束", "结束对话")):
        return True
    return text in {"表达偏好"}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plans", nargs="*", help="plan json files (default: all in data/plans)")
    p.add_argument("--apply", action="store_true", help="write cleaned plans in place")
    return p.parse_args()


def main():
    args = parse_args()
    paths = [Path(p) for p in args.plans] or sorted((ROOT / "data" / "plans").glob("*.json"))
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        seen = {}
        dropped = []
        kept_total = 0
        for micro, items in data.get("micros", {}).items():
            kept = []
            for item in items:
                text = str(item).strip()
                key = normalize(text)
                if is_generic(text):
                    dropped.append((micro, text, "generic"))
                    continue
                if len(key) < 3:
                    dropped.append((micro, text, "too_short"))
                    continue
                if key in seen:
                    dropped.append((micro, text, f"dup_of:{seen[key]}"))
                    continue
                seen[key] = micro
                kept.append(text)
            data["micros"][micro] = kept
            kept_total += len(kept)
        print(f"{path.name}: kept {kept_total}, dropped {len(dropped)}")
        for micro, text, why in dropped:
            print(f"  - {micro}: {text} ({why})")
        if args.apply:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
