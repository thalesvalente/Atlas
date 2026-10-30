"""Exercise the isolated harness and its actual HTTP/source boundaries."""
import hashlib
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("p03_harness", ROOT / "scripts/qa/atlas_parity02_p03_harness.py")
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


class HarnessStreamTests(unittest.TestCase):
    """Real handler/parser with a byte-stream test double, not a socket/browser."""
    def request(self, route, method="GET", headers=None):
        class Stream:
            def __init__(self, payload):
                self.input = io.BytesIO(payload)
                self.output = bytearray()

            def makefile(self, *args):
                return self.input

            def sendall(self, data):
                self.output.extend(data)

        fields = {"Host": "127.0.0.1:8766", **(headers or {})}
        raw = f"{method} {route} HTTP/1.0\r\n" + "".join(f"{k}: {v}\r\n" for k, v in fields.items()) + "\r\n"
        stream = Stream(raw.encode("ascii"))
        HARNESS.handler_class()(stream, ("127.0.0.1", 8000), SimpleNamespace(server_address=("127.0.0.1", 8766)))
        response_stream = Stream(bytes(stream.output))
        response = http.client.HTTPResponse(response_stream)
        response.begin()
        return response.status, dict(response.getheaders()), response.read()

    def test_handler_parser_serves_only_fixed_resources(self):
        for route, expected in HARNESS.resources().items():
            with self.subTest(route=route):
                status, headers, body = self.request(route)
                self.assertEqual(status, 200)
                self.assertEqual((body, headers["Content-Type"]), expected)
                self.assertEqual(headers["Content-Security-Policy"], HARNESS.CSP)
                self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

    def test_no_payload_traversal_catalog_or_arbitrary_files(self):
        for route in ("/data/result.csv", "/report.pdf", "/api/catalog", "/../AGENTS.md",
                      "/%2e%2e/AGENTS.md", "/artifact-read-model.json", "/https://example.invalid/payload"):
            with self.subTest(route=route):
                self.assertEqual(self.request(route)[0], 404)

    def test_cross_origin_and_wrong_host_are_rejected(self):
        for headers in ({"Host": "example.invalid"}, {"Origin": "https://example.invalid"},
                        {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.request("/demo-data.js", headers=headers)[0], 403)

    def test_mutation_methods_cannot_write(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertEqual(self.request("/", method=method)[0], 405)

    def test_fixture_transport_preserves_numbers_and_inert_text(self):
        status, _, module = self.request("/demo-data.js")
        self.assertEqual(status, 200)
        data = json.loads(module.decode()[len("export default "):-2])
        self.assertEqual(data, HARNESS.demo_data())
        self.assertEqual(data["table"]["rows"][0]["cells"]["count"], "9007199254740993")
        self.assertIn("<img", str(data["metadata"]))
        self.assertTrue(data["document"]["synthetic"])

    def test_reading_harness_keeps_fixture_bytes(self):
        paths = sorted(HARNESS.FIXTURES.glob("*.json"))
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        HARNESS.resources()
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(before, after)

    def test_C4_app_loads_only_representable_p03_components(self):
        """C4 explicitly replaces C2's historical shell-isolation assertion."""
        app = (HARNESS.STATIC / "app.js").read_text(encoding="utf-8")
        index = (HARNESS.STATIC / "index.html").read_text(encoding="utf-8")
        composition = (HARNESS.STATIC / "parity03_p03_composition.js").read_text(encoding="utf-8")
        self.assertIn("from './parity03_p03_composition.js'", app)
        self.assertIn('type="module" src="/app.js"', index)
        for name in ("parity02_p03_table", "parity02_p03_artifacts"):
            self.assertIn('href="/' + name + '.css"', index)
            self.assertIn("from './" + name + ".js'", composition)
        self.assertIn("renderMetadata", composition)
        self.assertIn("renderTable", composition)
        for text in (app, index, composition):
            for rich in ("renderCandidate", "validateCandidate", "p03-candidate/1"):
                self.assertNotIn(rich, text)


@unittest.skipIf(os.environ.get("P03_SKIP_LOOPBACK_REASON"),
                 "LOOPBACK_NOT_RUN: " + os.environ.get("P03_SKIP_LOOPBACK_REASON", ""))
class HarnessHTTPTests(unittest.TestCase):
    """Actual socket test. Explicit environmental skip must never count as PASS."""
    @classmethod
    def setUpClass(cls):
        cls.server = HARNESS.make_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, route, method="GET", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=3)
        try:
            connection.request(method, route, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_real_http_serves_only_fixed_resources(self):
        for route, expected in HARNESS.resources().items():
            with self.subTest(route=route):
                status, headers, body = self.request(route)
                self.assertEqual(status, 200)
                self.assertEqual((body, headers["Content-Type"]), expected)
                self.assertEqual(headers["Content-Security-Policy"], HARNESS.CSP)
                self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

    def test_no_payload_traversal_catalog_or_arbitrary_files(self):
        for route in ("/data/result.csv", "/report.pdf", "/api/catalog", "/../AGENTS.md",
                      "/%2e%2e/AGENTS.md", "/artifact-read-model.json", "/https://example.invalid/payload"):
            with self.subTest(route=route):
                self.assertEqual(self.request(route)[0], 404)

    def test_cross_origin_and_wrong_host_are_rejected(self):
        for headers in ({"Host": "example.invalid"}, {"Origin": "https://example.invalid"},
                        {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.request("/demo-data.js", headers=headers)[0], 403)

    def test_mutation_methods_cannot_write(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertEqual(self.request("/", method=method)[0], 405)

    def test_fixture_transport_preserves_numbers_and_inert_text(self):
        status, _, module = self.request("/demo-data.js")
        self.assertEqual(status, 200)
        data = json.loads(module.decode()[len("export default "):-2])
        self.assertEqual(data, HARNESS.demo_data())
        self.assertEqual(data["table"]["rows"][0]["cells"]["count"], "9007199254740993")
        self.assertIn("<img", str(data["metadata"]))
        self.assertTrue(data["document"]["synthetic"])



if __name__ == "__main__":
    unittest.main()
