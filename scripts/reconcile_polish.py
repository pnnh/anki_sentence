#!/usr/bin/env python3
"""Revert polished English that duplicates or near-duplicates earlier cards."""

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def normalize(text):
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences"))
    p.add_argument("--polished-dir", default=str(ROOT / "data" / "sentences_polished"))
    p.add_argument("--threshold", type=float, default=0.92)
    p.add_argument("--apply", action="store_true")
    return p.parse_args()


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def main():
    args = parse_args()
    data_dir, polished_dir = Path(args.data_dir), Path(args.polished_dir)
    report = []
    total_reverted = total_dropped = 0
    for path in sorted(polished_dir.glob("*.jsonl")):
        originals = {r["uid"]: r["en"] for r in load(data_dir / path.name)}
        rows = load(path)
        orig_en = [originals.get(r["uid"], r["en"]) for r in rows]

        final_n = []
        final_set = set()

        def clashes(en):
            n = normalize(en)
            if n in final_set:
                return True
            return any(SequenceMatcher(None, n, m).ratio() >= args.threshold for m in final_n)

        def assign(i, en, reason):
            rows[i]["en"] = en
            final_n.append(normalize(en))
            final_set.add(final_n[-1])
            if reason:
                report.append(
                    {"scene": rows[i]["scene"], "uid": rows[i]["uid"], "zh": rows[i]["zh"],
                     "kept_en": en, "reason": reason}
                )

        dropped = []
        reverted = 0
        for i, row in enumerate(rows):
            cand = row["en"]
            if not clashes(cand):
                assign(i, cand, None)
                continue
            old = orig_en[i]
            if not clashes(old):
                assign(i, old, "duplicate")
                reverted += 1
                continue
            fixed = False
            for j in range(i - 1, -1, -1):
                if not clashes_at(old, j, final_n, args.threshold):
                    continue
                saved_n = final_n[j]
                final_n[j] = ""
                if saved_n in final_set:
                    final_set.discard(saved_n)
                if not clashes(orig_en[j]):
                    rows[j]["en"] = orig_en[j]
                    final_n[j] = normalize(orig_en[j])
                    final_set.add(final_n[j])
                    assign(i, old, "duplicate_shift")
                    reverted += 2
                    fixed = True
                    break
                final_n[j] = saved_n
                final_set.add(saved_n)
            if not fixed:
                dropped.append(i)

        if dropped:
            dropped_set = set(dropped)
            rows = [r for i, r in enumerate(rows) if i not in dropped_set]
        total_reverted += reverted
        total_dropped += len(dropped)
        print(f"{path.stem:<18} reverted {reverted:>3} | dropped {len(dropped)}")
        if args.apply:
            tmp = path.with_suffix(".jsonl.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            tmp.replace(path)

    print(f"Total reverted {total_reverted}, dropped {total_dropped}")
    if args.apply:
        (ROOT / "reports" / "polish_reconcile.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in report) + "\n",
            encoding="utf-8",
        )


def clashes_at(en, j, final_n, threshold=0.92):
    n = normalize(en)
    return final_n[j] == n or SequenceMatcher(None, n, final_n[j]).ratio() >= threshold


if __name__ == "__main__":
    main()
