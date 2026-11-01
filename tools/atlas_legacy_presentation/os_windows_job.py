"""Windows native Job Object budgets, synthetic probes only.

A Job Object caps job-wide committed memory and child lifetime; it does not
restrict filesystem or network. Acquisition remains unconditionally blocked.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import subprocess
import sys
import time

JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
JOB_OBJECT_EXTENDED_LIMIT = 9
CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
MEMORY_BYTES = 256 * 1024 * 1024
WALL_SECONDS = 30.0


class NativeJobUnavailable(RuntimeError):
    pass


class _Basic(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD)]


class _Counters(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint64) for n in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class _Extended(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _Basic), ("IoInfo", _Counters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


class _Accounting(ctypes.Structure):
    _fields_ = [("TotalUserTime", ctypes.c_int64),
                ("TotalKernelTime", ctypes.c_int64),
                ("ThisPeriodTotalUserTime", ctypes.c_int64),
                ("ThisPeriodTotalKernelTime", ctypes.c_int64),
                ("TotalPageFaultCount", wintypes.DWORD),
                ("TotalProcesses", wintypes.DWORD),
                ("ActiveProcesses", wintypes.DWORD),
                ("TotalTerminatedProcesses", wintypes.DWORD)]


class _Startup(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
                ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
                ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD),
                ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                ("lpReserved2", ctypes.c_void_p),
                ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE),
                ("hStdError", wintypes.HANDLE)]


class _Proc(ctypes.Structure):
    _fields_ = [("hProcess", wintypes.HANDLE),
                ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD),
                ("dwThreadId", wintypes.DWORD)]


def run_synthetic_job(argv: list[str], *, wall_seconds: float = WALL_SECONDS,
                      inject_assign_failure: bool = False) -> dict:
    """CREATE_SUSPENDED -> set/query Job -> assign -> resume -> monotonic kill."""
    if sys.platform != "win32":
        raise NativeJobUnavailable("WINDOWS_ONLY")
    if not 0 < wall_seconds <= WALL_SECONDS:
        raise NativeJobUnavailable("UNSAFE_WALL_LIMIT")
    # Not a general-purpose Job-as-sandbox launcher: fixed, reviewed worker only.
    from pathlib import Path
    expected = Path(__file__).with_name("os_worker.py").resolve(strict=True)
    if (len(argv) < 4 or
            Path(argv[0]).resolve() != Path(sys.executable).resolve() or
            argv[1:3] != ["-I", "-S"] or
            Path(argv[3]).resolve() != expected):
        raise NativeJobUnavailable("UNTRUSTED_WORKER_REJECTED")
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k.CreateJobObjectW.restype = wintypes.HANDLE
    k.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    k.SetInformationJobObject.restype = wintypes.BOOL
    k.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD)]
    k.QueryInformationJobObject.restype = wintypes.BOOL
    k.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
        ctypes.POINTER(_Startup), ctypes.POINTER(_Proc)]
    k.CreateProcessW.restype = wintypes.BOOL
    k.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k.AssignProcessToJobObject.restype = wintypes.BOOL
    k.ResumeThread.argtypes = [wintypes.HANDLE]
    k.ResumeThread.restype = wintypes.DWORD
    k.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k.WaitForSingleObject.restype = wintypes.DWORD
    k.GetExitCodeProcess.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k.GetExitCodeProcess.restype = wintypes.BOOL
    k.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k.TerminateJobObject.restype = wintypes.BOOL
    k.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k.TerminateProcess.restype = wintypes.BOOL
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    k.CloseHandle.restype = wintypes.BOOL
    job = k.CreateJobObjectW(None, None)
    if not job:
        raise NativeJobUnavailable("JOB_CREATE_FAILED")
    process = _Proc()
    created = associated = False
    started = time.monotonic()
    timed_out = False
    try:
        spec = _Extended()
        spec.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
        spec.JobMemoryLimit = MEMORY_BYTES
        if not k.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT,
                                         ctypes.byref(spec), ctypes.sizeof(spec)):
            raise NativeJobUnavailable("JOB_SET_LIMIT_FAILED")
        check = _Extended()
        returned = wintypes.DWORD()
        if not k.QueryInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT,
                                           ctypes.byref(check), ctypes.sizeof(check),
                                           ctypes.byref(returned)):
            raise NativeJobUnavailable("JOB_QUERY_LIMIT_FAILED")
        flags = int(check.BasicLimitInformation.LimitFlags)
        required = JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if (flags & required) != required or flags & (
                JOB_OBJECT_LIMIT_BREAKAWAY_OK |
                JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK) or (
                check.JobMemoryLimit != MEMORY_BYTES):
            raise NativeJobUnavailable("JOB_LIMIT_MISMATCH")
        si = _Startup()
        si.cb = ctypes.sizeof(si)
        line = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        if not k.CreateProcessW(argv[0], line, None, None, False,
                                CREATE_SUSPENDED | CREATE_NO_WINDOW, None, None,
                                ctypes.byref(si), ctypes.byref(process)):
            raise NativeJobUnavailable("JOB_CREATE_SUSPENDED_FAILED")
        created = True
        if inject_assign_failure:
            raise NativeJobUnavailable("JOB_ASSIGN_FAILED_INJECTED")
        if not k.AssignProcessToJobObject(job, process.hProcess):
            raise NativeJobUnavailable("JOB_ASSIGN_FAILED")
        associated = True
        if k.ResumeThread(process.hThread) == 0xFFFFFFFF:
            raise NativeJobUnavailable("JOB_RESUME_FAILED")
        deadline = started + wall_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                if not k.TerminateJobObject(job, 124):
                    raise NativeJobUnavailable("JOB_TERMINATION_FAILED")
                k.WaitForSingleObject(process.hProcess, 2000)
                break
            wait = k.WaitForSingleObject(process.hProcess,
                                         max(1, min(100, int(remaining * 1000))))
            if wait == WAIT_OBJECT_0:
                break
            if wait != WAIT_TIMEOUT:
                raise NativeJobUnavailable("JOB_WAIT_FAILED")
        code = wintypes.DWORD()
        if not k.GetExitCodeProcess(process.hProcess, ctypes.byref(code)):
            raise NativeJobUnavailable("JOB_EXIT_STATUS_FAILED")
        accounting = _Accounting()
        if timed_out:
            for _ in range(25):
                if not k.QueryInformationJobObject(
                        job, 1, ctypes.byref(accounting),
                        ctypes.sizeof(accounting), None):
                    raise NativeJobUnavailable("JOB_ACCOUNTING_QUERY_FAILED")
                if accounting.ActiveProcesses == 0:
                    break
                time.sleep(0.04)
            if accounting.ActiveProcesses != 0:
                raise NativeJobUnavailable("JOB_DESCENDANTS_NOT_TERMINATED")
        return {
            "status": "OS_WALL_TIMEOUT_TERMINATED" if timed_out else "JOB_PROBE_EXITED",
            "exit_code": int(code.value), "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "job_memory_limit_bytes": MEMORY_BYTES,
            "memory_metric": "JobMemoryLimit_committed_bytes_job_total",
            "kill_on_job_close": True, "breakaway_permitted": False,
            "active_processes_after_timeout":
                int(accounting.ActiveProcesses) if timed_out else None,
            "filesystem_network_confined": False}
    finally:
        if created:
            if not associated:
                k.TerminateProcess(process.hProcess, 125)
            k.CloseHandle(process.hThread)
            k.CloseHandle(process.hProcess)
        # KILL_ON_JOB_CLOSE covers children, including supervisor termination.
        k.CloseHandle(job)
