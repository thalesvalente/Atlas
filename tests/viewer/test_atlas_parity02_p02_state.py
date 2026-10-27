"""Run behavioral URL/filter tests on the installed JavaScript asset using Node.

This is discoverable by scripts/run_checks.py; it does not claim browser coverage.
"""
from __future__ import annotations

from importlib.resources import files
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from atlas_viewer.catalog import Catalog

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


class P02StateTests(unittest.TestCase):
    def test_snapshot_bound_hash_filters_selection_and_deterministic_order(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node unavailable; pure JS state checks not executed")
        fixtures = REPO / "tests/fixtures/atlas_parity02/p02"
        catalog = Catalog([fixtures / "source-a", fixtures / "source-b"]).snapshot()
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "catalog.json"
            data.write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([
                node, str(REPO / "scripts/qa/atlas_parity02_p02_state_tests.mjs"),
                "--asset", str(files("atlas_viewer").joinpath("static", "parity02_p02_state.js")),
                "--catalog", str(data),
            ], cwd=directory, text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertGreaterEqual(report["total"], 20)
        self.assertFalse(report["browser_executed"])


if __name__ == "__main__":
    unittest.main()
