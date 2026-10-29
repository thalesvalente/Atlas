"""Regression probes for C4's exact-hash opt-in; historical gates remain strict."""
from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("c4_speckit_audit", ROOT / "scripts/qa/speckit_audit.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class C4ExactAuditTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.protected = {
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
            "docs/architecture/ADR-0002-protocol-candidate.md",
        }
        self.sibling = "packages/atlas/src/atlas_viewer/static/unlisted.js"
        self.names = set(AUDIT.P03_C4_ORIGINALS)
        for name in self.names | AUDIT.PRESENTATION_ORIGINALS | self.protected | {self.sibling}:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("synthetic baseline\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.commit("Baseline sintética")
        self.baseline = self.git("rev-parse", "HEAD").strip()
        for name in self.names:
            (self.root / name).write_text("frozen P02 " + name + "\n", encoding="utf-8")
        self.commit("P02 sintético congelado")
        self.p02 = self.git("rev-parse", "HEAD").strip()
        for name in self.names:
            (self.root / name).write_text("authorized C4 " + name + "\n", encoding="utf-8")
        self.pins = {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest() for name in self.names}

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def commit(self, message):
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic C4 audit", "-c", "user.email=c4-audit@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", message)

    def report(self, *, presentation=False, p02=False, c4=False):
        with patch.object(AUDIT, "BASELINE", self.baseline), \
             patch.object(AUDIT, "P02_PROTOCOL_BASELINE", self.baseline), \
             patch.object(AUDIT, "P02_CODE_SHA", self.p02), \
             patch.object(AUDIT, "P03_C4_ORIGINALS", self.pins):
            return AUDIT.audit_baseline(self.root, allow_presentation_delta=presentation,
                allow_p02_c0_delta=p02, allow_p03_c4_delta=c4)

    def test_default_and_previous_opt_ins_reject_C4_runtime_bytes(self):
        for options in ({}, {"presentation": True}, {"presentation": True, "p02": True}):
            report = self.report(**options)
            self.assertTrue(report["errors"])
            self.assertEqual(report["authorized_p03_c4_changes"], [])
            self.assertIsNone(report["p03_c4_authorization"])

    def test_C4_accepts_only_explicit_three_hashes_and_freezes_protocol(self):
        report = self.report(c4=True)
        self.assertEqual(report["errors"], [])
        self.assertEqual(set(report["authorized_p03_c4_changes"]), self.names)
        self.assertEqual(report["p03_c4_authorization"]["exact_paths_sha256"], self.pins)
        self.assertEqual(report["protocol_invariance"]["baseline_sha"], self.baseline)

    def test_named_paths_cannot_use_arbitrary_bytes_or_old_P02_bytes(self):
        for name in self.names:
            target = self.root / name
            original = target.read_bytes()
            for replacement in (b"arbitrary delta\n", ("frozen P02 " + name + "\n").encode()):
                target.write_bytes(replacement)
                report = self.report(c4=True)
                self.assertIn("Frozen C4 presentation changed: " + name, report["errors"])
                self.assertNotIn(name, report["authorized_p03_c4_changes"])
            target.write_bytes(original)

    def test_C4_named_path_cannot_be_deleted_or_a_directory(self):
        name = sorted(self.names)[0]
        target = self.root / name
        target.unlink()
        self.assertIn("Frozen C4 presentation changed: " + name, self.report(c4=True)["errors"])
        target.mkdir()
        self.assertIn("Frozen C4 presentation changed: " + name, self.report(c4=True)["errors"])

    def test_C4_does_not_grant_historical_presentation_or_sibling_edits(self):
        for name in (self.sibling, "packages/atlas/src/atlas_viewer/static/app.js"):
            target = self.root / name
            original = target.read_bytes()
            target.write_text("unlisted edit\n", encoding="utf-8")
            self.assertIn("Preserved baseline changed: " + name, self.report(c4=True)["errors"])
            target.write_bytes(original)

    def test_C4_still_rejects_governance_and_protocol_even_with_presentation_flag(self):
        for name in self.protected | {"packages/protocol/src/caderno_protocol/read_model.py"}:
            target = self.root / name
            original = target.read_bytes()
            target.write_text("unauthorized edit\n", encoding="utf-8")
            report = self.report(c4=True, presentation=True)
            self.assertTrue(report["errors"])
            if name.startswith("packages/protocol/"):
                self.assertIn("Frozen C1 protocol changed: " + name, report["errors"])
            else:
                self.assertIn("Preserved baseline changed: " + name, report["errors"])
            target.write_bytes(original)

    def test_C4_cli_has_no_hash_path_or_baseline_override(self):
        parser = AUDIT.build_parser()
        self.assertFalse(parser.parse_args([]).allow_p03_c4_delta)
        for option in ("--allow-path", "--exclude", "--baseline", "--hash"):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parser.parse_args(["--allow-p03-c4-delta", option, self.sibling])


if __name__ == "__main__":
    unittest.main()

