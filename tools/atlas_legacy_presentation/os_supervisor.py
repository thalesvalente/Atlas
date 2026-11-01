"""Native AP04 C2-B supervisor (test-only; production acquisition denied)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time

MAX_MEMORY_BYTES = 256 * 1024 * 1024
MAX_WALL_SECONDS = 30.0
OPERATIONS = frozenset({"denials", "memory", "sleep", "success",
                        "breakaway", "descendant"})


class OSProfileNotEnforced(RuntimeError):
    def __init__(self, code: str = "OS_PROFILE_NOT_ENFORCED") -> None:
        self.code = code
        super().__init__(code)


def require_production_acquisition(*_args: object, **_kwargs: object) -> None:
    """No test flag may grant real source access. Integration belongs to C2-D."""
    raise OSProfileNotEnforced("PRODUCTION_ACQUISITION_BLOCKED")


def _preflight(source: Path, outside: Path, scratch: Path) -> None:
    if not (source.is_absolute() and outside.is_absolute() and
            scratch.is_absolute()):
        raise OSProfileNotEnforced("PATH_NOT_ABSOLUTE")
    if source.is_symlink() or outside.is_symlink() or scratch.is_symlink():
        raise OSProfileNotEnforced("UNSAFE_SYMLINK")
    src, sc = source.lstat(), scratch.lstat()
    if not stat.S_ISREG(src.st_mode) or src.st_nlink != 1 or not stat.S_ISDIR(sc.st_mode):
        raise OSProfileNotEnforced("UNSAFE_INPUT")
    if scratch == source.parent or source.parent in scratch.parents or (
            scratch in source.parents):
        raise OSProfileNotEnforced("UNSAFE_SCRATCH")
    if os.name != "nt" and (sc.st_uid != os.getuid() or
                            stat.S_IMODE(sc.st_mode) != 0o700):
        raise OSProfileNotEnforced("UNSAFE_SCRATCH")
    if not outside.is_file() or source == outside:
        raise OSProfileNotEnforced("UNSAFE_OUTSIDE_PROBE")
    # Synthetic-only API: reject ordinary caller paths before launch.
    if (source.name != "os-allowlisted.json" or
            outside.name != "os-outside.json" or
            source.parent.name != "input" or
            outside.parent != source.parent or
            scratch.name != "scratch" or
            scratch.parent != source.parent.parent or
            scratch.parent.name != "os-invented"):
        raise OSProfileNotEnforced("SYNTHETIC_FIXTURE_REQUIRED")


def run_synthetic_probe(source: Path, outside: Path, scratch: Path,
                        mode: str, *, wall_seconds: float = MAX_WALL_SECONDS) -> dict:
    """Run built-in negative probes, using only invented, test-owned fixtures.

    The JSON receipt is never an importable descriptor. The caller is solely
    responsible for its own test scratch, no recursive scientific-file cleanup.
    """
    if mode not in OPERATIONS or not 0 < wall_seconds <= MAX_WALL_SECONDS:
        raise OSProfileNotEnforced("INVALID_PROBE")
    source, outside, scratch = Path(source), Path(outside), Path(scratch)
    _preflight(source, outside, scratch)
    worker = Path(__file__).with_name("os_worker.py").resolve(strict=True)
    report = scratch / "os-probe-report.json"
    if report.exists() or report.is_symlink():
        raise OSProfileNotEnforced("REPORT_ALREADY_EXISTS")
    args = [sys.executable, "-I", "-S", str(worker), "--source", str(source),
            "--outside", str(outside), "--scratch", str(scratch),
            "--mode", mode, "--supervisor-pid", str(os.getpid())]
    if sys.platform == "win32":
        from .os_windows_job import run_synthetic_job
        try:
            outcome = run_synthetic_job(args, wall_seconds=wall_seconds)
        except Exception as exc:
            raise OSProfileNotEnforced(
                getattr(exc, "args", ["JOB_SETUP_FAILED"])[0]) from None
    elif sys.platform == "linux":
        started = time.monotonic()
        proc = subprocess.Popen(
            args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, close_fds=True, start_new_session=True)
        timed_out = False
        try:
            proc.wait(timeout=wall_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=5)
        outcome = {
            "status": "OS_WALL_TIMEOUT_TERMINATED" if timed_out else "PROBE_EXITED",
            "exit_code": proc.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "memory_limit_bytes": MAX_MEMORY_BYTES,
            "memory_metric": "RLIMIT_AS_virtual_address_space",
            "filesystem_network_confined": False}
    else:
        raise OSProfileNotEnforced("PLATFORM_UNSUPPORTED")
    if outcome["timed_out"]:
        return {**outcome, "qualification": "OS_CONTROL_TESTED_IN_RUNNER_WALL_ONLY",
                "descriptor_published": False}
    detail = None
    if report.is_file() and not report.is_symlink() and report.stat().st_size <= 4096:
        try:
            detail = json.loads(report.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            detail = None
    if sys.platform == "win32":
        status = ("OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
                  if outcome["exit_code"] == 0 else "OS_PROFILE_NOT_ENFORCED")
        return {**outcome, "qualification": status, "probe": detail,
                "descriptor_published": False}
    enforced = (outcome["exit_code"] == 0 and isinstance(detail, dict) and
                detail.get("isolation") == "ENFORCED")
    return {**outcome, "qualification": (
                "OS_CONTROL_TESTED_IN_RUNNER" if enforced else
                "OS_ISOLATION_UNVERIFIED"), "probe": detail,
            "filesystem_network_confined": enforced,
            "descriptor_published": False}
