"""Loopback-only presentation server with a fixed source allowlist."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
from urllib.parse import urlsplit

from .catalog import Catalog

ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/parity02_p02_state.js": ("parity02_p02_state.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8")}
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
       "img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")


def make_server(catalog: Catalog, port: int = 8765) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        server_version = "AtlasLocal/0.1"

        def log_message(self, format: str, *args: object) -> None:
            # Avoid printing user-controlled titles, queries or local source paths.
            return

        def _reply(self, status: int, body: bytes, content_type: str = "application/json; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, value: object) -> None:
            self._reply(status, json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8"))

        def _allowed(self, require_origin: bool = False) -> bool:
            server_port = self.server.server_address[1]
            hosts = {f"127.0.0.1:{server_port}", f"localhost:{server_port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            allowed = host in hosts and self.headers.get("Sec-Fetch-Site", "") != "cross-site"
            if origin is not None:
                allowed = allowed and origin == "http://" + host
            elif require_origin:
                allowed = False
            if not allowed:
                self._json(403, {"error": "LOCAL_ORIGIN_REQUIRED"})
            return allowed

        def do_GET(self) -> None:
            if not self._allowed():
                return
            path = urlsplit(self.path).path
            if path in ASSETS:
                name, content_type = ASSETS[path]
                self._reply(200, files("atlas_viewer").joinpath("static", name).read_bytes(), content_type)
            elif path == "/api/catalog":
                self._json(200, catalog.snapshot())
            elif path == "/api/dossier":
                self._json(200, catalog.dossier())
            else:
                self._json(404, {"error": "NOT_FOUND"})

        def do_POST(self) -> None:
            if not self._allowed(require_origin=True):
                return
            if self.path != "/api/reindex":
                self._json(405, {"error": "READ_ONLY_VIEWER"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                size = -1
            if size < 0 or size > 1024 or self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
                self._json(400, {"error": "INVALID_REQUEST"})
                return
            if self.headers.get("Transfer-Encoding"):
                self._json(400, {"error": "UNSUPPORTED_TRANSFER_ENCODING"})
                return
            try:
                data = json.loads(self.rfile.read(size) or b"{}")
            except (ValueError, UnicodeError):
                data = None
            if data != {}:
                self._json(400, {"error": "FIXED_SOURCE_ALLOWLIST"})
                return
            self._json(200, catalog.rebuild())

        def do_PUT(self) -> None:
            self._json(405, {"error": "READ_ONLY_VIEWER"})

        do_DELETE = do_PUT
        do_PATCH = do_PUT
        do_OPTIONS = do_PUT

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server
