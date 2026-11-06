"""Verify the native-retention.js export without reserializing original DTOs."""

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .contracts import (
    DTO_KINDS, Identity, Rejected, Source, compact, fields, lexical_sha, reject_constant,
    require, text, unique_pairs,
)

INTENTS = ("KEEP_FULL", "KEEP_ESSENTIALS", "REVIEW_FOR_REMOVAL", "UNDECIDED")
WHITESPACE = re.compile(r"[ \t\r\n]*")


class NumberLexeme(str):
    """Distinguishes a JSON number token from a JSON string of digits."""


DECODER = json.JSONDecoder(object_pairs_hook=unique_pairs, parse_int=NumberLexeme,
                           parse_float=NumberLexeme, parse_constant=reject_constant)
JSON_TYPES = {str: "string", bool: "boolean", dict: "object", list: "array", type(None): "null"}


@dataclass(frozen=True)
class Item:
    identity: Identity
    intent: str
    baseline: bool


def dto_fragments(raw):
    require(type(raw) is str and raw, "INVALID_DTO_JSON")
    try:
        value = DECODER.decode(raw)
        if not isinstance(value, dict):
            return {}, {}
        fragments = {}
        pos = WHITESPACE.match(raw).end() + 1
        for key in value:
            _, end = DECODER.raw_decode(raw, WHITESPACE.match(raw, pos).end())
            start = WHITESPACE.match(raw, WHITESPACE.match(raw, end).end() + 1).end()
            _, end = DECODER.raw_decode(raw, start)
            fragments[key] = raw[start:end]
            pos = WHITESPACE.match(raw, end).end() + 1
        return value, fragments
    except Rejected:
        raise
    except (ValueError, RecursionError):
        raise Rejected("INVALID_DTO_JSON") from None


def verify_literal(identity, slot, name, value, fragments):
    if name is None:
        require(slot not in identity, "ORIGINAL_IDENTITY_MISMATCH")
        return
    actual = fields(identity.get(slot), ("field", "type", "raw_json", "display"), (),
                    "ORIGINAL_IDENTITY_MISMATCH")
    if isinstance(value, NumberLexeme):
        kind = "number" if any(char in value for char in ".eE") else "integer"
    else:
        kind = JSON_TYPES[type(value)]
    require(actual["field"] == name and actual["type"] == kind
            and actual["raw_json"] == fragments[name] and type(actual["display"]) is str,
            "ORIGINAL_IDENTITY_MISMATCH")


def verify_identity(identity, source, snapshot, values, fragments):
    fields(identity, ("selection_key", "source_id", "source_revision", "source_metadata_sha256",
                      "uid", "dto_kind"), ("source_key", "original_id", "record_kind"),
           "INVALID_SELECTION")
    uid, kind = identity["uid"], identity["dto_kind"]
    require(text(uid, 256) and kind in DTO_KINDS, "INVALID_SELECTION")
    require((identity["source_id"], identity["source_revision"], identity["source_metadata_sha256"])
            == (source.id, source.revision, source.metadata_sha256), "SELECTION_SOURCE_MISMATCH")
    record_kind = "kind" if kind == "record" and "kind" in fragments else None
    kind_fragment = [True, fragments[record_kind]] if record_kind is not None else [False]
    require(identity["selection_key"] == compact(["atlas-selection/1", snapshot, uid, kind, kind_fragment]),
            "SELECTION_KEY_MISMATCH")
    key = next((values[name] for name in ("key", "id")
                if type(values.get(name)) is str and values[name]), None)
    require(identity.get("source_key") == key and ("source_key" in identity) == (key is not None),
            "ORIGINAL_IDENTITY_MISMATCH")
    original = next((name for name in ("native_id", "id") if name in fragments), None)
    verify_literal(identity, "original_id", original, values.get(original), fragments)
    verify_literal(identity, "record_kind", record_kind, values.get(record_kind), fragments)
    return uid, kind, key


def verify_baseline(item, snapshot, identity, values, fragments):
    baseline = item.get("baseline")
    require(isinstance(baseline, dict), "BASELINE_MISMATCH")
    names = [name for name in ("baseline", "is_baseline") if name in fragments]
    flags = [values[name] for name in names]
    if type(values.get("kind")) is str and values["kind"] == "baseline":
        names.append("kind")
        flags.append(True)
    positive = any(value is True for value in flags)
    conflict = positive and any(value is False for value in flags)
    source_confirmed = positive and not conflict
    operator = baseline.get("operatorDesignated")
    require(type(operator) is bool and ("annotation" in baseline) == operator, "BASELINE_MISMATCH")
    if operator:
        annotation = baseline["annotation"]
        require(isinstance(annotation, dict) and all(annotation.get(key) == value for key, value in {
            "schema": "atlas-baseline-annotation/1", "origin": "OPERATOR_SESSION",
            "selection_key": identity["selection_key"], "snapshot_key": snapshot,
            "uid": identity["uid"], "dto_kind": identity["dto_kind"],
        }.items()) and type(annotation.get("note")) is str and annotation["note"].strip(),
            "BASELINE_MISMATCH")
    status = "NOT_DECLARED"
    if names:
        status = "UNCONFIRMED"
    if operator:
        status = "OPERATOR_SESSION"
    if source_confirmed:
        status = "SOURCE_DECLARED"
    if conflict:
        status = "CONFLICT"
    require(baseline.get("declarations") == [{"field": name, "raw_json": fragments[name]} for name in names]
            and baseline.get("status") == status and baseline.get("sourceConfirmed") is source_confirmed
            and baseline.get("conflict") is conflict
            and baseline.get("confirmed") is ((positive or operator) and not conflict), "BASELINE_MISMATCH")
    return positive or operator


