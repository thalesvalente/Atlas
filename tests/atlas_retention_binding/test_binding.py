"""End-to-end cases for the local CLI. All payload files are synthetic."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

REPO = Path(__file__).resolve().parents[2]
EXPORTED = REPO / "specs/005-experiment-triage/examples/retention-plan.synthetic.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def rows_digest(table):
    return sha(wire([[row["uid"], row["ordinal"], row["raw_json"]] for row in table["rows"]]))


class BindingTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        self.root = self.temp / "corpus"
        self.root.mkdir()
        self.backup_root = self.temp / "backup"
        self.backup_root.mkdir()
        self.plan_bytes = EXPORTED.read_bytes()
        self.plan = json.loads(self.plan_bytes)
        self.plan_path = self.temp / "plan.json"
        self.plan_path.write_bytes(self.plan_bytes)
        self.manifest_path = self.temp / "inventory.json"
        self.inventory = {
            "schema": "atlas-retention-inventory/1",
            "source": {key: self.plan["source"][key] for key in ("id", "revision", "metadata_sha256")},
            "parent_sha256": None,
            "provenance": {"producer": "fixture", "evidence": "synthetic-attestation"},
            "dependency_scope": "COMPLETE",
            "files": [],
            "bindings": [],
            "backups": [],
        }
        for i, item in enumerate(self.plan["items"]):
            data = ("invented payload " + str(i)).encode("ascii")
            name = f"data-{i}.bin"
            (self.root / name).write_bytes(data)
            self.inventory["files"].append({
                "id": f"file-{i}", "root": "corpus", "path": name,
                "bytes": len(data), "sha256": sha(data),
            })
            identity = item["identity"]
            binding = {
                "uid": identity["uid"], "dto_kind": identity["dto_kind"],
                "raw_sha256": sha(item["raw_json"].encode("utf-8")),
                "coverage": "COMPLETE", "files": [f"file-{i}"],
            }
            if "source_key" in identity:
                binding["source_key"] = identity["source_key"]
            if "table_rows" in item:
                binding["table_rows_sha256"] = rows_digest(item["table_rows"])
            self.inventory["bindings"].append(binding)

    def save_plan(self):
        self.plan_path.write_bytes(wire(self.plan))

    def run_binding(self, *, pin=None, plan_pin=None, extra=(), inventory_bytes=None):
        data = wire(self.inventory) if inventory_bytes is None else inventory_bytes
        self.manifest_path.write_bytes(data)
        result = subprocess.run(
            [sys.executable, "-B", *("-O",) * bool(sys.flags.optimize),
             "-m", "tools.atlas_retention_binding",
             "--plan", str(self.plan_path), "--plan-sha256", plan_pin or sha(self.plan_path.read_bytes()),
             "--inventory", str(self.manifest_path), "--inventory-sha256", pin or sha(data),
             "--root", f"corpus={self.root}", "--root", f"backup={self.backup_root}", *extra],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertTrue(result.stdout, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["DELETE_AUTHORIZED"], "NO")
        return result, report

    def accepted(self, **kwargs):
        result, report = self.run_binding(**kwargs)
        self.assertEqual(result.returncode, 0, (report, result.stderr))
        self.assertEqual(report["status"], "BOUND_READ_ONLY")
        return report

    def rejected(self, code, **kwargs):
        result, report = self.run_binding(**kwargs)
        self.assertEqual(result.returncode, 2, (report, result.stderr))
        self.assertEqual(report["status"], "REJECTED")
        self.assertEqual(report["error"], code)
        self.assertNotIn("items", report)
        self.assertEqual(result.stderr, "")

    def test_published_plan_binds_without_rewriting(self):
        files = list(self.root.iterdir())
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
        report = self.accepted()
        self.assertEqual(len(report["items"]), 3)
        self.assertEqual(report["space"]["logical_bytes"], sum(len(x[0]) for x in before.values()))
        self.assertEqual(report["space"]["protected_bytes"], report["space"]["logical_bytes"])
        self.assertEqual(self.plan_path.read_bytes(), self.plan_bytes)
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}, before)

    def test_selection_tampering_is_rejected(self):
        for identity in (self.plan["selection"][0], self.plan["items"][0]["identity"]):
            identity["selection_key"] = "forged"
        self.save_plan()
        self.rejected("SELECTION_KEY_MISMATCH")

    def test_plan_revision_must_match_current_inventory(self):
        self.inventory["source"]["revision"] = "INVENTED_REVISION_B"
        self.rejected("SNAPSHOT_MISMATCH")

    def test_duplicate_uid_is_rejected(self):
        self.plan["selection"].append(self.plan["selection"][0])
        self.plan["items"].append(self.plan["items"][0])
        self.save_plan()
        self.rejected("DUPLICATE_UID")

    def test_selection_and_item_identity_must_agree(self):
        self.plan["items"][0]["identity"]["source_key"] = "altered"
        self.save_plan()
        self.rejected("SELECTION_ITEM_MISMATCH")

    def test_inventory_integrity_requires_external_pin(self):
        self.rejected("INVENTORY_DIGEST_MISMATCH", pin="0" * 64)

    def test_intent_change_is_detected_by_plan_pin(self):
        self.plan["items"][2]["intent"] = "REVIEW_FOR_REMOVAL"
        self.save_plan()
        self.rejected("PLAN_DIGEST_MISMATCH", plan_pin=sha(self.plan_bytes))

    def test_plan_never_accepts_authorization(self):
        self.plan["items"][0]["protection"]["removal_authorized"] = True
        self.save_plan()
        self.rejected("PLAN_NOT_PROPOSAL_ONLY")

    def test_table_row_lexemes_must_match_authenticated_binding(self):
        row = self.plan["items"][2]["table_rows"]["rows"][0]
        row["raw_json"] = '{"id":"different-row"}'
        self.save_plan()
        self.rejected("TABLE_ROWS_MISMATCH")

    def test_file_missing_is_rejected(self):
        (self.root / "data-0.bin").unlink()
        self.rejected("FILE_MISSING")

    def test_same_size_different_contents_are_rejected(self):
        path = self.root / "data-0.bin"
        path.write_bytes(b"x" * path.stat().st_size)
        self.rejected("FILE_DIGEST_MISMATCH")

    def test_symlink_or_junction_is_rejected(self):
        # Windows junction creation does not depend on symlink privileges.
        source = self.root / "data-0.bin"
        source.rename(self.backup_root / source.name)
        link = self.root / "escape"
        if os.name == "nt":
            made = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(self.backup_root)],
                                  capture_output=True, check=True)
            self.assertEqual(made.returncode, 0)
            self.addCleanup(os.rmdir, link)
        else:
            link.symlink_to(self.backup_root, target_is_directory=True)
        self.inventory["files"][0]["path"] = "escape/data-0.bin"
        self.rejected("UNSAFE_FILE")

    def test_hostile_paths_are_rejected(self):
        for path in ("../backup/data-0.bin", "ok/../../outside", r"..\outside",
                     "/etc/passwd", "C:/Windows/win.ini", "//server/share/file",
                     "data-0.bin:secret", "aux.txt", "ok//data-0.bin", "ok./data-0.bin",
                     "./data-0.bin", "ok/\0file", "ok/\nfile"):
            with self.subTest(path=path):
                self.inventory["files"][0]["path"] = path
                self.rejected("INVALID_RELATIVE_PATH")

    def test_hardlink_is_rejected_even_when_the_alias_is_outside_root(self):
        os.link(self.root / "data-0.bin", self.backup_root / "alias")
        self.rejected("HARDLINK_UNSAFE")

    def test_shared_file_and_conflict_are_reported_once_in_totals(self):
        self.plan["items"][0]["intent"] = "REVIEW_FOR_REMOVAL"
        self.plan["items"][2]["intent"] = "KEEP_FULL"
        self.save_plan()
        self.inventory["bindings"][2]["files"].append("file-0")
        report = self.accepted()
        self.assertIn("SHARED_DEPENDENCY", report["items"][0]["blockers"])
        self.assertIn("RETENTION_CONFLICT", report["items"][0]["blockers"])
        shared = next(f for f in report["files"] if f["id"] == "file-0")
        self.assertEqual(shared["dependents"], 2)
        self.assertEqual(shared["selected_indices"], [0, 2])
        self.assertTrue(shared["protected"])
        self.assertEqual(report["space"]["logical_bytes"], sum(f["bytes"] for f in self.inventory["files"]))

    def test_unselected_dependent_blocks_review(self):
        self.plan["items"][0]["intent"] = "REVIEW_FOR_REMOVAL"
        self.save_plan()
        other = dict(self.inventory["bindings"][0], uid="unselected")
        self.inventory["bindings"].append(other)
        report = self.accepted()
        self.assertIn("SHARED_DEPENDENCY", report["items"][0]["blockers"])
        self.assertEqual(next(f for f in report["files"] if f["id"] == "file-0")["selected_indices"], [0])

    def test_failed_experiment_and_unproven_backup_do_not_make_eligible(self):
        self.assertIn("FAILED", self.plan["items"][0]["raw_json"])
        self.plan["items"][0]["intent"] = "REVIEW_FOR_REMOVAL"
        self.save_plan()
        report = self.accepted()
        self.assertEqual(report["items"][0]["eligibility"], "BLOCKED")
        self.assertIn("BACKUP_UNVERIFIED", report["items"][0]["blockers"])
        self.assertFalse(report["items"][0]["removal_authorized"])
        self.assertIsNone(report["space"]["recoverable_bytes"])
        self.assertEqual(report["space"]["recoverable_status"], "RECOVERABLE_SPACE_UNKNOWN")

    def test_baseline_is_protected_against_removal_intent(self):
        self.plan["items"][2]["intent"] = "REVIEW_FOR_REMOVAL"
        self.save_plan()
        report = self.accepted()
        self.assertIn("BASELINE_PROTECTED", report["items"][2]["blockers"])
        self.assertFalse(report["items"][2]["removal_authorized"])

    def test_partial_inventory_can_be_completed_with_authenticated_increment(self):
        self.inventory["dependency_scope"] = "UNKNOWN"
        binding = self.inventory["bindings"][0]
        binding["coverage"] = "PARTIAL"
        report = self.accepted()
        self.assertFalse(report["space"]["logical_complete"])
        self.assertIn("BINDING_COVERAGE_UNKNOWN", report["items"][0]["blockers"])
        delta = {
            **self.inventory, "parent_sha256": sha(wire(self.inventory)),
            "provenance": {"producer": "fixture", "evidence": "synthetic-complement"},
            "dependency_scope": "COMPLETE",
            "files": [], "bindings": [dict(binding, coverage="COMPLETE")],
        }
        path = self.temp / "delta.json"
        path.write_bytes(wire(delta))
        report = self.accepted(extra=("--inventory", str(path), "--inventory-sha256", sha(wire(delta))))
        self.assertTrue(report["space"]["logical_complete"])
        self.assertEqual(report["inventories"], 2)
        delta["parent_sha256"] = "0" * 64
        path.write_bytes(wire(delta))
        self.rejected("INVENTORY_PARENT_MISMATCH",
                      extra=("--inventory", str(path), "--inventory-sha256", sha(wire(delta))))

    def test_unauthorized_root_alias_does_not_resolve(self):
        self.inventory["files"][0]["root"] = "missing"
        self.rejected("ROOT_NOT_AUTHORIZED")

    def test_duplicate_root_alias_is_rejected(self):
        self.rejected("ROOT_ALIAS_COLLISION", extra=("--root", f"corpus={self.backup_root}"))

    def test_a_documentary_reference_is_never_used_as_a_path(self):
        self.plan["items"][0]["declared"]["artifacts"] = [{"raw_json": '"../../unauthorized"'}]
        self.save_plan()
        self.accepted()


if __name__ == "__main__":
    unittest.main()
