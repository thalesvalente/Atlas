"""Linux native OS confinement, test-only. No real source acquisition."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import platform
import resource
import signal
import stat
import sys

BUDGET_BYTES = 256 * 1024 * 1024
PR_SET_PDEATHSIG = 1
PR_SET_NO_NEW_PRIVS = 38
PR_SET_SECCOMP = 22
SECCOMP_MODE_FILTER = 2
LANDLOCK_CREATE_RULESET_VERSION = 1
LANDLOCK_RULE_PATH_BENEATH = 1
LL_EXECUTE = 1 << 0
LL_READ_FILE = 1 << 2
LL_TRUNCATE = 1 << 14
LL_IOCTL_DEV = 1 << 15
LL_V3_RIGHTS = (LL_TRUNCATE << 1) - 1


class IsolationUnavailable(RuntimeError):
    """Stable, non-sensitive OS enforcement error."""


class _Ruleset(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class _Beneath(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64),
                ("parent_fd", ctypes.c_int32)]


class _Filter(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort), ("jt", ctypes.c_ubyte),
                ("jf", ctypes.c_ubyte), ("k", ctypes.c_uint32)]


class _Program(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ushort),
                ("filters", ctypes.POINTER(_Filter))]


def _checked(ok: bool, error: str) -> None:
    if not ok:
        raise IsolationUnavailable(error)


def _seccomp(libc: ctypes.CDLL) -> None:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        arch = 0xC000003E
        forbidden = (41, 42, 43, 44, 49, 50, 53, 54, 55, 56, 57, 58,
                     59, 101, 272, 299, 308, 321, 322, 425, 435)
    elif machine in ("aarch64", "arm64"):
        arch = 0xC00000B7
        forbidden = (198, 200, 201, 202, 203, 206, 208, 210, 211,
                     212, 220, 221, 117, 268, 270, 277, 280, 425, 435)
    else:
        raise IsolationUnavailable("SECCOMP_ARCH_UNSUPPORTED")
    deny = 0x00050000 | 1
    ins = [
        _Filter(0x20, 0, 0, 4),
        _Filter(0x15, 1, 0, arch),
        _Filter(0x06, 0, 0, 0x80000000),  # BPF_RET | SECCOMP_RET_KILL_PROCESS
        _Filter(0x20, 0, 0, 0),
    ]
    if arch == 0xC000003E:
        ins += [_Filter(0x35, 0, 1, 0x40000000),
                _Filter(0x06, 0, 0, deny)]
    for syscall_no in forbidden:
        ins += [_Filter(0x15, 0, 1, syscall_no),
                _Filter(0x06, 0, 0, deny)]
    ins += [_Filter(0x06, 0, 0, 0x7FFF0000)]
    storage = (_Filter * len(ins))(*ins)
    program = _Program(len(ins), storage)
    _checked(libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER,
                        ctypes.byref(program), 0, 0) == 0,
             "SECCOMP_UNAVAILABLE")


def _landlock(libc: ctypes.CDLL, source: Path, scratch: Path) -> int:
    if not hasattr(os, "O_PATH"):
        raise IsolationUnavailable("LANDLOCK_O_PATH_UNAVAILABLE")
    syscall = libc.syscall
    syscall.restype = ctypes.c_long
    # Linux generic syscall numbers, x86_64 and aarch64.
    abi = syscall(444, None, 0, LANDLOCK_CREATE_RULESET_VERSION)
    _checked(abi >= 3, "LANDLOCK_ABI_LT_3_OR_UNAVAILABLE")
    handled = LL_V3_RIGHTS | (LL_IOCTL_DEV if abi >= 5 else 0)
    rules = _Ruleset(handled)
    rulesfd = syscall(444, ctypes.byref(rules), ctypes.sizeof(rules), 0)
    _checked(rulesfd >= 0, "LANDLOCK_CREATE_FAILED")
    try:
        for path, allowed in ((source, LL_READ_FILE),
                              (scratch, handled & ~LL_EXECUTE)):
            fd = os.open(path, os.O_PATH | os.O_CLOEXEC | os.O_NOFOLLOW)
            try:
                evidence = os.fstat(fd)
                if path == source:
                    _checked(stat.S_ISREG(evidence.st_mode) and
                             evidence.st_nlink == 1, "UNSAFE_SOURCE_RACE")
                attr = _Beneath(allowed, fd)
                _checked(syscall(445, rulesfd, LANDLOCK_RULE_PATH_BENEATH,
                                 ctypes.byref(attr), 0) == 0,
                         "LANDLOCK_RULE_FAILED")
            finally:
                os.close(fd)
        _checked(syscall(446, rulesfd, 0) == 0, "LANDLOCK_RESTRICT_FAILED")
    finally:
        os.close(rulesfd)
    return int(abi)


def enforce(source: Path, scratch: Path, *, supervisor_pid: int) -> dict:
    """Restrict self and descendants BEFORE opening source bytes."""
    if sys.platform != "linux" or platform.machine().lower() not in (
            "x86_64", "amd64", "aarch64", "arm64"):
        raise IsolationUnavailable("LINUX_PLATFORM_UNSUPPORTED")
    _checked(source.is_absolute() and scratch.is_absolute(),
             "PATH_NOT_ABSOLUTE")
    _checked(not source.is_symlink() and not scratch.is_symlink(),
             "UNSAFE_SYMLINK")
    src, out = source.lstat(), scratch.lstat()
    _checked(stat.S_ISREG(src.st_mode) and src.st_nlink == 1,
             "UNSAFE_SOURCE")
    _checked(stat.S_ISDIR(out.st_mode) and out.st_uid == os.getuid()
             and stat.S_IMODE(out.st_mode) == 0o700, "UNSAFE_SCRATCH")
    _checked(scratch != source.parent and source.parent not in scratch.parents
             and scratch not in source.parents, "UNSAFE_SCRATCH_LOCATION")
    libc = ctypes.CDLL(None, use_errno=True)
    _checked(libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL, 0, 0, 0) == 0,
             "PARENT_DEATH_GUARD_FAILED")
    _checked(os.getppid() == supervisor_pid, "SUPERVISOR_LOST")
    _checked(libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == 0,
             "NO_NEW_PRIVS_FAILED")
    # Linux address space: VAS, not RSS; no process creation allowed.
    # Prevent core-dump copies of a synthetic or future private payload.
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    _checked(resource.getrlimit(resource.RLIMIT_CORE) == (0, 0),
             "CORE_DUMP_LIMIT_FAILED")
    os.umask(0o077)
    resource.setrlimit(resource.RLIMIT_AS, (BUDGET_BYTES, BUDGET_BYTES))
    _checked(resource.getrlimit(resource.RLIMIT_AS) ==
             (BUDGET_BYTES, BUDGET_BYTES), "ADDRESS_SPACE_LIMIT_FAILED")
    abi = _landlock(libc, source, scratch)
    _seccomp(libc)
    return {"landlock_abi": abi,
            "memory_metric": "RLIMIT_AS_virtual_address_space",
            "memory_limit_bytes": BUDGET_BYTES,
            "network": "seccomp_socket_denied",
            "descendants": "seccomp_fork_clone_exec_denied"}
