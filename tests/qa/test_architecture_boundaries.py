"""Adversarial tests of the architecture guard itself, independent of the app."""
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "qa"))
from architecture_audit import audit_tree


class ArchitectureGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.protocol = self.root / "protocol" / "src" / "caderno_protocol"
        self.viewer = self.root / "viewer" / "src" / "atlas_viewer"
        self.protocol.mkdir(parents=True)
        self.viewer.mkdir(parents=True)

    def audit(self):
        return audit_tree(self.root, [self.protocol], [self.viewer], {"atlas_viewer"})

    def test_allowed_direction_is_not_rejected(self):
        (self.viewer / "main.py").write_text("from caderno_protocol import read\n", encoding="utf-8")
        self.assertEqual([], self.audit())

    def test_private_dependency_hidden_in_helper_is_rejected(self):
        (self.viewer / "main.py").write_text("from . import helper\n", encoding="utf-8")
        (self.viewer / "helper.py").write_text("import r4.campaigns\n", encoding="utf-8")
        self.assertEqual("FORBIDDEN_IMPORT", self.audit()[0]["code"])

    def test_reverse_ui_dependency_is_rejected(self):
        (self.protocol / "read.py").write_text("from atlas_viewer.main import render\n", encoding="utf-8")
        self.assertEqual("FORBIDDEN_IMPORT", self.audit()[0]["code"])

    def test_literal_dynamic_import_is_rejected(self):
        (self.viewer / "main.py").write_text("import importlib\nx = importlib.import_module('r4.campaigns')\n", encoding="utf-8")
        self.assertEqual("FORBIDDEN_IMPORT", self.audit()[0]["code"])

    def test_process_execution_capability_is_rejected_in_viewer(self):
        (self.viewer / "main.py").write_text("import subprocess\n", encoding="utf-8")
        self.assertEqual("VIEWER_PROCESS_EXECUTION", self.audit()[0]["code"])

    def test_missing_package_does_not_vacuously_pass(self):
        self.protocol.rmdir()
        self.assertEqual("MISSING_PACKAGE", self.audit()[0]["code"])

    def test_distribution_dependency_is_rejected(self):
        (self.root / "viewer" / "pyproject.toml").write_text('[project]\nname = "atlas-viewer"\ndependencies = ["r4>=1"]\n', encoding="utf-8")
        self.assertEqual("FORBIDDEN_DEPENDENCY", self.audit()[0]["code"])

    def test_import_string_in_documentation_is_not_code(self):
        (self.viewer / "main.py").write_text('"""Never import r4.campaigns."""\n', encoding="utf-8")
        self.assertEqual([], self.audit())


if __name__ == "__main__":
    unittest.main()
