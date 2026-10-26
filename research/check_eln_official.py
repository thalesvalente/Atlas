"""Run four pinned upstream ELN checks on the generated synthetic prototype.

Supply a checkout of the public ELN commit listed in the research report.
The upstream parser extracts its input into temporary directories: this research
harness is for our generated synthetic archive, not the application's reader.
The fifth upstream check targets RO-Crate 1.1 and is deliberately not invoked.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
from importlib.metadata import version
import json
from pathlib import Path

COMMIT = "2379f5131d543cd8a771a06403de9fb427039a91"
PINS = {"checks.py": "5736114ca2394737feffd4af6e6634429ec215a0a61edd0c8ae7b92587e0e07d",
        "schema.json": "aa4a58d2a579b75c3bc4d609f8d9073e7864f7bd4c3f10def69ea97fb11d1e75"}
VERSIONS = {"rocrate": "0.14.0", "jsonschema": "4.25.1", "roc-validator": "0.13.0"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path, help="Public ELN repository checkout")
    parser.add_argument("archive", type=Path, help="Generated synthetic.eln")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    for name, expected in VERSIONS.items():
        if version(name) != expected:
            parser.error(f"This experiment requires {name}=={expected}.")
    for name, expected in PINS.items():
        if hashlib.sha256((args.upstream / "tests" / name).read_bytes()).hexdigest() != expected:
            parser.error(f"Upstream {name} does not match the pinned public source.")
    if args.output.resolve() == args.archive.resolve() or args.output.resolve().is_relative_to(args.upstream.resolve()):
        parser.error("Write the derived receipt outside the upstream checkout and source archive.")
    spec = importlib.util.spec_from_file_location("eln_upstream_checks", args.upstream / "tests/checks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    for label, check in module.ALL_CHECKS[:4]:
        passed, details = check(args.archive)
        checks.append({"check": label, "passed": passed, "details": details})
    receipt = {"source": f"https://github.com/TheELNConsortium/TheELNFileFormat/blob/{COMMIT}/tests/checks.py",
               "library_versions": VERSIONS, "checks": checks,
               "scope": "Official first four checks only; checkValidator pins RO-Crate1.1 and was not used. External base1.2 report is separate.",
               "synthetic_only": True,
               "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
               "source_checks_sha256": PINS["checks.py"], "source_schema_sha256": PINS["schema.json"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "passed": sum(x["passed"] for x in checks)}))
    return 0 if all(x["passed"] for x in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
