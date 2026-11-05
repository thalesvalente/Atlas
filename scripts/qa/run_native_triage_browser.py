"""Run Feature 005 against installed Atlas, real Chromium and invented packages.

No source edits or arbitrary-file browser routes are used. The optional installed
root names an already installed QA target; it never installs dependencies. A fresh
work directory retains source hashes, screenshots, exports and the browser report.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
from importlib import resources
import importlib.util
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
import urllib.request

from make_triage_fixture import fixture, revised_fixture


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--installed-root", type=Path,
                        help="Existing pip --target directory; optional in a normal installed environment.")
    args = parser.parse_args()
    root, work = args.repo.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    report_path = work / "browser-native-triage-report.json"
    if args.installed_root:
        installed_root = args.installed_root.resolve(strict=True)
        if installed_root.is_relative_to(root / "packages"):
            raise RuntimeError("TRIAGE_QA_TARGET_MUST_BE_INSTALLED_OUTSIDE_SOURCE")
        sys.path.insert(0, str(installed_root))
    viewer = importlib.import_module("atlas_viewer")
    installed_module = Path(viewer.__file__).resolve()
    if installed_module.is_relative_to(root / "packages"):
        raise RuntimeError("TRIAGE_VIEWER_NOT_INSTALLED")
    r4_installed = importlib.util.find_spec("r4") is not None
    if r4_installed:
        raise RuntimeError("TRIAGE_QA_REQUIRES_ENVIRONMENT_WITHOUT_R4")
    asset_hashes = {}
    for candidate in sorted((root / "packages/atlas/src/atlas_viewer").rglob("*")):
        if not candidate.is_file() or "__pycache__" in candidate.parts or candidate.suffix in {".pyc", ".pyo"}:
            continue
        relative = candidate.relative_to(root / "packages/atlas/src/atlas_viewer").as_posix()
        installed = resources.files("atlas_viewer").joinpath(relative)
        asset_hashes[relative] = {"candidate_sha256": digest(candidate.read_bytes()),
                                  "installed_sha256": digest(installed.read_bytes()) if installed.is_file() else None}
    mismatched = [name for name, value in asset_hashes.items()
                  if value["candidate_sha256"] != value["installed_sha256"]]
    if mismatched:
        report_path.write_text(json.dumps({"status": "FAIL", "error": "INSTALLED_ASSET_DRIFT",
                                          "mismatched": mismatched, "installed_asset_hashes": asset_hashes}, indent=2), encoding="utf-8")
        raise RuntimeError("TRIAGE_INSTALLED_ASSET_DRIFT:" + ",".join(mismatched))
    exporter = runpy.run_path(str(root / "tools/export_native_notebook.py"))
    data = fixture()
    sources = [work / "source-triage-a", work / "source-triage-b"]
    for projection, source in zip((data, revised_fixture(data)), sources):
        exporter["export"](projection, source)
    entries = exporter["project_to_entries"](data)
    known = {entry["source_key"]: entry for entry in entries
             if entry.get("source_key") and entry["kind"] in {"record", "table", "asset"}}
    expected = {"fixture_scope": "INVENTED_DATA_ONLY", "total_records": len(data["records"]), "bulk_records": 1200,
                "revision_a": "INVENTED_TRIAGE_REVISION_A", "revision_b": "INVENTED_TRIAGE_REVISION_B",
                "uids": {key: entry["uid"] for key, entry in known.items()},
                "raw_json": {key: known[key]["raw_json"] for key in ("run-rf-proof", "state-missing", "hostile-record")},
                "table_json": exporter["dump"](data["result_tables"][0]).decode("utf-8"),
                "table_rows": 39, "ordinary_records": [record["id"] for record in data["records"]]}
    expected_path = work / "triage-expected.json"
    expected_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")

    def hashes():
        return {path.relative_to(work).as_posix(): digest(path.read_bytes())
                for source in sources for path in sorted(source.rglob("*")) if path.is_file()}

    before = hashes()
    (work / "source-hashes-before.json").write_text(json.dumps(before, indent=2), encoding="utf-8")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    if args.installed_root:
        # Explicitly choose only this preinstalled target, even with isolated
        # Python; PYTHONPATH and the checkout cannot silently satisfy imports.
        command = [sys.executable, "-I", "-c",
                   "import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); "
                   "sys.argv[0]='atlas_viewer'; runpy.run_module('atlas_viewer',run_name='__main__')",
                   str(installed_root)]
    else:
        command = [sys.executable, "-I", "-m", "atlas_viewer"]
    command += ["serve", "--port", str(port), "--source", str(sources[0]), "--source", str(sources[1])]
    process = subprocess.Popen(command, cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    result_code = 1
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("TRIAGE_INSTALLED_SERVER_FAILED:" + process.stderr.read().decode("utf-8", errors="replace")[-2000:])
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/notebook", timeout=2) as response:
                    snapshot = json.load(response)
                if len(snapshot["sources"]) != 2 or any(source["status"] != "READY" for source in snapshot["sources"]):
                    raise RuntimeError("TRIAGE_SYNTHETIC_SOURCE_NOT_READY")
                break
            except OSError:
                time.sleep(.1)
        else:
            raise TimeoutError("TRIAGE_SERVER_TIMEOUT")
        result = subprocess.run(["node", str(root / "scripts/qa/browser_native_triage.mjs"),
                                 "--url", f"http://127.0.0.1:{port}/notebook", "--expected", str(expected_path),
                                 "--report", str(report_path)], cwd=root, check=False)
        result_code = result.returncode
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)
        after = hashes()
        (work / "source-hashes-after.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {
            "status": "BLOCKED", "error": "BROWSER_REPORT_NOT_CREATED", "checks": []}
        report.update(source_bytes_unchanged=before == after,
                      source_hashes_before=before, source_hashes_after=after,
                      installed_import_outside_source=True, r4_installed=r4_installed,
                      installed_assets_equal_candidate=not mismatched,
                      installed_module_path=str(installed_module), installed_asset_hashes=asset_hashes,
                      tested_sha=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                      tested_tree=subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True).strip(),
                      tested_files_status=subprocess.check_output(
                          ["git", "status", "--porcelain", "--", "packages/atlas/src/atlas_viewer",
                           "scripts/qa/browser_native_triage.mjs", "scripts/qa/run_native_triage_browser.py",
                           "scripts/qa/make_triage_fixture.py"], cwd=root, text=True).splitlines(),
                      browser_exit_code=result_code)
        if before != after:
            report["status"] = "FAIL"
            result_code = 1
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
