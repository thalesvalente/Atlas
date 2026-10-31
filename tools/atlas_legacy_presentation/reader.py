"""Exact-file acquisition for invented fixtures only, never host qualification.

The default operational entry point fails BEFORE inspecting paths. The explicit
synthetic_fixture flag is a test facility, not an isolation/security guarantee.
No provider, network, source rewrite, recursive discovery or cleanup is provided.
"""
from __future__ import annotations
import ctypes
from datetime import datetime, timedelta, timezone
import hashlib
from functools import wraps
import json
import os
from pathlib import Path
import stat
import tempfile
import time
import unicodedata
import uuid
from .errors import ReaderError
from .parser import parse_source, transform, MAX_SOURCE_BYTES, MAX_DESCRIPTOR_BYTES
from .semantics import validate_descriptor

_PRIVATE = {}
_OWNED = {}
MAX_ALLOWLIST = 3
REPOSITORY = Path(__file__).resolve().parents[2]


def _fail(code):
    raise ReaderError(code)


def _fingerprint(st):
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_nlink


def _lexical(path):
    raw = os.fspath(path)
    if not isinstance(raw, str) or not raw or unicodedata.normalize('NFC', raw) != raw:
        _fail('UNSAFE_PATH')
    normalized = raw.replace('\\', '/')
    if normalized.startswith('//') or any(c in raw for c in '*?%') or '\x00' in raw:
        _fail('UNSAFE_PATH')
    if any(x in ('.', '..') for x in normalized.split('/')):
        _fail('UNSAFE_PATH')
    value = Path(raw)
    if not value.is_absolute() or ':' in normalized[2:]:
        _fail('UNSAFE_PATH')
    return value


def _chain(path, *, regular=False):
    path = _lexical(path)
    proof = []
    for part in list(reversed(path.parents)) + [path]:
        st = part.lstat()
        if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
            _fail('UNSAFE_PATH')
        proof.append((part, st.st_dev, st.st_ino))
    st = path.lstat()
    if regular and (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1):
        _fail('UNSAFE_PATH')
    if not regular and not stat.S_ISDIR(st.st_mode):
        _fail('UNSAFE_PATH')
    if path.resolve(strict=True) != path:
        _fail('UNSAFE_PATH')
    return proof


def _verify_chain(proof):
    for part, dev, ino in proof:
        st = part.lstat()
        if (st.st_dev, st.st_ino) != (dev, ino) or stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
            _fail('SOURCE_CHANGED')


def _windows_private_mkdir(path):
    # Explicit protected DACL: current token user and SYSTEM only.
    from ctypes import wintypes
    advapi = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    token = wintypes.HANDLE()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008, ctypes.byref(token)):
        _fail('SCRATCH_UNVERIFIED')
    sid_text = wintypes.LPWSTR()
    descriptor = ctypes.c_void_p()
    try:
        needed = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        buffer = ctypes.create_string_buffer(needed.value)
        if not advapi.GetTokenInformation(token, 1, buffer, needed, ctypes.byref(needed)):
            _fail('SCRATCH_UNVERIFIED')
        sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
        if not advapi.ConvertSidToStringSidW(sid, ctypes.byref(sid_text)):
            _fail('SCRATCH_UNVERIFIED')
        sddl = 'D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;' + sid_text.value + ')'
        if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None):
            _fail('SCRATCH_UNVERIFIED')
        class SecurityAttributes(ctypes.Structure):
            _fields_ = [('length', wintypes.DWORD), ('descriptor', ctypes.c_void_p), ('inherit', wintypes.BOOL)]
        attributes = SecurityAttributes(ctypes.sizeof(SecurityAttributes), descriptor, False)
        kernel.CreateDirectoryW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(SecurityAttributes)]
        if not kernel.CreateDirectoryW(str(path), ctypes.byref(attributes)):
            _fail('SCRATCH_UNVERIFIED')
    finally:
        if descriptor:
            kernel.LocalFree(descriptor)
        if sid_text:
            kernel.LocalFree(ctypes.cast(sid_text, ctypes.c_void_p))
        kernel.CloseHandle(token)


