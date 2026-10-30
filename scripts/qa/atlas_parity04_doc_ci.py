"""Fail-closed AP04 documentation-successor guard and CI dispatcher.

The historical P06, P03 and C4 controls remain unchanged in meaning. This
module recognizes one exact documentation successor of the frozen C4 object,
verifies its original nine documents by Git object identity, and binds every CI
repair file through a supplemental manifest. It grants no architectural,
scientific, merge, release, deployment or promotion authority.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Callable, Iterable
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
C4_SHA = "72d9b94e613a57c82a5afd309796f44b271e2185"
C4_TREE = "0a622663ca40232d6143659f82cfe9ce43702e90"
DOC_SHA = "c25d37998dac7174067a2819391f3af1625f96dc"
DOC_TREE = "e6eacdd02a329f88bc0dd656523b84a8fec9217e"
P03_INPUT_SHA = "ead1f753f52f22035326b7366dd2231c62775765"
ADR_PATH = "docs/architecture/ADR-0003-legacy-compatibility-proposed.md"
GATES_PATH = "docs/missions/atlas-parity-04/GATES.json"
C4_MANIFEST = "docs/missions/atlas-parity-03/c4-full-convergence/MANIFEST.sha256"
OVERLAY_ROOT = "docs/missions/atlas-parity-04/ci-repair"
OVERLAY_CONTRACT = OVERLAY_ROOT + "/OVERLAY.json"
OVERLAY_MANIFEST = OVERLAY_ROOT + "/MANIFEST.sha256"

DOC_PATHS = frozenset({
    ADR_PATH,
    "docs/missions/atlas-parity-04/ACTION-PLAN.md",
    "docs/missions/atlas-parity-04/DECISION-REGISTER.md",
    "docs/missions/atlas-parity-04/EVIDENCE-REGISTER.md",
    GATES_PATH,
    "docs/missions/atlas-parity-04/INTEROPERABILITY-GUARDRAILS.md",
    "docs/missions/atlas-parity-04/PARITY-MATRIX.csv",
    "docs/missions/atlas-parity-04/README.md",
    "docs/missions/atlas-parity-04/RESULT-REVIEW-TEMPLATE.md",
})

MODIFIED_REPAIR_PATHS = frozenset({
    ".github/workflows/atlas-parity02.yml",
    ".github/workflows/atlas-parity03-p03-gates.yml",
    ".github/workflows/atlas003-speckit.yml",
    ".github/workflows/atlas021.yml",
    "scripts/qa/atlas_parity03_c4_ci.py",
})

NEW_REPAIR_PATHS = frozenset({
    ".github/workflows/atlas-parity04-doc.yml",
    "scripts/qa/atlas_parity04_doc_ci.py",
    "tests/qa/test_atlas_parity04_doc_ci.py",
    OVERLAY_ROOT + "/RESULT.md",
    OVERLAY_ROOT + "/INPUT-SHAS.json",
    OVERLAY_ROOT + "/CI-ROOT-CAUSE.md",
    OVERLAY_ROOT + "/SUCCESSOR-DOC-CONTRACT.md",
    OVERLAY_ROOT + "/NEGATIVE-TESTS.json",
    OVERLAY_ROOT + "/CI-EVIDENCE.json",
    OVERLAY_ROOT + "/DECISION-COMPLIANCE.md",
    OVERLAY_ROOT + "/INDEPENDENT-REVIEW.md",
    OVERLAY_ROOT + "/HANDOFF.json",
    OVERLAY_CONTRACT,
    OVERLAY_MANIFEST,
})

REPAIR_PATHS = MODIFIED_REPAIR_PATHS | NEW_REPAIR_PATHS

C4_FROZEN_LITERAL_NAMES = frozenset({
    "INPUTS", "P03", "C1", "C2", "C3", "C4", "COMPOSITION",
    "COMPOSITION_TREE", "P03_C4_ADAPTERS", "ASSETS",
})

WORKFLOW_PATHS = frozenset({
    ".github/workflows/atlas-parity02.yml",
    ".github/workflows/atlas-parity03-p03-gates.yml",
    ".github/workflows/atlas003-speckit.yml",
    ".github/workflows/atlas021.yml",
    ".github/workflows/atlas-parity04-doc.yml",
})

FORBIDDEN_WORKFLOW_MARKERS = (
    "github.head_ref", "github.ref_name", "continue-on-error", "paths-ignore",
    "if: false", "|| true", "pull_request_target",
)

NEW_AP04_ACTION_PINS = (
    "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
)

# Content authorization is independent of the editable supplemental manifest.
# These are the reviewed control bytes, not hashes read back from that manifest.
# The test module also pins this guard's executable AST (excluding this table),
# so changing a control or this guard and rehashing the manifest is insufficient.
APPROVED_CONTROL_HASHES = (
    (".github/workflows/atlas-parity02.yml", "2f17a0711e43f27a465d4b99ae6b887cbc2dcd0cc2dd875a535961bd0dcb0937"),
    (".github/workflows/atlas-parity03-p03-gates.yml", "491fa56982ce7d427311a7a3e8fe4992c42381766ef3a3e8872d9c2d5adb1bd7"),
    (".github/workflows/atlas-parity04-doc.yml", "82ccfaa17d42b4433ddbb110a90102ac854f32c44eaf76fc68a33df1f955be25"),
    (".github/workflows/atlas003-speckit.yml", "c330d85e29925e7df35c834cb1cd1c4f19d995852b3bcf17d5d5c8fd5dd30fd5"),
    (".github/workflows/atlas021.yml", "db4589fe1570d0d0aa8d9a8bf39be7362df27b44a66172e2ae958e157098381d"),
    ("scripts/qa/atlas_parity03_c4_ci.py", "8edd381487b138fa1ad127ee9e4fb1460f515b6268850ab7e1d80563de2263b8"),
    ("tests/qa/test_atlas_parity04_doc_ci.py", "ef0c73fbb008881a0c9dbca931b4e03a256d381f0d533ba30d064aa51143777c"),
)
CONTROL_PATHS = WORKFLOW_PATHS | {
    "scripts/qa/atlas_parity03_c4_ci.py", "tests/qa/test_atlas_parity04_doc_ci.py",
}


@dataclass(frozen=True)
class SuccessorContract:
    c4_sha: str
    c4_tree: str
    doc_sha: str
    doc_tree: str
    doc_paths: frozenset[str]
    repair_paths: frozenset[str]
    modified_repair_paths: frozenset[str]
    adr_path: str
    gates_path: str
    c4_manifest: str
    overlay_contract: str
    overlay_manifest: str
    plan_id: str = "AP04-POR-v1.0-draft"
    approved_control_hashes: tuple[tuple[str, str], ...] = APPROVED_CONTROL_HASHES


PRODUCTION_CONTRACT = SuccessorContract(
    c4_sha=C4_SHA,
    c4_tree=C4_TREE,
    doc_sha=DOC_SHA,
    doc_tree=DOC_TREE,
    doc_paths=DOC_PATHS,
    repair_paths=REPAIR_PATHS,
    modified_repair_paths=MODIFIED_REPAIR_PATHS,
    adr_path=ADR_PATH,
    gates_path=GATES_PATH,
    c4_manifest=C4_MANIFEST,
    overlay_contract=OVERLAY_CONTRACT,
    overlay_manifest=OVERLAY_MANIFEST,
)


class GuardError(RuntimeError):
    """A closed gate with an exact diagnostic."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise GuardError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str, binary: bool = False, check: bool = True):
    completed = subprocess.run(
        ["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", "replace").strip()
        raise GuardError("git " + " ".join(args) + " failed: " + stderr)
    return completed.stdout if binary else completed.stdout.decode("utf-8").strip()


def is_ancestor(root: Path, ancestor: str, descendant: str = "HEAD") -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def tree_entry(root: Path, ref: str, path: str) -> tuple[str, str, str]:
    raw = git(root, "ls-tree", "-z", ref, "--", path, binary=True)
    entries = [entry for entry in raw.split(b"\0") if entry]
    require(len(entries) == 1, f"Expected exactly one Git tree entry: {ref}:{path}")
    header, raw_path = entries[0].split(b"\t", 1)
    mode, kind, oid = header.decode("ascii").split()
    require(raw_path.decode("utf-8") == path, f"Git path identity mismatch: {path}")
    return mode, kind, oid


def object_bytes(root: Path, ref: str, path: str) -> bytes:
    return git(root, "show", f"{ref}:{path}", binary=True)


def safe_manifest_path(path: str, manifest_path: str) -> bool:
    pure = PurePosixPath(path)
    return (
        path == pure.as_posix()
        and not pure.is_absolute()
        and ".." not in pure.parts
        and "\\" not in path
        and path != manifest_path
    )


def parse_manifest(raw: bytes, manifest_path: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        require(match is not None, f"Malformed supplemental manifest line: {line!r}")
        digest, path = match.groups()
        require(safe_manifest_path(path, manifest_path), f"Unsafe manifest path: {path}")
        require(path not in entries, f"Repeated manifest path: {path}")
        entries[path] = digest
    return entries


def parse_raw_diff(root: Path, base: str, target: str) -> dict[str, dict[str, str]]:
    raw = git(
        root, "diff", "--raw", "--full-index", "--abbrev=40", "-z", "--no-renames",
        base, target, "--", binary=True,
    )
    parts = raw.split(b"\0")
    changes: dict[str, dict[str, str]] = {}
    index = 0
    while index < len(parts) and parts[index]:
        header = parts[index].decode("ascii")
        require(index + 1 < len(parts), "Truncated raw Git diff")
        path = parts[index + 1].decode("utf-8")
        index += 2
        match = re.fullmatch(
            r":([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([A-Z])",
            header,
        )
        require(match is not None, f"Unsupported raw Git diff record: {header}")
        old_mode, new_mode, old_oid, new_oid, status = match.groups()
        require(path not in changes, f"Repeated changed path: {path}")
        changes[path] = {
            "status": status,
            "old_mode": old_mode,
            "new_mode": new_mode,
            "old_oid": old_oid,
            "new_oid": new_oid,
        }
    require(all(not part for part in parts[index:]), "Unexpected trailing raw diff data")
    return changes


def commit_sequence(root: Path, after: str, head: str) -> list[str]:
    value = git(root, "rev-list", "--reverse", f"{after}..{head}")
    return value.splitlines() if value else []


def verify_linear_repair_history(
    root: Path, contract: SuccessorContract, head: str,
) -> list[dict[str, object]]:
    commits = commit_sequence(root, contract.doc_sha, head)
    history: list[dict[str, object]] = []
    for commit in commits:
        parents = git(root, "rev-list", "--parents", "-n", "1", commit).split()
        require(len(parents) == 2, f"Repair history must be fast-forward and non-merge: {commit}")
        parent = parents[1]
        delta = parse_raw_diff(root, parent, commit)
        rejected = sorted(set(delta) - set(contract.repair_paths))
        require(not rejected, f"Repair commit changed unauthorized paths: {rejected}")
        for path, entry in delta.items():
            require(entry["status"] in {"A", "M"}, f"Repair commit uses forbidden status {entry['status']}: {path}")
            require(entry["new_mode"] == "100644", f"Repair path must remain a regular 100644 blob: {path}")
            if entry["status"] == "M":
                require(entry["old_mode"] == "100644", f"Repair changed file mode/type: {path}")
        history.append({"commit": commit, "parent": parent, "paths": sorted(delta)})
    return history


def top_level_literals(raw: bytes, names: Iterable[str], source: str) -> dict[str, object]:
    wanted = set(names)
    values: dict[str, object] = {}
    try:
        tree = ast.parse(raw.decode("utf-8"), filename=source)
    except (SyntaxError, UnicodeDecodeError) as error:
        raise GuardError(f"Cannot parse frozen Python declarations in {source}: {error}") from error
    for node in tree.body:
        name: str | None = None
        value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name, value = node.target.id, node.value
        if name not in wanted:
            continue
        require(name not in values, f"Repeated frozen declaration {name} in {source}")
        try:
            values[name] = ast.literal_eval(value)
        except (ValueError, TypeError) as error:
            raise GuardError(f"Frozen declaration {name} is no longer literal in {source}") from error
    missing = sorted(wanted - set(values))
    require(not missing, f"Missing frozen declarations in {source}: {missing}")
    return values


def verify_approved_control_content(root: Path, contract: SuccessorContract) -> dict[str, str]:
    hashes = dict(contract.approved_control_hashes)
    require(len(hashes) == len(contract.approved_control_hashes)
            and set(hashes) == CONTROL_PATHS,
            "Approved CI control inventory is incomplete, repeated or overbroad")
    for path, expected in sorted(hashes.items()):
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                f"Invalid approved CI control hash: {path}")
        target = root / path
        require(target.is_file() and not target.is_symlink(),
                f"Approved CI control is missing/nonregular: {path}")
        require(sha256(target.read_bytes()) == expected,
                f"Approved CI control bytes changed; manifest rehash grants no authorization: {path}")
    return hashes


def verify_c4_frozen_literals(root: Path, contract: SuccessorContract) -> dict[str, object]:
    path = "scripts/qa/atlas_parity03_c4_ci.py"
    baseline = top_level_literals(
        object_bytes(root, contract.c4_sha, path), C4_FROZEN_LITERAL_NAMES,
        f"{contract.c4_sha}:{path}",
    )
    current = top_level_literals(
        (root / path).read_bytes(), C4_FROZEN_LITERAL_NAMES, f"HEAD:{path}",
    )
    require(current == baseline,
            "Frozen C4 input, adapter or asset declarations changed in the successor")
    return {"path": path, "frozen_literals": sorted(baseline), "unchanged": True}


def workflow_action_pins(raw: bytes, path: str) -> list[str]:
    lines = []
    for line in raw.decode("utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("uses:") or stripped.startswith("- uses:"):
            value = stripped.split("uses:", 1)[1].strip()
            require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}", value) is not None,
                    f"Workflow action is not pinned by full SHA in {path}: {value}")
            lines.append(value)
    return lines


