"""Behavior tests for the isolated P03 public-contract metadata adapter."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "packages/atlas/src"), str(ROOT / "packages/protocol/src")]
from atlas_viewer.parity02_p03_metadata import (  # noqa: E402
    MAX_ENTITIES, MAX_ITEMS, MAX_TEXT, MetadataError, project_metadata,
)


class MetadataProjectionTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((ROOT / "tests/fixtures/atlas_parity02/p03/artifact-read-model.json").read_text())

    def project(self, **kwargs):
        return project_metadata(self.model, "synthetic-source-A", **kwargs)

    def item(self, eid):
        return next(item for item in self.project()["items"] if item["identity"]["id"] == eid)

    def fails(self, code, callback):
        with self.assertRaises(MetadataError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_source_pair_is_explicit_and_collision_free(self):
        a = project_metadata({"entities": [{"@id": "c", "@type": "File"}]}, "a:b")
        b = project_metadata({"entities": [{"@id": "b:c", "@type": "File"}]}, "a")
        self.assertNotEqual(a["items"][0]["identity"], b["items"][0]["identity"])
        self.assertEqual(a["items"][0]["identity"], {"source_key": "a:b", "id": "c"})

    def test_file_name_and_mime_do_not_infer_document_or_product(self):
        item = self.item("report.pdf")
        self.assertEqual(item["kind"], "artifact")
        self.assertEqual(item["types"], ["File"])
        self.assertEqual(item["media_type"], "application/pdf")
        self.assertNotIn("semantic_kind", item)

    def test_declared_and_observed_availability_are_separate(self):
        item = self.item("report.pdf")
        self.assertEqual(item["availability"], {"declared": "UNKNOWN", "observed": "UNVERIFIED"})
        self.assertEqual(self.item("data/source.csv")["availability"], {"declared": "MISSING", "observed": "MISSING"})

    def test_missing_calculated_digest_stays_absent(self):
        self.assertEqual(self.item("report.pdf")["digests"], {"declared_sha256": None, "calculated_sha256": None})
        item = self.item("data/unverified.csv")
        self.assertIsNone(item["digests"]["declared_sha256"])
        self.assertEqual(item["digests"]["calculated_sha256"], "b" * 64)
        self.assertEqual(item["availability"]["observed"], "AVAILABLE_UNVERIFIED")

    def test_digest_mismatch_preserves_both_values_without_approval(self):
        item = self.item("data/tampered.csv")
        self.assertEqual(item["digests"], {"declared_sha256": "c" * 64, "calculated_sha256": "d" * 64})
        self.assertEqual(item["availability"]["observed"], "INTEGRITY_MISMATCH")
        self.assertNotIn("authentic", item)
        self.assertNotIn("approved", item)

    def test_mentions_are_neutral_and_do_not_become_outputs(self):
        item = self.item("report.pdf")
        self.assertEqual(item["relations"], [])
        self.assertEqual(len(item["mentions"]), 1)
        self.assertEqual(item["mentions"][0]["kind"], "mention")
        self.assertEqual(item["mentions"][0]["source"]["id"], "urn:synthetic:run")
        self.assertEqual(item["mentions"][0]["target"]["id"], "report.pdf")

    def test_input_output_derivation_directions_match_graph(self):
        original = self.item("data/source.csv")
        produced = self.item("data/result.csv")
        triples = {(r["source"]["id"], r["target"]["id"], r["kind"]) for r in original["relations"] + produced["relations"]}
        self.assertEqual(triples, {("data/source.csv", "urn:synthetic:run", "input"),
                                  ("urn:synthetic:run", "data/result.csv", "output"),
                                  ("data/result.csv", "data/source.csv", "derived_from")})

    def test_forged_read_model_output_is_rejected(self):
        self.model["relations"].append({"source": "urn:synthetic:run", "target": "report.pdf", "kind": "output"})
        self.fails("INCONSISTENT_READ_MODEL", self.project)

    def test_projected_reference_must_be_declared_in_entities(self):
        self.model["runs"][0]["related_references"].append({"id": "data/tampered.csv"})
        self.fails("INCONSISTENT_READ_MODEL", self.project)

    def test_non_action_result_field_does_not_create_production(self):
        self.model["entities"][4]["result"] = [{"@id": "report.pdf"}]
        self.assertEqual(self.item("report.pdf")["relations"], [])

    def test_html_uri_and_unicode_remain_exact_strings(self):
        item = self.item("https://example.invalid/payload.html")
        self.assertEqual(item["name"], '<img src=x onerror="globalThis.P03_ATTACK=true">')
        self.assertEqual(item["description"], "javascript:globalThis.P03_ATTACK=true")
        self.assertEqual(self.item("data/result.csv")["name"], "Resultado α — água 🌱")

    def test_no_io_and_no_mutation_or_aliasing(self):
        before = deepcopy(self.model)
        with patch("builtins.open", side_effect=AssertionError("I/O forbidden in adapter")):
            projected = self.project()
        self.assertEqual(self.model, before)
        projected["items"][0]["types"].append("Product")
        projected["items"][0]["relations"][0]["source"]["id"] = "changed"
        self.assertEqual(self.model, before)

    def test_empty_and_missing_metadata_remain_explicit(self):
        empty = project_metadata({}, "synthetic-empty")
        self.assertEqual(empty["items"], [])
        self.assertIsNone(empty["source"]["name"])
        self.assertIsNone(empty["source"]["metadata_sha256"])
        item = project_metadata({"entities": [{"@id": "empty", "@type": "File"}]}, "source")["items"][0]
        self.assertEqual(item["name"], "empty")
        self.assertIsNone(item["description"])
        self.assertEqual(item["availability"], {"declared": None, "observed": "UNVERIFIED"})

    def test_invalid_identity_duplicates_and_types_have_codes(self):
        self.fails("FIELD_TYPE", lambda: project_metadata(self.model, ""))
        self.fails("FIELD_TYPE", lambda: project_metadata([], "source"))
        self.fails("UNRESOLVED_ENTITY", lambda: self.project(entity_ids=["missing"]))
        self.fails("DUPLICATE_ID", lambda: self.project(entity_ids=["report.pdf", "report.pdf"]))
        self.model["entities"].append(deepcopy(self.model["entities"][0]))
        self.fails("DUPLICATE_ID", self.project)

    def test_conflicting_availability_or_declared_digest_is_rejected(self):
        self.model["artifacts"][0]["availability"]["declared"] = "PRESENT"
        self.fails("INCONSISTENT_READ_MODEL", self.project)
        self.setUp()
        self.model["artifacts"][1]["declared_digest"] = "f" * 64
        self.fails("INCONSISTENT_READ_MODEL", self.project)

    def test_invalid_status_digest_and_text_are_rejected(self):
        self.model["artifacts"][0]["availability"]["status"] = "APPROVED"
        self.fails("STATUS_VALUE", self.project)
        self.setUp()
        self.model["entities"][1]["cp:sha256"] = "not-a-digest"
        self.model["artifacts"][1]["declared_digest"] = "not-a-digest"
        self.fails("DIGEST_FORMAT", self.project)
        self.setUp()
        self.model["entities"][0]["name"] = 7
        self.fails("FIELD_TYPE", self.project)

    def test_numeric_false_source_digest_is_not_treated_as_missing(self):
        for value in [False, 0, [], {}]:
            with self.subTest(value=value):
                self.fails("FIELD_TYPE", lambda: project_metadata({"source": {"metadata_sha256": value}}, "source"))
        self.assertIsNone(project_metadata({"source": {"metadata_sha256": ""}}, "source")["source"]["metadata_sha256"])

    def test_item_and_text_boundaries_are_enforced(self):
        model = {"entities": [{"@id": f"file-{n}", "@type": "File", "name": "🌱" * MAX_TEXT} for n in range(MAX_ITEMS)]}
        self.assertEqual(len(project_metadata(model, "bounded")["items"]), MAX_ITEMS)
        model["entities"].append({"@id": "overflow", "@type": "File"})
        self.fails("LIMIT", lambda: project_metadata(model, "bounded"))
        self.model["entities"][0]["name"] = "x" * (MAX_TEXT + 1)
        self.fails("LIMIT", self.project)
        self.fails("LIMIT", lambda: project_metadata({"entities": [{}] * (MAX_ENTITIES + 1)}, "bounded"))

    def test_numeric_metadata_is_not_coerced_or_exposed_as_product_value(self):
        self.model["entities"][0]["contentSize"] = 9007199254740993123456789
        self.model["entities"][0]["value"] = "000012345678901234567890"
        item = self.item("data/source.csv")
        self.assertNotIn("contentSize", item)
        self.assertNotIn("value", item)

    def test_sdk_read_model_of_existing_synthetic_package_is_consumable(self):
        from caderno_protocol import load_package, to_read_model
        package = load_package(ROOT / "examples/environmental/sample")
        self.assertTrue(package.report.valid, package.report.to_dict())
        projected = project_metadata(to_read_model(package), "environmental-synthetic")
        self.assertGreater(len(projected["items"]), 0)
        self.assertTrue(all(item["kind"] in {"artifact", "entity"} for item in projected["items"]))
        self.assertTrue(all(item["identity"]["source_key"] == "environmental-synthetic" for item in projected["items"]))


if __name__ == "__main__":
    unittest.main()
