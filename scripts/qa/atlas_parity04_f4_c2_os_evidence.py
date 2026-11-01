"""Observe actual JUnit outcome and GitHub SHA; cannot qualify missing tests."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


# The frozen C2-B manifest belongs to its OWN commit. Verify that historical
# object by SHA, without editing or pretending it hashes the current HEAD.
C2_B_FROZEN_SHA = "bc5b634dd05d822983a8b8d5ec9c247bf47b3e4d"
C2_B_MANIFEST_PATH = "docs/missions/atlas-parity-04/f4-c2-os-sandbox/MANIFEST.sha256"
SUCCESSOR_PATHS = frozenset({
    "tools/atlas_legacy_presentation/os_windows_acl.py",
    "tools/atlas_legacy_presentation/os_worker.py",
    "tools/atlas_legacy_presentation/os_supervisor.py",
    "tests/qa/test_atlas_parity04_f4_c2_os_sandbox.py",
    "scripts/qa/atlas_parity04_f4_c2_os_evidence.py",
    ".github/workflows/atlas-parity04-f4-c2-os-sandbox.yml",
})


def _git_bytes(*args: str) -> bytes:
    return subprocess.check_output(
        ["git", *args], timeout=15,
    )


def _git_text(*args: str) -> str:
    return _git_bytes(*args).decode("utf-8", errors="strict").strip()


def verify_successor() -> dict:
    """Fail-closed ancestry and original 15-object manifest under this HEAD."""
    head = _git_text("rev-parse", "HEAD")
    if subprocess.run(
            ["git", "merge-base", "--is-ancestor", C2_B_FROZEN_SHA, head],
            capture_output=True, timeout=15).returncode:
        raise ValueError("C2_B_HISTORY_NOT_DESCENDANT")
    manifest = _git_bytes("show", C2_B_FROZEN_SHA + ":" + C2_B_MANIFEST_PATH)
    if _git_bytes("show", "HEAD:" + C2_B_MANIFEST_PATH) != manifest:
        raise ValueError("C2_B_HISTORICAL_MANIFEST_CHANGED")
    checked = 0
    paths = set()
    for line in manifest.decode("utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, sep, path = line.partition("  ")
        if (sep != "  " or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or not path or path in paths or path == C2_B_MANIFEST_PATH
                or path.startswith("/") or ".." in path.split("/")):
            raise ValueError("C2_B_HISTORICAL_MANIFEST_INVALID")
        paths.add(path)
        original = _git_bytes("show", C2_B_FROZEN_SHA + ":" + path)
        if hashlib.sha256(original).hexdigest() != digest:
            raise ValueError("C2_B_HISTORICAL_MANIFEST_MISMATCH")
        checked += 1
    if checked != 15:
        raise ValueError("C2_B_HISTORICAL_ENTRY_COUNT_CHANGED")
    revisions = _git_text(
        "rev-list", "--reverse", "--ancestry-path",
        C2_B_FROZEN_SHA + ".." + head,
    ).splitlines()
    if not revisions:
        raise ValueError("C2_B_NO_SUCCESSOR")
    visited = set()
    for commit in revisions:
        parents = _git_text("show", "-s", "--format=%P", commit).split()
        if len(parents) != 1:
            raise ValueError("C2_B_NONLINEAR_SUCCESSOR")
        changes = _git_text(
            "diff", "--name-status", "--no-renames", parents[0], commit,
        ).splitlines()
        for changed in changes:
            status, sep, path = changed.partition("\t")
            if (sep != "\t" or status != "M"
                    or path not in SUCCESSOR_PATHS):
                raise ValueError("C2_B_UNAUTHORIZED_SUCCESSOR_PATH")
            visited.add(path)
    changed_final = set(
        _git_text("diff", "--name-only", C2_B_FROZEN_SHA, head).splitlines()
    )
    if not changed_final or changed_final != visited:
        raise ValueError("C2_B_SUCCESSOR_DELTA_MISMATCH")
    for path in changed_final:
        listing = _git_text("ls-tree", "HEAD", "--", path)
        if not listing.startswith("100644 blob "):
            raise ValueError("C2_B_SUCCESSOR_MODE_INVALID")
    return {
        "frozen_sha": C2_B_FROZEN_SHA,
        "frozen_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "historical_manifest_entries": checked,
        "historical_manifest_unchanged": True,
        "successor_commits": len(revisions),
        "changed_paths": sorted(changed_final),
        "current_tree": _git_text("rev-parse", "HEAD^{tree}"),
    }

def main() -> int:
    directory = Path(".test-output/atlas-parity04-f4-c2-os")
    directory.mkdir(parents=True, exist_ok=True)
    junit = directory / "junit.xml"
    metrics = None
    if junit.exists():
        try:
            root = ET.parse(junit).getroot()
            suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
            metrics = {k: sum(int(s.get(k, 0)) for s in suites)
                       for k in ("tests", "errors", "failures", "skipped")}
        except (ValueError, ET.ParseError):
            pass
    executed = metrics["tests"] - metrics["skipped"] if metrics else 0
    expected = os.getenv("ATLAS_CHECKOUT_SHA")
    try:
        git = subprocess.run(["git", "rev-parse", "HEAD"], text=True,
                             capture_output=True, timeout=10, check=True)
        actual = git.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        actual = None
    sha_matches = bool(actual and expected and actual == expected)
    passed = bool(metrics and executed >= 15
                  and metrics["errors"] == 0 and metrics["failures"] == 0
                  and sha_matches)
    successor = None
    successor_error = None
    if passed:
        try:
            successor = verify_successor()
        except (OSError, ValueError, subprocess.SubprocessError,
                UnicodeError) as exc:
            passed = False
            # Only stable error codes, not environment paths or private values.
            successor_error = (str(exc) if isinstance(exc, ValueError)
                               else "C2_B_SUCCESSOR_VERIFICATION_FAILED")
    report = {
        "mission": "AP04-F4-C2-B-OS-SANDBOX-CHAT-01",
        "commit_sha": actual,
        "expected_checkout_sha": expected,
        "trigger_sha": os.getenv("GITHUB_SHA"),
        "checkout_sha_verified": sha_matches,
        "executed_non_skipped": executed,
        "worker_optimize": os.getenv("ATLAS_WORKER_OPTIMIZE"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "runner_os": os.getenv("RUNNER_OS", platform.system()),
        "python": sys.version.split()[0],
        "optimize": sys.flags.optimize,
        "junit": metrics,
        "test_gate": "OBSERVED_PASS" if passed else "OBSERVED_FAILED_OR_MISSING",
        "production_acquisition": "PRODUCTION_ACQUISITION_BLOCKED",
        "host_qualification": "HOST_UNVERIFIED",
        "filesystem_network_windows":
            "OS_PROFILE_NOT_ENFORCED" if sys.platform == "win32"
            else "REQUIRES_OBSERVED_NEGATIVE_TESTS",
        "approval": "C2_B_OS_BLOCKED_EXACT",
        "independent_review": "COPILOT_REVIEW_HAS_UNRESOLVED_FINDINGS",
        "fixtures": "INVENTED_ONLY",
        "historical_successor": successor,
        "historical_successor_error": successor_error,
    }
    (directory / "observed-ci.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"test_gate": report["test_gate"], "junit": metrics,
                      "approval": report["approval"],
                      "sha": report["commit_sha"]}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
