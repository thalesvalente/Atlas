"""Direct actual R4 v5 field mapping — source values entirely invented."""
import copy
import hashlib
import json
import unittest

from tools.atlas_legacy_presentation.legacy_v5 import parse_legacy_export
from tools.atlas_legacy_presentation.legacy_v5_descriptor import transform_legacy_v5
from tools.atlas_legacy_presentation.semantics import validate_descriptor
from tools.atlas_legacy_presentation.errors import ReaderError
from pathlib import Path


SCHEMA = json.loads((Path(__file__).resolve().parents[2] /
                    "tools/atlas_legacy_presentation/descriptor.schema.json")
                    .read_text(encoding="utf-8"))
NOW = "2026-10-31T01:00:00Z"


def raw_v5():
    return {
        "schema": "r4-experiment-viewer-v5",
        "authority": "PRESENTATION_ONLY_NO_CLEANUP_AUTHORITY",
        "records": [
            {"id": "rec-a", "title": "Invented experiment",
             "family": "Example", "kind": "experiment", "result": "UNKNOWN",
             "retention": "REVIEW_REQUIRED", "resources": []}
        ],
        "edges": [], "resources": [], "products": [],
        "result_tables": [
            {"id": "rf-set", "label": "RF invented", "role": "NATIVE_RF_SOURCE_PRESENTATION",
             "record_id": "rec-a", "run_id": "run-a",
             "rows": [
                 {"native_id": "RF-EXAMPLE-1", "cells": {
                     "ID": "RF-EXAMPLE-1",
                     "Nome": "Invented item",
                     "Descrição": "<script>doNotRun()</script>",
                     "Critérios de Aceitação": "Invented acceptance criterion"}},
             ]}
        ],
        "frontiers": [], "sources": [], "source_crosswalk": [],
        "coverage": {"limits": [], "global_history_complete": False},
        "lineage_graph": {
            "schema": "r4-experiment-lineage-a10-v1",
            "nodes": [
                {"ui_id": "ui-parent", "key": "experiment-key",
                 "native_id": "experiment-key", "kind": "ExperimentFamily",
                 "label": "Invented family"},
                {"ui_id": "ui-child", "key": "run-a",
                 "native_id": "run-a", "kind": "Run",
                 "label": "Invented execution", "parent_key": "experiment-key"},
            ],
            "edges": [
                {"type": "MEMBER_OF",
                 "from_key": "run-a", "to_key": "experiment-key"}
            ],
        },
    }


def make_descriptor(data=None):
    source = raw_v5() if data is None else data
    blob = json.dumps(source, ensure_ascii=False).encode("utf-8")
    parsed = parse_legacy_export(blob, media_type="application/json")
    descriptor = transform_legacy_v5(
        parsed, source_id="invented-source", snapshot_id="invented-snapshot",
        access_policy_id="invented-test-policy",
        bytes_sha256=hashlib.sha256(blob).hexdigest(),
        observed_at=NOW, generated_at=NOW,
        expires_at="2026-10-31T02:00:00Z", synthetic_test=True)
    validate_descriptor(descriptor, SCHEMA, now=NOW)
    return descriptor


