"""Direct actual R4 v5 field mapping — source values entirely invented."""
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

    def test_invalid_numeric_native_id_rejected(self):
        src = raw_v5()
        src["lineage_graph"]["nodes"][0]["native_id"] = 123
        with self.assertRaises(ReaderError):
            make_descriptor(src)


if __name__ == "__main__":
    unittest.main()
