#!/usr/bin/env python3
"""Fail-closed CI gate for public P01 worksheets and public reader only."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
P01 = "docs/missions/atlas-parity-02/p01-contracts"
C3 = "docs/missions/atlas-parity-03/c3-contract-gate"
CONTRACT = "docs/contracts/atlas-parity-02/p01"
BASE = "c2d00fb137cac1d62d6b7cb045ddbe055355a4c5"
TECH = "3a308ee78e185912959920d85a97cd511a70a764"
TECH_TREE = "03894a33271c030a72ccb7b016aeed943b11f525"
DOCUMENT = "2cd0e4686fb7456cb7c114bd778bb32a6bd9fad7"
DOC_TREE = "e27541f68039dc09b3e29198be937f50978752a2"
MANIFEST_HASH = "88f64b8ab62d60e4355a3f29553173638f4d7e3844ce0e8126dc1484713c353c"
POPULATION = {"EXISTING": 11, "PARTIAL": 10, "REPRESENTABLE_NOT_PRESENTED": 3,
              "NOT_REPRESENTED_CURRENT_CONTRACT": 3, "UNKNOWN_UPSTREAM": 1}

class GateFailure(Exception):
    pass

def demand(ok, why):
    if not ok:
        raise GateFailure(why)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=False, env={**os.environ, "PYTHONUTF8": "1"})

def git(*cmd):
    p = run(["git", *cmd])
    demand(p.returncode == 0, "git error: " + p.stderr[-400:])
    return p.stdout.strip()

def tree(ref, path):
    entries = git("ls-tree", "-r", ref, "--", path).splitlines()
    return {name: meta.split()[-1] for meta, name in (line.split("\t", 1) for line in entries)}

def manifest(path, expected=None):
    values = {}
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  ([^\r\n]+)", line)
        demand(match is not None, "Malformed manifest: " + path)
        sha, name = match.groups()
        demand(name not in values and not name.startswith("/") and "\\" not in name
               and ".." not in Path(name).parts and (ROOT / name).is_file(),
               "Missing, unsafe or repeated path: " + name)
        demand(digest(ROOT / name) == sha, "SHA256 mismatch: " + name)
        values[name] = sha
    demand(path not in values and (expected is None or len(values) == expected),
           "Manifest size or self-inclusion violation: " + path)
    return values

def verify_inputs():
    head = git("rev-parse", "HEAD")
    demand(git("rev-parse", TECH + "^{tree}") == TECH_TREE and
           git("rev-parse", DOCUMENT + "^{tree}") == DOC_TREE, "P01 source trees changed")
    demand(run(["git", "merge-base", "--is-ancestor", DOCUMENT, head]).returncode == 0,
           "C3 head must descend from documented P01 head")
    original = P01 + "/MANIFEST.sha256"
    demand(digest(ROOT / original) == MANIFEST_HASH, "P01 manifest checksum differs")
    files = manifest(original, 82)
    handoff = json.loads((ROOT / P01 / "HANDOFF.json").read_text(encoding="utf-8"))
    demand(len(handoff["paths_changed"]) == 83 and
           set(handoff["paths_changed"]) == set(files) | {original},
           "P01 83-path handoff differs from 82 file hashes")
    demand(all(p.startswith((P01 + "/", CONTRACT + "/",
           "specs/004-atlas-parity-c0/workstreams/p01-contracts/")) for p in files),
           "P01 original manifest escaped roots")
    old, now = tree(TECH, CONTRACT), tree("HEAD", CONTRACT)
    demand(len(old) == 51 and all(now.get(p) == h for p, h in old.items()),
           "Technical contract/fixtures/validator bytes differ from TECH")
    demand(handoff["tested_documentary_payload"]["sha"] == TECH and
           handoff["tested_documentary_payload"]["tree"] == TECH_TREE,
           "P01 handoff technical binding absent")
    cases = json.loads((ROOT / CONTRACT / "examples/cases.json").read_text(encoding="utf-8"))["cases"]
    demand(len(cases) == 46 and len({r["id"] for r in cases}) == 46 and
           sum(r["expected_valid"] is True for r in cases) == 11, "46-case manifest drift")
    overflow = [r for r in cases if r["id"] == "negative-json-numeric-overflow"]
    demand(len(overflow) == 1 and overflow[0]["expected_errors"] == ["JSON_NONFINITE"] and
           "1e999" in (ROOT / CONTRACT / "examples" / overflow[0]["file"]).read_text(encoding="utf-8"),
           "1e999 regression negative lost")
    own = manifest(C3 + "/MANIFEST.sha256", 11)
    extras = {CONTRACT + "/run_contract_gate.py",
              ".github/workflows/atlas-parity03-contracts.yml",
              "specs/004-atlas-parity-c0/workstreams/p01-contracts/c3-contract-gate.md"}
    demand(all(p.startswith(C3 + "/") or p in extras for p in own),
           "C3 manifest includes foreign root")
    return {"head_sha": head, "p01_manifest_hash": MANIFEST_HASH, "checked_p01_hashes": 82,
            "p01_handoff_paths": 83, "technical_blobs_unchanged": 51, "checked_c3_hashes": 11}

def verify_matrix():
    with (ROOT / P01 / "CAPABILITY-PARITY.csv").open(encoding="utf-8", newline="") as f:
        original = {row["capability_id"]: row for row in csv.DictReader(f)}
    with (ROOT / C3 / "TRACEABILITY-MATRIX.csv").open(encoding="utf-8", newline="") as f:
        received = list(csv.DictReader(f))
    demand(len(original) == 28 and len(received) == 28 and
           {r["p01_id"] for r in received} == set(original) and
           len({r["p01_id"] for r in received}) == 28, "P01 matrix requires 28 distinct matching IDs")
    counts = dict.fromkeys(POPULATION, 0)
    for r in received:
        source = original[r["p01_id"]]
        for dest, key in (("journey", "journey"), ("p01_status", "current_support"),
                          ("p01_contract_class", "contract_class"), ("p01_next_task", "proposed_task"),
                          ("p01_owner", "owner")):
            demand(r[dest] == source[key], "Changed P01 meaning: " + r["p01_id"] + "/" + key)
        counts[r["p01_status"]] += 1
        demand(r["baseline_evidence_sha"] == BASE and r["p01_evidence_sha"] == DOCUMENT and
               r["upstream"] == "UNKNOWN_UPSTREAM", "Unpinned evidence/upstream")
        for area, key, expected in (("p02_applicability", "p02_code_sha",
                                     "b443f9eb25f118e6a68c2ad17c8e21ab7aa99990"),
                                    ("p03_applicability", "p03_code_sha",
                                     "6c412c36e1dbe11711daa15c6d8727fbe94fa0ad")):
            demand(r[key] == (expected if r[area] != "NOT_APPLICABLE" else "NOT_APPLICABLE"),
                   "P02/P03 code SHA misbinding: " + r["p01_id"])
        demand(r["test_scope"].strip() and r["actual_gap"].strip() and r["next_act_owner"].strip(),
               "No test/gap/owner for journey: " + r["p01_id"])
        demand(r["p06_c1_c2_test_state"] in {"NOT_VERIFIED_AT_C3", "BASELINE_REGRESSION_ONLY"},
               "C1/C2/P06 test overclaim")
        if r["p01_status"] == "UNKNOWN_UPSTREAM":
            demand(r["actual_gap"].startswith("UNKNOWN_UPSTREAM"), "Upstream promoted")
    demand(counts == POPULATION, "P01 populations changed")
    return {"journeys": 28, "status_counts": counts, "upstream": "UNKNOWN_UPSTREAM",
            "complete_parity_denominator": None, "ratio_for_0_over_0": None}

def execute_mode(mode, dest):
    python = [sys.executable, "-B"] + (["-O"] if mode == "optimized" else [])
    result = run(python + [CONTRACT + "/validate_examples.py", "--suite"])
    demand(result.returncode == 0, mode + ": P01 suite: " + (result.stderr + result.stdout)[-750:])
    suite = json.loads(result.stdout)
    cases, probes = suite["cases"], suite["reader_probes"]
    demand(suite["status"] == "PASS" and len(cases) == 46 and len(probes) == 9 and
           suite["positive_examples"] == 11 and suite["negative_examples"] == 35 and
           len({r["id"] for r in cases}) == 46 and len({r["id"] for r in probes}) == 9 and
           all(r["status"] == "PASS" for r in cases + probes), mode + ": failed/skipped/colliding P01 cases")
    demand(next(x for x in cases if x["id"] == "negative-json-numeric-overflow")["errors"] ==
           ["JSON_NONFINITE"], mode + ": numeric overflow was accepted")
    regression = run(python + ["-m", "unittest", "discover", "-s", "tests/viewer",
                               "-p", "test_related_references.py", "-v"])
    log = regression.stdout + regression.stderr
    found = re.search(r"Ran (\d+) tests? in", log)
    demand(regression.returncode == 0 and found is not None and int(found.group(1)) == 11
           and re.search(r"\bOK\b", log) and not re.search(r"\.\.\.\s+skipped\b|skipped=", log),
           mode + ": regression tests failed/skipped: " + log[-750:])
    audit = run(python + ["scripts/qa/architecture_audit.py", ".", "--protocol",
                          "packages/protocol/src/caderno_protocol", "--viewer",
                          "packages/atlas/src/atlas_viewer", "--viewer-module", "atlas_viewer"])
    demand(audit.returncode == 0, mode + ": architecture exit: " + audit.stderr[-750:])
    arch = json.loads(audit.stdout)
    demand(arch.get("status") == "PASS_SCOPED" and arch.get("findings") == [],
           mode + ": architecture gate failed")
    normalized = {"p01": suite, "regression": {"tests": 11, "failures": 0, "skips": 0},
                  "architecture": arch}
    canonical = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    hashvalue = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "report.json").write_text(json.dumps({"mode": mode, "normalized_sha256": hashvalue,
        "unique_cases": 46, "unique_reader_probes": 9, "related_reference_regressions": 11,
        "skips": 0, "details": normalized}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = ET.Element("testsuites")
    for label, collection in (("P01-cases", cases), ("P01-probes", probes)):
        group = ET.SubElement(report, "testsuite", name=label, tests=str(len(collection)),
                              failures="0", errors="0", skipped="0")
        for item in collection:
            ET.SubElement(group, "testcase", classname=label, name=item["id"])
    group = ET.SubElement(report, "testsuite", name="reference-regressions-and-architecture",
                          tests="12", failures="0", errors="0", skipped="0")
    for i in range(11):
        ET.SubElement(group, "testcase", classname="reference", name=f"case-{i+1:02d}")
    ET.SubElement(group, "testcase", classname="architecture", name="PASS_SCOPED")
    ET.ElementTree(report).write(dest / "junit.xml", encoding="utf-8", xml_declaration=True)
    return hashvalue

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, default=Path(".ci-p01-contracts"))
    output = (ROOT / cli.parse_args().output).resolve()
    if not output.is_relative_to(ROOT):
        raise SystemExit("Output outside repository denied")
    output.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "FAIL", "errors": [], "scope": "P01_PUBLIC_C0_DOCUMENTARY",
               "approval_scientific": False, "authentication_attested": False,
               "reasoning_effective": "UNVERIFIED"}
    try:
        receipt["inputs"] = verify_inputs()
        receipt["traceability"] = verify_matrix()
        results = {}
        for mode in ("normal", "optimized"):
            try:
                results[mode] = execute_mode(mode, output / mode)
            except (GateFailure, ValueError, OSError, KeyError, StopIteration) as error:
                receipt["errors"].append(mode + ": " + str(error))
        receipt["mode_report_hashes"] = results
        demand(len(results) == 2 and results["normal"] == results["optimized"],
               "Normal and -O results absent or not deterministic")
        demand(not receipt["errors"], "At least one mode failed")
        receipt["status"] = "PASS"
    except (GateFailure, ValueError, OSError, KeyError) as error:
        receipt["errors"].append(str(error))
    (output / "gate-receipt.json").write_text(json.dumps(receipt, sort_keys=True,
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "errors": receipt["errors"],
                      "head_sha": receipt.get("inputs", {}).get("head_sha"),
                      "mode_hashes": receipt.get("mode_report_hashes")}, ensure_ascii=False))
    return 0 if receipt["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
