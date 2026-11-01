"""Read the actual R4 Atlas v5 export as inert data, not a test-only source profile.

Adapted from the structural contract of the private R4 producer
`src/r4/campaigns/notebook_projection.py`, source revision
5c145615c8a1bd601351badddccaf3acea474ed2, with explicit owner
authorization for code transfer on 2026-10-31. No experiment data, legacy
runtime import, JS execution, document dereference or producer invocation.

The original exporter embeds JSON in <script id="data" type="application/json">
in a versioned index.html. Its ATLAS-ATUAL.html is ONLY a redirecting pointer.
This module does not chase pointer files, URLs or file paths.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .errors import ReaderError
from .parser import ParsedSource, parse_source

SCHEMA = "r4-experiment-viewer-v5"
AUTHORITY = "PRESENTATION_ONLY_NO_CLEANUP_AUTHORITY"
LINEAGE_SCHEMA = "r4-experiment-lineage-a10-v1"
REQUIRED_LISTS = (
    "records", "edges", "resources", "products", "result_tables",
    "frontiers", "sources", "source_crosswalk",
)
HISTORICAL_LISTS = (
    "product_items", "product_groups", "resource_documents",
    "storage_observations", "frontier_catalog", "external_runs",
    "coverage_ledger",
    "dossier_assessments", "dossier_packages",
)


def _require(ok: bool, code: str = "R4_V5_SOURCE_INVALID") -> None:
    if not ok:
        raise ReaderError(code)


def parse_legacy_export(raw: bytes, *, media_type: str = "text/html") -> ParsedSource:
    """Inert extraction of an already generated HTML/JSON snapshot.

    A single `script#data[type=application/json]` is required for HTML.
    Embedded application JS is treated as inert text and never executed.
    """
    parsed = parse_source(raw, media_type=media_type, source_profile="r4-v5")
    validate_legacy_projection(parsed.value)
    return parsed


def validate_legacy_projection(data: dict[str, Any]) -> None:
    """Validate R4 export invariants adapted from its original validator.

    This is structural validation of an exported *view*, not the scientific
    notebook, not authentication of an author, and not permission to access it.
    """
    _require(isinstance(data, dict) and data.get("schema") == SCHEMA
             and data.get("authority") == AUTHORITY, "SOURCE_FORMAT_UNSUPPORTED")
    for name in REQUIRED_LISTS:
        _require(isinstance(data.get(name), list), "R4_V5_REQUIRED_LIST:" + name)
    for name in HISTORICAL_LISTS:
        if name in data:
            _require(isinstance(data[name], list), "R4_V5_OPTIONAL_LIST:" + name)
    identifiers: dict[str, set[str]] = {}
    for name in ("records", "resources", "products", "result_tables", "frontiers"):
        rows = data[name]
        _require(len(rows) <= 100000, "QUOTA_EXCEEDED")
        _require(all(isinstance(row, dict) and isinstance(row.get("id"), str)
                     and bool(row["id"]) for row in rows), "R4_V5_IDENTIFIER:" + name)
        ids = [row["id"] for row in rows]
        _require(len(set(ids)) == len(ids), "R4_V5_DUPLICATE_ID:" + name)
        identifiers[name] = set(ids)
    _require(isinstance(data.get("coverage"), dict)
             and isinstance(data["coverage"].get("limits"), list),
             "R4_V5_COVERAGE_REQUIRED")
    for record in data["records"]:
        _require(all(isinstance(record.get(key), str)
                     for key in ("title", "family", "kind", "result", "retention")),
                 "R4_V5_RECORD_FIELDS")
        _require(isinstance(record.get("resources"), list)
                 and all(isinstance(item, str) for item in record["resources"])
                 and set(record["resources"]) <= identifiers["resources"],
                 "R4_V5_RESOURCE_REF")
    for edge in data["edges"]:
        _require(isinstance(edge, dict)
                 and edge.get("from") in identifiers["records"]
                 and edge.get("to") in identifiers["records"]
                 and isinstance(edge.get("type"), str)
                 and isinstance(edge.get("proofs"), list), "R4_V5_EDGE_INVALID")
    for table in data["result_tables"]:
        _require(isinstance(table.get("rows"), list), "R4_V5_TABLE_ROWS_REQUIRED")
        _require(len(table["rows"]) <= 100000, "QUOTA_EXCEEDED")
        for row in table["rows"]:
            _require(isinstance(row, dict), "R4_V5_ROW_INVALID")
            if row.get("cells") is not None:
                _require(isinstance(row["cells"], dict)
                         and all(isinstance(k, str) for k in row["cells"]),
                         "R4_V5_CELLS_INVALID")
    for product in data["products"]:
        _require(isinstance(product.get("run_id"), str)
                 and product.get("record_id") in identifiers["records"]
                 and product.get("pointer") in identifiers["resources"]
                 and isinstance(product.get("resources"), list)
                 and set(product["resources"]) <= identifiers["resources"],
                 "R4_V5_PRODUCT_REF")
    for item in data["source_crosswalk"]:
        _require(isinstance(item, dict)
                 and item.get("record_id") in identifiers["records"],
                 "R4_V5_CROSSWALK")
    graph = data.get("lineage_graph")
    if graph is not None:
        _require(isinstance(graph, dict)
                 and graph.get("schema") == LINEAGE_SCHEMA
                 and isinstance(graph.get("nodes"), list)
                 and isinstance(graph.get("edges"), list),
                 "R4_V5_LINEAGE_SCHEMA")
        _require(len(graph["nodes"]) <= 10000 and len(graph["edges"]) <= 100000,
                 "QUOTA_EXCEEDED")
        original_keys: set[str] = set()
        original_ui_ids: set[str] = set()
        for node in graph["nodes"]:
            _require(isinstance(node, dict), "R4_V5_LINEAGE_NODE")
            key, ui_id = node.get("key"), node.get("ui_id")
            _require(isinstance(ui_id, str) and ui_id
                     and isinstance(node.get("kind"), str),
                     "R4_V5_LINEAGE_ID")
            if key is not None:
                _require(isinstance(key, str) and key
                         and key not in original_keys, "R4_V5_LINEAGE_KEY")
                original_keys.add(key)
            _require(ui_id not in original_ui_ids, "R4_V5_LINEAGE_DUPLICATE_UI")
            original_ui_ids.add(ui_id)
            _require(node.get("native_id") is None
                     or isinstance(node["native_id"], str), "R4_V5_NATIVE_ID")
            _require(node.get("parent_key") is None
                     or isinstance(node["parent_key"], str), "R4_V5_PARENT_KEY")
        for edge in graph["edges"]:
            _require(isinstance(edge, dict)
                     and isinstance(edge.get("type"), str), "R4_V5_LINEAGE_EDGE")
            for key in ("from", "to", "from_key", "to_key"):
                _require(edge.get(key) is None or isinstance(edge[key], str),
                         "R4_V5_LINEAGE_ENDPOINT")


def inspect_legacy_projection(data: dict[str, Any]) -> dict[str, Any]:
    """Return a non-identifying structural summary, not a dataset.

    `records` and lineage graph nodes are DIFFERENT collections. This is the
    distinction lost by a synthetic-only adapter. Never infer total archive.
    """
    validate_legacy_projection(data)
    lineage = data.get("lineage_graph") or {}
    tables = data["result_tables"]
    counts = Counter(row.get("kind", "UNKNOWN") for row in lineage.get("nodes", ()))
    # No row values, source paths, native IDs, hashes or titles in the result.
    return {
        "format": SCHEMA,
        "records": len(data["records"]),
        "lineage_nodes": len(lineage.get("nodes", ())),
        "lineage_edges": len(lineage.get("edges", ())),
        "lineage_kinds": dict(sorted(counts.items())),
        "table_count": len(tables),
        "rows_per_table": [len(item["rows"]) for item in tables],
        "total_table_rows": sum(len(item["rows"]) for item in tables),
        "historical_collections": {
            name: len(data.get(name, ())) for name in HISTORICAL_LISTS
        },
        "global_history": "GLOBAL_UNPROVEN",
        "source_authority": "PRESENTATION_ONLY_NO_CLEANUP_AUTHORITY",
        "data_access": "ALREADY_EXPORTED_SNAPSHOT_ONLY",
        "scientific_approval": "NOT_EVALUATED",
    }


__all__ = ["SCHEMA", "AUTHORITY", "parse_legacy_export",
           "validate_legacy_projection", "inspect_legacy_projection"]
