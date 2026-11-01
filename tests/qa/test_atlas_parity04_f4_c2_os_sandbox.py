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


def test_native_memory_challenge():
    result = sandbox.run_synthetic_probe("memory")
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


def test_linux_os_denials_or_windows_explicit_block():
    result = sandbox.run_synthetic_probe("denials")
    assert result["descriptor_absent"] is True
    assert result["synthetic_source_unchanged"] is True
    if sys.platform == "win32":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
        assert result["probe"]["isolation"] == "OS_PROFILE_NOT_ENFORCED"
        assert result["filesystem_network_confined"] is False
        return
    assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER", result
    checks = result["probe"]["checks"]
    assert {k for k in checks if k != "scratch_write"} == {
        "outside_read", "source_write", "loopback_socket",
        "external_socket", "descendant_fork"}
    assert all(v == "DENIED_BY_OS" for k, v in checks.items()
               if k != "scratch_write")
    assert checks["scratch_write"] == "ALLOWED"


def test_monotonic_wall_clock_30s_kills_blocked_worker():
    result = sandbox.run_synthetic_probe("sleep", wall_seconds=30)
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


def test_exact_source_read_inside_native_profile():
    result = sandbox.run_synthetic_probe("success")
    assert result["descriptor_absent"] is True
    assert result["synthetic_source_unchanged"] is True
    assert result["probe"] is not None, result
    if sys.platform == "linux":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER", result
        assert result["probe"]["source_length_sample"] > 0
        assert result["probe"]["landlock_abi"] >= 3
        assert result["scratch_report_mode"] == 0o600
    else:
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
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


def test_windows_breakaway_denied():
    if sys.platform != "win32":
        pytest.skip("Linux denies fork/clone via seccomp")
    result = sandbox.run_synthetic_probe("breakaway")
    assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
    assert result["probe"]["breakaway"] == "BREAKAWAY_DENIED_BY_JOB"


def test_windows_descendants_killed_in_job():
    if sys.platform != "win32":
        pytest.skip("Linux denies fork via seccomp")
    result = sandbox.run_synthetic_probe("descendant", wall_seconds=2)
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
