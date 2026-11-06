"""Resolve authorized names and read the same object used for identity checks."""

from contextlib import ExitStack
from dataclasses import dataclass
from hashlib import sha256
import hmac
import os
from pathlib import Path
import sys

from .contracts import MAX_DOCUMENT_BYTES, Rejected, decode_document, digest, relative_path, require, token

BLOCK_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Stamp:
    identity: tuple
    size: int
    links: int
    changes: tuple


def open_root(stack, path):
    if sys.platform == "linux":
        from .linux import Root
    elif sys.platform == "win32":
        from .windows import Root
    else:
        raise Rejected("PLATFORM_UNSUPPORTED")
    try:
        return Root(stack, path)
    except (OSError, UnicodeError):
        raise Rejected("UNSAFE_ROOT") from None


def authorized_roots(stack, specs):
    roots = {}
    for spec in specs:
        alias, separator, value = spec.partition("=")
        require(separator and token(alias), "INVALID_ROOT_SPEC")
        require(alias not in roots, "ROOT_ALIAS_COLLISION")
        path = Path(value)
        require(path.is_absolute() and ".." not in path.parts, "INVALID_ROOT_SPEC")
        root = open_root(stack, path)
        canonical = Path(root.path)
        for previous in roots.values():
            length = min(len(previous.components), len(root.components))
            earlier = Path(previous.path)
            require(previous.identity != root.identity
                    and previous.components[:length] != root.components[:length]
                    and not canonical.is_relative_to(earlier) and not earlier.is_relative_to(canonical),
                    "ROOT_ALIAS_COLLISION")
        roots[alias] = root
    return roots


def consume(read, expected_size, collect):
    checksum = sha256()
    blocks = [] if collect else None
    remaining = expected_size
    while True:
        block = read(min(BLOCK_BYTES, remaining + 1))
        if not block:
            break
        remaining -= len(block)
        require(remaining >= 0, "FILE_CHANGED")
        checksum.update(block)
        if blocks is not None:
            blocks.append(block)
    require(remaining == 0, "FILE_CHANGED")
    return checksum.hexdigest(), b"".join(blocks) if blocks is not None else None


def inspect(root, parts, *, expected_sha, size=None, document=None, limit=MAX_DOCUMENT_BYTES):
    try:
        with root.open_file(parts) as (read, observed):
            require(observed.links == 1, "HARDLINK_UNSAFE")
            if document:
                require(0 <= observed.size <= limit, "DOCUMENT_LIMIT")
            else:
                require(observed.size == size, "FILE_SIZE_MISMATCH")
            actual_sha, payload = consume(read, observed.size, document is not None)
    except FileNotFoundError:
        raise Rejected("DOCUMENT_MISSING" if document else "FILE_MISSING") from None
    except (OSError, UnicodeError):
        raise Rejected("UNSAFE_DOCUMENT" if document else "UNSAFE_FILE") from None
    code = document + "_DIGEST_MISMATCH" if document else "FILE_DIGEST_MISMATCH"
    require(hmac.compare_digest(actual_sha, expected_sha), code)
    return observed, payload


def confirm(root, parts, expected):
    """Detect drift after a file's content check, without hashing it again."""
    try:
        with root.open_file(parts) as (_, observed):
            require(observed == expected, "FILE_CHANGED")
    except (OSError, UnicodeError, Rejected):
        raise Rejected("FILE_CHANGED") from None


def read_pinned_document(filename, expected_sha, document, *, limit=MAX_DOCUMENT_BYTES):
    require(digest(expected_sha), "INVALID_EXTERNAL_DIGEST")
    path = Path(os.path.abspath(filename))
    with ExitStack() as stack:
        root = open_root(stack, path.parent)
        _, raw = inspect(root, relative_path(path.name), expected_sha=expected_sha, document=document, limit=limit)
    return decode_document(raw), len(raw)
