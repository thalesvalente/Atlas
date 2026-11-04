"""Run focused screens/filters/exports against an installed native viewer.

Only invented test data is exported; no source paths or private data are used.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    tests = runpy.run_path(str(root / "tests/viewer/test_native_notebook.py"))
    exporter = tests["EXPORTER"]
    data = tests["projection"]()
    data["records"][0]["title"] = "Registro longo " + "prova " * 60
    data["records"][0]["source_ids"] = ["declared-run-alias"]
    data["records"][0]["resources"] = ["evidence", "unresolved-resource", None]
    data["records"][1]["family"] = "G"
    data["lineage_graph"]["nodes"][1]["run_id"] = "declared-run-alias"
    data["edges"].append({"id": "Composite-key-proof", "from": "evidence",
                           "from_key": ["not-interpreted"], "to_key": "child", "type": "MENTIONS"})
    table = data["result_tables"][0]
    table.update(id="Table-A", label="Tabela extensa " + "coluna de medição " * 35,
                 family="F", status="HOLD", record_id="declared-run-alias")
    table["rows"][0]["id"] = "Row-ID-Only"
    table["rows"][0]["evidence"] = [{"source_id": "invented-source", "quote": "Invented literal evidence", "exact": 9007199254740993}]
    data["result_tables"].append({"id": "Table-B-Only", "label": "Outra tabela",
                                  "family": "G", "status": "UNKNOWN", "rows": [
                                      {"id": "Third-row", "cells": {"Value": "Outro valor"}}]})
    data["resources"][0].update(title="Recurso " + "evidência " * 45,
                                family="Recurso", status="READY")
    data["large_global"] = 9007199254740993
    source = work / "source"
    receipt = exporter["export"](data, source)
    second_source = work / "source-2"
    second = tests["projection"]()
    second["atlas_integration"]["notebook_revision"] = "INVENTED_P02_OTHER_SNAPSHOT"
    exporter["export"](second, second_source)

    def hashes():
        return {str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
                for directory in (source, second_source) for p in directory.rglob("*") if p.is_file()}

    before = hashes()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, "-I", "-m", "atlas_viewer", "serve",
                                "--port", str(port), "--source", str(source), "--source", str(second_source)],
                               cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    report_path = work / "browser-p02-report.json"
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("INSTALLED_P02_SERVER_START_FAILED")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/notebook", timeout=2) as response:
                    snapshot = json.load(response)
                    if len(snapshot["sources"]) != 2 or any(item["status"] != "READY" for item in snapshot["sources"]):
                        raise RuntimeError("P02_EXPORT_NOT_CONSUMED")
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise TimeoutError("INSTALLED_P02_SERVER_TIMEOUT")
        result = subprocess.run(["node", str(root / "scripts/qa/browser_p02_notebook.mjs"),
                                 "--url", f"http://127.0.0.1:{port}/notebook",
                                 "--report", str(report_path),
                                 "--expected-digest", receipt["projection_sha256"],
                                 "--expected-table-digest", hashlib.sha256(exporter["dump"](table)).hexdigest()],
                                cwd=root, check=False)
        same = hashes() == before
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["source_bytes_unchanged"] = same
            report["tested_sha"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            if not same:
                report["status"] = "FAIL"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return result.returncode if same else 1
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
