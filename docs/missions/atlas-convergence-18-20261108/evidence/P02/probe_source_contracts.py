"""Public synthetic probes; no HTTP listener, private data or product writes."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

AREA = Path(__file__).resolve().parent
REPO = AREA.parents[1] / "repo"
sys.path[:0] = [str(REPO / "packages/protocol/src"), str(REPO / "packages/atlas/src")]
from atlas_viewer.catalog import Catalog
from atlas_viewer.native_notebook import snapshot, export_source, NativeViewError
from caderno_protocol import load_package

exporter = runpy.run_path(str(REPO / "tools/export_native_notebook.py"))
checks = []

def check(name, actual, expected):
    ok = actual == expected
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})
    if not ok:
        raise AssertionError(name)

with tempfile.TemporaryDirectory(prefix="p02-synthetic-", dir=AREA) as directory:
    tmp = Path(directory)
    a, b = tmp / "A", tmp / "B"
    shutil.copytree(REPO / "examples/environmental/sample", a)
    shutil.copytree(REPO / "examples/environmental/sample", b)
    catalog = Catalog([a, b])
    initial = catalog.snapshot()
    unchanged = catalog.rebuild()
    first_id = initial["sources"][0]["read_model"]["runs"][0]["id"]
    metadata = a / "ro-crate-metadata.json"
    doc = json.loads(metadata.read_text())
    next(row for row in doc["@graph"] if row["@id"] == first_id)["name"] = "P02_CHANGED_SAME_ID"
    metadata.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    verify_changed = catalog.snapshot()
    rebuilt = catalog.rebuild()
    restarted = Catalog([a, b]).snapshot()
    reordered = Catalog([b, a]).snapshot()
    check("verify_retains_original_read_model_before_explicit_rebuild", verify_changed["sources"][0]["read_model"], initial["sources"][0]["read_model"])
    check("verify_marks_changed_source", verify_changed["sources"][0]["status"], "CHANGED")
    check("rebuild_preserves_source_and_run_identifiers", rebuilt["sources"][0]["read_model"]["runs"][0]["id"], first_id)
    check("rebuild_accepts_explicit_new_snapshot", rebuilt["sources"][0]["read_model"]["runs"][0]["name"], "P02_CHANGED_SAME_ID")
    check("unaffected_B_read_model_retained", rebuilt["sources"][1]["read_model"], initial["sources"][1]["read_model"])
    (AREA / "catalog_scenarios.json").write_text(json.dumps({"initial": initial, "unchanged_rebuild": unchanged, "verify_changed": verify_changed, "changed_rebuild": rebuilt, "restarted": restarted, "reordered_restart": reordered}, ensure_ascii=False, indent=2))

    package = tmp / "native"
    data = {"records": [{"id": "r", "title": "Synthetic unchanged", "native_id": None, "number": 9007199254740993, "flag": False, "zero": 0, "missing_test": None}], "coverage": {"status": "UNKNOWN"}}
    exporter["export"](data, package)
    native_catalog = Catalog([package])
    original_native = snapshot(native_catalog)["sources"][0]
    check("native_ready_valid_synthetic_package", original_native["status"], "READY")
    check("native_export_exact_roundtrip", json.loads(export_source(native_catalog, "source-1", original_native["metadata_sha256"])), data)
    check("native_literal_integer_preserved", b"9007199254740993" in export_source(native_catalog, "source-1", original_native["metadata_sha256"]), True)
    changed_doc, changed_payloads = exporter["build_package"]({"records": [{"id": "r", "title": "Synthetic replacement"}]})
    for name, raw in changed_payloads.items():
        (package / name).write_bytes(raw)
    (package / "ro-crate-metadata.json").write_bytes(exporter["dump"](changed_doc))
    changed_native = snapshot(native_catalog)["sources"][0]
    check("native_changed_source_has_no_entries", (changed_native["status"], changed_native["entries"]), ("CHANGED", []))
    try:
        export_source(native_catalog, "source-1", original_native["metadata_sha256"])
        stale_export = "UNEXPECTED_ACCEPT"
    except NativeViewError as exc:
        stale_export = str(exc)
    check("native_stale_export_rejected", stale_export, "NATIVE_SNAPSHOT_CHANGED_OR_INVALID")
    native_catalog.rebuild()
    check("native_rebuild_accepts_new_selected_snapshot", snapshot(native_catalog)["sources"][0]["status"], "READY")

    payload = package / "data/view-0000.json"
    chunk = json.loads(payload.read_bytes())
    entry = next(e for e in chunk["entries"] if e["kind"] == "record")
    entry["native_id"] = "FORGED_PRESENTATION_ID"
    raw = exporter["dump"](chunk)
    payload.write_bytes(raw)
    metadata = package / "ro-crate-metadata.json"
    doc = json.loads(metadata.read_bytes())
    file = next(e for e in doc["@graph"] if e["@id"] == "data/view-0000.json")
    file["cp:sha256"] = hashlib.sha256(raw).hexdigest()
    file["contentSize"] = len(raw)
    metadata.write_bytes(exporter["dump"](doc))
    bad_catalog = Catalog([package])
    before_protocol = bad_catalog.snapshot()["sources"][0]
    bad_native = snapshot(bad_catalog)["sources"][0]
    after_protocol = bad_catalog.snapshot()["sources"][0]
    check("presentation_error_does_not_invalidate_public_protocol", before_protocol["status"], "READY")
    check("forged_presentation_rejected_without_mutating_protocol_read_model", before_protocol, after_protocol)
    check("presentation_error_status_isolated", bad_native["status"], "INVALID")
    check("presentation_error_specific_reason", bad_native["errors"], ["NATIVE_DISPLAY_VALUE_MISMATCH"])
    (AREA / "native_scenarios.json").write_text(json.dumps({"initial": original_native, "changed": changed_native, "bad_presentation": bad_native, "protocol_before": before_protocol, "protocol_after": after_protocol}, ensure_ascii=False, indent=2))

result = {"status": "PASS", "scope": "synthetic in-process Catalog/native reader; NOT browser/HTTP or private-host validation", "baseline_sha": "8f8fe01c3041361aa2607194d66af6a640d834ad", "checks": checks}
(AREA / "source-contract-probes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({"status": result["status"], "checks": len(checks), "check_names": [x["name"] for x in checks]}, ensure_ascii=False))
