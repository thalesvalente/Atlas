"""Produce a NEW public synthetic package for neutral-reference UI checks.

The two labels deliberately share every entity ID, while their local titles
differ. No source package or private producer is read or changed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--label", choices=["A", "B"], required=True)
    args = parser.parse_args()
    subprocess.run([sys.executable, "-I", str(args.repo.resolve() / "examples/environmental/export.py"),
                    str(args.output)], check=True)
    metadata = args.output / "ro-crate-metadata.json"
    document = json.loads(metadata.read_text(encoding="utf-8"))
    root = next(e for e in document["@graph"] if e["@id"] == "./")
    runs = [e for e in document["@graph"] if e.get("@type") == "CreateAction"]
    root["name"] = "Referências sintéticas — fonte " + args.label
    runs[0]["name"] = "Execução com referências " + args.label
    runs[1]["name"] = "Destino interno " + args.label
    references = [
        {"@id": "urn:atlas:synthetic:related:note", "@type": "CreativeWork",
         "name": "Nota da fonte " + args.label,
         "description": '<img src="https://example.invalid/related-image" onerror="window.__atlasRelatedQA=1"> Contexto sintético.'},
        {"@id": "urn:atlas:synthetic:related:" + "identifier" * 70, "@type": "CreativeWork",
         "description": "Sem título: manter o identificador completo com quebra de linha."},
        {"@id": "urn:atlas:synthetic:related:long-title", "@type": ["CreativeWork", "Text"],
         "name": "Título" * 80 + args.label,
         "description": "Título longo para verificar apresentação em largura estreita."},
        {"@id": "javascript:window.__atlasRelatedQA=1", "@type": "CreativeWork",
         "name": '<script>window.__atlasRelatedQA=1</script> ' + args.label,
         "description": "file:///unrequested/private.txt deve permanecer texto inerte."},
        {"@id": "urn:atlas:synthetic:related:non-text-title", "@type": "CreativeWork", "name": 42,
         "description": "Título não textual: apresentar o identificador declarado."},
        {"@id": "evidence/missing-related.txt", "@type": "File", "cp:availability": "MISSING",
         "cp:sha256": "a" * 64, "description": "Conteúdo não incluído no pacote sintético."},
        {"@id": "https://example.invalid/related-evidence.txt", "@type": "File",
         "name": "Referência externa não aberta", "cp:availability": "EXTERNAL", "cp:sha256": "b" * 64},
    ]
    document["@graph"].extend(references)
    root["hasPart"].extend({"@id": e["@id"]} for e in references if e["@type"] == "File")
    ids = [references[0]["@id"], runs[1]["@id"], "data/water.csv", "data/calibration.csv",
           *[e["@id"] for e in references[1:]], references[0]["@id"]]
    runs[0]["mentions"] = [{"@id": eid} for eid in ids]
    # A second accepted reference shape; later runs preserve the legacy empty state.
    runs[1]["mentions"] = {"@id": references[0]["@id"]}
    metadata.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
