"""Synthetic subprocess contracts for the external producer-only adapter.

The installed viewer does not load R4. Only the explicitly selected external
adapter is allowed to load the producer query API; legacy rendering is forbidden.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from atlas_viewer.native_notebook import read_source

ROOT = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


class ProducerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.code = self.root / "producer code"
        self.notebook = self.root / "synthetic notebook"
        self.notebook.mkdir()
        self.module = self.code / "src/r4/campaigns"
        self.module.mkdir(parents=True)
        for path in (self.module.parent, self.module):
            (path / "__init__.py").write_text("", encoding="utf-8")
        self.marker = self.root / "legacy-renderer-was-loaded"
        (self.module / "atlas.py").write_text(
            "from pathlib import Path\n"
            f"Path({str(self.marker)!r}).write_text('forbidden')\n"
            "raise RuntimeError('LEGACY_RENDERER_MUST_NOT_LOAD')\n",
            encoding="utf-8",
        )
        self.data = {"records": [{"id": "invented", "status": "HOLD"}],
                     "atlas_integration": {"notebook_revision": "synthetic-boundary-v1"}}
        self.source = self.notebook / "fixture.json"
        self.source.write_text(json.dumps(self.data), encoding="utf-8")

    def invoke(self):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "tools/export_native_notebook.py"),
             "--r4-code", str(self.code), "--notebook-root", str(self.notebook),
             "--output", str(self.root / "package")],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )

    def test_selected_producer_only_api_exports_without_importing_legacy_renderer(self):
        (self.module / "notebook_query_projection.py").write_text(
            "import json, sys\n"
            "def project(root):\n"
            "    if 'r4.campaigns.atlas' in sys.modules:\n"
            "        raise RuntimeError('LEGACY_RENDERER_LOADED')\n"
            "    return json.loads((root / 'fixture.json').read_text(encoding='utf-8'))\n",
            encoding="utf-8",
        )
        before = self.source.read_bytes()
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "EXPORTED")
        state, raw = read_source(self.root / "package", "invented")
        self.assertEqual(state["status"], "READY", state)
        self.assertEqual(json.loads(raw), self.data)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse(self.marker.exists())

    def test_renderer_only_checkout_is_refused_without_importing_the_renderer(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stderr)["status"], "BLOCKED")
        self.assertIn("notebook_query_projection", json.loads(result.stderr)["error"])
        self.assertFalse(self.marker.exists())
        self.assertFalse((self.root / "package").exists())

    def test_producer_error_is_propagated_without_publishing_package(self):
        (self.module / "notebook_query_projection.py").write_text(
            "def project(root):\n    raise ValueError('SYNTHETIC_PRODUCER_ERROR')\n",
            encoding="utf-8",
        )
        result = self.invoke()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stderr)["error"], "SYNTHETIC_PRODUCER_ERROR")
        self.assertFalse(self.marker.exists())
        self.assertFalse((self.root / "package").exists())


if __name__ == "__main__":
    unittest.main()
