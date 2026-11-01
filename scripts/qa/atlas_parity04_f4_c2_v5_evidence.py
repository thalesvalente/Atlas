"""Version-aware evidence for the REAL R4 v5 reader successor, fail-closed.

Historical C2 manifest and its 22 source objects are verified at their
original immutable SHA, never rewritten to accept changed implementation.
Every intermediate commit since that SHA is audited against exact ownership.
The code and QA of this successor still require review independent of author.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".test-output/atlas-parity04-f4-c2"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7"
MANIFEST = "docs/missions/atlas-parity-04/f4-c2-reader/MANIFEST.sha256"
ALLOWED = frozenset({
    ".github/workflows/atlas-parity04-f4-c2-reader.yml",
    "docs/missions/atlas-parity-04/f4-c2-reader/REAL-V5-TRANSFER-AND-IMPLEMENTATION.md",
    "tools/atlas_legacy_presentation/parser.py",
    "tools/atlas_legacy_presentation/legacy_v5.py",
    "tools/atlas_legacy_presentation/legacy_v5_descriptor.py",
    "tests/qa/test_atlas_parity04_f4_c2_real_v5.py",
    "tests/qa/test_atlas_parity04_f4_c2_v5_descriptor.py",
    "scripts/qa/atlas_parity04_f4_c2_v5_evidence.py",
})


def git(*args, raw=False):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=not raw,
    ).strip() if not raw else subprocess.check_output(["git", *args], cwd=ROOT)


def must(ok, code):
    if not ok:
        raise SystemExit(code)


def verify():
    head = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    must(subprocess.run(["git", "merge-base", "--is-ancestor", BASE, head],
                        cwd=ROOT).returncode == 0, "C2_V5_ANCESTRY_INVALID")
    raw = git("show", BASE + ":" + MANIFEST, raw=True)
    must(git("show", "HEAD:" + MANIFEST, raw=True) == raw,
         "C2_V5_HISTORICAL_MANIFEST_CHANGED")
    manifest_count = 0
    manifest_paths = set()
    for line in raw.decode("utf-8").splitlines():
        expected, sep, path = line.partition("  ")
        must(sep == "  " and bool(re.fullmatch(r"[a-f0-9]{64}", expected))
             and path not in manifest_paths and path != MANIFEST
             and not path.startswith("/") and ".." not in path.split("/"),
             "C2_V5_HISTORICAL_MANIFEST_INVALID")
        manifest_paths.add(path)
        source = git("show", BASE + ":" + path, raw=True)
        must(hashlib.sha256(source).hexdigest() == expected,
             "C2_V5_HISTORICAL_BLOB_MISMATCH")
        manifest_count += 1
    # Audit each commit separately: unauthorized modifications cannot be hidden
    # by a later revert producing an apparently harmless final tree.
    revisions = git("rev-list", "--reverse", "--ancestry-path", BASE + ".." + head).splitlines()
    touched = set()
    for revision in revisions:
        parents = git("show", "-s", "--format=%P", revision).split()
        must(len(parents) == 1, "C2_V5_NONLINEAR_HISTORY")
        changed = git("diff", "--name-status", "--no-renames", parents[0], revision).splitlines()
        for line in changed:
            status, sep, path = line.partition("\t")
            must(sep == "\t" and status in ("A", "M")
                 and path in ALLOWED,
                 "C2_V5_UNAUTHORIZED_HISTORY_PATH")
            touched.add(path)
    current = set(git("diff", "--name-only", BASE, head).splitlines())
    must(current == touched and bool(touched), "C2_V5_UNEXPECTED_DELTA")
    for path in current:
        mode = git("ls-tree", "HEAD", "--", path)
        must(mode.startswith("100644 blob "), "C2_V5_UNEXPECTED_MODE")
    workflow = (ROOT / ".github/workflows/atlas-parity04-f4-c2-reader.yml").read_text(encoding="utf-8")
    must("tests/qa/test_atlas_parity04_f4_c2_real_v5.py" in workflow
         and "tests/qa/test_atlas_parity04_f4_c2_v5_descriptor.py" in workflow
         and "scripts/qa/atlas_parity04_f4_c2_v5_evidence.py" in workflow,
         "C2_V5_FOCAL_SUITE_MISSING")
    must(not any(value in workflow for value in ("continue-on-error:", "paths-ignore:",
                                                   "if: false", "|| true")),
         "C2_V5_WORKFLOW_BYPASS")
    return {
        "commit": head, "tree": tree,
        "parents": git("show", "-s", "--format=%P", head).split(),
        "historical": {
            "sha": BASE, "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "manifest_entries_verified": manifest_count,
            "manifest_unchanged_at_head": True,
        },
        "successor": {
            "paths": sorted(touched), "history_commits": len(revisions),
            "ownership": "EXACT_PATHS_FAIL_CLOSED",
        },
    }


if __name__ == "__main__":
    report = verify()
    report.update({
        "profile": "r4-experiment-viewer-v5",
        "source_bytes_real": "NOT_ACCESSED",
        "production_acquisition": "BLOCKED",
        "hard_budget": "HARD_BUDGET_UNVERIFIED",
        "os_isolation": "OS_ISOLATION_UNVERIFIED",
        "reasoning_effective": "UNVERIFIED",
        "python_optimized": bool(sys.flags.optimize),
    })
    xml = OUT / "junit.xml"
    if not xml.is_file():
        raise SystemExit("C2_V5_JUNIT_REQUIRED")
    root = ET.parse(xml).getroot()
    cases = root.findall(".//testcase")
    report["tests"] = {
        "collected": len(cases),
        "passed": sum(t.find("failure") is None and t.find("error") is None
                      and t.find("skipped") is None for t in cases),
        "failed": sum(t.find("failure") is not None or t.find("error") is not None for t in cases),
        "skipped": sum(t.find("skipped") is not None for t in cases),
    }
    ind = OUT / "independence.json"
    if ind.is_file():
        report["independence"] = json.loads(ind.read_text(encoding="utf-8"))["checks"]
    target = OUT / "v5-successor-evidence.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("C2_V5_EVIDENCE=" + json.dumps(report, sort_keys=True, separators=(",", ":")))
    must(report["tests"]["failed"] == 0, "C2_V5_TESTS_FAILED")
    must(report["tests"]["passed"] >= 49, "C2_V5_TESTS_INCOMPLETE")
