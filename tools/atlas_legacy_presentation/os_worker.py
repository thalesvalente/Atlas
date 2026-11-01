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
    if os.name == "nt":
        # Native check of the ACTUAL child file, not only the directory.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from os_windows_acl import verify_private_child
        verify_private_child(scratch, scratch / "os-probe-report.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--outside", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--mode", choices=(
        "denials", "memory", "sleep", "success", "breakaway", "descendant"),
        required=True)
    parser.add_argument("--supervisor-pid", type=int, required=True)
    parser.add_argument("--broker-report-handle", type=int)
    parser.add_argument("--broker-denied-source-handle", type=int)
    parser.add_argument("--broker-source-length", type=int)
    parser.add_argument("--broker-loopback-port", type=int)
    args = parser.parse_args()
    broker_values = (
        args.broker_report_handle, args.broker_denied_source_handle,
        args.broker_source_length, args.broker_loopback_port)
    if any(v is not None for v in broker_values):
        if (sys.platform != "win32" or
                any(not isinstance(v, int) or v <= 0 for v in broker_values)):
            return 78
        return _windows_broker_worker(args)
    # Enforce synthetic boundary *in the independently executable worker*.
    # A direct CLI call must not inherit the supervisor's trust automatically.
    try:
        if os.getppid() != args.supervisor_pid:
            return 78
        if not (args.source.is_absolute() and args.outside.is_absolute()
                and args.scratch.is_absolute()):
            return 78
        parent = args.source.parent.parent
        if (args.source.name != "os-allowlisted.json" or
                args.outside.name != "os-outside.json" or
                args.source.parent.name != "input" or
                args.outside.parent != args.source.parent or
                args.scratch != parent / "scratch" or
                parent.name != "os-invented" or
                not parent.parent.name.startswith("atlas-c2b-")):
            return 78
        for path in (args.source, args.outside, args.scratch):
            for ancestor in (path, *path.parents):
                st = ancestor.lstat()
                if ancestor.is_symlink() or (
                        os.name == "nt" and
                        getattr(st, "st_file_attributes", 0) & 0x400):
                    return 78
        if os.name == "nt":
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from os_windows_acl import verify_private_scratch
            verify_private_scratch(args.scratch)
        else:
            import stat
            sc = args.scratch.stat()
            if (not stat.S_ISDIR(sc.st_mode) or sc.st_uid != os.getuid()
                    or stat.S_IMODE(sc.st_mode) != 0o700):
                return 78
        src = args.source.stat()
        if not args.source.is_file() or src.st_nlink != 1:
            return 78
    except Exception:
        return 78
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



