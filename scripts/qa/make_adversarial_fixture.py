"""Create NEW synthetic UI input via the public environmental producer.

Adds HTML-looking labels, repeated metric identity and incompatible units.
These fixtures exercise regression behavior; no observations are real.
"""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    subprocess.run([sys.executable, "-I", str(args.repo.resolve() / "examples/environmental/export.py"), str(args.output)], check=True)
    metadata = args.output / "ro-crate-metadata.json"
    document = json.loads(metadata.read_text(encoding="utf-8"))
    entities = {e["@id"]: e for e in document["@graph"]}
    runs = [e for e in document["@graph"] if e["@type"] == "CreateAction"]
    runs[0]["name"] = '<img src="https://example.invalid/qa" onerror="window.__atlasQA=1"> Rótulo sintético'
    runs[0]["description"] = '<script>window.__atlasQA=1</script> Texto não confiável de teste'
    original = entities[runs[0]["cp:metrics"][0]["@id"]]
    repeated = deepcopy(original)
    repeated["@id"] += "-qa-repeated"
    repeated["value"] = 999.25
    document["@graph"].append(repeated)
    runs[0]["cp:metrics"].append({"@id": repeated["@id"]})
    runs[0]["result"].append({"@id": repeated["@id"]})
    exact = {"@id": original["@id"] + "-qa-exact-integer", "@type": "PropertyValue",
             "name": "Inteiro exato sintético", "propertyID": "urn:qa:quantity:exact-integer",
             "value": 9007199254740993, "unitText": "1", "cp:valueType": "integer"}
    document["@graph"].append(exact)
    runs[0]["cp:metrics"].append({"@id": exact["@id"]})
    runs[0]["result"].append({"@id": exact["@id"]})
    entities[runs[1]["cp:metrics"][0]["@id"]]["unitText"] = "K"
    metadata.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
