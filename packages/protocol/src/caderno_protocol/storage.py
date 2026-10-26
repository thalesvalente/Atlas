"""Read explicitly supplied snapshots without downloading or extracting payloads."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, DecimalException
import math
import os
from pathlib import Path
import stat
from typing import Any
from urllib.parse import urlsplit
import zipfile
import zlib

# Match zipfile's optional LZMA support without requiring that Python extension
# on hosts that only read other supported archive compression methods.
try:
    import lzma
except ImportError:
    _LZMA_ERRORS = ()
else:
    _LZMA_ERRORS = (lzma.LZMAError,)

from .model import Package, ValidationIssue, ValidationReport, safe_relative_path, types, validate_document

MAX_METADATA_BYTES = 2 * 1024 * 1024
MAX_PAYLOAD_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 4096
MAX_COMPRESSION_RATIO = 200


class UnsafeSource(ValueError):
    pass


def _regular_bytes(path: Path, limit: int, base: Path | None = None) -> bytes:
    if base is not None:
        # Do not permit links in explicitly referenced paths. This policy is not
        # a certification of hostile-host race freedom or a retirement tool.
        try:
            rel = path.relative_to(base)
        except ValueError as exc:
            raise UnsafeSource("Payload is outside the authorized package base.") from exc
        current = base
        for part in rel.parts:
            current = current / part
            if current.is_symlink():
                raise UnsafeSource("Symbolic links in package references are unsupported.")
        if not path.resolve().is_relative_to(base.resolve()):
            raise UnsafeSource("Resolved payload escapes its package base.")
    if path.is_symlink():
        raise UnsafeSource("Symbolic links are unsupported.")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise UnsafeSource("Only regular files can be read.")
        if info.st_size > limit:
            raise UnsafeSource("File exceeds the read limit.")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            result = stream.read(limit + 1)
        if len(result) > limit:
            raise UnsafeSource("File grew beyond the read limit.")
        return result
    finally:
        os.close(fd)


def _strict_json(data: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("Duplicate JSON key: " + key)
            obj[key] = value
        return obj
    def invalid_constant(value: str) -> None:
        raise ValueError("Non-finite JSON number: " + value)
    def precise_float(literal: str) -> float:
        # Accept only decimals whose ordinary Python JSON round trip preserves
        # their numeric value. Raw source bytes remain the authority; silently
        # rounding a more precise scientific value is never an import policy.
        value = float(literal)
        if not math.isfinite(value):
            raise ValueError("Non-finite or overflowing JSON decimal.")
        try:
            preserved = Decimal(literal) == Decimal(str(value))
        except DecimalException as exc:
            raise ValueError("JSON decimal exceeds the supported exponent or precision.") from exc
        if not preserved:
            raise ValueError("JSON decimal precision would be lost by the supported numeric representation.")
        return value
    document = json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=invalid_constant, parse_float=precise_float)
    if not isinstance(document, dict):
        raise ValueError("Metadata must be a JSON object.")
    return document


def load_package(path: str | os.PathLike[str]) -> Package:
    """Open a directory, metadata JSON or ZIP as an offline read-only snapshot.

    Errors are returned in Package.report, including inaccessible sources, so
    callers can render an honest failure state without fabricating a dataset.
    """
    source = Path(path)
    source_name = source.name
    archive: zipfile.ZipFile | None = None
    archive_file: Any = None
    try:
        if source.is_symlink():
            raise UnsafeSource("The explicitly supplied source must not be a symbolic link.")
        archive_prefix = ""
        if source.is_dir():
            base = source
            raw = _regular_bytes(source / "ro-crate-metadata.json", MAX_METADATA_BYTES, base)
            payload_reader = lambda name, limit: _regular_bytes(base / name, limit, base)
        elif source.suffix.lower() in {".zip", ".eln"}:
            # The archive is held by an opened descriptor; no extraction occurs.
            data = _regular_bytes(source, MAX_ARCHIVE_BYTES)
            from io import BytesIO
            archive_file = BytesIO(data)
            archive = zipfile.ZipFile(archive_file)
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_MEMBERS or sum(x.file_size for x in infos) > MAX_EXPANDED_BYTES:
                raise UnsafeSource("Archive exceeds member or expanded-byte limit.")
            names: set[str] = set()
            files: dict[str, zipfile.ZipInfo] = {}
            for info in infos:
                name = info.filename.rstrip("/")
                if safe_relative_path(name) != name:
                    raise UnsafeSource("Archive contains a non-portable or unsafe member path.")
                if name.casefold() in names:
                    raise UnsafeSource("Archive contains duplicate or case-colliding names.")
                names.add(name.casefold())
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode) or (mode and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_IFMT(mode) == 0)):
                    raise UnsafeSource("Archive links and special files are unsupported.")
                if info.flag_bits & 1:
                    raise UnsafeSource("Encrypted archives are not supported.")
                if info.file_size > MAX_PAYLOAD_BYTES or (info.file_size > 1024 and info.file_size / max(info.compress_size, 1) > MAX_COMPRESSION_RATIO):
                    raise UnsafeSource("Archive member exceeds size or compression-ratio limit.")
                if not info.is_dir():
                    files[name] = info
            candidates = [n for n in files if n == "ro-crate-metadata.json" or n.endswith("/ro-crate-metadata.json")]
            if len(candidates) != 1:
                raise UnsafeSource("An archive must contain exactly one metadata document.")
            metadata_name = candidates[0]
            archive_prefix = metadata_name[:-len("ro-crate-metadata.json")]
            if archive_prefix and any(not n.startswith(archive_prefix) for n in files):
                raise UnsafeSource("Archive contains members outside the package root.")
            if files[metadata_name].file_size > MAX_METADATA_BYTES:
                raise UnsafeSource("Metadata exceeds the read limit.")
            raw = archive.read(files[metadata_name])
            def payload_reader(name: str, limit: int) -> bytes:
                item = files.get(archive_prefix + name)
                if item is None:
                    raise FileNotFoundError(name)
                if item.file_size > limit:
                    raise UnsafeSource("Payload exceeds the remaining read budget.")
                return archive.read(item)
        else:
            base = source.parent
            raw = _regular_bytes(source, MAX_METADATA_BYTES, base)
            payload_reader = lambda name, limit: _regular_bytes(base / name, limit, base)
        document = _strict_json(raw)
        report = validate_document(document)
        statuses: dict[str, dict[str, Any]] = {}
        payload_bytes_read = 0
        graph = document.get("@graph", [])
        for entity in graph if isinstance(graph, list) else []:
            if not isinstance(entity, dict) or "File" not in types(entity):
                continue
            eid = entity.get("@id")
            if not isinstance(eid, str):
                continue
            entry: dict[str, Any] = {"declared": entity.get("cp:availability", "UNKNOWN"), "status": "UNVERIFIED"}
            statuses[eid] = entry
            try:
                external = urlsplit(eid).scheme in {"http", "https"}
            except ValueError:
                entry["status"] = "UNSAFE_REFERENCE"
                continue
            if external:
                entry["status"] = "EXTERNAL_UNRESOLVED"
                continue
            relative = safe_relative_path(eid)
            if relative is None:
                entry["status"] = "UNSAFE_REFERENCE"
                continue
            if payload_bytes_read >= MAX_EXPANDED_BYTES:
                entry["status"] = "READ_BUDGET_EXCEEDED"
                report.warnings.append(ValidationIssue("READ_BUDGET_EXCEEDED", eid, "Aggregate payload verification budget was exhausted; the record remains unverified."))
                continue
            try:
                payload = payload_reader(relative, min(MAX_PAYLOAD_BYTES, MAX_EXPANDED_BYTES - payload_bytes_read))
                payload_bytes_read += len(payload)
            except FileNotFoundError:
                entry["status"] = "MISSING"
                report.warnings.append(ValidationIssue("PAYLOAD_MISSING", eid, "The record exists but its local payload is absent."))
                continue
            except (OSError, UnsafeSource, zipfile.BadZipFile, zlib.error, *_LZMA_ERRORS, RuntimeError) as exc:
                entry["status"] = "UNAVAILABLE"
                report.warnings.append(ValidationIssue("PAYLOAD_UNAVAILABLE", eid, str(exc)))
                continue
            actual = hashlib.sha256(payload).hexdigest()
            entry["sha256"] = actual
            entry["size"] = len(payload)
            declared = entity.get("cp:sha256")
            if declared is not None and actual != declared:
                entry["status"] = "INTEGRITY_MISMATCH"
                report.errors.append(ValidationIssue("INTEGRITY_MISMATCH", eid, "Payload bytes do not match their declared SHA-256 digest; authenticity is not evaluated."))
            elif isinstance(entity.get("contentSize"), int) and entity["contentSize"] != len(payload):
                entry["status"] = "INTEGRITY_MISMATCH"
                report.errors.append(ValidationIssue("SIZE_MISMATCH", eid, "Payload length differs from its declared contentSize."))
            else:
                entry["status"] = "AVAILABLE" if declared else "AVAILABLE_UNVERIFIED"
        return Package(document, hashlib.sha256(raw).hexdigest(), report, statuses, source_name)
    except FileNotFoundError:
        return Package({}, "", ValidationReport(errors=[ValidationIssue("SOURCE_INACCESSIBLE", "$", "The supplied source or metadata file is absent.")]), source_name=source_name)
    except (PermissionError, OSError, ValueError, UnicodeError, zipfile.BadZipFile, zlib.error, *_LZMA_ERRORS, RuntimeError, RecursionError) as exc:
        code = "SOURCE_UNSAFE" if isinstance(exc, UnsafeSource) else "SOURCE_INVALID"
        return Package({}, "", ValidationReport(errors=[ValidationIssue(code, "$", str(exc))]), source_name=source_name)
    finally:
        if archive is not None:
            archive.close()
        if archive_file is not None:
            archive_file.close()
