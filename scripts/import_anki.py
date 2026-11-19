#!/usr/bin/env python3
"""Import generated sentence cards into Anki through AnkiConnect."""

import argparse
import json
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parent.parent
DECK = "生活英语句子"
MODEL = "生活句子 ZH→EN"
FIELDS = ["Chinese", "English", "SceneZH", "SceneEN"]

FRONT = """<div class="scene">[{{SceneZH}}]</div>
<div class="sentence">{{Chinese}}</div>"""

BACK = """{{FrontSide}}
<hr id="answer">
<div class="scene">[{{SceneEN}}]</div>
<div class="sentence en">{{English}}</div>"""

CSS = """.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
  font-size: 22px;
  line-height: 1.65;
  text-align: center;
  color: #1f2328;
  background-color: #fbfbf9;
  padding: 18px;
}
.scene {
  font-size: 13px;
  color: #8a8f98;
  margin-bottom: 14px;
  letter-spacing: .02em;
}
.sentence { margin: 0 auto; max-width: 34em; }
.en { font-size: 25px; color: #0b5cad; margin-top: 8px; }
hr#answer { border: 0; border-top: 1px solid #e2e2da; margin: 22px auto; width: 70%; }
"""


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", default=str(ROOT / "data" / "sentences_polished"))
    p.add_argument("--deck", default=DECK)
    p.add_argument("--model-name", default=MODEL)
    p.add_argument("--scene", help="only import this scene id")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=100)
    p.add_argument("--anki-url", default="http://127.0.0.1:8765")
    p.add_argument("--manifest", default=str(ROOT / "data" / "imported.json"))
    p.add_argument("--apply", action="store_true", help="actually write to Anki")
    p.add_argument("--verify", action="store_true", help="check manifest note ids still exist")
    p.add_argument(
        "--update-existing",
        action="store_true",
        help="update fields of notes already in the manifest",
    )
    return p.parse_args()


