"""Native OS counterproofs: every launched worker consumes internally invented bytes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest
from tools.atlas_legacy_presentation import os_supervisor as sandbox


@pytest.fixture
def synthetic(tmp_path: Path):
    """Only preflight/injected-assignment tests receive external invented paths."""
    parent = tmp_path / "atlas-c2b-fixture"
    parent.mkdir()
    root = parent / "os-invented"
    root.mkdir()
    inputs = root / "input"
    inputs.mkdir()
    scratch = root / "scratch"
    if os.name == "nt":
        from tools.atlas_legacy_presentation.os_windows_acl import (
            create_private_scratch)
        create_private_scratch(scratch)
    else:
        scratch.mkdir(mode=0o700)
        scratch.chmod(0o700)
    source = inputs / "os-allowlisted.json"
    outside = inputs / "os-outside.json"
    source.write_bytes(b'{"synthetic":true,"payload":"invented"}')
    outside.write_bytes(b'{"synthetic":true,"outside":"invented"}')
    return source, outside, scratch


def test_production_denied_even_with_synthetic_override():
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="PRODUCTION_ACQUISITION_BLOCKED"):
        sandbox.require_production_acquisition(
            synthetic_fixture=True, source="private")


def test_memory_and_wall_budgets_fixed():
    assert sandbox.MAX_MEMORY_BYTES == 268435456
    assert sandbox.MAX_WALL_SECONDS == 30


def test_external_paths_cannot_be_passed_to_public_probe(synthetic):
    source, outside, scratch = synthetic
    with pytest.raises(TypeError):
        sandbox.run_synthetic_probe(source, outside, scratch, "success")


def test_preflight_rejects_symlink(synthetic):
    source, outside, scratch = synthetic
    link = source.parent / "os-allowlisted-link"
    try:
        link.symlink_to(source)
    except (OSError, NotImplementedError) as exc:
        pytest.fail(f"OS_SYMLINK_FIXTURE_UNAVAILABLE: {type(exc).__name__}")
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="UNSAFE_REPARSE_OR_SYMLINK"):
        sandbox._preflight(link, outside, scratch)


def test_preflight_rejects_symlinked_ancestor(synthetic):
    source, outside, scratch = synthetic
    redirect = scratch.parent.parent / "aliased-fixtures"
    try:
        redirect.symlink_to(source.parent.parent, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.fail(f"OS_ANCESTOR_SYMLINK_UNAVAILABLE: {type(exc).__name__}")
    aliased = redirect / "input" / source.name
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="UNSAFE_REPARSE_OR_SYMLINK"):
        sandbox._preflight(aliased, outside, scratch)


def test_windows_junction_rejected(synthetic):
    if sys.platform != "win32":
        pytest.skip("Windows junction/reparse-point syscall only")
    source, outside, scratch = synthetic
    junction = scratch.parent.parent / "junction"
    created = subprocess.run(
        ["cmd", "/d", "/s", "/c", "mklink", "/J",
         str(junction), str(source.parent.parent)],
        capture_output=True, text=True)
    if created.returncode:
        pytest.fail("JUNCTION_FIXTURE_UNAVAILABLE")
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="UNSAFE_REPARSE_OR_SYMLINK"):
        sandbox._preflight(junction / "input" / source.name,
                           outside, scratch)


def test_native_memory_challenge(record_property):
    result = sandbox.run_synthetic_probe("memory")
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["timed_out"] is False
    assert result["descriptor_absent"] is True
    assert result["descriptor_published"] is False
    assert result["synthetic_source_unchanged"] is True
    assert result["probe"] is not None, result
    assert result["probe"]["memory_probe"] == "MEMORY_ERROR_OS_LIMIT", result
    assert result["probe"]["worker_optimize"] == int(
        os.getenv("ATLAS_WORKER_OPTIMIZE", "0"))
    if sys.platform == "win32":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
        assert result["memory_metric"] == "JobMemoryLimit_committed_bytes_job_total"
        assert result["job_memory_limit_bytes"] == 268435456
        assert result["kill_on_job_close"] is True
        assert result["breakaway_permitted"] is False
        assert result["windows_scratch_acl_checked"] is True
    else:
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER"
        assert result["probe"]["memory_metric"] == "RLIMIT_AS_virtual_address_space"


def test_linux_os_denials_or_windows_explicit_block(record_property):
    result = sandbox.run_synthetic_probe("denials")
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["descriptor_absent"] is True
    assert result["synthetic_source_unchanged"] is True
    if sys.platform == "win32":
        assert result["qualification"] == (
            "OS_CONTROL_TESTED_IN_RUNNER_APPCONTAINER")
        assert result["probe"]["isolation"] == (
            "APPCONTAINER_NO_NETWORK_CAPABILITIES")
        assert result["appcontainer_token_verified"] is True
        assert result["appcontainer_loopback_exception_absent"] is True
        assert result["loopback_control_passed"] is True
        assert result["loopback_worker_accepted"] is False
        assert result["filesystem_network_confined"] is True
        return
    assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER", result
    checks = result["probe"]["checks"]
    assert {k for k in checks if k != "scratch_write"} == {
        "outside_read", "source_read", "source_write", "loopback_socket",
        "external_socket", "descendant_fork"}
    assert all(v == "DENIED_BY_OS" for k, v in checks.items()
               if k != "scratch_write")
    assert checks["scratch_write"] == "ALLOWED"


def test_monotonic_wall_clock_30s_kills_blocked_worker(record_property):
    result = sandbox.run_synthetic_probe("sleep", wall_seconds=30)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["timed_out"] is True, result
    assert result["status"] == "OS_WALL_TIMEOUT_TERMINATED"
    assert result["elapsed_seconds"] >= 29
    assert result["elapsed_seconds"] < 35
    assert result["descriptor_absent"] is True
    assert result["descriptor_published"] is False


def test_invalid_modes_and_time_budgets_denied():
    for mode, budget in (("arbitrary", 1), ("memory", 31), ("memory", 0)):
        with pytest.raises(sandbox.OSProfileNotEnforced, match="INVALID_PROBE"):
            sandbox.run_synthetic_probe(mode, wall_seconds=budget)


def test_windows_child_inherits_private_scratch_acl(synthetic):
    if sys.platform != "win32":
        pytest.skip("Only Windows can verify child NTFS DACL inheritance")
    _, _, scratch = synthetic
    from tools.atlas_legacy_presentation.os_windows_acl import (
        WindowsScratchUnverified, verify_private_child,
    )
    child = scratch / "invented-child.txt"
    child.write_text("synthetic", encoding="utf-8")
    verify_private_child(scratch, child)
    # Child outside the trusted parent must never pass as a private child.
    with pytest.raises(WindowsScratchUnverified,
                       match="SCRATCH_CHILD_PATH_UNVERIFIED"):
        verify_private_child(scratch, scratch.parent / "input" / "os-allowlisted.json")


def test_report_no_clobber(synthetic):
    _, _, scratch = synthetic
    from tools.atlas_legacy_presentation.os_worker import _report
    _report(scratch, {"fixture": "original"})
    with pytest.raises(FileExistsError):
        _report(scratch, {"fixture": "attacker"})
    assert json.loads((scratch / "os-probe-report.json").read_text(
        encoding="utf-8"))["fixture"] == "original"


def test_synthetic_source_validated_without_worker_read():
    result = sandbox.run_synthetic_probe("success")
    assert result["descriptor_absent"] is True
    assert result["synthetic_source_unchanged"] is True
    assert result["probe"] is not None, result
    if sys.platform == "linux":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER", result
        assert result["probe"]["source_bytes_read_by_worker"] == 0
        assert result["probe"]["source_opened_by_worker"] is False
        assert result["probe"]["landlock_abi"] >= 3
        assert result["probe"]["scratch_only_landlock_abi"] >= 3
        assert result["scratch_report_mode"] == 0o600
    else:
        assert result["qualification"] == (
            "OS_CONTROL_TESTED_IN_RUNNER_APPCONTAINER_SOURCE_ONLY")
        assert result["probe"]["source_length_sample"] == len(
            sandbox._INVENTED_SOURCE)
        assert result["appcontainer_token_verified"] is True
        assert result["windows_scratch_acl_checked"] is True


def test_seccomp_foreign_arch_is_kill_bpf():
    if sys.platform != "linux":
        pytest.skip("Seccomp BPF code structure applicable to Linux only")
    import ctypes
    from tools.atlas_legacy_presentation import os_linux_isolation as linux
    class FakeLibc:
        def prctl(self, option, mode, program, arg4, arg5):
            p = ctypes.cast(program, ctypes.POINTER(linux._Program)).contents
            assert p.length > 4
            assert p.filters[1].code == 0x15
            assert p.filters[2].code == 0x06  # BPF_RET
            assert p.filters[2].k == 0x80000000  # SECCOMP_RET_KILL_PROCESS
            return 0
    linux._seccomp(FakeLibc())


def test_windows_breakaway_denied(record_property):
    if sys.platform != "win32":
        pytest.skip("Linux denies fork/clone via seccomp")
    result = sandbox.run_synthetic_probe("breakaway")
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
    assert result["probe"]["breakaway"] == (
        "BREAKAWAY_DENIED_BY_JOB_WITH_POSITIVE_CONTROL")
    assert result["probe"]["positive_control_exit_code"] == 0
    assert result["probe"]["process_in_job"] is True
    assert result["probe"]["breakaway_winerror"] == 5


def test_windows_descendants_killed_in_job(record_property):
    if sys.platform != "win32":
        pytest.skip("Linux denies fork via seccomp")
    result = sandbox.run_synthetic_probe("descendant", wall_seconds=2)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["timed_out"] is True
    assert result["active_processes_after_timeout"] == 0
    assert result["descriptor_absent"] is True


def test_windows_association_error_terminates_suspended_worker(synthetic):
    if sys.platform != "win32":
        pytest.skip("Windows Job only")
    source, outside, scratch = synthetic
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    argv = [sys.executable, "-I", "-S", str(worker),
            "--source", str(source), "--outside", str(outside),
            "--scratch", str(scratch), "--mode", "success",
            "--supervisor-pid", str(os.getpid())]
    with pytest.raises(NativeJobUnavailable, match="JOB_ASSIGN_FAILED_INJECTED"):
        run_synthetic_job(argv, inject_assign_failure=True)
    assert not (scratch / "os-probe-report.json").exists()


def test_unrecognized_synthetic_fixture_layout_rejected(synthetic):
    source, outside, scratch = synthetic
    bogus = source.parent / "non-synthetic.json"
    bogus.write_text('{"invented":true}', encoding="utf-8")
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="SYNTHETIC_FIXTURE_REQUIRED"):
        sandbox._preflight(bogus, outside, scratch)


def test_windows_job_refuses_arbitrary_entrypoint():
    if sys.platform != "win32":
        pytest.skip("Windows Job-specific negative contract")
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    with pytest.raises(NativeJobUnavailable,
                       match="UNTRUSTED_WORKER_REJECTED"):
        run_synthetic_job([sys.executable, "-I", "-S", "untrusted.py"])


def test_evidence_all_skipped_must_fail(tmp_path, monkeypatch):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / ".test-output/atlas-parity04-f4-c2-os"
    directory.mkdir(parents=True)
    (directory / "junit.xml").write_text(
        '<testsuite tests="2" skipped="2" failures="0" errors="0"/>',
        encoding="utf-8")
    assert evidence.main() == 2
    receipt = json.loads((directory / "observed-ci.json").read_text())
    assert receipt["test_gate"] != "OBSERVED_PASS"


def test_evidence_failures_must_exit_nonzero(tmp_path, monkeypatch):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / ".test-output/atlas-parity04-f4-c2-os"
    directory.mkdir(parents=True)
    (directory / "junit.xml").write_text(
        '<testsuite tests="2" skipped="0" failures="1" errors="0"/>',
        encoding="utf-8")
    assert evidence.main() == 2


def test_evidence_checkout_sha_mismatch_must_fail(tmp_path, monkeypatch):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ATLAS_CHECKOUT_SHA", "0" * 40)
    directory = tmp_path / ".test-output/atlas-parity04-f4-c2-os"
    directory.mkdir(parents=True)
    (directory / "junit.xml").write_text(
        '<testsuite tests="1" skipped="0" failures="0" errors="0"/>',
        encoding="utf-8")
    assert evidence.main() == 2



def test_direct_worker_refuses_untrusted_paths(tmp_path):
    """No data from caller-selected paths may be parsed by the worker CLI."""
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    fake = tmp_path / "untrusted.json"
    fake.write_text('{"invented":true}', encoding="utf-8")
    out = tmp_path / "untrusted-report"
    out.mkdir()
    cmd = [sys.executable, "-I", "-S", str(worker),
           "--source", str(fake), "--outside", str(fake),
           "--scratch", str(out), "--mode", "success",
           "--supervisor-pid", str(os.getpid())]
    result = subprocess.run(cmd, capture_output=True, timeout=8)
    assert result.returncode == 78
    assert fake.read_text(encoding="utf-8") == '{"invented":true}'
    assert list(out.iterdir()) == []


def test_windows_job_rejects_tampered_argument_vector(synthetic):
    if sys.platform != "win32":
        pytest.skip("Windows native job API only")
    source, outside, scratch = synthetic
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    valid = [sys.executable, "-I", "-S", str(worker),
             "--source", str(source), "--outside", str(outside),
             "--scratch", str(scratch), "--mode", "success",
             "--supervisor-pid", str(os.getpid())]
    tampered = [
        valid[:-1] + ["0"],
        valid[:5] + ["--other-flag"] + valid[6:],
        valid + ["--unexpected", "value"],
    ]
    for args in tampered:
        with pytest.raises(NativeJobUnavailable,
                           match="WORKER_ARGUMENTS_UNTRUSTED"):
            run_synthetic_job(args)



def test_aarch64_socketpair_is_in_native_seccomp_denyset(monkeypatch):
    """AArch64 is not the hosted Ubuntu arch; validate its BPF branch structurally."""
    if sys.platform != "linux":
        pytest.skip("Linux seccomp structural test")
    import ctypes
    from tools.atlas_legacy_presentation import os_linux_isolation as linux
    monkeypatch.setattr(linux.platform, "machine", lambda: "aarch64")

    class FakeLibc:
        def prctl(self, option, mode, program, arg4, arg5):
            p = ctypes.cast(program, ctypes.POINTER(linux._Program)).contents
            checks = [
                (p.filters[i].code, p.filters[i].k,
                 p.filters[i + 1].code, p.filters[i + 1].k)
                for i in range(p.length - 1)
            ]
            assert (0x15, 199, 0x06, 0x00050001) in checks
            assert p.filters[2].code == 0x06
            assert p.filters[2].k == 0x80000000
            return 0

    linux._seccomp(FakeLibc())



def test_windows_appcontainer_broker_never_degrades_to_unconfined(synthetic, record_property):
    """Native process-token challenge, no mock, with exact inherited handles.

    A missing profile/runtime is a blocked result, never evidence of a pass.
    The legacy Job-only tests remain separate and unchanged.
    """
    if sys.platform != "win32":
        pytest.skip("AppContainer requires Windows native kernel")
    source, outside, scratch = synthetic
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    argv = [sys.executable, "-I"]
    if os.environ.get("ATLAS_WORKER_OPTIMIZE") == "1":
        argv.append("-O")
    argv += ["-S", str(worker),
             "--source", str(source), "--outside", str(outside),
             "--scratch", str(scratch), "--mode", "denials",
             "--supervisor-pid", str(os.getpid())]
    try:
        result = run_synthetic_job(argv, wall_seconds=8, appcontainer=True)
    except NativeJobUnavailable as exc:
        pytest.fail("APPCONTAINER_OS_ENFORCEMENT_MISSING:" + str(exc))
    else:
        record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["appcontainer_token_verified"] is True
        assert result["filesystem_network_confined"] is False
        report_path = scratch / "os-probe-report.json"
        detail = (json.loads(report_path.read_text())
                  if report_path.is_file() and report_path.stat().st_size < 4096
                  else None)
        assert result["exit_code"] == 0, (
            "APPCONTAINER_NEGATIVE_PROBE_FAILED:" +
            repr({"outcome": result, "synthetic_checks": detail}))
        record_property("native_probe", json.dumps(detail, sort_keys=True))
        assert detail is not None
        assert detail["appcontainer_token_verified"] is True
        assert detail["report_read_denied_os"] is True
        assert detail["report_read_winerror"] == 5
        assert detail["source_bytes_read_by_worker"] == 0
        assert detail["isolation"] == "APPCONTAINER_NO_NETWORK_CAPABILITIES"
        assert set(detail["checks"]) == {
            "outside_read", "source_read", "source_write",
            "scratch_path_write",
            "loopback_connect"}
        assert all(v == "DENIED_BY_OS"
                   for k, v in detail["checks"].items()
                   if k != "loopback_connect")
        assert result["appcontainer_loopback_exception_absent"] is True
        assert result["loopback_control_passed"] is True
        assert result["loopback_worker_accepted"] is False
        assert detail["checks"]["loopback_connect"] in (
            "DENIED_BY_OS", "NO_CONNECTION_TIMEOUT")
        assert detail["loopback_connect_os_error"] in (13, 10013, 10035, 10060)
        assert detail["worker_optimize"] == int(os.environ.get(
            "ATLAS_WORKER_OPTIMIZE", "0"))


def test_windows_broker_flags_cannot_authenticate_direct_worker(synthetic):
    if sys.platform != "win32":
        pytest.skip("AppContainer process-token test only")
    source, outside, scratch = synthetic
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    command = [sys.executable, "-I", "-S", str(worker),
               "--source", str(source), "--outside", str(outside),
               "--scratch", str(scratch), "--mode", "success",
               "--supervisor-pid", str(os.getpid()),
               "--broker-report-handle", "123457",
               "--broker-source-length", str(len(sandbox._INVENTED_SOURCE)),
               "--broker-loopback-port", "12345"]
    checked = subprocess.run(command, capture_output=True, timeout=8)
    assert checked.returncode == 78
    assert not (scratch / "os-probe-report.json").exists()



def _appcontainer_argv(synthetic, mode: str) -> list[str]:
    source, outside, scratch = synthetic
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    argv = [sys.executable, "-I"]
    if os.environ.get("ATLAS_WORKER_OPTIMIZE") == "1":
        argv += ["-O"]
    return argv + ["-S", str(worker),
                   "--source", str(source), "--outside", str(outside),
                   "--scratch", str(scratch), "--mode", mode,
                   "--supervisor-pid", str(os.getpid())]


def test_windows_appcontainer_memory_native_limit(synthetic, record_property):
    if sys.platform != "win32":
        pytest.skip("Native AppContainer limit challenge is Windows-only")
    from tools.atlas_legacy_presentation.os_windows_job import run_synthetic_job
    result = run_synthetic_job(
        _appcontainer_argv(synthetic, "memory"),
        wall_seconds=10, appcontainer=True)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["appcontainer_token_verified"] is True
    assert result["job_memory_limit_bytes"] == 268435456
    assert result["timed_out"] is False
    assert result["exit_code"] == 0, result
    report = json.loads((synthetic[2] / "os-probe-report.json").read_text())
    assert report["memory_probe"] == "MEMORY_ERROR_OS_LIMIT"
    assert report["source_bytes_read_by_worker"] == 0


def test_windows_appcontainer_descendants_killed_at_native_deadline(synthetic, record_property):
    if sys.platform != "win32":
        pytest.skip("Native AppContainer descendants Windows-only")
    from tools.atlas_legacy_presentation.os_windows_job import run_synthetic_job
    result = run_synthetic_job(
        _appcontainer_argv(synthetic, "descendant"),
        wall_seconds=3, appcontainer=True)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["appcontainer_token_verified"] is True
    report_path = synthetic[2] / "os-probe-report.json"
    assert report_path.exists(), result
    detail = json.loads(report_path.read_text())
    record_property("native_probe", json.dumps(detail, sort_keys=True))
    if result["timed_out"]:
        assert result["status"] == "OS_WALL_TIMEOUT_TERMINATED"
        assert result["active_processes_after_timeout"] == 0
        assert detail["descendant_started"] > 0
    else:
        assert result["exit_code"] == 0, {
            "outcome": result, "synthetic_probe": detail}
        assert detail["child_spawn"] == "DENIED_BY_OS", detail
        assert detail["child_os_errno"] == 13
        assert detail["child_os_winerror"] == 5
        assert detail["job_specific_denial_proven"] is False
    assert detail["creation_api"] == "CreateProcessW"
    assert detail["creation_phase"] == "PROCESS_CREATE"
    assert not any(synthetic[2].glob("atlas-c2-*.json"))


def test_windows_appcontainer_child_escape_has_native_causal_attribution(synthetic, record_property):
    if sys.platform != "win32":
        pytest.skip("Native AppContainer child escape Windows-only")
    from tools.atlas_legacy_presentation.os_windows_job import run_synthetic_job
    result = run_synthetic_job(
        _appcontainer_argv(synthetic, "breakaway"),
        wall_seconds=10, appcontainer=True)
    report_path = synthetic[2] / "os-probe-report.json"
    report = (json.loads(report_path.read_text()) if report_path.exists() else None)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["exit_code"] == 0, {"native_job": result, "native_probe": report}
    record_property("native_probe", json.dumps(report, sort_keys=True))
    assert report["creation_api"] == "CreateProcessW"
    assert report["creation_phase"] == "PROCESS_CREATE"
    assert report["process_in_job"] is True
    assert report["breakaway_winerror"] == 5
    if report["breakaway"] == "BREAKAWAY_DENIED_BY_JOB_WITH_POSITIVE_CONTROL":
        # Only a successful ordinary child control permits Job attribution.
        assert report["positive_control_exit_code"] == 0
    else:
        # Both process attempts denied by the OS. Do NOT call this
        # JOB_DENIED: the separate Job-only positive-control test proves
        # the Job breakaway restriction in a launch-capable token.
        assert report["breakaway"] == (
            "CHILD_AND_BREAKAWAY_CREATION_DENIED_BY_OS_NOT_JOB_PROOF")
        assert report["normal_child_winerror"] == 5
        assert report["job_specific_denial_proven"] is False


def test_windows_appcontainer_source_rename_denied_after_handle_pin(synthetic, record_property):
    if sys.platform != "win32":
        pytest.skip("Native Windows handle-sharing rule only")
    from tools.atlas_legacy_presentation.os_windows_job import run_synthetic_job
    result = run_synthetic_job(
        _appcontainer_argv(synthetic, "success"),
        wall_seconds=10, appcontainer=True, inject_source_swap=True)
    record_property("native_job_result", json.dumps(result, sort_keys=True))
    assert result["source_swap_denied_os"] is True
    assert result["exit_code"] == 0, result
    assert synthetic[0].is_file()
    assert not (synthetic[0].parent / "os-swap-attempt.json").exists()


def test_windows_appcontainer_rejects_mutated_source_before_worker(synthetic):
    if sys.platform != "win32":
        pytest.skip("Native Windows source broker only")
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    source, _, scratch = synthetic
    source.write_bytes(b'{"synthetic":true,"payload":"tampered"}')
    with pytest.raises(NativeJobUnavailable, match="BROKER_SOURCE_NOT_INVENTED"):
        run_synthetic_job(
            _appcontainer_argv(synthetic, "success"),
            wall_seconds=10, appcontainer=True)
    assert not any(scratch.glob("atlas-c2-*.json"))
    report = scratch / "os-probe-report.json"
    assert not report.exists() or report.stat().st_size == 0


def test_windows_appcontainer_assignment_failure_never_resumes_worker(synthetic):
    if sys.platform != "win32":
        pytest.skip("Native Windows fault injection only")
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    with pytest.raises(NativeJobUnavailable, match="JOB_ASSIGN_FAILED_INJECTED"):
        run_synthetic_job(
            _appcontainer_argv(synthetic, "success"),
            wall_seconds=10, appcontainer=True, inject_assign_failure=True)
    assert not any(synthetic[2].glob("atlas-c2-*.json"))
    report = synthetic[2] / "os-probe-report.json"
    assert not report.exists() or report.stat().st_size == 0



def test_windows_broker_has_no_source_read_api_or_handle_transit():
    """Reviewable structural contract plus the native child handle check."""
    from tools.atlas_legacy_presentation import os_worker, os_windows_job
    import inspect
    worker = inspect.getsource(os_worker._windows_broker_worker)
    native = inspect.getsource(os_windows_job._AppContainerLaunch.prepare)
    assert "args.broker_source_handle" not in worker
    assert "args.broker_source_length" in worker
    assert "source_sample = src.read" not in worker
    assert "(wintypes.HANDLE * 1)(out)" in native
    assert "src_attrs" in native



def test_native_handle_integer_conversion_rejects_forged_or_invalid():
    """ctypes ABI converter: verifies both native restype and wrapped HANDLE."""
    import ctypes
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, _numeric_handle)
    assert _numeric_handle(42) == "42"
    assert _numeric_handle(ctypes.c_void_p(42)) == "42"
    for invalid in (None, 0, ctypes.c_void_p(), -1, ctypes.c_void_p(-1)):
        with pytest.raises(NativeJobUnavailable, match="BROKER_HANDLE_INVALID"):
            _numeric_handle(invalid)



def test_job_breakaway_classifier_refuses_unrelated_launch_errors():
    """Unit-level negative control, separate from OS-native Job counterproof."""
    from tools.atlas_legacy_presentation.os_worker import (
        _is_job_breakaway_denial)
    assert not _is_job_breakaway_denial(FileNotFoundError(2, "missing"))
    assert not _is_job_breakaway_denial(PermissionError(13, "without winerror"))
    class SimulatedNativeDenial(PermissionError):
        winerror = 5
    assert not _is_job_breakaway_denial(SimulatedNativeDenial(13, "setup"))
    native = SimulatedNativeDenial(13, "native call")
    native._atlas_createprocess_call = True
    assert _is_job_breakaway_denial(native)


def test_forged_synthetic_path_direct_cli_never_opens_source(synthetic):
    """A spoofed parent PID and correct fixture names never authorize data."""
    source, outside, scratch = synthetic
    secret = b"PRIVATE_BYTES_NOT_AUTHORIZED_FOR_TEST_WORKER"
    source.write_bytes(secret)
    worker = Path(sandbox.__file__).with_name("os_worker.py")
    command = [sys.executable, "-I", "-S", str(worker),
               "--source", str(source), "--outside", str(outside),
               "--scratch", str(scratch), "--mode", "success",
               "--supervisor-pid", str(os.getpid())]
    response = subprocess.run(command, capture_output=True, timeout=8)
    assert response.returncode == 78, response
    assert secret not in response.stdout + response.stderr
    report = scratch / "os-probe-report.json"
    if report.exists():
        assert secret not in report.read_bytes()
        assert json.loads(report.read_text())["isolation"] == (
            "OS_ISOLATION_UNVERIFIED")
    assert source.read_bytes() == secret


def test_windows_native_child_never_opens_nul_or_uses_popen(monkeypatch):
    if sys.platform != "win32":
        pytest.skip("Windows native process creation only")
    from tools.atlas_legacy_presentation.os_worker import _NativeChild
    def forbidden(*args, **kwargs):
        raise PermissionError(13, "simulated NUL setup denial")
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    child = _NativeChild()
    try:
        assert child.wait(timeout=4) == 0
    finally:
        if child.handle is not None:
            child.kill()
            child.wait(timeout=4)


def test_windows_native_child_classifies_only_createprocess_errors(monkeypatch):
    if sys.platform != "win32":
        pytest.skip("Windows native process creation only")
    import _winapi
    from tools.atlas_legacy_presentation.os_worker import (
        _NativeChild, _is_job_breakaway_denial)
    class NativeDenied(PermissionError):
        winerror = 5
    def setup_error():
        raise NativeDenied(13, "setup")
    with monkeypatch.context() as m:
        m.setattr(subprocess, "STARTUPINFO", setup_error)
        with pytest.raises(NativeDenied) as caught:
            _NativeChild()
        assert not _is_job_breakaway_denial(caught.value)
    for error, expected in (
            (FileNotFoundError(2, "missing interpreter"), False),
            (PermissionError(13, "no native code"), False),
            (NativeDenied(13, "native denial"), True)):
        def failed(*args, **kwargs):
            assert args[4] is False  # No inherited source/report/std handles.
            assert args[8].dwFlags == 0  # No STARTF_USESTDHANDLES.
            raise error
        with monkeypatch.context() as m:
            m.setattr(_winapi, "CreateProcess", failed)
            with pytest.raises(OSError) as caught:
                _NativeChild()
            assert _is_job_breakaway_denial(caught.value) is expected


def test_windows_supervisor_crash_kills_worker_and_descendant(synthetic, record_property):
    """Hold native process handles across parent death; PID reuse cannot pass."""
    if sys.platform != "win32":
        pytest.skip("Windows Job kill-on-close native counterproof only")
    import _winapi
    import time
    source, outside, scratch = synthetic
    script = (
        "import os,sys; "
        "from tools.atlas_legacy_presentation.os_windows_job import run_synthetic_job; "
        "worker=" + repr(str(Path(sandbox.__file__).with_name("os_worker.py"))) + "; "
        "args=[sys.executable,'-I']+(['-O'] if os.environ.get("
        "'ATLAS_WORKER_OPTIMIZE')=='1' else [])+['-S',worker,"
        "'--source'," + repr(str(source)) + ",'--outside'," +
        repr(str(outside)) + ",'--scratch'," + repr(str(scratch)) +
        ",'--mode','descendant','--supervisor-pid',str(os.getpid())]; "
        "run_synthetic_job(args,wall_seconds=30)"
    )
    supervisor = subprocess.Popen(
        [sys.executable, "-c", script], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, close_fds=True)
    held = []
    report = scratch / "os-probe-report.json"
    try:
        detail = None
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if report.exists():
                try:
                    detail = json.loads(report.read_text())
                except (OSError, ValueError):
                    pass
                if detail and detail.get("descendant_started"):
                    break
            if supervisor.poll() is not None:
                pytest.fail("SUPERVISOR_EXITED_BEFORE_CRASH_CHALLENGE:" +
                            repr(supervisor.communicate(timeout=2)))
            time.sleep(0.02)
        assert detail and detail.get("descendant_started"), detail
        for pid in (detail["worker_pid"], detail["descendant_started"]):
            handle = _winapi.OpenProcess(0x00100001, False, pid)
            held.append(handle)
            assert _winapi.WaitForSingleObject(handle, 0) == 258
        supervisor.kill()  # Abrupt death: no Python finally executes.
        supervisor.wait(timeout=4)
        for handle in held:
            assert _winapi.WaitForSingleObject(handle, 4000) == 0
        record_property("native_crash_proof", json.dumps({
            "worker_pid": detail["worker_pid"],
            "descendant_pid": detail["descendant_started"],
            "both_alive_before_crash": True,
            "both_signaled_after_crash": True,
            "worker_optimize": detail["worker_optimize"]}, sort_keys=True))
        assert not any(scratch.glob("atlas-c2-*.json"))
        assert source.read_bytes() == sandbox._INVENTED_SOURCE
    finally:
        if supervisor.poll() is None:
            supervisor.kill()
            supervisor.wait(timeout=4)
        for handle in held:
            if _winapi.WaitForSingleObject(handle, 0) != 0:
                _winapi.TerminateProcess(handle, 79)
                _winapi.WaitForSingleObject(handle, 4000)
            _winapi.CloseHandle(handle)
        supervisor.communicate(timeout=4)


def _positive_evidence_junit(path: Path, system: str):
    """Parser fixture, never counted as a native sandbox observation."""
    import xml.etree.ElementTree as ET
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    skips = evidence.LINUX_TESTS if system == "win32" else evidence.WINDOWS_TESTS
    suite = ET.Element("testsuite", tests=str(len(evidence.REQUIRED_TESTS)),
                       errors="0", failures="0", skipped=str(len(skips)))
    for name in sorted(evidence.REQUIRED_TESTS):
        case = ET.SubElement(suite, "testcase", name=name,
                             classname=evidence.JUNIT_CLASS)
        if name in skips:
            ET.SubElement(case, "skipped", message=skips[name])
    ET.ElementTree(suite).write(path, encoding="utf-8")
    return suite


def test_evidence_only_opposite_os_skips_are_permitted(tmp_path):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    path = tmp_path / "junit.xml"
    for system in ("win32", "linux"):
        _positive_evidence_junit(path, system)
        observed = evidence.observe_junit(path, system)
        assert observed["gate"] == "OBSERVED_PASS", observed


def test_evidence_mandatory_native_skip_fails_with_many_passes(tmp_path):
    import xml.etree.ElementTree as ET
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    path = tmp_path / "junit.xml"
    suite = _positive_evidence_junit(path, "win32")
    name = "test_windows_appcontainer_broker_never_degrades_to_unconfined"
    case = next(c for c in suite.findall("testcase") if c.get("name") == name)
    ET.SubElement(case, "skipped", message="unsupported native setup")
    suite.set("skipped", str(int(suite.get("skipped")) + 1))
    ET.ElementTree(suite).write(path, encoding="utf-8")
    observed = evidence.observe_junit(path, "win32")
    assert observed["executed_non_skipped"] >= 15
    assert "JUNIT_UNAUTHORIZED_SKIP:" + name in observed["errors"]
    assert observed["gate"] == "OBSERVED_FAILED_OR_MISSING"


def test_evidence_reverted_history_violation_is_not_silenced():
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    with pytest.raises(evidence.HistoryVerificationError) as caught:
        evidence.verify_successor()
    receipt = caught.value.receipt
    assert receipt["historical_manifest_unchanged"] is True
    assert receipt["historical_manifest_entries"] == 15
    forbidden = [error for error in receipt["errors"]
                 if error["code"] == "C2_B_UNAUTHORIZED_SUCCESSOR_PATH"]
    assert {error["sha"] for error in forbidden} == {
        "226afaaf7771c84f269335c6a40976758b9efbc0",
        "aa2aa933625c88e75043b264d7090d1ddfaa293e"}
    assert all(error["path"].endswith("/THREAT-MODEL.md")
               for error in forbidden)
    assert forbidden[0]["old_blob"] == forbidden[1]["new_blob"]
    assert receipt["successors"][-1]["sha"] == evidence._git_text(
        "rev-parse", "HEAD")


def test_evidence_pytest_pass_cannot_override_history_failure(tmp_path, monkeypatch):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / ".test-output/atlas-parity04-f4-c2-os"
    directory.mkdir(parents=True)
    _positive_evidence_junit(directory / "junit.xml", sys.platform)
    head = "a" * 40
    monkeypatch.setenv("ATLAS_CHECKOUT_SHA", head)
    monkeypatch.setenv("ATLAS_WORKER_OPTIMIZE", "0")
    monkeypatch.setattr(evidence, "_git_text", lambda *args: head)
    def invalid_history():
        raise evidence.HistoryVerificationError({
            "errors": [{"code": "C2_B_UNAUTHORIZED_SUCCESSOR_PATH",
                        "sha": "b" * 40, "path": "historical-document"}]})
    monkeypatch.setattr(evidence, "verify_successor", invalid_history)
    assert evidence.main() == 2
    receipt = json.loads((directory / "observed-ci.json").read_text())
    assert receipt["pytest_gate"] == "OBSERVED_PASS"
    assert receipt["checkout_sha_verified"] is True
    assert receipt["historical_gate"] == "BLOCKED"
    assert receipt["test_gate"] == "OBSERVED_FAILED_OR_MISSING"


def test_evidence_frozen_manifest_mutation_rejected(monkeypatch):
    from scripts.qa import atlas_parity04_f4_c2_os_evidence as evidence
    original = evidence._git_bytes
    def mutated(*args):
        if args == ("show", "HEAD:" + evidence.C2_B_MANIFEST_PATH):
            return b"mutated"
        return original(*args)
    monkeypatch.setattr(evidence, "_git_bytes", mutated)
    with pytest.raises(ValueError, match="C2_B_HISTORICAL_MANIFEST_CHANGED"):
        evidence.verify_successor()
