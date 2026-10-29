"""Composition-only, exact-SHA gates; engineering execution belongs to Actions."""
from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "C1": ("326b92ae27effb6941801ed3e9af5c07aa90fb95", "7a9bbc1765bbbf3897760ccc50a0b22aec3ee239"),
    "C2": ("f625f8be40156fd9fe4572a0ac2074910efd96cf", "d60783a212b3593e7677ca8761557ad7b758e763"),
    "C3": ("c0b42a17710fdf3cef3ec4ea13c840796d57d18f", "928fec43fb493387a48789a226f59988587a19a2"),
}
P03 = "docs/missions/atlas-parity-02/p03-components"
C1 = "docs/missions/atlas-parity-03/c1-core-composition"
C2 = "docs/missions/atlas-parity-03/c2-p03-qualification"
C3 = "docs/missions/atlas-parity-03/c3-contract-gate"
C4 = "docs/missions/atlas-parity-03/c4-full-convergence"
COMPOSITION = "c120f8ae9e455e19b4e0bcd35f47ec0fd7a0117c"
COMPOSITION_TREE = "3f1f378a3e39b0f148effdc010177144fe29e7c4"
# The only C2 frozen-file override is its now-inapplicable shell-isolation
# assertion. The replacement asserts active representable P03 and inactive rich
# demonstrators; original bytes remain verified in the immutable C2 manifest.
P03_C4_ADAPTERS = {
    "tests/viewer/test_atlas_parity02_p03_harness.py":
        "3bed307fb7f9aec6b4d4929be2865a8344c66b3f0f2a7c0c9aa749661b9c7689",
}
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/parity02_p02_state.js": ("parity02_p02_state.js", "text/javascript; charset=utf-8"),
    "/parity02_p03_table.js": ("parity02_p03_table.js", "text/javascript; charset=utf-8"),
    "/parity02_p03_table.css": ("parity02_p03_table.css", "text/css; charset=utf-8"),
    "/parity02_p03_artifacts.js": ("parity02_p03_artifacts.js", "text/javascript; charset=utf-8"),
    "/parity02_p03_artifacts.css": ("parity02_p03_artifacts.css", "text/css; charset=utf-8"),
    "/parity03_p03_composition.js": ("parity03_p03_composition.js", "text/javascript; charset=utf-8"),
}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def git(*args, binary=False):
    value = subprocess.check_output(["git", *args], cwd=ROOT)
    return value if binary else value.decode("utf-8").strip()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity():
    return {
        "tested_sha": git("rev-parse", "HEAD"), "tested_tree": git("rev-parse", "HEAD^{tree}"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
        "python": platform.python_version(), "optimization": sys.flags.optimize,
        "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
        "actions_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "host_operation": "NOT_RUN", "scientific_approval": False,
    }


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def historical_manifest(ref, path, *, current=False, expected=None, adapters=None):
    raw = git("show", ref + ":" + path, binary=True)
    entries = {}
    for line in raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  ([^\r\n]+)", line)
        require(match is not None, "Malformed historical manifest: " + path)
        sha, name = match.groups()
        require(name not in entries and not name.startswith("/") and "\\" not in name
                and ".." not in Path(name).parts and name != path, "Unsafe/repeated manifest path: " + name)
        source = git("show", ref + ":" + name, binary=True)
        require(digest(source) == sha, "Historical manifest mismatch: " + ref + ":" + name)
        if current:
            target = ROOT / name
            matches = (digest(target.read_bytes()) == adapters[name]
                       if adapters and name in adapters and target.is_file()
                       else target.is_file() and target.read_bytes() == source)
            require(target.is_file() and not target.is_symlink() and matches,
                    "Frozen source changed in composition: " + name)
        entries[name] = sha
    require(expected is None or len(entries) == expected, "Historical manifest count changed: " + path)
    return {"source_sha": ref, "path": path, "sha256": digest(raw), "entries": len(entries),
            "current_bytes_required": current, "strict_current_adapters": dict(adapters or {})}


def tree(ref):
    result = {}
    for entry in git("ls-tree", "-r", "-z", ref, binary=True).split(b"\0"):
        if not entry:
            continue
        meta, raw = entry.split(b"\t", 1)
        mode, kind, oid = meta.split()
        require(kind == b"blob", "Embedded tree/gitlink is not an approved composition input")
        result[raw.decode("utf-8")] = oid.decode("ascii")
    return result


def inputs(output):
    report = {**identity(), "status": "FAIL", "scope": "C4_COMPOSED_INPUT_BINDING"}
    try:
        require(not git("status", "--porcelain", "--untracked-files=normal"),
                "Exact-SHA input evidence requires a clean checkout")
        for name, (sha, expected_tree) in INPUTS.items():
            require(git("rev-parse", sha + "^{tree}") == expected_tree, name + " tree differs")
            require(subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                                   cwd=ROOT).returncode == 0, name + " ancestry is absent")
        c1, c2, c3 = (INPUTS[name][0] for name in ("C1", "C2", "C3"))
        require(git("rev-parse", COMPOSITION + "^{tree}") == COMPOSITION_TREE
                and git("rev-list", "--parents", "-n", "1", COMPOSITION).split()[1:] == [c1, c2, c3],
                "Three-parent source composition differs")
        require(subprocess.run(["git", "merge-base", "--is-ancestor", COMPOSITION, "HEAD"],
                               cwd=ROOT).returncode == 0, "C4 must descend from its recorded source composition")
        report["historical_manifests"] = [
            historical_manifest(c1, C1 + "/MANIFEST.sha256", expected=283),
            historical_manifest(c2, C2 + "/MANIFEST.sha256"),
            historical_manifest(c2, P03 + "/MANIFEST.sha256", current=True, expected=56,
                                adapters=P03_C4_ADAPTERS),
            historical_manifest(c3, C3 + "/MANIFEST.sha256", current=True, expected=11),
            historical_manifest(c3, "docs/missions/atlas-parity-02/p01-contracts/MANIFEST.sha256",
                                current=True, expected=82),
        ]
        frozen = json.loads(git("show", c2 + ":" + P03 + "/evidence/FREEZE.json"))
        require(len(frozen["files"]) == 25, "P03 frozen inventory differs")
        for item in frozen["files"]:
            expected_hash = P03_C4_ADAPTERS.get(item["path"], item["sha256"])
            require(digest((ROOT / item["path"]).read_bytes()) == expected_hash,
                    "P03 frozen blob changed: " + item["path"])
        require(set(P03_C4_ADAPTERS) <= {item["path"] for item in frozen["files"]},
                "C4 contextual adapter must target exactly the declared frozen test")
        manifest_path = C4 + "/MANIFEST.sha256"
        own = historical_manifest("HEAD", manifest_path, current=True)
        declared = {line.split("  ", 1)[1] for line in
                    (ROOT / manifest_path).read_text(encoding="utf-8").splitlines()}
        authored = set(git("diff", "--name-only", COMPOSITION, "HEAD").splitlines()) - {manifest_path}
        require(declared == authored, "C4 manifest must cover every authored path, with no arbitrary exclusions")
        report["current_C4_manifest"] = {**own, "authored_paths": sorted(authored), "coverage_exact": True}
        baseline_csv = csv.DictReader(io.StringIO(git("show", c3 + ":" + C3 + "/TRACEABILITY-MATRIX.csv")))
        original_rows = {row["p01_id"]: row for row in baseline_csv}
        with (ROOT / C4 / "TRACEABILITY-MATRIX.csv").open(encoding="utf-8", newline="") as stream:
            composed_csv = csv.DictReader(stream)
            composed_rows = list(composed_csv)
        extra_columns = ["c4_scope", "c4_gate_state", "c4_sha_binding",
                         "study_c_attribution", "complete_legacy_denominator"]
        require(composed_csv.fieldnames == baseline_csv.fieldnames + extra_columns
                and len(composed_rows) == len(original_rows) == 28
                and {row["p01_id"] for row in composed_rows} == set(original_rows),
                "C4 traceability must preserve 28 distinct P01 journeys and all original columns")
        for row in composed_rows:
            require(all(row[name] == original_rows[row["p01_id"]][name] for name in baseline_csv.fieldnames),
                    "C4 altered a historical C3/P01 traceability statement: " + row["p01_id"])
            require(row["study_c_attribution"] == "NOT_ATTRIBUTED"
                    and row["complete_legacy_denominator"] == "UNKNOWN"
                    and all(row[name].strip() for name in extra_columns),
                    "C4 promoted an absent study or a complete-parity denominator")
        report["C4_traceability"] = {"journeys": 28, "original_columns_unchanged": True,
            "study_c_attribution": "NOT_ATTRIBUTED", "complete_legacy_denominator": "UNKNOWN"}
        originals = {name: tree(sha) for name, (sha, _) in INPUTS.items()}
        current = tree("HEAD")
        fixture_paths = {path for files in originals.values() for path in files
                         if path.startswith("tests/fixtures/")}
        require({path for path in current if path.startswith("tests/fixtures/")} == fixture_paths,
                "Composition may not add/remove inherited fixtures")
        for path in fixture_paths:
            expected = {files[path] for files in originals.values() if path in files}
            require(len(expected) == 1 and current[path] in expected,
                    "Inherited fixture byte mismatch: " + path)
        server = ast.parse((ROOT / "packages/atlas/src/atlas_viewer/server.py").read_text(encoding="utf-8"))
        assignments = [node for node in server.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "ASSETS" for target in node.targets)]
        require(len(assignments) == 1 and ast.literal_eval(assignments[0].value) == ASSETS,
                "Main server allowlist differs from the nine exact approved assets")
        for name in ("app.js", "parity03_p03_composition.js"):
            text = (ROOT / "packages/atlas/src/atlas_viewer/static" / name).read_text(encoding="utf-8")
            require(not re.search(r"\b(?:renderCandidate|validateCandidate)\b", text)
                    and "p03-candidate/1" not in text, "Rich demonstrator activated in main shell")
        require(not (ROOT / ".specify/feature.json").exists(), "Shared feature pointer unexpectedly present")
        audit_spec = importlib.util.spec_from_file_location("c4_frozen_audit",
            ROOT / "scripts/qa/atlas_parity02_p06_audit.py")
        audit = importlib.util.module_from_spec(audit_spec)
        audit_spec.loader.exec_module(audit)
        protected = audit.audit(ROOT)
        require(protected["status"] == "PASS_SCOPED" and not protected["errors"],
                "Protocol/public-source/governance bytes changed")
        origins = []
        for path, blob in sorted(current.items()):
            if originals["C1"].get(path) == blob:
                continue
            matches = [name for name, files in originals.items() if files.get(path) == blob]
            origins.append({"path": path, "candidate_blob": blob, "unchanged_input_blobs": matches,
                            "origin": matches[0] if matches else "C4_DELTA"})
        report.update(status="PASS", inputs={name: {"sha": sha, "tree": value}
                      for name, (sha, value) in INPUTS.items()}, p03_frozen_source_files=25,
                      p03_current_unchanged_files=24, p03_contextual_test_adapters=P03_C4_ADAPTERS,
                      inherited_fixture_files=len(fixture_paths), protected_inputs=protected,
                      composition_blob_origins=origins, assets=ASSETS, rich_demonstrators_active=False,
                      representable_P03_imports_declared=True,
                      main_application_browser_evidence="REQUIRED_SEPARATE_GATE",
                      historical_C1_C2_C3_results_are_current_C4_proof=False)
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    save(output / "INPUT-SHAS.json", report)
    print("C4_INPUT_SUMMARY=" + json.dumps({
        key: report.get(key) for key in ("status", "error", "tested_sha", "tested_tree", "inputs",
        "historical_manifests", "p03_frozen_source_files", "p03_current_unchanged_files",
        "p03_contextual_test_adapters", "inherited_fixture_files", "C4_traceability")},
        ensure_ascii=False, separators=(",", ":")))
    if "current_C4_manifest" in report:
        print("C4_MANIFEST_SUMMARY=" + json.dumps(report["current_C4_manifest"], separators=(",", ":")))
    require(report["status"] == "PASS", report.get("error", "Input binding failed"))
    return report


