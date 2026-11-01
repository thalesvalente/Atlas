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
from pathlib import Path

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
                      inject_assign_failure: bool = False,
                      appcontainer: bool = False) -> dict:
    """CREATE_SUSPENDED -> set/query Job -> assign -> resume -> monotonic kill."""
    if sys.platform != "win32":
        raise NativeJobUnavailable("WINDOWS_ONLY")
    if not 0 < wall_seconds <= WALL_SECONDS:
        raise NativeJobUnavailable("UNSAFE_WALL_LIMIT")
    # Not a general-purpose Job-as-sandbox launcher: fixed, reviewed worker only.
    from pathlib import Path
    expected = Path(__file__).with_name("os_worker.py").resolve(strict=True)
    if argv[1:3] == ["-I", "-S"]:
        worker_index = 3
    elif argv[1:4] == ["-I", "-O", "-S"]:
        worker_index = 4
    else:
        worker_index = -1
    if (worker_index < 0 or len(argv) <= worker_index or
            Path(argv[0]).resolve() != Path(sys.executable).resolve() or
            Path(argv[worker_index]).resolve() != expected):
        raise NativeJobUnavailable("UNTRUSTED_WORKER_REJECTED")
    # Validate every operand, not only the interpreter and module.
    flags = argv[worker_index + 1:]
    expected_flags = ["--source", "--outside", "--scratch", "--mode",
                      "--supervisor-pid"]
    if len(flags) != 10 or flags[::2] != expected_flags:
        raise NativeJobUnavailable("WORKER_ARGUMENTS_UNTRUSTED")
    try:
        import os
        from .os_supervisor import _preflight, _OPERATIONS
        src, outside, scratch = [Path(flags[i]) for i in (1, 3, 5)]
        if flags[7] not in _OPERATIONS or int(flags[9]) != os.getpid():
            raise NativeJobUnavailable("WORKER_ARGUMENTS_UNTRUSTED")
        _preflight(src, outside, scratch)
        if not scratch.parent.parent.name.startswith("atlas-c2b-"):
            raise NativeJobUnavailable("WORKER_ARGUMENTS_UNTRUSTED")
    except NativeJobUnavailable:
        raise
    except Exception:
        raise NativeJobUnavailable("WORKER_ARGUMENTS_UNTRUSTED") from None
    flags_args = flags
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
    profile = None
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
        if appcontainer:
            profile = _AppContainerLaunch(Path(flags_args[1]), Path(flags_args[5]))
            profile.prepare()
        si = profile.startup if profile else _Startup()
        if not profile:
            si.cb = ctypes.sizeof(si)
        process_argv = list(argv)
        executable = argv[0]
        cwd = None
        if profile:
            executable = profile.launch_exe
            process_argv[0] = executable
            process_argv[worker_index] = profile.launch_worker
            process_argv += profile.argv_suffix
            cwd = profile.launch_cwd
        line = ctypes.create_unicode_buffer(subprocess.list2cmdline(process_argv))
        creation = CREATE_SUSPENDED | CREATE_NO_WINDOW
        if profile:
            creation |= 0x00080000  # EXTENDED_STARTUPINFO_PRESENT
        startup_pointer = ctypes.cast(ctypes.byref(si), ctypes.POINTER(_Startup))
        if not k.CreateProcessW(executable, line, None, None, bool(profile),
                                creation, None, cwd, startup_pointer,
                                ctypes.byref(process)):
            raise NativeJobUnavailable("JOB_CREATE_SUSPENDED_FAILED")
        created = True
        if profile:
            profile.verify_child(process.hProcess)
        if inject_assign_failure:
            raise NativeJobUnavailable("JOB_ASSIGN_FAILED_INJECTED")
        if not k.AssignProcessToJobObject(job, process.hProcess):
            raise NativeJobUnavailable("JOB_ASSIGN_FAILED")
        associated = True
        # Time budget starts at the worker's first runnable instant, not while
        # copying the disposable runtime or configuring the suspended token.
        started = time.monotonic()
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
                # A completion observed past the wall deadline is still expired.
                if time.monotonic() >= deadline:
                    timed_out = True
                    if not k.TerminateJobObject(job, 124):
                        raise NativeJobUnavailable("JOB_TERMINATION_FAILED")
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
            "filesystem_network_confined": False,
            "appcontainer_token_verified": bool(profile),
            "appcontainer_loopback_exception_absent":
                profile.loopback_no_exception if profile else None,
            "loopback_control_passed":
                profile.loopback_control_passed if profile else None,
            "loopback_worker_accepted":
                profile._loopback_worker_accepted() if profile else None}
    finally:
        if created:
            if not associated:
                k.TerminateProcess(process.hProcess, 125)
            k.CloseHandle(process.hThread)
            k.CloseHandle(process.hProcess)
        # KILL_ON_JOB_CLOSE covers children, including supervisor termination.
        k.CloseHandle(job)
        if profile:
            profile.close()


