"""Reproduce the synthetic RO-Crate versus ELN representation experiment.

The ELN result is an alternative prototype, never a supported Atlas profile.
This script only writes new synthetic outputs below the supplied directory.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import zipfile

from caderno_protocol import Package, ValidationReport, to_read_model


def compare(destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("environmental_export", root / "examples/environmental/export.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original, payloads = module.build_document()
    crate_dir = destination / "crate-1.3"
    crate_dir.mkdir()
    eln_dir = destination / "eln-1.2"
    eln_dir.mkdir()
    alternate = deepcopy(original)
    alternate["@context"][0] = "https://w3id.org/ro/crate/1.2/context"
    metadata = alternate["@graph"][0]
    metadata["conformsTo"] = {"@id": "https://w3id.org/ro/crate/1.2"}
    metadata["version"] = "1.2+20260923"
    metadata["sdPublisher"] = {"@id": module.identifier("agent")}
    # Do not falsely declare a 1.3-dependent profile on a 1.2 ELN crate.
    alternate["@graph"][1].pop("conformsTo")
    for directory, document in [(crate_dir, original), (eln_dir, alternate)]:
        for name, data in payloads.items():
            (directory / name).parent.mkdir(parents=True, exist_ok=True)
            (directory / name).write_bytes(data)
        (directory / "ro-crate-metadata.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = destination / "synthetic.eln"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(eln_dir.rglob("*")):
            if path.is_file():
                output.write(path, "synthetic.eln/" + path.relative_to(eln_dir).as_posix())
    a = to_read_model(Package(original, "", ValidationReport()))
    b = to_read_model(Package(alternate, "", ValidationReport()))
    keys = ["projects", "experiments", "runs", "relations"]
    comparison = {"synthetic_only": True, "projection_comparison_is_not_validation": True,
                  "equivalent_fields": {k: a[k] == b[k] for k in keys},
                  "counts": {k: len(a[k]) for k in keys},
                  "ro_crate": "1.3 / Process Run 0.6 / Caderno 0.1.0a1 candidate",
                  "eln": "1.2+20260923 / RO-Crate 1.2 / extensions retained; no Process Run 0.6 claim",
                  "losses_without_extensions": ["review status", "partial/unknown execution", "typed missing-value reason", "timestamp origin", "declared availability"],
                  "semantic_identity_claim": "Only selected domain facts match. JSON-LD contexts and profile declarations differ; byte or full RDF equality is not claimed."}
    (destination / "comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return comparison


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    result = compare(parser.parse_args().output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(result["equivalent_fields"].values()) else 1)
