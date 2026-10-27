"""Check installed wheel assets and HTTP allowlisting in engineering CI only."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import zipfile


def probe(work: Path) -> dict:
    import importlib.util
    from importlib.resources import files
    import atlas_viewer
    from atlas_viewer.catalog import Catalog
    from atlas_viewer.server import ASSETS, make_server

    if importlib.util.find_spec("r4") is not None:
        raise RuntimeError("Private producer unexpectedly installed")
    if not Path(atlas_viewer.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Viewer was not imported from the isolated installation")
    wheel_paths = list((work / "wheels").glob("atlas_viewer-*.whl"))
    if len(wheel_paths) != 1:
        raise RuntimeError("Expected exactly one viewer wheel")
    with zipfile.ZipFile(wheel_paths[0]) as wheel:
        packed = {name.removeprefix("atlas_viewer/static/"): wheel.read(name)
                  for name in wheel.namelist()
                  if name.startswith("atlas_viewer/static/") and not name.endswith("/")}
    allowed = {name for name, _ in ASSETS.values()}
    if set(packed) != allowed:
        raise RuntimeError("Wheel static assets differ from the server allowlist")
    server = make_server(Catalog([]), 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    checks = []

    def request(path, headers=None):
        connection = http.client.HTTPConnection(host, port, timeout=5)
        try:
            connection.request("GET", path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    try:
        for route, (name, mime) in ASSETS.items():
            status, headers, body = request(route)
            installed = files("atlas_viewer").joinpath("static", name).read_bytes()
            if status != 200 or body != packed[name] or body != installed:
                raise RuntimeError("Missing or changed packaged asset: " + route)
            if headers.get("Content-Type") != mime:
                raise RuntimeError("Unexpected asset content type: " + route)
            for directive in ("default-src 'none'", "script-src 'self'",
                              "connect-src 'self'", "base-uri 'none'",
                              "frame-ancestors 'none'"):
                if directive not in headers.get("Content-Security-Policy", ""):
                    raise RuntimeError("Missing CSP directive: " + directive)
            if "Access-Control-Allow-Origin" in headers:
                raise RuntimeError("Unexpected cross-origin asset access")
            checks.append({"route": route, "status": 200,
                           "sha256": hashlib.sha256(body).hexdigest()})
        for route in (
            "/static/index.html", "/static/app.js", "/static/unknown.js",
            "/ro-crate-metadata.json", "/packages/protocol/pyproject.toml",
            "/%2e%2e/AGENTS.md", "/../AGENTS.md", "/favicon.ico",
        ):
            if route not in ASSETS and request(route)[0] != 404:
                raise RuntimeError("Non-allowlisted path was served: " + route)
        for headers in (
            {"Host": "untrusted.example"},
            {"Origin": "null"},
            {"Origin": "https://" + str(host) + ":" + str(port)},
            {"Sec-Fetch-Site": "cross-site"},
        ):
            if request("/api/catalog", headers)[0] != 403:
                raise RuntimeError("Foreign origin or host was accepted")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return {
        "status": "PASS_SCOPED", "assets": checks,
        "wheel_sha256": hashlib.sha256(wheel_paths[0].read_bytes()).hexdigest(),
        "isolated_installed_viewer": True, "r4_absent": True,
        "scope": "wheel bytes, fixed HTTP assets, CSP/origin; no browser claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    if args.probe:
        print(json.dumps(probe(work), ensure_ascii=True))
        return 0
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    command = [str(python), "-I", "-X", "utf8"]
    if sys.flags.optimize:
        command.append("-O")
    command.extend([str(Path(__file__).resolve()), "--work", str(work), "--probe"])
    completed = subprocess.run(command, check=True, cwd=work / "outside-source",
                               capture_output=True, text=True, encoding="utf-8")
    report = json.loads(completed.stdout)
    root = Path(__file__).resolve().parents[2]
    report["tested_sha"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    report["optimization"] = sys.flags.optimize
    report["platform"] = sys.platform
    (work / "parity02-p06-wheel-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
