"""Authenticate an append-only view of the LOCAL inventory graph."""

from dataclasses import dataclass

from .contracts import DTO_KINDS, Identity, Source, digest, fields, relative_path, require, text, token


@dataclass(frozen=True)
class File:
    root: str
    path: tuple[str, ...]
    size: int
    sha256: str

    @classmethod
    def read(cls, value):
        fields(value, ("id", "root", "path", "bytes", "sha256"), (), "INVALID_INVENTORY_FILE")
        size = value["bytes"]
        require(token(value["id"]) and token(value["root"]) and digest(value["sha256"])
                and type(size) is int and 0 <= size < 2**63, "INVALID_INVENTORY_FILE")
        return cls(value["root"], relative_path(value["path"]), size, value["sha256"])


@dataclass(frozen=True)
class Binding:
    identity: Identity
    complete: bool
    evidence_scope: str
    files: frozenset[str]

    @classmethod
    def read(cls, value):
        fields(value, ("uid", "dto_kind", "raw_sha256", "coverage", "files",
                       "validation_status", "evidence_scope"),
               ("source_key", "table_rows_sha256"), "INVALID_INVENTORY_BINDING")
        uid, kind, raw = value["uid"], value["dto_kind"], value["raw_sha256"]
        key, rows = value.get("source_key"), value.get("table_rows_sha256")
        require(text(uid, 256) and kind in DTO_KINDS and digest(raw)
                and ("source_key" not in value or text(key, 65536)), "INVALID_INVENTORY_BINDING")
        require(digest(rows) if kind == "table" else "table_rows_sha256" not in value,
                "INVALID_INVENTORY_BINDING")
        ids = value["files"]
        require(isinstance(ids, list) and all(token(ref) for ref in ids) and len(set(ids)) == len(ids)
                and value["coverage"] in ("PARTIAL", "COMPLETE"), "INVALID_INVENTORY_BINDING")
        complete = value["coverage"] == "COMPLETE"
        scope = value["evidence_scope"]
        require(value["validation_status"] == "VERIFIED" and scope in ("PHYSICAL_BINDING", "DOCUMENTARY_WITNESS")
                and (not complete or scope == "PHYSICAL_BINDING"), "INVALID_BINDING_EVIDENCE")
        require(not complete or ids, "LINK_NOT_PROVEN")
        return cls(Identity(uid, kind, key, raw, rows), complete, scope, frozenset(ids))


@dataclass(frozen=True)
class Backup:
    copy: str
    independence_evidence: str | None
    restore_evidence: str | None


class Inventory:
    def __init__(self, source: Source):
        self.source = source
        self.parent = None
        self.complete = False
        self.segments = 0
        self.files = {}
        self.bindings = {}
        self.backups = {}
        self.paths = set()

    def append(self, document, sha256):
        fields(document, ("schema", "source", "parent_sha256", "provenance",
                          "dependency_scope", "files", "bindings", "backups"), (), "INVALID_INVENTORY")
        require(document["schema"] == "atlas-retention-inventory/1", "INVENTORY_SCHEMA_UNSUPPORTED")
        require(Source.read(document["source"]) == self.source, "SNAPSHOT_MISMATCH")
        require(document["parent_sha256"] == self.parent, "INVENTORY_PARENT_MISMATCH")
        provenance = fields(document["provenance"], ("producer", "evidence"), (), "INVALID_PROVENANCE")
        require(all(text(value, 1024) and value.strip() for value in provenance.values()), "INVALID_PROVENANCE")
        scope = document["dependency_scope"]
        require(scope in ("UNKNOWN", "COMPLETE"), "INVALID_DEPENDENCY_SCOPE")
        require(all(isinstance(document[key], list) for key in ("files", "bindings", "backups")),
                "INVALID_INVENTORY")
        require(not self.complete or (scope == "COMPLETE" and not document["bindings"]),
                "DEPENDENCY_SCOPE_SEALED")

        for value in document["files"]:
            file = File.read(value)
            file_id = value["id"]
            require(file_id not in self.files, "DUPLICATE_FILE_ID")
            folded = file.root, tuple(part.casefold() for part in file.path)
            require(folded not in self.paths, "FILE_ALIAS_COLLISION")
            self.paths.add(folded)
            self.files[file_id] = file

        seen = set()
        for value in document["bindings"]:
            binding = Binding.read(value)
            uid = binding.identity.uid
            require(uid not in seen, "DUPLICATE_UID")
            seen.add(uid)
            previous = self.bindings.get(uid)
            if previous is not None:
                require(not previous.complete and binding.identity == previous.identity
                        and (previous.evidence_scope == "DOCUMENTARY_WITNESS"
                             or binding.evidence_scope == previous.evidence_scope)
                        and previous.files <= binding.files and previous != binding,
                        "INVENTORY_BINDING_NOT_INCREMENTAL")
            require(binding.files <= self.files.keys(), "LINK_NOT_PROVEN")
            self.bindings[uid] = binding

        self.complete = scope == "COMPLETE"
        require(not self.complete or all(b.complete for b in self.bindings.values()),
                "INCOMPLETE_DEPENDENCY_SCOPE")
        primary = {ref for binding in self.bindings.values() for ref in binding.files}
        seen_backups = set()
        for value in document["backups"]:
            fields(value, ("primary", "copy"), ("independence_evidence", "restore_evidence"), "INVALID_BACKUP")
            origin, copy = value["primary"], value["copy"]
            require(token(origin) and token(copy) and origin in primary and copy in self.files
                    and origin not in seen_backups, "INVALID_BACKUP")
            seen_backups.add(origin)
            for key in value.keys() - {"primary", "copy"}:
                require(text(value[key], 1024) and value[key].strip(), "INVALID_BACKUP")
            first, second = self.files[origin], self.files[copy]
            require(first.root != second.root and (first.size, first.sha256) == (second.size, second.sha256),
                    "INVALID_BACKUP")
            previous = self.backups.get(origin)
            if previous is not None:
                require(copy == previous.copy, "BACKUP_NOT_INCREMENTAL")
                for key in ("independence_evidence", "restore_evidence"):
                    attestation = getattr(previous, key)
                    if attestation is not None:
                        require(value.get(key, attestation) == attestation, "BACKUP_NOT_INCREMENTAL")
                        value = {**value, key: attestation}
            backup = Backup(copy, value.get("independence_evidence"), value.get("restore_evidence"))
            require(backup != previous, "BACKUP_NOT_INCREMENTAL")
            self.backups[origin] = backup
        require(primary.isdisjoint(backup.copy for backup in self.backups.values()), "BACKUP_IS_PRIMARY")
        self.parent = sha256
        self.segments += 1

    def select(self, items):
        selected = {}
        for uid, item in items.items():
            binding = self.bindings.get(uid)
            require(binding is not None and binding.files, "LINK_NOT_PROVEN")
            expected = binding.identity
            actual = item.identity
            require((actual.kind, actual.source_key, actual.raw_sha256)
                    == (expected.kind, expected.source_key, expected.raw_sha256),
                    "INVENTORY_IDENTITY_MISMATCH")
            require(actual.table_rows_sha256 == expected.table_rows_sha256, "TABLE_ROWS_MISMATCH")
            selected[uid] = binding
        return selected
