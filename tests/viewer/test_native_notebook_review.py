"""Regression counterexamples from independent native implementation review."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest

from atlas_viewer.catalog import Catalog
from atlas_viewer.native_notebook import snapshot, read_source, export_source, NativeViewError

ROOT = Path(__file__).resolve().parents[2]
EXPORTER = runpy.run_path(str(ROOT / "tools/export_native_notebook.py"))


class NativeReviewTests(unittest.TestCase):
    def test_explicit_null_identity_is_not_a_structural_id(self):
        data = {"records": [{"id": "structural-1", "native_id": None}, {"id": "record-2"}]}
        entries = EXPORTER["project_to_entries"](data)
        records = [e for e in entries if e["kind"] == "record"]
        self.assertIsNone(records[0]["native_id"])
        self.assertEqual(records[0]["source_key"], "structural-1")
        self.assertIsNone(json.loads(records[0]["raw_json"])["native_id"])
        self.assertEqual(records[1]["native_id"], "record-2")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "crate"
            EXPORTER["export"](data, output)
            self.assertEqual(read_source(output, "source")[0]["status"], "READY")

    def test_changed_valid_package_requires_explicit_catalog_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "crate"
            EXPORTER["export"]({"records": [{"id": "initial"}]}, output)
            catalog = Catalog([output])
            initial = snapshot(catalog)["sources"][0]
            self.assertEqual(initial["status"], "READY")
            doc, payloads = EXPORTER["build_package"]({"records": [{"id": "replacement"}]})
            for name, raw in payloads.items(): (output / name).write_bytes(raw)
            (output / "ro-crate-metadata.json").write_bytes(EXPORTER["dump"](doc))
            self.assertEqual(catalog.snapshot()["sources"][0]["status"], "CHANGED")
            native = snapshot(catalog)["sources"][0]
            self.assertEqual(native["status"], "CHANGED")
            self.assertEqual(native["entries"], [])
            with self.assertRaises(NativeViewError):
                export_source(catalog, "source-1", initial["metadata_sha256"])
            catalog.rebuild()
            current = snapshot(catalog)["sources"][0]
            self.assertEqual(current["status"], "READY")
            self.assertIn('"replacement"', export_source(catalog, "source-1", current["metadata_sha256"]).decode())

    def test_display_values_cannot_disagree_with_digest_valid_original(self):
        data = {"records": [{"id": "structural", "native_id": None, "title": "Unchanged"}]}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "crate"
            EXPORTER["export"](data, output)
            payload = output / "data/view-0000.json"
            chunk = json.loads(payload.read_bytes())
            entry = next(e for e in chunk["entries"] if e["kind"] == "record")
            entry["native_id"] = "FORGED"
            raw = EXPORTER["dump"](chunk)
            payload.write_bytes(raw)
            meta = output / "ro-crate-metadata.json"
            document = json.loads(meta.read_bytes())
            file = next(e for e in document["@graph"] if e["@id"] == "data/view-0000.json")
            file["cp:sha256"] = hashlib.sha256(raw).hexdigest()
            file["contentSize"] = len(raw)
            meta.write_bytes(EXPORTER["dump"](document))
            result, original = read_source(output, "selected")
            self.assertEqual(result["status"], "INVALID")
            self.assertIn("NATIVE_DISPLAY_VALUE_MISMATCH", result["errors"])
            self.assertIsNone(original)


if __name__ == "__main__":
    unittest.main()