def _io_errors(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except OSError:
            _fail('IO_UNVERIFIED')
    return guarded


@_io_errors
def private_scratch(parent):
    """Create one private child of an explicitly supplied, separate parent.

    A same-process receipt is required for writes. No existing directory is
    adopted and no ACL on a preexisting directory is changed.
    """
    parent = _lexical(parent)
    _chain(parent)
    if parent == REPOSITORY or REPOSITORY in parent.parents:
        _fail('SCRATCH_UNVERIFIED')
    directory = parent / ('atlas-c2-synthetic-' + uuid.uuid4().hex)
    if os.name == 'nt':
        _windows_private_mkdir(directory)
    else:
        directory.mkdir(mode=0o700)
    st = directory.lstat()
    if os.name != 'nt' and (stat.S_IMODE(st.st_mode) != 0o700 or st.st_uid != os.getuid()):
        _fail('SCRATCH_UNVERIFIED')
    _PRIVATE[str(directory)] = (st.st_dev, st.st_ino)
    return directory


def _scratch(path, source):
    path = _lexical(path)
    _chain(path)
    st = path.lstat()
    if _PRIVATE.get(str(path)) != (st.st_dev, st.st_ino):
        _fail('SCRATCH_UNVERIFIED')
    if source.parent == path or source.parent in path.parents or path in source.parents:
        _fail('UNSAFE_PATH')
    if path == REPOSITORY or REPOSITORY in path.parents:
        _fail('SCRATCH_UNVERIFIED')
    if os.name != 'nt' and (stat.S_IMODE(st.st_mode) != 0o700 or st.st_uid != os.getuid()):
        _fail('SCRATCH_UNVERIFIED')
    return path


def _open_read(source, flags, *, create=False):
    if os.name != 'nt':
        return os.open(source, flags)
    from ctypes import wintypes
    import msvcrt
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateFileW(str(source), 0xC0000000 if create else 0x80000000, 7, None, 1 if create else 3, 0x80 if create else 0x00200000 | 0x08000000, None)
    if handle == wintypes.HANDLE(-1).value:
        _fail('IO_UNVERIFIED')
    try:
        return msvcrt.open_osfhandle(handle, (os.O_RDWR if create else os.O_RDONLY) | os.O_BINARY)
    except OSError:
        kernel.CloseHandle(handle)
        _fail('IO_UNVERIFIED')


def _source_stamp(fd, *, single_link=True):
    if os.name != 'nt':
        return _fingerprint(os.fstat(fd))
    # Use the same Win32 metadata API for both held and re-opened handles.
    # Python path stat/fstat may differ in timestamp representation on Windows.
    from ctypes import wintypes
    import msvcrt
    class FileInformation(ctypes.Structure):
        _fields_ = [('attributes', wintypes.DWORD), ('created', wintypes.FILETIME), ('accessed', wintypes.FILETIME), ('written', wintypes.FILETIME), ('volume', wintypes.DWORD), ('size_hi', wintypes.DWORD), ('size_lo', wintypes.DWORD), ('links', wintypes.DWORD), ('index_hi', wintypes.DWORD), ('index_lo', wintypes.DWORD)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(FileInformation)]
    info = FileInformation()
    if not kernel.GetFileInformationByHandle(msvcrt.get_osfhandle(fd), ctypes.byref(info)):
        _fail('SOURCE_CHANGED')
    if info.attributes & 0x400 or (single_link and info.links != 1):
        _fail('UNSAFE_PATH')
    ticks = lambda value: (value.dwHighDateTime << 32) | value.dwLowDateTime
    return info.volume, (info.index_hi << 32) | info.index_lo, (info.size_hi << 32) | info.size_lo, ticks(info.written), ticks(info.created), info.links


def _path_stamp(path, flags, *, single_link=True):
    candidate = _open_read(path, flags)
    try:
        return _source_stamp(candidate, single_link=single_link)
    finally:
        os.close(candidate)


def _remove_partial(path, fd):
    # Never unlink a path whose identity no longer matches our still-open file.
    try:
        if _path_stamp(path, os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0), single_link=False) == _source_stamp(fd, single_link=False):
            path.unlink()
            return True
    except FileNotFoundError:
        return False
    return False


def _after_read(path):
    """Fault injection seam for synthetic counterproofs, not a CLI option."""