def verify_table(item, kind, rows_by_uid):
    if kind != "table":
        require("table_rows" not in item, "INVALID_TABLE_ROWS")
        return None
    table = fields(item.get("table_rows"), ("status", "transport_skeleton", "count", "rows"), (),
                   "INVALID_TABLE_ROWS")
    rows = table["rows"]
    require(table["status"] == "COMPLETE_FOR_SNAPSHOT" and table["transport_skeleton"] is True
            and isinstance(rows, list) and type(table["count"]) is int and table["count"] == len(rows),
            "INVALID_TABLE_ROWS")
    ordered = []
    for ordinal, row in enumerate(rows):
        fields(row, ("uid", "ordinal", "raw_json"), (), "INVALID_TABLE_ROWS")
        uid, raw = row["uid"], row["raw_json"]
        require(text(uid, 256) and type(row["ordinal"]) is int and row["ordinal"] == ordinal,
                "INVALID_TABLE_ROWS")
        require(uid not in rows_by_uid, "DUPLICATE_ROW_UID")
        dto_fragments(raw)
        rows_by_uid[uid] = lexical_sha(raw)
        ordered.append([uid, ordinal, raw])
    return sha256(compact(ordered).encode("utf-8")).hexdigest()


def read_plan(document):
    fields(document, ("schema", "version", "status", "DELETE_AUTHORIZED", "source", "snapshot_key",
                      "selection", "items", "space_estimate", "provenance"),
           ("pending_verifications",), "INVALID_PLAN")
    require(document["schema"] == "atlas-retention-plan/1" and type(document["version"]) is int
            and document["version"] == 1, "PLAN_SCHEMA_UNSUPPORTED")
    provenance = document["provenance"]
    space = document["space_estimate"]
    require(document["status"] == "PROPOSAL_ONLY" and document["DELETE_AUTHORIZED"] == "NO"
            and isinstance(provenance, dict) and provenance.get("mode") == "DERIVED_SESSION_PROPOSAL"
            and provenance.get("source_read_only") is True
            and provenance.get("physical_presence_verified") is False
            and provenance.get("operator_intentions_are_commands") is False
            and provenance.get("scientific_acceptance") == "NOT_ASSERTED"
            and isinstance(space, dict) and space.get("status") == "NOT_MEASURED"
            and space.keys() <= {"status", "label"}, "PLAN_NOT_PROPOSAL_ONLY")
    source = Source.read(document["source"], plan=True)
    snapshot = source.snapshot_key
    require(document["snapshot_key"] == snapshot, "SNAPSHOT_KEY_MISMATCH")
    selection, exported = document["selection"], document["items"]
    require(isinstance(selection, list) and isinstance(exported, list)
            and 0 < len(selection) == len(exported) <= 100_000, "INVALID_SELECTION")
    result = {}
    rows_by_uid = {}
    for identity, item in zip(selection, exported, strict=True):
        fields(item, ("identity", "raw_json", "intent", "protection", "baseline"),
               ("title", "type", "type_label", "execution", "declared", "gaps", "pending_verifications",
                "table_rows"), "INVALID_PLAN_ITEM")
        require(isinstance(identity, dict) and item["identity"] == identity, "SELECTION_ITEM_MISMATCH")
        intent = item["intent"]
        protection = item["protection"]
        require(intent in INTENTS, "INVALID_INTENT")
        require(isinstance(protection, dict) and protection.get("status") == "PROTECTED"
                and protection.get("removal_authorized") is False, "PLAN_NOT_PROPOSAL_ONLY")
        raw = item["raw_json"]
        values, fragments = dto_fragments(raw)
        uid, kind, key = verify_identity(identity, source, snapshot, values, fragments)
        require(uid not in result, "DUPLICATE_UID")
        baseline = verify_baseline(item, snapshot, identity, values, fragments)
        table_digest = verify_table(item, kind, rows_by_uid)
        result[uid] = Item(Identity(uid, kind, key, lexical_sha(raw), table_digest), intent, baseline)
    for uid in rows_by_uid.keys() & result.keys():
        identity = result[uid].identity
        require(identity.kind == "row" and identity.raw_sha256 == rows_by_uid[uid], "TABLE_ROWS_MISMATCH")
    return source, result
