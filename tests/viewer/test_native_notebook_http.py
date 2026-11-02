"""HTTP integration of native source snapshots, fixed allowlists and exports."""
from __future__ import annotations
import http.client
import json
from pathlib import Path
import runpy
import tempfile
import threading
import unittest

from atlas_viewer.catalog import Catalog
from atlas_viewer.server import make_server

ROOT = Path(__file__).resolve().parents[2]
EXPORTER = runpy.run_path(str(ROOT / "tools/export_native_notebook.py"))


class NativeHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / "package"
        self.data = {"records": [{"id": "one", "kind": "Run", "title": "<script>not executed</script>", "number": 9007199254740993}], "coverage": {"status": "UNKNOWN"}}
        EXPORTER["export"](self.data, self.package)
        self.server = make_server(Catalog([self.package]), 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.addCleanup(self.close)

    def close(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        answer = response.status, dict(response.getheaders()), response.read()
        conn.close()
        return answer

    def get(self, path, headers=None):
        return self.request("GET", path, headers=headers)

    def test_native_page_is_not_an_iframe_and_uses_strict_csp(self):
        status, headers, raw = self.get("/notebook")
        self.assertEqual(status, 200)
        self.assertNotIn(b"<iframe", raw)
        self.assertNotIn("unsafe-inline", headers["Content-Security-Policy"])
        self.assertIn(b"native_notebook.js", raw)
        for asset in ("native_notebook.js", "native_graph.js", "native_rebuild.js", "native_notebook.css", "parity02_p03_table.js"):
            self.assertEqual(self.get("/" + asset)[0], 200)
        self.assertIn(b'href="/notebook"', self.get("/")[2])

    def test_export_is_bound_to_selected_source_and_snapshot(self):
        status, _, raw = self.get("/api/notebook")
        self.assertEqual(status, 200)
        source = json.loads(raw)["sources"][0]
        self.assertEqual(source["status"], "READY")
        route = "/api/notebook/export?source=source-1&snapshot=" + source["metadata_sha256"]
        status, _, result = self.get(route)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(result), self.data)
        self.assertIn(b"9007199254740993", result)
        self.assertEqual(self.get("/api/notebook/export?source=../../private&snapshot=x")[0], 409)
        self.assertEqual(self.get("/api/notebook?path=/private")[0], 400)
        self.assertEqual(self.get("/api/notebook/export?source=a&source=b&snapshot=c")[0], 400)
        self.assertEqual(self.get("/api/notebook", {"Origin": "https://example.invalid"})[0], 403)
        self.assertEqual(self.get("/api/notebook", {"Host": "evil.invalid"})[0], 403)
        payload = self.package / "data/view-0000.json"
        payload.write_bytes(b"corrupt")
        self.assertEqual(self.get(route)[0], 409)
        state = json.loads(self.get("/api/notebook")[2])["sources"][0]
        self.assertEqual(state["status"], "CHANGED")
        self.assertEqual(state["entries"], [])

    def test_valid_replacement_is_visible_only_after_explicit_same_origin_reindex(self):
        metadata = self.package / "ro-crate-metadata.json"
        doc, payloads = EXPORTER["build_package"]({"records": [{"id": "replacement"}]})
        for name, raw in payloads.items(): (self.package / name).write_bytes(raw)
        metadata.write_bytes(EXPORTER["dump"](doc))
        before = json.loads(self.get("/api/notebook")[2])["sources"][0]
        self.assertEqual(before["status"], "CHANGED")
        self.assertEqual(before["entries"], [])
        self.assertEqual(self.request("POST", "/api/reindex", "{}", {"Content-Type": "application/json"})[0], 403)
        status, _, _ = self.request("POST", "/api/reindex", "{}", {
            "Content-Type": "application/json", "Origin": f"http://127.0.0.1:{self.port}"})
        self.assertEqual(status, 200)
        after = json.loads(self.get("/api/notebook")[2])["sources"][0]
        self.assertEqual(after["status"], "READY")
        self.assertEqual(next(e["native_id"] for e in after["entries"] if e["kind"] == "record"), "replacement")


if __name__ == "__main__":
    unittest.main()
