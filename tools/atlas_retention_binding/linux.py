"""Use Linux openat2 for beneath-root opens and keep files pinned by descriptor."""

from contextlib import ExitStack, contextmanager
import ctypes
import errno
import os
from pathlib import Path
import platform
import re
import stat

from .contracts import Rejected, require
from .filesystem import Stamp

# Linux UAPI uses syscall 437 on both supported architectures.
SYS_OPENAT2 = 437
RESOLVE_NO_XDEV = 0x01
RESOLVE_NO_SYMLINKS = 0x04
RESOLVE_BENEATH = 0x08
RESOLVE_LOCAL = RESOLVE_NO_SYMLINKS | RESOLVE_BENEATH
PATH_FLAGS = os.O_PATH | os.O_CLOEXEC
DIRECTORY_FLAGS = PATH_FLAGS | os.O_DIRECTORY
LOCAL_FILESYSTEMS = {b"ext2", b"ext3", b"ext4", b"btrfs", b"xfs", b"tmpfs", b"overlay"}
MOUNTINFO_ESCAPE = re.compile(rb"\\([0-7]{3})")


class OpenHow(ctypes.Structure):
    _fields_ = [("flags", ctypes.c_uint64), ("mode", ctypes.c_uint64), ("resolve", ctypes.c_uint64)]


LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.syscall.restype = ctypes.c_long


def open_beneath(stack, directory, parts, flags, resolve):
    name = os.fsencode("/".join(parts) or ".")
    how = OpenHow(flags, 0, resolve)
    fd = LIBC.syscall(ctypes.c_long(SYS_OPENAT2), ctypes.c_int(directory), ctypes.c_char_p(name),
                      ctypes.byref(how), ctypes.c_size_t(ctypes.sizeof(how)))
    if fd < 0:
        error = ctypes.get_errno()
        if error in (errno.ENOSYS, errno.EINVAL):
            raise Rejected("OPENAT2_UNAVAILABLE")
        raise OSError(error, os.strerror(error))
    stack.callback(os.close, fd)
    return fd


def stamp(fd):
    info = os.fstat(fd)
    return Stamp((info.st_dev, info.st_ino), info.st_size, info.st_nlink,
                 (info.st_mtime_ns, info.st_ctime_ns, info.st_mode))


def mount_path(field):
    unescaped = MOUNTINFO_ESCAPE.sub(lambda match: bytes([int(match[1], 8)]), field)
    return Path(os.fsdecode(unescaped))


def physical_components(fd, path, device):
    # A bind-mounted subtree has a different namespace path but the same
    # filesystem-relative ancestry. Use that ancestry to reject overlap.
    with open(f"/proc/self/fdinfo/{fd}", "rb") as info:
        mount_id = next((line.split()[1] for line in info if line.startswith(b"mnt_id:")), None)
    with open("/proc/self/mountinfo", "rb") as mounts:
        for line in mounts:
            prefix, _, suffix = line.partition(b" - ")
            columns = prefix.split()
            if columns[0] == mount_id:
                require(suffix.split()[0] in LOCAL_FILESYSTEMS, "FILESYSTEM_UNSUPPORTED")
                mountpoint = mount_path(columns[4])
                require(path.is_relative_to(mountpoint), "UNSAFE_ROOT")
                offset = path.relative_to(mountpoint)
                return (device, *(mount_path(columns[3]) / offset).parts)
    raise Rejected("FILESYSTEM_UNSUPPORTED")


def handle_path(fd):
    return os.readlink(f"/proc/self/fd/{fd}")


class Root:
    def __init__(self, stack, path):
        require(platform.machine() in ("x86_64", "aarch64"), "PLATFORM_UNSUPPORTED")
        require(path.anchor == "/", "INVALID_ROOT_SPEC")
        self.parts = path.parts
        self.path = str(path)
        self.system = os.open("/", DIRECTORY_FLAGS)
        stack.callback(os.close, self.system)
        self.fd = self.reopen(stack)
        self.identity = stamp(self.fd).identity
        require(handle_path(self.fd) == self.path, "UNSAFE_ROOT")
        self.components = physical_components(self.fd, path, self.identity[0])

    def reopen(self, stack):
        return open_beneath(stack, self.system, self.parts[1:], DIRECTORY_FLAGS, RESOLVE_LOCAL)

    def inside(self, stack, parts, flags):
        return open_beneath(stack, self.fd, parts, flags, RESOLVE_LOCAL | RESOLVE_NO_XDEV)

    @contextmanager
    def open_file(self, parts):
        with ExitStack() as held:
            root_before = stamp(self.fd)
            require(stamp(self.reopen(held)) == root_before, "FILE_CHANGED")
            parents = []
            for length in range(1, len(parts)):
                prefix = parts[:length]
                parent = self.inside(held, prefix, DIRECTORY_FLAGS)
                parents.append((prefix, stamp(parent)))

            named = self.inside(held, parts, PATH_FLAGS)
            before = stamp(named)
            require(stat.S_ISREG(before.changes[-1]), "UNSAFE_FILE")
            require(before.links == 1, "HARDLINK_UNSAFE")
            expected = os.path.join(self.path, *parts)
            require(handle_path(named) == expected, "FILE_ALIAS_COLLISION")
            flags = os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC
            # The only magic link followed is the process's own pinned descriptor.
            descriptor = f"/proc/self/fd/{named}"
            try:
                fd = os.open(descriptor, flags | os.O_NOATIME)
            except PermissionError:
                fd = os.open(descriptor, flags)
            with os.fdopen(fd, "rb") as stream:
                require(stamp(fd) == before, "FILE_CHANGED")
                yield stream.read, before
                try:
                    current = self.inside(held, parts, PATH_FLAGS)
                    require(stamp(fd) == before and stamp(current) == before and handle_path(current) == expected,
                            "FILE_CHANGED")
                    for prefix, observed in parents:
                        require(stamp(self.inside(held, prefix, DIRECTORY_FLAGS)) == observed, "FILE_CHANGED")
                    require(stamp(self.reopen(held)) == root_before, "FILE_CHANGED")
                except OSError:
                    raise Rejected("FILE_CHANGED") from None
