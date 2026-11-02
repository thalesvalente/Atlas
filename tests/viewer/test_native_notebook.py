"""Executable integration of the real exporter, SDK and native reader.

Inputs are invented unit data; this does not certify the private host corpus.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
import zipfile

from caderno_protocol import load_package
from atlas_viewer.native_notebook import read_source, restore_projection, snapshot
from atlas_viewer.catalog import Catalog

ROOT = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))
EXPORTER = runpy.run_path(str(ROOT / "tools/export_native_notebook.py"))


def projection():
    return {"schema": "r4-experiment-viewer-v5", "atlas_integration": {"notebook_revision": "test-invented-revision"},
            "records": [{"id": "same", "title": "Registro A", "family": "F", "status": "HOLD", "kind": "Run"},
                        {"id": "same", "title": "Registro B", "family": "F", "status": "UNKNOWN", "kind": "Run"}],
            "lineage_graph": {"nodes": [{"key": "root", "native_id": None, "label": "Família", "kind": "Family"},
                                         {"key": "child", "parent_key": "root", "native_id": "R1", "label": "Execução", "kind": "Run"}], "edges": []},
            "edges": [{"from": "same", "to": None, "kind": "mention"}],
            "result_tables": [{"id": "T", "label": "Medições", "role": "UNADMITTED_NATIVE_RF", "rows": [
                {"native_id": None, "cells": {"ID": "RF-001", "Inteiro": 9007199254740993, "Ausente": None}},
                {"native_id": None, "cells": {"ID": "RF-002", "Inteiro": 0, "Formula": "=1+1"}}]}],
            "resources": [{"id": "evidence", "name": "Documento", "uri": "file:///private/never-opened", "availability": "UNKNOWN"}],
            "coverage": {"global_history": "GLOBAL_UNPROVEN", "limits": ["invented unit case"]},
            "unknown_empty": [], "unknown_null": None, "unknown_nested": {"a/b": [1, 2], "~key": False}}


class NativeNotebookTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = projection()
        self.output = self.root / "package"
        EXPORTER["export"](self.data, self.output)

    def test_protocol_and_native_reader_use_same_export_without_producer_installed(self):
        package = load_package(self.output)
        self.assertTrue(package.report.valid, package.report.to_dict())
        state, raw = read_source(self.output, "selected-1")
        self.assertEqual(state["status"], "READY", state)
        self.assertEqual(json.loads(raw), self.data)
        self.assertEqual(restore_projection(state["entries"]), self.data)
        self.assertEqual(state["revision"], "test-invented-revision")
        self.assertEqual(state["scientific_approval"], "NOT_EVALUATED")
        rows = [e for e in state["entries"] if e["kind"] == "row"]
        self.assertEqual(rows[0]["cells"]["Inteiro"]["text"], "9007199254740993")
        self.assertEqual(rows[0]["cells"]["Ausente"]["type"], "null")
        self.assertNotIn("Ausente", rows[1]["cells"])
        records = [e for e in state["entries"] if e["kind"] == "record"]
        self.assertNotEqual(records[0]["uid"], records[1]["uid"])
        nodes = [e for e in state["entries"] if e["kind"] == "node"]
        self.assertIsNone(nodes[0]["native_id"])
        self.assertEqual(nodes[1]["parent_uid"], nodes[0]["uid"])

    def test_every_field_roundtrips_without_mutating_projection_or_package(self):
        before = EXPORTER["dump"](self.data)
        files = {p.relative_to(self.output).as_posix(): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        catalog = Catalog([self.output])
        for _ in range(2):
            report = snapshot(catalog)
            self.assertEqual(report["sources"][0]["status"], "READY")
        self.assertEqual(EXPORTER["dump"](self.data), before)
        self.assertEqual(files, {p.relative_to(self.output).as_posix(): p.read_bytes() for p in self.output.rglob("*") if p.is_file()})

    def test_tampered_payload_invalidates_whole_source(self):
        payload = self.output / "data/view-0000.json"
        payload.write_bytes(payload.read_bytes() + b" ")
        state, raw = read_source(self.output, "selected")
        self.assertEqual(state["status"], "INVALID")
        self.assertEqual(state["entries"], [])
        self.assertIsNone(raw)

    def test_zip_uses_same_readonly_protocol(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for p in self.output.rglob("*"):
                if p.is_file(): z.write(p, "snapshot/" + p.relative_to(self.output).as_posix())
        state, raw = read_source(archive, "zip")
        self.assertEqual(state["status"], "READY", state)
        self.assertEqual(json.loads(raw), self.data)

    def test_existing_destination_and_source_overlap_rejected(self):
        with self.assertRaises(FileExistsError): EXPORTER["export"](self.data, self.output)
        with self.assertRaisesRegex(ValueError, "DISJOINT"):
            EXPORTER["export"](self.data, self.output / "nested", forbidden_roots=[self.output])

    def test_chunking_retains_order_and_snapshot(self):
        old = EXPORTER["build_package"].__globals__["MAX_PAYLOAD_BYTES"]
        try:
            EXPORTER["build_package"].__globals__["MAX_PAYLOAD_BYTES"] = 7500
            document, payloads = EXPORTER["build_package"](self.data)
            self.assertGreater(len(payloads), 1)
            entries = []
            for n, raw in enumerate(payloads.values()):
                chunk = json.loads(raw)
                self.assertEqual(chunk["ordinal"], n)
                entries.extend(chunk["entries"])
            self.assertEqual(restore_projection(entries), self.data)
        finally:
            EXPORTER["build_package"].__globals__["MAX_PAYLOAD_BYTES"] = old

    def test_wrong_projection_and_unknown_version_fail_closed(self):
        with self.assertRaises(ValueError): EXPORTER["build_package"]({"not_records": []})
        metadata = self.output / "ro-crate-metadata.json"
        doc = json.loads(metadata.read_text(encoding="utf-8"))
        doc["@graph"][1][EXPORTER["VIEW_NS"] + "version"] = "future"
        metadata.write_bytes(EXPORTER["dump"](doc))
        state, _ = read_source(self.output, "bad")
        self.assertEqual(state["status"], "INVALID")
        self.assertIn("NATIVE_VERSION_UNSUPPORTED", state["errors"])


if __name__ == "__main__":
    unittest.main()
