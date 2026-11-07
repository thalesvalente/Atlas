#!/usr/bin/env python3
"""Verify A01 post-transfer destination bytes without rewriting historical authorization."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL = "docs/missions/atlas-a01/REUSE-MANIFEST.json"
SUCCESSOR = "docs/missions/atlas-a01/REUSE-SUCCESSOR-20261107.json"


def fail(reason: str) -> None:
    raise SystemExit("A01_SUCCESSOR_FAIL: " + reason)


def git_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def source(path: str) -> bytes:
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT):
        fail("PATH_ESCAPE " + path)
    return resolved.read_bytes()


def declaration_lines(lines: list[str], symbol: str) -> list[int]:
    pattern = re.compile(
        r"^\s*(?:export\s+)?(?:(?:async\s+)?function|const|let|var)\s+"
        + re.escape(symbol) + r"\b"
    )
    return [number for number, line in enumerate(lines, 1) if pattern.search(line)]


def main() -> None:
    previous_bytes = source(HISTORICAL)
    previous = json.loads(previous_bytes)
    current = json.loads(source(SUCCESSOR))
    if current["schema"] != "atlas-a01-presentation-destination-successor/1":
        fail("INVALID_SCHEMA")
    observed = current["observation"]
    if git_sha(previous_bytes) != observed["original_manifest_blob_sha1"]:
        fail("HISTORICAL_MANIFEST_DRIFT")
    if observed["authorization"] != previous["authorization"]:
        fail("TRANSFER_AUTHORIZATION_MISMATCH")
    allowed = set(previous["destination_sha256"])
    destinations = current["destination_sha256"]
    git_blobs = current["destination_git_blob_sha1"]
    if set(destinations) != allowed or set(git_blobs) != allowed or len(allowed) != 8:
        fail("UNAUTHORIZED_DESTINATION_SET")
    expected_lines = {}
    for path in sorted(allowed):
        raw = source(path)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != destinations[path]:
            fail("DESTINATION_SHA256_DRIFT " + path)
        if git_sha(raw) != git_blobs[path]:
            fail("DESTINATION_GIT_BLOB_DRIFT " + path)
        if b"\r\n" in raw:
            fail("UNEXPECTED_CRLF_DESTINATION " + path)
        expected_lines[path] = raw.decode("utf-8").splitlines()
    original_symbols = [
        (src["source_path"], dst["symbol"], dst["path"])
        for src in previous["transfers"]
        for record in [*src.get("functions", []), *src.get("declarations", [])]
        for dst in record.get("destination_symbols", [])
    ]
    anchors = current["current_declaration_anchors"]
    if len(anchors) != len(original_symbols):
        fail("DECLARATION_COUNT_MISMATCH")
    for entry, original in zip(anchors, original_symbols):
        if (entry["original_source"], entry["symbol"], entry["destination_path"]) != original:
            fail("HISTORICAL_DECLARATION_ORDER_DRIFT")
        path = entry["destination_path"]
        actual = declaration_lines(expected_lines[path], entry["symbol"])
        if actual != entry["current_declaration_lines"]:
            fail("CURRENT_DECLARATION_ANCHOR_DRIFT " + path + ":" + entry["symbol"])
        expected_status = (
            "ABSORBED_OR_RENAMED_NO_DIRECT_DECLARATION" if not actual
            else "DIRECT_DECLARATION_FOUND" if len(actual) == 1
            else "MULTIPLE_DECLARATIONS_REVIEW_REQUIRED"
        )
        if expected_status != entry["current_status"]:
            fail("DECLARATION_STATUS_MISMATCH")
    for critical in current["verified_current_critical_function_ranges"]:
        lines = expected_lines[critical["path"]]
        start, end = critical["start_line"], critical["end_line"]
        if not (1 <= start <= end <= len(lines)):
            fail("OUT_OF_RANGE_CRITICAL_SPAN " + critical["symbol"])
        if not re.search(r"\bfunction\s+" + re.escape(critical["symbol"]) + r"\s*\(",
                         lines[start - 1]):
            fail("CRITICAL_DECLARATION_DRIFT " + critical["symbol"])
        if lines[end - 1].strip() != "}":
            fail("CRITICAL_END_DRIFT " + critical["symbol"])
    print(json.dumps({
        "status": "PASS_SCOPED",
        "historical_transfer_manifest": "UNCHANGED_VERIFIED",
        "authorized_destination_files": len(allowed),
        "declaration_anchor_entries": len(anchors),
        "critical_function_ranges": len(current["verified_current_critical_function_ranges"]),
        "publication_or_scientific_acceptance": "NOT_GRANTED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
