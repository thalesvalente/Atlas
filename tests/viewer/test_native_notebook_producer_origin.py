"""Synthetic checks: a selected producer must not import a different checkout.

These are origin checks for trusted producer code, not an OS sandbox guarantee.
Every import runs in a fresh process; fixtures contain no private producer code.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


class ProducerOriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="atlas-origin-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.code = self.root / "selected checkout"
        self.campaigns = self.code / "src/r4/campaigns"
        self.campaigns.mkdir(parents=True)
        self.notebook = self.root / "synthetic-notebook"
        self.notebook.mkdir()
        self.original = self.notebook / "original.txt"
        self.original.write_bytes(b"synthetic-source-must-not-change")
        self.marker = self.root / "unexpected-execution"
        self.output = self.root / "derived-package"

    def module(self, directory=None, *, marker=False, relative=False):
        directory = directory or self.campaigns
        directory.mkdir(parents=True, exist_ok=True)
        body = "from pathlib import Path\n"
        if marker:
            body += f"Path({str(self.marker)!r}).write_text('executed', encoding='utf-8')\n"
        projection = "def project(root):\n    return {'records': [{'id': 'synthetic-origin-record'}]}\n"
        if relative:
            (directory / "origin_fixture_support.py").write_text(projection, encoding="utf-8")
            body += "from .origin_fixture_support import project\n"
        else:
            body += projection
        target = directory / "notebook_query_projection.py"
        target.write_text(body, encoding="utf-8")
        return target

    def regular_packages(self, campaigns=None):
        campaigns = campaigns or self.campaigns
        for folder in (campaigns.parent, campaigns):
            (folder / "__init__.py").write_text("", encoding="utf-8")

    def link(self, destination, target, *, directory=False):
        try:
            destination.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest(f"This runner cannot create a synthetic symlink: {exc.__class__.__name__}")

    def invoke(self, *extra_paths):
        # Source-tree packages are explicit public test dependencies. The adapter
        # itself is an external checkout tool, never part of the viewer wheel.
        paths = [str(REPO / "packages/protocol/src"), str(REPO / "packages/atlas/src"),
                 *(str(p) for p in extra_paths)]
        argv = [str(REPO / "tools/export_native_notebook.py"),
                "--r4-code", str(self.code), "--notebook-root", str(self.notebook),
                "--output", str(self.output)]
        boot = ("import sys,runpy,json;sys.path[:0]=" + repr(paths)
                + ";sys.argv=" + repr(argv)
                + ";print(json.dumps({'producer_python_optimize':sys.flags.optimize}),file=sys.stderr)"
                + ";runpy.run_path(sys.argv[0],run_name='__main__')")
        # -I ignores PYTHONOPTIMIZE, so propagate and observe the flag explicitly.
        completed = subprocess.run([sys.executable, "-I", "-B", *(["-O"] * sys.flags.optimize), "-c", boot],
                                   capture_output=True, text=True, timeout=20,
                                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(json.loads(completed.stderr.splitlines()[0])["producer_python_optimize"],
                         sys.flags.optimize, completed.stderr)
        return completed

    def assert_blocked_before_execution(self, completed):
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        receipt = json.loads(completed.stderr.strip().splitlines()[-1])
        self.assertEqual(receipt["status"], "BLOCKED")
        self.assertFalse(self.marker.exists(), "Producer code ran before the origin gate rejected it")
        self.assertFalse(self.output.exists(), "Rejected producer must not publish a package")
        self.assertEqual(self.original.read_bytes(), b"synthetic-source-must-not-change")

    def test_regular_selected_producer_exports_without_changing_notebook(self):
        self.regular_packages()
        self.module(relative=True)
        completed = self.invoke()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "EXPORTED")
        self.assertEqual(self.original.read_bytes(), b"synthetic-source-must-not-change")

    def test_namespace_selected_producer_remains_supported(self):
        self.module(relative=True)
        completed = self.invoke()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue((self.output / "ro-crate-metadata.json").is_file())

    def test_terminal_module_symlink_is_rejected_before_execution(self):
        self.regular_packages()
        outside = self.module(self.root / "outside", marker=True)
        self.link(self.campaigns / outside.name, outside)
        self.assert_blocked_before_execution(self.invoke())

    def test_parent_initializer_symlink_is_rejected_before_execution(self):
        self.module()
        outside = self.root / "outside-init.py"
        outside.write_text(f"from pathlib import Path\nPath({str(self.marker)!r}).write_text('executed')\n",
                           encoding="utf-8")
        self.link(self.campaigns.parent / "__init__.py", outside)
        self.assert_blocked_before_execution(self.invoke())

    def test_producer_package_symlink_is_rejected_before_execution(self):
        self.campaigns.rmdir()
        outside = self.root / "outside-package"
        self.module(outside, marker=True)
        self.link(self.campaigns, outside, directory=True)
        self.assert_blocked_before_execution(self.invoke())

    def test_source_directory_symlink_is_rejected_before_execution(self):
        self.campaigns.rmdir()
        self.campaigns.parent.rmdir()
        (self.code / "src").rmdir()
        outside = self.root / "outside-src"
        self.module(outside / "r4/campaigns", marker=True)
        self.link(self.code / "src", outside, directory=True)
        self.assert_blocked_before_execution(self.invoke())

    def test_ambient_regular_package_cannot_shadow_selected_namespace(self):
        self.module()
        ambient = self.root / "ambient-site-packages"
        external = ambient / "r4/campaigns"
        self.module(external, marker=True)
        self.regular_packages(external)
        self.assert_blocked_before_execution(self.invoke(ambient))

    def test_missing_selected_module_does_not_run_parent_initializer(self):
        self.regular_packages()
        (self.campaigns.parent / "__init__.py").write_text(
            f"from pathlib import Path\nPath({str(self.marker)!r}).write_text('executed')\n",
            encoding="utf-8")
        self.assert_blocked_before_execution(self.invoke())


if __name__ == "__main__":
    unittest.main()
