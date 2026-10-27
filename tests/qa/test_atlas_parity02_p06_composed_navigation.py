"""Compose P06 package-replacement expectations with P02 snapshot-bound state.

The real installed JS asset is executed by Node. This is a pure-state regression,
not evidence of a browser or user-host execution.
"""
from importlib.resources import files
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ComposedNavigationTests(unittest.TestCase):
    def test_replaced_snapshot_discards_stale_selection_and_requires_explicit_new_selection(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required; absence is a failure, not a skip")
        asset = files("atlas_viewer").joinpath("static", "parity02_p02_state.js")
        result = subprocess.run(
            [node, str(ROOT / "scripts/qa/atlas_parity02_p06_composed_state_tests.mjs"),
             "--asset", str(asset)], check=False, capture_output=True, text=True,
            encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "PASS_SCOPED")
        self.assertEqual(len(report["checks"]), 4)
        self.assertTrue(all(check["status"] == "PASS" for check in report["checks"]))
        self.assertIn("NOT a browser run", report["scope"])


if __name__ == "__main__":
    unittest.main()
