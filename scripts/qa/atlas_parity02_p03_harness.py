"""Explicit synthetic P03 demonstration; independent from the Atlas server.

Only the fixed route map is served, in loopback. This is an engineering harness,
not a payload browser, a new application route, or a persisted Caderno reader.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "packages/atlas/src/atlas_viewer/static"
FIXTURES = ROOT / "tests/fixtures/atlas_parity02/p03"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; "
       "connect-src 'none'; img-src 'none'; base-uri 'none'; "
       "frame-ancestors 'none'; form-action 'none'")


def demo_data() -> dict:
    """Read only named synthetic fixtures; never dereference their payload IDs."""
    names = {
        "table": "table-positive.json", "empty": "table-empty.json",
        "malicious": "table-malicious.json", "metadata": "artifact-descriptor.json",
        "document": "document-candidate.json", "product": "artifact-product-candidate.json",
    }
    return {key: json.loads((FIXTURES / name).read_text(encoding="utf-8"))
            for key, name in names.items()}


def resources() -> dict[str, tuple[bytes, str]]:
    files = {
        "/": (Path(__file__).with_suffix(".html"), "text/html; charset=utf-8"),
        "/harness.mjs": (Path(__file__).with_suffix(".mjs"), "text/javascript; charset=utf-8"),
        "/harness.css": (Path(__file__).with_suffix(".css"), "text/css; charset=utf-8"),
    }
    for name in ("parity02_p03_table.js", "parity02_p03_artifacts.js",
                 "parity02_p03_table.css", "parity02_p03_artifacts.css"):
        files["/" + name] = (STATIC / name, "text/css; charset=utf-8" if name.endswith(".css")
                            else "text/javascript; charset=utf-8")
    result = {route: (path.read_bytes(), mime) for route, (path, mime) in files.items()}
    # A separate module avoids injecting JSON into an inline HTML/script context.
    payload = "export default " + json.dumps(demo_data(), ensure_ascii=True, allow_nan=False) + ";\n"
    result["/demo-data.js"] = (payload.encode("utf-8"), "text/javascript; charset=utf-8")
    return result


def handler_class(routes: dict[str, tuple[bytes, str]] | None = None) -> type[BaseHTTPRequestHandler]:
    routes = resources() if routes is None else routes

    class Handler(BaseHTTPRequestHandler):
        server_version = "AtlasP03SyntheticHarness/1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def reply(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            current_port = self.server.server_address[1]
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            if (host not in {f"127.0.0.1:{current_port}", f"localhost:{current_port}"}
                    or self.headers.get("Sec-Fetch-Site") == "cross-site"
                    or (origin is not None and origin != "http://" + host)):
                self.reply(403, b"LOCAL_ORIGIN_REQUIRED")
                return
            resource = routes.get(urlsplit(self.path).path)
            if resource is None:
                self.reply(404, b"NOT_IN_SYNTHETIC_ALLOWLIST")
                return
            self.reply(200, *resource)

        def do_POST(self) -> None:
            self.reply(405, b"READ_ONLY_SYNTHETIC_HARNESS")

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

    return Handler


def make_server(port: int = 0) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", port), handler_class())
    server.daemon_threads = True
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    with make_server(args.port) as server:
        url = f"http://127.0.0.1:{server.server_address[1]}"
        print(json.dumps({"url": url, "synthetic": True, "visible_in_main_app": False})
              if args.json else f"P03 · fixtures sintéticas · {url}", flush=True)
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