@_io_errors
def prepare(source, allowlist, scratch, *, ttl_seconds=3600, synthetic_fixture=False):
    """Produce one ephemeral descriptor only in explicit synthetic test mode.

    This process has no qualified OS network/filesystem/memory confinement.
    The synthetic flag asserts operator intent, not proof that bytes are public.
    Operational acquisition is therefore unconditionally disabled.
    """
    if synthetic_fixture is not True:
        _fail('HARD_BUDGET_UNVERIFIED')
    if type(ttl_seconds) is not int or not 0 < ttl_seconds <= 3600 or not 0 < len(allowlist) <= MAX_ALLOWLIST:
        _fail('QUOTA_EXCEEDED')
    source = _lexical(source)
    allowed = [_lexical(p) for p in allowlist]
    if str(source) not in {str(p) for p in allowed}:
        _fail('PATH_NOT_ALLOWED')
    if len({unicodedata.normalize('NFC', str(p)).casefold() for p in allowed}) != len(allowed):
        _fail('UNSAFE_PATH')
    source_proof = _chain(source, regular=True)
    scratch = _scratch(scratch, source)
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    started = time.monotonic()
    temporary = None
    destination = None
    temporary_fd = None
    fd = _open_read(source, flags)
    try:
        before = _source_stamp(fd)
        if before != _path_stamp(source, flags) or before[2] > MAX_SOURCE_BYTES:
            _fail('QUOTA_EXCEEDED' if before[2] > MAX_SOURCE_BYTES else 'SOURCE_CHANGED')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            raw = handle.read(MAX_SOURCE_BYTES + 1)
            if len(raw) > MAX_SOURCE_BYTES:
                _fail('QUOTA_EXCEEDED')
            digest = hashlib.sha256(raw).hexdigest()
            _after_read(source)

            def stable():
                try:
                    _verify_chain(source_proof)
                    handle.seek(0)
                    second = handle.read(MAX_SOURCE_BYTES + 1)
                    if len(second) > MAX_SOURCE_BYTES or _source_stamp(fd) != before or _path_stamp(source, flags) != before or hashlib.sha256(second).hexdigest() != digest:
                        _fail('SOURCE_CHANGED')
                except OSError:
                    _fail('SOURCE_CHANGED')
                # Cooperative limit is additional detection, never hard isolation.
                if time.monotonic() - started > 30:
                    _fail('COOPERATIVE_DEADLINE_EXCEEDED')

            stable()
            media_type = 'text/html' if source.suffix.lower() in ('.html', '.htm') else 'application/json'
            parsed = parse_source(raw, media_type=media_type)
            current = datetime.now(timezone.utc)
            timestamp = lambda dt: dt.isoformat().replace('+00:00', 'Z')
            src = parsed.value
            descriptor = transform(parsed, source_id=src.get('source_id'), snapshot_id=src.get('snapshot_id'), access_policy_id=src.get('access_policy_id'), bytes_sha256=digest, observed_at=timestamp(current), generated_at=timestamp(current), expires_at=timestamp(current + timedelta(seconds=ttl_seconds)))
            schema = json.loads(Path(__file__).with_name('descriptor.schema.json').read_text(encoding='utf-8'))
            validate_descriptor(descriptor, schema, now=timestamp(current))
            descriptor['validation']['descriptor_schema'] = 'PASS'
            descriptor['validation']['descriptor_semantics'] = 'PASS'
            validate_descriptor(descriptor, schema, now=timestamp(current))
            encoded = (json.dumps(descriptor, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
            if len(encoded) > MAX_DESCRIPTOR_BYTES:
                _fail('QUOTA_EXCEEDED')
            stable()
            _scratch(scratch, source)
            destination = scratch / ('atlas-c2-' + uuid.uuid4().hex + '.json')
            temporary = scratch / (destination.name + '.partial')
            if os.name == 'nt':
                temporary_fd = _open_read(temporary, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_BINARY, create=True)
            else:
                temporary_fd = os.open(temporary, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(temporary_fd, 'wb', closefd=False) as target:
                target.write(encoded)
                target.flush()
                os.fsync(target.fileno())
            stable()
            # Atomic publication with no-clobber semantics on both supported OSes.
            os.link(temporary, destination, follow_symlinks=False)
            if not _remove_partial(temporary, temporary_fd):
                _fail('DERIVED_IDENTITY_CHANGED')
            temporary = None
            _OWNED[str(destination)] = _fingerprint(destination.lstat())
            return destination
    except ReaderError:
        raise
    except OSError:
        _fail('IO_UNVERIFIED')
    finally:
        os.close(fd)
        try:
            if temporary is not None and temporary_fd is not None:
                _remove_partial(temporary, temporary_fd)
        finally:
            if temporary_fd is not None:
                os.close(temporary_fd)


@_io_errors
def cleanup_owned(path):
    """Remove only this process's exact derived identity; no directory scan."""
    path = _lexical(path)
    recorded = _OWNED.get(str(path))
    if recorded is None:
        _fail('NOT_OWNED')
    _chain(path, regular=True)
    if _fingerprint(path.lstat()) != recorded:
        _fail('DERIVED_IDENTITY_CHANGED')
    path.unlink()
    del _OWNED[str(path)]