class _StartupEx(ctypes.Structure):
    _fields_ = [("StartupInfo", _Startup), ("lpAttributeList", ctypes.c_void_p)]


class _SecurityCapabilities(ctypes.Structure):
    _fields_ = [("AppContainerSid", ctypes.c_void_p),
                ("Capabilities", ctypes.c_void_p),
                ("CapabilityCount", wintypes.DWORD),
                ("Reserved", wintypes.DWORD)]


class _InheritAttributes(ctypes.Structure):
    _fields_ = [("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", ctypes.c_void_p),
                ("bInheritHandle", wintypes.BOOL)]

class _SidAndAttributes(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wintypes.DWORD)]


class _AppContainerLaunch:
    """Ephemeral profile and exactly two inherited file capabilities.

    Not a production file broker. Operates only on the already-created
    invented fixture. No ACLs, accounts, firewall or global policies changed.
    """
    def __init__(self, source, scratch):
        self.source = source
        self.scratch = scratch
        self.profile_name = None
        self.sid = ctypes.c_void_p()
        self.handles = []
        self.attributes = None
        self.attr_buf = None
        self.startup = _StartupEx()
        self.argv_suffix = []
        self.listener = None
        self._initialized = False
        self.loopback_no_exception = False
        self.loopback_control_passed = False

    def _verify_network_policy(self):
        """Read-only native WFP AppContainer exception inventory.

        If its SID has an exemption or the inventory cannot be verified,
        fail closed. No firewall/host policy is ever modified.
        """
        firewall = ctypes.WinDLL("FirewallAPI", use_last_error=True)
        firewall.NetworkIsolationGetAppContainerConfig.argtypes = [
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(ctypes.POINTER(_SidAndAttributes))]
        firewall.NetworkIsolationGetAppContainerConfig.restype = wintypes.DWORD
        adv = ctypes.WinDLL("advapi32", use_last_error=True)
        adv.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        adv.EqualSid.restype = wintypes.BOOL
        self.kernel.GetProcessHeap.restype = wintypes.HANDLE
        self.kernel.HeapFree.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p]
        self.kernel.HeapFree.restype = wintypes.BOOL
        count = wintypes.DWORD()
        entries = ctypes.POINTER(_SidAndAttributes)()
        if firewall.NetworkIsolationGetAppContainerConfig(
                ctypes.byref(count), ctypes.byref(entries)) != 0:
            raise NativeJobUnavailable("APPCONTAINER_LOOPBACK_POLICY_UNVERIFIED")
        try:
            if count.value > 10000 or (count.value and not entries):
                raise NativeJobUnavailable("APPCONTAINER_LOOPBACK_POLICY_UNVERIFIED")
            for index in range(count.value):
                sid = entries[index].Sid
                if sid and adv.EqualSid(self.sid, sid):
                    raise NativeJobUnavailable("APPCONTAINER_LOOPBACK_EXEMPT")
            self.loopback_no_exception = True
        finally:
            if entries:
                heap = self.kernel.GetProcessHeap()
                for index in range(min(count.value, 10000)):
                    if entries[index].Sid:
                        self.kernel.HeapFree(heap, 0, entries[index].Sid)
                self.kernel.HeapFree(heap, 0, ctypes.cast(entries, ctypes.c_void_p))

    def _verify_listener_positive_control(self):
        import socket
        self.listener.settimeout(3)
        with socket.create_connection(self.listener.getsockname(), timeout=3):
            peer, _ = self.listener.accept()
            peer.close()
        self.listener.settimeout(0.15)
        self.loopback_control_passed = True

    def _loopback_worker_accepted(self):
        import socket
        try:
            peer, _ = self.listener.accept()
        except socket.timeout:
            return False
        else:
            peer.close()
            return True

    def _stage_python_runtime(self):
        """Copy only installed public Python runtime into this disposable fixture.

        AppContainer must not be granted permissions on the runner's Python
        installation or repository. ACLs apply only to new test-owned files.
        """
        import shutil
        import subprocess
        base = Path(sys.base_prefix)
        runtime = self.scratch.parent / "runtime"
        runtime.mkdir(mode=0o700)
        if not (base / "python.exe").is_file() or not (base / "Lib").is_dir():
            raise NativeJobUnavailable("BROKER_RUNTIME_SOURCE_MISSING")
        adv = ctypes.WinDLL("advapi32", use_last_error=True)
        adv.ConvertSidToStringSidW.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
        adv.ConvertSidToStringSidW.restype = wintypes.BOOL
        sid_text = wintypes.LPWSTR()
        if not adv.ConvertSidToStringSidW(self.sid, ctypes.byref(sid_text)):
            raise NativeJobUnavailable("BROKER_RUNTIME_SID_UNVERIFIED")
        try:
            sid_string = sid_text.value
        finally:
            self.kernel.LocalFree(ctypes.cast(sid_text, ctypes.c_void_p))
        # The package gets read+execute ONLY on the disposable runtime.
        grant = subprocess.run(
            ["icacls", str(runtime), "/grant",
             "*" + sid_string + ":(OI)(CI)(RX)"],
            capture_output=True, text=True, timeout=20)
        if grant.returncode:
            raise NativeJobUnavailable("BROKER_RUNTIME_ACL_GRANT_FAILED")
        for name in ("python.exe", "python3.dll", "python312.dll",
                     "vcruntime140.dll", "vcruntime140_1.dll"):
            if (base / name).is_file():
                shutil.copy2(base / name, runtime / name)
        if not (runtime / "python312.dll").is_file():
            raise NativeJobUnavailable("BROKER_RUNTIME_PYTHON_DLL_MISSING")
        shutil.copytree(
            base / "Lib", runtime / "Lib",
            ignore=shutil.ignore_patterns("site-packages", "__pycache__"))
        if (base / "DLLs").is_dir():
            shutil.copytree(base / "DLLs", runtime / "DLLs")
        shutil.copy2(Path(__file__).with_name("os_worker.py"),
                     runtime / "os_worker.py")
        self.launch_exe = str(runtime / "python.exe")
        self.launch_worker = str(runtime / "os_worker.py")
        self.launch_cwd = str(runtime)

    def prepare(self):
        import secrets
        import socket
        from .os_supervisor import _INVENTED_SOURCE, _preflight
        from .os_windows_acl import verify_private_child
        _preflight(self.source, self.scratch.parent / "input" / "os-outside.json",
                   self.scratch)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        userenv = ctypes.WinDLL("userenv", use_last_error=True)
        self.kernel = kernel
        self.userenv = userenv
        userenv.CreateAppContainerProfile.argtypes = [
            wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
            ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
        userenv.CreateAppContainerProfile.restype = ctypes.c_long
        userenv.DeleteAppContainerProfile.argtypes = [wintypes.LPCWSTR]
        userenv.DeleteAppContainerProfile.restype = ctypes.c_long
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree.restype = ctypes.c_void_p
        kernel.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.POINTER(_InheritAttributes), wintypes.DWORD,
            wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.ReadFile.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        kernel.ReadFile.restype = wintypes.BOOL
        kernel.SetFilePointerEx.argtypes = [
            wintypes.HANDLE, ctypes.c_int64, ctypes.c_void_p, wintypes.DWORD]
        kernel.SetFilePointerEx.restype = wintypes.BOOL
        kernel.InitializeProcThreadAttributeList.argtypes = [
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
            ctypes.POINTER(ctypes.c_size_t)]
        kernel.InitializeProcThreadAttributeList.restype = wintypes.BOOL
        kernel.UpdateProcThreadAttribute.argtypes = [
            ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t,
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
        kernel.UpdateProcThreadAttribute.restype = wintypes.BOOL
        kernel.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
        kernel.DeleteProcThreadAttributeList.restype = None
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        self.profile_name = "AtlasC2BSynthetic" + secrets.token_hex(12)
        if userenv.CreateAppContainerProfile(
                self.profile_name, "Atlas C2-B synthetic", "Disposable CI fixture",
                None, 0, ctypes.byref(self.sid)) != 0 or not self.sid.value:
            self.profile_name = None
            raise NativeJobUnavailable("APPCONTAINER_PROFILE_CREATE_FAILED")
        self._verify_network_policy()
        self._stage_python_runtime()
        # Open source with no FILE_SHARE_WRITE/DELETE; keep it pinned through
        # worker termination. FILE_FLAG_OPEN_REPARSE_POINT rejects link races.
        attrs = _InheritAttributes(ctypes.sizeof(_InheritAttributes), None, True)
        invalid = ctypes.c_void_p(-1).value
        src = kernel.CreateFileW(str(self.source), 0x80000000, 1,
                                 ctypes.byref(attrs), 3, 0x00200000, None)
        if src in (None, invalid):
            raise NativeJobUnavailable("BROKER_SOURCE_OPEN_FAILED")
        self.handles.append(src)
        buf = ctypes.create_string_buffer(len(_INVENTED_SOURCE) + 1)
        count = wintypes.DWORD()
        if not kernel.ReadFile(src, buf, len(buf), ctypes.byref(count), None):
            raise NativeJobUnavailable("BROKER_SOURCE_VERIFY_FAILED")
        if bytes(buf.raw[:count.value]) != _INVENTED_SOURCE:
            raise NativeJobUnavailable("BROKER_SOURCE_NOT_INVENTED")
        if not kernel.SetFilePointerEx(src, 0, None, 0):
            raise NativeJobUnavailable("BROKER_SOURCE_REWIND_FAILED")
        # The worker gets a WRITE-only handle. It cannot name/open a new
        # output outside scratch, and cannot overwrite a prior receipt.
        report = self.scratch / "os-probe-report.json"
        out = kernel.CreateFileW(str(report), 0x40000000, 1,
                                 ctypes.byref(attrs), 1, 0x00000080, None)
        if out in (None, invalid):
            raise NativeJobUnavailable("BROKER_REPORT_CREATE_FAILED")
        self.handles.append(out)
        from .os_windows_acl import WindowsScratchUnverified
        try:
            verify_private_child(self.scratch, report)
        except WindowsScratchUnverified:
            raise NativeJobUnavailable("BROKER_REPORT_ACL_UNVERIFIED") from None
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        self._verify_listener_positive_control()
        self.argv_suffix = ["--broker-source-handle", str(int(src)),
                            "--broker-report-handle", str(int(out)),
                            "--broker-loopback-port",
                            str(self.listener.getsockname()[1])]
        sizes = ctypes.c_size_t()
        kernel.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(sizes))
        if not sizes.value:
            raise NativeJobUnavailable("APPCONTAINER_ATTRIBUTES_UNAVAILABLE")
        self.attr_buf = ctypes.create_string_buffer(sizes.value)
        self.attributes = ctypes.cast(self.attr_buf, ctypes.c_void_p)
        if not kernel.InitializeProcThreadAttributeList(
                self.attributes, 2, 0, ctypes.byref(sizes)):
            raise NativeJobUnavailable("APPCONTAINER_ATTRIBUTES_INIT_FAILED")
        self._initialized = True
        caps = _SecurityCapabilities(self.sid, None, 0, 0)
        self._caps = caps  # pointer must outlive CreateProcessW
        self._handle_array = (wintypes.HANDLE * 2)(*self.handles)
        if not kernel.UpdateProcThreadAttribute(
                self.attributes, 0, 0x00020009, ctypes.byref(caps),
                ctypes.sizeof(caps), None, None):
            raise NativeJobUnavailable("APPCONTAINER_CAPABILITIES_FAILED")
        if not kernel.UpdateProcThreadAttribute(
                self.attributes, 0, 0x00020002,
                ctypes.byref(self._handle_array), ctypes.sizeof(self._handle_array),
                None, None):
            raise NativeJobUnavailable("APPCONTAINER_HANDLE_LIST_FAILED")
        self.startup.StartupInfo.cb = ctypes.sizeof(_StartupEx)
        self.startup.lpAttributeList = self.attributes

    def verify_child(self, child):
        """Must verify actual suspended process token, not caller's flags."""
        adv = ctypes.WinDLL("advapi32", use_last_error=True)
        adv.OpenProcessToken.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
        adv.OpenProcessToken.restype = wintypes.BOOL
        adv.GetTokenInformation.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD)]
        adv.GetTokenInformation.restype = wintypes.BOOL
        adv.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        adv.EqualSid.restype = wintypes.BOOL
        token = wintypes.HANDLE()
        if not adv.OpenProcessToken(child, 0x0008, ctypes.byref(token)):
            raise NativeJobUnavailable("APPCONTAINER_CHILD_TOKEN_UNAVAILABLE")
        try:
            returned = wintypes.DWORD()
            is_app = wintypes.DWORD()
            if not adv.GetTokenInformation(token, 29, ctypes.byref(is_app),
                                            ctypes.sizeof(is_app), ctypes.byref(returned)
                                            ) or is_app.value != 1:
                raise NativeJobUnavailable("APPCONTAINER_CHILD_NOT_ISOLATED")
            buffer = ctypes.create_string_buffer(256)
            if not adv.GetTokenInformation(token, 31, buffer, len(buffer),
                                            ctypes.byref(returned)):
                raise NativeJobUnavailable("APPCONTAINER_CHILD_SID_UNVERIFIED")
            actual_sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
            if not actual_sid or not adv.EqualSid(actual_sid, self.sid):
                raise NativeJobUnavailable("APPCONTAINER_CHILD_SID_MISMATCH")
            if not adv.GetTokenInformation(token, 30, buffer, len(buffer),
                                            ctypes.byref(returned)):
                raise NativeJobUnavailable("APPCONTAINER_CAPABILITIES_UNVERIFIED")
            if ctypes.cast(buffer, ctypes.POINTER(wintypes.DWORD))[0] != 0:
                raise NativeJobUnavailable("APPCONTAINER_NETWORK_CAPABILITY_PRESENT")
        finally:
            self.kernel.CloseHandle(token)

    def close(self):
        if self._initialized:
            self.kernel.DeleteProcThreadAttributeList(self.attributes)
        if self.listener:
            self.listener.close()
        for handle in self.handles:
            self.kernel.CloseHandle(handle)
        if self.sid.value:
            self.kernel.LocalFree(self.sid)
        if self.profile_name:
            if self.userenv.DeleteAppContainerProfile(self.profile_name) != 0:
                raise NativeJobUnavailable("APPCONTAINER_PROFILE_CLEANUP_FAILED")
