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


class _ACL(ctypes.Structure):
    _fields_ = [("revision", ctypes.c_ubyte),
                ("reserved", ctypes.c_ubyte),
                ("size", ctypes.c_uint16),
                ("ace_count", ctypes.c_uint16),
                ("reserved2", ctypes.c_uint16)]


class _AceHeader(ctypes.Structure):
    _fields_ = [("ace_type", ctypes.c_ubyte),
                ("ace_flags", ctypes.c_ubyte),
                ("ace_size", ctypes.c_uint16)]


def verify_private_scratch(path: Path) -> None:
    """Verify exact token-owner and DACL ACE SIDs by Win32 binary APIs.

    SDDL rendering is not authoritative: Windows may serialize well-known
    principals as abbreviations or numeric SIDs. Compare kernel SIDs instead.
    """
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
    adv.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    adv.EqualSid.restype = wintypes.BOOL
    adv.IsValidSid.argtypes = [ctypes.c_void_p]
    adv.IsValidSid.restype = wintypes.BOOL
    adv.ConvertStringSidToSidW.argtypes = [
        wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_void_p)]
    adv.ConvertStringSidToSidW.restype = wintypes.BOOL
    adv.GetAce.argtypes = [
        ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    adv.GetAce.restype = wintypes.BOOL
    adv.GetNamedSecurityInfoW.argtypes = [
        wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p)]
    adv.GetNamedSecurityInfoW.restype = wintypes.DWORD
    adv.GetSecurityDescriptorControl.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(wintypes.WORD),
        ctypes.POINTER(wintypes.DWORD)]
    adv.GetSecurityDescriptorControl.restype = wintypes.BOOL

    token = wintypes.HANDLE()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008,
                                ctypes.byref(token)):
        raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
    try:
        required = wintypes.DWORD()
        adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(required))
        if required.value < ctypes.sizeof(ctypes.c_void_p):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        token_buf = ctypes.create_string_buffer(required.value)
        if not adv.GetTokenInformation(token, 1, token_buf, required,
                                       ctypes.byref(required)):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        user = ctypes.cast(token_buf, ctypes.POINTER(ctypes.c_void_p))[0]
        owner = ctypes.c_void_p()
        dacl = ctypes.c_void_p()
        sd = ctypes.c_void_p()
        if adv.GetNamedSecurityInfoW(
                str(path), 1, 0x00000001 | 0x00000004,
                ctypes.byref(owner), None, ctypes.byref(dacl), None,
                ctypes.byref(sd)) != 0:
            raise WindowsScratchUnverified("SCRATCH_DACL_UNVERIFIED")
        try:
            if not owner.value or not dacl.value or not adv.EqualSid(owner, user):
                raise WindowsScratchUnverified("SCRATCH_OWNER_UNVERIFIED")
            control = wintypes.WORD()
            revision = wintypes.DWORD()
            if not adv.GetSecurityDescriptorControl(
                    sd, ctypes.byref(control), ctypes.byref(revision)):
                raise WindowsScratchUnverified("SCRATCH_CONTROL_UNVERIFIED")
            if not (control.value & 0x1000):  # SE_DACL_PROTECTED
                raise WindowsScratchUnverified("SCRATCH_DACL_NOT_PROTECTED")
            acl = ctypes.cast(dacl, ctypes.POINTER(_ACL)).contents
            if acl.ace_count < 1 or acl.ace_count > 8:
                raise WindowsScratchUnverified("SCRATCH_ACE_COUNT_UNVERIFIED")
            system_sid = ctypes.c_void_p()
            admin_sid = ctypes.c_void_p()
            if (not adv.ConvertStringSidToSidW("S-1-5-18",
                                               ctypes.byref(system_sid)) or
                    not adv.ConvertStringSidToSidW("S-1-5-32-544",
                                                   ctypes.byref(admin_sid))):
                raise WindowsScratchUnverified("SCRATCH_BUILTIN_SIDS_UNVERIFIED")
            try:
                has_user_write = False
                for idx in range(acl.ace_count):
                    ace = ctypes.c_void_p()
                    if not adv.GetAce(dacl, idx, ctypes.byref(ace)) or not ace.value:
                        raise WindowsScratchUnverified("SCRATCH_ACE_UNVERIFIED")
                    header = ctypes.cast(ace, ctypes.POINTER(_AceHeader)).contents
                    if (header.ace_type != 0 or header.ace_flags & 0x10
                            or header.ace_size < 12):
                        raise WindowsScratchUnverified("SCRATCH_ACE_UNSAFE")
                    # ACCESS_ALLOWED_ACE = ACE_HEADER(4) + AccessMask(4)
                    # + SidStart. Sid pointer refers to the SID at +8.
                    trustee = ctypes.c_void_p(ace.value + 8)
                    if not adv.IsValidSid(trustee):
                        raise WindowsScratchUnverified("SCRATCH_ACE_INVALID_SID")
                    is_user = bool(adv.EqualSid(trustee, user))
                    if not (is_user or adv.EqualSid(trustee, system_sid)
                            or adv.EqualSid(trustee, admin_sid)):
                        raise WindowsScratchUnverified("SCRATCH_ACL_TOO_BROAD")
                    # FILE_ADD_FILE (0x2) / GENERIC_ALL (0x10000000)
                    # / FILE_ALL_ACCESS (0x001f01ff)
                    mask = ctypes.c_uint32.from_address(ace.value + 4).value
                    if is_user and (mask & 0x2 or mask & 0x10000000):
                        has_user_write = True
                if not has_user_write:
                    raise WindowsScratchUnverified("SCRATCH_USER_WRITE_UNVERIFIED")
            finally:
                if system_sid.value:
                    kernel.LocalFree(system_sid)
                if admin_sid.value:
                    kernel.LocalFree(admin_sid)
        finally:
            if sd.value:
                kernel.LocalFree(sd)
    finally:
        kernel.CloseHandle(token)


