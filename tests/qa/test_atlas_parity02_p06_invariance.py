"""Counterexamples for the frozen public protocol and source-byte boundary."""
from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "parity02_p06_audit", ROOT / "scripts/qa/atlas_parity02_p06_audit.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class FrozenInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.originals = (
            "packages/protocol/src/caderno_protocol/read_model.py",
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            "examples/environmental/sample/ro-crate-metadata.json",
            "docs/architecture/ADR-0002-protocol-candidate.md",
            ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
        )
        for name in self.originals:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic frozen bytes\n")
        (self.root / ".gitignore").write_text("__pycache__/\n*.egg-info/\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic QA", "-c",
                 "user.email=qa@example.invalid", "-c", "commit.gpgsign=false",
                 "commit", "-qm", "Baseline sintética")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def report(self):
        return AUDIT.audit(self.root, self.base)

    def test_unchanged_inputs_pass_and_report_actual_commit_and_tree(self):
        report = self.report()
        self.assertEqual(report["status"], "PASS_SCOPED")
        self.assertEqual(report["protected_files"], len(self.originals))
        self.assertEqual(report["tested_sha"], self.base)
        self.assertEqual(report["tested_tree"], self.git("rev-parse", "HEAD^{tree}").strip())
        self.assertEqual(set(report["baseline_sha256"]), set(self.originals))

    def test_each_protected_area_rejects_a_material_byte_change(self):
        for name in self.originals:
            with self.subTest(path=name):
                path = self.root / name
                before = path.read_bytes()
                path.write_bytes(before + b"unauthorized delta")
                self.assertEqual(self.report()["errors"],
                                 [{"path": name, "reason": "BYTES_CHANGED"}])
                path.write_bytes(before)

    def test_protocol_deletion_is_not_an_allowed_presentation_change(self):
        name = self.originals[0]
        (self.root / name).unlink()
        self.assertIn({"path": name, "reason": "MISSING_OR_NONREGULAR"},
                      self.report()["errors"])

    def test_added_untracked_protocol_code_is_rejected(self):
        name = "packages/protocol/src/caderno_protocol/new_loader.py"
        (self.root / name).write_bytes(b"unapproved loader\n")
        self.assertIn({"path": name, "reason": "UNEXPECTED_PROTECTED_FILE"},
                      self.report()["errors"])

    def test_component_output_and_python_cache_do_not_masquerade_as_inputs(self):
        path = self.root / "packages/atlas/src/atlas_viewer/static/component.js"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"synthetic component\n")
        cache = self.root / "packages/protocol/src/caderno_protocol/__pycache__"
        cache.mkdir()
        (cache / "read_model.cpython-312.pyc").write_bytes(b"generated cache")
        self.assertEqual(self.report()["errors"], [])


if __name__ == "__main__":
    unittest.main()