class DirectV5DescriptorTests(unittest.TestCase):
    def test_real_r4_v5_direct_profile_yields_approved_descriptor(self):
        d = make_descriptor()
        self.assertEqual(d["source"]["original_format"], "r4-experiment-viewer-v5")
        self.assertEqual(len(d["tables"]), 1)
        self.assertEqual(len(d["nodes"]), 3)
        self.assertEqual(d["validation"]["authenticity"], "NOT_VERIFIED")
        self.assertEqual(d["coverage"]["global_total"], None)

    def test_rf_literal_and_native_id_not_inferred(self):
        d = make_descriptor()
        row = d["tables"][0]["rows"][0]
        requirement = row["requirement"]
        self.assertEqual(requirement["native_id"], "RF-EXAMPLE-1")
        self.assertEqual(row["cells"][requirement["fields"]["description"]]["literal"],
                         "<script>doNotRun()</script>")
        self.assertEqual(requirement["category_status"], "MISSING")
        self.assertIsNone(requirement["fields"]["category"])
        self.assertEqual(d["tables"][0]["record_binding"]["resolution"], "RESOLVED")

    def test_explicit_parent_only_when_original_native_matches(self):
        d = make_descriptor()
        run = next(n for n in d["nodes"] if n["identity"]["native_id"] == "run-a")
        self.assertEqual(run["tree_state"], "PARENT_RESOLVED")
        self.assertFalse(run["binding_gap"])

    def test_non_native_source_key_is_gap_not_fabricated_identity(self):
        source = raw_v5()
        source["lineage_graph"]["nodes"][0]["native_id"] = None
        d = make_descriptor(source)
        root = next(n for n in d["nodes"] if n["identity"]["locator"] == "/lineage_graph/nodes/0")
        self.assertIsNone(root["identity"]["native_id"])
        child = next(n for n in d["nodes"] if n["identity"]["native_id"] == "run-a")
        self.assertEqual(child["tree_state"], "RUN_EXTERNAL_ISOLATED")
        self.assertEqual(child["parent"]["declared_id"], "experiment-key")
        self.assertEqual(child["parent"]["resolution"], "UNRESOLVED")
        self.assertTrue(any(g["code"] == "SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE"
                            for g in d["gaps"]))

    def test_unadmitted_native_rf_remains_without_native_id(self):
        source = raw_v5()
        source["result_tables"][0]["role"] = "UNADMITTED_NATIVE_RF"
        source["result_tables"][0]["rows"][0]["native_id"] = None
        source["result_tables"][0]["rows"][0]["cells"].pop("ID")
        d = make_descriptor(source)
        row = d["tables"][0]["rows"][0]
        self.assertIsNone(row["identity"]["native_id"])
        self.assertEqual(row["requirement"]["admission"], "UNADMITTED_NATIVE_RF")
        self.assertIsNone(row["requirement"]["native_id"])

    def test_repeated_edges_keep_distinct_occurrences(self):
        src = raw_v5()
        src["lineage_graph"]["edges"].append(dict(src["lineage_graph"]["edges"][0]))
        d = make_descriptor(src)
        self.assertEqual([r["repeat_occurrence"] for r in d["relations"]], [1, 2])
        self.assertEqual(len({r["repeat_group"] for r in d["relations"]}), 1)

    def test_2911_original_lineage_nodes_are_independent_from_record_count(self):
        src = raw_v5()
        src["lineage_graph"]["nodes"] = [
            {"ui_id": f"ui-{i}", "key": f"key-{i}",
             "native_id": None, "kind": "Stage", "label": f"Invented {i}"}
            for i in range(2911)
        ]
        src["lineage_graph"]["edges"] = [
            {"type": "MEMBER_OF", "from_key": f"key-{i}",
             "to_key": f"key-{i+1}"}
            for i in range(1595)
        ]
        d = make_descriptor(src)
        self.assertEqual(len(d["nodes"]), 2912)
        self.assertEqual(len(d["relations"]), 1595)
        self.assertEqual(len(d["tables"]), 1)
        self.assertEqual(len(d["tables"][0]["rows"]), 1)

    def test_lineage_source_key_never_resolves_to_unrelated_record_id(self):
        source = raw_v5()
        # The lineage parent structural key happens to equal a record's native ID,
        # but the graph's parent node has NO native ID. Never choose the record.
        source["lineage_graph"]["nodes"][0]["key"] = "rec-a"
        source["lineage_graph"]["nodes"][0]["native_id"] = None
        source["lineage_graph"]["nodes"][1]["parent_key"] = "rec-a"
        descriptor = make_descriptor(source)
        child = next(node for node in descriptor["nodes"]
                     if node["identity"]["locator"] == "/lineage_graph/nodes/1")
        self.assertEqual(child["parent_key_literal"], "rec-a")
        self.assertEqual(child["parent"]["resolution"], "NULL_ENDPOINT")
        self.assertIsNone(child["parent"]["target_navigation_id"])
        self.assertTrue(child["binding_gap"])
        self.assertTrue(any(gap["code"] == "SOURCE_KEY_NAMESPACE_COLLISION"
                            for gap in descriptor["gaps"]))
        self.assertIn("/lineage_graph/nodes/1/parent_key",
                      {field["locator"] for field in descriptor["unmapped_fields"]})

    def test_invalid_numeric_native_id_rejected(self):
        src = raw_v5()
        src["lineage_graph"]["nodes"][0]["native_id"] = 123
        with self.assertRaises(ReaderError):
            make_descriptor(src)

    def test_lineage_graph_endpoint_cross_collection_collision_is_gap(self):
        source = raw_v5()
        source["lineage_graph"]["nodes"][0]["native_id"] = None
        source["lineage_graph"]["nodes"][0]["key"] = "rec-a"
        source["lineage_graph"]["edges"] = [
            {"type": "MEMBER_OF", "from_key": "rec-a", "to_key": "run-a"}]
        descriptor = make_descriptor(source)
        relation = descriptor["relations"][0]
        self.assertEqual(relation["from"]["resolution"], "NULL_ENDPOINT")
        self.assertIsNone(relation["from"]["target_navigation_id"])
        self.assertEqual(relation["to"]["resolution"], "RESOLVED")
        self.assertTrue(relation["binding_gap"])
        self.assertIn("/lineage_graph/edges/0/from_key",
                      {entry["locator"] for entry in descriptor["unmapped_fields"]})

    def test_table_record_id_not_resolved_to_unrelated_lineage_node(self):
        source = raw_v5()
        source["lineage_graph"]["nodes"].append({
            "key": "graph-local-key", "ui_id": "ui-third",
            "native_id": "ghost", "kind": "Run", "label": "Unrelated run"})
        source["result_tables"][0]["record_id"] = "ghost"
        descriptor = make_descriptor(source)
        table = descriptor["tables"][0]
        self.assertEqual(table["record_binding"]["resolution"], "NULL_ENDPOINT")
        self.assertTrue(any(entry["locator"] == "/result_tables/0/record_id"
                            and entry["value"]["literal"] == "ghost"
                            for entry in descriptor["unmapped_fields"]))

    def test_real_r4_v5_original_population_and_five_rf_tables(self):
        source = raw_v5()
        source["records"] = [dict(source["records"][0], id=f"rec-{i}")
                             for i in range(159)]
        counts = [39, 85, 28, 0, 0]
        tables = []
        for table_index, count in enumerate(counts):
            unadmitted = table_index == 2
            rows = []
            for index in range(count):
                identifier = f"RF-INVENTED-{table_index}-{index}"
                rows.append({
                    "native_id": None if unadmitted else identifier,
                    "cells": {"ID": "" if unadmitted else identifier,
                              "Núcleo / Módulo": "Módulo inventado",
                              "Nome": f"Nome {index}",
                              "Descrição": "Unicode ação ⚙",
                              "Critérios de Aceitação": "Critério literal"}})
            tables.append({"id": f"table-{table_index}", "label": "Inventada",
                           "role": ("UNADMITTED_NATIVE_RF" if unadmitted
                                    else "NATIVE_RF_SOURCE_PRESENTATION"),
                           "record_id": "rec-0" if table_index == 0 else "unlinked",
                           "rows": rows})
        source["result_tables"] = tables
        d = make_descriptor(source)
        self.assertEqual(len(d["nodes"]), 161)
        self.assertEqual([len(x["rows"]) for x in d["tables"]], counts)
        self.assertEqual(sum(len(x["rows"]) for x in d["tables"]), 152)
        self.assertEqual(sum(r["requirement"]["admission"] == "UNADMITTED_NATIVE_RF"
                             and r["identity"]["native_id"] is None
                             for table in d["tables"] for r in table["rows"]), 28)
        self.assertEqual(d["tables"][0]["record_binding"]["resolution"], "RESOLVED")
        self.assertTrue(all(x["record_binding"]["resolution"] == "UNRESOLVED"
                            for x in d["tables"][1:]))
        self.assertEqual(d["coverage"]["global_total"], None)

    def test_root_sidecars_and_a10_metadata_are_loss_accounted(self):
        source = raw_v5()
        source["sources"] = [{"id": "fake-source", "sha256": "not-authenticated"}]
        source["source_crosswalk"] = [{"record_id": "rec-a", "source_id": "invented"}]
        source["frontiers"] = [{"id": "fr-1", "records": ["rec-a"]}]
        source["external_runs"] = [{"id": "external-1", "run_id": "ghost"}]
        source["dossier_batch"] = {"status": "NOT_IMPORTED", "member_ledger": []}
        source["lineage_graph"]["branches"] = [{"ui_id": "invented-branch"}]
        source["lineage_graph"]["counts"] = {"nodes": 2, "edges": 1}
        d = make_descriptor(source)
        fields = {field["locator"]: field["value"] for field in d["unmapped_fields"]}
        for loc in ("/sources/0/id", "/source_crosswalk/0/record_id",
                    "/frontiers/0/id", "/external_runs/0/run_id",
                    "/dossier_batch/status",
                    "/lineage_graph/branches/0/ui_id",
                    "/lineage_graph/counts/nodes"):
            self.assertIn(loc, fields)
        self.assertEqual(fields["/dossier_batch/member_ledger"]["type"], "array")
        self.assertTrue(any(gap["code"] == "UNMAPPED_ROOT_FIELD"
                            for gap in d["gaps"]))

    def test_source_numeric_precision_null_missing_and_unicode(self):
        source = raw_v5()
        source["result_tables"][0]["role"] = "UNKNOWN"
        source["result_tables"][0]["rows"][0]["native_id"] = None
        source["result_tables"][0]["rows"][0]["cells"] = {
            "large": 900719925474099312345,
            "null": None, "absent": "", "emoji": "áé🔬"}
        raw = json.dumps(source, ensure_ascii=False).encode("utf-8")
        p = parse_legacy_export(raw, media_type="application/json")
        d = transform_legacy_v5(
            p, source_id="invented-source", snapshot_id="invented-snapshot",
            access_policy_id="invented-test-policy",
            bytes_sha256=hashlib.sha256(raw).hexdigest(),
            observed_at=NOW, generated_at=NOW,
            expires_at="2026-10-31T02:00:00Z", synthetic_test=True)
        validate_descriptor(d, SCHEMA, now=NOW)
        row = d["tables"][0]["rows"][0]
        self.assertEqual([c["type"] for c in row["cells"]],
                         ["integer", "null", "string", "string"])
        self.assertEqual(row["cells"][0]["lexeme"], "900719925474099312345")
        self.assertEqual(row["cells"][3]["literal"], "áé🔬")
        self.assertEqual(row["requirement"], None)

    def test_partial_invalid_source_rejected_without_partial_result(self):
        source = raw_v5()
        source["result_tables"].append({
            "id": "bad-table", "label": "Invented",
            "role": "UNADMITTED_NATIVE_RF",
            "rows": [{"native_id": "BAD-INVENTED",
                      "cells": {"ID": "BAD-INVENTED"}}]})
        data = json.dumps(source).encode("utf-8")
        parsed = parse_legacy_export(data, media_type="application/json")
        with self.assertRaises(ReaderError):
            transform_legacy_v5(
                parsed, source_id="source", snapshot_id="snapshot",
                access_policy_id="policy",
                bytes_sha256=hashlib.sha256(data).hexdigest(),
                observed_at=NOW, generated_at=NOW,
                expires_at="2026-10-31T02:00:00Z", synthetic_test=True)

    def test_dossier_collections_must_be_lists(self):
        source = raw_v5()
        source["dossier_packages"] = {"id": "not-a-list"}
        with self.assertRaises(ReaderError):
            parse_legacy_export(json.dumps(source).encode(),
                                media_type="application/json")

    def test_unadmitted_id_conflict_rejected_not_promoted(self):
        source = raw_v5()
        source["result_tables"][0]["role"] = "UNADMITTED_NATIVE_RF"
        with self.assertRaises(ReaderError):
            make_descriptor(source)

    def test_only_explicit_product_role_and_binding_produce_product(self):
        source = raw_v5()
        source["resources"] = [{"id": "res-1", "path": "invented/path"}]
        source["product_items"] = [{
            "id": "p-1", "label": "Invented product",
            "kind": "Product", "product_role": "SOURCE_DECLARED",
            "atlas_record_id": "rec-a"}]
        source["products"] = [{
            "id": "r4-product", "label": "No explicit product_role",
            "run_id": "run-a", "record_id": "rec-a",
            "pointer": "res-1", "resources": ["res-1"]}]
        d = make_descriptor(source)
        asset_kinds = {a["identity"]["native_id"]: a["kind"] for a in d["assets"]}
        self.assertEqual(asset_kinds["res-1"], "File")
        self.assertEqual(asset_kinds["p-1"], "Product")
        self.assertEqual(asset_kinds["r4-product"], "Other")
        self.assertTrue(any(gap["code"] == "PRODUCT_ROLE_OR_BINDING_UNVERIFIED"
                            for gap in d["gaps"]))


if __name__ == "__main__":
    unittest.main()
