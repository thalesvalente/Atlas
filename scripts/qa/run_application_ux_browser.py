"""Qualify the installed application with invented, loss-sensitive fixtures only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
from importlib import resources
import json
import os
from pathlib import Path
import re
import runpy
import socket
import subprocess
import sys
import time
import urllib.request

import atlas_viewer


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fixture():
    rows = []
    for index in range(205):
        cells = {f"C{column:02d}": f"row-{index:03d}/column-{column:02d}" for column in range(65)}
        cells.update(C00=f"row-{index:03d}", C01=9007199254740993 + index,
                     C02="0.123456789012345678901234567890", C03=-0.0,
                     C05="=1+1", C06='comma, quote " and\nnext line', C07=index % 2 == 0,
                     C08=1.2345678901234567, C09=" -2+3", C10="@SUM(1,2)")
        if index % 2 == 0:
            cells["C04"] = None
        else:
            del cells["C04"]
        rows.append({"id": f"row-{index:03d}", "native_id": None, "cells": cells,
                     "evidence": [{"source_id": "synthetic-reference", "exact": 9007199254740993}]})
    table = {"id": "table-main", "label": "Tabela da aplicação", "record_id": "record-root",
             "family": "APPLICATION", "status": "HOLD", "rows": rows}
    long_table = {"id": "table-long", "label": "Tabela de texto integral",
                  "rows": [{"id": "row-long", "cells": {"Texto": "INVENTED_LONG_VALUE_" + "á" * 9000}}]}
    data = {
        "schema": "synthetic-application-ux", "atlas_integration": {"notebook_revision": "INVENTED_APPLICATION_REVISION"},
        "records": [
            {"id": "record-root", "native_id": None, "title": "Registro principal", "family": "APPLICATION", "status": "HOLD", "date": "2026-01-01T12:00:00Z"},
            {"id": "record-no-status", "title": "Registro sem estado", "family": "APPLICATION"},
            {"id": "record-unknown", "title": "Registro UNKNOWN", "status": "UNKNOWN"},
            {"title": "Registro sem ID", "status": None},
            {"id": "record-empty-id", "native_id": "", "title": "Registro com textos vazios", "status": ""}],
        "lineage_graph": {"nodes": [{"key": "root", "native_id": None, "label": "Raiz sintética", "run_id": "record-root"},
                                    {"key": "child", "parent_key": "root", "native_id": "child-native", "label": "Filho sintético", "run_id": "record-root"}], "edges": []},
        "edges": [{"id": "relation-main", "from_key": "record-root", "to": "synthetic-reference", "type": "MENTIONS"}],
        "result_tables": [table, long_table],
        "resources": [{"id": "synthetic-reference", "title": "Dossiê sintético", "uri": "https://example.invalid/never-opened", "availability": "UNKNOWN"}],
        "coverage": {"scope": "INVENTED_DATA_ONLY"}, "empty_collection": [], "global_null": None,
        "global_integer": 9007199254740993,
    }
    empty = {"schema": "synthetic-application-empty", "atlas_integration": {"notebook_revision": "INVENTED_EMPTY_REVISION"},
             "records": [], "lineage_graph": {"nodes": [], "edges": []}, "edges": [], "result_tables": [], "resources": [], "empty_collection": []}
    fallback = {"schema": "synthetic-record-tree-fallback", "atlas_integration": {"notebook_revision": "INVENTED_RECORD_TREE_REVISION"},
                "records": [{"id": "fallback-root", "title": "Registro raiz sem nós"},
                            {"id": "fallback-child", "parent_key": "fallback-root", "title": "Registro filho sem nós"}],
                "lineage_graph": {"nodes": [], "edges": []}, "result_tables": [], "resources": [], "edges": []}
    late = {
        "schema": "synthetic-late-linked-populations", "atlas_integration": {"notebook_revision": "INVENTED_LATE_POPULATIONS_REVISION"},
        "records": [{"id": f"late-record-{index:03d}", "title": f"Registro tardio {index:03d}", "family": "LATE"} for index in range(205)],
        "lineage_graph": {"nodes": [{"key": "late-root", "native_id": None, "label": "Nó de navegação tardia", "family": "ANCHOR",
                                      "run_id": "late-record-157", "resource_id": "late-asset-057",
                                      "source_id": "late-relation-157", "group_id": "late-collection-057"}], "edges": []},
        "resources": [{"id": f"late-asset-{index:03d}", "title": f"Recurso tardio {index:03d}", "family": "LATE"} for index in range(85)],
        "edges": [{"id": f"late-relation-{index:03d}", "title": f"Relação tardia {index:03d}", "type": "MENTIONS", "family": "LATE"} for index in range(205)],
        "invented_collections": [{"id": f"late-collection-{index:03d}", "title": f"Coleção tardia {index:03d}", "family": "LATE"} for index in range(85)],
        "result_tables": [],
    }
    return data, empty, table, long_table, fallback, late


def expected_csv(rows, scalar):
    # Use Python's CSV writer independently of the browser serialization.
    columns = sorted({column for row in rows for column in row["cells"]})
    output = io.StringIO(newline="")
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    def safe(value):
        text = value if isinstance(value, str) else scalar(value)
        return "'" + text if re.match(r"^[\s\x00-\x1f]*[=+@-]", text) else text
    writer.writerow([safe(column) for column in columns])
    for row in rows:
        writer.writerow([safe(row["cells"][column]) if column in row["cells"] else "" for column in columns])
    return output.getvalue().removesuffix("\r\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--require-graph-cancel", action="store_true", required=True,
                        help="Require the composed graph cancellation API and real delayed-callback close regressions.")
    args = parser.parse_args()
    root, work = args.repo.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    report_path = work / "browser-application-report.json"
    candidate_package = (root / "packages/atlas/src/atlas_viewer").resolve()
    installed_package = Path(atlas_viewer.__file__).resolve().parent
    if installed_package.is_relative_to((root / "packages").resolve()):
        raise RuntimeError("APPLICATION_NOT_IMPORTED_FROM_INSTALLED_DISTRIBUTION")
    asset_hashes = {}
    for candidate_path in sorted(candidate_package.rglob("*")):
        if not candidate_path.is_file() or "__pycache__" in candidate_path.parts or candidate_path.suffix in {".pyc", ".pyo"}:
            continue
        relative = candidate_path.relative_to(candidate_package).as_posix()
        candidate = digest(candidate_path.read_bytes())
        installed_path = resources.files("atlas_viewer").joinpath(relative)
        installed = digest(installed_path.read_bytes()) if installed_path.is_file() else None
        asset_hashes[relative] = {"candidate_sha256": candidate, "installed_sha256": installed, "matches": candidate == installed}
    mismatched = [name for name, value in asset_hashes.items() if not value["matches"]]
    if mismatched:
        report_path.write_text(json.dumps({"status": "FAIL", "error": "INSTALLED_APPLICATION_ASSET_DRIFT", "installed_asset_hashes": asset_hashes}, indent=2), encoding="utf-8")
        raise RuntimeError("INSTALLED_APPLICATION_ASSET_DRIFT:" + ",".join(mismatched))
    exporter = runpy.run_path(str(root / "tools/export_native_notebook.py"))
    data, empty, table, long_table, fallback, late = fixture()
    sources = [work / "source-application", work / "source-empty", work / "source-record-tree", work / "source-late-populations"]
    receipt = exporter["export"](data, sources[0])
    exporter["export"](empty, sources[1])
    exporter["export"](fallback, sources[2])
    exporter["export"](late, sources[3])
    entries = exporter["project_to_entries"](data)
    late_entries = exporter["project_to_entries"](late)
    table_entry = next(entry for entry in entries if entry["kind"] == "table" and entry["source_key"] == table["id"])
    table_rows = [entry for entry in entries if entry.get("table_uid") == table_entry["uid"]]
    manifest = {
        "projection_sha256": receipt["projection_sha256"],
        "table_sha256": digest(exporter["dump"](table)),
        "rows_sha256": digest(exporter["dump"](table["rows"])),
        "csv_sha256": digest(expected_csv(table["rows"], exporter["scalar"])),
        "long_table_sha256": digest(exporter["dump"](long_table)),
        "long_text": long_table["rows"][0]["cells"]["Texto"],
        "table_uid": table_entry["uid"],
        "rows": [{"uid": entry["uid"], "pointer": entry["pointer"], "cells": entry["cells"]} for entry in table_rows],
        "columns": sorted({column for row in table["rows"] for column in row["cells"]}),
        "late_targets": {kind: {"uid": target["uid"], "pointer": target["pointer"], "title": target["title"], "source_key": target["source_key"]}
                         for kind, key in (("record", "late-record-157"), ("asset", "late-asset-057"),
                                           ("relation", "late-relation-157"), ("collection", "late-collection-057"))
                         for target in late_entries if target["kind"] == kind and target["source_key"] == key},
        "decimal_coverage": "JSON float plus 30-digit decimal text; Decimal is unsupported by the existing stdlib exporter",
    }
    expected = work / "application-expected.json"
    expected.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    def hashes():
        return {str(path.relative_to(work)): digest(path.read_bytes())
                for source in sources for path in source.rglob("*") if path.is_file()}
    before = hashes()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, "-I", "-m", "atlas_viewer", "serve", "--port", str(port),
                                "--source", str(sources[0]), "--source", str(sources[1]), "--source", str(sources[2]), "--source", str(sources[3])],
                               cwd=work, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("INSTALLED_APPLICATION_SERVER_START_FAILED")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/notebook", timeout=2) as response:
                    snapshot = json.load(response)
                    if len(snapshot["sources"]) != 4 or any(source["status"] != "READY" for source in snapshot["sources"]):
                        raise RuntimeError("SYNTHETIC_APPLICATION_EXPORT_NOT_CONSUMED")
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise TimeoutError("INSTALLED_APPLICATION_SERVER_TIMEOUT")
        browser_command = ["node", str(Path(__file__).with_name("browser_application_ux.mjs")),
                           "--url", f"http://127.0.0.1:{port}/notebook", "--report", str(report_path),
                           "--expected", str(expected), "--synthetic-metadata", str(sources[0] / "ro-crate-metadata.json"),
                           "--require-graph-cancel", "true"]
        result = subprocess.run(browser_command,
                                cwd=root, check=False)
        same = hashes() == before
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            tested_status = subprocess.check_output(["git", "status", "--porcelain", "--",
                                                    "packages/atlas/src/atlas_viewer", "tools/export_native_notebook.py",
                                                    "scripts/qa/run_application_ux_browser.py", "scripts/qa/browser_application_ux.mjs"], cwd=root, text=True).splitlines()
            report.update(source_bytes_unchanged=same,
                          tested_sha=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                          decimal_coverage=manifest["decimal_coverage"], installed_asset_hashes=asset_hashes,
                          installed_module_path=str(Path(atlas_viewer.__file__).resolve()),
                          installed_import_outside_source=True, installed_assets_equal_candidate=not mismatched,
                          tested_files_dirty=bool(tested_status), tested_files_status=tested_status)
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
