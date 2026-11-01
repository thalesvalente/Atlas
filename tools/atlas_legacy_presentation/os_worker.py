"""Trusted synthetic-only adversarial worker; never parses private payloads."""
from __future__ import annotations

import argparse
import errno
import json
import os
from pathlib import Path
import socket
import sys
import time


def _report(scratch: Path, payload: dict) -> None:
    # Test-only receipt, not a publishable descriptor.
    # Exclusive create: a hostile existing file can never be clobbered.
    with (scratch / "os-probe-report.json").open("x", encoding="utf-8") as fp:
        json.dump({**payload, "worker_optimize": sys.flags.optimize},
                  fp, sort_keys=True)
        fp.flush()
        os.fsync(fp.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--outside", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--mode", choices=(
        "denials", "memory", "sleep", "success", "breakaway", "descendant"),
        required=True)
    parser.add_argument("--supervisor-pid", type=int, required=True)
    args = parser.parse_args()
    if sys.platform != "linux":
        # Job-only probes MUST NOT inspect non-fixture source or do any network.
        if args.mode == "memory":
            try:
                block = bytearray(300 * 1024 * 1024)
                block[0] = 7
                verdict = "ALLOCATED_OVER_LIMIT"
            except MemoryError:
                verdict = "MEMORY_ERROR_OS_LIMIT"
            _report(args.scratch, {"memory_probe": verdict})
        elif args.mode == "sleep":
            _report(args.scratch, {"sleep_started": True})
            time.sleep(90)
        elif args.mode == "success":
            _report(args.scratch, {"job_probe": True})
        elif args.mode == "denials":
            _report(args.scratch, {"isolation": "OS_PROFILE_NOT_ENFORCED"})
        elif args.mode == "breakaway":
            import subprocess
            try:
                child = subprocess.Popen([sys.executable, "-c", "pass"],
                                         creationflags=0x01000000)
                child.wait(timeout=4)
                verdict = "BREAKAWAY_SUCCEEDED_UNSAFE"
            except OSError:
                verdict = "BREAKAWAY_DENIED_BY_JOB"
            _report(args.scratch, {"breakaway": verdict})
        elif args.mode == "descendant":
            import subprocess
            child = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(90)"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            _report(args.scratch, {"descendant_started": child.pid})
            time.sleep(90)
        return 0

    try:
        # -I -S: no user site/startup hooks. Trusted imports before source read.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from os_linux_isolation import enforce
        evidence = enforce(args.source, args.scratch,
                           supervisor_pid=args.supervisor_pid)
    except Exception as exc:
        reason = (exc.args[0] if type(exc).__name__ == "IsolationUnavailable"
                  else "SETUP_FAILED")
        _report(args.scratch, {"isolation": "OS_ISOLATION_UNVERIFIED",
                               "reason": reason})
        return 78

    if args.mode in ("breakaway", "descendant"):
        _report(args.scratch, {"isolation": "ENFORCED",
                               "operation": "DENIED_UNSUPPORTED_ON_LINUX",
                               **evidence})
        return 79
    if args.mode == "sleep":
        _report(args.scratch, {"isolation": "ENFORCED", "sleep_started": True,
                               **evidence})
        time.sleep(90)
        return 0
    if args.mode == "memory":
        try:
            block = bytearray(300 * 1024 * 1024)
            block[0] = 7
            verdict = "ALLOCATED_OVER_LIMIT"
        except MemoryError:
            verdict = "MEMORY_ERROR_OS_LIMIT"
        _report(args.scratch, {"isolation": "ENFORCED",
                               "memory_probe": verdict, **evidence})
        return 0 if verdict == "MEMORY_ERROR_OS_LIMIT" else 79
    if args.mode == "success":
        with args.source.open("rb") as handle:
            payload = handle.read(128)
        _report(args.scratch, {"isolation": "ENFORCED",
                               "source_length_sample": len(payload),
                               **evidence})
        return 0

    checks = {}
    for name, action in (
        ("outside_read", lambda: args.outside.open("rb").read(1)),
        ("source_write", lambda: args.source.open("ab").write(b"X")),
        ("loopback_socket", lambda: socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)),
        ("external_socket", lambda: socket.socket(
            socket.AF_INET6, socket.SOCK_STREAM)),
        ("descendant_fork", lambda: os.fork()),
    ):
        try:
            result = action()
            if isinstance(result, socket.socket):
                result.close()
            checks[name] = "PERMITTED_UNSAFE"
        except OSError as exc:
            checks[name] = ("DENIED_BY_OS" if exc.errno in (
                errno.EACCES, errno.EPERM) else "UNEXPECTED_ERROR")
        except Exception:
            checks[name] = "UNEXPECTED_ERROR"
    try:
        (args.scratch / "os-owned-write.tmp").write_text(
            "synthetic", encoding="utf-8")
        checks["scratch_write"] = "ALLOWED"
    except Exception:
        checks["scratch_write"] = "UNEXPECTED_ERROR"
    _report(args.scratch, {"isolation": "ENFORCED", "checks": checks, **evidence})
    safe = (all(value == "DENIED_BY_OS" for name, value in checks.items()
                if name != "scratch_write") and checks["scratch_write"] == "ALLOWED")
    return 0 if safe else 79


if __name__ == "__main__":
    raise SystemExit(main())
