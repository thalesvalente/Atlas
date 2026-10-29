"""Strict, isolated P03 qualification harness; no Atlas application routes.

The original 25 P03 files remain frozen. The focal embedding stylesheet is
separate and sets a bounded table viewport. Targets match the eight named routes
byte for byte, without URL decoding, wildcard lookup, path normalization, or
filesystem route resolution.
"""
from __future__ import annotations

import argparse
import importlib.util
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
import sys

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "p03_frozen_resources", ROOT / "scripts/qa/atlas_parity02_p03_harness.py")
_FROZEN = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_FROZEN)
# The frozen HTML contains a constant data:, favicon. Permit that local image
# scheme without enabling any remote image, connection, font, or payload source.
CSP = _FROZEN.CSP.replace("img-src 'none'", "img-src data:")
ROUTES = frozenset({"/", "/harness.mjs", "/harness.css", "/demo-data.js",
                    "/parity02_p03_table.js", "/parity02_p03_artifacts.js",
                    "/parity02_p03_table.css", "/parity02_p03_artifacts.css"})


def resources() -> dict[str, tuple[bytes, str]]:
    result = _FROZEN.resources()
    result["/harness.css"] = (Path(__file__).with_suffix(".css").read_bytes(), "text/css; charset=utf-8")
    if set(result) != ROUTES:
        raise RuntimeError("P03 resource allowlist changed")
    return result


def install_loopback_guard(events: list[dict] | None = None) -> None:
    """Deny non-loopback socket operations in this qualification process.

    This is an in-process Python audit guard, not a firewall or host setting.
    It is deliberately installed only by the explicit harness/gate entrypoint.
    """
    sink = events if events is not None else []

    def audit(event: str, args: tuple) -> None:
        if event not in {"socket.connect", "socket.bind", "socket.getaddrinfo"}:
            return
        address = args[0] if event == "socket.getaddrinfo" else args[1]
        host = address if event == "socket.getaddrinfo" else address[0] if isinstance(address, tuple) else None
        allowed = False
        try:
            allowed = bool(host) and ipaddress.ip_address(host).is_loopback
        except (ValueError, TypeError):
            pass
        sink.append({"event": event, "host": host, "allowed": allowed})
        if not allowed:
            raise RuntimeError("P03_LOOPBACK_ONLY: " + event)

    sys.addaudithook(audit)


def handler_class() -> type[BaseHTTPRequestHandler]:
    route_bytes = resources()

    class Handler(BaseHTTPRequestHandler):
        server_version = "AtlasP03QualificationHarness/1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def reply(self, status: int, body: bytes,
                  content_type: str = "text/plain; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self) -> None:
            port = self.server.server_address[1]
            hosts = self.headers.get_all("Host", [])
            origins = self.headers.get_all("Origin", [])
            if (len(hosts) != 1 or hosts[0] != f"127.0.0.1:{port}"
                    or len(origins) > 1
                    or (origins and origins[0] != f"http://127.0.0.1:{port}")
                    or self.headers.get("Sec-Fetch-Site") == "cross-site"):
                self.reply(403, b"LOCAL_ORIGIN_REQUIRED")
                return
            if (self.headers.get_all("Transfer-Encoding")
                    or self.headers.get_all("Content-Length", []) not in ([], ["0"])):
                self.reply(400, b"REQUEST_BODY_NOT_ALLOWED")
                return
            # BaseHTTPRequestHandler normalizes leading // in self.path. Read
            # the original parsed request target so aliases remain rejected.
            parts = self.raw_requestline.decode("iso-8859-1").split()
            target = parts[1] if len(parts) >= 2 else ""
            resource = route_bytes.get(target)
            if resource is None:
                self.reply(404, b"NOT_IN_SYNTHETIC_ALLOWLIST")
                return
            self.reply(200, *resource)

        def do_POST(self) -> None:
            self.reply(405, b"READ_ONLY_SYNTHETIC_HARNESS")

        do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = do_TRACE = do_CONNECT = do_POST

    return Handler


def make_server(port: int = 0) -> ThreadingHTTPServer:
    class LoopbackServer(ThreadingHTTPServer):
        def server_bind(self) -> None:
            # HTTPServer's default performs getfqdn/reverse DNS. This fixture
            # server needs neither DNS nor a name supplied by the environment.
            TCPServer.server_bind(self)
            self.server_name = "127.0.0.1"
            self.server_port = self.server_address[1]

    server = LoopbackServer(("127.0.0.1", port), handler_class())
    server.daemon_threads = True
    return server


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    install_loopback_guard()
    with make_server(args.port) as server:
        info = {"url": f"http://127.0.0.1:{server.server_address[1]}",
                "synthetic": True, "visible_in_main_app": False,
                "scope": "P03_ISOLATED_HARNESS"}
        print(json.dumps(info) if args.json else info["url"], flush=True)
        try:
            server.serve_forever(poll_interval=0.05)
        except KeyboardInterrupt:
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
