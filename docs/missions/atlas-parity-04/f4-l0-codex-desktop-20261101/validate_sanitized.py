"""Pure-stdlib strict sanitized-shape check. Never opens scientific sources.

Usage: py -3 -I validate_sanitized.py PATH_TO_LOCAL_SANITIZED_JSON
A schema PASS does NOT authorize publication. Does not access network or Git.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

STATUSES = {
    "NOT_EXECUTED", "F4_L0_PRECHECK_ONLY", "F4_L0_SOURCE_NOT_AUTHORIZED",
    "F4_L0_RECEIPT_NOT_FOUND", "F4_L0_REAL_SOURCE_SHAPE_WITNESSED_SCOPED",
    "F4_L0_STRUCTURAL_GAP_EXACT", "SOURCE_DRIFT",
    "LOCAL_WORKSPACE_UNAVAILABLE", "WORKSPACE_WRITE_BLOCKED",
    "PRIVATE_PAYLOAD_EXPOSURE_UNVERIFIED",
}
COUNTS = {
    "records", "lineage_nodes", "lineage_edges", "table_count",
    "table_rows_total", "unadmitted_rf_rows",
    "resolved_explicit_parent_keys", "unbound_tables",
}
CHECKS = {
    "v5_export_declared", "a10_lineage_declared",
    "source_key_native_id_distinct", "missing_null_distinguished",
}
BASE = "86aec49d793d10c1d0b35db58fda747e0febdb23"
ROOT_KEYS = {
    "schema", "mission", "c2_d_sha", "result", "host_local_verified",
    "workspace_write_probe", "source_authorization", "source_read",
    "source_integrity", "f1_comparison", "proof_scope",
    "observed_counts", "structural_checks", "privacy_review",
    "operator_publication_approval", "gates", "global_archive",
}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def pairs_no_duplicates(items):
    value = {}
    for key, data in items:
        require(key not in value, "DUPLICATE_JSON_KEY")
        value[key] = data
    return value


def one_of(value, options, name):
    require(type(value) is str and value in options, "INVALID_" + name)


def verify(data):
    require(type(data) is dict and set(data) == ROOT_KEYS, "ROOT_KEYS")
    require(data["schema"] == "ap04-f4-l0-codex-sanitized-v1", "SCHEMA")
    require(data["mission"] == "AP04-F4-L0-CODEX-DESKTOP-01", "MISSION")
    require(data["c2_d_sha"] == BASE, "C2D_SHA")
    one_of(data["result"], STATUSES, "RESULT")
    require(type(data["host_local_verified"]) is bool, "HOST_FLAG")
    one_of(data["workspace_write_probe"], {"NOT_RUN", "PASS", "BLOCKED"}, "WRITE_PROBE")
    one_of(data["source_authorization"], {
        "NOT_GRANTED", "GRANTED_LOCALLY_FOR_EXACT_F1_THREE",
        "NOT_NEEDED_RECEIPTS_ONLY"}, "SOURCE_AUTHORIZATION")
    require(type(data["source_read"]) is bool, "READ_FLAG")
    one_of(data["source_integrity"], {
        "NOT_RECHECKED", "MATCH", "DRIFT", "UNVERIFIED"}, "INTEGRITY")
    one_of(data["f1_comparison"], {
        "NOT_RUN", "PASS_SELECTED_SCOPE", "DRIFT", "STRUCTURAL_GAP",
        "UNVERIFIED"}, "F1_COMPARISON")
    require(data["proof_scope"] == "SELECTED_F1_FILES_ONLY", "SCOPE")
    counts = data["observed_counts"]
    require(type(counts) is dict and set(counts) == COUNTS, "COUNT_FIELDS")
    for value in counts.values():
        require(value is None or type(value) is int and value >= 0, "COUNT_TYPE")
    checks = data["structural_checks"]
    require(type(checks) is dict and set(checks) == CHECKS, "CHECK_FIELDS")
    for value in checks.values():
        require(value is None or type(value) is bool, "CHECK_TYPE")
    one_of(data["privacy_review"], {
        "PENDING", "PERFORMED_WITH_FINDINGS",
        "APPROVED_FOR_PUBLICATION", "REJECTED"}, "PRIVACY_REVIEW")
    require(type(data["operator_publication_approval"]) is bool, "PUBLICATION_FLAG")
    require(data["gates"] == {
        "G4": "BLOCKED", "G5": "NOT_EVALUATED", "G6": "NOT_EVALUATED",
        "L1": "NOT_EXECUTED", "C3_dependency_satisfied": False}, "GATES")
    require(data["global_archive"] == "UNKNOWN_UPSTREAM", "GLOBAL_ARCHIVE")
    if data["source_read"]:
        require(data["host_local_verified"], "READ_REQUIRES_LOCAL")
        require(data["source_authorization"] == "GRANTED_LOCALLY_FOR_EXACT_F1_THREE",
                "READ_REQUIRES_AUTHORIZATION")
    if data["result"] == "F4_L0_REAL_SOURCE_SHAPE_WITNESSED_SCOPED":
        require(data["source_read"] and data["source_integrity"] == "MATCH",
                "WITNESS_REQUIRES_INTEGRITY")
        require(data["f1_comparison"] == "PASS_SELECTED_SCOPE",
                "WITNESS_REQUIRES_SELECTED_F1_COMPARISON")
    if data["operator_publication_approval"]:
        require(data["privacy_review"] == "APPROVED_FOR_PUBLICATION",
                "PUBLICATION_REQUIRES_PRIVACY_REVIEW")


def main(argv):
    if len(argv) != 2:
        print("usage: validate_sanitized.py PATH_TO_SANITIZED_JSON", file=sys.stderr)
        return 2
    try:
        file = Path(argv[1])
        require(file.is_file() and file.stat().st_size <= 32768, "FILE_SIZE_OR_TYPE")
        data = json.loads(
            file.read_text(encoding="utf-8"),
            object_pairs_hook=pairs_no_duplicates,
            parse_constant=lambda _v: (_ for _ in ()).throw(ValueError("NONFINITE")))
        verify(data)
        print("SANITIZED_FORMAT_PASS; G4=BLOCKED; NO_AUTOMATIC_PUBLICATION")
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        # Do not echo supplied paths or sensitive source values.
        code = str(exc)
        print("SANITIZED_FORMAT_FAIL: " + (
            code if code.isupper() and len(code) <= 64 else "INVALID_OR_UNREADABLE"),
            file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
