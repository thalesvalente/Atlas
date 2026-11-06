"""Open single Windows path components relative to held directory handles."""

from contextlib import ExitStack, contextmanager
import ctypes as c
from ctypes import wintypes as w
from pathlib import PureWindowsPath
import re

from .contracts import Rejected, require
from .filesystem import Stamp

FILE_READ_DATA = 0x0001
FILE_TRAVERSE = 0x0020
FILE_READ_ATTRIBUTES = 0x0080
SYNCHRONIZE = 0x00100000
FILE_SHARE_READ = 0x0001
FILE_SHARE_WRITE = 0x0002
FILE_OPEN = 1
OPEN_EXISTING = 3
FILE_SYNCHRONOUS_IO_NONALERT = 0x0020
FILE_OPEN_REPARSE_POINT = 0x00200000
FILE_OPEN_NO_RECALL = 0x00400000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_FLAG_OPEN_NO_RECALL = 0x00100000
OBJ_CASE_INSENSITIVE = 0x0040
OBJ_DONT_REPARSE = 0x1000
FILE_TYPE_DISK = 1
# Device, reparse point, offline, recall-on-open and recall-on-data-access.
UNSAFE_ATTRIBUTES = 0x40 | 0x400 | 0x1000 | 0x40000 | 0x400000
DIRECTORY_ACCESS = FILE_TRAVERSE | FILE_READ_ATTRIBUTES | SYNCHRONIZE
FILE_ACCESS = FILE_READ_DATA | FILE_READ_ATTRIBUTES | SYNCHRONIZE
DIRECTORY_SHARE = FILE_SHARE_READ | FILE_SHARE_WRITE
INVALID_HANDLE = w.HANDLE(-1).value


class UnicodeString(c.Structure):
    _fields_ = [("length", w.USHORT), ("maximum", w.USHORT), ("buffer", w.LPWSTR)]


class ObjectAttributes(c.Structure):
    _fields_ = [
        ("length", w.ULONG), ("root", w.HANDLE), ("name", c.POINTER(UnicodeString)),
        ("attributes", w.ULONG), ("security_descriptor", w.LPVOID), ("security_qos", w.LPVOID),
    ]


class IoStatus(c.Structure):
    # Pointer-sized union of NTSTATUS and PVOID, followed by ULONG_PTR.
    _fields_ = [("status", w.LPVOID), ("information", c.c_size_t)]


class BasicInfo(c.Structure):
    _fields_ = [("creation_time", c.c_int64), ("access_time", c.c_int64),
                ("write_time", c.c_int64), ("change_time", c.c_int64), ("attributes", w.DWORD)]


class StandardInfo(c.Structure):
    _fields_ = [("allocation_size", c.c_int64), ("size", c.c_int64), ("links", w.DWORD),
                ("delete_pending", c.c_ubyte), ("directory", c.c_ubyte)]


class IdInfo(c.Structure):
    _fields_ = [("volume", c.c_uint64), ("file_id", c.c_ubyte * 16)]


KERNEL = c.WinDLL("kernel32", use_last_error=True)
NTDLL = c.WinDLL("ntdll", use_last_error=True)


def api(library, name, result, *args):
    function = getattr(library, name)
    function.restype = result
    function.argtypes = args
    return function


create_file = api(KERNEL, "CreateFileW", w.HANDLE, w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID,
                  w.DWORD, w.DWORD, w.HANDLE)
close_handle = api(KERNEL, "CloseHandle", w.BOOL, w.HANDLE)
drive_type = api(KERNEL, "GetDriveTypeW", w.UINT, w.LPCWSTR)
final_path = api(KERNEL, "GetFinalPathNameByHandleW", w.DWORD, w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD)
file_type = api(KERNEL, "GetFileType", w.DWORD, w.HANDLE)
file_information = api(KERNEL, "GetFileInformationByHandleEx", w.BOOL, w.HANDLE, c.c_int, w.LPVOID, w.DWORD)
read_file = api(KERNEL, "ReadFile", w.BOOL, w.HANDLE, w.LPVOID, w.DWORD, c.POINTER(w.DWORD), w.LPVOID)
nt_create_file = api(NTDLL, "NtCreateFile", w.LONG, c.POINTER(w.HANDLE), w.DWORD,
                     c.POINTER(ObjectAttributes), c.POINTER(IoStatus), w.LPVOID,
                     w.ULONG, w.ULONG, w.ULONG, w.ULONG, w.LPVOID, w.ULONG)
win_error = api(NTDLL, "RtlNtStatusToDosError", w.ULONG, w.LONG)


