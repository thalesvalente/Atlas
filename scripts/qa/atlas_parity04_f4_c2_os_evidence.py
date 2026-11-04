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
    "tools/atlas_legacy_presentation/os_windows_job.py",
    "tools/atlas_legacy_presentation/os_windows_acl.py",
    "tools/atlas_legacy_presentation/os_worker.py",
    "tools/atlas_legacy_presentation/os_supervisor.py",
    "tests/qa/test_atlas_parity04_f4_c2_os_sandbox.py",
    "scripts/qa/atlas_parity04_f4_c2_os_evidence.py",
    ".github/workflows/atlas-parity04-f4-c2-os-sandbox.yml",
})


JUNIT_CLASS = "tests.qa.test_atlas_parity04_f4_c2_os_sandbox"
REQUIRED_TESTS = frozenset({
    "test_production_denied_even_with_synthetic_override",
    "test_memory_and_wall_budgets_fixed",
    "test_external_paths_cannot_be_passed_to_public_probe",
    "test_preflight_rejects_symlink",
    "test_preflight_rejects_symlinked_ancestor",
    "test_windows_junction_rejected",
    "test_native_memory_challenge",
    "test_linux_os_denials_or_windows_explicit_block",
    "test_monotonic_wall_clock_30s_kills_blocked_worker",
    "test_invalid_modes_and_time_budgets_denied",
    "test_windows_child_inherits_private_scratch_acl",
    "test_report_no_clobber",
    "test_synthetic_source_validated_without_worker_read",
    "test_seccomp_foreign_arch_is_kill_bpf",
    "test_windows_breakaway_denied",
    "test_windows_descendants_killed_in_job",
    "test_windows_association_error_terminates_suspended_worker",
    "test_unrecognized_synthetic_fixture_layout_rejected",
    "test_windows_job_refuses_arbitrary_entrypoint",
    "test_evidence_all_skipped_must_fail",
    "test_evidence_failures_must_exit_nonzero",
    "test_evidence_checkout_sha_mismatch_must_fail",
    "test_direct_worker_refuses_untrusted_paths",
    "test_windows_job_rejects_tampered_argument_vector",
    "test_aarch64_socketpair_is_in_native_seccomp_denyset",
    "test_windows_appcontainer_broker_never_degrades_to_unconfined",
    "test_windows_broker_flags_cannot_authenticate_direct_worker",
    "test_windows_appcontainer_memory_native_limit",
    "test_windows_appcontainer_descendants_killed_at_native_deadline",
    "test_windows_appcontainer_child_escape_has_native_causal_attribution",
    "test_windows_appcontainer_source_rename_denied_after_handle_pin",
    "test_windows_appcontainer_rejects_mutated_source_before_worker",
    "test_windows_appcontainer_assignment_failure_never_resumes_worker",
    "test_windows_broker_has_no_source_read_api_or_handle_transit",
    "test_native_handle_integer_conversion_rejects_forged_or_invalid",
    "test_job_breakaway_classifier_refuses_unrelated_launch_errors",
    "test_forged_synthetic_path_direct_cli_never_opens_source",
    "test_windows_native_child_never_opens_nul_or_uses_popen",
    "test_windows_native_child_classifies_only_createprocess_errors",
    "test_windows_supervisor_crash_kills_worker_and_descendant",
    "test_evidence_only_opposite_os_skips_are_permitted",
    "test_evidence_mandatory_native_skip_fails_with_many_passes",
    "test_evidence_reverted_history_violation_is_not_silenced",
    "test_evidence_pytest_pass_cannot_override_history_failure",
    "test_evidence_frozen_manifest_mutation_rejected",
})
WINDOWS_TESTS = {
    "test_windows_junction_rejected": "Windows junction/reparse-point syscall only",
    "test_windows_child_inherits_private_scratch_acl": "Only Windows can verify child NTFS DACL inheritance",
    "test_windows_breakaway_denied": "Linux denies fork/clone via seccomp",
    "test_windows_descendants_killed_in_job": "Linux denies fork via seccomp",
    "test_windows_association_error_terminates_suspended_worker": "Windows Job only",
    "test_windows_job_refuses_arbitrary_entrypoint": "Windows Job-specific negative contract",
    "test_windows_job_rejects_tampered_argument_vector": "Windows native job API only",
    "test_windows_appcontainer_broker_never_degrades_to_unconfined": "AppContainer requires Windows native kernel",
    "test_windows_broker_flags_cannot_authenticate_direct_worker": "AppContainer process-token test only",
    "test_windows_appcontainer_memory_native_limit": "Native AppContainer limit challenge is Windows-only",
    "test_windows_appcontainer_descendants_killed_at_native_deadline": "Native AppContainer descendants Windows-only",
    "test_windows_appcontainer_child_escape_has_native_causal_attribution": "Native AppContainer child escape Windows-only",
    "test_windows_appcontainer_source_rename_denied_after_handle_pin": "Native Windows handle-sharing rule only",
    "test_windows_appcontainer_rejects_mutated_source_before_worker": "Native Windows source broker only",
    "test_windows_appcontainer_assignment_failure_never_resumes_worker": "Native Windows fault injection only",
    "test_windows_native_child_never_opens_nul_or_uses_popen": "Windows native process creation only",
    "test_windows_native_child_classifies_only_createprocess_errors": "Windows native process creation only",
    "test_windows_supervisor_crash_kills_worker_and_descendant": "Windows Job kill-on-close native counterproof only"
}
LINUX_TESTS = {
    "test_seccomp_foreign_arch_is_kill_bpf": "Seccomp BPF code structure applicable to Linux only",
    "test_aarch64_socketpair_is_in_native_seccomp_denyset": "Linux seccomp structural test"
}


