"""Independent public-contract tests using the environmental exporter path.

Run against an installed SDK. ATLAS_TEST_REPO may identify the source tree
containing the independent producer; no private producer/source is required.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from caderno_protocol import PROFILE_ID, load_package, to_read_model, validate_document

REPO = Path(os.environ.get("ATLAS_TEST_REPO", str(Path(__file__).resolve().parents[2])))


def file_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def replace_id(value, old, new):
    if isinstance(value, dict):
        return {k: (new if k == "@id" and v == old else replace_id(v, old, new)) for k, v in value.items()}
    if isinstance(value, list):
        return [replace_id(v, old, new) for v in value]
    return value


class ProtocolAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origin_temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.origin_temp.cleanup)
        cls.origin = Path(cls.origin_temp.name) / "environment"
        subprocess.run([sys.executable, str(REPO / "examples/environmental/export.py"), str(cls.origin)], check=True, capture_output=True, text=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "crate"
        shutil.copytree(self.origin, self.source)
        self.metadata = self.source / "ro-crate-metadata.json"
        self.document = json.loads(self.metadata.read_text(encoding="utf-8"))

    def write(self, document=None):
        self.metadata.write_text(json.dumps(self.document if document is None else document, ensure_ascii=False), encoding="utf-8")

    def entity(self, type_name):
        return next(e for e in self.document["@graph"] if type_name in (e["@type"] if isinstance(e["@type"], list) else [e["@type"]]))

    def codes(self, report):
        return {e.code for e in report.errors}

    def test_real_exporter_produces_valid_complete_partial_failed_and_unknown(self):
        package = load_package(self.source)
        self.assertTrue(package.report.valid, package.report.to_dict())
        model = to_read_model(package)
        self.assertEqual({"COMPLETED", "PARTIAL", "FAILED", "UNKNOWN"}, {r["status"] for r in model["runs"]})
        self.assertEqual(2, len(model["projects"]))
        self.assertTrue(all(r["synthetic"] for r in model["runs"]))
        self.assertTrue(any(r["review_status"] == "HOLD" for r in model["runs"]))
        self.assertEqual("NOT_VERIFIED", package.report.to_dict()["authenticity"])
        self.assertEqual("NOT_EVALUATED", package.report.to_dict()["scientific_acceptance"])

    def test_read_projection_and_reload_do_not_change_source_bytes(self):
        before = file_hashes(self.source)
        first = to_read_model(load_package(self.source))
        second = to_read_model(load_package(self.source))
        self.assertEqual(before, file_hashes(self.source))
        self.assertEqual(first, second)

    def test_graph_order_does_not_change_graph_validity(self):
        self.document["@graph"].reverse()
        self.assertTrue(validate_document(self.document).valid)

    def test_metadata_digest_is_byte_integrity_not_semantic_canonicalization(self):
        first = load_package(self.source)
        self.write()
        second = load_package(self.source)
        self.assertTrue(second.report.valid)
        self.assertEqual(first.document, second.document)
        self.assertNotEqual(first.metadata_sha256, second.metadata_sha256)

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        self.metadata.write_text('{"@context": [], "@context": [], "@graph": []}', encoding="utf-8")
        self.assertIn("SOURCE_INVALID", self.codes(load_package(self.source).report))

    def test_duplicate_graph_ids_are_rejected(self):
        self.document["@graph"].append(deepcopy(self.document["@graph"][0]))
        self.assertIn("DUPLICATE_ID", self.codes(validate_document(self.document)))

    def test_unknown_context_never_causes_network_loading(self):
        self.document["@context"] = "https://example.invalid/attacker-context"
        self.write()
        with patch("socket.socket.connect", side_effect=AssertionError("Network must not be attempted")):
            package = load_package(self.source)
        self.assertIn("UNSUPPORTED_CONTEXT", self.codes(package.report))

    def test_context_redefinition_is_rejected(self):
        self.document["@context"][-1]["cp"] = "https://example.invalid/semantic-redefinition#"
        self.assertIn("UNSUPPORTED_CONTEXT", self.codes(validate_document(self.document)))

    def test_future_profile_is_not_downgraded(self):
        root = next(e for e in self.document["@graph"] if e["@id"] == "./")
        for ref in root["conformsTo"]:
            if ref["@id"] == PROFILE_ID:
                ref["@id"] += "-future"
        self.assertIn("UNSUPPORTED_PROFILE", self.codes(validate_document(self.document)))

    def test_missing_run_experiment_is_graph_error(self):
        self.entity("CreateAction")["cp:experiment"] = {"@id": "urn:qa:missing-experiment"}
        self.assertIn("RUN_EXPERIMENT", self.codes(validate_document(self.document)))

    def test_missing_local_payload_retains_record_and_reports_availability(self):
        (self.source / "data/partial.csv").unlink()
        package = load_package(self.source)
        self.assertTrue(package.report.valid)
        self.assertEqual("MISSING", package.payload_status["data/partial.csv"]["status"])
        self.assertTrue(any(x["id"] == "data/partial.csv" for x in to_read_model(package)["artifacts"]))

    def test_changed_payload_fails_byte_integrity(self):
        (self.source / "data/water.csv").write_bytes(b"altered synthetic bytes")
        package = load_package(self.source)
        self.assertIn("INTEGRITY_MISMATCH", self.codes(package.report))
        self.assertEqual("INTEGRITY_MISMATCH", package.payload_status["data/water.csv"]["status"])

    def test_external_payload_remains_unresolved_without_network(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network must not be attempted")):
            package = load_package(self.source)
        self.assertEqual("EXTERNAL_UNRESOLVED", package.payload_status["https://example.invalid/synthetic-large-data.csv"]["status"])

    def test_traversal_references_are_rejected_without_reading(self):
        outside = self.base / "outside.csv"
        outside.write_bytes(b"not authorized for package")
        for bad in ["../outside.csv", "%2e%2e/outside.csv", "..\\outside.csv", "/outside.csv", "file:///outside.csv"]:
            with self.subTest(path=bad):
                doc = replace_id(self.document, "data/water.csv", bad)
                self.write(doc)
                package = load_package(self.source)
                self.assertIn("UNSAFE_REFERENCE", self.codes(package.report))
                self.assertNotIn("sha256", package.payload_status[bad])

    def test_malformed_uri_returns_validation_error_instead_of_crashing(self):
        for bad in ["https://[bad", "http://[invalid", "//["]:
            with self.subTest(uri=bad):
                doc = replace_id(self.document, "data/water.csv", bad)
                report = validate_document(doc)
                self.assertFalse(report.valid)

    def test_boolean_is_not_number(self):
        self.entity("PropertyValue")["value"] = True
        self.assertIn("METRIC_VALUE_TYPE", self.codes(validate_document(self.document)))

    def test_nonfinite_numbers_are_rejected_at_document_and_json_boundaries(self):
        self.entity("PropertyValue")["value"] = float("nan")
        self.assertIn("NONFINITE_NUMBER", self.codes(validate_document(self.document)))
        self.write()
        self.assertIn("SOURCE_INVALID", self.codes(load_package(self.source).report))

    def test_missing_numeric_value_requires_reason(self):
        metric = self.entity("PropertyValue")
        metric["value"] = None
        metric.pop("cp:missingReason", None)
        self.assertIn("MISSING_VALUE_REASON", self.codes(validate_document(self.document)))

    def test_high_precision_decimal_bytes_are_rejected_instead_of_rounded(self):
        self.entity("PropertyValue")["value"] = "QA_HIGH_PRECISION_LITERAL"
        raw = json.dumps(self.document).replace('"QA_HIGH_PRECISION_LITERAL"', '1.0000000000000001')
        self.metadata.write_text(raw, encoding="utf-8")
        self.assertFalse(load_package(self.source).report.valid)

    def test_integer_above_javascript_safe_range_remains_exact_in_sdk(self):
        metric = self.entity("PropertyValue")
        metric.update(value=9007199254740993, unitText="1", **{"cp:valueType": "integer"})
        self.write()
        package = load_package(self.source)
        self.assertTrue(package.report.valid, package.report.to_dict())
        observed = next(m for run in to_read_model(package)["runs"] for m in run["metrics"] if m["id"] == metric["@id"])
        self.assertEqual(9007199254740993, observed["value"])
        self.assertIs(type(observed["value"]), int)

    def test_numeric_metric_requires_unit(self):
        self.entity("PropertyValue").pop("unitText", None)
        self.assertIn("METRIC_UNIT", self.codes(validate_document(self.document)))

    def test_timestamp_requires_timezone(self):
        self.entity("CreateAction")["startTime"] = "2026-10-24T09:00:00"
        self.assertIn("TIMESTAMP", self.codes(validate_document(self.document)))

    def test_synthetic_accepted_science_is_rejected(self):
        self.entity("CreateAction")["cp:reviewStatus"] = "ACCEPTED"
        self.assertIn("SYNTHETIC_APPROVAL", self.codes(validate_document(self.document)))

    def test_execution_success_cannot_contradict_action_status(self):
        self.entity("CreateAction")["actionStatus"] = {"@id": "http://schema.org/FailedActionStatus"}
        self.assertIn("ACTION_STATUS", self.codes(validate_document(self.document)))

    def test_derivation_cycle_is_rejected(self):
        runs = [e for e in self.document["@graph"] if e["@type"] == "CreateAction"]
        runs[0]["prov:wasDerivedFrom"] = [{"@id": runs[1]["@id"]}]
        runs[1]["prov:wasDerivedFrom"] = [{"@id": runs[0]["@id"]}]
        self.assertIn("DERIVATION_CYCLE", self.codes(validate_document(self.document)))

    def test_zip_traversal_is_rejected_without_extracting(self):
        archive = self.base / "unsafe.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("ro-crate-metadata.json", self.metadata.read_bytes())
            z.writestr("../outside.txt", b"must not be written")
        package = load_package(archive)
        self.assertIn("SOURCE_UNSAFE", self.codes(package.report))
        self.assertFalse((self.base / "outside.txt").exists())

    def test_zip_symlink_is_rejected(self):
        archive = self.base / "link.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("ro-crate-metadata.json", self.metadata.read_bytes())
            member = zipfile.ZipInfo("data/link.csv")
            member.create_system = 3
            member.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(member, "../../outside")
        self.assertIn("SOURCE_UNSAFE", self.codes(load_package(archive).report))

    def test_zip_case_colliding_names_are_rejected(self):
        archive = self.base / "collision.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("ro-crate-metadata.json", self.metadata.read_bytes())
            z.writestr("data/x.csv", b"one")
            z.writestr("data/X.csv", b"two")
        self.assertIn("SOURCE_UNSAFE", self.codes(load_package(archive).report))

    def test_payload_symlink_outside_package_is_not_read(self):
        outside = self.base / "outside.csv"
        outside.write_bytes(b"not authorized")
        payload = self.source / "data/water.csv"
        payload.unlink()
        try:
            payload.symlink_to(outside)
        except OSError as exc:
            self.skipTest("Host cannot create symlinks: " + type(exc).__name__)
        package = load_package(self.source)
        self.assertEqual("UNAVAILABLE", package.payload_status["data/water.csv"]["status"])
        self.assertNotIn("sha256", package.payload_status["data/water.csv"])

    def test_symlink_metadata_is_not_read(self):
        saved = self.base / "metadata-copy.json"
        self.metadata.rename(saved)
        try:
            self.metadata.symlink_to(saved)
        except OSError as exc:
            self.skipTest("Host cannot create symlinks: " + type(exc).__name__)
        self.assertIn("SOURCE_UNSAFE", self.codes(load_package(self.source).report))

    def test_absent_source_is_not_fabricated_empty_success(self):
        package = load_package(self.base / "does-not-exist")
        self.assertIn("SOURCE_INACCESSIBLE", self.codes(package.report))
        self.assertEqual([], to_read_model(package)["runs"])

    def test_metadata_limit_is_enforced(self):
        self.metadata.write_bytes(b" " * (2 * 1024 * 1024 + 1))
        self.assertIn("SOURCE_UNSAFE", self.codes(load_package(self.source).report))

    def test_aggregate_payload_budget_applies_to_expanded_directories(self):
        root = next(e for e in self.document["@graph"] if e["@id"] == "./")
        chunk = b"q" * (8 * 1024 * 1024)
        for index in range(5):
            name = f"data/budget-{index}.bin"
            (self.source / name).write_bytes(chunk)
            self.document["@graph"].append({"@id": name, "@type": "File", "cp:availability": "PRESENT"})
            root["hasPart"].append({"@id": name})
        self.write()
        package = load_package(self.source)
        loaded_bytes = sum(x.get("size", 0) for x in package.payload_status.values())
        self.assertLessEqual(loaded_bytes, 32 * 1024 * 1024)
        self.assertTrue(any(x["status"] == "UNAVAILABLE" for x in package.payload_status.values()))


if __name__ == "__main__":
    unittest.main()