def write_junit(path, name, checks, failures=()):
    failures = set(failures)
    root = ET.Element("testsuites")
    suite = ET.SubElement(root, "testsuite", name=name, tests=str(len(checks)),
                          failures=str(len(failures)), errors="0", skipped="0")
    for check in checks:
        case = ET.SubElement(suite, "testcase", classname=name, name=check)
        if check in failures:
            ET.SubElement(case, "failure", message="See SHA-bound JSON/log evidence")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def installed(work):
    command = [sys.executable, *(["-O"] if sys.flags.optimize else []), str(ROOT / "scripts/qa/atlas_parity02_p06_installed_checks.py"),
               "--repo", str(ROOT), "--work", str(work), "--install-test-tools"]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    source = work / "parity02-p06-installed-checks.json"
    report = {**identity(), "status": "FAIL", "scope": "C4_INSTALLED_C1_SUITE", "skips": 0}
    try:
        receipt = json.loads(source.read_text(encoding="utf-8"))
        original = json.loads(git("show", INPUTS["C1"][0] + ":" + C1 +
                                  "/receipts/r2/installed-linux-O0.json"))
        expected = set(original["test_ids"])
        actual = set(receipt["test_ids"])
        require(completed.returncode == 0 and receipt["status"] == "PASS_SCOPED",
                "Installed composed suite failed")
        require(len(expected) == 122 and expected <= actual and len(actual) >= 122,
                "The composed collection lost inherited C1 test identities")
        require(receipt["tested_sha"] == report["tested_sha"]
                and receipt["optimization"] == sys.flags.optimize
                and receipt["consumer_outside_checkout"]
                and receipt["unique_test_cases"] == receipt["total_executed"] == len(actual),
                "Installed suite has a SHA/mode/collection/isolation mismatch")
        require(all(item["skipped"] == item["failures"] == item["errors"] == 0
                    and not item["loader_errors"] for item in receipt["suites"]),
                "Installed suite skipped or failed a case")
        report.update(status="PASS", inherited_C1_cases=len(expected), unique_test_cases=len(actual),
                      all_C1_test_ids_preserved=True, full_installed_suite=receipt)
        write_junit(work / "c4-installed-junit.xml", "C4-installed", sorted(actual))
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        write_junit(work / "c4-installed-junit.xml", "C4-installed", ["collection-gate"], ["collection-gate"])
    save(work / "c4-installed-receipt.json", report)
    print("C4_INSTALLED_SUMMARY=" + json.dumps({key: report.get(key) for key in
        ("status", "error", "tested_sha", "tested_tree", "optimization", "platform", "skips",
         "inherited_C1_cases", "unique_test_cases", "all_C1_test_ids_preserved")}, separators=(",", ":")))
    require(report["status"] == "PASS", report.get("error", "Installed suite failed"))


