"""Exercise the strict P03 harness over actual loopback sockets; never skip."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
from pathlib import Path
import platform
import subprocess
import sys
import threading

from atlas_parity03_p03_harness import CSP, ROOT, install_loopback_guard, make_server, resources


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_hashes() -> dict[str, str]:
    paths = [ROOT / item["path"] for item in json.loads((ROOT / "docs/missions/atlas-parity-02/p03-components/evidence/FREEZE.json").read_text(encoding="utf-8"))["files"]]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def bind_execution(paths: list[str], head: str) -> dict:
    files = []
    for path in sorted(set(paths)):
        result = subprocess.run(["git", "show", "HEAD:" + path], cwd=ROOT, capture_output=True)
        raw = (ROOT / path).read_bytes()
        files.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(),
                      "matches_head": result.returncode == 0 and result.stdout == raw})
    tracked_clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=ROOT).returncode == 0
    bound = tracked_clean and all(file["matches_head"] for file in files)
    return {"attribution": "GIT_COMMIT" if bound else "PRECOMMIT_UNBOUND",
            "tested_sha": head if bound else None, "tracked_worktree_clean": tracked_clean, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = {"status": "FAIL", "scope": "P03_ISOLATED_HARNESS_REAL_HTTP",
               "observed_head_sha": git_value("rev-parse", "HEAD"), "head_tree": git_value("rev-parse", "HEAD^{tree}"),
               "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "platform": platform.platform(),
               "optimization": sys.flags.optimize, "skips": 0, "visible_in_main_app": False,
               "main_server_assets_qualified": False,
               "gate_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "checks": [], "network_events": []}
    before = source_hashes()
    binding = bind_execution([*before, "docs/missions/atlas-parity-02/p03-components/evidence/FREEZE.json",
                              "scripts/qa/atlas_parity03_p03_harness.py",
                              "scripts/qa/atlas_parity03_p03_harness.css",
                              "scripts/qa/atlas_parity03_p03_http.py"], receipt["observed_head_sha"])
    receipt.update(tested_sha=binding["tested_sha"], attribution=binding["attribution"], execution_binding=binding)
    server = thread = None
    try:
        install_loopback_guard(receipt["network_events"])
        server = make_server(0)
        receipt["bind_address"] = list(server.server_address)
        require(server.server_address[0] == "127.0.0.1", "Not bound to loopback")
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()

        def request(target: str, *, method: str = "GET", headers: dict | None = None,
                    body: bytes | None = None, duplicate_host: bool = False):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
            try:
                if duplicate_host:
                    connection.putrequest(method, target)
                    connection.putheader("Host", "example.invalid")
                    connection.endheaders()
                else:
                    connection.request(method, target, body=body, headers=headers or {})
                response = connection.getresponse()
                return response.status, dict(response.getheaders()), response.read()
            finally:
                connection.close()

        expected = resources()
        for route, (body, mime) in sorted(expected.items()):
            status, headers, actual = request(route)
            require(status == 200 and actual == body, "Resource bytes/status differ: " + route)
            require(headers.get("Content-Type") == mime, "MIME differs: " + route)
            require(headers.get("Content-Security-Policy") == CSP, "CSP differs: " + route)
            require(headers.get("X-Content-Type-Options") == "nosniff", "nosniff missing")
            require(headers.get("Cache-Control") == "no-store", "Cache policy changed")
            require(int(headers["Content-Length"]) == len(body), "Incorrect content length")
            receipt["checks"].append({"kind": "resource", "route": route, "status": status,
                                      "mime": mime, "sha256": hashlib.sha256(actual).hexdigest()})
        targets = ["/*", "/parity02_p03_*.js", "/scripts/qa/", "/../AGENTS.md",
                   "/%2e%2e/AGENTS.md", "/%252e%252e/AGENTS.md", "/harness.mjs/../harness.css",
                   "/harness.mjs?payload=1", "/harness.mjs#fragment", "/?x=1", "/%68arness.mjs",
                   "//harness.mjs", "/./harness.mjs", "/harness.mjs/", "/\\harness.mjs",
                   "/data/result.csv", "/report.pdf", "/api/catalog", "/api/payload",
                   "/artifact-read-model.json", "/unknown", "/favicon.ico",
                   "http://example.invalid/harness.mjs",
                   f"http://127.0.0.1:{server.server_address[1]}/harness.mjs"]
        for target in targets:
            # Explicit Host keeps absolute-form negative focused on route matching.
            status, headers, body = request(target, headers={"Host": f"127.0.0.1:{server.server_address[1]}"})
            require(status == 404 and body == b"NOT_IN_SYNTHETIC_ALLOWLIST", "Unknown/alias target accepted: " + target)
            require(headers.get("Content-Security-Policy") == CSP, "Negative response missing CSP")
            receipt["checks"].append({"kind": "negative_route", "route": target, "status": status})
        for header in ({"Host": "example.invalid"}, {"Origin": "https://example.invalid"},
                       {"Sec-Fetch-Site": "cross-site"}):
            require(request("/", headers=header)[0] == 403, "Cross origin request accepted")
            receipt["checks"].append({"kind": "negative_origin", "header": header, "status": 403})
        require(request("/", duplicate_host=True)[0] == 403, "Duplicate Host accepted")
        receipt["checks"].append({"kind": "duplicate_host", "status": 403})
        for method in ("POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"):
            require(request("/", method=method)[0] == 405, "Mutation/unsupported method accepted: " + method)
            receipt["checks"].append({"kind": "negative_method", "method": method, "status": 405})
        require(request("/", body=b"payload")[0] == 400, "GET body accepted")
        receipt["checks"].append({"kind": "get_body", "status": 400})
        require(request("/", headers={"Transfer-Encoding": "chunked"})[0] == 400, "Transfer-Encoding accepted")
        receipt["checks"].append({"kind": "transfer_encoding", "status": 400})
        data = json.loads(request("/demo-data.js")[2].decode("utf-8")[len("export default "):-2])
        require(data["table"]["rows"][0]["cells"]["count"] == "9007199254740993", "Large integer changed in transport")
        require(data["document"]["synthetic"] is True and data["product"]["synthetic"] is True,
                "Demonstrators lost synthetic marker")
        receipt["checks"].append({"kind": "typed_transport_and_synthetic_markers", "status": "PASS"})
        after = source_hashes()
        require(after == before, "Frozen P03 source/fixture bytes changed")
        require(all(event["allowed"] for event in receipt["network_events"]), "External network operation observed")
        receipt.update(status="PASS", real_socket=True, source_bytes_unchanged=True,
                       source_sha256=after, request_count=len(receipt["checks"]),
                       external_network_operations=0, network_policy="in-process Python audit guard; loopback IPs only")
    except Exception as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
    finally:
        if server is not None:
            if thread is not None:
                server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("status", "scope", "tested_sha", "attribution", "optimization", "skips")}, indent=2))
    if receipt["status"] != "PASS":
        print(receipt.get("error", "HTTP qualification failed"), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
