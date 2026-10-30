"""Opt-in, disposable metadata presentation for the existing public read model.

This module performs no I/O. Its descriptor is a P03 presentation proposal, not
a persisted Caderno format, a validator for the protocol, or a payload reader.
"""
from __future__ import annotations

from typing import Any

MAX_ENTITIES = 10_000
MAX_ITEMS = 200
MAX_RELATIONS = 5_000
MAX_TEXT = 16_384
MAX_ID = 2_048
_DECLARED = {"PRESENT", "MISSING", "EXTERNAL", "UNKNOWN"}
_OBSERVED = {"UNVERIFIED", "AVAILABLE", "AVAILABLE_UNVERIFIED", "MISSING",
             "EXTERNAL_UNRESOLVED", "UNAVAILABLE", "INTEGRITY_MISMATCH",
             "READ_BUDGET_EXCEEDED", "UNSAFE_REFERENCE"}


class MetadataError(ValueError):
    """Predictable presentation-input error; ``code`` is stable for callers."""

    def __init__(self, code: str, path: str) -> None:
        self.code, self.path = code, path
        super().__init__(f"{code}: {path}")


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MetadataError("FIELD_TYPE", path)
    return value


def _text(value: Any, path: str, *, required: bool = False, limit: int = MAX_TEXT) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value):
        raise MetadataError("FIELD_TYPE", path)
    if len(value) > limit:
        raise MetadataError("LIMIT", path)
    return value


def _array(value: Any, path: str, limit: int) -> list[Any]:
    if not isinstance(value, list):
        raise MetadataError("FIELD_TYPE", path)
    if len(value) > limit:
        raise MetadataError("LIMIT", path)
    return value


