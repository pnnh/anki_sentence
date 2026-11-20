import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import polish


class OverridesFixture(unittest.TestCase):
    APPROVED = "Please wait for me here."
    MODEL_EN = "Could you say that again?"

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.data_dir = self.root / "data" / "sentences"
        self.out_dir = self.root / "output"
        self.patch_dir = self.root / "patches"
        for directory in (self.data_dir, self.out_dir, self.patch_dir):
            directory.mkdir(parents=True)
        self.scene_path = self.data_dir / "daily.jsonl"
        self.out_path = self.out_dir / "daily.jsonl"
        self.patch_path = self.patch_dir / "daily.jsonl"
        self.default_overrides = self.root / "data" / "sentence_overrides.json"
        self.record = self.make_record("daily-001")
        self.write_jsonl(self.scene_path, [self.record])
        self.args = SimpleNamespace(
            batch=10, max_words=16, limit=None, pause=0, retries=0,
            model="mock-model", temperature=0.2, timeout=1,
            ollama_url="http://unused.invalid", think=None,
        )
        self.start_patch(patch.object(polish, "ROOT", self.root))
        self.model = self.start_patch(patch.object(
            polish, "call_ollama", autospec=True,
            side_effect=AssertionError("Unexpected model call"),
        ))
        self.network = self.start_patch(patch.object(
            polish.request, "urlopen",
            side_effect=AssertionError("Network access is forbidden in these tests"),
        ))
        self.start_patch(patch.object(sys, "stdout", io.StringIO()))
        self.start_patch(patch.object(sys, "stderr", io.StringIO()))

    def start_patch(self, patcher):
        mocked = patcher.start()
        self.addCleanup(patcher.stop)
        return mocked

    def tearDown(self):
        self.network.assert_not_called()

    @staticmethod
    def make_record(uid):
        return {
            "uid": uid,
            "scene": "daily",
            "scene_zh": "日常生活",
            "micro": "waiting",
            "micro_zh": "等候",
            "zh": "请在这里等我。",
            "en": "Wait here for me please.",
            "pack": "core",
            "level": "A1",
            "tags": ["日常", "waiting"],
            "metadata": {"source": "原始数据", "reviewed": False, "order": 7},
        }

    @staticmethod
    def write_jsonl(path, records):
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )

    @staticmethod
    def read_jsonl(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    @staticmethod
    def write_mapping(path, mapping):
        path.write_text(json.dumps(mapping, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def make_patch(record):
        return {
            "uid": record["uid"], "scene": record["scene"], "zh": record["zh"],
            "micro": record["micro"], "old_en": record["en"],
            "new_en": "This is a resumed translation.", "changed": True,
            "model": "previous-model", "created_at": "2025-01-01T00:00:00+00:00",
            "metadata": {"note": "保留补丁", "revision": 3},
        }

    def allow_model(self):
        self.model.side_effect = None
        self.model.return_value = [{"id": 1, "en": self.MODEL_EN}]

    def run_scene(self, overrides):
        return polish.polish_scene(
            self.args, self.scene_path, self.out_dir, self.patch_dir, overrides,
        )

    def run_main(self, *options):
        argv = [
            "polish.py", "--out-dir", str(self.out_dir),
            "--patch-dir", str(self.patch_dir), "--pause", "0", "--retries", "0",
            *map(str, options),
        ]
        with patch.object(sys, "argv", argv):
            polish.main()

    def make_pack_dir(self):
        pack_dir = self.root / "data" / "packs" / "sentences"
        pack_dir.mkdir(parents=True)
        self.write_jsonl(pack_dir / self.scene_path.name, [self.record])
        return pack_dir


class PolishSceneOverridesTests(OverridesFixture):
    def test_overrides_beat_resumed_patches_and_stale_output(self):
        resumed = self.make_record("daily-002")
        raw_records = [self.record, resumed]
        self.write_jsonl(self.scene_path, raw_records)
        stale_records = [
            {**self.record, "en": "Stale approved English.",
             "metadata": {"note": "已保存的元数据", "revision": 9}},
            {**resumed, "en": "Stale resumed English."},
        ]
        self.write_jsonl(self.out_path, stale_records)
        patches = [self.make_patch(record) for record in raw_records]
        self.write_jsonl(self.patch_path, patches)
        patch_bytes = self.patch_path.read_bytes()
        raw_bytes = self.scene_path.read_bytes()

        self.run_scene({self.record["uid"]: self.APPROVED})

        self.assertEqual(self.read_jsonl(self.out_path), [
            {**stale_records[0], "en": self.APPROVED},
            {**stale_records[1], "en": patches[1]["new_en"]},
        ])
        self.assertEqual(self.patch_path.read_bytes(), patch_bytes)
        self.assertEqual(self.scene_path.read_bytes(), raw_bytes)
        self.model.assert_not_called()

    def test_reconstructs_raw_records_with_overrides_when_output_is_absent(self):
        resumed = self.make_record("daily-002")
        records = [self.record, resumed]
        self.write_jsonl(self.scene_path, records)
        patches = [self.make_patch(record) for record in records]
        self.write_jsonl(self.patch_path, patches)
        patch_bytes = self.patch_path.read_bytes()
        raw_bytes = self.scene_path.read_bytes()
        self.assertFalse(self.out_path.exists())

        self.run_scene({self.record["uid"]: self.APPROVED})

        self.assertEqual(self.read_jsonl(self.out_path), [
            {**self.record, "en": self.APPROVED},
            {**resumed, "en": patches[1]["new_en"]},
        ])
        self.assertEqual(self.patch_path.read_bytes(), patch_bytes)
        self.assertEqual(self.scene_path.read_bytes(), raw_bytes)
        self.model.assert_not_called()

    def test_approved_without_patches_are_written_exactly_and_other_scene_uids_ignored(self):
        approved = "Thanks."
        overrides = {self.record["uid"]: approved, "another-scene-001": "Not in this scene."}
        original_overrides = overrides.copy()
        raw_bytes = self.scene_path.read_bytes()

        self.run_scene(overrides)

        self.assertEqual(self.read_jsonl(self.out_path), [{**self.record, "en": approved}])
        self.assertEqual(overrides, original_overrides)
        self.assertEqual(self.scene_path.read_bytes(), raw_bytes)
        self.assertFalse(self.patch_path.exists())
        self.model.assert_not_called()

    def test_unapproved_records_still_reach_model_and_approved_do_not_consume_limit(self):
        pending = {
            **self.make_record("daily-002"), "zh": "能再说一遍吗？",
            "en": "Could you say that another time?",
        }
        self.write_jsonl(self.scene_path, [self.record, pending])
        raw_bytes = self.scene_path.read_bytes()
        self.args.limit = 1
        self.allow_model()

        self.run_scene({self.record["uid"]: self.APPROVED})

        self.model.assert_called_once()
        args, prompt = self.model.call_args.args
        self.assertIs(args, self.args)
        self.assertIn(pending["zh"], prompt)
        self.assertIn(pending["en"], prompt)
        self.assertNotIn(self.record["zh"], prompt)
        self.assertNotIn(self.record["en"], prompt)
        self.assertNotIn(self.APPROVED, prompt)
        self.assertEqual(self.read_jsonl(self.out_path), [
            {**self.record, "en": self.APPROVED}, {**pending, "en": self.MODEL_EN},
        ])
        patches = self.read_jsonl(self.patch_path)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["uid"], pending["uid"])
        self.assertEqual(patches[0]["old_en"], pending["en"])
        self.assertEqual(patches[0]["new_en"], self.MODEL_EN)
        self.assertEqual(self.scene_path.read_bytes(), raw_bytes)

    def test_rerun_is_idempotent_and_preserves_approved_patch_while_appending_others(self):
        pending = self.make_record("daily-002")
        self.write_jsonl(self.scene_path, [self.record, pending])
        approved_patch = self.make_patch(self.record)
        self.write_jsonl(self.patch_path, [approved_patch])
        approved_patch_bytes = self.patch_path.read_bytes()
        self.allow_model()
        overrides = {self.record["uid"]: self.APPROVED}

        self.run_scene(overrides)

        self.model.assert_called_once()
        self.assertEqual(self.read_jsonl(self.out_path), [
            {**self.record, "en": self.APPROVED}, {**pending, "en": self.MODEL_EN},
        ])
        patches = self.read_jsonl(self.patch_path)
        self.assertEqual([entry["uid"] for entry in patches], [self.record["uid"], pending["uid"]])
        self.assertEqual(patches[0], approved_patch)
        self.assertTrue(self.patch_path.read_bytes().startswith(approved_patch_bytes))
        output_bytes = self.out_path.read_bytes()
        patch_bytes = self.patch_path.read_bytes()
        self.model.reset_mock()
        self.model.side_effect = AssertionError("Rerun must not call the model")

        self.run_scene(overrides)

        self.model.assert_not_called()
        self.assertEqual(self.out_path.read_bytes(), output_bytes)
        self.assertEqual(self.patch_path.read_bytes(), patch_bytes)


class MainOverridesTests(OverridesFixture):
    def test_cli_parses_overrides_as_path(self):
        override_path = self.root / "alternate.json"
        with patch.object(sys, "argv", ["polish.py", "--overrides", str(override_path)]):
            args = polish.parse_args()
        self.assertIsInstance(args.overrides, Path)
        self.assertEqual(args.overrides, override_path)

    def test_default_mapping_applies_to_default_base_directory(self):
        self.write_mapping(self.default_overrides, {
            self.record["uid"]: self.APPROVED, "other-scene-001": "An unrelated translation.",
        })

        self.run_main()

        self.assertEqual(self.read_jsonl(self.out_path), [{**self.record, "en": self.APPROVED}])
        self.model.assert_not_called()

    def test_default_mapping_applies_when_data_directory_resolves_to_base(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: self.APPROVED})
        equivalent_path = self.data_dir / ".." / "sentences"

        self.run_main("--data-dir", equivalent_path)

        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.APPROVED)
        self.model.assert_not_called()

    def test_default_mapping_does_not_apply_to_packs(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: self.APPROVED})
        pack_dir = self.make_pack_dir()
        self.allow_model()

        self.run_main("--data-dir", pack_dir)

        self.model.assert_called_once()
        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.MODEL_EN)

    def test_malformed_default_mapping_is_not_read_for_packs(self):
        self.write_mapping(self.default_overrides, ["not a mapping"])
        pack_dir = self.make_pack_dir()
        self.allow_model()

        self.run_main("--data-dir", pack_dir)

        self.model.assert_called_once()
        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.MODEL_EN)

    def test_missing_default_file_is_allowed(self):
        self.assertFalse(self.default_overrides.exists())
        self.allow_model()

        self.run_main()

        self.model.assert_called_once()
        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.MODEL_EN)

    def test_explicit_alternate_path_takes_precedence_over_default(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: "Default English."})
        alternate = self.root / "alternate overrides.json"
        self.write_mapping(alternate, {self.record["uid"]: self.APPROVED})

        self.run_main("--overrides", alternate)

        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.APPROVED)
        self.model.assert_not_called()

    def test_explicit_mapping_can_be_used_for_packs(self):
        pack_dir = self.make_pack_dir()
        alternate = self.root / "alternate.json"
        self.write_mapping(alternate, {self.record["uid"]: self.APPROVED})

        self.run_main("--data-dir", pack_dir, "--overrides", alternate)

        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.APPROVED)
        self.model.assert_not_called()

    def test_explicit_empty_mapping_does_not_fall_back_to_default(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: self.APPROVED})
        alternate = self.root / "empty.json"
        self.write_mapping(alternate, {})
        self.allow_model()

        self.run_main("--overrides", alternate)

        self.model.assert_called_once()
        self.assertEqual(self.read_jsonl(self.out_path)[0]["en"], self.MODEL_EN)

    def test_explicit_missing_path_fails_without_fallback_or_requests(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: self.APPROVED})
        missing = self.root / "missing.json"
        self.assertFalse(missing.exists())

        with self.assertRaises((FileNotFoundError, SystemExit)):
            self.run_main("--overrides", missing)

        self.model.assert_not_called()
        self.assertFalse(self.out_path.exists())
        self.assertFalse(self.patch_path.exists())

    def test_malformed_explicit_mapping_is_rejected_before_requests(self):
        invalid_mappings = (
            [], ["uid"], None, "not a mapping", 42, False,
            {"": self.APPROVED}, {self.record["uid"]: ""},
            {self.record["uid"]: None}, {self.record["uid"]: 42},
            {self.record["uid"]: False}, {self.record["uid"]: [self.APPROVED]},
            {self.record["uid"]: {"en": self.APPROVED}},
            {self.record["uid"]: self.APPROVED, "other-scene-001": None},
        )
        alternate = self.root / "invalid.json"
        for mapping in invalid_mappings:
            with self.subTest(mapping=mapping):
                self.write_mapping(alternate, mapping)
                with self.assertRaises(SystemExit):
                    self.run_main("--overrides", alternate)
                self.model.assert_not_called()
                self.assertFalse(self.out_path.exists())
                self.assertFalse(self.patch_path.exists())

    def test_malformed_default_mapping_is_rejected_before_requests(self):
        self.write_mapping(self.default_overrides, {self.record["uid"]: None})

        with self.assertRaises(SystemExit):
            self.run_main()

        self.model.assert_not_called()
        self.assertFalse(self.out_path.exists())
        self.assertFalse(self.patch_path.exists())


if __name__ == "__main__":
    unittest.main()
