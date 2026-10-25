"""Disposable presentation projection; the RO-Crate remains the source."""
from __future__ import annotations
from copy import deepcopy
from typing import Any

from .model import Package, PROFILE_ID, refs, types


def to_read_model(package: Package) -> dict[str, Any]:
    graph = package.document.get("@graph", [])
    if not isinstance(graph, list):
        graph = []
    entities = {e["@id"]: e for e in graph if isinstance(e, dict) and isinstance(e.get("@id"), str)}
    root = entities.get("./", {})
    def first(value: Any) -> str | None:
        ids = refs(value)
        return ids[0] if ids else None
    def properties(value: Any) -> list[dict[str, Any]]:
        out = []
        for eid in refs(value):
            e = entities.get(eid, {})
            out.append({"id": eid, "name": e.get("name", eid), "property_id": e.get("propertyID"),
                        "value": e.get("value"), "type": e.get("cp:valueType"),
                        "unit": e.get("unitText"), "precision": e.get("cp:precision"),
                        "missing_reason": e.get("cp:missingReason")})
        return out
    def related_references(value: Any) -> list[dict[str, Any]]:
        # Identity is local to this Package. A mention carries no input, output,
        # derivation, authenticity or approval claim. Keep its first occurrence.
        out = []
        for eid in dict.fromkeys(refs(value)):
            e = entities.get(eid, {})
            name, description = e.get("name"), e.get("description")
            out.append({"id": eid, "name": name if isinstance(name, str) and name else eid,
                        "types": types(e),
                        "description": description if isinstance(description, str) else "",
                        "declared_digest": deepcopy(e.get("cp:sha256")),
                        "availability": deepcopy(package.payload_status.get(eid, {"status": "UNVERIFIED"}))})
        return out
    projects = [{"id": eid, "name": e.get("name", eid), "description": e.get("description", "")}
                for eid, e in entities.items() if "cp:Project" in types(e)]
    experiments = [{"id": eid, "name": e.get("name", eid), "description": e.get("description", ""),
                    "project_id": first(e.get("isPartOf"))}
                   for eid, e in entities.items() if "cp:Experiment" in types(e)]
    experiment_by_id = {e["id"]: e for e in experiments}
    artifacts = [{"id": eid, "name": e.get("name", eid), "media_type": e.get("encodingFormat"),
                  "declared_digest": e.get("cp:sha256"), "availability": deepcopy(package.payload_status.get(eid, {"status": "UNVERIFIED"})),
                  "description": e.get("description", "")}
                 for eid, e in entities.items() if "File" in types(e)]
    artifact_by_id = {e["id"]: e for e in artifacts}
    runs = []
    relations = []
    for eid, e in entities.items():
        for parent in refs(e.get("prov:wasDerivedFrom")):
            relations.append({"source": eid, "target": parent, "kind": "derived_from"})
        if "CreateAction" not in types(e):
            continue
        exp = first(e.get("cp:experiment"))
        inputs, outputs = refs(e.get("object")), refs(e.get("result"))
        for ref in inputs:
            relations.append({"source": ref, "target": eid, "kind": "input"})
        for ref in outputs:
            relations.append({"source": eid, "target": ref, "kind": "output"})
        runs.append({"id": eid, "name": e.get("name", eid), "description": e.get("description", ""),
                     "project_id": experiment_by_id.get(exp, {}).get("project_id"), "experiment_id": exp,
                     "status": e.get("cp:executionStatus", "UNKNOWN"), "review_status": e.get("cp:reviewStatus", "UNKNOWN"),
                     "synthetic": e.get("cp:synthetic"), "timestamp_origin": e.get("cp:timestampOrigin", "UNKNOWN"),
                     "started_at": e.get("startTime"), "ended_at": e.get("endTime"),
                     "metrics": properties(e.get("cp:metrics")), "parameters": properties(e.get("cp:parameters")),
                     "inputs": inputs, "outputs": outputs,
                     "related_references": related_references(e.get("mentions")),
                     "artifacts": [artifact_by_id[x] for x in inputs + outputs if x in artifact_by_id],
                     "agent_id": first(e.get("agent")), "instrument_id": first(e.get("instrument")),
                     "derived_from": refs(e.get("prov:wasDerivedFrom"))})
    return {"source": {"name": root.get("name", package.source_name), "description": root.get("description", ""),
                       "metadata_sha256": package.metadata_sha256, "profiles": refs(root.get("conformsTo")),
                       "candidate_profile": PROFILE_ID, "validation": package.report.to_dict(),
                       "date_published": root.get("datePublished"), "source_name": package.source_name},
            "projects": projects, "experiments": experiments, "runs": runs, "artifacts": artifacts,
            "relations": relations, "entities": deepcopy(list(entities.values())),
            "authority": "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL"}