class HistoryVerificationError(ValueError):
    def __init__(self, receipt: dict):
        self.receipt = receipt
        super().__init__(receipt["errors"][0]["code"])


def _raw_changes(parent: str, commit: str) -> list[dict]:
    fields = _git_bytes(
        "diff", "--raw", "-z", "--no-renames", "--no-abbrev",
        parent, commit, "--").split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) % 2:
        raise ValueError("C2_B_RAW_DIFF_INVALID")
    changes = []
    for index in range(0, len(fields), 2):
        header = fields[index].decode("ascii").split()
        if (len(header) != 5 or not header[0].startswith(":")
                or not re.fullmatch(r"[0-9a-f]{40}", header[2])
                or not re.fullmatch(r"[0-9a-f]{40}", header[3])):
            raise ValueError("C2_B_RAW_DIFF_INVALID")
        changes.append({
            "old_mode": header[0][1:], "new_mode": header[1],
            "old_blob": header[2], "new_blob": header[3],
            "status": header[4],
            "path": fields[index + 1].decode("utf-8", errors="strict")})
    return changes


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
    receipt = {
        "frozen_sha": C2_B_FROZEN_SHA,
        "frozen_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
        "historical_manifest_entries": checked,
        "historical_manifest_unchanged": True,
        "successor_commits": len(revisions),
        "current_tree": _git_text("rev-parse", "HEAD^{tree}"),
        "successors": [], "errors": [],
    }
    previous = C2_B_FROZEN_SHA
    for commit in revisions:
        parents = _git_text("show", "-s", "--format=%P", commit).split()
        record = {
            "sha": commit, "parents": parents,
            "tree": _git_text("rev-parse", commit + "^{tree}"),
            "changes": [],
        }
        receipt["successors"].append(record)
        if parents != [previous]:
            receipt["errors"].append({
                "code": "C2_B_NONLINEAR_SUCCESSOR", "sha": commit,
                "parents": parents})
        if len(parents) == 1:
            record["changes"] = _raw_changes(parents[0], commit)
            for change in record["changes"]:
                path = change["path"]
                visited.add(path)
                details = {"sha": commit, "parent": parents[0],
                           "tree": record["tree"], **change}
                if change["status"] != "M" or path not in SUCCESSOR_PATHS:
                    receipt["errors"].append({
                        "code": "C2_B_UNAUTHORIZED_SUCCESSOR_PATH", **details})
                if (change["old_mode"] != "100644"
                        or change["new_mode"] != "100644"):
                    receipt["errors"].append({
                        "code": "C2_B_SUCCESSOR_MODE_INVALID", **details})
        previous = commit
    changed_final = set(
        _git_text("diff", "--name-only", C2_B_FROZEN_SHA, head).splitlines())
    receipt["changed_paths"] = sorted(changed_final)
    receipt["all_visited_paths"] = sorted(visited)
    if not changed_final or changed_final != visited:
        receipt["errors"].append({"code": "C2_B_SUCCESSOR_DELTA_MISMATCH"})
    for path in changed_final:
        listing = _git_text("ls-tree", "HEAD", "--", path)
        if not listing.startswith("100644 blob "):
            receipt["errors"].append({
                "code": "C2_B_SUCCESSOR_MODE_INVALID", "sha": head, "path": path})
    if receipt["errors"]:
        raise HistoryVerificationError(receipt)
    return receipt


