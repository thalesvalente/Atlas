"""Public synthetic regressions for source-scoped, neutral run references."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from atlas_viewer.catalog import Catalog
from caderno_protocol import load_package, to_read_model, validate_document
from caderno_protocol import storage

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))
NOTE_ID = "urn:atlas:synthetic:related:note"


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class RelatedReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        shutil.copytree(REPO / "examples/environmental/sample", self.source)
        self.metadata = self.source / "ro-crate-metadata.json"
        self.document = json.loads(self.metadata.read_text(encoding="utf-8"))
        self.runs = [e for e in self.document["@graph"] if e.get("@type") == "CreateAction"]
        self.note = {"@id": NOTE_ID, "@type": "CreativeWork", "name": "Nota sintética A",
                     "description": "Contexto declarado sem relação causal."}
        self.document["@graph"].append(self.note)
        self.runs[0]["mentions"] = [{"@id": NOTE_ID}]

    def write(self):
        self.metadata.write_text(json.dumps(self.document, ensure_ascii=False) + "\n", encoding="utf-8")

    def read(self):
        self.write()
        package = load_package(self.source)
        self.assertTrue(package.report.valid, package.report.to_dict())
        return package, to_read_model(package)

    def test_declared_mention_is_visible_without_input_or_output_invention(self):
        before = to_read_model(load_package(self.source))
        package, model = self.read()
        run = model["runs"][0]
        self.assertIn("related_references", run, "Declared mentions must be visible in the run projection")
        self.assertEqual(run["related_references"], [{
            "id": NOTE_ID, "name": "Nota sintética A", "types": ["CreativeWork"],
            "description": "Contexto declarado sem relação causal.",
            "declared_digest": None, "availability": {"status": "UNVERIFIED"},
        }])
        for key in ("inputs", "outputs", "artifacts", "derived_from", "status", "review_status",
                    "metrics", "parameters", "started_at", "ended_at", "timestamp_origin"):
            self.assertEqual(run[key], before["runs"][0][key], key)
        self.assertEqual(model["relations"], before["relations"])
        self.assertEqual(package.document, self.document)

    def test_single_reference_and_list_forms_preserve_first_occurrence_order(self):
        other_id = self.runs[1]["@id"]
        cases = [({"@id": NOTE_ID}, [NOTE_ID]),
                 ([{"@id": NOTE_ID}, {"@id": other_id}, {"@id": NOTE_ID}], [NOTE_ID, other_id]),
                 ([], [])]
        for declared, expected in cases:
            with self.subTest(declared=declared):
                self.runs[0]["mentions"] = declared
                _, model = self.read()
                self.assertEqual([r["id"] for r in model["runs"][0]["related_references"]], expected)

    def test_missing_empty_and_long_titles_keep_declared_identity(self):
        for title in (None, "", 42, "Long" * 150):
            with self.subTest(title=title):
                if title is None:
                    self.note.pop("name", None)
                else:
                    self.note["name"] = title
                _, model = self.read()
                actual = model["runs"][0]["related_references"][0]
                self.assertEqual(actual["id"], NOTE_ID)
                self.assertEqual(actual["name"], title if isinstance(title, str) and title else NOTE_ID)

    def test_packages_without_run_mentions_continue_with_empty_references(self):
        self.runs[0].pop("mentions")
        _, model = self.read()
        self.assertTrue(all(run["related_references"] == [] for run in model["runs"]))
        self.assertNotIn("related_references", self.document["@graph"][0])

    def test_unresolved_mentions_are_rejected_without_source_fallback(self):
        for target in ("urn:atlas:synthetic:undeclared", "https://example.invalid/undeclared"):
            with self.subTest(target=target):
                self.runs[0]["mentions"] = [{"@id": target}]
                self.write()
                report = validate_document(self.document)
                self.assertFalse(report.valid)
                self.assertIn("MISSING_REFERENCE", {issue.code for issue in report.errors})
                source = Catalog([self.source]).snapshot()["sources"][0]
                self.assertEqual(source["status"], "INVALID")
                self.assertIsNone(source["read_model"])

    def test_expanded_reference_objects_are_not_silently_normalized(self):
        self.runs[0]["mentions"] = {"@id": NOTE_ID, "name": "Embedded entity is outside the contract"}
        self.assertIn("REFERENCE_FORM", {issue.code for issue in validate_document(self.document).errors})

    def test_availability_and_digest_keep_observed_and_declared_meanings(self):
        missing = {"@id": "evidence/missing.txt", "@type": "File", "cp:availability": "MISSING",
                   "cp:sha256": "a" * 64}
        external = {"@id": "https://example.invalid/related.txt", "@type": "File",
                    "cp:availability": "EXTERNAL", "cp:sha256": "b" * 64}
        self.document["@graph"].extend([missing, external])
        self.document["@graph"][1]["hasPart"].extend({"@id": e["@id"]} for e in (missing, external))
        ids = [NOTE_ID, "data/water.csv", missing["@id"], external["@id"]]
        self.runs[0]["mentions"] = [{"@id": eid} for eid in ids]
        with patch("urllib.request.urlopen", side_effect=AssertionError("External references must not be opened")):
            package, model = self.read()
        references = {ref["id"]: ref for ref in model["runs"][0]["related_references"]}
        self.assertEqual(references[NOTE_ID]["availability"], {"status": "UNVERIFIED"})
        for eid in ids[1:]:
            self.assertEqual(references[eid]["availability"], package.payload_status[eid])
        self.assertEqual(references["data/water.csv"]["availability"]["status"], "AVAILABLE")
        self.assertEqual(references[missing["@id"]]["availability"]["status"], "MISSING")
        self.assertEqual(references[external["@id"]]["availability"]["status"], "EXTERNAL_UNRESOLVED")
        self.assertEqual(references[missing["@id"]]["declared_digest"], "a" * 64)
        self.assertNotIn("sha256", references[missing["@id"]]["availability"])
        self.assertNotIn("sha256", references[external["@id"]]["availability"])
        references["data/water.csv"]["availability"]["status"] = "MODIFIED_COPY"
        self.assertEqual(package.payload_status["data/water.csv"]["status"], "AVAILABLE")

    def test_same_ids_in_two_sources_resolve_inside_their_own_package(self):
        self.write()
        second = self.root / "second"
        shutil.copytree(self.source, second)
        document = deepcopy(self.document)
        next(e for e in document["@graph"] if e["@id"] == NOTE_ID)["name"] = "Nota sintética B"
        (second / "ro-crate-metadata.json").write_text(json.dumps(document), encoding="utf-8")
        catalog = Catalog([self.source, second]).snapshot()
        self.assertTrue(catalog["collisions"])
        a, b = catalog["sources"]
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(a["read_model"]["runs"][0]["related_references"][0]["name"], "Nota sintética A")
        self.assertEqual(b["read_model"]["runs"][0]["related_references"][0]["name"], "Nota sintética B")

    def test_mixed_inputs_outputs_and_mentions_do_not_create_extra_lineage(self):
        original = to_read_model(load_package(self.source))
        ids = [NOTE_ID, self.runs[0]["object"][0]["@id"], self.runs[0]["result"][0]["@id"]]
        self.runs[0]["mentions"] = [{"@id": eid} for eid in ids]
        _, model = self.read()
        run = model["runs"][0]
        self.assertEqual([r["id"] for r in run["related_references"]], ids)
        self.assertEqual(run["inputs"], original["runs"][0]["inputs"])
        self.assertEqual(run["outputs"], original["runs"][0]["outputs"])
        self.assertEqual(model["relations"], original["relations"])
        self.assertEqual({r["review_status"] for r in model["runs"]}, {"UNKNOWN", "HOLD"})

    def test_html_and_unsafe_uri_context_stay_data_without_arbitrary_read(self):
        target = "javascript:window.__atlasRelatedQA=1"
        self.note.update({"@id": target, "name": '<img src="https://example.invalid/x" onerror="window.__atlasRelatedQA=1">',
                          "description": '<script>window.__atlasRelatedQA=1</script> file:///unrequested/private.txt'})
        self.runs[0]["mentions"] = {"@id": target}
        self.write()
        observed = []
        original_read = storage._regular_bytes
        def tracked_read(path, limit, base=None):
            observed.append(Path(path))
            return original_read(path, limit, base)
        with patch.object(storage, "_regular_bytes", side_effect=tracked_read), patch(
                "urllib.request.urlopen", side_effect=AssertionError("No external reference resolution")):
            package = load_package(self.source)
            model = to_read_model(package)
        self.assertTrue(package.report.valid, package.report.to_dict())
        reference = model["runs"][0]["related_references"][0]
        self.assertEqual(reference["id"], target)
        self.assertEqual(reference["name"], self.note["name"])
        self.assertEqual(reference["description"], self.note["description"])
        self.assertTrue(all(path.is_relative_to(self.source) for path in observed))

    def test_index_rebuild_adds_projection_to_legacy_index_without_source_write(self):
        self.write()
        before = hashes(self.source)
        def old_projection(package):
            model = to_read_model(package)
            for run in model["runs"]:
                run.pop("related_references", None)
            return model
        with patch("atlas_viewer.catalog.to_read_model", side_effect=old_projection):
            catalog = Catalog([self.source])
        old = catalog.snapshot()
        self.assertNotIn("related_references", old["sources"][0]["read_model"]["runs"][0])
        new = catalog.rebuild()
        self.assertEqual(new["generation"], old["generation"] + 1)
        self.assertEqual(new["sources"][0]["read_model"]["runs"][0]["related_references"][0]["id"], NOTE_ID)
        self.assertEqual(new["sources"][0]["metadata_sha256"], old["sources"][0]["metadata_sha256"])
        self.assertEqual(hashes(self.source), before)
        self.assertEqual(catalog.dossier()["authority"], "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL")


if __name__ == "__main__":
    unittest.main()
