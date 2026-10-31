"""Strict isolated F3A gate: frozen-base custody, manifest, real Chromium and unittest XML."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = "54bb16d350f7bc34fafb95438bd64a2397d58bf3"
DOCS = "docs/missions/atlas-parity-04/f3a-graph/"
MANIFEST = DOCS + "MANIFEST.sha256"
PRODUCT = {
    "packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.js",
    "packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.css",
    "tests/qa/test_atlas_parity04_f3a_graph.py",
    "tests/fixtures/atlas_parity04_f3a_graph.json",
    "scripts/qa/atlas_parity04_f3a_browser.mjs",
    "scripts/qa/atlas_parity04_f3a_ci.py",
    ".github/workflows/atlas-parity04-f3a-graph.yml",
}
DOC_NAMES = {
    "PLAN.md", "INPUT-SHAS.json", "GRAPH-CONTRACT.md", "RESULT.md",
    "BROWSER-RECEIPT.json", "NEGATIVE-TESTS.json", "INDEPENDENT-REVIEW.md",
    "HANDOFF.json", "CI-EVIDENCE.json", "GLOBAL-GATE-REPAIR-CONTRACT.md",
    "MANIFEST.sha256",
}
ALLOWED = PRODUCT | {DOCS + name for name in DOC_NAMES}
OUTPUT = Path(os.environ.get("F3A_OUTPUT", str(ROOT / ".test-output" / "atlas-parity04-f3a")))

def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8").strip()

def tree(ref):
    entries = {}
    raw = subprocess.check_output(["git", "ls-tree", "-rz", "--full-tree", ref], cwd=ROOT)
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split()
        entries[path.decode("utf-8")] = (mode, kind, oid)
    return entries

def preflight():
    sha, tree_sha = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
    expected = os.environ.get("F3A_EXPECTED_SHA")
    require(expected is None or sha == expected, "Runner HEAD differs from expected GitHub head SHA")
    subprocess.run(["git", "merge-base", "--is-ancestor", BASE, sha], cwd=ROOT, check=True)
    previous = BASE
    history = []
    for commit in git("rev-list", "--reverse", BASE + ".." + sha).splitlines():
        parents = git("show", "-s", "--format=%P", commit).split()
        require(parents == [previous], "F3A history must be one-parent fast-forward only: " + commit)
        changes = git("diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", commit).splitlines()
        require(changes, "Empty F3A commit is not qualification evidence")
        for line in changes:
            status, path = line.split("\t")
            require(status in {"A", "M"} and path in ALLOWED, "Out-of-ownership intermediate delta: " + line)
        history.append({"sha": commit, "parent": previous, "changes": changes})
        previous = commit
    require(history and previous == sha, "No F3A candidate commits after frozen base")
    base_entries, head_entries = tree(BASE), tree(sha)
    require(all(head_entries.get(path) == item for path, item in base_entries.items()), "Frozen base file/mode/blob changed")
    additions = set(head_entries) - set(base_entries)
    require(additions <= ALLOWED and PRODUCT <= additions and MANIFEST in additions, "Unexpected/missing F3A inventory")
    for path in additions:
        require(head_entries[path][0:2] == ("100644", "blob"), "F3A file is not ordinary 100644 blob: " + path)
        require(not (ROOT / path).is_symlink(), "Symlink refused")
        actual = subprocess.check_output(["git", "hash-object", "--no-filters", str(ROOT / path)], cwd=ROOT).decode("ascii").strip()
        # Windows checkout may use CRLF, so compare normalized tracked UTF-8 content through Git.
        tracked = subprocess.check_output(["git", "show", sha + ":" + path], cwd=ROOT)
        local = (ROOT / path).read_bytes()
        require(local.replace(b"\r\n", b"\n") == tracked.replace(b"\r\n", b"\n"), "Working file differs from tracked source: " + path)
    lines = (ROOT / MANIFEST).read_text(encoding="utf-8").splitlines()
    expected_paths = sorted(additions - {MANIFEST})
    manifest = {}
    for line in lines:
        digest, path = line.split("  ", 1)
        require(len(digest) == 64 and set(digest) <= set("0123456789abcdef") and path not in manifest, "Malformed/duplicate manifest entry")
        manifest[path] = digest
    require(list(manifest) == expected_paths, "Manifest must cover exact sorted additions except itself")
    files = []
    for path, expected_hash in manifest.items():
        tracked = subprocess.check_output(["git", "show", sha + ":" + path], cwd=ROOT)
        digest = hashlib.sha256(tracked).hexdigest()
        require(digest == expected_hash, "Manifest mismatch: " + path)
        files.append({"path": path, "blob": head_entries[path][2], "sha256": digest, "bytes": len(tracked)})
    receipt = {"schema": "atlas-f3a-input-receipt-v1", "sha": sha, "tree": tree_sha, "base_sha": BASE, "history": history, "files": files, "base_files_preserved": len(base_entries), "global_gates_modified": False}
    (OUTPUT / "inputs.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)
    return receipt

class Result(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.started = time.monotonic()
    def stopTest(self, test):
        self.timings[test.id()] = time.monotonic() - self.started
        super().stopTest(test)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.timings = {}; self.ids = []
    def addSuccess(self, test):
        self.ids.append(test.id()); super().addSuccess(test)
    def addError(self, test, err):
        self.ids.append(test.id()); super().addError(test, err)
    def addFailure(self, test, err):
        self.ids.append(test.id()); super().addFailure(test, err)
    def addSkip(self, test, reason):
        self.ids.append(test.id()); super().addSkip(test, reason)

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["F3A_OUTPUT"] = str(OUTPUT)
    inputs = preflight()
    spec = importlib.util.spec_from_file_location("f3a_graph_tests", ROOT / "tests/qa/test_atlas_parity04_f3a_graph.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    expected = suite.countTestCases()
    require(expected == 22, "Unexpected F3A collection; require all 22 named tests")
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    failures = {t.id(): detail for t, detail in result.failures}
    errors = {t.id(): detail for t, detail in result.errors}
    receipt = {"schema": "atlas-f3a-tests-receipt-v1", "sha": inputs["sha"], "tree": inputs["tree"], "python_optimize": sys.flags.optimize, "tests": result.testsRun, "expected": expected, "ids": result.ids, "failures": failures, "errors": errors, "skips": [(t.id(), reason) for t, reason in result.skipped], "passed": result.wasSuccessful() and result.testsRun == expected and not result.skipped}
    (OUTPUT / "tests-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    xml = ET.Element("testsuite", name="F3A isolated real Chromium", tests=str(result.testsRun), failures=str(len(failures)), errors=str(len(errors)), skipped=str(len(result.skipped)))
    props = ET.SubElement(xml, "properties")
    for name, value in (("sha", inputs["sha"]), ("tree", inputs["tree"]), ("python_optimize", str(sys.flags.optimize))):
        ET.SubElement(props, "property", name=name, value=value)
    for ident in result.ids:
        node = ET.SubElement(xml, "testcase", classname=ident.rsplit(".", 1)[0], name=ident.rsplit(".", 1)[1], time=str(result.timings.get(ident, 0)))
        if ident in failures: ET.SubElement(node, "failure").text = failures[ident]
        if ident in errors: ET.SubElement(node, "error").text = errors[ident]
    ET.ElementTree(xml).write(OUTPUT / "junit.xml", encoding="utf-8", xml_declaration=True)
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if receipt["passed"] else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "fatal.json").write_text(json.dumps({"error": str(exc), "python_optimize": sys.flags.optimize}, indent=2) + "\n", encoding="utf-8")
        raise
