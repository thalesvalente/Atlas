"""Run the P02 synthetic browser proof from an installed consumer, without polling.

Example: INSTALLED_PYTHON -I atlas_parity02_p02_run_browser.py --report REPORT.json
The two fixture packages are read directly, hashed before/after, never rewritten.
The server is this process's loopback-only child thread; no host service is used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import threading

import atlas_viewer
import caderno_protocol
from atlas_viewer.catalog import Catalog
from atlas_viewer.server import make_server


def hashes(sources):
    return {source.name: {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(source.rglob("*")) if path.is_file()}
            for source in sources}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--code-sha", default="UNSPECIFIED")
    args = parser.parse_args()
    repo = args.repo.resolve()
    report_path = args.report.resolve()
    viewer_location = Path(atlas_viewer.__file__).resolve()
    protocol_location = Path(caderno_protocol.__file__).resolve()
    if viewer_location.is_relative_to(repo) or protocol_location.is_relative_to(repo):
        raise RuntimeError("This proof requires SDK/viewer installed outside the source checkout")
    if importlib.util.find_spec("r4") is not None:
        raise RuntimeError("This proof requires an environment without R4")
    fixtures = repo / "tests/fixtures/atlas_parity02/p02"
    sources = [fixtures / "source-a", fixtures / "source-b"]
    before = hashes(sources)
    catalog = Catalog(sources)
    snapshot = catalog.snapshot()
    if not all(source["report"]["valid"] for source in snapshot["sources"]):
        raise RuntimeError("Both public synthetic sources must validate")
    server = make_server(catalog, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    command = ["node", str(repo / "scripts/qa/atlas_parity02_p02_browser.mjs"),
               "--url", f"http://127.0.0.1:{server.server_address[1]}",
               "--report", str(report_path), "--code-sha", args.code_sha]
    if args.screenshots:
        command.extend(["--screenshots", str(args.screenshots.resolve())])
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-p02-consumer-") as directory:
            result = subprocess.run(command, cwd=directory, check=False, timeout=240)
        immutable = hashes(sources) == before
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["consumer"] = {"viewer_import_outside_checkout": True,
                                  "sdk_import_outside_checkout": True,
                                  "r4_installed": False,
                                  "python_optimized": bool(__import__("sys").flags.optimize)}
            report["source_package_sha256"] = before
            report["source_package_bytes_unchanged"] = immutable
            if not immutable:
                report["status"] = "FAIL"
                report["error"] = "Source package bytes changed during browser verification"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result.returncode if immutable else 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
