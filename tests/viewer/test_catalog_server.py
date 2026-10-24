"""Behavioral checks of the installed viewer boundary and derived index."""
from __future__ import annotations

import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import threading
import unittest
import zipfile

from atlas_viewer.catalog import Catalog, MAX_SOURCES
from atlas_viewer.server import make_server

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


def digests(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        shutil.copytree(REPO / "examples/environmental/sample", self.source)
        self.addCleanup(self.tmp.cleanup)

    def test_installed_read_and_reindex_never_write_source(self):
        before = digests(self.source)
        catalog = Catalog([self.source])
        snapshot = catalog.snapshot()
        self.assertEqual(snapshot["sources"][0]["status"], "READY")
        self.assertEqual(len(snapshot["sources"][0]["read_model"]["runs"]), 4)
        self.assertEqual(catalog.dossier()["kind"], "ATLAS_DERIVED_DOSSIER")
        self.assertEqual(catalog.rebuild()["generation"], 2)
        self.assertEqual(digests(self.source), before)

    def test_metadata_change_does_not_silently_change_cached_records(self):
        catalog = Catalog([self.source])
        old = catalog.snapshot()["sources"][0]["name"]
        meta = self.source / "ro-crate-metadata.json"
        document = json.loads(meta.read_text(encoding="utf-8"))
        document["@graph"][1]["name"] = "New explicit source version"
        meta.write_text(json.dumps(document), encoding="utf-8")
        observed = catalog.snapshot()["sources"][0]
        self.assertEqual(observed["status"], "CHANGED")
        self.assertEqual(observed["name"], old)
        rebuilt = catalog.rebuild()["sources"][0]
        self.assertFalse(rebuilt["changed"])
        self.assertEqual(rebuilt["name"], "New explicit source version")

    def test_payload_tampering_detected_and_reindex_does_not_promote_it(self):
        catalog = Catalog([self.source])
        (self.source / "data/water.csv").write_bytes(b"tampered")
        self.assertTrue(catalog.snapshot()["sources"][0]["changed"])
        fresh = catalog.rebuild()["sources"][0]
        self.assertEqual(fresh["status"], "INVALID")
        self.assertIsNone(fresh["read_model"])
        self.assertEqual(fresh["scientific_approval"], "NOT_EVALUATED")

    def test_source_scoping_preserves_ids_instead_of_deduplication(self):
        other = self.root / "second"
        shutil.copytree(self.source, other)
        data = Catalog([self.source, other]).snapshot()
        self.assertEqual(len(data["sources"]), 2)
        self.assertEqual(sum(len(s["read_model"]["runs"]) for s in data["sources"]), 8)
        self.assertTrue(data["collisions"])
        self.assertNotEqual(data["sources"][0]["id"], data["sources"][1]["id"])

    def test_returned_projection_is_not_the_internal_index(self):
        catalog = Catalog([self.source])
        data = catalog.snapshot()
        data["sources"][0]["read_model"]["runs"].clear()
        self.assertEqual(len(catalog.snapshot()["sources"][0]["read_model"]["runs"]), 4)

    def test_empty_and_inaccessible_sources_do_not_fabricate_runs(self):
        self.assertEqual(Catalog([]).snapshot()["sources"], [])
        source = Catalog([self.root / "absent"]).snapshot()["sources"][0]
        self.assertEqual(source["status"], "UNAVAILABLE")
        self.assertIsNone(source["read_model"])

    def test_source_count_is_bounded(self):
        with self.assertRaises(ValueError):
            Catalog([self.source] * (MAX_SOURCES + 1))

    def test_large_integer_has_exact_display_text_and_dossier_bytes(self):
        meta = self.source / "ro-crate-metadata.json"
        document = json.loads(meta.read_text(encoding="utf-8"))
        metric = next(e for e in document["@graph"] if e.get("@type") == "PropertyValue")
        metric.update(value=9007199254740993, **{"cp:valueType": "integer", "unitText": "1", "cp:precision": 0})
        meta.write_text(json.dumps(document), encoding="utf-8")
        catalog = Catalog([self.source])
        source = catalog.snapshot()["sources"][0]
        self.assertTrue(source["report"]["valid"])
        observed = source["read_model"]["runs"][0]["metrics"][0]
        self.assertEqual(observed["value"], 9007199254740993)
        self.assertEqual(observed["display_value"], "9007199254740993")
        self.assertIn('9007199254740993', json.dumps(catalog.dossier()))

    def test_corrupt_zip_does_not_hide_other_sources_or_invent_payload_availability(self):
        before = digests(self.source)
        for member in ("ro-crate-metadata.json", "data/water.csv"):
            with self.subTest(corrupt_member=member):
                archive = self.root / ("bad-metadata.zip" if member.endswith(".json") else "bad-payload.zip")
                with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
                    for path in self.source.rglob("*"):
                        if path.is_file():
                            stream.write(path, path.relative_to(self.source).as_posix())
                with zipfile.ZipFile(archive) as stream:
                    info = stream.getinfo(member)
                raw = bytearray(archive.read_bytes())
                name_length, extra_length = struct.unpack_from("<HH", raw, info.header_offset + 26)
                raw[info.header_offset + 30 + name_length + extra_length] = 0xff
                archive.write_bytes(raw)
                corrupt_bytes = archive.read_bytes()
                catalog = Catalog([self.source, archive])
                for observed in (catalog.snapshot(), catalog.dossier(), catalog.rebuild()):
                    self.assertEqual(len(observed["sources"]), 2)
                    good, damaged = observed["sources"]
                    self.assertEqual(good["status"], "READY")
                    self.assertEqual(len(good["read_model"]["runs"]), 4)
                    if member.endswith(".json"):
                        self.assertEqual(damaged["status"], "INVALID")
                        self.assertIsNone(damaged["read_model"])
                        self.assertIn("SOURCE_INVALID", {e["code"] for e in damaged["report"]["errors"]})
                    else:
                        self.assertEqual(damaged["status"], "READY")
                        self.assertEqual(len(damaged["read_model"]["runs"]), 4)
                        self.assertIn("PAYLOAD_UNAVAILABLE", {e["code"] for e in damaged["report"]["warnings"]})
                self.assertEqual(archive.read_bytes(), corrupt_bytes)
        self.assertEqual(digests(self.source), before)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog([])
        self.server = make_server(self.catalog, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.host = f"127.0.0.1:{self.port}"
        self.addCleanup(self.close)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        result = (response.status, dict(response.getheaders()), response.read())
        conn.close()
        return result

    def test_packaged_assets_and_catalog(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Atlas", body)
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        status, _, body = self.request("GET", "/api/catalog")
        self.assertEqual(json.loads(body)["sources"], [])

    def test_dns_rebinding_and_cross_origin_are_rejected(self):
        self.assertEqual(self.request("GET", "/api/catalog", headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request("GET", "/api/catalog", headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.request("GET", "/api/catalog", headers={"Sec-Fetch-Site": "cross-site"})[0], 403)

    def test_only_fixed_source_reindex_is_allowed(self):
        headers = {"Origin": "http://" + self.host, "Content-Type": "application/json"}
        self.assertEqual(self.request("POST", "/api/reindex", "{}", headers)[0], 200)
        self.assertEqual(self.request("POST", "/api/reindex", '{"source":"/private"}', headers)[0], 400)
        self.assertEqual(self.request("POST", "/api/reindex", "{}")[0], 403)
        self.assertEqual(self.request("POST", "/api/execute", "{}", headers)[0], 405)

    def test_no_path_serving_or_scientific_mutation_endpoints(self):
        for path in ["/../pyproject.toml", "/%2e%2e/pyproject.toml", "/api/approve", "/api/delete", "/api/run"]:
            self.assertEqual(self.request("GET", path)[0], 404)
        for method in ["PUT", "DELETE", "PATCH"]:
            self.assertEqual(self.request(method, "/api/catalog")[0], 405)


if __name__ == "__main__":
    unittest.main()