def verify_workflow_safety(root: Path, contract: SuccessorContract) -> dict[str, object]:
    reports: dict[str, object] = {}
    for path in sorted(WORKFLOW_PATHS):
        current = (root / path).read_bytes()
        text = current.decode("utf-8")
        for marker in FORBIDDEN_WORKFLOW_MARKERS:
            require(marker not in text, f"Forbidden workflow routing/bypass marker in {path}: {marker}")
        current_pins = workflow_action_pins(current, path)
        if path in contract.modified_repair_paths:
            baseline_pins = workflow_action_pins(object_bytes(root, contract.c4_sha, path), path)
            require(current_pins == baseline_pins, f"Existing workflow action pins changed: {path}")
        else:
            require(path == ".github/workflows/atlas-parity04-doc.yml",
                    f"Unexpected new workflow in safety check: {path}")
            require(tuple(current_pins) == NEW_AP04_ACTION_PINS,
                    f"New AP04 workflow action pins/order differ: {path}")
        reports[path] = {"action_pins": current_pins, "forbidden_markers": False}
    return reports


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load audit module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def default_boundary_audit(root: Path, contract: SuccessorContract) -> dict:
    module = load_module(root / "scripts/qa/atlas_parity02_p06_audit.py", "ap04_historical_p06")
    raw = module.audit(root)
    expected = [{"path": contract.adr_path, "reason": "UNEXPECTED_PROTECTED_FILE"}]
    require(raw.get("errors") == expected, "Historical P06 differs from the one exact AP04 ADR rejection")
    require(raw.get("status") == "FAIL", "Historical P06 must remain strict and RED for the new ADR")
    return {
        "status": "PASS_EXACT_SUCCESSOR_EXCEPTION",
        "historical_audit_status": raw["status"],
        "historical_errors": raw["errors"],
        "authorized_exception": {
            "path": contract.adr_path,
            "reason": "EXACT_BLOB_PINNED_BY_BASELINE_DOC_SHA",
            "does_not_authorize_prefix": "docs/architecture/",
        },
        "historical_protection_weakened": False,
    }


