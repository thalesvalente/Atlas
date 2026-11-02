"""AP04 C2-B native supervisor, exclusively for internally generated synthetic fixtures.

The public probe API accepts no paths, so a caller cannot pass private files.
Production acquisition is unconditionally refused until C2-D qualification.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time

MAX_MEMORY_BYTES = 256 * 1024 * 1024
MAX_WALL_SECONDS = 30.0
_OPERATIONS = frozenset({"denials", "memory", "sleep", "success",
                         "breakaway", "descendant"})
_INVENTED_SOURCE = b'{"synthetic":true,"payload":"invented"}'
_INVENTED_OUTSIDE = b'{"synthetic":true,"outside":"invented"}'


class OSProfileNotEnforced(RuntimeError):
    def __init__(self, code: str = "OS_PROFILE_NOT_ENFORCED") -> None:
        self.code = code
        super().__init__(code)


def require_production_acquisition(*_args: object, **_kwargs: object) -> None:
    raise OSProfileNotEnforced("PRODUCTION_ACQUISITION_BLOCKED")


def _chain_no_reparse(path: Path) -> None:
    """lstat every ancestor; never silently follow a junction/point/reparse."""
    for part in (path, *path.parents):
        st = part.lstat()
        if stat.S_ISLNK(st.st_mode) or (
                os.name == "nt" and getattr(st, "st_file_attributes", 0) & 0x400):
            raise OSProfileNotEnforced("UNSAFE_REPARSE_OR_SYMLINK")


def _preflight(source: Path, outside: Path, scratch: Path) -> None:
    if not all(p.is_absolute() for p in (source, outside, scratch)):
        raise OSProfileNotEnforced("PATH_NOT_ABSOLUTE")
    try:
        for path in (source, outside, scratch):
            _chain_no_reparse(path)
        src, out, sc = source.lstat(), outside.lstat(), scratch.lstat()
    except OSError:
        raise OSProfileNotEnforced("PATH_UNVERIFIED") from None
    if not (stat.S_ISREG(src.st_mode) and src.st_nlink == 1
            and stat.S_ISREG(out.st_mode) and out.st_nlink == 1
            and stat.S_ISDIR(sc.st_mode)):
        raise OSProfileNotEnforced("UNSAFE_FIXTURE")
    if (source.name != "os-allowlisted.json" or
            outside.name != "os-outside.json" or
            source.parent.name != "input" or outside.parent != source.parent or
            scratch.name != "scratch" or scratch.parent != source.parent.parent or
            scratch.parent.name != "os-invented"):
        raise OSProfileNotEnforced("SYNTHETIC_FIXTURE_REQUIRED")
    if os.name == "nt":
        from .os_windows_acl import WindowsScratchUnverified, verify_private_scratch
        try:
            verify_private_scratch(scratch)
        except WindowsScratchUnverified as exc:
            raise OSProfileNotEnforced(str(exc)) from None
        except Exception:
            raise OSProfileNotEnforced("WINDOWS_SCRATCH_API_UNVERIFIED") from None
    elif sc.st_uid != os.getuid() or stat.S_IMODE(sc.st_mode) != 0o700:
        raise OSProfileNotEnforced("SCRATCH_NOT_PRIVATE")


def _write_invented(path: Path, value: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as f:
            f.write(value)
    finally:
        os.close(fd)


def run_synthetic_probe(mode: str, *, wall_seconds: float = MAX_WALL_SECONDS) -> dict:
    """Only generate/use disposable built-in invented fixtures. No external paths."""
    if mode not in _OPERATIONS or not 0 < wall_seconds <= MAX_WALL_SECONDS:
        raise OSProfileNotEnforced("INVALID_PROBE")
    optimize = os.environ.get("ATLAS_WORKER_OPTIMIZE", "0")
    if optimize not in ("0", "1"):
        raise OSProfileNotEnforced("INVALID_WORKER_OPTIMIZE")
    with tempfile.TemporaryDirectory(prefix="atlas-c2b-") as temporary:
        root = Path(temporary) / "os-invented"
        root.mkdir(mode=0o700)
        inputs = root / "input"
        inputs.mkdir(mode=0o700)
        scratch = root / "scratch"
        if os.name == "nt":
            from .os_windows_acl import (WindowsScratchUnverified,
                                         create_private_scratch)
            try:
                create_private_scratch(scratch)
            except WindowsScratchUnverified as exc:
                raise OSProfileNotEnforced(str(exc)) from None
        else:
            scratch.mkdir(mode=0o700)
            scratch.chmod(0o700)
            # A second native Landlock layer revokes access to all sources.
            # The anchor is an internal, disposable, invented scratch file.
            _write_invented(scratch / ".os-scratch-only-anchor",
                            b"atlas-c2b-invented-landlock-scratch-anchor")
        source = inputs / "os-allowlisted.json"
        outside = inputs / "os-outside.json"
        _write_invented(source, _INVENTED_SOURCE)
        _write_invented(outside, _INVENTED_OUTSIDE)
        _preflight(source, outside, scratch)
        return _probe_owned(source, outside, scratch, mode,
                            wall_seconds=wall_seconds, optimize=optimize)


def _probe_owned(source: Path, outside: Path, scratch: Path, mode: str, *,
                 wall_seconds: float, optimize: str) -> dict:
    """Internal primitive; never treat direct use as authorization to acquire."""
    # Revalidate before worker; no other exported API calls this primitive.
    _preflight(source, outside, scratch)
    worker = Path(__file__).with_name("os_worker.py").resolve(strict=True)
    report = scratch / "os-probe-report.json"
    if report.exists() or report.is_symlink():
        raise OSProfileNotEnforced("REPORT_ALREADY_EXISTS")
    args = [sys.executable, "-I"]
    if optimize == "1":
        args.append("-O")
    args += ["-S", str(worker), "--source", str(source),
             "--outside", str(outside), "--scratch", str(scratch),
             "--mode", mode, "--supervisor-pid", str(os.getpid())]
    if sys.platform == "win32":
        from .os_windows_job import run_synthetic_job
        try:
            # Operations that read the synthetic source or challenge network
            # NEVER run in the Job-only path. Job-only modes exercise budgets,
            # process containment and fault injection without reading payloads.
            outcome = run_synthetic_job(
                args, wall_seconds=wall_seconds,
                appcontainer=mode in ("success", "denials"))
        except Exception as exc:
            raise OSProfileNotEnforced(
                getattr(exc, "args", ["JOB_SETUP_FAILED"])[0]) from None
    elif sys.platform == "linux":
        started = time.monotonic()
        deadline = started + wall_seconds
        proc = subprocess.Popen(
            args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, close_fds=True, start_new_session=True)
        timed_out = False
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
            if time.monotonic() >= deadline:
                timed_out = True
        except subprocess.TimeoutExpired:
            timed_out = True
        if timed_out:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                raise OSProfileNotEnforced("WORKER_KILL_UNVERIFIED") from None
        outcome = {
            "status": "OS_WALL_TIMEOUT_TERMINATED" if timed_out else "PROBE_EXITED",
            "exit_code": proc.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "memory_limit_bytes": MAX_MEMORY_BYTES,
            "memory_metric": "RLIMIT_AS_virtual_address_space",
            "filesystem_network_confined": False}
    else:
        raise OSProfileNotEnforced("PLATFORM_UNSUPPORTED")
    # These booleans are observed from the disposable fixture, never constants.
    descriptor_absent = not any(scratch.glob("atlas-c2-*.json"))
    source_unchanged = source.read_bytes() == _INVENTED_SOURCE
    result = {**outcome, "descriptor_published": not descriptor_absent,
              "descriptor_absent": descriptor_absent,
              "synthetic_source_unchanged": source_unchanged}
    if not descriptor_absent or not source_unchanged:
        raise OSProfileNotEnforced("SYNTHETIC_BOUNDARY_VIOLATED")
    if outcome["timed_out"]:
        return {**result,
                "qualification": "OS_CONTROL_TESTED_IN_RUNNER_WALL_ONLY",
                "requested_worker_optimize": int(optimize)}
    detail = None
    if sys.platform == "win32" and report.exists():
        from .os_windows_acl import WindowsScratchUnverified, verify_private_child
        try:
            verify_private_child(scratch, report)
        except (WindowsScratchUnverified, OSError):
            raise OSProfileNotEnforced("WINDOWS_CHILD_ACL_UNVERIFIED") from None
    if report.is_file() and not report.is_symlink() and report.stat().st_size <= 4096:
        try:
            detail = json.loads(report.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            detail = None
    result["probe"] = detail
    result["requested_worker_optimize"] = int(optimize)
    if detail is not None and detail.get("worker_optimize") != int(optimize):
        raise OSProfileNotEnforced("WORKER_OPTIMIZE_UNVERIFIED")
    if sys.platform == "win32":
        appcontainer_mode = mode in ("success", "denials")
        token_verified = (
            outcome.get("appcontainer_token_verified") is True and
            outcome.get("appcontainer_loopback_exception_absent") is True and
            outcome.get("loopback_control_passed") is True and
            outcome.get("loopback_worker_accepted") is False)
        report_native = (
            isinstance(detail, dict) and
            detail.get("isolation") == "APPCONTAINER_NO_NETWORK_CAPABILITIES")
        if appcontainer_mode:
            if not (outcome["exit_code"] == 0 and token_verified and report_native):
                raise OSProfileNotEnforced("WINDOWS_APPCONTAINER_OS_PROFILE_MISSING")
            if mode == "denials":
                checks = detail.get("checks", {})
                if (set(checks) != {
                        "outside_read", "source_read", "source_write",
                        "scratch_path_write",
                        "loopback_connect"} or
                    any(v != "DENIED_BY_OS" for k, v in checks.items()
                        if k != "loopback_connect") or
                    checks["loopback_connect"] not in (
                        "DENIED_BY_OS", "NO_CONNECTION_TIMEOUT") or
                    detail.get("loopback_connect_os_error") not in (
                        13, 10013, 10035, 10060)):
                    raise OSProfileNotEnforced("WINDOWS_NATIVE_OS_DENIAL_MISSING")
                result["qualification"] = (
                    "OS_CONTROL_TESTED_IN_RUNNER_APPCONTAINER")
                result["filesystem_network_confined"] = True
            else:
                if detail.get("source_length_sample") != len(_INVENTED_SOURCE):
                    raise OSProfileNotEnforced("WINDOWS_HANDLE_SOURCE_UNVERIFIED")
                result["qualification"] = (
                    "OS_CONTROL_TESTED_IN_RUNNER_APPCONTAINER_SOURCE_ONLY")
                result["filesystem_network_confined"] = False
        else:
            result["qualification"] = (
                "OS_CONTROL_TESTED_IN_RUNNER_JOB_ONLY"
                if outcome["exit_code"] == 0 and detail is not None
                else "OS_PROFILE_NOT_ENFORCED")
        result["windows_scratch_acl_checked"] = True
        return result
    enforced = (outcome["exit_code"] == 0 and isinstance(detail, dict) and
                detail.get("isolation") == "ENFORCED")
    result["qualification"] = (
        "OS_CONTROL_TESTED_IN_RUNNER" if enforced else
        "OS_ISOLATION_UNVERIFIED")
    result["filesystem_network_confined"] = enforced
    if report.is_file():
        result["scratch_report_mode"] = stat.S_IMODE(report.stat().st_mode)
    return result
