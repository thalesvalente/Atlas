"""External, read-only adapter: existing notebook projection -> standard crate.

The producer-only project() API is reused, never copied into the viewer.
No HTML parsing, source discovery, migrations, provider calls or overwrites.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zlib
import ctypes
import errno

from caderno_protocol import CONTEXT, PROFILE_ID, PROFILE_VERSION, PROCESS_PROFILE
from caderno_protocol.model import RO_CRATE, validate_document
from caderno_protocol.storage import MAX_METADATA_BYTES, MAX_PAYLOAD_BYTES, MAX_EXPANDED_BYTES, _strict_json, _regular_bytes
from atlas_viewer.native_values import scalar, dtype, entry_values

MEDIA_TYPE = "application/vnd.atlas.native-view+json"
COMPRESSED_MEDIA_TYPE = "application/vnd.atlas.native-view+zlib"
# Bound the logical presentation separately from the protocol's 32 MiB
# *stored* payload cap; no files or scientific records are truncated.
MAX_NATIVE_LOGICAL_BYTES = 256 * 1024 * 1024
VIEW_NS = "https://github.com/thalesvalente/Atlas/ns/presentation#"
ASSETS = {"resources", "products", "product_items", "product_groups", "resource_documents",
          "dossier_assessments", "dossier_packages"}


def dump(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def pointer(base, key):
    return base + "/" + str(key).replace("~", "~0").replace("/", "~1")


def project_to_entries(data: dict) -> list[dict]:
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("SOURCE_PROJECTION_RECORDS_REQUIRED")
    entries = []
    def add(value, path, group, kind, **extra):
        entry = {"uid": "view:" + str(len(entries)), "pointer": path,
                 "group": group, "kind": kind, **entry_values(value, group, kind),
                 "parent_uid": None, "raw_json": dump(value).decode("utf-8"), **extra}
        entries.append(entry)
        if len(entries) > 100000: raise ValueError("NATIVE_ENTRY_LIMIT")
        return entry
    # Exact skeleton retains empty collections, unknown scalars and nulls.
    skeleton = {key: [] if isinstance(value, list) else {} if isinstance(value, dict)
                else value for key, value in data.items()}
    add(skeleton, "", "$structure", "collection")
    for group, value in data.items():
        path = pointer("", group)
        if group == "lineage_graph" and isinstance(value, dict):
            graph = {k: [] if k in ("nodes", "edges") and isinstance(v, list) else v
                     for k, v in value.items()}
            add(graph, path, group, "collection")
            for collection in ("nodes", "edges"):
                if isinstance(value.get(collection), list):
                    for i, row in enumerate(value[collection]):
                        add(row, pointer(pointer(path, collection), i), group + "." + collection,
                            "node" if collection == "nodes" else "relation")
        elif group == "result_tables" and isinstance(value, list):
            for i, table in enumerate(value):
                if not isinstance(table, dict) or not isinstance(table.get("rows"), list):
                    raise ValueError("SOURCE_TABLE_INVALID")
                tp = pointer(path, i)
                head = {**table, "rows": []}
                te = add(head, tp, group, "table", row_count=len(table["rows"]))
                for n, row in enumerate(table["rows"]):
                    if not isinstance(row, dict) or not isinstance(row.get("cells"), dict):
                        raise ValueError("SOURCE_TABLE_CELLS_REQUIRED")
                    add(row, pointer(pointer(tp, "rows"), n), group, "row",
                        table_uid=te["uid"], ordinal=n)
        elif isinstance(value, list):
            kind = "record" if group == "records" else "relation" if group == "edges" else "asset" if group in ASSETS else "collection"
            for i, row in enumerate(value): add(row, pointer(path, i), group, kind)
        elif isinstance(value, dict):
            add(value, path, group, "collection")
    keys = defaultdict(list)
    for entry in entries:
        if entry["kind"] in ("record", "node") and entry["source_key"]:
            keys[(entry["group"], entry["source_key"])].append(entry["uid"])
    for entry in entries:
        candidates = keys.get((entry["group"], entry["parent_key"]), [])
        if entry["parent_key"]:
            entry["parent_resolution"] = "RESOLVED" if len(candidates) == 1 else "COLLISION" if candidates else "UNRESOLVED"
            if len(candidates) == 1: entry["parent_uid"] = candidates[0]
        else:
            entry["parent_resolution"] = "NOT_DECLARED"
    return entries


def build_package(data: dict, title: str = "Caderno — consulta nativa") -> tuple[dict, dict[str, bytes]]:
    from atlas_viewer.native_notebook import validate_entries, restore_projection
    entries = project_to_entries(data)
    validate_entries(entries)
    original = dump(data)
    if dump(restore_projection(entries)) != original:
        raise ValueError("NATIVE_ROUNDTRIP_MISMATCH")
    integration = data.get("atlas_integration", {})
    observed_revision = integration.get("notebook_revision") if isinstance(integration, dict) else None
    revision = observed_revision if isinstance(observed_revision, str) and observed_revision else "projection-sha256:" + hashlib.sha256(original).hexdigest()
    if len(revision) > 1024: raise ValueError("NATIVE_REVISION_LIMIT")
    payloads, pending, size = {}, [], 0
    def flush():
        nonlocal pending, size
        ordinal = len(payloads)
        raw = dump({"format": "atlas-native-view", "version": "1", "revision": revision,
                    "ordinal": ordinal, "entries": pending})
        if len(raw) > MAX_PAYLOAD_BYTES: raise ValueError("NATIVE_PAYLOAD_LIMIT")
        payloads[f"data/view-{ordinal:04d}.json"] = raw
        pending, size = [], 0
    for entry in entries:
        needed = len(dump(entry)) + 1
        if needed > MAX_PAYLOAD_BYTES - 4096: raise ValueError("NATIVE_SINGLE_ENTRY_TOO_LARGE")
        if pending and size + needed > MAX_PAYLOAD_BYTES - 4096: flush()
        pending.append(entry)
        size += needed
    if pending: flush()
    logical_bytes = sum(map(len, payloads.values()))
    if logical_bytes > MAX_NATIVE_LOGICAL_BYTES:
        raise ValueError("NATIVE_LOGICAL_LIMIT_NO_TRUNCATION")
    compressed_meta = {}
    if logical_bytes > MAX_EXPANDED_BYTES:
        # Only the optional presentation Files are compressed. No modifications
        # to the scientific protocol or its existing 32-MiB read budget.
        original_payloads = payloads
        payloads = {}
        for name, raw in original_payloads.items():
            path = name + ".zlib"
            zipped = zlib.compress(raw, level=6)
            payloads[path] = zipped
            compressed_meta[path] = {
                "rawSize": len(raw),
                "rawSha256": hashlib.sha256(raw).hexdigest(),
            }
        if sum(map(len, payloads.values())) > MAX_EXPANDED_BYTES:
            raise ValueError("NATIVE_COMPRESSED_AGGREGATE_LIMIT_NO_TRUNCATION")
    transport_version = "2" if compressed_meta else "1"
    ref = lambda eid: {"@id": eid}
    root = {"@id": "./", "@type": "Dataset", "name": title,
            "description": "Projeção de consulta derivada da API original; não concede aprovação científica.",
            "license": "Nenhuma licença adicional concedida; manter permissões das fontes.",
            "datePublished": datetime.now(timezone.utc).isoformat(),
            "conformsTo": [ref(PROCESS_PROFILE), ref(PROFILE_ID)],
            "hasPart": [ref(p) for p in payloads], "mentions": [],
            VIEW_NS + "version": transport_version, VIEW_NS + "revision": revision,
            VIEW_NS + "entryCount": len(entries), VIEW_NS + "projectionDigest": hashlib.sha256(original).hexdigest()}
    if compressed_meta:
        root[VIEW_NS + "logicalBytes"] = logical_bytes
    graph = [{"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": ref("./"), "conformsTo": ref(RO_CRATE)}, root,
             {"@id": PROCESS_PROFILE, "@type": ["CreativeWork", "http://www.w3.org/ns/dx/prof/Profile"], "name": "Process Run Crate", "version": "0.6"},
             {"@id": PROFILE_ID, "@type": ["CreativeWork", "http://www.w3.org/ns/dx/prof/Profile"], "name": "Caderno", "version": PROFILE_VERSION}]
    graph.extend(dict({"@id": path, "@type": "File", "name": "Apresentação nativa " + str(i),
                  "encodingFormat": COMPRESSED_MEDIA_TYPE if compressed_meta else MEDIA_TYPE,
                  "cp:availability": "PRESENT",
                  "cp:sha256": hashlib.sha256(raw).hexdigest(), "contentSize": len(raw)},
                 **({VIEW_NS + "rawSize": compressed_meta[path]["rawSize"],
                     VIEW_NS + "rawSha256": compressed_meta[path]["rawSha256"]}
                    if compressed_meta else {}))
                 for i, (path, raw) in enumerate(payloads.items()))
    document = {"@context": CONTEXT, "@graph": graph}
    report = validate_document(document)
    if not report.valid or len(dump(document)) > MAX_METADATA_BYTES:
        raise ValueError("EXPORTED_PROTOCOL_INVALID:" + ",".join(e.code for e in report.errors))
    return document, payloads


def safe_root(path: Path) -> Path:
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("SOURCE_REPARSE_UNSUPPORTED")
    return path.resolve(strict=True)



def _sync_directory(path: Path) -> None:
    """Flush directory entries on POSIX; Windows fsyncs each file."""
    if os.name == "posix":
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _publish_new_directory(staging: Path, destination: Path) -> None:
    """Atomic publish without replacing an existing directory on supported hosts."""
    if os.name == "nt":
        # Windows os.rename refuses an existing destination.
        os.rename(staging, destination)
    elif sys.platform.startswith("linux"):
        # Plain POSIX rename can replace an existing EMPTY directory. Linux's
        # RENAME_NOREPLACE makes a concurrent export fail without overwriting it.
        libc = ctypes.CDLL(None, use_errno=True)
        renameat2 = getattr(libc, "renameat2", None)
        if renameat2 is None:
            raise OSError(errno.ENOSYS, "ATOMIC_NOREPLACE_UNAVAILABLE")
        renameat2.argtypes = [
            ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        if renameat2(-100, os.fsencode(staging), -100,
                     os.fsencode(destination), 1) != 0:
            failure = ctypes.get_errno()
            raise OSError(failure, os.strerror(failure), str(destination))
    else:
        # Do not fall back to potentially overwriting a directory.
        raise OSError(errno.ENOSYS, "ATOMIC_NOREPLACE_UNAVAILABLE")


def export(data: dict, output: Path, *, forbidden_roots=()) -> dict:
    output = output.absolute()
    parent = safe_root(output.parent)
    destination = parent / output.name
    if destination.exists() or destination.is_symlink(): raise FileExistsError("OUTPUT_MUST_BE_NEW")
    for root in forbidden_roots:
        root = safe_root(Path(root))
        if destination == root or destination.is_relative_to(root) or root.is_relative_to(destination):
            raise ValueError("OUTPUT_MUST_BE_DISJOINT")
    document, payloads = build_package(data)
    # The final pathname must never describe a partially written package.
    # Keep failed staging for inspection; a retry can use the same final name.
    staging = Path(tempfile.mkdtemp(prefix=".atlas-native-staging-",
                                    dir=parent))
    (staging / "data").mkdir(mode=0o700)
    for name, raw in payloads.items():
        with (staging / name).open("xb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    with (staging / "ro-crate-metadata.json").open("xb") as stream:
        stream.write(dump(document)); stream.flush(); os.fsync(stream.fileno())
    _sync_directory(staging / "data")
    _sync_directory(staging)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("OUTPUT_MUST_BE_NEW")
    _publish_new_directory(staging, destination)
    # If parent directory fsync fails, the destination is already complete:
    # never delete, overwrite or silently claim durable publication.
    _sync_directory(parent)
    root = document["@graph"][1]
    return {"status": "EXPORTED", "output": str(destination),
            "revision": root[VIEW_NS + "revision"], "entries": root[VIEW_NS + "entryCount"],
            "projection_sha256": root[VIEW_NS + "projectionDigest"],
            "provider_calls": 0, "scientific_approval": "NOT_EVALUATED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--r4-code", type=Path, help="Checkout confiável com notebook_query_projection.project; não é carregado no viewer")
    source.add_argument("--projection", type=Path, help="JSON da projeção original já exportada, não HTML")
    parser.add_argument("--notebook-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        roots = []
        if args.r4_code:
            if args.notebook_root is None: parser.error("--notebook-root é obrigatório com --r4-code")
            code, notebook = safe_root(args.r4_code), safe_root(args.notebook_root)
            roots = [code, notebook]
            sys.path.insert(0, str(code / "src"))
            producer = importlib.import_module("r4.campaigns.notebook_query_projection")
            if not Path(producer.__file__).resolve().is_relative_to(code / "src"):
                raise ValueError("PRODUCER_MODULE_OUTSIDE_SELECTED_CODE")
            data = producer.project(notebook)
        else:
            source_file = safe_root(args.projection)
            roots = [source_file.parent]
            data = _strict_json(_regular_bytes(source_file, MAX_EXPANDED_BYTES))
        receipt = export(data, args.output, forbidden_roots=roots)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