def verify_original_documents(
    root: Path, contract: SuccessorContract,
) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(contract.doc_paths):
        baseline_mode, baseline_kind, baseline_oid = tree_entry(root, contract.doc_sha, path)
        head_mode, head_kind, head_oid = tree_entry(root, "HEAD", path)
        require(baseline_mode == head_mode == "100644", f"Original AP04 document mode changed: {path}")
        require(baseline_kind == head_kind == "blob", f"Original AP04 document is not a regular blob: {path}")
        baseline_raw = object_bytes(root, contract.doc_sha, path)
        current = root / path
        require(current.is_file() and not current.is_symlink(), f"Original AP04 document missing/nonregular: {path}")
        require(current.read_bytes() == baseline_raw, f"Original AP04 document bytes changed: {path}")
        require(head_oid == baseline_oid, f"Original AP04 document blob changed: {path}")
        documents.append({"path": path, "blob": baseline_oid, "sha256": sha256(baseline_raw)})
    return documents


def verify_overlay(
    root: Path, contract: SuccessorContract,
) -> tuple[dict[str, object], dict[str, str], str]:
    contract_path = root / contract.overlay_contract
    manifest_path = root / contract.overlay_manifest
    require(contract_path.is_file() and not contract_path.is_symlink(), "Missing/nonregular overlay contract")
    require(manifest_path.is_file() and not manifest_path.is_symlink(), "Missing/nonregular overlay manifest")

    overlay = json.loads(contract_path.read_text(encoding="utf-8"))
    require(overlay.get("schema") == "atlas-parity04-doc-ci-overlay-v1", "Overlay schema mismatch")
    require(overlay.get("plan_id") == contract.plan_id, "Overlay plan identity mismatch")
    require(overlay.get("base_sha") == contract.c4_sha, "Overlay C4 baseline mismatch")
    require(overlay.get("baseline_doc_sha") == contract.doc_sha, "Overlay documentation baseline mismatch")
    require(overlay.get("adr0003") == "PROPOSED_NOT_APPROVED", "Overlay promoted ADR-0003")
    require(overlay.get("historical_manifests") == "IMMUTABLE", "Overlay permits historical manifest mutation")
    authorizations = overlay.get("authorized_paths")
    require(isinstance(authorizations, list), "Overlay authorized_paths must be a list")
    purposes: dict[str, str] = {}
    for item in authorizations:
        require(isinstance(item, dict), "Overlay authorization entry must be an object")
        path, purpose = item.get("path"), item.get("purpose")
        require(isinstance(path, str) and isinstance(purpose, str) and purpose.strip(),
                "Overlay authorization requires path and nonempty purpose")
        require(path not in purposes, f"Repeated overlay authorization: {path}")
        purposes[path] = purpose.strip()
    require(set(purposes) == set(contract.repair_paths), "Overlay path set is incomplete or overbroad")

    manifest_raw = manifest_path.read_bytes()
    entries = parse_manifest(manifest_raw, contract.overlay_manifest)
    canonical_manifest = "".join(
        f"{entries[path]}  {path}\n" for path in sorted(entries)
    ).encode("utf-8")
    require(manifest_raw == canonical_manifest,
            "Supplemental manifest must use canonical sorted bytes")
    expected_entries = set(contract.repair_paths) - {contract.overlay_manifest}
    require(set(entries) == expected_entries, "Supplemental manifest entries are incomplete or overbroad")
    for path, expected_hash in sorted(entries.items()):
        target = root / path
        require(target.is_file() and not target.is_symlink(), f"Manifest target missing/nonregular: {path}")
        mode, kind, _ = tree_entry(root, "HEAD", path)
        require(mode == "100644" and kind == "blob", f"Manifest target has forbidden mode/type: {path}")
        require(sha256(target.read_bytes()) == expected_hash, f"Supplemental manifest hash mismatch: {path}")
    return overlay, entries, sha256(manifest_raw)


