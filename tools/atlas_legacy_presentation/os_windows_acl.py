"""Read-only Windows DACL/owner verification of a disposable synthetic scratch.

Never changes ACLs of sources, drives, users, or host policy.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import re
import sys


class WindowsScratchUnverified(RuntimeError):
    pass


def verify_private_scratch(path: Path) -> None:
    """Fail closed unless only current user, SYSTEM, or Administrators have allow ACEs."""
    if sys.platform != "win32":
        raise WindowsScratchUnverified("WINDOWS_ONLY")
    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    adv.OpenProcessToken.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    adv.OpenProcessToken.restype = wintypes.BOOL
    adv.GetTokenInformation.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD)]
    adv.GetTokenInformation.restype = wintypes.BOOL
    adv.ConvertSidToStringSidW.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    adv.ConvertSidToStringSidW.restype = wintypes.BOOL
    adv.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    adv.EqualSid.restype = wintypes.BOOL
    adv.GetNamedSecurityInfoW.argtypes = [
        wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p)]
    adv.GetNamedSecurityInfoW.restype = wintypes.DWORD
    adv.ConvertSecurityDescriptorToStringSecurityDescriptorW.argtypes = [
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(wintypes.LPWSTR), ctypes.c_void_p]
    adv.ConvertSecurityDescriptorToStringSecurityDescriptorW.restype = wintypes.BOOL

    token = wintypes.HANDLE()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008,
                                ctypes.byref(token)):
        raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
    try:
        needed = wintypes.DWORD()
        adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        if needed.value < ctypes.sizeof(ctypes.c_void_p):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        buf = ctypes.create_string_buffer(needed.value)
        if not adv.GetTokenInformation(token, 1, buf, needed,
                                       ctypes.byref(needed)):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        user_sid = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
        sid_string = wintypes.LPWSTR()
        if not adv.ConvertSidToStringSidW(user_sid, ctypes.byref(sid_string)):
            raise WindowsScratchUnverified("SCRATCH_SID_UNVERIFIED")
        try:
            username_sid = sid_string.value
        finally:
            kernel.LocalFree(ctypes.cast(sid_string, ctypes.c_void_p))
        owner = ctypes.c_void_p()
        dacl = ctypes.c_void_p()
        sd = ctypes.c_void_p()
        if adv.GetNamedSecurityInfoW(
                str(path), 1, 0x00000001 | 0x00000004,
                ctypes.byref(owner), None, ctypes.byref(dacl), None,
                ctypes.byref(sd)) != 0:
            raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
        try:
            if not owner.value or not dacl.value or not adv.EqualSid(
                    owner, user_sid):
                raise WindowsScratchUnverified("SCRATCH_OWNER_UNVERIFIED")
            sddl = wintypes.LPWSTR()
            if not adv.ConvertSecurityDescriptorToStringSecurityDescriptorW(
                    sd, 1, 0x00000004, ctypes.byref(sddl), None):
                raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
            try:
                descriptor = sddl.value or ""
            finally:
                kernel.LocalFree(ctypes.cast(sddl, ctypes.c_void_p))
            if "D:" not in descriptor:
                raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
            dacl_text = descriptor.split("D:", 1)[1].split("S:", 1)[0]
            entries = re.findall(r"\(([^()]*)\)", dacl_text)
            if not entries:
                raise WindowsScratchUnverified("SCRATCH_DACL_EMPTY")
            authorized = {"SY", "BA", username_sid.upper()}
            has_user_write = False
            for ace in entries:
                fields = ace.split(";")
                if len(fields) < 6:
                    raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
                ace_type, rights, sid = fields[0], fields[2], fields[5]
                if ace_type in ("A", "OA", "XA", "ZA"):
                    if ace_type != "A" or sid.upper() not in authorized:
                        raise WindowsScratchUnverified("SCRATCH_ACL_TOO_BROAD")
                    if sid.upper() == username_sid.upper() and (
                            "FA" in rights or "FW" in rights or
                            rights.startswith("0x")):
                        has_user_write = True
                elif ace_type != "D":
                    raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
            if not has_user_write:
                raise WindowsScratchUnverified("SCRATCH_USER_WRITE_UNVERIFIED")
        finally:
            if sd.value:
                kernel.LocalFree(sd)
    finally:
        kernel.CloseHandle(token)
