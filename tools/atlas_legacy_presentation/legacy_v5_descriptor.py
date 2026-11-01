"""Project already-exported R4 v5 data into the approved 0.2.0 VIEW descriptor.

Uses the *actual* `r4-experiment-viewer-v5` and typed A10 lineage fields;
there is no invented input schema and no invocation of R4 or source discovery.

The native graph `key`, derived `ui_id`, and scientific `native_id` are
distinct in R4. The approved v0.2.0 reference shape can resolve by native_id
only. Where a declared source key is not a proven native ID we preserve the
literal key and an explicit gap, NEVER forge a native_id or scientific link.

Adapted with explicit authorization from the R4 code contract at
5c145615c8a1bd601351badddccaf3acea474ed2 (2026-10-31).
Only synthetic-v5-shaped *test values* may enter the public repository.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import uuid

from .errors import ReaderError
from .parser import ParsedSource, _cell, pointer, MISSING
from .legacy_v5 import validate_legacy_projection

_KINDS = {
    "ExperimentFamily": "Family", "Run": "Run", "Execution": "Run",
    "Experiment": "Experiment", "Family": "Family", "Project": "Project",
    "run": "Run", "experiment": "Experiment",
}
_ASSETS = (
    ("resources", "File"), ("products", "Product"),
    ("product_items", "Product"), ("product_groups", "ProductGroup"),
    ("resource_documents", "ResourceDocument"),
    ("dossier_assessments", "DossierAssessment"),
    ("dossier_packages", "DossierPackage"),
)
_EXTRA_ROOT_COLLECTIONS = (
    "sources", "source_crosswalk", "frontiers", "storage_observations",
    "frontier_catalog", "external_runs", "coverage_ledger",
    "source_roots_coverage", "dossier_batch", "historical_coverage",
)


def _fail(reason):
    raise ReaderError(reason)


def _text(value):
    return value if isinstance(value, str) and value else None


class _Builder:
    def __init__(self, parsed, source_id, snapshot_id):
        self.parsed = parsed
        self.source_id = source_id
        self.snapshot_id = snapshot_id
        self.session = uuid.uuid4().hex
        self.sequence = 0
        self.counter = Counter()
        self.nodes = []
        self.tables = []
        self.assets = []
        self.relations = []
        self.unmapped = []
        self.gaps = Counter()
        self.targets = []
        self.pending = []
        self.graph_keys = {}

    def identity(self, original, locator):
        native = _text(original)
        if original is not None and native is None:
            _fail("R4_V5_NATIVE_ID_INVALID")
        ordinal = self.counter[native] if native is not None else 0
        if native is not None:
            self.counter[native] += 1
        self.sequence += 1
        ident = {
            "native_id": native,
            "navigation_id": f"nav:{self.session}:{self.sequence}",
            "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
            "occurrence": ordinal,
            "locator": locator,
        }
        return ident

    def preserve(self, row, locator, owner, consumed=()):
        """Preserve unrendered source fields as typed original lexemes."""
        for key, value in row.items():
            if key in consumed:
                continue
            path = pointer(locator, key)
            self.unmapped.append({
                "owner_navigation_id": owner,
                "locator": path,
                "source_key_literal": key,
                "value": _cell(self.parsed, path, value),
            })

    def gap(self, code, number=1):
        self.gaps[code] += number

    def add_node(self, raw, loc, *, lineage=False):
        if not isinstance(raw, dict):
            _fail("R4_V5_NODE_INVALID")
        if lineage:
            original = raw.get("native_id")
            kind = raw.get("kind")
            label = raw.get("label")
            parent_key = raw.get("parent_key")
        else:
            original = raw.get("id")
            kind = raw.get("kind")
            label = raw.get("title")
            parent_key = raw.get("parent_key")
        if not isinstance(kind, str) or not isinstance(label, str) or not label:
            _fail("R4_V5_NODE_INVALID")
        if parent_key is not None and not isinstance(parent_key, str):
            _fail("R4_V5_PARENT_INVALID")
        ident = self.identity(original, loc)
        node = {
            "identity": ident, "kind": _KINDS.get(kind, "Other"),
            "original_type": kind, "entity_status": "SOURCE_ENTITY",
            "label_literal": label,
            "family_literal": raw.get("family") if isinstance(raw.get("family"), str) else None,
            "parent_key_literal": parent_key,
            "parent": None, "tree_state": "PARENT_UNKNOWN",
            "external_reference": None, "binding_gap": True,
        }
        self.nodes.append(node)
        self.targets.append(node)
        self.pending.append(("parent", node, parent_key, loc, lineage, raw.get("root") is True))
        if lineage:
            key = raw.get("key")
            if key is not None:
                if not isinstance(key, str) or not key or key in self.graph_keys:
                    _fail("R4_V5_LINEAGE_KEY_INVALID")
                self.graph_keys[key] = node
        self.preserve(raw, loc, ident["navigation_id"],
                      ("native_id", "kind", "label", "family", "parent_key")
                      if lineage else ("id", "kind", "title", "family", "parent_key"))
        return node

    def add_table(self, raw, loc):
        if not isinstance(raw, dict) or not isinstance(raw.get("rows"), list):
            _fail("R4_V5_TABLE_INVALID")
        ident = self.identity(raw["id"], loc)
        table = {
            "identity": ident, "title_literal": _text(raw.get("label")) or _text(raw["id"]),
            "domain": "RF" if raw.get("role") in ("UNADMITTED_NATIVE_RF", "NATIVE_RF_SOURCE_PRESENTATION") else "UNKNOWN",
            "domain_origin": "DECLARED" if raw.get("role") in ("UNADMITTED_NATIVE_RF", "NATIVE_RF_SOURCE_PRESENTATION") else "UNKNOWN",
            "record_binding": None, "columns": [], "rows": [],
        }
        # Original R4 row.cells is a mapping, not the invented list input.
        keys = []
        for row in raw["rows"]:
            if not isinstance(row, dict) or not isinstance(row.get("cells"), dict):
                _fail("R4_V5_ROW_CELLS_REQUIRED")
            for key in row["cells"]:
                if not isinstance(key, str):
                    _fail("R4_V5_COLUMN_KEY")
                if key not in keys:
                    keys.append(key)
        if len(keys) > 256:
            _fail("QUOTA_EXCEEDED")
        table["columns"] = [
            {"ordinal": i, "native_key": key, "header_literal": key or "(empty header)"}
            for i, key in enumerate(keys)
        ]
        position = {key: i for i, key in enumerate(keys)}
        for ordinal, rawrow in enumerate(raw["rows"]):
            path = pointer(pointer(loc, "rows"), ordinal)
            native = rawrow.get("native_id")
            rid = self.identity(native, path)
            cells = rawrow["cells"]
            rendered = [
                _cell(self.parsed, pointer(pointer(path, "cells"), key),
                      cells[key]) if key in cells else
                _cell(self.parsed, pointer(pointer(path, "cells"), key), MISSING)
                for key in keys
            ]
            requirement = None
            if table["domain"] == "RF":
                fields = {
                    "id": position.get("ID"),
                    "module": position.get("Núcleo / Módulo"),
                    "title": position.get("Nome"),
                    "description": position.get("Descrição"),
                    "acceptance_criteria": position.get("Critérios de Aceitação",
                                                       position.get("Critérios de aceite")),
                    "category": position.get("Categoria"),
                }
                is_unadmitted = raw.get("role") == "UNADMITTED_NATIVE_RF"
                if is_unadmitted and native is not None:
                    _fail("R4_V5_UNADMITTED_NATIVE_CONFLICT")
                admission = ("UNADMITTED_NATIVE_RF" if is_unadmitted
                             else "ADMITTED_NATIVE_RF" if native is not None
                             else "NOT_EVALUATED")
                cat = fields["category"]
                category_status = ("MISSING" if cat is None or
                                   rendered[cat]["type"] in ("missing", "null") else "PRESENT")
                requirement = {
                    "kind": "RF", "native_id": native,
                    "admission": admission,
                    "admission_evidence_locator": path if native is not None else None,
                    "fields": fields, "category_status": category_status,
                }
            item = {
                "identity": rid, "ordinal": ordinal, "cells": rendered,
                "requirement": requirement, "run_binding": None, "binding_gap": True,
            }
            table["rows"].append(item)
            self.targets.append(item)
            self.pending.append(("run_binding", item, rawrow.get("run_id", raw.get("run_id")),
                                 path, False, False))
            self.preserve(rawrow, path, rid["navigation_id"],
                          ("cells", "native_id", "run_id"))
        self.tables.append(table)
        self.targets.append(table)
        self.pending.append(("record_binding", table, raw.get("record_id"), loc, False, False))
        self.preserve(raw, loc, ident["navigation_id"],
                      ("id", "label", "rows", "record_id", "role"))
        return table

    def add_asset(self, raw, loc, category):
        if not isinstance(raw, dict):
            _fail("R4_V5_ASSET_INVALID")
        ident = self.identity(raw.get("id"), loc)
        label = (raw.get("label") or raw.get("name") or raw.get("title")
                 or raw.get("id") or category)
        if not isinstance(label, str) or not label:
            _fail("R4_V5_ASSET_LABEL")
        original_type = raw.get("kind", category)
        if not isinstance(original_type, str):
            _fail("R4_V5_ASSET_KIND")
        binding = (raw.get("atlas_record_id") or raw.get("record_id")
                   or raw.get("binding_id"))
        role = raw.get("product_role") if isinstance(raw.get("product_role"), str) else None
        kind = category
        if category == "Product" and (not role or binding is None):
            kind = "Other"  # No promotion of unbound assets to products.
            self.gap("PRODUCT_ROLE_OR_BINDING_UNVERIFIED")
        if original_type == "File":
            kind = "File"
        asset = {
            "identity": ident, "kind": kind, "original_type": original_type,
            "label_literal": label, "declared_product_role": role,
            "declared_binding": None,
            "media_type_literal": raw.get("media_type") if isinstance(raw.get("media_type"), str) else None,
            "uri_literal": raw.get("uri") if isinstance(raw.get("uri"), str) else None,
            "availability": "DECLARED_ONLY", "opened": False,
        }
        self.assets.append(asset)
        self.targets.append(asset)
        self.pending.append(("declared_binding", asset, binding, loc, False, False))
        self.preserve(raw, loc, ident["navigation_id"],
                      ("id", "kind", "label", "name", "title", "product_role",
                       "record_id", "atlas_record_id", "binding_id", "media_type", "uri"))
        return asset

    def ref(self, declared, path):
        if declared is not None and (not isinstance(declared, str) or not declared):
            _fail("R4_V5_REFERENCE_INVALID")
        if declared is None:
            state, target = "NULL_ENDPOINT", None
        else:
            matches = self.by_native.get(declared, [])
            state = ("RESOLVED" if len(matches) == 1 else
                     "COLLISION" if len(matches) > 1 else "UNRESOLVED")
            target = matches[0]["identity"]["navigation_id"] if state == "RESOLVED" else None
        return {
            "source_id": self.source_id, "snapshot_id": self.snapshot_id,
            "declared_id": declared, "target_navigation_id": target,
            "resolution": state, "evidence_locator": path,
        }

    def resolve(self):
        self.by_native = defaultdict(list)
        for item in self.targets:
            if item["identity"]["native_id"] is not None:
                self.by_native[item["identity"]["native_id"]].append(item)
        for name, obj, declared, loc, lineage, root in self.pending:
            ref = self.ref(declared, pointer(loc, "parent_key") if name == "parent"
                           else pointer(loc, "record_id") if name == "record_binding"
                           else pointer(loc, "run_id") if name == "run_binding"
                           else pointer(loc, "binding_id"))
            if name == "parent":
                obj[name] = ref
                if lineage and declared in self.graph_keys:
                    ancestor = self.graph_keys[declared]
                    if ancestor["identity"]["native_id"] != declared:
                        if self.by_native.get(declared):
                            _fail("R4_V5_PARENT_SCOPE_UNREPRESENTABLE")
                        self.gap("SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE")
                if ref["resolution"] == "RESOLVED":
                    candidate = self.by_native[declared][0]
                    if candidate not in self.nodes:
                        _fail("R4_V5_PARENT_SCOPE_UNREPRESENTABLE")
                    obj["tree_state"] = "PARENT_RESOLVED"
                    obj["binding_gap"] = False
                elif root and declared is None:
                    obj["tree_state"] = "ROOT_DECLARED"
                    obj["binding_gap"] = False
                elif obj["kind"] == "Run":
                    obj["tree_state"] = "RUN_EXTERNAL_ISOLATED"
                elif declared is not None:
                    obj["tree_state"] = "ORPHAN"
            else:
                obj[name] = ref
                if name == "run_binding":
                    if ref["resolution"] == "RESOLVED":
                        candidate = self.by_native[declared][0]
                        if candidate.get("kind") != "Run":
                            _fail("R4_V5_RUN_BINDING_UNREPRESENTABLE")
                    obj["binding_gap"] = ref["resolution"] != "RESOLVED"
        # Cycle members must be accounted for by the exact descriptor contract.
        by_nav = {n["identity"]["navigation_id"]: n for n in self.nodes}
        done, cycles = set(), set()
        for start in by_nav:
            seen, chain, current = {}, [], start
            while current in by_nav and current not in done:
                if current in seen:
                    cycles.update(chain[seen[current]:])
                    break
                seen[current] = len(chain)
                chain.append(current)
                p = by_nav[current]["parent"]
                current = p["target_navigation_id"] if p["resolution"] == "RESOLVED" else None
            done.update(chain)
        if cycles:
            self.gap("TREE_CYCLE", len(cycles))
            for nav in cycles:
                by_nav[nav]["binding_gap"] = True

    def add_relation(self, raw, loc, *, graph=False):
        if not isinstance(raw, dict):
            _fail("R4_V5_EDGE_INVALID")
        rid = self.identity(raw.get("id"), loc)
        kind = raw.get("type")
        if not isinstance(kind, str):
            _fail("R4_V5_EDGE_INVALID")
        if graph:
            left = raw.get("from_key", raw.get("from"))
            right = raw.get("to_key", raw.get("to"))
            causal = raw.get("causal_status") == "VERIFIED_DECLARED_PROVENANCE"
            semantics = ("ORGANIZATIONAL_MEMBERSHIP" if kind == "MEMBER_OF" else
                         "DECLARED_LINEAGE" if causal else "UNKNOWN")
        else:
            left, right = raw.get("from"), raw.get("to")
            semantics = ("DECLARED_LINEAGE" if kind in
                         ("DERIVED_FROM", "INPUT_FROM", "PREDECESSOR") and
                         bool(raw.get("proofs")) else "NEUTRAL_MENTION")
        from_ref = self.ref(left, pointer(loc, "from_key" if graph and "from_key" in raw else "from"))
        to_ref = self.ref(right, pointer(loc, "to_key" if graph and "to_key" in raw else "to"))
        issues = []
        if from_ref["resolution"] != "RESOLVED" or to_ref["resolution"] != "RESOLVED":
            issues.append("DECLARED_SOURCE_ENDPOINT_NOT_NATIVE_RESOLVED")
            self.gap("DECLARED_RELATION_UNRESOLVED")
        item = {
            "identity": rid, "kind_literal": kind, "semantics": semantics,
            "direction": "FROM_TO" if left is not None and right is not None else "UNKNOWN",
            "from": from_ref, "to": to_ref, "evidence_locator": loc,
            "issues": issues, "repeat_group": None, "repeat_occurrence": 1,
            "binding_gap": bool(issues),
        }
        self.relations.append(item)
        self.preserve(raw, loc, rid["navigation_id"],
                      ("id", "type", "from", "to", "from_key", "to_key"))
        return item

    def finalize_relations(self):
        groups = defaultdict(list)
        for e in self.relations:
            sig = (
                e["kind_literal"], e["semantics"], e["direction"],
                e["from"]["source_id"], e["from"]["snapshot_id"],
                e["from"]["declared_id"], e["from"]["resolution"],
                e["to"]["source_id"], e["to"]["snapshot_id"],
                e["to"]["declared_id"], e["to"]["resolution"],
            )
            groups[sig].append(e)
        for group in groups.values():
            if len(group) > 1:
                tag = "repeat:" + hashlib.sha256(
                    repr((self.session, group[0]["identity"]["locator"])).encode()
                ).hexdigest()[:20]
                for i, e in enumerate(group, 1):
                    e["repeat_group"] = tag
                    e["repeat_occurrence"] = i
                self.gap("REPEATED_RELATION_OCCURRENCE", len(group) - 1)

    def coverage(self, source):
        targets = self.nodes + self.tables + [
            row for table in self.tables for row in table["rows"]
        ] + self.assets
        groups = {
            "presentation_node_occurrences": len(self.nodes),
            "source_nodes": len(self.nodes),
            "external_reference_stubs": 0,
            "tables": len(self.tables),
            "rows": sum(len(t["rows"]) for t in self.tables),
            "relations": len(self.relations),
            "assets": len(self.assets),
        }
        for name in _EXTRA_ROOT_COLLECTIONS:
            raw = source.get(name)
            if isinstance(raw, list) and raw:
                self.gap("UNMAPPED_ROOT_COLLECTION_" + name.upper(), len(raw))
            elif isinstance(raw, dict) and raw:
                self.gap("UNMAPPED_ROOT_OBJECT_" + name.upper(), 1)
        result_counts = [
            {
                "unit": name, "selected": size, "loaded": size,
                "visible": None, "unavailable": 0, "unknown_reason": None,
            } for name, size in groups.items()
        ]
        return {
            "population": "SELECTED_QUALIFYING_PAYLOAD",
            "global_archive": "UNKNOWN_UPSTREAM",
            "global_history": "GLOBAL_UNPROVEN",
            "global_total": None, "global_percentage": None,
            "snapshot_overlap": "NOT_SUMMED", "counts": result_counts,
        }


def transform_legacy_v5(parsed: ParsedSource, *, source_id: str,
                        snapshot_id: str, access_policy_id: str,
                        bytes_sha256: str, observed_at: str,
                        generated_at: str, expires_at: str,
                        synthetic_test: bool = False) -> dict:
    """Convert actual R4 v5 fields, never the invented source envelope.

    `synthetic_test=True` labels only the provenance of invented test bytes.
    A real producer cannot claim qualified acquisition through this function:
    the operational reader still refuses until the host is OS-constrained.
    """
    src = parsed.value
    validate_legacy_projection(src)
    if not all(isinstance(v, str) and v for v in
               (source_id, snapshot_id, access_policy_id)):
        _fail("SOURCE_IDENTITY_MISMATCH")
    if not isinstance(bytes_sha256, str) or len(bytes_sha256) != 64:
        _fail("SOURCE_DIGEST_REQUIRED")
    b = _Builder(parsed, source_id, snapshot_id)
    graph = src.get("lineage_graph") or {}
    for i, item in enumerate(graph.get("nodes", [])):
        b.add_node(item, f"/lineage_graph/nodes/{i}", lineage=True)
    for i, item in enumerate(src["records"]):
        b.add_node(item, f"/records/{i}")
    for i, table in enumerate(src["result_tables"]):
        b.add_table(table, f"/result_tables/{i}")
    for group, category in _ASSETS:
        for i, item in enumerate(src.get(group, [])):
            b.add_asset(item, f"/{group}/{i}", category)
    b.resolve()
    for i, edge in enumerate(graph.get("edges", [])):
        b.add_relation(edge, f"/lineage_graph/edges/{i}", graph=True)
    for i, edge in enumerate(src["edges"]):
        b.add_relation(edge, f"/edges/{i}")
    b.finalize_relations()
    policy = {
        "source_access": "EXTERNAL_EXACT_ALLOWLIST_ONLY",
        "max_descriptor_bytes": 33554432, "ttl_max_seconds": 3600,
        "browser_persistence": "MEMORY_ONLY", "automatic_uri_access": False,
    }
    return {
        "format": "atlas-legacy-presentation", "version": "0.2.0",
        "authority": "LEGACY_DERIVED", "synthetic": synthetic_test,
        "source": {
            "source_id": source_id, "scope": "R4_V5_EXPORTED_SNAPSHOT_ONLY",
            "original_format": "r4-experiment-viewer-v5",
            "original_profile_declared": src["schema"],
            "availability": "OBSERVED_AVAILABLE",
            "access_policy_id": access_policy_id,
            "declared_scientific_review": None,
        },
        "snapshot": {
            "snapshot_id": snapshot_id,
            "binding_basis": "SYNTHETIC_FIXTURE" if synthetic_test else "OBSERVED_BYTES_AND_POLICY",
            "bytes_sha256": bytes_sha256,
            "digest_status": "OBSERVED_BYTES",
            "observed_at": observed_at, "scientific_at": None,
            "generated_at": generated_at, "expires_at": expires_at,
            "freshness": "OBSERVED_SNAPSHOT_ONLY",
        },
        "validation": {
            "descriptor_schema": "NOT_RUN", "descriptor_semantics": "NOT_RUN",
            "literal_comparison": "NOT_PERFORMED",
            "source_profile_assessment": "NOT_ASSERTED",
            "authenticity": "NOT_VERIFIED", "scientific_approval": "NOT_EVALUATED",
        },
        "policy": policy,
        "nodes": b.nodes, "tables": b.tables, "relations": b.relations,
        "assets": b.assets, "unmapped_fields": b.unmapped,
        "coverage": b.coverage(src),
        "gaps": [
            {
                "code": name, "scope": "ONE_EXPORTED_R4_V5_SNAPSHOT",
                "count": count, "unit": "observed occurrences",
                "note": "Original source values remain in the input export; no invented binding or authority.",
            } for name, count in sorted(b.gaps.items()) if count
        ],
    }