def _digest(value: Any, path: str) -> str | None:
    value = _text(value, path)
    if value is not None and (len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
        raise MetadataError("DIGEST_FORMAT", path)
    return value


def _refs(value: Any, path: str) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    _array(values, path, MAX_RELATIONS)
    out: list[str] = []
    for index, ref in enumerate(values):
        item = _object(ref, f"{path}[{index}]")
        if set(item) != {"@id"}:
            raise MetadataError("REFERENCE_SHAPE", f"{path}[{index}]")
        eid = _text(item["@id"], f"{path}[{index}].@id", required=True, limit=MAX_ID)
        if eid not in out:
            out.append(eid)
    return out


def project_metadata(read_model: dict[str, Any], source_key: str, *,
                     entity_ids: list[str] | None = None) -> dict[str, Any]:
    """Return declared metadata and corroborated relations, without opening data.

    ``source_key`` is the integrator's opaque, stable snapshot identity. The
    default selection is File entities plus targets explicitly mentioned by
    CreateAction entities. ``entity_ids`` selects other declared entities.
    The exact identity remains the structured pair (source_key, @id).
    SDK availability observations are copied, never recomputed or promoted to
    authenticity. Missing values remain None; missing observations UNVERIFIED.
    """
    model = _object(read_model, "read_model")
    key = _text(source_key, "source_key", required=True, limit=MAX_ID)
    source = _object(model.get("source", {}), "source")
    entities: dict[str, dict[str, Any]] = {}
    entity_types: dict[str, list[str]] = {}
    for index, raw in enumerate(_array(model.get("entities", []), "entities", MAX_ENTITIES)):
        entity = _object(raw, f"entities[{index}]")
        eid = _text(entity.get("@id"), f"entities[{index}].@id", required=True, limit=MAX_ID)
        if eid in entities:
            raise MetadataError("DUPLICATE_ID", eid)
        raw_types = entity.get("@type", [])
        labels = [raw_types] if isinstance(raw_types, str) else _array(raw_types, f"{eid}.@type", 64)
        entity_types[eid] = [_text(label, f"{eid}.@type", required=True, limit=MAX_ID) for label in labels]
        entities[eid] = entity

    selected = [eid for eid in entities if "File" in entity_types[eid]]
    proven: list[tuple[str, str, str]] = []
    mentioned: list[tuple[str, str, str]] = []
    for eid, entity in entities.items():
        fields = [("prov:wasDerivedFrom", "derived_from"), ("mentions", "mention")]
        if "CreateAction" in entity_types[eid]:
            fields += [("object", "input"), ("result", "output")]
        for prop, kind in fields:
            for target in _refs(entity.get(prop), f"{eid}.{prop}"):
                if target not in entities:
                    raise MetadataError("UNRESOLVED_ENTITY", target)
                relation = (target, eid, kind) if kind == "input" else (eid, target, kind)
                bucket = mentioned if kind == "mention" else proven
                if relation not in bucket:
                    bucket.append(relation)
                if len(proven) + len(mentioned) > MAX_RELATIONS:
                    raise MetadataError("LIMIT", "relations")
                if kind == "mention" and "CreateAction" in entity_types[eid] and target not in selected:
                    selected.append(target)

    # A caller cannot inject an output relation that the preserved graph lacks.
    for index, raw in enumerate(_array(model.get("relations", []), "relations", MAX_RELATIONS)):
        relation = _object(raw, f"relations[{index}]")
        triple = tuple(_text(relation.get(k), f"relations[{index}].{k}", required=True, limit=MAX_ID)
                       for k in ("source", "target", "kind"))
        if triple not in proven:
            raise MetadataError("INCONSISTENT_READ_MODEL", f"relations[{index}]")

    observed: dict[str, dict[str, Any]] = {}

    def observe(raw: Any, path: str, *, artifact: bool = False) -> None:
        item = _object(raw, path)
        eid = _text(item.get("id"), f"{path}.id", required=True, limit=MAX_ID)
        if eid not in entities:
            raise MetadataError("UNRESOLVED_ENTITY", eid)
        if artifact and "File" not in entity_types[eid]:
            raise MetadataError("INCONSISTENT_READ_MODEL", path)
        availability = _object(item.get("availability", {}), f"{path}.availability")
        status = _text(availability.get("status", "UNVERIFIED"), f"{path}.availability.status", required=True)
        if status not in _OBSERVED:
            raise MetadataError("STATUS_VALUE", f"{path}.availability.status")
        actual = _digest(availability.get("sha256"), f"{path}.availability.sha256")
        entry = {"status": status, "sha256": actual}
        if "declared" in availability and availability["declared"] != entities[eid].get("cp:availability"):
            raise MetadataError("INCONSISTENT_READ_MODEL", f"{path}.availability.declared")
        if eid in observed and observed[eid] != entry:
            raise MetadataError("INCONSISTENT_READ_MODEL", path)
        if "declared_digest" in item and item["declared_digest"] != entities[eid].get("cp:sha256"):
            raise MetadataError("INCONSISTENT_READ_MODEL", f"{path}.declared_digest")
        observed[eid] = entry

    artifact_ids: set[str] = set()
    for index, artifact in enumerate(_array(model.get("artifacts", []), "artifacts", MAX_ENTITIES)):
        observe(artifact, f"artifacts[{index}]", artifact=True)
        eid = artifact["id"]
        if eid in artifact_ids:
            raise MetadataError("DUPLICATE_ID", f"artifacts[{index}].id")
        artifact_ids.add(eid)
    for index, run in enumerate(_array(model.get("runs", []), "runs", MAX_ENTITIES)):
        run = _object(run, f"runs[{index}]")
        rid = _text(run.get("id"), f"runs[{index}].id", required=True, limit=MAX_ID)
        if rid not in entities or "CreateAction" not in entity_types[rid]:
            raise MetadataError("INCONSISTENT_READ_MODEL", f"runs[{index}]")
        for rindex, ref in enumerate(_array(run.get("related_references", []), f"runs[{index}].related_references", MAX_ITEMS)):
            observe(ref, f"runs[{index}].related_references[{rindex}]")
            if (rid, ref["id"], "mention") not in mentioned:
                raise MetadataError("INCONSISTENT_READ_MODEL", f"runs[{index}].related_references[{rindex}]")

    if entity_ids is not None:
        selected = []
        for eid in _array(entity_ids, "entity_ids", MAX_ITEMS):
            eid = _text(eid, "entity_ids", required=True, limit=MAX_ID)
            if eid not in entities:
                raise MetadataError("UNRESOLVED_ENTITY", eid)
            if eid in selected:
                raise MetadataError("DUPLICATE_ID", "entity_ids")
            selected.append(eid)
    if len(selected) > MAX_ITEMS:
        raise MetadataError("LIMIT", "items")

    def identity(eid: str) -> dict[str, str]:
        return {"source_key": key, "id": eid}

    def relations_for(eid: str, relations: list[tuple[str, str, str]]) -> list[dict[str, Any]]:
        return [{"source": identity(a), "target": identity(b), "kind": kind}
                for a, b, kind in relations if eid in (a, b)]

    items = []
    for eid in selected:
        entity = entities[eid]
        declared = _text(entity.get("cp:availability"), f"{eid}.cp:availability")
        if declared is not None and declared not in _DECLARED:
            raise MetadataError("STATUS_VALUE", f"{eid}.cp:availability")
        current = observed.get(eid, {"status": "UNVERIFIED", "sha256": None})
        items.append({"identity": identity(eid), "kind": "artifact" if "File" in entity_types[eid] else "entity",
                      "name": _text(entity.get("name"), f"{eid}.name") or eid,
                      "types": list(entity_types[eid]),
                      "description": _text(entity.get("description"), f"{eid}.description"),
                      "media_type": _text(entity.get("encodingFormat"), f"{eid}.encodingFormat"),
                      "availability": {"declared": declared, "observed": current["status"]},
                      "digests": {"declared_sha256": _digest(entity.get("cp:sha256"), f"{eid}.cp:sha256"),
                                  "calculated_sha256": current["sha256"]},
                      "relations": relations_for(eid, proven), "mentions": relations_for(eid, mentioned)})
    source_digest = source.get("metadata_sha256")
    return {"version": "p03-metadata/1", "semantic_status": "DERIVED_CURRENT_CONTRACT",
            "source": {"key": key, "name": _text(source.get("name"), "source.name"),
                       "metadata_sha256": _digest(None if source_digest == "" else source_digest, "source.metadata_sha256")},
            "items": items}
