"""Generic native presentation payloads in existing, explicitly selected crates.

This module has no producer imports and never evaluates HTML or follows URIs.
The protocol remains unchanged: a view is an ordinary digest-bound File payload.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import zipfile

from caderno_protocol import load_package
from caderno_protocol.model import safe_relative_path, types
from caderno_protocol.storage import (
    MAX_ARCHIVE_BYTES, MAX_EXPANDED_BYTES, MAX_METADATA_BYTES, MAX_PAYLOAD_BYTES,
    _regular_bytes, _strict_json,
)

MEDIA_TYPE = "application/vnd.atlas.native-view+json"
VIEW_NS = "https://github.com/thalesvalente/Atlas/ns/presentation#"
MAX_ENTRIES = 100000
KINDS = frozenset({"record", "node", "relation", "table", "row", "asset", "collection"})


class NativeViewError(ValueError):
    pass


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _json_value(raw: str):
    # Reuse the SDK duplicate-key / finite / precision policy also for scalars.
    return _strict_json(("{\"value\":" + raw + "}").encode("utf-8"))["value"]


def restore_projection(entries: list[dict]) -> dict:
    """Reassemble original values by JSON Pointer without numeric JS conversion."""
    root = None
    seen = set()
    for entry in entries:
        pointer = entry["pointer"]
        if pointer in seen:
            raise NativeViewError("NATIVE_DUPLICATE_POINTER")
        seen.add(pointer)
        value = _json_value(entry["raw_json"])
        if pointer == "":
            if root is not None or not isinstance(value, dict):
                raise NativeViewError("NATIVE_ROOT_INVALID")
            root = value
            continue
        if root is None or not pointer.startswith("/"):
            raise NativeViewError("NATIVE_POINTER_ORDER")
        parts = pointer[1:].split("/")
        if any(re.search(r"~(?![01])", part) for part in parts):
            raise NativeViewError("NATIVE_POINTER_ESCAPE")
        parts = [part.replace("~1", "/").replace("~0", "~") for part in parts]
        parent = root
        for key in parts[:-1]:
            if isinstance(parent, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
                parent = parent[int(key)]
            elif isinstance(parent, dict):
                parent = parent[key]
            else:
                raise NativeViewError("NATIVE_POINTER_PARENT")
        key = parts[-1]
        if isinstance(parent, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", key) or int(key) != len(parent):
                raise NativeViewError("NATIVE_NONCONTIGUOUS_OCCURRENCE")
            parent.append(value)
        elif isinstance(parent, dict):
            if key not in parent:
                raise NativeViewError("NATIVE_POINTER_UNDECLARED")
            parent[key] = value
        else:
            raise NativeViewError("NATIVE_POINTER_PARENT")
    if root is None:
        raise NativeViewError("NATIVE_ROOT_MISSING")
    return root


def validate_entries(entries: list[dict]) -> None:
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise NativeViewError("NATIVE_ENTRY_LIMIT")
    seen = set()
    for e in entries:
        if not isinstance(e, dict) or e.get("kind") not in KINDS:
            raise NativeViewError("NATIVE_ENTRY_TYPE")
        for key in ("uid", "pointer", "group", "title", "raw_json"):
            if not isinstance(e.get(key), str):
                raise NativeViewError("NATIVE_ENTRY_FIELD")
        if not e["uid"] or len(e["uid"]) > 256 or e["uid"] in seen:
            raise NativeViewError("NATIVE_IDENTITY_COLLISION")
        seen.add(e["uid"])
        for key in ("native_id", "source_key", "parent_key", "parent_uid",
                    "table_uid", "family", "status", "date"):
            if key in e and e[key] is not None and not isinstance(e[key], str):
                raise NativeViewError("NATIVE_SCALAR_TYPE")
        fields = e.get("fields")
        if not isinstance(fields, list) or len(fields) > 4096:
            raise NativeViewError("NATIVE_FIELDS_LIMIT")
        for field in fields:
            if not isinstance(field, dict) or any(not isinstance(field.get(k), str)
                                                  for k in ("name", "text", "type")):
                raise NativeViewError("NATIVE_FIELD_TYPE")
        if e["kind"] == "row":
            if not isinstance(e.get("table_uid"), str) or not isinstance(e.get("cells"), dict):
                raise NativeViewError("NATIVE_ROW_INVALID")
            for key, cell in e["cells"].items():
                if (not isinstance(key, str) or not isinstance(cell, dict)
                        or cell.get("type") not in ("null", "string", "integer", "number", "boolean", "array", "object")
                        or not isinstance(cell.get("text"), str)):
                    raise NativeViewError("NATIVE_CELL_INVALID")
    if sum(e["kind"] == "node" for e in entries) > 10000:
        raise NativeViewError("NATIVE_NODE_LIMIT")
    tables = {e["uid"] for e in entries if e["kind"] == "table"}
    for e in entries:
        if e.get("parent_uid") is not None and e["parent_uid"] not in seen:
            raise NativeViewError("NATIVE_PARENT_MISSING")
        if e["kind"] == "row" and e["table_uid"] not in tables:
            raise NativeViewError("NATIVE_TABLE_MISSING")


def _reader(path: Path, metadata_digest: str):
    """Use SDK bounds and confinement; never accept a request-controlled path."""
    if path.suffix.lower() in (".zip", ".eln") and not path.is_dir():
        archive_bytes = _regular_bytes(path, MAX_ARCHIVE_BYTES)
        archive = zipfile.ZipFile(BytesIO(archive_bytes))
        candidates = [i.filename for i in archive.infolist()
                      if i.filename == "ro-crate-metadata.json" or i.filename.endswith("/ro-crate-metadata.json")]
        if len(candidates) != 1:
            archive.close()
            raise NativeViewError("NATIVE_METADATA_AMBIGUOUS")
        metadata_name = candidates[0]
        prefix = metadata_name[:-len("ro-crate-metadata.json")]
        def read(name, limit):
            if safe_relative_path(name) != name:
                raise NativeViewError("NATIVE_UNSAFE_PATH")
            info = archive.getinfo(prefix + name)
            if info.file_size > limit:
                raise NativeViewError("NATIVE_PAYLOAD_LIMIT")
            return archive.read(info)
        if hashlib.sha256(read("ro-crate-metadata.json", MAX_METADATA_BYTES)).hexdigest() != metadata_digest:
            archive.close()
            raise NativeViewError("NATIVE_SOURCE_CHANGED")
        return read, archive.close
    base = path if path.is_dir() else path.parent
    metadata = base / "ro-crate-metadata.json" if path.is_dir() else path
    def read(name, limit):
        if safe_relative_path(name) != name:
            raise NativeViewError("NATIVE_UNSAFE_PATH")
        return _regular_bytes(base / name, limit, base)
    def finish():
        if hashlib.sha256(_regular_bytes(metadata, MAX_METADATA_BYTES, base)).hexdigest() != metadata_digest:
            raise NativeViewError("NATIVE_SOURCE_CHANGED")
    finish()
    return read, finish


def read_source(path: Path, source_id: str) -> tuple[dict, bytes | None]:
    result = {"id": source_id, "status": "INVALID", "entries": [],
              "authority": "DERIVED_NOT_SCIENTIFIC_APPROVAL"}
    try:
        package = load_package(path)
        result["metadata_sha256"] = package.metadata_sha256
        if not package.report.valid:
            result["errors"] = [e.code for e in package.report.errors]
            return result, None
        graph = package.document["@graph"]
        root = next(e for e in graph if e["@id"] == "./")
        result["name"] = root.get("name", source_id)
        payloads = [e for e in graph if "File" in types(e) and e.get("encodingFormat") == MEDIA_TYPE]
        if not payloads:
            result["status"] = "NO_NATIVE_PRESENTATION"
            return result, None
        if root.get(VIEW_NS + "version") != "1":
            raise NativeViewError("NATIVE_VERSION_UNSUPPORTED")
        revision = root.get(VIEW_NS + "revision")
        count = root.get(VIEW_NS + "entryCount")
        expected_digest = root.get(VIEW_NS + "projectionDigest")
        if (not isinstance(revision, str) or not revision or len(revision) > 1024
                or type(count) is not int or not 0 <= count <= MAX_ENTRIES
                or not isinstance(expected_digest, str) or not re.fullmatch("[0-9a-f]{64}", expected_digest)):
            raise NativeViewError("NATIVE_MANIFEST_INVALID")
        read, finish = _reader(Path(path), package.metadata_sha256)
        chunks = {}
        total = 0
        try:
            for payload in payloads:
                name = payload["@id"]
                observation = package.payload_status.get(name, {})
                if observation.get("status") != "AVAILABLE":
                    raise NativeViewError("NATIVE_PAYLOAD_NOT_VERIFIED")
                raw = read(name, MAX_PAYLOAD_BYTES)
                total += len(raw)
                if total > MAX_EXPANDED_BYTES or len(raw) != payload.get("contentSize"):
                    raise NativeViewError("NATIVE_PAYLOAD_LIMIT")
                if hashlib.sha256(raw).hexdigest() != payload.get("cp:sha256"):
                    raise NativeViewError("NATIVE_PAYLOAD_CHANGED")
                chunk = _strict_json(raw)
                ordinal = chunk.get("ordinal")
                if (chunk.get("format") != "atlas-native-view" or chunk.get("version") != "1"
                        or chunk.get("revision") != revision or type(ordinal) is not int
                        or ordinal < 0 or ordinal in chunks or not isinstance(chunk.get("entries"), list)):
                    raise NativeViewError("NATIVE_CHUNK_INVALID")
                chunks[ordinal] = chunk["entries"]
        finally:
            finish()
        if sorted(chunks) != list(range(len(chunks))):
            raise NativeViewError("NATIVE_CHUNK_SEQUENCE")
        entries = [e for i in range(len(chunks)) for e in chunks[i]]
        if len(entries) != count:
            raise NativeViewError("NATIVE_COUNT_MISMATCH")
        validate_entries(entries)
        raw_projection = json_bytes(restore_projection(entries))
        if hashlib.sha256(raw_projection).hexdigest() != expected_digest:
            raise NativeViewError("NATIVE_PROJECTION_MISMATCH")
        result.update(status="READY", entries=entries, revision=revision,
                      projection_sha256=expected_digest, bytes_verified=total,
                      authenticity="NOT_VERIFIED", scientific_approval="NOT_EVALUATED")
        return result, raw_projection
    except (OSError, ValueError, KeyError, TypeError, IndexError, RecursionError, zipfile.BadZipFile) as exc:
        result["entries"] = []
        result["errors"] = [str(exc) if isinstance(exc, NativeViewError) else "NATIVE_SOURCE_INVALID"]
        return result, None


def snapshot(catalog) -> dict:
    return {"version": "1", "authority": "DERIVED_NOT_SCIENTIFIC_APPROVAL",
            "sources": [read_source(s.path, s.id)[0] for s in catalog.sources]}


def export_source(catalog, source_id: str, expected_snapshot: str) -> bytes:
    source = next((s for s in catalog.sources if s.id == source_id), None)
    if source is None:
        raise NativeViewError("NATIVE_SOURCE_NOT_SELECTED")
    result, raw = read_source(source.path, source.id)
    if raw is None or result.get("metadata_sha256") != expected_snapshot:
        raise NativeViewError("NATIVE_SNAPSHOT_CHANGED_OR_INVALID")
    return raw
