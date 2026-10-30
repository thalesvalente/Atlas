#!/usr/bin/env python3
"""Validate P01 documentary worksheets and exercise the unchanged public reader.

Not a Caderno extension, production parser, sidecar requirement or approval gate.
Only explicit local examples are read. No network, server, model or producer access.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
for relative in ("packages/protocol/src", "packages/atlas/src"):
    sys.path.insert(0, str(REPO / relative))

from caderno_protocol import load_package, to_read_model, validate_document
from atlas_viewer.catalog import Catalog

AUTHORITY = "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL"
LAYERS = ["source", "projection", "selection", "conversion", "package", "read_model", "interface"]
CLASSES = {"CURRENT_CONTRACT", "COMPATIBLE_PRESENTATION_CANDIDATE", "PERSISTED_EVOLUTION_REQUIRED"}
RELATIONS = {"mentions": "reference", "object": "input", "result": "output", "prov:wasDerivedFrom": "derived_from"}


class ContractError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def require(condition, code, message):
    if not condition:
        raise ContractError(code, message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def integer(value):
    return type(value) is int and value >= 0


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "JSON_DUPLICATE_KEY", "Repeated object key: " + key)
        out[key] = value
    return out


def reject_constant(value):
    raise ContractError("JSON_NONFINITE", "Non-finite JSON number: " + value)


def finite_float(value):
    parsed = float(value)
    require(math.isfinite(parsed), "JSON_NONFINITE", "JSON numeric overflow is not an unknown finite value.")
    return parsed


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs,
                      parse_constant=reject_constant, parse_float=finite_float)


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def temporal(observation, role):
    require(isinstance(observation, dict), "TIME_SHAPE", "Each role needs an observation object.")
    value, precision, origin = (observation.get(k) for k in ("value", "precision", "origin"))
    if value is None:
        require(precision == "UNKNOWN" and origin == "UNKNOWN", "TIME_UNKNOWN", "Absent time keeps unknown origin and precision.")
        return
    expected = {"event": "DECLARED_EVENT", "file_created": "FILE_CREATED", "observed": "OBSERVATION"}[role]
    require(origin == expected, "TIME_ROLE", "A date cannot silently change temporal role.")
    require(precision in {"day", "second"}, "TIME_PRECISION", "Only explicit day/second precision is demonstrated.")
    if precision == "second":
        require(timestamp(value), "TIME_FORMAT", "A second-resolution observation needs a valid timestamp with offset.")
    else:
        try:
            valid = isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) and date.fromisoformat(value)
        except ValueError:
            valid = False
        require(bool(valid), "TIME_FORMAT", "A day-resolution observation preserves a valid date only.")


def presentation(document):
    require(text(document.get("catalog_scope")), "CATALOG_SCOPE", "Catalog scope is explicit and local.")
    sources = document.get("sources")
    require(isinstance(sources, list) and sources, "SOURCE_SHAPE", "At least one declared source is required in this worksheet.")
    source_ids = set()
    for source in sources:
        sid = source.get("id")
        require(text(sid) and sid not in source_ids, "SOURCE_ID", "Sources need unique contextual IDs.")
        source_ids.add(sid)
        require(source.get("identity_scope") == "CURRENT_CATALOG" and source.get("stable_across_reorder") is False,
                "ORDINAL_STABILITY", "An ordinal source does not promise stability after reorder.")
        require(isinstance(source.get("metadata_sha256"), str) and re.fullmatch(r"[a-f0-9]{64}", source["metadata_sha256"]),
                "DIGEST_FORMAT", "A declared digest identifies bytes, not authenticity.")
    entities = document.get("entities")
    require(isinstance(entities, list), "ENTITY_SHAPE", "Entities must be an ordered array.")
    index = {}
    for entity in entities:
        key = (entity.get("source_id"), entity.get("id"))
        require(key[0] in source_ids and text(key[1]), "ENTITY_ID", "Each entity must belong to a declared source.")
        require(key not in index, "DUPLICATE_CONTEXTUAL_ID", "An ID is unique inside its source, not globally.")
        index[key] = entity
        types = entity.get("declared_types")
        require(isinstance(types, list) and types and all(text(t) for t in types), "ENTITY_TYPES", "Preserve declared types.")
        kind = entity.get("presentation_kind")
        require(kind in {"execution", "document", "product", "table", "reference", "documentary_milestone"}, "ENTITY_KIND", "Unknown worksheet kind.")
        require((kind == "execution") == ("CreateAction" in types), "ENTITY_KIND", "Document/product must not become an execution.")
        require(kind != "document" or bool(set(types) & {"DigitalDocument", "TextDigitalDocument", "ScholarlyArticle", "Report"}),
                "ENTITY_KIND", "A document label needs explicit type support in this worksheet.")
        require(kind != "product" or "Product" in types, "ENTITY_KIND", "A product label needs explicit Product support.")
        category = entity.get("contract_class")
        require(category in CLASSES, "CONTRACT_CLASS", "Distinguish current contract, candidate presentation and evolution.")
        require(kind not in {"table", "documentary_milestone"} or category == "PERSISTED_EVOLUTION_REQUIRED",
                "CONTRACT_CLASS", "Typed table/milestone semantics are a future proposal in this worksheet.")
        times = entity.get("time")
        require(isinstance(times, dict) and set(times) == {"event", "file_created", "observed"}, "TIME_SHAPE", "Three temporal roles stay separate.")
        for role, observation in times.items():
            temporal(observation, role)
    relations = document.get("relations")
    require(isinstance(relations, list), "RELATION_SHAPE", "Relations must be explicit.")
    for relation in relations:
        subject, target = relation.get("source", {}), relation.get("target", {})
        skey, tkey = (subject.get("source_id"), subject.get("id")), (target.get("source_id"), target.get("id"))
        require(skey[0] == tkey[0], "CROSS_SOURCE_RELATION", "No resolution in a different source.")
        require(skey in index and tkey in index, "MISSING_REFERENCE", "Both contextual endpoints must exist.")
        predicate = relation.get("declared_predicate")
        require(predicate in RELATIONS and relation.get("presentation_relation") == RELATIONS[predicate],
                "RELATION_SEMANTICS", "A mention cannot become input/output/derivation.")
        require(predicate not in {"object", "result"} or index[skey]["presentation_kind"] == "execution",
                "RELATION_SUBJECT", "object/result retain the execution as declared subject.")


def cell_value(column, cell):
    value, raw, missing = cell.get("value"), cell.get("raw"), cell.get("missing_reason")
    if value is None:
        require(text(missing) and raw is None, "CELL_MISSING_REASON", "Missing is null with a reason, never fabricated zero/raw.")
        return
    require(missing is None, "CELL_MISSING_REASON", "A known value cannot carry an unresolved missing-state claim.")
    dtype = column.get("type")
    good = ((dtype == "number" and (type(value) is int or (type(value) is float and math.isfinite(value))))
            or (dtype == "integer" and type(value) is int)
            or (dtype == "boolean" and type(value) is bool)
            or (dtype == "string" and isinstance(value, str))
            or dtype is None)
    require(good, "CELL_TYPE", "Typed values preserve bool, integer, number and string distinctions.")
    require(isinstance(raw, str), "CELL_LEXEME", "Known cells preserve their declared lexical form.")
    if dtype in {"integer", "number"}:
        try:
            lexical = Decimal(raw)
            equal = lexical.is_finite() and lexical == Decimal(str(value))
        except InvalidOperation:
            equal = False
        require(equal, "CELL_LEXEME", "Lexical and typed numeric value must agree exactly.")
        if dtype == "integer":
            require(re.fullmatch(r"-?(?:0|[1-9]\d*)", raw) is not None, "CELL_LEXEME", "Integer lexical form must remain integral.")
        precision = column.get("precision")
        if precision is not None:
            require(-lexical.as_tuple().exponent >= precision, "CELL_PRECISION", "Do not invent declared decimal places lost in the literal.")
    elif dtype == "boolean":
        require(raw == ("true" if value else "false"), "CELL_LEXEME", "Boolean text is not an arbitrary string.")
    elif dtype == "string":
        require(raw == value, "CELL_LEXEME", "String lexical form is preserved without numeric coercion.")


def table(document):
    require(document.get("contract_class") == "PERSISTED_EVOLUTION_REQUIRED", "TABLE_CONTRACT_CLASS", "The general typed grid is not a current Caderno schema.")
    tables = document.get("tables")
    require(isinstance(tables, list) and tables, "TABLE_SHAPE", "Explicit documentary tables are required.")
    index = {}
    for grid in tables:
        tid = grid.get("id")
        require(text(tid) and tid not in index, "TABLE_ID", "Table IDs are unique in this worksheet.")
        columns, rows = grid.get("columns"), grid.get("rows")
        require(isinstance(columns, list) and columns and isinstance(rows, list), "TABLE_SHAPE", "Columns and rows are ordered arrays.")
        col_ids = [c.get("id") for c in columns]
        require(all(text(x) for x in col_ids) and len(set(col_ids)) == len(col_ids), "COLUMN_ID", "Column IDs are unique within a table.")
        require(col_ids == grid.get("column_order"), "COLUMN_ORDER", "Column order must equal its explicitly declared source order.")
        row_ids = [r.get("id") for r in rows]
        require(all(text(x) for x in row_ids) and len(set(row_ids)) == len(row_ids), "ROW_ID", "Row IDs are unique within a table.")
        require(row_ids == grid.get("row_order"), "ROW_ORDER", "Row order must equal its explicitly declared source order.")
        for col in columns:
            require(col.get("type") in {None, "number", "integer", "string", "boolean"}, "COLUMN_TYPE", "Unsupported declared type.")
            require(col.get("precision") is None or integer(col["precision"]), "COLUMN_PRECISION", "Precision is a nonnegative integer or unknown.")
            for name in ("semantic_id", "unit", "measurement_context"):
                require(col.get(name) is None or text(col[name]), "COLUMN_METADATA", "Unknown metadata stays null.")
        by_col, by_row = {c["id"]: c for c in columns}, {}
        for row in rows:
            cells = row.get("cells")
            require(isinstance(cells, list) and [c.get("column_id") for c in cells] == col_ids, "CELL_ORDER", "Each ordered cell identifies its column.")
            by_row[row["id"]] = {c["column_id"]: c for c in cells}
            for cell in cells:
                cell_value(by_col[cell["column_id"]], cell)
        index[tid] = (by_col, by_row)
    comparisons = document.get("comparisons")
    require(isinstance(comparisons, list), "COMPARISON_SHAPE", "Comparison claims must be explicit.")
    for comparison in comparisons:
        values = []
        for side in ("left", "right"):
            location = comparison.get(side, {})
            tid, cid, rid = (location.get(k) for k in ("table_id", "column_id", "row_id"))
            require(tid in index and cid in index[tid][0] and rid in index[tid][1], "COMPARISON_TARGET", "Comparison endpoints must exist.")
            values.append((index[tid][0][cid], index[tid][1][rid][cid]))
        (left, lc), (right, rc) = values
        fields = ("semantic_id", "type", "unit", "measurement_context")
        if any(left.get(k) is not None and right.get(k) is not None and left[k] != right[k] for k in fields):
            expected = "INCOMPATIBLE"
        elif any(left.get(k) is None or right.get(k) is None for k in fields) or lc.get("value") is None or rc.get("value") is None:
            expected = "UNKNOWN"
        elif left["type"] not in {"number", "integer"}:
            expected = "INCOMPATIBLE"
        else:
            expected = "COMPATIBLE"
        require(comparison.get("decision") == expected, "COMPARISON_COMPATIBILITY", "Quantitative comparison needs known semantic identity, type, unit, context and values; no conversion is implied.")


def coverage(document):
    require(document.get("derived") is True and document.get("caderno_required") is False, "SIDECAR_AUTHORITY", "Coverage is derived and optional.")
    require(document.get("collection_total_inferred_from_loaded_runs") is False, "COLLECTION_INFERENCE", "Loaded runs do not define the collection total.")
    require(text(document.get("scope_id")) and timestamp(document.get("observed_at")), "COVERAGE_SCOPE", "Scope and observation time are explicit.")
    selection = document.get("selection", {})
    require(all(text(selection.get(k)) for k in ("criterion", "unit", "selection_id")), "SELECTION_CRITERION", "The selected population and criterion must be explicit.")
    measures = document.get("layers")
    require(isinstance(measures, list) and [m.get("layer") for m in measures] == LAYERS, "LAYER_CHAIN", "Describe all seven layers exactly once, in order.")
    by_layer = {m["layer"]: m for m in measures}
    for measure in measures:
        require(text(measure.get("unit")) and text(measure.get("scope_id")), "MEASURE_SCOPE", "Every number needs a unit and scope.")
        require(type(measure.get("known")) is bool, "KNOWN_FLAG", "Known must be a boolean.")
        count = measure.get("count")
        if not measure["known"]:
            require(count is None, "UNKNOWN_NOT_NULL", "Unknown is null, not zero or false.")
        else:
            require(integer(count), "COUNT_TYPE", "Counts are nonnegative integers; bool is not an integer count.")
            require(isinstance(measure.get("evidence"), list) and bool(measure["evidence"]) and all(text(e) for e in measure["evidence"]),
                    "COUNT_EVIDENCE", "Known counts need declared evidence.")
    for measure in measures:
        denominator, ratio = measure.get("denominator"), measure.get("ratio")
        if denominator is None:
            require(ratio is None, "RATIO_UNDEFINED", "No ratio with an unknown denominator.")
            continue
        require(isinstance(denominator, dict) and denominator.get("layer") in by_layer, "DENOMINATOR_TARGET", "Denominator names an existing measured layer.")
        other = by_layer[denominator["layer"]]
        require(denominator.get("scope_id") == measure["scope_id"] == other["scope_id"], "DENOMINATOR_SCOPE", "Different scopes cannot silently share a denominator.")
        require(denominator.get("unit") == measure["unit"] == other["unit"], "DENOMINATOR_UNIT", "Units must be identical.")
        require(denominator.get("relation") == "SUBSET_OF" and text(denominator.get("mapping_evidence")), "DENOMINATOR_MAPPING", "Subset correspondence needs explicit evidence.")
        require(measure["known"] and other["known"] and integer(denominator.get("count")) and denominator["count"] == other["count"],
                "DENOMINATOR_COUNT", "Denominator must equal the known referenced count.")
        require(measure["count"] <= denominator["count"], "SUBSET_COUNT", "A subset cannot exceed its denominator.")
        if denominator["count"] == 0:
            require(ratio is None, "RATIO_UNDEFINED", "0/0 has no percentage.")
        elif ratio is not None:
            require(type(ratio) in (int, float) and math.isfinite(ratio) and math.isclose(ratio, measure["count"] / denominator["count"], rel_tol=1e-12),
                    "RATIO_VALUE", "An explicit ratio must match its exact counts.")
    losses = document.get("losses")
    require(isinstance(losses, list), "LOSS_SHAPE", "Losses/limitations are explicit.")
    unknown_explained = set()
    for loss in losses:
        start, end = loss.get("from_layer"), loss.get("to_layer")
        require(start in by_layer and end in by_layer and start != end, "LOSS_LAYERS", "Both loss layers must exist.")
        require(text(loss.get("reason")), "LOSS_REASON", "A loss or unknown boundary needs a reason.")
        if loss.get("count") is None:
            unknown_explained.update((start, end))
            continue
        a, b = by_layer[start], by_layer[end]
        require(integer(loss["count"]) and a["known"] and b["known"] and a["unit"] == b["unit"] == loss.get("unit")
                and a["scope_id"] == b["scope_id"] and loss.get("mapping") == "ONE_TO_ONE" and a["count"] - b["count"] == loss["count"],
                "LOSS_COUNT", "A numeric loss needs comparable observed populations and a one-to-one mapping.")
    require(all(m["known"] or m["layer"] in unknown_explained for m in measures), "UNKNOWN_REASON", "Every unknown layer needs an explicit explanatory boundary.")


def validate(data, format_name=None):
    require(isinstance(data, dict), "DOCUMENT_TYPE", "An example is an object.")
    kind = format_name or data.get("kind") or ("CADERNO_CURRENT" if "@context" in data else None)
    if kind == "CADERNO_CURRENT":
        return sorted({"SDK:" + issue.code for issue in validate_document(data).errors})
    require(data.get("status") == "CANDIDATE" and data.get("authority") == AUTHORITY and data.get("synthetic") is True,
            "WORKSHEET_AUTHORITY", "Worksheets are synthetic candidate documents, never scientific approval.")
    validators = {"ATLAS_P01_PRESENTATION_EXAMPLE": presentation, "ATLAS_P01_TABLE_EXAMPLE": table, "ATLAS_P01_COVERAGE_EXAMPLE": coverage}
    require(kind in validators, "WORKSHEET_KIND", "Unsupported documentary worksheet.")
    validators[kind](data)
    return []


def errors_for(path, format_name=None):
    try:
        return validate(read_json(path), format_name)
    except ContractError as exc:
        return [exc.code]
    except (json.JSONDecodeError, UnicodeError):
        return ["JSON_SYNTAX"]
    except (KeyError, TypeError, AttributeError, ValueError):
        return ["WORKSHEET_SHAPE"]


def reader_probes():
    examples = HERE / "examples"
    a, b = examples / "current-profile-minimal.json", examples / "current-profile-second-source.json"
    hashes_before = {p.name: sha256(p) for p in (a, b)}
    package = load_package(a)
    require(package.report.valid, "PROBE_PROFILE", "The synthetic package must be accepted by the real reader.")
    model = to_read_model(package)
    uid = lambda name: "urn:atlas:p01:synthetic:" + name
    facts = []
    def check(id_, condition, detail):
        require(condition, "PROBE_FAILED", id_ + ": " + detail)
        facts.append({"id": id_, "status": "PASS", "detail": detail})
    check("CURRENT_ENTITIES", len(model["entities"]) == len(package.document["@graph"]) == 13,
          "All 13 declared graph entities survive in entities.")
    check("DOCUMENT_PRODUCT_NOT_RUNS", [r["id"] for r in model["runs"]] == [uid("run")],
          "Document, product and table-file metadata do not create additional runs.")
    run = model["runs"][0]
    check("MENTION_NEUTRAL_ORDER", [r["id"] for r in run["related_references"]] == [uid("document"), uid("product"), "tables/sample.csv"] and not run["inputs"] and not run["outputs"] and not model["relations"],
          "Duplicate mention deduplicated in order, with zero experimental edges inferred.")
    check("UNKNOWN_VALUES_TIMES", run["metrics"][0]["value"] is None and bool(run["metrics"][0]["missing_reason"]) and run["metrics"][0]["precision"] == 2 and run["started_at"] is None and run["ended_at"] is None and run["timestamp_origin"] == "UNKNOWN",
          "Absent value, declared precision and unknown event time are preserved.")
    check("TABLE_METADATA_ONLY", len(model["artifacts"]) == 1 and model["artifacts"][0]["id"] == "tables/sample.csv" and "rows" not in model["artifacts"][0],
          "A table file is representable as metadata; no typed grid is fabricated.")
    first = Catalog([a, b]).snapshot(check_changes=False)
    second = Catalog([b, a]).snapshot(check_changes=False)
    check("SOURCE_SCOPED_COLLISION", len(first["sources"]) == 2 and len(first["collisions"]) > 0 and first["sources"][0]["read_model"]["runs"][0]["related_references"][0]["name"] == "Documento sintético A" and first["sources"][1]["read_model"]["runs"][0]["related_references"][0]["name"] == "Documento sintético B",
          "Same entity IDs in two sources retain different source-local titles.")
    check("ORDINAL_REORDER_LIMIT", first["sources"][0]["id"] == second["sources"][0]["id"] == "source-1" and first["sources"][0]["metadata_sha256"] != second["sources"][0]["metadata_sha256"],
          "Reordering changes which bytes source-1 denotes; stable identity is not asserted.")
    invalid = Catalog([examples / "negative-current-missing-reference.json"]).snapshot(check_changes=False)
    check("INVALID_SOURCE_NOT_INDEXED", invalid["sources"][0]["status"] == "INVALID" and invalid["sources"][0]["read_model"] is None,
          "The current reader rejects a missing target; no alternate source is searched.")
    check("INPUT_BYTES_UNCHANGED", hashes_before == {p.name: sha256(p) for p in (a, b)}, "Observed synthetic inputs are byte-identical after these reads.")
    return facts


def run_suite():
    manifest = read_json(HERE / "examples/cases.json")
    cases = manifest["cases"]
    require(len({c["id"] for c in cases}) == len(cases), "CASE_ID", "Case IDs must be unique.")
    rows = []
    for case in cases:
        relative = Path(case["file"])
        require(relative.name == str(relative) and relative.suffix == ".json", "CASE_PATH", "Only explicit local JSON case files are supported.")
        path = HERE / "examples" / relative
        actual = errors_for(path, case["format"])
        passed = sorted(actual) == sorted(case["expected_errors"]) and (not actual) == case["expected_valid"]
        rows.append({"id": case["id"], "expected_valid": case["expected_valid"], "errors": actual, "status": "PASS" if passed else "FAIL", "sha256": sha256(path)})
    try:
        probes = reader_probes()
    except ContractError as exc:
        probes = [{"id": "READER_PROBES", "status": "FAIL", "error": exc.code, "message": str(exc)}]
    ok = all(r["status"] == "PASS" for r in rows + probes)
    return {"status": "PASS" if ok else "FAIL", "scope": "P01_DOCUMENTARY_EXAMPLES_AND_UNCHANGED_READER", "unique_examples": len(rows),
            "positive_examples": sum(c["expected_valid"] for c in cases), "negative_examples": sum(not c["expected_valid"] for c in cases),
            "reader_probes": probes, "cases": rows, "validator_sha256": sha256(Path(__file__)), "cases_manifest_sha256": sha256(HERE / "examples/cases.json"),
            "not_claimed": ["browser_execution", "legacy_parity", "host_access", "scientific_approval", "new_protocol"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--suite", action="store_true")
    group.add_argument("--file", type=Path)
    args = parser.parse_args()
    if args.suite:
        result = run_suite()
    else:
        actual = errors_for(args.file)
        result = {"status": "REJECTED" if actual else "ACCEPTED", "errors": actual, "sha256": sha256(args.file)}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["status"] in {"PASS", "ACCEPTED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