class _SecurityAttributes(ctypes.Structure):
    _fields_ = [("nLength", wintypes.DWORD),
                ("lpSecurityDescriptor", ctypes.c_void_p),
                ("bInheritHandle", wintypes.BOOL)]


def create_private_scratch(path: Path) -> None:
    """Create one NEW test-owned scratch using an explicitly protected DACL.

    This changes neither inherited directories nor any source ACL.
    """
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
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(wintypes.DWORD)]
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = wintypes.BOOL
    kernel.CreateDirectoryW.argtypes = [
        wintypes.LPCWSTR, ctypes.POINTER(_SecurityAttributes)]
    kernel.CreateDirectoryW.restype = wintypes.BOOL
    token = wintypes.HANDLE()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008,
                                ctypes.byref(token)):
        raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
    try:
        needed = wintypes.DWORD()
        adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        if needed.value < ctypes.sizeof(ctypes.c_void_p):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        buffer = ctypes.create_string_buffer(needed.value)
        if not adv.GetTokenInformation(token, 1, buffer, needed,
                                       ctypes.byref(needed)):
            raise WindowsScratchUnverified("SCRATCH_TOKEN_UNVERIFIED")
        user_sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
        sid_text = wintypes.LPWSTR()
        if not adv.ConvertSidToStringSidW(user_sid, ctypes.byref(sid_text)):
            raise WindowsScratchUnverified("SCRATCH_SID_UNVERIFIED")
        try:
            sid_string = sid_text.value
        finally:
            kernel.LocalFree(ctypes.cast(sid_text, ctypes.c_void_p))
    finally:
        kernel.CloseHandle(token)
    # Protected DACL: exactly current token owner and SYSTEM; no broad ACEs.
    # Elevated CI runners may default newly created owners to Administrators.
    # Explicit owner is our current token user SID; no global security changes.
    sddl = f"O:{sid_string}D:P(A;;FA;;;SY)(A;;FA;;;{sid_string})"
    descriptor = ctypes.c_void_p()
    if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            sddl, 1, ctypes.byref(descriptor), None):
        raise WindowsScratchUnverified("SCRATCH_DESCRIPTOR_BUILD_FAILED")
    try:
        attrs = _SecurityAttributes(ctypes.sizeof(_SecurityAttributes),
                                    descriptor, False)
        if not kernel.CreateDirectoryW(str(path), ctypes.byref(attrs)):
            raise WindowsScratchUnverified("SCRATCH_PRIVATE_CREATE_FAILED")
    finally:
        kernel.LocalFree(descriptor)
    verify_private_scratch(path)
