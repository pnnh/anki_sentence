#!/usr/bin/env python3
"""Build distributable release artifacts: .apkg, data zip, and checksums."""

import argparse
import hashlib
import html
import json
import os
import sys
import zipfile
from pathlib import Path

import genanki

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from import_anki import BACK, CSS, DECK, FIELDS, FRONT, MODEL, tag_for  # noqa: E402

ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences_polished"))
    p.add_argument("--pack-dir", default=str(ROOT / "data" / "packs" / "final"))
    p.add_argument("--out-dir", default=str(ROOT / "dist"))
    p.add_argument("--version", default=os.environ.get("GITHUB_REF_NAME", "dev"))
    return p.parse_args()


def stable_id(text):
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % (2**31)


def load_records(data_dirs):
    records = []
    found = False
    for data_dir in data_dirs:
        paths = sorted(Path(data_dir).glob("*.jsonl"))
        if not paths:
            continue
        found = True
        for path in paths:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
    if not found:
        raise SystemExit(f"No JSONL files in {', '.join(map(str, data_dirs))}")
    uids = {r["uid"] for r in records}
    if len(uids) != len(records):
        raise SystemExit("Duplicate UIDs found; run qc.py first.")
    return records


def dedupe(records):
    seen = set()
    unique = []
    for rec in records:
        key = (rec["zh"].strip(), rec["en"].strip())
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    return unique


def field(text):
    return html.escape(str(text), quote=False)


def build_deck(records):
    model = genanki.Model(
        stable_id(f"{MODEL}::model"),
        MODEL,
        fields=[{"name": name} for name in FIELDS],
        templates=[{"name": "Card 1", "qfmt": FRONT, "afmt": BACK}],
        css=CSS,
    )
    deck = genanki.Deck(stable_id(f"{DECK}::deck"), DECK)
    for rec in records:
        deck.add_note(
            genanki.Note(
                model=model,
                guid=rec["uid"],
                fields=[
                    field(rec["zh"]),
                    field(rec["en"]),
                    field(rec["scene_zh"]),
                    field(rec["scene_en"]),
                ],
                tags=tag_for(rec),
            )
        )
    return deck


def write_data_zip(path, version, data_dirs):
    root = f"anki_sentence-{version}"
    entries = []
    for data_dir in data_dirs:
        if Path(data_dir).is_dir():
            entries += [(p, p.relative_to(ROOT)) for p in sorted(Path(data_dir).glob("*.jsonl"))]
    entries += [(p, p.relative_to(ROOT)) for p in sorted((ROOT / "config").rglob("*")) if p.is_file()]
    entries += [(p, p.relative_to(ROOT)) for p in sorted((ROOT / "prompts").rglob("*")) if p.is_file()]
    entries += [(ROOT / name, Path(name)) for name in ("README.md", "LICENSE")]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, rel in entries:
            info = zipfile.ZipInfo(f"{root}/{rel.as_posix()}", date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_dirs = [args.data_dir]
    if Path(args.pack_dir).is_dir():
        data_dirs.append(args.pack_dir)
    records = load_records(data_dirs)
    unique = dedupe(records)
    deck = build_deck(unique)

    apkg = out_dir / f"anki_sentence-{args.version}.apkg"
    data_zip = out_dir / f"anki_sentence-{args.version}-data.zip"
    deck.write_to_file(str(apkg))
    write_data_zip(data_zip, args.version, data_dirs)

    sums = out_dir / "SHA256SUMS"
    lines = [f"{sha256(p)}  {p.name}" for p in (apkg, data_zip)]
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8")

    scenes = len({r["scene"] for r in unique})
    print(f"Built {apkg.name} ({apkg.stat().st_size / 1024:.0f} KiB)")
    print(f"Built {data_zip.name} ({data_zip.stat().st_size / 1024:.0f} KiB)")
    print(f"Built {sums.name}")
    print(
        f"Cards: {len(unique)} | scenes: {scenes} | version: {args.version} | "
        f"duplicates skipped: {len(records) - len(unique)}"
    )


if __name__ == "__main__":
    main()
