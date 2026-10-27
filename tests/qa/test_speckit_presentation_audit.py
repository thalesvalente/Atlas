"""Keep the feature's narrow audit opt-in from weakening protected contracts."""
from pathlib import Path
from contextlib import redirect_stderr
import io
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


class P02C0AuditTests(unittest.TestCase):
    """Real Git snapshots exercise explicit authorization and frozen bytes."""

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
        self.sibling = "packages/atlas/src/atlas_viewer/static/unlisted.js"
        names = (AUDIT.PRESENTATION_ORIGINALS | AUDIT.P02_C0_ORIGINALS
                 | set(self.protected) | {self.sibling})
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic baseline\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.commit("Synthetic baseline")
        self.baseline = self.git("rev-parse", "HEAD").strip()
        for name in AUDIT.P02_C0_ORIGINALS:
            (self.root / name).write_text(f"frozen P02 delta for {name}\n", encoding="utf-8")
        self.commit("Synthetic frozen P02")
        self.code_sha = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def commit(self, message):
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic audit", "-c", "user.email=audit@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", message)

    def report(self, *, presentation=False, p02=False):
        with patch.object(AUDIT, "BASELINE", self.baseline), \
             patch.object(AUDIT, "P02_PROTOCOL_BASELINE", self.baseline), \
             patch.object(AUDIT, "P02_CODE_SHA", self.code_sha):
            return AUDIT.audit_baseline(self.root, allow_presentation_delta=presentation,
                                        allow_p02_c0_delta=p02)

    def test_default_and_historical_opt_in_reject_all_three_p02_paths(self):
        expected = {f"Preserved baseline changed: {name}" for name in AUDIT.P02_C0_ORIGINALS}
        for presentation in (False, True):
            report = self.report(presentation=presentation)
            self.assertEqual(set(report["errors"]), expected)
            self.assertEqual(report["authorized_p02_c0_changes"], [])
            self.assertIsNone(report["p02_c0_authorization"])

    def test_p02_opt_in_records_only_exact_frozen_paths(self):
        report = self.report(presentation=True, p02=True)
        self.assertEqual(report["errors"], [])
        self.assertEqual(set(report["authorized_p02_c0_changes"]), AUDIT.P02_C0_ORIGINALS)
        authorization = report["p02_c0_authorization"]
        self.assertEqual(authorization["frozen_code_sha"], self.code_sha)
        self.assertEqual(set(authorization["exact_paths_sha256"]), AUDIT.P02_C0_ORIGINALS)
        self.assertEqual(report["protocol_invariance"]["baseline_sha"], self.baseline)
        self.assertEqual(report["protocol_invariance"]["preserved_files"], 2)

    def test_p02_opt_in_does_not_implicitly_grant_historical_allowance(self):
        name = "packages/atlas/src/atlas_viewer/static/app.js"
        (self.root / name).write_text("historical presentation delta\n", encoding="utf-8")
        self.assertIn(f"Preserved baseline changed: {name}", self.report(p02=True)["errors"])
        self.assertEqual(self.report(presentation=True, p02=True)["errors"], [])

    def test_p02_named_path_with_unfrozen_bytes_is_rejected(self):
        for name in sorted(AUDIT.P02_C0_ORIGINALS):
            path = self.root / name
            original = path.read_bytes()
            path.write_text("arbitrary runtime delta\n", encoding="utf-8")
            report = self.report(presentation=True, p02=True)
            self.assertIn(f"Preserved baseline changed: {name}", report["errors"])
            self.assertNotIn(name, report["authorized_p02_c0_changes"])
            path.write_bytes(original)

    def test_p02_cannot_be_rolled_back_to_historical_bytes(self):
        name = "packages/atlas/src/atlas_viewer/catalog.py"
        (self.root / name).write_text("synthetic baseline\n", encoding="utf-8")
        self.assertIn(f"Frozen P02 input changed: {name}",
                      self.report(presentation=True, p02=True)["errors"])

    def test_p02_named_paths_cannot_be_deleted_or_replaced_by_directories(self):
        name = "packages/atlas/src/atlas_viewer/catalog.py"
        path = self.root / name
        path.unlink()
        self.assertIn(f"Preserved baseline changed: {name}",
                      self.report(presentation=True, p02=True)["errors"])
        path.mkdir()
        self.assertIn(f"Preserved baseline changed: {name}",
                      self.report(presentation=True, p02=True)["errors"])

    def test_p02_does_not_grant_a_directory_exception(self):
        (self.root / self.sibling).write_text("unauthorized sibling delta\n", encoding="utf-8")
        self.assertIn(f"Preserved baseline changed: {self.sibling}",
                      self.report(presentation=True, p02=True)["errors"])

    def test_both_opt_ins_still_reject_governance_protocol_and_skills(self):
        for name in self.protected:
            (self.root / name).write_text("unauthorized protected delta\n", encoding="utf-8")
        errors = self.report(presentation=True, p02=True)["errors"]
        for name in self.protected:
            self.assertIn(f"Preserved baseline changed: {name}", errors)

    def test_current_protocol_pin_overrides_historical_read_model_allowance(self):
        name = "packages/protocol/src/caderno_protocol/read_model.py"
        (self.root / name).write_text("unauthorized protocol delta\n", encoding="utf-8")
        self.assertIn(f"Frozen C1 protocol changed: {name}",
                      self.report(presentation=True, p02=True)["errors"])

    def test_protocol_additions_and_deletions_are_rejected(self):
        removed = self.protected[0]
        (self.root / removed).unlink()
        added = "packages/protocol/unlisted.txt"
        (self.root / added).write_text("unexpected protocol addition\n", encoding="utf-8")
        errors = self.report(presentation=True, p02=True)["errors"]
        self.assertIn(f"Frozen C1 protocol changed: {removed}", errors)
        self.assertIn(f"Unexpected C1 protocol file: {added}", errors)

    def test_cli_has_no_path_exclusion_or_baseline_override(self):
        parser = AUDIT.build_parser()
        args = parser.parse_args([])
        self.assertFalse(args.allow_presentation_delta)
        self.assertFalse(args.allow_p02_c0_delta)
        for forbidden in ("--exclude", "--allow-path", "--baseline"):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                parser.parse_args(["--allow-p02-c0-delta", forbidden, self.sibling])
            self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