def anki(url, action, **params):
    payload = {"action": action, "version": 6, "params": params}
    req = request.Request(
        url.rstrip("/"),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        raise RuntimeError(f"{action}: {data['error']}")
    return data.get("result")


def load_records(data_dir, scene):
    records = []
    for path in sorted(Path(data_dir).glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    if not scene or rec["scene"] == scene:
                        records.append(rec)
    return records


def ensure_deck(url, deck):
    anki(url, "createDeck", deck=deck)


def ensure_model(url, model):
    existing = anki(url, "modelNames")
    if model in existing:
        fields = anki(url, "modelFieldNames", modelName=model)
        missing = [f for f in FIELDS if f not in fields]
        if missing:
            raise SystemExit(
                f"Note type {model!r} exists but is missing fields: {missing}. "
                "Rename or delete it in Anki and rerun."
            )
        return
    anki(
        url,
        "createModel",
        modelName=model,
        inOrderFields=FIELDS,
        css=CSS,
        isCloze=False,
        cardTemplates=[{"Name": "Card 1", "Front": FRONT, "Back": BACK}],
    )


def tag_for(rec):
    model_tag = rec.get("model", "unknown").replace(":", "-").replace(" ", "-")
    tags = [
        f"scene::{rec['scene']}",
        f"micro::{rec['scene']}::{rec['micro']}",
        f"phase::{rec.get('phase', 1)}",
        f"src::{model_tag}",
        f"uid::{rec['uid']}",
    ]
    tags += [t for t in rec.get("tags", []) if t.split("::")[0] in ("pack", "pattern", "topic")]
    return tags


def note_for(rec, deck, model):
    return {
        "deckName": deck,
        "modelName": model,
        "fields": {
            "Chinese": rec["zh"],
            "English": rec["en"],
            "SceneZH": rec["scene_zh"],
            "SceneEN": rec["scene_en"],
        },
        "tags": tag_for(rec),
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    }


def load_manifest(path):
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def save_manifest(path, manifest):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def existing_uids(url, manifest, candidates, verify):
    if not verify:
        return set(manifest) & {r["uid"] for r in candidates}
    by_note = {nid: uid for uid, nid in manifest.items() if nid}
    candidate_uids = {r["uid"] for r in candidates}
    note_ids = [nid for nid in by_note if by_note[nid] in candidate_uids]
    alive = set()
    for start in range(0, len(note_ids), 100):
        chunk = note_ids[start : start + 100]
        infos = anki(url, "notesInfo", notes=chunk)
        for info in infos:
            nid = info.get("noteId")
            if nid in by_note:
                alive.add(by_note[nid])
    return alive


def main():
    args = parse_args()
    try:
        version = anki(args.anki_url, "version")
    except Exception as exc:
        raise SystemExit(f"Cannot reach AnkiConnect at {args.anki_url}: {exc}")

    records = load_records(args.data_dir, args.scene)
    if args.limit:
        records = records[: args.limit]
    if not records:
        raise SystemExit("No records selected.")

    manifest = load_manifest(args.manifest)
    skip = existing_uids(args.anki_url, manifest, records, args.verify)
    todo = [r for r in records if r["uid"] not in skip]
    existing = [r for r in records if r["uid"] in skip] if args.update_existing else []

    scenes = {}
    for rec in records:
        scenes[rec["scene"]] = rec["scene_zh"]

    scene_summary = ", ".join(
        f"{sid}({sum(1 for rec in records if rec['scene'] == sid)})" for sid in scenes
    )
    print(f"AnkiConnect v{version} | deck: {args.deck} | note type: {args.model_name}")
    print(
        f"Selected: {len(records)} | already imported: {len(skip)} | "
        f"to add: {len(todo)} | to update: {len(existing)}"
    )
    print(f"Scenes: {scene_summary}")

    for rec in todo[:5]:
        print("\n  Front: [{}] {}".format(rec["scene_zh"], rec["zh"]))
        print("  Back:  [{}] {}".format(rec["scene_en"], rec["en"]))
        print("  Tags:  " + " ".join(tag_for(rec)))

    if not args.apply:
        print("\nDry run. Add --apply to create the deck/note type and import.")
        return

    ensure_deck(args.anki_url, args.deck)
    ensure_model(args.anki_url, args.model_name)

    updated = 0
    for rec in existing:
        nid = manifest.get(rec["uid"])
        if not nid:
            continue
        anki(
            args.anki_url,
            "updateNoteFields",
            note={
                "id": nid,
                "fields": {
                    "Chinese": rec["zh"],
                    "English": rec["en"],
                    "SceneZH": rec["scene_zh"],
                    "SceneEN": rec["scene_en"],
                },
            },
        )
        updated += 1
    if existing:
        print(f"Updated {updated} existing notes.", flush=True)

    imported = 0
    duplicates = 0
    for start in range(0, len(todo), args.batch_size):
        chunk = todo[start : start + args.batch_size]
        try:
            note_ids = anki(
                args.anki_url,
                "addNotes",
                notes=[note_for(rec, args.deck, args.model_name) for rec in chunk],
            )
        except RuntimeError:
            note_ids = []
            for rec in chunk:
                try:
                    ids = anki(
                        args.anki_url,
                        "addNotes",
                        notes=[note_for(rec, args.deck, args.model_name)],
                    )
                    note_ids.append(ids[0] if ids else None)
                except RuntimeError:
                    note_ids.append(None)
        for rec, nid in zip(chunk, note_ids):
            if nid:
                manifest[rec["uid"]] = nid
                imported += 1
            else:
                duplicates += 1
        save_manifest(args.manifest, manifest)
        print(
            f"  batch {start + len(chunk):>4}/{len(todo)} | imported {imported} | "
            f"duplicates {duplicates}",
            flush=True,
        )

    save_manifest(args.manifest, manifest)
    print(
        f"\nDone. Imported {imported}, updated {updated}, duplicates {duplicates}, "
        f"manifest {args.manifest}"
    )


if __name__ == "__main__":
    main()
