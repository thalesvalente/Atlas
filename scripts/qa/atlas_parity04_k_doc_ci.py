"""Object-bound C4/K documentary succession. No architectural acceptance."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE_SHA = "54bb16d350f7bc34fafb95438bd64a2397d58bf3"
BASE_TREE = "1372dd532b2323fc1ebaa5c2f00b6d537c636dc9"
BASE_PARENT = "bd2166651f159e70a8165e0f12c8ad2a3270a0d6"
OBSERVED_K_SHA = "508ccb257a44dc66da13d1edfec7f00ef5231d09"
GUARD_PATH = "scripts/qa/atlas_parity04_k_doc_ci.py"
TEST_PATH = "tests/qa/test_atlas_parity04_k_doc_ci.py"
DOC_ROOT = "docs/missions/atlas-parity-04/c4-k-successor-ci"
BINDING_PATH = DOC_ROOT + "/K-BINDING.json"
RESULT_PATH = DOC_ROOT + "/RESULT.md"
K_ROOT = "docs/missions/atlas-parity-04/f4-c2-key-identity/"
K_PATHS = frozenset(K_ROOT + name for name in (
    "COMPATIBILITY-AND-MIGRATION-LESS.md", "CURRENT-CONTRACT-COUNTEREXAMPLES.md",
    "DECISION-REQUEST.md", "DESCRIPTOR-0.2.1-CANDIDATE.md", "HANDOFF.json",
    "INDEPENDENT-REVIEW.md", "INPUT-SHAS.json", "MANIFEST.sha256",
    "OPTIONS-AND-RISK.md", "RESULT.md", "SYNTHETIC-IDENTITY-FIXTURES.json",
))
MODIFIED_PATHS = frozenset((
    ".github/workflows/atlas-parity02.yml",
    ".github/workflows/atlas-parity03-p03-gates.yml",
    ".github/workflows/atlas-parity04-doc.yml",
    ".github/workflows/atlas-parity03-c4.yml",
    ".github/workflows/atlas003-speckit.yml", ".github/workflows/atlas021.yml",
    "scripts/qa/atlas_parity03_c4_ci.py",
    "scripts/qa/atlas_parity02_p06_installed_checks.py",
    "scripts/run_checks.py",
))
INFRA_PATHS = MODIFIED_PATHS | {GUARD_PATH, TEST_PATH, BINDING_PATH, RESULT_PATH}
FROZEN_INFRA_EPOCHS = {
    "333ba38c6533e1279f8a1cc2cdeb335a23844d68": {
        "tree": "6ed2a7d8531e6280aa6be7b9a2c791e793f475b3",
        "parent": BASE_SHA,
        "state": "FAILED_TECHNICAL_ATTEMPT_SPECKIT_AND_GRAFT_FINDING",
    },
}
# BEGIN_APPROVED_HASHES
APPROVED_HASHES = {'.github/workflows/atlas-parity02.yml': '4af24eca5ac8838b7cde70837e2a280dad8b5e5501185338806cc766533b1b4e', '.github/workflows/atlas-parity03-c4.yml': '56a2ec70a741b26d095846b3766788f0ca4eacdce1288b344cf2fdbb6e1183a5', '.github/workflows/atlas-parity03-p03-gates.yml': 'bf9866bad49b578e5d7b11cabcb4205cd6f753fb8e7cc3926bb4cf4d01ead7f0', '.github/workflows/atlas-parity04-doc.yml': 'e59dc02fe16cd9565ba7d4152c6aba0435f53c091e6de2c69173a35dcd31f260', '.github/workflows/atlas003-speckit.yml': '205281c0ef8c75a188fea2236a4dbe7fc82b588d27606612d504846b297dd068', '.github/workflows/atlas021.yml': '03aac2ea8243e8799edfd9bff66a9bb670e5fd0320b480a342311bb16448a2e8', 'docs/missions/atlas-parity-04/c4-k-successor-ci/K-BINDING.json': '24cdb857746b481257f90972c0602cf5b77377286d8be5607224872d1dda4fb7', 'docs/missions/atlas-parity-04/c4-k-successor-ci/RESULT.md': '35effe6a75ddd846824bf2ff374acd63830cc1e50cb3b57eeea143b28008d948', 'scripts/qa/atlas_parity02_p06_installed_checks.py': 'e59663002278ce231dfbd65b8f5242e49977ce6eab6a877346a2fc79e0d30c5e', 'scripts/qa/atlas_parity03_c4_ci.py': '206052c28d341c399037c6900a912c2310899e1af77134b7ce2d75444137f031', 'scripts/run_checks.py': '7f54ba3033c3ef88fd42781bd7d62aae83ab99d23a825848a35098f16d447a05', 'tests/qa/test_atlas_parity04_k_doc_ci.py': 'e40684899bbe6624c354052ebee63cacd91ac38cb22b6191736260665130643d'}
# END_APPROVED_HASHES
_SNAPSHOTS = {}


class GuardError(RuntimeError):
    """Closed, attributable engineering failure."""


def require(value, message):
    if not value:
        raise GuardError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args, binary=False):
    result = subprocess.run(["git", "--no-replace-objects", *args], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(result.returncode == 0, "Git read failed: " + " ".join(args) + ": "
            + result.stderr.decode("utf-8", "replace"))
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def exact_commit(root, sha):
    require(isinstance(sha, str) and re.fullmatch(r"[a-f0-9]{40}", sha) is not None,
            "An exact immutable commit SHA is required")
    require(git(root, "rev-parse", sha + "^{commit}") == sha, "Commit object differs")
    return sha


def raw_commit(root, sha):
    exact_commit(root, sha)
    raw = git(root, "cat-file", "commit", sha, binary=True)
    require(hashlib.sha1(b"commit " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest() == sha,
            "Raw commit content differs from its immutable object ID")
    headers = raw.split(b"\n\n", 1)[0].split(b"\n")
    trees = [line[5:].decode("ascii") for line in headers if line.startswith(b"tree ")]
    parents = [line[7:].decode("ascii") for line in headers if line.startswith(b"parent ")]
    require(len(trees) == 1 and all(re.fullmatch(r"[a-f0-9]{40}", oid) for oid in trees + parents),
            "Raw commit tree/parent header differs")
    return trees[0], parents


def verify_repository_view(root):
    require(git(root, "rev-parse", "--is-shallow-repository") == "false", "Shallow history is unauthorized")
    require(not any(os.environ.get(name) for name in ("GIT_GRAFT_FILE", "GIT_SHALLOW_FILE", "GIT_REPLACE_REF_BASE")),
            "Alternate genealogy environment is unauthorized")
    graft_path = Path(git(root, "rev-parse", "--git-path", "info/grafts"))
    if not graft_path.is_absolute():
        graft_path = Path(root) / graft_path
    require(not graft_path.exists(), "Graft metadata is unauthorized")
    require(not git(root, "for-each-ref", "--format=%(refname)", "refs/replace/"), "Replacement refs are unauthorized")


def safe_path(path):
    require(isinstance(path, str) and path and "\\" not in path and ":" not in path
            and "\0" not in path and "\n" not in path and "\r" not in path,
            "Unsafe path encoding")
    pure = PurePosixPath(path)
    require(not pure.is_absolute() and ".." not in pure.parts and path == pure.as_posix(),
            "Unsafe or noncanonical path")
    return path


def tree_records(root, ref):
    records = {}
    for entry in git(root, "ls-tree", "-r", "-z", ref, binary=True).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split()
        name = safe_path(path.decode("utf-8"))
        require(name not in records, "Duplicate Git path")
        records[name] = (mode, kind, oid)
    return records


def object_bytes(root, ref, path):
    safe_path(path)
    return git(root, "show", ref + ":" + path, binary=True)


def changes_between(root, old, new):
    before, after = tree_records(root, old), tree_records(root, new)
    return {p: (before.get(p), after.get(p)) for p in before.keys() | after.keys()
            if before.get(p) != after.get(p)}


def verify_records(root, ref, expected_records):
    actual = tree_records(root, ref)
    for path, item in expected_records.items():
        safe_path(path)
        require(set(item) == {"mode", "type", "blob", "sha256"}, "Object binding schema differs")
        require(item["mode"] == "100644" and item["type"] == "blob", "Object binding mode differs")
        require(actual.get(path) == ("100644", "blob", item["blob"]), "Pinned object differs: " + path)
        require(digest(object_bytes(root, ref, path)) == item["sha256"], "Pinned hash differs: " + path)


def verify_leg(root, baseline_sha, head_sha, expected_paths, modified_paths=(), expected_records=None):
    verify_repository_view(root)
    exact_commit(root, baseline_sha)
    exact_commit(root, head_sha)
    expected_paths, modified_paths = set(expected_paths), set(modified_paths)
    for path in expected_paths:
        safe_path(path)
    require(modified_paths <= expected_paths, "Modified ownership exceeds exact path set")
    raw_commit(root, baseline_sha)
    chain, seen, cursor = [], set(), head_sha
    while cursor != baseline_sha:
        require(cursor not in seen and len(chain) < 10000, "Invalid or excessive raw commit ancestry")
        seen.add(cursor)
        tree, parents = raw_commit(root, cursor)
        require(len(parents) == 1, "Nonlinear, merge or unrelated raw ancestry is unauthorized")
        chain.append((cursor, tree, parents[0]))
        cursor = parents[0]
    previous, history = baseline_sha, []
    for commit, tree, parent in reversed(chain):
        require(parent == previous, "Raw parent identity differs")
        changes = changes_between(root, previous, commit)
        require(set(changes) <= expected_paths, "Unauthorized intermediate path: " + str(sorted(set(changes) - expected_paths)))
        for path, (old, new) in changes.items():
            require(new is not None and new[:2] == ("100644", "blob"), "Deletion, symlink or forbidden mode: " + path)
            require(old is None or old[:2] == ("100644", "blob"), "Forbidden prior mode: " + path)
        history.append({"commit": commit, "parent": previous,
                        "tree": tree, "paths": sorted(changes)})
        previous = commit
    require(previous == head_sha, "Incomplete commit ancestry")
    changes = changes_between(root, baseline_sha, head_sha)
    require(set(changes) == expected_paths, "Exact final path inventory differs")
    for path, (old, new) in changes.items():
        require(new is not None and new[:2] == ("100644", "blob"), "Final object mode/type differs")
        require((old is not None) == (path in modified_paths), "Final ADD/MODIFY status differs: " + path)
    if expected_records is not None:
        require(set(expected_records) == expected_paths, "Pinned inventory differs")
        verify_records(root, head_sha, expected_records)
    return history


def verify_manifest(root, head, manifest_path, expected_paths):
    safe_path(manifest_path)
    raw, entries = object_bytes(root, head, manifest_path), {}
    require(tree_records(root, head).get(manifest_path, ())[:2] == ("100644", "blob"), "Manifest mode differs")
    for line in raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        require(match is not None, "Malformed documentary manifest")
        sha, path = match.groups()
        safe_path(path)
        require(path not in entries and path != manifest_path, "Duplicate/self manifest entry")
        entries[path] = sha
    require(raw == "".join(entries[p] + "  " + p + "\n" for p in sorted(entries)).encode("utf-8"), "Noncanonical manifest")
    require(set(entries) == set(expected_paths) - {manifest_path}, "Manifest inventory differs")
    records = tree_records(root, head)
    for path, sha in entries.items():
        require(records.get(path, ())[:2] == ("100644", "blob"), "Manifest target mode differs")
        require(digest(object_bytes(root, head, path)) == sha, "Manifest hash differs: " + path)
    return entries


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def read_binding(root):
    raw = (root / BINDING_PATH).read_bytes()
    binding = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    require(raw == (json.dumps(binding, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"), "Binding must be canonical JSON")
    return binding


def verify_binding(root, binding):
    require(set(binding) == {"schema", "baseline_sha", "baseline_tree", "finalized", "head",
                            "tree", "parent", "files", "commits", "p01_receipt"}, "K binding schema differs")
    require(binding["schema"] == "atlas-c4-k-successor-v1" and binding["baseline_sha"] == BASE_SHA
            and binding["baseline_tree"] == BASE_TREE and type(binding["finalized"]) is bool, "K baseline or terminal authority differs")
    if not binding["finalized"]:
        require(all(binding[key] is None for key in ("head", "tree", "parent", "p01_receipt"))
                and binding["files"] == {} and binding["commits"] == [], "Pending K binding must not imply consumption")
        return {"status": "NOT_RUN", "state": "READY_FOR_K_FINAL_SHA"}
    head = exact_commit(root, binding["head"])
    require(git(root, "rev-parse", head + "^{tree}") == binding["tree"], "K tree differs")
    require(git(root, "rev-list", "--parents", "-n", "1", head).split() == [head, binding["parent"]], "K parent differs")
    history = verify_leg(root, BASE_SHA, head, K_PATHS, expected_records=binding["files"])
    require(OBSERVED_K_SHA in {item["commit"] for item in history}, "K observed ancestry was replaced")
    require([item["commit"] for item in history] == binding["commits"], "K intermediate commit inventory differs")
    require(isinstance(binding["p01_receipt"], str) and binding["p01_receipt"].startswith("https://github.com/thalesvalente/Atlas/"), "Terminal P01 receipt is absent")
    manifest = verify_manifest(root, head, K_ROOT + "MANIFEST.sha256", K_PATHS)
    return {"status": "PASS", "head": head, "tree": binding["tree"], "parent": binding["parent"],
            "history": history, "files": binding["files"], "manifest_entries": manifest,
            "scope": "DOCUMENTARY_SUCCESSION_ONLY", "architectural_approval": False}


def source_without_hashes(raw):
    text = raw.decode("utf-8")
    tree = ast.parse(text)
    tables = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
              and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "APPROVED_HASHES"]
    require(len(tables) == 1, "Expected one isolated control authorization table")
    table = tables[0]
    ast.literal_eval(table.value)
    lines = text.splitlines(keepends=True)
    first, last = table.lineno - 1, table.end_lineno
    require(lines[first - 1].strip() == "# BEGIN_APPROVED_HASHES" and lines[last].strip() == "# END_APPROVED_HASHES", "Control table markers differ")
    for node in tree.body:
        if node is not table:
            require(not (getattr(node, "lineno", 0) <= last and getattr(node, "end_lineno", 0) > first), "Executable control table overlap")
    return "".join(lines[:first] + lines[last:]).encode("utf-8")


def verify_control_preflight(root):
    test_raw = (root / TEST_PATH).read_bytes()
    tree = ast.parse(test_raw.decode("utf-8"))
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"EXPECTED_GUARD_SHA256", "APPROVED_EXTERNAL_HASHES"}:
                require(name not in values, "Duplicate independent control declaration")
                values[name] = ast.literal_eval(node.value)
    require(set(values) == {"EXPECTED_GUARD_SHA256", "APPROVED_EXTERNAL_HASHES"}, "Independent preflight is absent")
    require(digest(source_without_hashes((root / GUARD_PATH).read_bytes())) == values["EXPECTED_GUARD_SHA256"], "Independent guard source differs")
    expected = {**values["APPROVED_EXTERNAL_HASHES"], TEST_PATH: digest(test_raw)}
    require(APPROVED_HASHES == expected and set(expected) == INFRA_PATHS - {GUARD_PATH}, "Independent controls reject rehashed authorization")


def verify_infrastructure(root, head):
    verify_control_preflight(root)
    history = verify_leg(root, BASE_SHA, head, INFRA_PATHS, MODIFIED_PATHS)
    require(set(APPROVED_HASHES) == INFRA_PATHS - {GUARD_PATH}, "Infrastructure control inventory differs")
    semantics = digest(source_without_hashes((root / GUARD_PATH).read_bytes()))
    records = tree_records(root, head)
    for path in INFRA_PATHS:
        target = root / path
        require(target.is_file() and not target.is_symlink() and records[path][:2] == ("100644", "blob"), "Nonregular current infrastructure")
        require(target.read_bytes() == object_bytes(root, head, path), "Checkout bytes differ: " + path)
    for item in history:
        if item["commit"] in FROZEN_INFRA_EPOCHS:
            epoch = FROZEN_INFRA_EPOCHS[item["commit"]]
            require(item["tree"] == epoch["tree"] and item["parent"] == epoch["parent"],
                    "Frozen technical attempt identity differs")
            continue
        for path in item["paths"]:
            raw = object_bytes(root, item["commit"], path)
            if path == GUARD_PATH:
                require(digest(source_without_hashes(raw)) == semantics, "Unauthorized intermediate guard source revision")
            else:
                require(digest(raw) == APPROVED_HASHES[path], "Unauthorized infrastructure object revision: " + path)
    return history


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "Module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_snapshot(root):
    root = Path(root).resolve()
    key = str(root)
    if key not in _SNAPSHOTS:
        require(git(root, "rev-parse", BASE_SHA + "^{tree}") == BASE_TREE, "Frozen F2 baseline tree differs")
        require(git(root, "rev-list", "--parents", "-n", "1", BASE_SHA).split() == [BASE_SHA, BASE_PARENT], "Frozen F2 baseline parent differs")
        temporary = tempfile.TemporaryDirectory(prefix="atlas-frozen-f2-")
        snapshot = Path(temporary.name) / "snapshot"
        subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(root), str(snapshot)], check=True, capture_output=True)
        subprocess.run(["git", "-c", "core.autocrlf=false", "checkout", "--quiet", "--detach", BASE_SHA], cwd=snapshot, check=True, capture_output=True)
        _SNAPSHOTS[key] = (temporary, snapshot)
    snapshot = _SNAPSHOTS[key][1]
    require(git(snapshot, "rev-parse", "HEAD") == BASE_SHA
            and git(snapshot, "rev-parse", "HEAD^{tree}") == BASE_TREE
            and not git(snapshot, "status", "--porcelain", "--untracked-files=normal"),
            "Frozen predecessor checkout identity or bytes changed")
    return snapshot


def load_frozen_f2_tests(root):
    snapshot = frozen_snapshot(root)
    return load_module("test_atlas_parity04_f2_doc_ci", snapshot / "tests/qa/test_atlas_parity04_f2_doc_ci.py")


def historical_audit(root):
    snapshot = frozen_snapshot(root)
    old = load_module("atlas_frozen_f2_k_predecessor", snapshot / "scripts/qa/atlas_parity04_f2_doc_ci.py")
    report = old.audit(snapshot)
    require(report["status"] == "PASS", "Frozen F2 predecessor audit failed: " + report.get("error", "UNKNOWN"))
    return report


def audit(root=ROOT):
    root = Path(root).resolve()
    report = {"status": "FAIL", "scope": "C4_K_DOCUMENTARY_SUCCESSOR", "platform": platform.platform(),
              "optimization": sys.flags.optimize, "adr0003": "PROPOSED_NOT_APPROVED",
              "architectural_approval": False, "scientific_approval": False,
              "merge_deploy_release": "NOT_AUTHORIZED", "PR20_C2_B": "OUT_OF_SCOPE_UNRESOLVED"}
    try:
        require(not git(root, "status", "--porcelain", "--untracked-files=normal"), "Exact-SHA audit requires a clean checkout")
        head = git(root, "rev-parse", "HEAD")
        report.update(tested_sha=head, tested_tree=git(root, "rev-parse", "HEAD^{tree}"),
                      tested_parent=git(root, "rev-parse", "HEAD^"))
        history = verify_infrastructure(root, head)
        historical = historical_audit(root)
        binding = verify_binding(root, read_binding(root))
        report.update(status="PASS", mode="AP04_C4_K_DOCUMENTARY_SUCCESSOR",
                      state="C4_K_SUCCESSOR_QUALIFIED_FOR_COMPOSITION" if binding["status"] == "PASS" else "C4_K_HARNESS_READY_AWAITING_K_SHA",
                      infrastructure_history=history, k_input=binding,
                      frozen_technical_attempts=FROZEN_INFRA_EPOCHS,
                      frozen_f2={"sha": BASE_SHA, "tree": BASE_TREE, "status": historical["status"]},
                      frozen_boundary=historical["frozen_boundary"],
                      protected_paths="EVERY_BASELINE_PATH_EXCEPT_EXACT_INFRA_MODIFICATIONS",
                      limitations=["K source remains on separate immutable leg", "No ARC-09 acceptance", "No C2-B qualification"])
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    return report


def classify_ref(root, ref="HEAD"):
    require(ref == "HEAD", "Classify requires exact checkout audit")
    report = audit(root)
    require(report["status"] == "PASS", report.get("error", "Successor rejected"))
    return report["mode"]


def save(path, report):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def junit(path, report):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    suite = ET.Element("testsuite", name="C4-K", tests="1", failures="0" if report["status"] == "PASS" else "1", errors="0", skipped="0")
    case = ET.SubElement(suite, "testcase", classname="C4K", name="audit")
    if report["status"] != "PASS":
        ET.SubElement(case, "failure", message=report.get("error", "FAILED"))
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def regression(root, output, junit_path):
    current = load_module("test_atlas_parity04_k_doc_ci", root / TEST_PATH)
    historical = load_frozen_f2_tests(root)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([loader.loadTestsFromModule(current), loader.loadTestsFromModule(historical)])
    def case_ids(cases):
        for item in cases:
            if isinstance(item, unittest.TestSuite):
                yield from case_ids(item)
            else:
                yield item.id()
    ids = list(case_ids(suite))
    require(len(ids) == len(set(ids)) and len(ids) > 32, "Regression collection is empty or duplicated")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"status": "PASS" if result.wasSuccessful() and not result.skipped and not loader.errors
              and not result.expectedFailures and not result.unexpectedSuccesses and result.testsRun == len(ids) else "FAIL",
              "tested_sha": git(root, "rev-parse", "HEAD"), "tested_tree": git(root, "rev-parse", "HEAD^{tree}"),
              "frozen_f2_test_source_sha": BASE_SHA, "tests": result.testsRun, "failures": len(result.failures),
              "frozen_f2_test_source_tree": BASE_TREE, "test_ids": ids,
              "current_test_ids": [i for i in ids if i.startswith("test_atlas_parity04_k_doc_ci.")],
              "historical_test_ids": [i for i in ids if i.startswith("test_atlas_parity04_f2_doc_ci.")],
              "optimization": sys.flags.optimize, "platform": platform.platform(),
              "errors": len(result.errors), "skips": len(result.skipped), "loader_errors": loader.errors,
              "expected_failures": len(result.expectedFailures), "unexpected_successes": len(result.unexpectedSuccesses)}
    save(output, report)
    junit(junit_path, report)
    return 0 if report["status"] == "PASS" else 1


def speckit_successor(root, authorization):
    require(authorization["status"] == "PASS", "Spec Kit requires exact infrastructure authorization")
    original = load_module("atlas_unchanged_speckit_k", root / "scripts/qa/speckit_audit.py")
    historical_result = original.audit(root, allow_presentation_delta=True, allow_p03_c4_delta=True)
    expected_error = "Preserved baseline changed: scripts/run_checks.py"
    require(historical_result["status"] == "FAIL" and historical_result["errors"] == [expected_error],
            "Spec Kit detected changes outside the exact C4-K control successor")
    control_path = "scripts/run_checks.py"
    require(digest((root / control_path).read_bytes()) == APPROVED_HASHES[control_path],
            "Exact source collector control authorization differs")
    return {"status": "PASS", "scope": "C4_K_EXACT_SPECKIT_CONTROL_SUCCESSOR",
            "tested_sha": authorization["tested_sha"], "tested_tree": authorization["tested_tree"],
            "historical_default_audit": historical_result,
            "authorized_successor_control": {"path": control_path, "sha256": APPROVED_HASHES[control_path]},
            "default_auditor_unchanged": True, "generic_exclusions": False,
            "architectural_approval": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["audit", "boundary", "classify", "regression", "speckit", "p03-inputs", "p03-browser", "installed", "validate-k"])
    parser.add_argument("--output", type=Path, default=Path(".test-output/atlas-parity04-k/SUCCESSOR.json"))
    parser.add_argument("--junit", type=Path, default=Path(".test-output/atlas-parity04-k/successor.xml"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--k-sha")
    parser.add_argument("--install-test-tools", action="store_true")
    args = parser.parse_args()
    require(args.repo is None or args.repo.resolve() == ROOT, "An alternate checkout cannot supply successor evidence")
    if args.command == "regression":
        return regression(ROOT, args.output, args.junit)
    report = audit(ROOT)
    if args.command == "validate-k":
        require(report["status"] == "PASS", report.get("error", "Infrastructure failed"))
        require(report["k_input"]["status"] == "PASS" and args.k_sha == report["k_input"]["head"], "Exact terminal K SHA not consumed")
    if args.command in {"audit", "boundary", "validate-k"}:
        save(args.output, report)
        junit(args.junit, report)
        print("C4_K_SUCCESSOR_SUMMARY=" + json.dumps({k: report.get(k) for k in ("status", "state", "tested_sha", "tested_tree", "error")}))
        return 0 if report["status"] == "PASS" else 1
    require(report["status"] == "PASS", report.get("error", "Successor rejected"))
    if args.command == "classify":
        print(report["mode"])
        if os.environ.get("GITHUB_OUTPUT"):
            with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
                stream.write("mode=" + report["mode"] + "\n")
        return 0
    if args.command == "speckit":
        result = speckit_successor(ROOT, report)
        save(args.output, result)
        print("C4_K_SPECKIT_SUCCESSOR=" + json.dumps(result, ensure_ascii=False))
        return 0
    else:
        command = ["scripts/qa/atlas_parity03_c4_ci.py", {"p03-inputs": "inputs", "p03-browser": "p03-browser", "installed": "installed"}[args.command]]
        if args.command == "installed":
            require(args.work is not None, "Installed work path is required")
            command += ["--work", str(args.work.resolve())]
        else:
            require(args.output_dir is not None, "Output directory is required")
            command += ["--output-dir", str(args.output_dir.resolve())]
    return subprocess.run([sys.executable, *command], cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GuardError, OSError, ValueError, KeyError) as error:
        print("C4_K_SUCCESSOR_ERROR=" + type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise SystemExit(1)