def verify_final_delta(
    root: Path, contract: SuccessorContract, head: str,
) -> tuple[dict[str, dict[str, str]], list[str]]:
    changes = parse_raw_diff(root, contract.c4_sha, head)
    allowed = set(contract.doc_paths) | set(contract.repair_paths)
    rejected = sorted(set(changes) - allowed)
    missing = sorted(allowed - set(changes))
    require(not rejected, f"Unexpected path in complete C4 successor delta: {rejected}")
    require(not missing, f"Authorized successor path missing from complete delta: {missing}")

    expected_modified = set(contract.modified_repair_paths)
    expected_added = allowed - expected_modified
    for path, entry in changes.items():
        expected_status = "M" if path in expected_modified else "A"
        require(entry["status"] == expected_status,
                f"Unexpected Git status for {path}: {entry['status']} != {expected_status}")
        require(entry["new_mode"] == "100644", f"Successor path must be a regular 100644 blob: {path}")
        if expected_status == "M":
            require(entry["old_mode"] == "100644", f"Modified control changed mode/type: {path}")
        else:
            require(entry["old_mode"] == "000000", f"Added successor path unexpectedly existed in C4: {path}")
    return changes, rejected


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_junit(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = [
        "c4_identity", "documentation_identity", "linear_history", "complete_delta",
        "supplemental_manifest", "historical_boundary", "adr_state",
    ]
    failed = report.get("status") != "PASS"
    suites = ET.Element("testsuites")
    suite = ET.SubElement(
        suites, "testsuite", name="AP04-documentation-successor",
        tests=str(len(checks)), failures="1" if failed else "0", errors="0", skipped="0",
    )
    for index, check in enumerate(checks):
        case = ET.SubElement(suite, "testcase", classname="AP04DocSuccessor", name=check)
        if failed and index == 0:
            ET.SubElement(case, "failure", message=report.get("error", "guard failed"))
    ET.ElementTree(suites).write(path, encoding="utf-8", xml_declaration=True)


def audit(
    root: Path = ROOT,
    *,
    contract: SuccessorContract = PRODUCTION_CONTRACT,
    boundary_audit: Callable[[Path, SuccessorContract], dict] | None = None,
    output: Path | None = None,
    junit: Path | None = None,
) -> dict:
    root = root.resolve()
    report: dict[str, object] = {
        "status": "FAIL",
        "scope": "AP04_DOCUMENTATION_SUCCESSOR_CI_ONLY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "reasoning_effective": "UNVERIFIED",
        "base_sha": contract.c4_sha,
        "base_tree": contract.c4_tree,
        "baseline_doc_sha": contract.doc_sha,
        "baseline_doc_tree": contract.doc_tree,
        "adr0003": "PROPOSED_NOT_APPROVED",
        "architectural_approval": False,
        "scientific_approval": False,
        "merge_release_deploy_promotion": "NOT_AUTHORIZED",
    }
    try:
        require((root / ".git").exists(), "Repository root is not a Git checkout")
        require(not git(root, "status", "--porcelain", "--untracked-files=normal"),
                "Successor evidence requires a clean checkout")
        head = git(root, "rev-parse", "HEAD")
        head_tree = git(root, "rev-parse", "HEAD^{tree}")
        report.update(tested_sha=head, tested_tree=head_tree)

        require(git(root, "rev-parse", contract.c4_sha + "^{tree}") == contract.c4_tree,
                "Frozen C4 tree identity mismatch")
        require(git(root, "rev-parse", contract.doc_sha + "^{tree}") == contract.doc_tree,
                "Published AP04 documentation tree identity mismatch")
        doc_parents = git(root, "rev-list", "--parents", "-n", "1", contract.doc_sha).split()
        require(doc_parents == [contract.doc_sha, contract.c4_sha],
                "Published AP04 documentation commit is not the direct C4 successor")
        require(is_ancestor(root, contract.c4_sha, head), "HEAD does not descend from frozen C4")
        require(is_ancestor(root, contract.doc_sha, head), "HEAD does not descend from published AP04 documents")

        c4_manifest_current = root / contract.c4_manifest
        c4_manifest_raw = object_bytes(root, contract.c4_sha, contract.c4_manifest)
        require(c4_manifest_current.is_file() and not c4_manifest_current.is_symlink(),
                "Historical C4 manifest is missing/nonregular")
        require(c4_manifest_current.read_bytes() == c4_manifest_raw,
                "Historical C4 manifest bytes changed")
        require(tree_entry(root, "HEAD", contract.c4_manifest)[2]
                == tree_entry(root, contract.c4_sha, contract.c4_manifest)[2],
                "Historical C4 manifest blob changed")

        documents = verify_original_documents(root, contract)
        gates = json.loads((root / contract.gates_path).read_text(encoding="utf-8"))
        require(gates.get("plan_id") == contract.plan_id, "AP04 plan identity changed")
        require(gates.get("adr0003") == "PROPOSED_NOT_APPROVED", "ADR-0003 is no longer proposed")
        require(gates.get("scope") == "DOCUMENTATION_ONLY", "Published AP04 scope changed")
        non_authorizations = set(gates.get("non_authorizations", []))
        require({"merge_main", "release", "deploy", "promotion"} <= non_authorizations,
                "Published AP04 non-authorizations were weakened")

        changes, rejected = verify_final_delta(root, contract, head)
        history = verify_linear_repair_history(root, contract, head)
        approved_controls = verify_approved_control_content(root, contract)
        c4_frozen_literals = verify_c4_frozen_literals(root, contract)
        workflow_safety = verify_workflow_safety(root, contract)
        overlay, entries, manifest_hash = verify_overlay(root, contract)
        frozen_boundary = (boundary_audit or default_boundary_audit)(root, contract)

        report.update(
            status="PASS",
            mode="AP04_DOCUMENTATION_SUCCESSOR",
            original_documents=documents,
            original_document_count=len(documents),
            c4_manifest={"path": contract.c4_manifest, "sha256": sha256(c4_manifest_raw),
                         "source_sha": contract.c4_sha, "immutable": True},
            complete_delta={"paths": sorted(changes), "count": len(changes),
                            "rejected_paths": rejected,
                            "statuses": {path: entry["status"] for path, entry in sorted(changes.items())}},
            repair_history=history,
            approved_control_hashes=approved_controls,
            c4_frozen_literals=c4_frozen_literals,
            workflow_safety=workflow_safety,
            overlay={"path": contract.overlay_contract, "authorized_paths": len(overlay["authorized_paths"]),
                     "manifest_path": contract.overlay_manifest, "manifest_sha256": manifest_hash,
                     "manifest_entries": entries},
            frozen_boundary=frozen_boundary,
            limitations=[
                "CI engineering evidence only; no ADR-0003 approval",
                "No private source, host replay, migration, merge, release, deployment or promotion",
                "Terminal GitHub run IDs and independent review remain separate closing gates",
            ],
        )
    except Exception as error:  # fail closed and preserve an attributable receipt
        report["error"] = f"{type(error).__name__}: {error}"

    if output is not None:
        write_json(output, report)
    if junit is not None:
        write_junit(junit, report)
    return report


def classify(root: Path = ROOT) -> str:
    root = root.resolve()
    head = git(root, "rev-parse", "HEAD")
    if head == C4_SHA:
        require(git(root, "rev-parse", "HEAD^{tree}") == C4_TREE, "Exact C4 SHA has unexpected tree")
        return "C4_BASELINE"
    if is_ancestor(root, DOC_SHA, head):
        report = audit(root)
        require(report["status"] == "PASS", str(report.get("error", "AP04 successor guard failed")))
        return "AP04_DOCUMENTATION_SUCCESSOR"
    if is_ancestor(root, P03_INPUT_SHA, head) and not is_ancestor(root, C4_SHA, head):
        return "P03_ISOLATED"
    raise GuardError("Candidate is not an exact C4, AP04 documentation successor or isolated P03 lineage")


def run_python(root: Path, relative_script: str, *args: str) -> int:
    return subprocess.run([sys.executable, str(root / relative_script), *args], cwd=root, check=False).returncode


def dispatch_p03_inputs(root: Path, output_dir: Path) -> int:
    mode = classify(root)
    script = "scripts/qa/atlas_parity03_p03_ci.py" if mode == "P03_ISOLATED" \
        else "scripts/qa/atlas_parity03_c4_ci.py"
    return run_python(root, script, "inputs", "--output-dir", str(output_dir))


def dispatch_p03_browser(root: Path, output_dir: Path) -> int:
    mode = classify(root)
    if mode == "P03_ISOLATED":
        return run_python(root, "scripts/qa/atlas_parity03_p03_ci.py", "browser",
                          "--output-dir", str(output_dir))
    return run_python(root, "scripts/qa/atlas_parity03_c4_ci.py", "p03-browser",
                      "--output-dir", str(output_dir))


def dispatch_installed(root: Path, repo: Path, work: Path, install_test_tools: bool) -> int:
    mode = classify(root)
    common = ["--repo", str(repo), "--work", str(work)]
    if install_test_tools:
        common.append("--install-test-tools")
    if mode == "P03_ISOLATED":
        return run_python(root, "scripts/qa/atlas_parity02_p06_installed_checks.py", *common)
    return run_python(root, "scripts/qa/atlas_parity03_c4_ci.py", "installed", *common)


def dispatch_speckit(root: Path) -> int:
    mode = classify(root)
    option = "--allow-p02-c0-delta" if mode == "P03_ISOLATED" else "--allow-p03-c4-delta"
    return run_python(root, "scripts/qa/speckit_audit.py", "--allow-presentation-delta", option)


def dispatch_boundary(root: Path, output: Path) -> int:
    mode = classify(root)
    if mode == "AP04_DOCUMENTATION_SUCCESSOR":
        report = audit(root, output=output)
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0 if report["status"] == "PASS" else 1
    return run_python(root, "scripts/qa/atlas_parity02_p06_audit.py", "--output", str(output))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)

    audit_parser = commands.add_parser("audit")
    audit_parser.add_argument("--output", type=Path,
                              default=Path(".test-output/atlas-parity04/SUCCESSOR-DOC-RECEIPT.json"))
    audit_parser.add_argument("--junit", type=Path,
                              default=Path(".test-output/atlas-parity04/successor-doc-junit.xml"))

    commands.add_parser("classify")

    boundary = commands.add_parser("boundary")
    boundary.add_argument("--output", type=Path, required=True)

    commands.add_parser("speckit")

    p03_inputs = commands.add_parser("p03-inputs")
    p03_inputs.add_argument("--output-dir", type=Path, required=True)

    p03_browser = commands.add_parser("p03-browser")
    p03_browser.add_argument("--output-dir", type=Path, required=True)

    installed = commands.add_parser("installed")
    installed.add_argument("--repo", type=Path, required=True)
    installed.add_argument("--work", type=Path, required=True)
    installed.add_argument("--install-test-tools", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.repo_root.resolve()
    require(root == ROOT, "Alternate repository roots cannot produce production AP04 evidence")
    if args.command == "audit":
        report = audit(root, output=args.output.resolve(), junit=args.junit.resolve())
        print("AP04_SUCCESSOR_SUMMARY=" + json.dumps({
            key: report.get(key) for key in (
                "status", "error", "tested_sha", "tested_tree", "base_sha",
                "baseline_doc_sha", "original_document_count", "adr0003",
            )
        }, separators=(",", ":")))
        return 0 if report["status"] == "PASS" else 1
    if args.command == "classify":
        mode = classify(root)
        print(mode)
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with Path(output).open("a", encoding="utf-8") as stream:
                stream.write("mode=" + mode + "\n")
        return 0
    if args.command == "boundary":
        return dispatch_boundary(root, args.output.resolve())
    if args.command == "speckit":
        return dispatch_speckit(root)
    if args.command == "p03-inputs":
        return dispatch_p03_inputs(root, args.output_dir.resolve())
    if args.command == "p03-browser":
        return dispatch_p03_browser(root, args.output_dir.resolve())
    if args.command == "installed":
        return dispatch_installed(root, args.repo.resolve(), args.work.resolve(), args.install_test_tools)
    raise GuardError("Unknown command")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GuardError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"AP04_DOC_CI_GUARD_ERROR={type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)
