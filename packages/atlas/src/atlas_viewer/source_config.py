"""Local preferences for explicitly selected sources; never scientific state.

Only save_sources writes, and only to the selected configuration file. Loading
preferences does not search for sources, import a producer, or alter a package.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any

from caderno_protocol import load_package

from .catalog import MAX_SOURCES

CONFIG_VERSION = 1
MAX_CONFIG_BYTES = 64 * 1024
MAX_PATH_CHARS = 4096
_METADATA = "ro-crate-metadata.json"


class SourceConfigError(ValueError):
    """A stable diagnostic which contains no selected paths or source data."""


def _path(value: str | os.PathLike[str], *, base: Path | None = None) -> Path:
    try:
        text = os.fspath(value)
        if (not isinstance(text, str) or not text.strip()
                or len(text) > MAX_PATH_CHARS
                or any(ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in text)):
            raise SourceConfigError("ATLAS_CONFIG_PATH_INVALID")
        path = Path(text).expanduser()
        return path if path.is_absolute() else (base or Path.cwd()) / path
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        if isinstance(exc, SourceConfigError):
            raise
        raise SourceConfigError("ATLAS_CONFIG_PATH_INVALID") from None


def default_config_path() -> Path:
    """Return the user-specific location without reading or creating it."""
    try:
        if sys.platform == "win32":
            location = os.environ.get("LOCALAPPDATA")
            root = _path(location) if location else Path.home() / "AppData" / "Local"
            if location and not Path(location).is_absolute():
                raise SourceConfigError("ATLAS_CONFIG_DEFAULT_LOCATION_INVALID")
            return root / "Atlas" / "sources.json"
        location = os.environ.get("XDG_CONFIG_HOME")
        if location and not Path(location).is_absolute():
            raise SourceConfigError("ATLAS_CONFIG_DEFAULT_LOCATION_INVALID")
        root = _path(location) if location else Path.home() / ".config"
        return root / "atlas" / "sources.json"
    except (OSError, RuntimeError) as exc:
        if isinstance(exc, SourceConfigError):
            raise
        raise SourceConfigError("ATLAS_CONFIG_DEFAULT_LOCATION_INVALID") from None


def _config_path(value: str | os.PathLike[str] | None) -> Path:
    return default_config_path() if value is None else _path(value)


def _source_values(values: Any) -> list[str]:
    if not isinstance(values, list):
        raise SourceConfigError("ATLAS_CONFIG_SOURCES_INVALID")
    if len(values) > MAX_SOURCES:
        raise SourceConfigError("ATLAS_MAX_16_EXPLICIT_SOURCES")
    for value in values:
        if (not isinstance(value, str) or not value.strip()
                or len(value) > MAX_PATH_CHARS
                or any(ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in value)):
            raise SourceConfigError("ATLAS_CONFIG_SOURCE_INVALID")
    return values


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SourceConfigError("ATLAS_CONFIG_DUPLICATE_KEY")
        result[key] = value
    return result


def _invalid_number(_: str) -> None:
    raise SourceConfigError("ATLAS_CONFIG_JSON_INVALID")


def _read_document(path: Path, *, missing_ok: bool) -> dict[str, Any] | None:
    """Read one bounded regular file; no directory discovery or package reads."""
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise SourceConfigError("ATLAS_CONFIG_FILE_UNSAFE")
        flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise SourceConfigError("ATLAS_CONFIG_FILE_UNSAFE")
            if info.st_size > MAX_CONFIG_BYTES:
                raise SourceConfigError("ATLAS_CONFIG_TOO_LARGE")
            raw = stream.read(MAX_CONFIG_BYTES + 1)
        if len(raw) > MAX_CONFIG_BYTES:
            raise SourceConfigError("ATLAS_CONFIG_TOO_LARGE")
    except FileNotFoundError:
        if missing_ok:
            return None
        raise SourceConfigError("ATLAS_CONFIG_NOT_FOUND") from None
    except OSError:
        raise SourceConfigError("ATLAS_CONFIG_READ_FAILED") from None
    try:
        document = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                              parse_constant=_invalid_number)
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, SourceConfigError):
            raise
        raise SourceConfigError("ATLAS_CONFIG_JSON_INVALID") from None
    if not isinstance(document, dict) or set(document) != {"version", "sources"}:
        raise SourceConfigError("ATLAS_CONFIG_SCHEMA_INVALID")
    if type(document["version"]) is not int or document["version"] != CONFIG_VERSION:
        raise SourceConfigError("ATLAS_CONFIG_VERSION_UNSUPPORTED")
    _source_values(document["sources"])
    return document


def _readable_regular(path: Path) -> None:
    """Check access without reading payloads or blocking on special files."""
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise SourceConfigError("ATLAS_SOURCE_UNSAFE")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise SourceConfigError("ATLAS_SOURCE_UNSAFE")
    finally:
        os.close(descriptor)


def _normalize_sources(values: list[str], *, base: Path | None = None) -> list[str]:
    _source_values(values)  # Reject the complete count/types before accessing a source.
    selected: list[str] = []
    identities: set[str] = set()
    for value in values:
        path = _path(value, base=base)
        try:
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                metadata = path / _METADATA
            elif stat.S_ISREG(info.st_mode):
                metadata = path
            else:
                raise SourceConfigError("ATLAS_SOURCE_UNSAFE")
            _readable_regular(metadata)
            # Check the supplied leaf before resolving aliases: do not turn a
            # forbidden symbolic-link source into an apparently ordinary path.
            resolved = path.resolve(strict=True)
            identity = os.path.normcase(str(metadata.resolve(strict=True)))
        except FileNotFoundError:
            raise SourceConfigError("ATLAS_SOURCE_NOT_FOUND") from None
        except (OSError, RuntimeError):
            raise SourceConfigError("ATLAS_SOURCE_INACCESSIBLE") from None
        if identity in identities:
            raise SourceConfigError("ATLAS_SOURCE_DUPLICATE")
        identities.add(identity)
        selected.append(str(resolved))
    return selected


def resolve_sources(sources: list[str] | None = None,
                    config_path: str | os.PathLike[str] | None = None) -> list[str]:
    """Select explicit CLI sources, otherwise the explicit/default JSON.

    None means no command-line selection. An explicitly supplied empty list is
    a deliberate empty selection and does not read any configuration.
    """
    if sources is not None:
        return _normalize_sources(sources)
    path = _config_path(config_path)
    document = _read_document(path, missing_ok=config_path is None)
    if document is None:
        return []
    return _normalize_sources(document["sources"], base=path.parent)


def config_summary(config_path: str | os.PathLike[str] | None = None, *,
                   show_paths: bool = False) -> dict[str, Any]:
    """Show preferences without opening sources, including now-missing sources."""
    path = _config_path(config_path)
    document = _read_document(path, missing_ok=config_path is None)
    values = document["sources"] if document is not None else []
    summary: dict[str, Any] = {
        "version": CONFIG_VERSION,
        "configured": document is not None,
        "source_count": len(values),
        "sources": values if show_paths else ["<local path hidden>"] * len(values),
    }
    if show_paths:
        summary["config_path"] = str(path)
    return summary


def _protect_sources(target: Path, selected: list[str], previous: dict[str, Any] | None) -> None:
    """Prevent the preference write from targeting selected scientific storage."""
    destination = target.resolve(strict=False)
    # These are fixed paths anchored at explicitly supplied locations, not a
    # directory scan or discovery of additional sources. The marker protects
    # an existing package even if its configured metadata alias was removed.
    if (destination.name.casefold() == _METADATA
            or (destination.parent / _METADATA).is_file()):
        raise SourceConfigError("ATLAS_CONFIG_INSIDE_SOURCE")
    candidates = [Path(value) for value in selected]
    if previous:
        candidates.extend(_path(value, base=target.parent)
                          for value in previous["sources"])
    for path in candidates:
        resolved = path.resolve(strict=False)
        if destination == resolved:
            raise SourceConfigError("ATLAS_CONFIG_INSIDE_SOURCE")
        if resolved.name.casefold() == _METADATA:
            root = resolved.parent
        elif resolved.is_dir():
            root = resolved
        elif resolved.is_file() and resolved.suffix.lower() not in {".zip", ".eln"}:
            # The protocol accepts any ordinary metadata filename, not only
            # ro-crate-metadata.json; its payload base is the parent directory.
            # Archives remain single-file sources, so a sibling config is safe.
            root = resolved.parent
        elif (resolved.parent / _METADATA).is_file():
            root = resolved.parent
        else:
            continue
        if destination.is_relative_to(root):
            raise SourceConfigError("ATLAS_CONFIG_INSIDE_SOURCE")


def save_sources(sources: list[str],
                 config_path: str | os.PathLike[str] | None = None) -> None:
    """Validate all choices, then atomically replace only the preference JSON.

    An existing malformed/non-configuration file is preserved, requiring an
    explicit manual repair or a new --config path. Clearing writes an empty
    versioned list; it never deletes a package or recursively removes anything.
    """
    selected = _normalize_sources(sources)
    target = _config_path(config_path)
    previous = _read_document(target, missing_ok=True)
    try:
        _protect_sources(target, selected, previous)
        for value in selected:
            if not load_package(value).report.valid:
                raise SourceConfigError("ATLAS_SOURCE_INVALID_PACKAGE")
        encoded = (json.dumps({"version": CONFIG_VERSION, "sources": selected},
                              ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        if len(encoded) > MAX_CONFIG_BYTES:
            raise SourceConfigError("ATLAS_CONFIG_TOO_LARGE")
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # mkstemp creates an exclusive regular file with user-only POSIX mode.
        descriptor, temporary = tempfile.mkstemp(prefix=".atlas-sources-", suffix=".tmp",
                                                  dir=target.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            # Recheck destination type before the commit point. An atomic replace
            # preserves the previous file until this single operation succeeds.
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise SourceConfigError("ATLAS_CONFIG_FILE_UNSAFE")
            os.replace(temporary, target)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
    except SourceConfigError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise SourceConfigError("ATLAS_CONFIG_WRITE_FAILED") from None
