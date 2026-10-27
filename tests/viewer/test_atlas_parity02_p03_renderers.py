"""Make actual Node behavior/DOM-contract tests discoverable by the Python suite."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RendererBehaviorTests(unittest.TestCase):
    def run_node(self, script, count):
        node = shutil.which("node")
        self.assertIsNotNone(node, "P03 behavior tests require Node.js 24 or later")
        result = subprocess.run([node, "--test-reporter=tap", f"scripts/qa/{script}"],
                                cwd=ROOT, text=True, capture_output=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"# tests {count}", result.stdout)
        self.assertIn("# fail 0", result.stdout)
        self.assertIn("# skipped 0", result.stdout)

    def test_metadata_javascript_behavior(self):
        self.run_node("atlas_parity02_p03_artifacts_test.mjs", 14)

    def test_real_renderers_with_dom_recorder_not_browser(self):
        self.run_node("atlas_parity02_p03_dom_test.mjs", 6)


if __name__ == "__main__":
    unittest.main()
