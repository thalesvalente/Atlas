"""Run pinned external RO-Crate validation and save a path-sanitized receipt.

Cache warming is an explicit optional operation using public standard URLs.
Validation itself always uses --offline. This is test tooling, not SDK runtime.
"""
from __future__ import annotations
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--profile", choices=["ro-crate-1.2", "ro-crate-1.3"], default="ro-crate-1.3")
    parser.add_argument("--warm-cache", action="store_true")
    parser.add_argument("--expect", choices=["valid", "invalid"], default="valid")
    args = parser.parse_args()
    if version("roc-validator") != "0.13.0":
        parser.error("Install exactly roc-validator==0.13.0 for this reference experiment.")
    base = args.source if args.source.is_dir() else args.source.parent
    if args.output.resolve().is_relative_to(base.resolve()):
        parser.error("The derived receipt must be outside the source package.")
    command = [sys.executable, "-c", "from rocrate_validator.cli import cli; cli()"]
    warm = None
    if args.warm_cache:
        invocation = command + ["cache", "warm", "--cache-path", str(args.cache), "--profile-identifier", args.profile]
        result = subprocess.run(invocation, text=True, capture_output=True, timeout=60)
        warm = {"requested": True, "exit_code": result.returncode,
                "scope": "Only public context/specification URLs declared by the selected upstream profile"}
        if result.returncode:
            print(result.stderr or result.stdout, file=sys.stderr)
            return result.returncode
    with tempfile.TemporaryDirectory(prefix="caderno-reference-") as temporary:
        raw = Path(temporary) / "reference.json"
        result = subprocess.run(command + ["validate", "--offline", "--cache-path", str(args.cache),
            "--profile-identifier", args.profile, "--no-auto-profile", "--skip-availability-check",
            "--output-format", "json", "--output-file", str(raw), str(args.source)],
            text=True, capture_output=True, timeout=60)
        if not raw.is_file():
            print(result.stderr or result.stdout, file=sys.stderr)
            return result.returncode or 2
        report = json.loads(raw.read_text(encoding="utf-8"))
    metadata = base / "ro-crate-metadata.json"
    summary = {
        "validator": "roc-validator", "version": "0.13.0", "profile": args.profile,
        "scope": "Upstream REQUIRED base-profile checks, offline; not Caderno or Process Run 0.6 certification",
        "source_metadata_sha256": hashlib.sha256(metadata.read_bytes()).hexdigest(),
        "passed": report["passed"], "exit_code": result.returncode,
        "expected": args.expect, "expectation_met": bool(report["passed"]) == (args.expect == "valid"),
        "offline": True, "metadata_only": False, "web_availability_checked": False,
        "cache_warm": warm,
        "statistics": {k: v for k, v in report["statistics"].items() if not k.startswith("started") and not k.startswith("finished") and k != "duration"},
        "skipped": [{"check": x["name"], "reason": x["message"], "category": x["category"]} for x in report["skipped_check_details"]],
        "issues": [{"check": x["check"]["name"], "message": x["message"], "severity": x["severity"]} for x in report["issues"]],
        "limitations": ["No proof of remote payload availability", "No authenticity or scientific acceptance evaluation", "Process Run 0.6 has no matching profile in this reference release"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": summary["passed"], "expectation_met": summary["expectation_met"],
                      "pass": summary["statistics"]["total_passed_checks"], "fail": summary["statistics"]["total_failed_checks"],
                      "skip": summary["statistics"]["total_skipped_checks"]}))
    return 0 if summary["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
