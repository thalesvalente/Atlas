"""Run the installed native viewer against the real exporter in a real browser.

Engineering data is invented and labelled; no private corpus is copied to CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
import urllib.request


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--work", type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[2]
    work = args.work.resolve()
    work.mkdir(exist_ok=False)
    tests = runpy.run_path(str(root / "tests/viewer/test_native_notebook.py"))
    exporter = tests["EXPORTER"]
    data = tests["projection"]()
    data["records"][0]["date"] = "2026-01-01T12:00:00Z"
    data["records"][1]["title"] = "<img src=x onerror=window.nativeInjected=1>"
    data["lineage_graph"]["nodes"].extend({"key": "node-" + str(i), "parent_key": "root", "native_id": "native-" + str(i), "label": "Nó " + str(i), "kind": "Run"} for i in range(1200))
    data["lineage_graph"]["nodes"][-1]["label"] = "Último nó da coleção"
    table = data["result_tables"][0]
    table["rows"].extend({"native_id": None, "cells": {"ID": "ROW-" + str(i), "Inteiro": i}} for i in range(125))
    paths = [work / "source-a", work / "source-b"]
    first = exporter["export"](data, paths[0])
    second = tests["projection"]()
    second["atlas_integration"]["notebook_revision"] = "separate-invented-source"
    exporter["export"](second, paths[1])
    def hashes():
        return {str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
                for directory in paths for p in directory.rglob("*") if p.is_file()}
    before = hashes()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]
    command = [sys.executable, "-I", "-m", "atlas_viewer", "serve", "--port", str(port)]
    for source in paths: command += ["--source", str(source)]
    process = subprocess.Popen(command, cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    report_path = work / "browser-native-report.json"
    try:
        for _ in range(100):
            if process.poll() is not None: raise RuntimeError("INSTALLED_NATIVE_SERVER_START_FAILED")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/notebook", timeout=2) as r:
                    model = json.load(r)
                    if len(model["sources"]) != 2 or any(s["status"] != "READY" for s in model["sources"]):
                        raise RuntimeError("NATIVE_EXPORT_NOT_CONSUMED")
                    break
            except OSError: time.sleep(.1)
        else: raise TimeoutError("INSTALLED_NATIVE_SERVER_TIMEOUT")
        result = subprocess.run(["node", str(root / "scripts/qa/browser_native_notebook.mjs"),
                                 "--url", f"http://127.0.0.1:{port}", "--report", str(report_path),
                                 "--expected-digest", first["projection_sha256"]], cwd=root, check=False)
        same = hashes() == before
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["source_bytes_unchanged"] = same
            report["tested_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            report["scope"] = "INSTALLED_NATIVE_UI_ENGINEERING_NOT_PRIVATE_HOST_PARITY"
            if not same: report["status"] = "FAIL"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return result.returncode if same else 1
    finally:
        process.terminate()
        try: process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.communicate(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