def observe_junit(path: Path, system: str) -> dict:
    """Require every mandatory test and only explicit opposite-OS skips."""
    observation = {"metrics": None, "executed_non_skipped": 0, "errors": []}
    errors = observation["errors"]
    allowed = LINUX_TESTS if system == "win32" else WINDOWS_TESTS
    if system not in ("win32", "linux"):
        errors.append("UNSUPPORTED_RUNNER_OS")
    try:
        root = ET.parse(path).getroot()
        suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        if not suites:
            raise ValueError("JUNIT_SUITE_MISSING")
        metrics = {
            key: sum(int(suite.get(key, "0")) for suite in suites)
            for key in ("tests", "errors", "failures", "skipped")}
        cases = [case for suite in suites for case in suite.findall("testcase")]
        if any(value < 0 for value in metrics.values()):
            raise ValueError("JUNIT_NEGATIVE_METRICS")
        observation["metrics"] = metrics
        names = [case.get("name", "") for case in cases]
        if len(names) != len(set(names)):
            errors.append("JUNIT_DUPLICATE_TEST_IDENTITY")
        if any(case.get("classname") != JUNIT_CLASS for case in cases):
            errors.append("JUNIT_UNEXPECTED_TEST_MODULE")
        missing = sorted(REQUIRED_TESTS - set(names))
        if missing:
            errors.append("JUNIT_REQUIRED_TESTS_MISSING")
            observation["missing_tests"] = missing
        skipped = []
        actual = {"tests": len(cases), "errors": 0, "failures": 0, "skipped": 0}
        for case in cases:
            name = case.get("name", "")
            actual["errors"] += len(case.findall("error"))
            actual["failures"] += len(case.findall("failure"))
            skips = case.findall("skipped")
            actual["skipped"] += len(skips)
            if skips:
                skipped.append(name)
                if (len(skips) != 1 or name not in allowed
                        or allowed[name] != skips[0].get("message", "")):
                    errors.append("JUNIT_UNAUTHORIZED_SKIP:" + name)
        if set(skipped) != set(allowed):
            errors.append("JUNIT_OS_SKIP_SET_MISMATCH")
        if actual != metrics:
            errors.append("JUNIT_METRICS_MISMATCH")
        executed = metrics["tests"] - metrics["skipped"]
        observation["executed_non_skipped"] = executed
        observation["skipped_tests"] = sorted(skipped)
        if executed < 15 or metrics["errors"] or metrics["failures"]:
            errors.append("JUNIT_FAILED_OR_INSUFFICIENT")
    except (OSError, ValueError, ET.ParseError):
        errors.append("JUNIT_MISSING_OR_INVALID")
    observation["gate"] = (
        "OBSERVED_PASS" if not errors else "OBSERVED_FAILED_OR_MISSING")
    return observation


def main() -> int:
    directory = Path(".test-output/atlas-parity04-f4-c2-os")
    directory.mkdir(parents=True, exist_ok=True)
    junit = observe_junit(directory / "junit.xml", sys.platform)
    expected = os.getenv("ATLAS_CHECKOUT_SHA")
    try:
        actual = _git_text("rev-parse", "HEAD")
    except (OSError, subprocess.SubprocessError, UnicodeError):
        actual = None
    sha_matches = bool(actual and expected and actual == expected)
    successor = None
    successor_error = None
    try:
        successor = verify_successor()
        historical_gate = "OBSERVED_PASS"
    except HistoryVerificationError as exc:
        successor = exc.receipt
        successor_error = str(exc)
        historical_gate = "BLOCKED"
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exc:
        successor_error = (str(exc) if isinstance(exc, ValueError)
                           else "C2_B_SUCCESSOR_VERIFICATION_FAILED")
        historical_gate = "BLOCKED"
    worker_optimize = os.getenv("ATLAS_WORKER_OPTIMIZE")
    execution_config_valid = (
        sys.flags.optimize == 0 and worker_optimize in ("0", "1"))
    native_observed = (junit["gate"] == "OBSERVED_PASS" and sha_matches
                       and execution_config_valid)
    passed = native_observed and historical_gate == "OBSERVED_PASS"
    report = {
        "mission": "AP04-F4-C2-B-OS-SANDBOX-CHAT-01",
        "commit_sha": actual, "expected_checkout_sha": expected,
        "trigger_sha": os.getenv("GITHUB_SHA"),
        "checkout_sha_verified": sha_matches,
        "pytest_gate": junit["gate"], "junit": junit["metrics"],
        "junit_observation": junit,
        "executed_non_skipped": junit["executed_non_skipped"],
        "historical_gate": historical_gate,
        "historical_successor": successor,
        "historical_successor_error": successor_error,
        "worker_optimize": worker_optimize,
        "execution_config_valid": execution_config_valid,
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "runner_os": os.getenv("RUNNER_OS", platform.system()),
        "python": sys.version.split()[0], "optimize": sys.flags.optimize,
        "test_gate": "OBSERVED_PASS" if passed else "OBSERVED_FAILED_OR_MISSING",
        "native_fixture_scope": (
            "NATIVE_FIXTURE_TESTS_OBSERVED" if native_observed
            else "NATIVE_FIXTURE_TESTS_NOT_OBSERVED"),
        "production_acquisition": "PRODUCTION_ACQUISITION_BLOCKED",
        "host_qualification": "HOST_UNVERIFIED",
        "approval": "C2_B_OS_BLOCKED_EXACT",
        "independent_review": "NOT_EVALUATED_BY_THIS_CHECKER",
        "fixtures": "INVENTED_ONLY",
    }
    (directory / "observed-ci.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        key: report[key] for key in (
            "commit_sha", "checkout_sha_verified", "pytest_gate", "junit",
            "historical_gate", "historical_successor_error",
            "test_gate", "approval")}, sort_keys=True))
    if successor:
        print(json.dumps({"historical_errors": successor.get("errors", [])},
                         sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