def browser(work, output):
    spec = importlib.util.spec_from_file_location("c4_browser_selection",
        ROOT / "scripts/qa/atlas_parity03_p03_ci.py")
    p03 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p03)
    env = dict(os.environ)
    env["ATLAS_BROWSER_BINARY"] = p03.installed_browser()
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    command = [str(python), "-I", "-X", "utf8"] + (["-O"] if sys.flags.optimize else [])
    command += [str(ROOT / "scripts/qa/atlas_parity03_c4_browser.py"),
                "--work", str(work), "--output-dir", str(output)]
    completed = subprocess.run(command, cwd=work / "outside-source", env=env, check=False)
    report = json.loads((output / "BROWSER-RECEIPT.json").read_text(encoding="utf-8"))
    require(completed.returncode == 0 and report["status"] == "PASS"
            and report["tested_sha"] == git("rev-parse", "HEAD")
            and report["optimization"] == sys.flags.optimize
            and all(check["status"] == "PASS" for check in report["checks"])
            and report["external_requests"] == report["page_errors"] == report["console_errors"] == [],
            "Integrated browser evidence failed or mismatched its C4 SHA")
    write_junit(output / "browser-junit.xml", "C4-integrated-browser",
                [check["name"] for check in report["checks"]])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("stage", choices=["inputs", "installed", "browser"])
    cli.add_argument("--repo", type=Path, default=ROOT)
    cli.add_argument("--work", type=Path)
    cli.add_argument("--install-test-tools", action="store_true")
    cli.add_argument("--output-dir", type=Path, default=ROOT / ".test-output/atlas-parity03-c4")
    args = cli.parse_args()
    require(args.repo.resolve() == ROOT, "An alternate checkout cannot supply C4 evidence")
    if args.stage == "inputs":
        inputs(args.output_dir.resolve())
    else:
        require(args.work is not None, "Installed/browser gate requires --work outside checkout")
        work = args.work.resolve()
        require(not work.is_relative_to(ROOT) and work != ROOT, "Consumer must be outside checkout")
        if args.stage == "installed":
            installed(work)
        else:
            browser(work, args.output_dir.resolve())


if __name__ == "__main__":
    main()

