"""Expose A01's actual JavaScript regressions to the existing cross-OS discovery."""
from pathlib import Path
import shutil
import subprocess
import unittest


class A01PresentationRegressionTests(unittest.TestCase):
    def test_actual_javascript_regressions(self):
        root = Path(__file__).resolve().parents[2]
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required by the existing presentation development suite")
        result = subprocess.run(
            [node, "--test", "--test-reporter=tap", str(root / "scripts/qa/test_native_a01_fix.mjs")],
            cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# fail 0", result.stdout)
        self.assertIn("# skipped 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
