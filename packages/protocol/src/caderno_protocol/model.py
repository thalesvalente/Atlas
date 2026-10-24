"""Validate a deliberately restricted JSON-LD profile, without remote loading.

This is not a validator for arbitrary RDF/JSON-LD or proof of scientific validity.
The fixed context and graph-shape restrictions make direct relation checks sound
for the supported serialization. Original records are never changed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from functools import lru_cache
import hashlib
from importlib.resources import files
import json
import math
import re
import unicodedata
from typing import Any
from urllib.parse import unquote, urlsplit

PROFILE_VERSION = "0.1.0a1"
PROFILE_ID = "https://github.com/thalesvalente/Atlas/blob/feat/atlas021-interface-protocol/docs/protocol/0.1.0a1.md"
NS = "https://github.com/thalesvalente/Atlas/ns/caderno#"
RO_CRATE = "https://w3id.org/ro/crate/1.3"
PROCESS_PROFILE = "https://w3id.org/ro/wfrun/process/0.6"
CONTEXT = [RO_CRATE + "/context", {"cp": NS, "prov": "http://www.w3.org/ns/prov#"}]
MAX_NODES = 10000
MAX_DEPTH = 20
STATUSES = {"COMPLETED", "PARTIAL", "FAILED", "RUNNING", "UNKNOWN"}
REVIEWS = {"UNKNOWN", "HOLD", "ACCEPTED", "REJECTED", "NOT_APPLICABLE"}
ACTION_STATUS = {
    "COMPLETED": "http://schema.org/CompletedActionStatus",
    "FAILED": "http://schema.org/FailedActionStatus",
    "RUNNING": "http://schema.org/ActiveActionStatus",
    "PARTIAL": "http://schema.org/FailedActionStatus",
    "UNKNOWN": "http://schema.org/PotentialActionStatus",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass
class ValidationReport:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": [asdict(x) for x in self.errors],
                "warnings": [asdict(x) for x in self.warnings],
                "scope": "caderno-0.1.0a1-restricted-serialization",
                "authenticity": "NOT_VERIFIED", "scientific_acceptance": "NOT_EVALUATED"}


@dataclass
class Package:
    document: dict[str, Any]
    metadata_sha256: str
    report: ValidationReport
    payload_status: dict[str, dict[str, Any]] = field(default_factory=dict)
    source_name: str = ""


def types(entity: dict[str, Any]) -> list[str]:
    value = entity.get("@type", [])
    return [value] if isinstance(value, str) else [x for x in value if isinstance(x, str)] if isinstance(value, list) else []


def refs(value: Any) -> list[str]:
    if isinstance(value, dict) and set(value) == {"@id"} and isinstance(value["@id"], str):
        return [value["@id"]]
    if isinstance(value, list):
        return [ref for item in value for ref in refs(item)]
    return []


def safe_relative_path(value: str) -> str | None:
    """Return a safe portable package path; never accepts an external URI."""
    if not isinstance(value, str) or not value or len(value) > 2048:
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        return None
    decoded = unquote(value)
    if "\\" in decoded or "\x00" in decoded or ":" in decoded or decoded.startswith("/"):
        return None
    parts = decoded.split("/")
    if any(p in {"", ".", ".."} for p in parts):
        return None
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10)}
    if any(p.endswith((".", " ")) or p.split(".")[0].upper() in reserved for p in parts):
        return None
    if any(ord(c) < 32 for c in decoded):
        return None
    return decoded


@lru_cache(maxsize=1)
def _context_terms() -> frozenset[str]:
    directory = files("caderno_protocol").joinpath("resources")
    catalog = json.loads(directory.joinpath("context-catalog.json").read_text(encoding="utf-8"))
    entry = catalog["contexts"][RO_CRATE + "/context"]
    raw = directory.joinpath(entry["filename"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise ValueError("Installed context catalogue digest mismatch.")
    return frozenset(json.loads(raw)["@context"])


def _known_term(value: str, terms: frozenset[str]) -> bool:
    return value in terms or value.startswith(("cp:", "prov:", "https://", "http://"))


def _timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value and parsed.tzinfo is not None
    except ValueError:
        return False


def validate_document(document: Any) -> ValidationReport:
    report = ValidationReport()
    def error(code: str, path: str, message: str) -> None:
        report.errors.append(ValidationIssue(code, path, message))
    def warning(code: str, path: str, message: str) -> None:
        report.warnings.append(ValidationIssue(code, path, message))
    if not isinstance(document, dict):
        error("DOCUMENT_TYPE", "$", "Expected a JSON object.")
        return report
    try:
        context_terms = _context_terms()
    except (OSError, ValueError, KeyError) as exc:
        error("CONTEXT_CATALOG", "$", str(exc))
        return report
    if document.get("@context") != CONTEXT:
        error("UNSUPPORTED_CONTEXT", "$.@context", "Only the pinned RO-Crate 1.3 context plus the exact cp/prov prefix map is supported; no remote contexts are loaded.")
    if set(document) != {"@context", "@graph"}:
        error("DOCUMENT_KEYS", "$", "Restricted serialization requires only @context and @graph at the top level.")
    graph = document.get("@graph")
    if not isinstance(graph, list) or len(graph) > MAX_NODES:
        error("GRAPH_LIMIT", "$.@graph", f"Expected a graph array containing at most {MAX_NODES} entities.")
        return report
    entities: dict[str, dict[str, Any]] = {}
    payload_aliases: dict[str, str] = {}
    for index, entity in enumerate(graph):
        path = f"$.@graph[{index}]"
        if not isinstance(entity, dict) or not isinstance(entity.get("@id"), str):
            error("ENTITY_ID", path, "Every entity needs a string @id.")
            continue
        eid = entity["@id"]
        if not eid or len(eid) > 2048 or any(ord(c) < 32 for c in eid):
            error("ENTITY_ID", path, "Empty, overlong or control-character identifiers are forbidden.")
        if eid in entities:
            error("DUPLICATE_ID", path, "Duplicate graph identifiers are not merged.")
        entities[eid] = entity
        etypes = types(entity)
        raw_types = entity.get("@type")
        if not etypes or any(not t for t in etypes) or (isinstance(raw_types, list) and len(raw_types) != len(etypes)):
            error("ENTITY_TYPE", path, "A non-empty string @type or array of types is required.")
        if any(not _known_term(t, context_terms) for t in etypes):
            error("UNMAPPED_TERM", path + ".@type", "Every type must be in the pinned context or use a namespaced IRI.")
        for key in entity:
            if not key.startswith("@") and not _known_term(key, context_terms):
                error("UNMAPPED_TERM", path + "." + key, "Extension properties must use an explicit namespace.")
        if any(k.startswith("@") and k not in {"@id", "@type"} for k in entity):
            error("GRAPH_FORM", path, "Nested contexts, reverse graphs and alternate JSON-LD forms are outside this profile.")
        if "File" in etypes:
            try:
                parsed = urlsplit(eid)
                remote = parsed.scheme in {"https", "http"} and bool(parsed.hostname) and not parsed.username and not parsed.password
            except ValueError:
                remote = False
            if not remote and safe_relative_path(eid) is None:
                error("UNSAFE_REFERENCE", path + ".@id", "File identifiers must be safe relative paths or HTTP(S) references, which are never downloaded.")
            if not remote:
                relative = safe_relative_path(eid)
                if relative is not None:
                    alias = unicodedata.normalize("NFC", relative).casefold()
                    if alias in payload_aliases and payload_aliases[alias] != eid:
                        error("ID_ALIAS_COLLISION", path + ".@id", "File identifiers alias the same portable package path.")
                    payload_aliases[alias] = eid
    root = entities.get("./", {})
    metadata = entities.get("ro-crate-metadata.json", {})
    if "CreativeWork" not in types(metadata) or refs(metadata.get("about")) != ["./"]:
        error("METADATA_DESCRIPTOR", "ro-crate-metadata.json", "Descriptor must be CreativeWork and refer to ./ through about.")
    if refs(metadata.get("conformsTo")) != [RO_CRATE]:
        error("UNSUPPORTED_VERSION", "ro-crate-metadata.json.conformsTo", "This candidate supports RO-Crate 1.3 only.")
    if "Dataset" not in types(root):
        error("ROOT_DATASET", "./", "The root Dataset ./ is required.")
    for key in ("name", "description", "license", "datePublished"):
        if key not in root or root[key] in (None, "", []):
            error("ROOT_REQUIRED", "./." + key, "Root metadata is missing " + key + ".")
    published = root.get("datePublished")
    if isinstance(published, str):
        try:
            if "T" in published:
                if not _timestamp(published):
                    raise ValueError()
            else:
                date.fromisoformat(published)
        except ValueError:
            error("DATE_FORMAT", "./.datePublished", "Use an ISO date or timezone-aware timestamp for the snapshot publication date.")
    else:
        error("DATE_FORMAT", "./.datePublished", "Snapshot publication date must be a string.")
    profiles = refs(root.get("conformsTo"))
    if PROFILE_ID not in profiles:
        error("UNSUPPORTED_PROFILE", "./.conformsTo", "The exact pre-release Caderno profile 0.1.0a1 is required; unknown versions are not downgraded.")
    if PROCESS_PROFILE not in profiles:
        error("PROCESS_PROFILE", "./.conformsTo", "Process Run Crate 0.6 must be declared.")
    if any(p not in {PROFILE_ID, PROCESS_PROFILE} for p in profiles):
        error("UNSUPPORTED_PROFILE", "./.conformsTo", "Additional profile declarations require explicit reader support.")
    for profile_id in (PROFILE_ID, PROCESS_PROFILE):
        profile_types = types(entities.get(profile_id, {}))
        if "CreativeWork" not in profile_types or "http://www.w3.org/ns/dx/prof/Profile" not in profile_types:
            error("PROFILE_ENTITY", profile_id, "Profile declarations must reference both CreativeWork and W3C Profile entities.")

    # Graph relations, not merely JSON object shape, are validated here.
    total_relations = 0
    def walk(value: Any, path: str, depth: int = 0) -> None:
        nonlocal total_relations
        if depth > MAX_DEPTH:
            error("DEPTH_LIMIT", path, "Metadata nesting exceeds the profile limit.")
            return
        if isinstance(value, dict):
            if "@id" in value:
                if set(value) != {"@id"} or not isinstance(value["@id"], str):
                    error("REFERENCE_FORM", path, "Nested entities must use a bare @id reference; define full entities at graph level.")
                    return
                total_relations += 1
                target = value["@id"]
                if target not in entities and not target.startswith(("https://", "http://")):
                    error("MISSING_REFERENCE", path, "Referenced entity does not exist in this snapshot: " + target)
            else:
                error("NESTED_OBJECT", path, "Arbitrary nested JSON objects are not supported; use named graph entities or a literal string.")
        elif isinstance(value, list):
            for pos, item in enumerate(value):
                walk(item, f"{path}[{pos}]", depth + 1)
        elif not isinstance(value, (str, int, float, bool, type(None))):
            error("VALUE_TYPE", path, "Unsupported JSON value.")
        elif isinstance(value, float) and not math.isfinite(value):
            error("NONFINITE_NUMBER", path, "NaN and infinities are forbidden.")
    for eid, entity in entities.items():
        for key, value in entity.items():
            if key not in {"@id", "@type"}:
                walk(value, eid + "." + key)
            if key in {"hasPart", "mentions", "isPartOf", "cp:experiment", "cp:metrics", "cp:parameters", "object", "result", "instrument", "agent", "prov:wasDerivedFrom"}:
                for target in refs(value):
                    if target not in entities:
                        error("MISSING_REFERENCE", eid + "." + key, "Graph relation targets an undeclared entity: " + target)
    if total_relations > 100000:
        error("RELATION_LIMIT", "$.@graph", "At most 100000 graph relations are supported.")
    project_ids = {eid for eid, e in entities.items() if "cp:Project" in types(e)}
    experiment_ids = {eid for eid, e in entities.items() if "cp:Experiment" in types(e)}
    for eid in project_ids | experiment_ids:
        entity = entities[eid]
        if "Dataset" not in types(entity) or not isinstance(entity.get("name"), str):
            error("COLLECTION_TYPE", eid, "Projects and experiments must also be named Datasets.")
        if not eid.startswith(("urn:", "https://", "http://")):
            error("NAMESPACE_REQUIRED", eid, "Projects and experiments need a producer-scoped absolute identifier.")
        if eid in experiment_ids:
            parents = refs(entity.get("isPartOf"))
            if len(parents) != 1 or parents[0] not in project_ids:
                error("EXPERIMENT_PROJECT", eid, "An experiment must reference exactly one declared project.")
    has_parts = set(refs(root.get("hasPart")))
    for eid, entity in entities.items():
        etypes = types(entity)
        if "SoftwareApplication" in etypes:
            for key in ("name", "url", "version"):
                if not isinstance(entity.get(key), str) or not entity.get(key):
                    error("SOFTWARE_METADATA", eid + "." + key, "SoftwareApplication requires explicit name, url and version; unknown software version must be declared as unknown.")
        if ("File" in etypes or "Dataset" in etypes) and eid != "./" and eid not in has_parts:
            error("ROOT_INVENTORY", eid, "Each data entity must appear in the root hasPart inventory.")
        if "PropertyValue" in etypes:
            dtype = entity.get("cp:valueType")
            if not isinstance(dtype, str) or dtype not in {"number", "integer", "string", "boolean"}:
                error("METRIC_TYPE", eid, "PropertyValue requires cp:valueType number/integer/string/boolean.")
            if not isinstance(entity.get("propertyID"), str) or not entity.get("propertyID"):
                error("METRIC_ID", eid, "PropertyValue needs a stable propertyID.")
            value = entity.get("value")
            if value is None:
                if not isinstance(entity.get("cp:missingReason"), str) or not entity.get("cp:missingReason"):
                    error("MISSING_VALUE_REASON", eid, "Missing values need an explicit reason and must not become zero.")
            else:
                allowed = ((dtype == "number" and type(value) in (int, float)) or
                           (dtype == "integer" and type(value) is int) or
                           (dtype == "string" and isinstance(value, str)) or
                           (dtype == "boolean" and type(value) is bool))
                if not allowed:
                    error("METRIC_VALUE_TYPE", eid, "Value disagrees with its declared type.")
            if isinstance(dtype, str) and dtype in {"number", "integer"} and (not isinstance(entity.get("unitText"), str) or not entity.get("unitText")):
                error("METRIC_UNIT", eid, "Numeric values require an explicit unit; use 1 for dimensionless quantities.")
            if "cp:precision" in entity and (type(entity["cp:precision"]) is not int or entity["cp:precision"] < 0):
                error("PRECISION", eid, "Precision must be a non-negative integer.")
        if "File" in etypes:
            digest = entity.get("cp:sha256")
            if digest is not None and (not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
                error("DIGEST_FORMAT", eid, "cp:sha256 must be a lowercase SHA-256 digest of payload bytes.")
            availability = entity.get("cp:availability")
            if not isinstance(availability, str) or availability not in {"PRESENT", "MISSING", "EXTERNAL", "UNKNOWN"}:
                error("AVAILABILITY", eid, "File availability declaration is required and does not prove availability.")
            if "contentSize" in entity and (type(entity["contentSize"]) is not int or entity["contentSize"] < 0):
                error("CONTENT_SIZE", eid, "contentSize must be a non-negative integer of payload bytes.")
        if "CreateAction" not in etypes:
            continue
        if not eid.startswith(("urn:", "https://", "http://")):
            error("NAMESPACE_REQUIRED", eid, "Run IDs need a producer-scoped absolute identifier.")
        status, review = entity.get("cp:executionStatus"), entity.get("cp:reviewStatus")
        if not isinstance(status, str) or status not in STATUSES:
            error("EXECUTION_STATUS", eid, "An explicit supported execution status is required.")
        if not isinstance(review, str) or review not in REVIEWS:
            error("REVIEW_STATUS", eid, "An explicit review status separate from execution is required.")
        if type(entity.get("cp:synthetic")) is not bool:
            error("SYNTHETIC_DECLARATION", eid, "cp:synthetic must explicitly identify synthetic records.")
        if entity.get("cp:synthetic") is True and review == "ACCEPTED":
            error("SYNTHETIC_APPROVAL", eid, "Synthetic demonstration records cannot declare accepted science in this profile.")
        if isinstance(status, str) and status in ACTION_STATUS and refs(entity.get("actionStatus")) != [ACTION_STATUS[status]]:
            error("ACTION_STATUS", eid, "actionStatus must explicitly agree with cp:executionStatus; absent status must not imply success.")
        experiment = refs(entity.get("cp:experiment"))
        if len(experiment) != 1 or experiment[0] not in experiment_ids:
            error("RUN_EXPERIMENT", eid, "Each run must reference one declared experiment.")
        tool = refs(entity.get("instrument"))
        if len(tool) != 1 or "SoftwareApplication" not in types(entities.get(tool[0], {})):
            error("RUN_INSTRUMENT", eid, "Each run requires one declared SoftwareApplication.")
        agent = refs(entity.get("agent"))
        if len(agent) != 1 or not ({"Person", "Organization"} & set(types(entities.get(agent[0], {})))):
            error("RUN_AGENT", eid, "Each run requires one declared Person or Organization; identity is not authenticated.")
        time_origin = entity.get("cp:timestampOrigin")
        if not isinstance(time_origin, str) or time_origin not in {"DECLARED", "OBSERVED", "UNKNOWN"}:
            error("TIMESTAMP_ORIGIN", eid, "Timestamp origin must be DECLARED, OBSERVED or UNKNOWN.")
        for key in ("startTime", "endTime"):
            if key in entity and not _timestamp(entity[key]):
                error("TIMESTAMP", eid + "." + key, "Use a timezone-aware ISO 8601 timestamp; do not manufacture missing time.")
        if all(_timestamp(entity.get(k)) for k in ("startTime", "endTime")):
            if datetime.fromisoformat(entity["startTime"].replace("Z", "+00:00")) > datetime.fromisoformat(entity["endTime"].replace("Z", "+00:00")):
                error("TIME_ORDER", eid, "Run start time is after end time.")
        for key in ("cp:metrics", "cp:parameters", "object", "result"):
            values = entity.get(key, [])
            if not isinstance(values, list) or len(refs(values)) != len(values):
                error("RELATION_ARRAY", eid + "." + key, "This profile uses arrays of bare @id references.")
            if key in {"cp:metrics", "cp:parameters"}:
                for target in refs(values):
                    if "PropertyValue" not in types(entities.get(target, {})):
                        error("METRIC_REFERENCE", eid + "." + key, "Metrics and parameters must reference PropertyValue entities.")
        if eid not in refs(root.get("mentions")):
            error("RUN_INVENTORY", eid, "Run must be mentioned by the root dataset.")
        if not entity.get("startTime") and not entity.get("endTime"):
            warning("UNKNOWN_TIME", eid, "No run timestamp was supplied; the viewer must preserve unknown time.")
    # A derivation cycle is contradictory in the supported immutable snapshot model.
    derived = {eid: refs(e.get("prov:wasDerivedFrom")) for eid, e in entities.items()}
    seen: set[str] = set()
    active: set[str] = set()
    def visit(start: str) -> bool:
        stack = [(start, False)]
        while stack:
            eid, returning = stack.pop()
            if returning:
                active.discard(eid)
                seen.add(eid)
                continue
            if eid in active:
                return False
            if eid in seen:
                continue
            active.add(eid)
            stack.append((eid, True))
            stack.extend((parent, False) for parent in derived.get(eid, []) if parent in entities)
        return True
    for eid in entities:
        if eid not in seen and not visit(eid):
            error("DERIVATION_CYCLE", eid, "Immutable derivation graph contains a cycle.")
            break
    return report
