"""Run the isolated candidate's Node behavior suite; this is not browser QA."""
from pathlib import Path
import shutil
import subprocess
import unittest


class TableBehaviorTests(unittest.TestCase):
    def test_candidate_table_behavior_suite(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is required for P03 table behavior tests")
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [node, "--test-reporter=tap", "scripts/qa/atlas_parity02_p03_table_test.mjs"],
            cwd=root, text=True, capture_output=True, timeout=60, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# tests 42", result.stdout)
        self.assertIn("# fail 0", result.stdout)
        self.assertIn("# skipped 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
