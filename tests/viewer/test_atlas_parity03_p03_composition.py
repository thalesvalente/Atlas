"""C4 runtime integration behavior, discovered from the installed viewer suite."""
from __future__ import annotations

from importlib.resources import files
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from atlas_viewer.catalog import Catalog
from atlas_viewer.parity02_p03_metadata import MetadataError

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))
SAMPLE = REPO / "examples/environmental/sample"


class P03CompositionTests(unittest.TestCase):
    def test_metadata_identity_binds_source_and_snapshot_without_collapsing_duplicate_ids(self):
        catalog = Catalog([SAMPLE, SAMPLE])
        sources = catalog.snapshot(check_changes=False)["sources"]
        descriptors = [source["presentation"]["metadata"] for source in sources]
        self.assertTrue(all(source["report"]["valid"] for source in sources))
        self.assertTrue(all(not source["presentation"]["errors"] for source in sources))
        self.assertNotEqual(descriptors[0]["source"]["key"], descriptors[1]["source"]["key"])
        self.assertEqual(sources[0]["snapshot_id"], sources[1]["snapshot_id"])
        for source, descriptor in zip(sources, descriptors):
            self.assertEqual(json.loads(descriptor["source"]["key"]), [source["id"], source["snapshot_id"]])
            self.assertTrue(descriptor["items"])
            self.assertTrue(all(item["identity"]["source_key"] == descriptor["source"]["key"] for item in descriptor["items"]))

    def test_metadata_presentation_error_keeps_valid_source_runs_and_dossier(self):
        baseline = Catalog([SAMPLE]).snapshot(check_changes=False)["sources"][0]
        with patch("atlas_viewer.catalog.project_metadata", side_effect=MetadataError("LIMIT", "items")):
            catalog = Catalog([SAMPLE])
        source = catalog.snapshot(check_changes=False)["sources"][0]
        self.assertEqual(source["status"], "READY")
        self.assertEqual(source["report"], baseline["report"])
        self.assertEqual(source["read_model"], baseline["read_model"])
        self.assertEqual(source["snapshot_id"], baseline["snapshot_id"])
        self.assertIsNone(source["presentation"]["metadata"])
        self.assertEqual(source["presentation"]["errors"], [{"component": "metadata", "code": "LIMIT", "path": "items"}])
        self.assertEqual(catalog.dossier()["sources"][0]["read_model"], baseline["read_model"])

    def test_unavailable_source_has_no_fabricated_presentation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Catalog([Path(directory) / "absent"]).snapshot(check_changes=False)["sources"][0]
        self.assertIsNone(source["read_model"])
        self.assertEqual(source["presentation"], {"metadata": None, "errors": []})

    def test_typed_selection_identity_lifecycle_and_visible_errors_in_installed_module(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node 24 is required; this gate must not skip.")
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([
                node, str(REPO / "tests/viewer/atlas_parity03_p03_composition_cases.mjs"),
                "--module", str(files("atlas_viewer").joinpath("static", "parity03_p03_composition.js")),
            ], cwd=directory, text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "PASS")
        self.assertGreaterEqual(receipt["cases"], 9)
        self.assertFalse(receipt["browser_executed"])


if __name__ == "__main__":
    unittest.main()
