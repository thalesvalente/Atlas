"""Installed main-application browser driver using newly generated synthetic copies.

Only Actions invokes this driver. The fixture driver changes one disposable
copy for package-replacement QA; inherited repository fixtures remain untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import threading

import atlas_viewer
import caderno_protocol
from atlas_viewer.catalog import Catalog
from atlas_viewer.server import ASSETS, make_server
from caderno_protocol import load_package, validate_document

ROOT = Path(__file__).resolve().parents[2]


def demand(value, message):
    if not value:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def fixture(label, generator):
    doc = generator.document(label)
    graph = doc["@graph"]
    run = next(item for item in graph if item.get("@id") == generator.PREFIX + "run:00")
    declarations = [
        ("exact", "integer", 9007199254740993, "1", "Inteiro exato"),
        ("small-unit", "number", 0.0000125, "µg/L", "Unidade incompatível"),
        ("absent", "number", None, "mg/L", "Ausência explícita"),
    ]
    for key, kind, value, unit, name in declarations:
        identifier = generator.PREFIX + "c4:" + key
        item = {"@id": identifier, "@type": "PropertyValue", "propertyID": "urn:synthetic:c4:" + key,
                "name": name, "cp:valueType": kind, "value": value, "unitText": unit, "cp:precision": 5}
        if value is None:
            item["cp:missingReason"] = "Não medido; desconhecido não é zero"
        graph.append(item)
        run["cp:metrics"].append({"@id": identifier})
    identifier = generator.PREFIX + "c4:boolean"
    graph.append({"@id": identifier, "@type": "PropertyValue", "propertyID": "urn:synthetic:c4:boolean",
                  "name": "Booleano declarado", "cp:valueType": "boolean", "value": False})
    run["cp:parameters"].append({"@id": identifier})
    for item in graph:
        if item.get("@id") == "data/output.csv":
            item["name"] = 'Arquivo .pdf <img src="https://example.invalid/c4.png" onerror="window.__c4QA=1"> 日本語 🧪 ' + "TítuloSemEspaços" * 16
            item["description"] = '<script>window.__c4QA=1</script> File declarado; não infere produto ou documento rico.'
    demand(validate_document(doc).valid, "Generated C4 fixture is not a valid protocol document")
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    work, output = args.work.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / "BROWSER-RECEIPT.json"
    for module in (atlas_viewer, caderno_protocol):
        location = Path(module.__file__).resolve()
        demand(not location.is_relative_to(ROOT)
               and location.is_relative_to(Path(sys.prefix).resolve()),
               "Browser driver must use SDK/viewer installed outside checkout")
    demand(sys.flags.isolated == 1 and importlib.util.find_spec("r4") is None,
           "Browser driver requires isolated installed modules without R4")
    spec = importlib.util.spec_from_file_location("c4_public_fixture_generator",
        ROOT / "scripts/qa/atlas_parity02_p02_fixture.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    case = work / "c4-generated-consumer"
    case.mkdir(exist_ok=False)
    sources = []
    for label in ("A", "B"):
        source = case / label
        (source / "data").mkdir(parents=True)
        (source / "data/input.csv").write_bytes(generator.PAYLOAD)
        (source / "ro-crate-metadata.json").write_text(
            json.dumps(fixture(label, generator), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        demand(load_package(source).report.valid, "Generated package failed SDK validation")
        sources.append(source)
    replacement = json.loads((sources[0] / "ro-crate-metadata.json").read_text(encoding="utf-8"))
    replacement = json.loads(json.dumps(replacement, ensure_ascii=False)
        .replace(generator.PREFIX, "urn:atlas:synthetic:c4:replacement:"))
    replacement["@graph"][1]["name"] += " SUBSTITUIDA"
    # Exceed only the optional P03 metadata presentation budget. The protocol
    # package stays valid and must remain readable when its presentation fails.
    for index in range(201):
        identifier = f"https://example.invalid/c4-unopened/{index}.dat"
        replacement["@graph"].append({"@id": identifier, "@type": "File",
            "name": f"Referência sintética externa {index}", "cp:availability": "EXTERNAL"})
        replacement["@graph"][1]["hasPart"].append({"@id": identifier})
    demand(validate_document(replacement).valid, "Replacement must stay valid")
    replacement_bytes = (json.dumps(replacement, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    replacement_file = case / "replacement.json"
    replacement_file.write_bytes(replacement_bytes)
    before = [hashes(source) for source in sources]
    expected = [dict(value) for value in before]
    expected[0]["ro-crate-metadata.json"] = sha(replacement_bytes)
    catalog = Catalog(sources)
    initial = catalog.snapshot()
    demand(all(source["report"]["valid"] and source["status"] == "READY"
               for source in initial["sources"]), "Both initial sources must be READY")
    server = make_server(catalog, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        command = ["node", str(ROOT / "scripts/qa/atlas_parity03_c4_browser.mjs"),
            "--url", f"http://127.0.0.1:{server.server_address[1]}", "--report", str(receipt_path),
            "--metadata", str(sources[0] / "ro-crate-metadata.json"), "--replacement", str(replacement_file),
            "--screenshots", str(output / "screenshots")]
        completed = subprocess.run(command, cwd=work / "outside-source", check=False, timeout=300)
        report = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {
            "status": "FAIL", "error": "Integrated browser produced no receipt"}
        unchanged = [hashes(source) for source in sources] == expected
        report.update(
            tested_sha=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            tested_tree=subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
            optimization=sys.flags.optimize, python=sys.version.split()[0], platform=sys.platform,
            consumer_outside_checkout=True, sdk_without_viewer_r4="SEPARATE_CLEAN_INSTALL_RECEIPT",
            viewer_without_r4=True, host_operation="NOT_RUN", inherited_fixtures_modified=False,
            synthetic_copy_change="ONE_DRIVER_METADATA_REPLACEMENT",
            synthetic_copy_bytes_match_expected=unchanged,
            synthetic_initial_sha256=before, synthetic_final_sha256=expected,
            installed_wheels=json.loads((work / "clean-install-report.json").read_text(encoding="utf-8"))["wheel_sha256"],
            screenshot_sha256={name: sha((output / "screenshots" / name).read_bytes())
                for name in report.get("screenshots", [])},
        )
        if completed.returncode or not unchanged or len(report["screenshot_sha256"]) < 4:
            report["status"] = "FAIL"
            report.setdefault("error", "Browser/copy immutability/screenshot gate failed")
        receipt_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("C4_BROWSER_RECEIPT=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")))
        print(json.dumps({key: report.get(key) for key in
            ("status", "tested_sha", "optimization", "synthetic_copy_bytes_match_expected", "error")}))
        return 0 if report["status"] == "PASS" else 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())

