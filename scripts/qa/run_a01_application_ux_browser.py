"""Additional A01 browser gates; installed viewer and real synthetic exporter.

Called by the existing application UX runner. No workflow, protocol or producer
is modified. The data below are invented, never extracted from the private corpus.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
import urllib.request

import atlas_viewer


def fixture():
    rows = []
    for i in range(205):
        rows.append({"id": f"row-{i:03d}", "nucleus_id": "N" if i < 105 else "M",
                     "resource_id": "asset-00", "cells": {
                         "ID": f"RF-{i:03d}", "Nome": f"Linha sintética {i:03d}",
                         "Inteiro": 9007199254740993 + i, "Decimal": "0.123456789012345678901",
                         "Zero": -0.0, "NULL": None, "Fórmula": "=1+1"}})
    tables = [
        {"id": "table-a", "label": "Tabela A", "project": "P", "run_id": "R",
         "stage": "S", "admission": "HOLD", "rows": rows},
        {"id": "table-null", "label": "Tabela NULL", "project": None, "run_id": False,
         "stage": "", "admission": 0, "rows": []},
        {"id": "table-missing", "label": "Tabela ausente", "rows": []},
        {"id": "table-other", "label": "Tabela outra execução", "project": "P", "run_id": "R2",
         "stage": "S", "admission": "HOLD", "rows": [
             {"id": "null-nucleus", "nucleus_id": None, "cells": {"ID": "NULL"}},
             {"id": "empty-nucleus", "nucleus_id": "", "cells": {"ID": "EMPTY"}},
             {"id": "missing-nucleus", "cells": {"ID": "MISSING"}}]},
    ]
    return {"schema": "synthetic-a01-regressions",
            "atlas_integration": {"notebook_revision": "INVENTED_A01_FIX_REVISION"},
            "records": [], "lineage_graph": {"nodes": [], "edges": []}, "edges": [],
            "result_tables": tables,
            "resources": [{"id": f"asset-{i:02d}", "label": f"Documento sintético {i:02d}",
                           "run_id": "R", "stage_id": "S", "status": "HOLD",
                           "uri": "https://example.invalid/never-opened"} for i in range(12)]}


def expected_csv(rows, scalar):
    columns = sorted({k for row in rows for k in row["cells"]})
    output = io.StringIO(newline="")
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    def safe(v):
        text = v if isinstance(v, str) else scalar(v)
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text
    writer.writerow(columns)
    for row in rows:
        writer.writerow([safe(row["cells"][key]) if key in row["cells"] else "" for key in columns])
    return output.getvalue().removesuffix("\r\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root, work = args.repo.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    installed = Path(atlas_viewer.__file__).resolve()
    if installed.is_relative_to(root / "packages"):
        raise RuntimeError("A01_VIEWER_NOT_INSTALLED")
    exporter = runpy.run_path(str(root / "tools/export_native_notebook.py"))
    data = fixture()
    source = work / "source-a01-functional"
    exporter["export"](data, source)
    def hashes():
        return {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob("*") if p.is_file()}
    before = hashes()
    entries = exporter["project_to_entries"](data)
    table = next(e for e in entries if e["kind"] == "table" and e["source_key"] == "table-a")
    rows = sorted((e for e in entries if e.get("table_uid") == table["uid"]), key=lambda e: e["ordinal"])
    expected = {"table_uid": table["uid"], "row_uid": rows[104]["uid"],
                "selected_json": exporter["dump"](data["result_tables"][0]["rows"][:105]).decode("utf-8"),
                "selected_csv": expected_csv(data["result_tables"][0]["rows"][:105], exporter["scalar"])}
    expected_path = work / "a01-expected.json"
    expected_path.write_text(json.dumps(expected, ensure_ascii=False), encoding="utf-8")
    report_path = work / "browser-application-a01-report.json"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, "-I", "-m", "atlas_viewer", "serve", "--port", str(port), "--source", str(source)],
                               cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("A01_INSTALLED_SERVER_FAILED")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/notebook", timeout=2) as response:
                    snapshot = json.load(response)
                    if len(snapshot["sources"]) != 1 or snapshot["sources"][0]["status"] != "READY":
                        raise RuntimeError("A01_SYNTHETIC_SOURCE_NOT_READY")
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise TimeoutError("A01_INSTALLED_SERVER_TIMEOUT")
        result = subprocess.run(["node", str(root / "scripts/qa/browser_application_ux_a01.mjs"),
                                 "--url", f"http://127.0.0.1:{port}/notebook", "--expected", str(expected_path),
                                 "--report", str(report_path)], cwd=root, check=False)
        same = before == hashes()
        if not report_path.exists():
            raise RuntimeError("A01_BROWSER_REPORT_MISSING")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report.update(source_bytes_unchanged=same, installed_import_outside_source=True,
                      tested_sha=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip())
        if not same or result.returncode:
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
