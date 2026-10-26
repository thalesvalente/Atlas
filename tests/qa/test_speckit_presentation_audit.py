"""Keep the feature's narrow audit opt-in from weakening protected contracts."""
from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("speckit_audit", ROOT / "scripts/qa/speckit_audit.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class PresentationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.protected = (
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            "docs/architecture/ADR-0002-protocol-candidate.md",
            ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
        )
        for name in AUDIT.PRESENTATION_ORIGINALS | set(self.protected):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic baseline\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic audit", "-c", "user.email=audit@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic baseline")
        self.baseline = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def report(self, enabled=False):
        with patch.object(AUDIT, "BASELINE", self.baseline):
            return AUDIT.audit_baseline(self.root, allow_presentation_delta=enabled)

    def test_default_still_rejects_authorized_runtime_edits(self):
        name = "packages/protocol/src/caderno_protocol/read_model.py"
        (self.root / name).write_text("synthetic delta\n", encoding="utf-8")
        self.assertEqual(self.report()["errors"], [f"Preserved baseline changed: {name}"])
        self.assertEqual(self.report()["authorized_presentation_changes"], [])

    def test_opt_in_is_explicit_and_records_exact_changed_paths(self):
        for name in AUDIT.PRESENTATION_ORIGINALS:
            (self.root / name).write_text("synthetic presentation delta\n", encoding="utf-8")
        report = self.report(True)
        self.assertEqual(report["errors"], [])
        self.assertEqual(set(report["authorized_presentation_changes"]), AUDIT.PRESENTATION_ORIGINALS)
        self.assertEqual(len(self.report()["errors"]), len(AUDIT.PRESENTATION_ORIGINALS))

    def test_opt_in_does_not_allow_contract_governance_or_skill_edits(self):
        for name in self.protected:
            (self.root / name).write_text("unauthorized synthetic change\n", encoding="utf-8")
        errors = self.report(True)["errors"]
        self.assertEqual(set(errors), {f"Preserved baseline changed: {name}" for name in self.protected})

    def test_opt_in_does_not_allow_deleting_a_presentation_file(self):
        name = "packages/atlas/src/atlas_viewer/static/app.js"
        (self.root / name).unlink()
        self.assertIn(f"Preserved baseline changed: {name}", self.report(True)["errors"])


if __name__ == "__main__":
    unittest.main()
