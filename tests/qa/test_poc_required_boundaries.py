"""Independent, bounded cases missing from the PoC's baseline regressions.

Only the existing public environmental fixture is used. No new producer,
profile change, private source or unbounded archive is introduced.
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from caderno_protocol import load_package, to_read_model, validate_document


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "poc_existing_environmental_fixture", ROOT / "examples/environmental/export.py"
)
EXPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORTER)


class PocRequiredBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.document, _ = EXPORTER.build_document()

    def test_missing_or_invalid_entity_ids_return_explicit_errors(self):
        invalid_ids = [None, False, 7, [], {}, "", "invalid\x00identifier"]
        for identifier in invalid_ids:
            with self.subTest(identifier=identifier):
                document = deepcopy(self.document)
                entity = {"@type": "CreativeWork", "name": "Invalid ID fixture"}
                if identifier is not None:
                    entity["@id"] = identifier
                document["@graph"].append(entity)
                before = deepcopy(document)
                report = validate_document(document)
                self.assertFalse(report.valid)
                self.assertIn("ENTITY_ID", {issue.code for issue in report.errors})
                self.assertEqual(document, before)

    def test_invalid_entity_types_return_explicit_errors(self):
        for entity_type in [None, False, 7, {}, [], "", ["CreativeWork", 7]]:
            with self.subTest(entity_type=entity_type):
                document = deepcopy(self.document)
                document["@graph"].append({
                    "@id": "urn:atlas:public-poc:invalid-type",
                    "@type": entity_type,
                    "name": "Invalid type fixture",
                })
                before = deepcopy(document)
                report = validate_document(document)
                self.assertFalse(report.valid)
                self.assertIn("ENTITY_TYPE", {issue.code for issue in report.errors})
                self.assertEqual(document, before)

    def test_controlled_zip_bomb_is_rejected_before_any_member_is_opened(self):
        # 64 KiB expanded is sufficient to exceed the documented ratio of 200.
        # The archive is tiny, local and synthetic; no destructive payload exists.
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = EXPORTER.export(base / "environmental")
            archive = base / "bounded-ratio.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as stream:
                stream.write(source / "ro-crate-metadata.json", "ro-crate-metadata.json")
                stream.writestr("data/bounded-repetition.bin", b"0" * (64 * 1024))
            with zipfile.ZipFile(archive) as stream:
                info = stream.getinfo("data/bounded-repetition.bin")
            self.assertGreater(info.file_size / info.compress_size, 200)
            self.assertLess(archive.stat().st_size, 16 * 1024)
            before = archive.read_bytes()
            with patch.object(zipfile.ZipFile, "open", side_effect=AssertionError(
                "Unsafe archive must be rejected before metadata/payload decompression"
            )):
                package = load_package(archive)
            self.assertFalse(package.report.valid)
            self.assertIn("SOURCE_UNSAFE", {issue.code for issue in package.report.errors})
            self.assertEqual({}, package.document)
            self.assertEqual([], to_read_model(package)["runs"])
            self.assertEqual(archive.read_bytes(), before)
            self.assertFalse((base / "data").exists())
            self.assertTrue(load_package(source).report.valid)


if __name__ == "__main__":
    unittest.main()
