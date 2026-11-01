"""Contract-level regression for the real R4 v5 export profile (invented bytes)."""
import copy
import json
import unittest

from tools.atlas_legacy_presentation.errors import ReaderError
from tools.atlas_legacy_presentation.legacy_v5 import (
    parse_legacy_export, inspect_legacy_projection,
)


def source():
    return {
        "schema": "r4-experiment-viewer-v5",
        "authority": "PRESENTATION_ONLY_NO_CLEANUP_AUTHORITY",
        "records": [{
            "id": "example-record-1", "title": "Invented example",
            "family": "Invented family", "kind": "mission", "result": "UNKNOWN",
            "retention": "REVIEW_REQUIRED", "resources": [],
        }],
        "edges": [], "resources": [], "products": [],
        "result_tables": [{
            "id": "table-1", "label": "Invented RF",
            "role": "UNADMITTED_NATIVE_RF", "record_id": None,
            "rows": [{"native_id": None, "cells": {
                "Nome": "Invented requirement", "Descrição": "<script>evil()</script>",
                "Critérios de Aceitação": "Invented acceptance", "ID": "",
            }}],
        }],
        "frontiers": [], "sources": [], "source_crosswalk": [],
        "coverage": {"limits": [], "global_history_complete": False},
        "lineage_graph": {
            "schema": "r4-experiment-lineage-a10-v1",
            "nodes": [
                {"ui_id": "ui-root", "key": "native-structural-1",
                 "native_id": None, "kind": "ExperimentFamily",
                 "label": "Example family"},
                {"ui_id": "ui-run", "key": "native-structural-2",
                 "native_id": "RUN-EXAMPLE", "kind": "Run",
                 "parent_key": "native-structural-1",
                 "label": "Invented run"},
            ],
            "edges": [{"from_key": "native-structural-1",
                       "to_key": "native-structural-2",
                       "type": "MEMBER_OF"}],
        },
    }


class V5SourceTests(unittest.TestCase):
    def test_inert_legacy_html_and_separate_collections(self):
        data = json.dumps(source(), ensure_ascii=False)
        html = ('<!doctype html><script>throw Error("should not run")</script>'
                '<script type="application/json" id="data">' + data +
                '</script><script>alert("not executed")</script>')
        parsed = parse_legacy_export(html.encode("utf-8"))
        summary = inspect_legacy_projection(parsed.value)
        self.assertEqual((summary["records"], summary["lineage_nodes"], summary["lineage_edges"]),
                         (1, 2, 1))
        self.assertEqual(summary["rows_per_table"], [1])
        self.assertEqual(parsed.value["result_tables"][0]["rows"][0]["native_id"], None)
        self.assertIn("<script>", parsed.value["result_tables"][0]["rows"][0]["cells"]["Descrição"])

    def test_real_profile_is_not_the_synthetic_source_contract(self):
        raw = json.dumps(source()).encode()
        self.assertEqual(parse_legacy_export(raw, media_type="application/json").value["schema"],
                         "r4-experiment-viewer-v5")
        with self.assertRaises(ReaderError):
            parse_legacy_export(b'{"format":"atlas-legacy-synthetic-source"}',
                                media_type="application/json")

    def test_duplicate_and_missing_data_blocked(self):
        original = source()
        duplicate = json.dumps(original).replace('"schema":', '"schema": "evil", "schema":', 1)
        with self.assertRaises(ReaderError):
            parse_legacy_export(duplicate.encode(), media_type="application/json")
        original.pop("source_crosswalk")
        with self.assertRaises(ReaderError):
            parse_legacy_export(json.dumps(original).encode(), media_type="application/json")

    def test_graph_keys_are_not_promoted_to_native_ids(self):
        parsed = parse_legacy_export(json.dumps(source()).encode(), media_type="application/json")
        node = parsed.value["lineage_graph"]["nodes"][0]
        self.assertEqual(node["key"], "native-structural-1")
        self.assertIsNone(node["native_id"])
        self.assertEqual(node["ui_id"], "ui-root")

    def test_duplicate_lineage_ui_id_rejected(self):
        original = source()
        original["lineage_graph"]["nodes"][1]["ui_id"] = "ui-root"
        with self.assertRaises(ReaderError):
            parse_legacy_export(json.dumps(original).encode(), media_type="application/json")

    def test_html_requires_exact_single_data_block(self):
        data = json.dumps(source())
        block = '<script id="data" type="application/json">' + data + '</script>'
        with self.assertRaises(ReaderError):
            parse_legacy_export((block + block).encode())
        with self.assertRaises(ReaderError):
            parse_legacy_export(b'<script>const DATA = {};</script>')
        with self.assertRaises(ReaderError):
            parse_legacy_export(('<script id="data" src="x" type="application/json">' +
                                 data + '</script>').encode())

    def test_original_numeric_lexeme_retained(self):
        raw = json.dumps(source()).replace('"ID": ""', '"ID": 90071992547409931111')
        parsed = parse_legacy_export(raw.encode(), media_type="application/json")
        self.assertEqual(parsed.lexemes["/result_tables/0/rows/0/cells/ID"],
                         "90071992547409931111")

    def test_original_graph_large_and_records_distinct(self):
        original = source()
        original["lineage_graph"]["nodes"] = [
            {"ui_id": f"ui-{i}", "key": f"key-{i}", "native_id": None,
             "kind": "Stage", "label": f"Invented {i}"}
            for i in range(2911)
        ]
        original["lineage_graph"]["edges"] = [
            {"from_key": f"key-{i}", "to_key": f"key-{i+1}", "type": "MEMBER_OF"}
            for i in range(1595)
        ]
        parsed = parse_legacy_export(json.dumps(original).encode(),
                                     media_type="application/json")
        summary = inspect_legacy_projection(parsed.value)
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["lineage_nodes"], 2911)
        self.assertEqual(summary["lineage_edges"], 1595)


if __name__ == "__main__":
    unittest.main()
