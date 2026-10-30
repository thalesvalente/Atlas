"""Exact-input, zero-skip and portable orchestration gates for isolated P03."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
CODE = "6c412c36e1dbe11711daa15c6d8727fbe94fa0ad"
INPUT = "ead1f753f52f22035326b7366dd2231c62775765"
INPUT_TREE = "624c1ad386666ed2db046a05b0a66530a5ee24c1"
CODE_TREE = "f9cac8cba86763c2ff98f883e33962648fc01004"
P03 = "docs/missions/atlas-parity-02/p03-components/"
MANIFEST_SHA256 = "10e6142468aabdd6e8454665207fd8050ff4f64d6b3dcfd9cde81d699ac71e77"
WORKSTREAM = "specs/004-atlas-parity-c0/workstreams/p03-components/c2-qualification"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def git(*args, binary=False):
    result = subprocess.check_output(["git", *args], cwd=ROOT)
    return result if binary else result.decode("utf-8").strip()


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def identity():
    return {"tested_sha": git("rev-parse", "HEAD"), "tested_tree": git("rev-parse", "HEAD^{tree}"),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
            "python": platform.python_version(), "optimization": sys.flags.optimize,
            "actions_run_id": os.environ.get("GITHUB_RUN_ID"),
            "actions_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "visible_in_main_app": False, "reasoning_effective": "UNVERIFIED"}


def save(output, name, payload):
    output.mkdir(parents=True, exist_ok=True)
    (output / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": name, "status": payload.get("status"),
                      "tested_sha": payload.get("tested_sha")}, ensure_ascii=False))


def allowed(path):
    return (path.startswith("scripts/qa/atlas_parity03_p03_")
            or path.startswith("tests/viewer/test_atlas_parity03_p03_")
            or path.startswith("tests/fixtures/atlas_parity03/p03/")
            or path == ".github/workflows/atlas-parity03-p03-gates.yml"
            or path.startswith("docs/missions/atlas-parity-03/c2-p03-qualification/")
            or path.startswith(WORKSTREAM + "/"))


def inputs(output):
    result = {**identity(), "status": "FAIL", "scope": "P03_FROZEN_INPUT_AND_OWNERSHIP"}
    try:
        require(git("rev-parse", INPUT + "^{tree}") == INPUT_TREE, "Handoff tree mismatch")
        require(git("rev-parse", CODE + "^{tree}") == CODE_TREE, "Code tree mismatch")
        require(git("rev-list", "--parents", "-n", "1", INPUT).split()[1:] == [CODE], "Handoff parent mismatch")
        require(subprocess.run(["git", "merge-base", "--is-ancestor", INPUT, "HEAD"], cwd=ROOT).returncode == 0,
                "Candidate does not descend from fixed handoff")
        require(subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=ROOT).returncode == 0,
                "Tracked worktree differs from HEAD")
        manifest = git("show", INPUT + ":" + P03 + "MANIFEST.sha256", binary=True)
        require(sha256(manifest) == MANIFEST_SHA256, "P03 manifest SHA256 mismatch")
        entries = []
        for line in manifest.decode("utf-8").splitlines():
            digest, path = line.split(maxsplit=1)
            path = path.lstrip(" *")
            raw = git("show", INPUT + ":" + path, binary=True)
            require(sha256(raw) == digest and (ROOT / path).read_bytes() == raw, "P03 manifest entry changed: " + path)
            entries.append({"path": path, "sha256": digest})
        require(len(entries) == 56, "Expected 56 original manifest entries")
        freeze = json.loads(git("show", INPUT + ":" + P03 + "evidence/FREEZE.json"))
        require(len(freeze["files"]) == 25, "Expected 25 frozen files")
        bound = []
        for entry in freeze["files"]:
            path = entry["path"]
            raw = (ROOT / path).read_bytes()
            require(sha256(raw) == entry["sha256"], "Frozen bytes changed: " + path)
            require(raw == git("show", CODE + ":" + path, binary=True)
                    == git("show", INPUT + ":" + path, binary=True)
                    == git("show", "HEAD:" + path, binary=True), "Frozen Git binding differs: " + path)
            bound.append({**entry, "code_blob": git("rev-parse", CODE + ":" + path),
                          "handoff_blob": git("rev-parse", INPUT + ":" + path),
                          "candidate_blob": git("rev-parse", "HEAD:" + path)})
        inherited = git("ls-tree", "-r", "--name-only", INPUT).splitlines()
        require(len(inherited) == 219, "Fixed handoff inventory changed")
        for path in inherited:
            require(git("rev-parse", INPUT + ":" + path) == git("rev-parse", "HEAD:" + path),
                    "Inherited file modified: " + path)
        delta = git("diff", "--name-only", INPUT, "HEAD").splitlines()
        require(all(allowed(path) for path in delta), "Path outside C2 ownership")
        for path in ("packages/atlas/src/atlas_viewer/static/app.js", "packages/atlas/src/atlas_viewer/static/index.html"):
            require("parity02_p03" not in (ROOT / path).read_text(encoding="utf-8"), "P03 activated in main shell")
        require(not (ROOT / ".specify/feature.json").exists(), "Global feature pointer unexpectedly present")
        result.update(status="PASS", code_sha=CODE, code_tree=CODE_TREE, handoff_sha=INPUT,
                      handoff_tree=INPUT_TREE, original_manifest_sha256=MANIFEST_SHA256,
                      original_manifest_entries=entries, frozen_files=bound,
                      unchanged_inherited_files=len(inherited), delta_paths=delta,
                      main_server_assets_qualified=False)
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    save(output, "INPUT-SHAS.json", result)
    require(result["status"] == "PASS", result.get("error", "Input qualification failed"))


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def tests(output):
    result = {**identity(), "status": "FAIL", "scope": "SDK_AND_P03_FOCAL_COLLECTION", "skips": 0}
    try:
        require(not os.environ.get("P03_SKIP_LOOPBACK_REASON"), "An HTTP skip flag is forbidden in qualification")
        require(importlib.metadata.version("jsonschema") == "4.25.1", "jsonschema test pin missing")
        node = subprocess.check_output(["node", "--version"], text=True).strip()
        require(node.startswith("v24."), "Node 24 is required")
        suite = unittest.TestSuite()
        selections = [("packages/protocol/tests", "test_sdk.py"),
                      ("tests/viewer", "test_atlas_parity02_p03_*.py")]
        for relative, pattern in selections:
            directory = str(ROOT / relative)
            suite.addTests(unittest.TestLoader().discover(directory, pattern=pattern, top_level_dir=directory))
        ids = [case.id() for case in flatten(suite)]
        require(len(ids) == 47 and len(ids) == len(set(ids)), "Expected exactly 47 distinct SDK/P03 methods")
        schema_ids = [name for name in ids if name.endswith(".test_profile_schema_matches_positive_fixture")]
        require(len(schema_ids) == 1, "Previously skipped SDK schema test not collected exactly once")
        execution = unittest.TextTestRunner(verbosity=2).run(suite)
        result.update(node=node, jsonschema="4.25.1", collected=len(ids), test_ids=ids,
                      tests_run=execution.testsRun, failures=len(execution.failures), errors=len(execution.errors),
                      skips=len(execution.skipped), skip_details=[(case.id(), reason) for case, reason in execution.skipped],
                      expected_failures=len(execution.expectedFailures), unexpected_successes=len(execution.unexpectedSuccesses),
                      schema_test=schema_ids[0])
        require(execution.wasSuccessful() and execution.testsRun == len(ids) and not execution.skipped
                and not execution.expectedFailures, "Collection must pass with zero skips/expected failures")
        result["status"] = "PASS"
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    save(output, "TEST-RECEIPT.json", result)
    require(result["status"] == "PASS", result.get("error", "Focal tests failed"))


def installed_browser():
    candidates = [os.environ.get("CHROME_BIN"), os.environ.get("CHROME_PATH"),
                  shutil.which("google-chrome"), shutil.which("google-chrome-stable"),
                  shutil.which("chromium"), shutil.which("chromium-browser")]
    if os.name == "nt":
        for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(key)
            if base:
                candidates.append(str(Path(base) / "Google/Chrome/Application/chrome.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("EXISTING_CHROMIUM_NOT_FOUND: no browser download is authorized by this gate")


def run_stage(stage, output):
    env = dict(os.environ)
    if stage == "build":
        work = Path(env.get("RUNNER_TEMP", "/tmp")) / ("atlas-p03-install-" + str(os.getpid()))
        command = [sys.executable, str(ROOT / "scripts/qa/atlas_parity03_p03_build.py"),
                   "--work", str(work), "--output", str(output / "BUILD-AND-INSTALL.json")]
    elif stage == "http":
        command = [sys.executable, str(ROOT / "scripts/qa/atlas_parity03_p03_http.py"),
                   "--output", str(output / "HTTP-RECEIPT.json")]
    else:
        env.update(P03_PYTHON=sys.executable, P03_BROWSER_EXECUTABLE=installed_browser())
        print("Using existing Chromium executable: " + env["P03_BROWSER_EXECUTABLE"])
        command = ["node", str(ROOT / "scripts/qa/atlas_parity03_p03_browser.mjs"), "--output-dir", str(output)]
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def summary(output):
    receipts = {}
    head = git("rev-parse", "HEAD")
    for name in ("INPUT-SHAS.json", "TEST-RECEIPT.json", "BUILD-AND-INSTALL.json", "HTTP-RECEIPT.json", "BROWSER-RECEIPT.json"):
        path = output / name
        if path.exists():
            item = json.loads(path.read_text(encoding="utf-8"))
            receipts[name] = {"status": item["status"], "tested_sha": item.get("tested_sha", item.get("tested_head")),
                              "sha256": sha256(path.read_bytes()), "skips": item.get("skips", item.get("skipped", 0))}
    required = {"INPUT-SHAS.json", "BROWSER-RECEIPT.json"} if os.environ.get("P03_JOB_KIND") == "browser" else {
        "INPUT-SHAS.json", "TEST-RECEIPT.json", "BUILD-AND-INSTALL.json", "HTTP-RECEIPT.json"}
    ok = required <= receipts.keys() and all(v["status"] in {"PASS", "PASS_SCOPED"}
        and v["tested_sha"] == head and v["skips"] == 0 for v in receipts.values())
    record = {**identity(), "status": "PASS" if ok else "FAIL", "receipts": receipts,
              "required": sorted(required), "qualifies_main_shell": False}
    save(output, "JOB-SUMMARY.json", record)
    # Full JSON receipts are retained as artifacts; compact machine-readable summary is also in logs.
    print("P03_JOB_SUMMARY=" + json.dumps(record, separators=(",", ":")))
    require(ok, "Required receipt missing, failed, skipped or attributed to a different SHA")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["inputs", "tests", "build", "http", "browser", "summary"])
    parser.add_argument("--output-dir", type=Path, default=Path(".test-output/atlas-parity03-p03"))
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if args.stage == "inputs": inputs(output)
    elif args.stage == "tests": tests(output)
    elif args.stage == "summary": summary(output)
    else: run_stage(args.stage, output)


if __name__ == "__main__":
    main()
