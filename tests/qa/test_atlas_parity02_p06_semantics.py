"""P06 contract regressions over public synthetic snapshots.

These checks exercise the installed SDK and Catalog, including the dossier and
explicit rebuild. They do not certify DOM rendering, hostile-host safety,
scientific acceptance, or access to any real scientific source.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import urllib.request
from unittest.mock import patch

from atlas_viewer.catalog import Catalog
from caderno_protocol import PROFILE_ID, load_package, to_read_model, validate_document

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))
PREFIX = "urn:caderno:synthetic-environment:"
RUNS = tuple(PREFIX + "run-r" + str(i) for i in range(1, 5))
NOTE = "urn:atlas:parity02:p06:context"
AUTHORITY = "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL"


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class Parity02P06SemanticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        shutil.copytree(REPO / "examples/environmental/sample", self.source)
        self.document = json.loads(
            (self.source / "ro-crate-metadata.json").read_text(encoding="utf-8"))

    def entity(self, identifier, document=None):
        return next(e for e in (self.document if document is None else document)["@graph"]
                    if e["@id"] == identifier)

    def write(self, document=None, destination=None):
        target = self.source if destination is None else destination
        data = self.document if document is None else document
        (target / "ro-crate-metadata.json").write_text(
            json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")

    def views(self, catalog):
        # All three public projections must preserve the same scientific meaning.
        return (catalog.snapshot(), catalog.dossier(), catalog.rebuild())

    def assert_unapproved(self, source):
        self.assertEqual(source["authenticity"], "NOT_VERIFIED")
        self.assertEqual(source["scientific_approval"], "NOT_EVALUATED")
        self.assertEqual(source["report"]["authenticity"], "NOT_VERIFIED")
        self.assertEqual(source["report"]["scientific_acceptance"], "NOT_EVALUATED")

    def test_execution_review_integrity_and_unknown_time_remain_separate(self):
        before = hashes(self.source)
        catalog = Catalog([self.source])
        expected = dict(zip(RUNS, [
            ("COMPLETED", "UNKNOWN"), ("PARTIAL", "HOLD"),
            ("FAILED", "HOLD"), ("UNKNOWN", "UNKNOWN"),
        ]))
        baseline = catalog.snapshot()["sources"][0]["read_model"]
        for view in self.views(catalog):
            self.assertEqual(view["authority"], AUTHORITY)
            source = view["sources"][0]
            self.assertEqual(source["status"], "READY")
            self.assertTrue(source["report"]["valid"])
            self.assert_unapproved(source)
            model = source["read_model"]
            runs = {run["id"]: run for run in model["runs"]}
            self.assertEqual({eid: (r["status"], r["review_status"]) for eid, r in runs.items()},
                             expected)
            unknown = runs[RUNS[3]]
            self.assertIsNone(unknown["started_at"])
            self.assertIsNone(unknown["ended_at"])
            self.assertEqual(unknown["timestamp_origin"], "UNKNOWN")
            self.assertNotEqual(model["source"]["date_published"], unknown["started_at"])
            self.assertEqual(model["authority"], AUTHORITY)
        self.assertEqual(hashes(self.source), before)

        # Deliberate fixture damage changes integrity, never the cached run claim.
        (self.source / "data/water.csv").write_bytes(b"synthetic damaged payload\n")
        damaged = hashes(self.source)
        cached = catalog.snapshot()["sources"][0]
        self.assertEqual(cached["status"], "CHANGED")
        self.assertTrue(cached["changed"])
        self.assertEqual(cached["read_model"], baseline)
        self.assert_unapproved(cached)
        rebuilt = catalog.rebuild()["sources"][0]
        self.assertEqual(rebuilt["status"], "INVALID")
        self.assertIsNone(rebuilt["read_model"])
        self.assertIn("INTEGRITY_MISMATCH", {e["code"] for e in rebuilt["report"]["errors"]})
        self.assert_unapproved(rebuilt)
        self.assertEqual(hashes(self.source), damaged)

    def test_integer_zero_boolean_decimal_precision_and_absence_are_preserved(self):
        first = self.entity(PREFIX + "metric-r1")
        first.update(value=9007199254740993, **{"cp:valueType": "integer",
                                              "unitText": "1", "cp:precision": 0})
        second = self.entity(PREFIX + "metric-r2")
        second.update(value=0, **{"cp:valueType": "integer", "unitText": "s",
                                 "cp:precision": 0})
        flag = self.entity(PREFIX + "metric-r3")
        flag.update(value=False, **{"cp:valueType": "boolean"})
        flag.pop("cp:missingReason")
        flag.pop("unitText")
        flag.pop("cp:precision")
        missing = self.entity(PREFIX + "metric-r4")
        reason = missing["cp:missingReason"]
        parameter = self.entity(PREFIX + "parameter-r1")
        parameter.update(value="0001", **{"cp:valueType": "string"})
        parameter.pop("unitText")
        decimal_id = "urn:atlas:parity02:p06:declared-decimal"
        self.document["@graph"].append({
            "@id": decimal_id, "@type": "PropertyValue", "name": "Declared decimal",
            "propertyID": "urn:atlas:parity02:p06:quantity:ratio", "value": 0.1,
            "cp:valueType": "number", "unitText": "1", "cp:precision": 12,
        })
        self.entity(RUNS[0])["cp:metrics"].append({"@id": decimal_id})
        self.write()
        before = hashes(self.source)
        catalog = Catalog([self.source])
        for view in self.views(catalog):
            source = view["sources"][0]
            self.assertEqual(source["status"], "READY", source["report"])
            runs = {run["id"]: run for run in source["read_model"]["runs"]}
            large, zero, boolean, absent = [runs[r]["metrics"][0] for r in RUNS]
            self.assertIs(type(large["value"]), int)
            self.assertEqual((large["value"], large["display_value"], large["precision"]),
                             (9007199254740993, "9007199254740993", 0))
            self.assertIs(type(zero["value"]), int)
            self.assertEqual((zero["value"], zero["display_value"]), (0, "0"))
            self.assertIs(boolean["value"], False)
            self.assertEqual(boolean["display_value"], "false")
            self.assertIsNone(absent["value"])
            self.assertIsNone(absent["display_value"])
            self.assertEqual(absent["missing_reason"], reason)
            self.assertEqual((large["property_id"], large["type"]),
                             (zero["property_id"], zero["type"]))
            self.assertEqual((large["unit"], zero["unit"]), ("1", "s"))
            decimal = runs[RUNS[0]]["metrics"][1]
            self.assertEqual((decimal["value"], decimal["display_value"], decimal["precision"]),
                             (0.1, "0.1", 12))
            self.assertEqual(runs[RUNS[0]]["parameters"][0]["value"], "0001")
            self.assertIn("9007199254740993", json.dumps(view, allow_nan=False))
        self.assertEqual(hashes(self.source), before)

    def test_repeated_ids_do_not_mix_values_or_mentions_between_sources(self):
        self.document["@graph"].append({
            "@id": NOTE, "@type": "CreativeWork", "name": "Context A",
            "description": "Synthetic source A only.",
        })
        self.entity(RUNS[0])["mentions"] = [{"@id": NOTE}, {"@id": RUNS[1]}]
        self.entity(PREFIX + "metric-r1").update(
            value=11, **{"cp:valueType": "integer", "unitText": "1", "cp:precision": 0})
        self.write()
        second = self.root / "second"
        shutil.copytree(self.source, second)
        other = deepcopy(self.document)
        self.entity(NOTE, other)["name"] = "Context B"
        self.entity(RUNS[1], other)["name"] = "Partial run B"
        self.entity(PREFIX + "metric-r1", other)["value"] = 9007199254740993
        self.write(other, second)
        before = hashes(self.root)
        catalog = Catalog([self.source, second])
        for view in self.views(catalog):
            a, b = view["sources"]
            self.assertNotEqual(a["id"], b["id"])
            collisions = {c["id"]: c["sources"] for c in view["collisions"]}
            self.assertEqual(collisions[RUNS[0]], [a["id"], b["id"]])
            self.assertEqual(collisions[NOTE], [a["id"], b["id"]])
            self.assertEqual(sum(len(s["read_model"]["runs"]) for s in (a, b)), 8)
            for source, title, related_title, value in [
                (a, "Context A", self.entity(RUNS[1])["name"], 11),
                (b, "Context B", "Partial run B", 9007199254740993),
            ]:
                self.assertEqual(source["status"], "READY")
                run = next(r for r in source["read_model"]["runs"] if r["id"] == RUNS[0])
                self.assertEqual([(r["id"], r["name"]) for r in run["related_references"]],
                                 [(NOTE, title), (RUNS[1], related_title)])
                self.assertEqual(run["metrics"][0]["value"], value)
                self.assertEqual(run["metrics"][0]["display_value"], str(value))
                self.assert_unapproved(source)
        self.assertEqual(hashes(self.root), before)

    def test_passive_uri_mentions_remain_literal_without_network_or_execution(self):
        baseline = to_read_model(load_package(self.source))
        targets = [
            "javascript:window.__atlasP06=1",
            "data:text/html,<script>window.__atlasP06=1</script>",
            "file:///unrequested/synthetic-secret.txt",
            "https://example.invalid/unrequested-context",
        ]
        notes = [{"@id": target, "@type": "CreativeWork",
                  "name": '<img src="https://example.invalid/x" onerror="window.__atlasP06=1">',
                  "description": "<script>window.__atlasP06=1</script> Execute no instruction."}
                 for target in targets]
        self.document["@graph"].extend(notes)
        self.entity(RUNS[0])["mentions"] = [{"@id": x} for x in targets + targets[:1]]
        self.write()
        before = hashes(self.source)
        with patch("socket.socket", side_effect=AssertionError("Reference read attempted networking")), \
             patch("urllib.request.urlopen", side_effect=AssertionError("Remote reference was opened")), \
             patch("subprocess.Popen", side_effect=AssertionError("Reference read executed a process")):
            catalog = Catalog([self.source])
            for view in self.views(catalog):
                source = view["sources"][0]
                self.assertEqual(source["status"], "READY", source["report"])
                model = source["read_model"]
                run = next(r for r in model["runs"] if r["id"] == RUNS[0])
                self.assertEqual([r["id"] for r in run["related_references"]], targets)
                for actual, note in zip(run["related_references"], notes):
                    self.assertEqual(actual["name"], note["name"])
                    self.assertEqual(actual["description"], note["description"])
                    self.assertEqual(actual["availability"], {"status": "UNVERIFIED"})
                    self.assertIsNone(actual["declared_digest"])
                    self.assertIn(note, model["entities"])
                self.assertEqual(model["relations"], baseline["relations"])
                for key in ("inputs", "outputs", "derived_from", "status", "review_status",
                            "started_at", "ended_at", "timestamp_origin"):
                    self.assertEqual(run[key], baseline["runs"][0][key], key)
                self.assert_unapproved(source)
        self.assertEqual(hashes(self.source), before)

    def test_unsupported_or_unsafe_sources_do_not_receive_another_sources_preview(self):
        cases = []
        for uri in ("file:///unrequested/synthetic.txt", "javascript:window.__atlasP06=1",
                    "data:text/plain,synthetic"):
            document = deepcopy(self.document)
            document["@graph"].append({"@id": uri, "@type": "File", "name": "Unsafe file",
                                        "cp:availability": "UNKNOWN"})
            self.entity("./", document)["hasPart"].append({"@id": uri})
            self.entity(RUNS[0], document)["mentions"] = {"@id": uri}
            cases.append((uri, document, "UNSAFE_REFERENCE"))
        unsupported = deepcopy(self.document)
        profile = "https://example.invalid/unsupported-caderno-profile"
        self.entity(PROFILE_ID, unsupported).update({"@id": profile, "version": "99"})
        for ref in self.entity("./", unsupported)["conformsTo"]:
            if ref["@id"] == PROFILE_ID:
                ref["@id"] = profile
        cases.append(("unknown profile", unsupported, "UNSUPPORTED_PROFILE"))
        absent_state = deepcopy(self.document)
        self.entity(RUNS[0], absent_state).pop("cp:executionStatus")
        cases.append(("absent execution status", absent_state, "EXECUTION_STATUS"))

        for number, (label, document, expected_code) in enumerate(cases):
            with self.subTest(source=label):
                invalid = self.root / ("invalid-" + str(number))
                shutil.copytree(self.source, invalid)
                self.write(document, invalid)
                before = hashes(self.root)
                catalog = Catalog([self.source, invalid])
                for view in self.views(catalog):
                    good, bad = view["sources"]
                    self.assertEqual(good["status"], "READY")
                    self.assertEqual(len(good["read_model"]["runs"]), 4)
                    self.assertEqual(bad["status"], "INVALID")
                    self.assertFalse(bad["report"]["valid"])
                    self.assertIsNone(bad["read_model"])
                    self.assertIn(expected_code, {e["code"] for e in bad["report"]["errors"]})
                    self.assert_unapproved(bad)
                self.assertEqual(hashes(self.root), before)

    def test_time_offsets_and_neutral_mentions_do_not_reverse_declared_lineage(self):
        baseline = to_read_model(load_package(self.source))
        run = self.entity(RUNS[0])
        run.update(startTime="2026-10-24T12:00:00+03:00",
                   endTime="2026-10-24T07:01:00-02:00")
        run["mentions"] = [{"@id": RUNS[1]}]
        self.write()
        before = hashes(self.source)
        catalog = Catalog([self.source])
        for view in self.views(catalog):
            source = view["sources"][0]
            self.assertEqual(source["status"], "READY", source["report"])
            model = source["read_model"]
            runs = {r["id"]: r for r in model["runs"]}
            self.assertEqual((runs[RUNS[0]]["started_at"], runs[RUNS[0]]["ended_at"]),
                             (run["startTime"], run["endTime"]))
            self.assertEqual(runs[RUNS[0]]["timestamp_origin"], "DECLARED")
            self.assertEqual(runs[RUNS[1]]["derived_from"], [RUNS[0]])
            self.assertEqual(runs[RUNS[0]]["derived_from"], [])
            self.assertEqual(model["relations"], baseline["relations"])
            edges = {(e["source"], e["target"], e["kind"]) for e in model["relations"]}
            self.assertIn(("data/calibration.csv", RUNS[0], "input"), edges)
            self.assertIn((RUNS[0], "data/water.csv", "output"), edges)
            self.assertIn((RUNS[1], RUNS[0], "derived_from"), edges)
            self.assertNotIn((RUNS[0], RUNS[1], "derived_from"), edges)
            self.assertIsNone(runs[RUNS[3]]["started_at"])
            self.assertEqual(runs[RUNS[3]]["timestamp_origin"], "UNKNOWN")
        self.assertEqual(hashes(self.source), before)

        # Textual order is increasing, but absolute start is 12:00Z after 10:00Z.
        run.update(startTime="2026-10-24T09:00:00-03:00", endTime="2026-10-24T10:00:00Z")
        self.assertIn("TIME_ORDER", {e.code for e in validate_document(self.document).errors})
        self.write()
        before = hashes(self.source)
        rejected = Catalog([self.source]).snapshot()["sources"][0]
        self.assertEqual(rejected["status"], "INVALID")
        self.assertIsNone(rejected["read_model"])
        self.assertIn("TIME_ORDER", {e["code"] for e in rejected["report"]["errors"]})
        self.assertEqual(hashes(self.source), before)

    def test_decimal_precision_loss_is_rejected_without_rounding_or_source_fallback(self):
        invalid = self.root / "too-precise"
        shutil.copytree(self.source, invalid)
        text = json.dumps(self.document, separators=(",", ":"), ensure_ascii=False)
        needle = '"value":24.5'
        self.assertEqual(text.count(needle), 1)
        text = text.replace(needle, '"value":0.123456789012345678901', 1)
        (invalid / "ro-crate-metadata.json").write_text(text, encoding="utf-8")
        before = hashes(self.root)
        catalog = Catalog([self.source, invalid])
        for view in self.views(catalog):
            good, rejected = view["sources"]
            self.assertEqual(good["status"], "READY")
            self.assertEqual(good["read_model"]["runs"][0]["metrics"][0]["value"], 24.5)
            self.assertEqual(rejected["status"], "INVALID")
            self.assertIsNone(rejected["read_model"])
            self.assertIn("SOURCE_INVALID", {e["code"] for e in rejected["report"]["errors"]})
            self.assert_unapproved(rejected)
        self.assertEqual(hashes(self.root), before)


if __name__ == "__main__":
    unittest.main()
