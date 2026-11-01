"""OS negative challenges use disposable entirely invented fixture files."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import pytest
from tools.atlas_legacy_presentation import os_supervisor as sandbox


@pytest.fixture
def synthetic(tmp_path: Path):
    root = tmp_path / "os-invented"
    root.mkdir()
    sources = root / "input"
    sources.mkdir()
    scratch = root / "scratch"
    scratch.mkdir(mode=0o700)
    if os.name != "nt":
        scratch.chmod(0o700)
    source = sources / "os-allowlisted.json"
    source.write_text('{"synthetic":true,"payload":"invented"}', encoding="utf-8")
    outside = sources / "os-outside.json"
    outside.write_text('{"synthetic":true,"outside":"invented"}',
                       encoding="utf-8")
    return source, outside, scratch


def test_production_denied_even_with_synthetic_override():
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="PRODUCTION_ACQUISITION_BLOCKED"):
        sandbox.require_production_acquisition(
            synthetic_fixture=True, source="private")


def test_memory_and_wall_budgets_fixed():
    assert sandbox.MAX_MEMORY_BYTES == 268435456
    assert sandbox.MAX_WALL_SECONDS == 30


def test_preflight_rejects_symlink(synthetic):
    source, outside, scratch = synthetic
    link = source.parent / "os-link"
    try:
        link.symlink_to(source)
    except (OSError, NotImplementedError):
        pytest.skip("Windows runner cannot create a test-owned symlink")
    with pytest.raises(sandbox.OSProfileNotEnforced, match="UNSAFE_SYMLINK"):
        sandbox.run_synthetic_probe(link, outside, scratch, "success")


def test_native_memory_challenge(synthetic):
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(source, outside, scratch, "memory")
    assert result["timed_out"] is False
    assert result["descriptor_published"] is False
    assert result["probe"] is not None, result
    assert list(scratch.glob("atlas-c2-*.json")) == []
    assert result["probe"]["memory_probe"] == "MEMORY_ERROR_OS_LIMIT", result
    if sys.platform == "win32":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
        assert result["memory_metric"] == "JobMemoryLimit_committed_bytes_job_total"
        assert result["job_memory_limit_bytes"] == 268435456
        assert result["kill_on_job_close"] is True
        assert result["breakaway_permitted"] is False
    else:
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER"
        assert result["probe"]["memory_metric"] == "RLIMIT_AS_virtual_address_space"


def test_linux_os_denials_or_windows_explicit_block(synthetic):
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(source, outside, scratch, "denials")
    assert result["descriptor_published"] is False
    if sys.platform == "win32":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
        assert result["probe"] == {"isolation": "OS_PROFILE_NOT_ENFORCED"}
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
    assert source.read_text(encoding="utf-8") == (
        '{"synthetic":true,"payload":"invented"}')


def test_monotonic_wall_clock_30s_kills_blocked_worker(synthetic):
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(
        source, outside, scratch, "sleep", wall_seconds=30)
    assert result["timed_out"] is True, result
    assert result["status"] == "OS_WALL_TIMEOUT_TERMINATED"
    assert result["elapsed_seconds"] >= 29
    assert result["elapsed_seconds"] < 35
    assert result["descriptor_published"] is False
    assert list(scratch.glob("atlas-c2-*.json")) == []


def test_invalid_modes_and_time_budgets_denied(synthetic):
    source, outside, scratch = synthetic
    for mode, budget in (("arbitrary", 1), ("memory", 31), ("memory", 0)):
        with pytest.raises(sandbox.OSProfileNotEnforced, match="INVALID_PROBE"):
            sandbox.run_synthetic_probe(
                source, outside, scratch, mode, wall_seconds=budget)


def test_report_never_overwrites_existing_file(synthetic):
    source, outside, scratch = synthetic
    report = scratch / "os-probe-report.json"
    report.write_text("previous owned report", encoding="utf-8")
    with pytest.raises(sandbox.OSProfileNotEnforced,
                       match="REPORT_ALREADY_EXISTS"):
        sandbox.run_synthetic_probe(source, outside, scratch, "success")
    assert report.read_text(encoding="utf-8") == "previous owned report"


def test_exact_source_read_inside_native_profile(synthetic):
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(source, outside, scratch, "success")
    assert result["descriptor_published"] is False
    assert result["probe"] is not None, result
    if sys.platform == "linux":
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER", result
        assert result["probe"]["source_length_sample"] > 0
        assert result["probe"]["landlock_abi"] >= 3
        import stat
        assert stat.S_IMODE(
            (scratch / "os-probe-report.json").stat().st_mode) == 0o600
    else:
        assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"


def test_windows_breakaway_denied(synthetic):
    if sys.platform != "win32":
        pytest.skip("Not applicable: Linux deny fork/clone in native seccomp probe")
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(source, outside, scratch, "breakaway")
    assert result["qualification"] == "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
    assert result["probe"]["breakaway"] == "BREAKAWAY_DENIED_BY_JOB"


def test_windows_descendants_killed_in_job(synthetic):
    if sys.platform != "win32":
        pytest.skip("Not applicable: Linux forks are denied")
    source, outside, scratch = synthetic
    result = sandbox.run_synthetic_probe(
        source, outside, scratch, "descendant", wall_seconds=2)
    assert result["timed_out"] is True
    assert result["active_processes_after_timeout"] == 0
    assert result["descriptor_published"] is False


def test_windows_association_error_terminates_suspended_worker(synthetic):
    if sys.platform != "win32":
        pytest.skip("Not applicable: Windows Job only")
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
        sandbox.run_synthetic_probe(bogus, outside, scratch, "success")
    assert not (scratch / "os-probe-report.json").exists()


def test_windows_job_refuses_arbitrary_entrypoint(synthetic):
    if sys.platform != "win32":
        pytest.skip("Windows Job-specific negative contract")
    from tools.atlas_legacy_presentation.os_windows_job import (
        NativeJobUnavailable, run_synthetic_job)
    with pytest.raises(NativeJobUnavailable,
                       match="UNTRUSTED_WORKER_REJECTED"):
        run_synthetic_job([sys.executable, "-I", "-S", "untrusted.py"])
