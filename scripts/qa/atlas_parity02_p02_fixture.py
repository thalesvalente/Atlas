"""Build two NEW, deterministic, public synthetic Caderno packages for C0 QA.

This generator consumes no producer, host or historical data. The fixture has
28 runs (14 per source); that is test coverage, not a product limit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from caderno_protocol import CONTEXT, PROCESS_PROFILE, PROFILE_ID, load_package, validate_document

PREFIX = "urn:atlas:synthetic:parity02:p02:"
STATUSES = ("COMPLETED", "PARTIAL", "FAILED", "RUNNING", "UNKNOWN")
REVIEWS = ("UNKNOWN", "HOLD", "REJECTED", "NOT_APPLICABLE")
ACTION_STATUS = {
    "COMPLETED": "http://schema.org/CompletedActionStatus",
    "PARTIAL": "http://schema.org/FailedActionStatus",
    "FAILED": "http://schema.org/FailedActionStatus",
    "RUNNING": "http://schema.org/ActiveActionStatus",
    "UNKNOWN": "http://schema.org/PotentialActionStatus",
}
PAYLOAD = b"sample,value\nsynthetic,1.25\n"
ADVERSARIAL = '<img src="https://example.invalid/p02.png" onerror="window.__atlasP02QA=1">'


def ref(identifier: str) -> dict[str, str]:
    return {"@id": identifier}


def document(label: str) -> dict:
    """All entity IDs repeat between sources; their declared content differs."""
    if label not in {"A", "B"}:
        raise ValueError("Synthetic label must be A or B")
    graph = [
        {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": ref("./"),
         "conformsTo": ref("https://w3id.org/ro/crate/1.3")},
        {"@id": "./", "@type": "Dataset", "name": f"Coorte sintética — fonte {label}",
         "description": "Fixture pública gerada para C0. Recorte e universo de origem não declarados.",
         "license": "https://creativecommons.org/publicdomain/zero/1.0/",
         "datePublished": "2026-10-27", "conformsTo": [ref(PROCESS_PROFILE), ref(PROFILE_ID)],
         "hasPart": [], "mentions": []},
        *[{"@id": profile, "@type": ["CreativeWork", "http://www.w3.org/ns/dx/prof/Profile"],
           "name": "Perfil público fixado"} for profile in (PROCESS_PROFILE, PROFILE_ID)],
        {"@id": PREFIX + "producer", "@type": "Organization", "name": "Produtor de fixtures sintéticas"},
        {"@id": PREFIX + "software", "@type": "SoftwareApplication", "name": "Gerador público C0",
         "version": "fixture-1", "url": "https://example.invalid/synthetic-p02"},
        {"@id": PREFIX + "note", "@type": "CreativeWork", "name": f"Nota da fonte {label}",
         "description": "Menção de contexto, sem relação causal, consumo ou produção."},
        {"@id": "javascript:window.__atlasP02QA=1", "@type": "CreativeWork",
         "name": ADVERSARIAL + " " + label,
         "description": '<script>window.__atlasP02QA=1</script> file:///not-requested.txt'},
        {"@id": "data/input.csv", "@type": "File", "name": "Entrada sintética " + label,
         "encodingFormat": "text/csv", "cp:availability": "PRESENT", "contentSize": len(PAYLOAD),
         "cp:sha256": hashlib.sha256(PAYLOAD).hexdigest()},
        {"@id": "data/output.csv", "@type": "File", "name": "Saída não incluída " + label,
         "cp:availability": "MISSING", "cp:sha256": "a" * 64},
        {"@id": "https://example.invalid/p02-reference.txt", "@type": "File",
         "name": "Referência externa não acessada " + label, "cp:availability": "EXTERNAL",
         "cp:sha256": "b" * 64},
    ]
    for number in range(2):
        graph.append({"@id": PREFIX + f"project:{number}", "@type": ["Dataset", "cp:Project"],
                      "name": f"Projeto {number + 1} — {label}", "description": "Projeto sintético."})
    for number, family in enumerate(("Hidrologia", "Modelagem α", "Validação química")):
        graph.append({"@id": PREFIX + f"experiment:{number}", "@type": ["Dataset", "cp:Experiment"],
                      "name": f"{family} — fonte {label}", "isPartOf": ref(PREFIX + f"project:{number % 2}")})
    for number in range(14):
        eid = PREFIX + f"run:{number:02d}"
        name = f"Execução {number:02d} — {label}"
        if number == 6:
            name += " · Ação, água, 日本語, αβγ, 🧪 " + "TítuloSemEspaços" * 24
        if number == 7:
            name += " " + ADVERSARIAL
        run = {"@id": eid, "@type": "CreateAction", "name": name,
               "description": "Registro integralmente sintético. Não representa ciência aceita.",
               "cp:experiment": ref(PREFIX + f"experiment:{number % 3}"),
               "agent": ref(PREFIX + "producer"), "instrument": ref(PREFIX + "software"),
               "cp:executionStatus": STATUSES[number % len(STATUSES)],
               "actionStatus": ref(ACTION_STATUS[STATUSES[number % len(STATUSES)]]),
               "cp:reviewStatus": REVIEWS[number % len(REVIEWS)], "cp:synthetic": True,
               "cp:timestampOrigin": ("UNKNOWN" if number in {8, 10, 13} else "OBSERVED" if number == 9 else "DECLARED"),
               "cp:metrics": [], "cp:parameters": [], "object": [], "result": []}
        if number not in {8, 10, 13}:
            run["startTime"] = f"2026-10-{number + 1:02d}T10:00:00-03:00"
            run["endTime"] = f"2026-10-{number + 1:02d}T10:05:00-03:00"
        elif number == 10:
            run["endTime"] = "2026-10-11T10:05:00-03:00"
            run["cp:timestampOrigin"] = "DECLARED"
        if number % 4 != 3 and number != 8:
            metric = {"@id": PREFIX + f"metric:{number:02d}", "@type": "PropertyValue",
                      "propertyID": "urn:synthetic:concentration", "name": "Concentração",
                      "cp:valueType": "number", "unitText": "mg/L", "cp:precision": 3,
                      "value": (number + 1) * 1.25 + (0.5 if label == "B" else 0)}
            if number == 1:
                metric["unitText"] = "µg/L"
            elif number == 2:
                metric.update({"cp:valueType": "integer", "value": 3, "cp:precision": 0})
            elif number == 4:
                metric.update({"value": None, "cp:missingReason": "Não medido; desconhecido não é zero"})
            elif number == 5:
                metric.update({"propertyID": "urn:synthetic:exact-count", "name": "Contagem exata",
                               "cp:valueType": "integer", "unitText": "1", "value": 9007199254740993,
                               "cp:precision": 0})
            elif number == 12:
                metric["cp:precision"] = 9007199254740993
            graph.append(metric)
            run["cp:metrics"].append(ref(metric["@id"]))
        if number % 3 == 0:
            parameter = {"@id": PREFIX + f"parameter:{number:02d}", "@type": "PropertyValue",
                         "propertyID": "urn:synthetic:method", "name": "Método", "cp:valueType": "string",
                         "value": "Método α — " + label}
            graph.append(parameter)
            run["cp:parameters"].append(ref(parameter["@id"]))
        if number not in {8, 10, 13}:
            run["object"] = [ref("data/input.csv")]
            run["result"] = [ref("data/output.csv")]
        if number in {2, 4, 6, 12}:
            run["prov:wasDerivedFrom"] = [ref(PREFIX + f"run:{number - 1:02d}")]
        if number % 2 == 0 and number != 8:
            run["mentions"] = [ref(PREFIX + "note"), ref(PREFIX + "run:01"),
                               ref("javascript:window.__atlasP02QA=1"),
                               ref("https://example.invalid/p02-reference.txt"), ref("data/output.csv")]
        graph.append(run)
    root = graph[1]
    root["hasPart"] = [ref(e["@id"]) for e in graph if e["@id"] != "./" and
                       (e["@type"] == "File" or isinstance(e["@type"], list) and "Dataset" in e["@type"])]
    root["mentions"] = [ref(e["@id"]) for e in graph if e["@type"] == "CreateAction"]
    result = {"@context": CONTEXT, "@graph": graph}
    report = validate_document(result)
    if not report.valid:
        raise ValueError(report.to_dict())
    return result


def build(output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=False)
    sources = []
    for label in ("A", "B"):
        source = output / ("source-" + label.lower())
        (source / "data").mkdir(parents=True)
        (source / "data/input.csv").write_bytes(PAYLOAD)
        (source / "ro-crate-metadata.json").write_text(
            json.dumps(document(label), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        package = load_package(source)
        if not package.report.valid:
            raise ValueError(package.report.to_dict())
        sources.append(source)
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="A new destination; existing directories are never overwritten")
    args = parser.parse_args()
    for source in build(args.output):
        print(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