def _windows_broker_worker(args) -> int:
    """Never read source bytes from a caller-supplied handle.

    The trusted supervisor checks the exact invented source and owns its
    non-inheritable read handle. The worker inherits only a WRITE-only report
    handle; a forged AppContainer launch therefore cannot trigger a read of
    a separately inherited private file.
    """
    try:
        import ctypes
        import msvcrt
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        adv = ctypes.WinDLL("advapi32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        adv.OpenProcessToken.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
        adv.OpenProcessToken.restype = wintypes.BOOL
        adv.GetTokenInformation.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD)]
        adv.GetTokenInformation.restype = wintypes.BOOL
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        token = wintypes.HANDLE()
        if not adv.OpenProcessToken(k.GetCurrentProcess(), 0x0008,
                                    ctypes.byref(token)):
            return 78
        try:
            is_app = wintypes.DWORD()
            length = wintypes.DWORD()
            caps = ctypes.create_string_buffer(256)
            if not adv.GetTokenInformation(
                    token, 29, ctypes.byref(is_app), ctypes.sizeof(is_app),
                    ctypes.byref(length)) or is_app.value != 1:
                return 78
            if not adv.GetTokenInformation(
                    token, 30, caps, len(caps), ctypes.byref(length)):
                return 78
            if ctypes.cast(caps, ctypes.POINTER(wintypes.DWORD))[0] != 0:
                return 78
        finally:
            k.CloseHandle(token)
        if os.getppid() != args.supervisor_pid or not all(
                p.is_absolute() for p in (
                    args.source, args.outside, args.scratch)):
            return 78
        if not (
                args.source.name == "os-allowlisted.json" and
                args.outside.name == "os-outside.json" and
                args.scratch.name == "scratch" and
                args.source.parent.name == "input" and
                args.outside.parent == args.source.parent and
                args.scratch.parent == args.source.parent.parent):
            return 78
        # Verify the supervisor's source handle identifier is INVALID in
        # this child. It must NOT be inherited or read, even under forged
        # AppContainer credentials or command-line switches.
        k.GetHandleInformation.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.GetHandleInformation.restype = wintypes.BOOL
        observed = wintypes.DWORD()
        if k.GetHandleInformation(wintypes.HANDLE(
                args.broker_denied_source_handle), ctypes.byref(observed)):
            return 78
        if ctypes.get_last_error() != 6:  # ERROR_INVALID_HANDLE
            return 78
        expected_len = len(b'{"synthetic":true,"payload":"invented"}')
        if args.broker_source_length != expected_len:
            return 78
        def report(payload):
            output = {**payload, "worker_optimize": sys.flags.optimize,
                      "appcontainer_token_verified": True,
                      "source_handle_not_inherited": True}
            data = json.dumps(output, sort_keys=True).encode("utf-8")
            with os.fdopen(msvcrt.open_osfhandle(
                    args.broker_report_handle,
                    os.O_WRONLY | os.O_BINARY), "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        if args.mode == "success":
            report({"isolation": "APPCONTAINER_NO_NETWORK_CAPABILITIES",
                    "source_length_sample": args.broker_source_length,
                    "source_handle_not_inherited": True})
            return 0
        if args.mode == "memory":
            try:
                block = bytearray(300 * 1024 * 1024)
                block[0] = 1
                verdict = "ALLOCATED_OVER_LIMIT"
            except MemoryError:
                verdict = "MEMORY_ERROR_OS_LIMIT"
            report({"memory_probe": verdict, "isolation":
                    "APPCONTAINER_NO_NETWORK_CAPABILITIES"})
            return 0 if verdict == "MEMORY_ERROR_OS_LIMIT" else 79
        if args.mode == "sleep":
            report({"sleep_started": True, "isolation":
                    "APPCONTAINER_NO_NETWORK_CAPABILITIES"})
            time.sleep(90)
            return 0
        if args.mode == "descendant":
            import subprocess
            try:
                child = subprocess.Popen(
                    [sys.executable, "-I", "-S", "-c",
                     "import time; time.sleep(90)"],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            except OSError as exc:
                # Child-creation denial is a distinct, valid negative proof.
                # An unrelated runtime/loader error is NOT a security pass.
                denied = isinstance(exc, PermissionError) and (
                    exc.errno == 13 or getattr(exc, "winerror", None) == 5)
                report({"child_spawn": "DENIED_BY_OS" if denied else
                        "UNVERIFIED_ERROR",
                        "child_os_errno": exc.errno,
                        "isolation": "APPCONTAINER_NO_NETWORK_CAPABILITIES"})
                return 0 if denied else 79
            report({"descendant_started": child.pid,
                    "isolation": "APPCONTAINER_NO_NETWORK_CAPABILITIES"})
            time.sleep(90)
            return 0
        if args.mode == "breakaway":
            import subprocess
            try:
                child = subprocess.Popen(
                    [sys.executable, "-I", "-S", "-c", "pass"],
                    creationflags=0x01000000, stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                child.wait(timeout=4)
                verdict = "BREAKAWAY_SUCCEEDED_UNSAFE"
            except OSError:
                verdict = "BREAKAWAY_DENIED_BY_JOB"
            report({"breakaway": verdict,
                    "isolation": "APPCONTAINER_NO_NETWORK_CAPABILITIES"})
            return 0 if verdict == "BREAKAWAY_DENIED_BY_JOB" else 79
        if args.mode != "denials":
            return 78
        checks = {}
        for name, action in (
            ("outside_read", lambda: args.outside.open("rb").read(1)),
            ("source_write", lambda: args.source.open("ab").write(b"x")),
            ("scratch_path_write", lambda: (
                args.scratch / "broker-path-write.tmp").write_text("x")),
        ):
            try:
                action()
                checks[name] = "PERMITTED_UNSAFE"
            except PermissionError:
                checks[name] = "DENIED_BY_OS"
            except OSError:
                checks[name] = "OTHER_ERROR_UNVERIFIED"
        connect_error = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                connect_error = sock.connect_ex(
                    ("127.0.0.1", args.broker_loopback_port))
        except OSError as exc:
            connect_error = exc.errno
        # On Windows, timed connect_ex may yield 10035 (in progress)
        # or 10060 (timeout) when WFP silently drops loopback.
        # These outcomes alone do not prove enforcement. Do NOT equate a plain timeout
        # with OS denial: the supervisor additionally verifies the WFP
        # exemption inventory, token capabilities, positive control and
        # absence of an accepted worker connection.
        checks["loopback_connect"] = (
            "DENIED_BY_OS" if connect_error in (13, 10013) else
            "NO_CONNECTION_TIMEOUT" if connect_error in (10035, 10060) else
            "PERMITTED_OR_UNVERIFIED")
        safe = all(v == "DENIED_BY_OS" for k, v in checks.items()
                   if k != "loopback_connect") and checks[
                       "loopback_connect"] in (
                           "DENIED_BY_OS", "NO_CONNECTION_TIMEOUT")
        report({"isolation": "APPCONTAINER_NO_NETWORK_CAPABILITIES",
                "checks": checks, "loopback_connect_os_error": connect_error})
        return 0 if safe else 79
    except Exception:
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
