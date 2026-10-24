"""Independent synthetic environmental producer using the published candidate.

Run: python examples/environmental/export.py /new/output/directory
No observations are real. Does not read R4, hidden directories, or a provider.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from caderno_protocol import CONTEXT, NS, PROCESS_PROFILE, PROFILE_ID, PROFILE_VERSION
from caderno_protocol.model import ACTION_STATUS, RO_CRATE


def ref(value: str) -> dict[str, str]:
    return {"@id": value}


def identifier(name: str) -> str:
    return "urn:caderno:synthetic-environment:" + name


def build_document() -> tuple[dict, dict[str, bytes]]:
    payloads = {
        "data/water.csv": b"synthetic,temperature_degC\ntrue,24.5\ntrue,24.8\n",
        "data/calibration.csv": b"synthetic,reference_degC\ntrue,25.0\n",
        "data/partial.csv": b"synthetic,status\ntrue,partial-result\n",
    }
    projects = [("water", "Águas — demonstração sintética"), ("calibration", "Calibração — demonstração sintética")]
    experiments = [("river", "water", "Comparação de temperatura"),
                   ("nutrient", "water", "Nutrientes — ensaio interrompido"),
                   ("sensor", "calibration", "Verificação de sensor sem data conhecida")]
    graph = [
        {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": ref("./"), "conformsTo": ref(RO_CRATE)},
        {"@id": "./", "@type": "Dataset", "name": "Caderno ambiental sintético",
         "description": "Dados inventados exclusivamente para testar interoperabilidade. Nenhuma medição representa o mundo real.",
         "datePublished": "2026-10-24", "license": "Rights not granted; synthetic review candidate only. No software license is selected by this metadata.",
         "conformsTo": [ref(PROCESS_PROFILE), ref(PROFILE_ID)], "hasPart": [], "mentions": [],
         "cp:synthetic": True, "cp:timestampOrigin": "DECLARED"},
        {"@id": PROCESS_PROFILE, "@type": ["CreativeWork", "http://www.w3.org/ns/dx/prof/Profile"], "name": "Process Run Crate", "version": "0.6"},
        {"@id": PROFILE_ID, "@type": ["CreativeWork", "http://www.w3.org/ns/dx/prof/Profile"], "name": "Caderno candidate profile", "version": PROFILE_VERSION},
        {"@id": identifier("software"), "@type": "SoftwareApplication", "name": "Gerador ambiental sintético", "version": "0.1.0a1", "url": "https://github.com/thalesvalente/Atlas/tree/main/examples/environmental"},
        {"@id": identifier("agent"), "@type": "Organization", "name": "Equipe fictícia de demonstração"},
    ]
    for name, title in projects:
        graph.append({"@id": identifier("project-" + name), "@type": ["Dataset", "cp:Project"],
                      "name": title, "description": "Projeto fictício para testes do contrato público."})
    for name, project, title in experiments:
        graph.append({"@id": identifier("experiment-" + name), "@type": ["Dataset", "cp:Experiment"],
                      "name": title, "description": "Experimento inteiramente sintético.",
                      "isPartOf": ref(identifier("project-" + project))})
    for path, data in payloads.items():
        graph.append({"@id": path, "@type": "File", "name": path, "encodingFormat": "text/csv",
                      "cp:availability": "PRESENT", "cp:sha256": hashlib.sha256(data).hexdigest(), "contentSize": len(data)})
    graph.extend([
        {"@id": "https://example.invalid/synthetic-large-data.csv", "@type": "File", "name": "Grande arquivo externo — não baixado", "cp:availability": "EXTERNAL", "encodingFormat": "text/csv"},
    ])
    run_specs = [
        ("r1", "river", "Coleta simulada A", "COMPLETED", "UNKNOWN", 24.5, "degC", "temperature", "2026-10-24T09:00:00Z", "2026-10-24T09:01:00Z", ["data/water.csv"], []),
        ("r2", "river", "Coleta simulada B — parcial", "PARTIAL", "HOLD", 24.8, "degC", "temperature", "2026-10-24T10:00:00Z", "2026-10-24T10:01:00Z", ["data/partial.csv"], [identifier("run-r1")]),
        ("r3", "nutrient", "Ensaio simulado — falha", "FAILED", "HOLD", None, "mg/L", "nitrate", "2026-10-24T11:00:00Z", "2026-10-24T11:00:10Z", [], []),
        ("r4", "sensor", "Estado desconhecido do sensor fictício", "UNKNOWN", "UNKNOWN", None, "degC", "temperature", None, None, ["https://example.invalid/synthetic-large-data.csv"], []),
    ]
    for name, exp, title, status, review, value, unit, prop, started, ended, outputs, derived in run_specs:
        metric = {"@id": identifier("metric-" + name), "@type": "PropertyValue", "name": prop,
                  "propertyID": "urn:environmental:quantity:" + prop, "value": value, "unitText": unit,
                  "cp:valueType": "number", "cp:precision": 1}
        if value is None:
            metric["cp:missingReason"] = "Medição sintética não produzida neste cenário."
        parameter = {"@id": identifier("parameter-" + name), "@type": "PropertyValue", "name": "Janela de amostragem",
                     "propertyID": "urn:environmental:parameter:sample-window", "value": 60, "unitText": "s", "cp:valueType": "integer"}
        run = {"@id": identifier("run-" + name), "@type": "CreateAction", "name": title,
               "description": "Execução fictícia do produtor ambiental independente.",
               "instrument": ref(identifier("software")), "agent": ref(identifier("agent")),
               "cp:experiment": ref(identifier("experiment-" + exp)), "cp:executionStatus": status,
               "cp:reviewStatus": review, "cp:synthetic": True, "cp:timestampOrigin": "DECLARED" if started else "UNKNOWN",
               "actionStatus": ref(ACTION_STATUS[status]), "object": [ref("data/calibration.csv")],
               "result": [ref(x) for x in outputs] + [ref(metric["@id"])],
               "cp:metrics": [ref(metric["@id"])], "cp:parameters": [ref(parameter["@id"])],
               "prov:wasDerivedFrom": [ref(x) for x in derived]}
        if started:
            run["startTime"] = started
        if ended:
            run["endTime"] = ended
        graph.extend([metric, parameter, run])
    root = graph[1]
    root["hasPart"] = [ref(e["@id"]) for e in graph if e["@id"] != "./" and any(t in (e["@type"] if isinstance(e["@type"], list) else [e["@type"]]) for t in ("Dataset", "File"))]
    root["mentions"] = [ref(e["@id"]) for e in graph if e["@type"] == "CreateAction"]
    return {"@context": deepcopy(CONTEXT), "@graph": graph}, payloads


def export(output: str | Path) -> Path:
    destination = Path(output)
    # Export only to a new explicitly selected directory. Never rewrite snapshots.
    destination.mkdir(parents=True, exist_ok=False)
    document, payloads = build_document()
    for name, data in payloads.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (destination / "ro-crate-metadata.json").write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    args = parser.parse_args()
    export(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