def open_child(stack, parent, component, directory):
    encoded_length = len(component.encode("utf-16-le"))
    buffer = c.create_unicode_buffer(component, encoded_length // 2 + 1)
    name = UnicodeString(encoded_length, encoded_length + 2, c.cast(buffer, w.LPWSTR))
    attributes = ObjectAttributes(c.sizeof(ObjectAttributes), parent, c.pointer(name),
                                  OBJ_CASE_INSENSITIVE | OBJ_DONT_REPARSE, None, None)
    handle, status = w.HANDLE(), IoStatus()
    result = nt_create_file(
        c.byref(handle), DIRECTORY_ACCESS if directory else FILE_ACCESS,
        c.byref(attributes), c.byref(status), None, 0,
        DIRECTORY_SHARE if directory else FILE_SHARE_READ, FILE_OPEN,
        FILE_OPEN_REPARSE_POINT | FILE_SYNCHRONOUS_IO_NONALERT | FILE_OPEN_NO_RECALL, None, 0,
    )
    if result < 0:
        raise c.WinError(win_error(result))
    stack.callback(close_handle, handle)
    return handle


def handle_path(handle):
    buffer = c.create_unicode_buffer(32768)
    length = final_path(handle, buffer, len(buffer), 0)  # Normalized path, DOS volume.
    if not 0 < length < len(buffer):
        raise OSError("GetFinalPathNameByHandleW failed")
    return buffer.value


def information(handle, info_class, info_type):
    info = info_type()
    if not file_information(handle, info_class, c.byref(info), c.sizeof(info)):
        raise c.WinError(c.get_last_error())
    return info


def stamp(handle, directory):
    basic = information(handle, 0, BasicInfo)       # FileBasicInfo
    standard = information(handle, 1, StandardInfo) # FileStandardInfo
    require(file_type(handle) == FILE_TYPE_DISK and not basic.attributes & UNSAFE_ATTRIBUTES
            and not standard.delete_pending and bool(standard.directory) == directory, "UNSAFE_FILE")
    identity = information(handle, 18, IdInfo)      # FileIdInfo
    return Stamp((identity.volume, bytes(identity.file_id)), standard.size, standard.links,
                 (basic.creation_time, basic.write_time, basic.change_time, basic.attributes))


def read_bytes(handle, size):
    buffer, count = c.create_string_buffer(size), w.DWORD()
    if not read_file(handle, buffer, size, c.byref(count), None):
        error = c.get_last_error()
        if error == 38:  # ERROR_HANDLE_EOF
            return b""
        raise c.WinError(error)
    return buffer[:count.value]


class Root:
    def __init__(self, stack, path):
        drive = path.anchor
        require(re.fullmatch(r"[A-Za-z]:\\", drive) is not None and drive_type(drive) in (2, 3, 6),
                "UNSAFE_ROOT")
        expected = "\\\\?\\" + drive
        handle = create_file(expected, DIRECTORY_ACCESS, DIRECTORY_SHARE, None, OPEN_EXISTING,
                             FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT
                             | FILE_FLAG_OPEN_NO_RECALL, None)
        if handle == INVALID_HANDLE:
            raise c.WinError(c.get_last_error())
        stack.callback(close_handle, handle)
        stamp(handle, True)
        actual = handle_path(handle)
        require(actual.casefold() == expected.casefold(), "UNSAFE_ROOT")
        for component in path.parts[1:]:
            handle = open_child(stack, handle, component, True)
            stamp(handle, True)
            expected = actual.rstrip("\\") + "\\" + component
            actual = handle_path(handle)
            require(actual.casefold() == expected.casefold(), "UNSAFE_ROOT")
        self.handle = handle
        self.path = actual
        self.identity = stamp(handle, True).identity
        self.components = (self.identity[0], *(part.casefold()
                                              for part in PureWindowsPath(actual[4:]).parts[1:]))

    @contextmanager
    def open_file(self, parts):
        with ExitStack() as held:
            parent, parent_path = self.handle, self.path
            guards = [(parent, parent_path, stamp(parent, True))]
            for part in parts[:-1]:
                parent = open_child(held, parent, part, True)
                parent_path = parent_path.rstrip("\\") + "\\" + part
                observed = stamp(parent, True)
                require(handle_path(parent) == parent_path, "FILE_ALIAS_COLLISION")
                guards.append((parent, parent_path, observed))
            handle = open_child(held, parent, parts[-1], False)
            expected = parent_path.rstrip("\\") + "\\" + parts[-1]
            before = stamp(handle, False)
            require(handle_path(handle) == expected, "FILE_ALIAS_COLLISION")
            yield lambda size: read_bytes(handle, size), before
            try:
                require(stamp(handle, False) == before and handle_path(handle) == expected, "FILE_CHANGED")
                for directory, name, observed in guards:
                    require(stamp(directory, True) == observed and handle_path(directory) == name, "FILE_CHANGED")
            except OSError:
                raise Rejected("FILE_CHANGED") from None
