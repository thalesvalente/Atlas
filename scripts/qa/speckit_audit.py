"""Read-only audit of official Spec Kit assets and preserved Atlas baseline."""
from __future__ import annotations

import ast
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASELINE = "a6e57c9c6748b4a0d50b554613c93e2b8a785554"
SKILLS = {"analyze", "checklist", "clarify", "constitution", "converge",
          "implement", "plan", "specify", "tasks", "taskstoissues"}
EDITABLE_ORIGINALS = {".gitignore", ".specify/toolchain.json", "README.md",
                      "THIRD_PARTY_NOTICES.md"}
# CLOSE01 authorizes only presentation and its existing browser/CI harness.
# The default setup audit remains strict; persisted contracts and governance
# are never exempted by this feature-specific opt-in.
PRESENTATION_ORIGINALS = {
    "packages/protocol/src/caderno_protocol/read_model.py",
    "packages/atlas/src/atlas_viewer/static/app.js",
    "packages/atlas/src/atlas_viewer/static/style.css",
    "scripts/qa/browser.mjs",
    "scripts/ci/run_browser.py",
    ".github/workflows/atlas021.yml",
}
# PARITY-03 C1 consumes the frozen P02 object. This opt-in is independent of
# the historical presentation allowance: there is no directory or caller-
# supplied exclusion, and even these three paths must match the approved input.
P02_CODE_SHA = "b443f9eb25f118e6a68c2ad17c8e21ab7aa99990"
P02_PROTOCOL_BASELINE = "c2d00fb137cac1d62d6b7cb045ddbe055355a4c5"
P02_C0_ORIGINALS = {
    "packages/atlas/src/atlas_viewer/catalog.py",
    "packages/atlas/src/atlas_viewer/server.py",
    "packages/atlas/src/atlas_viewer/static/index.html",
}
P02_AUTHORIZATION = (
    "ATLAS-PARITY-03-C1; "
    "docs/missions/atlas-parity-02/p02-c0/P06-INTEGRATION.md section 1"
)
# C4 is an explicit composition authorization, independent of the frozen P02
# opt-in. No path, baseline, manifest or hash can be supplied by the caller.
P03_C4_ORIGINALS = {
    "packages/atlas/src/atlas_viewer/catalog.py": "c2066ead521ad8a1c02f0824e8d14b225ae98f2dcb28b1a4ba5d0ba8f5308b63",
    "packages/atlas/src/atlas_viewer/server.py": "8c3e0ffbe74a9d62bb2ac9bb4b6e97c013e1a4d92500d7b042750981d8a87d90",
    "packages/atlas/src/atlas_viewer/static/index.html": "61bd9a62a5df83f00dc787fbd2bd2cde9c8f798a5101c4d090992f8cefe1e030",
}
P03_C4_AUTHORIZATION = "ATLAS-PARITY-03-C4R; representable P03 presentation in C1"


def audit_protocol_baseline(root: Path) -> dict:
    """Pin all protocol files to the C1 baseline, including additions/deletions."""
    names = subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", P02_PROTOCOL_BASELINE,
         "--", "packages/protocol"], cwd=root,
    ).decode("utf-8").rstrip("\0").split("\0")
    if not names or names == [""]:
        raise ValueError("Frozen C1 baseline has no protocol; refusing an empty audit")
    errors: list[str] = []
    preserved = 0
    for name in names:
        expected = subprocess.check_output(
            ["git", "show", f"{P02_PROTOCOL_BASELINE}:{name}"], cwd=root,
        )
        path = root / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
            errors.append(f"Frozen C1 protocol changed: {name}")
        else:
            preserved += 1
    listed = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
         "--", "packages/protocol"], cwd=root,
    ).decode("utf-8").rstrip("\0").split("\0")
    for name in sorted(set(listed) - set(names) - {""}):
        errors.append(f"Unexpected C1 protocol file: {name}")
    return {"baseline_sha": P02_PROTOCOL_BASELINE,
            "preserved_files": preserved, "errors": errors}


def audit_baseline(root: Path, *, allow_presentation_delta: bool = False,
                   allow_p02_c0_delta: bool = False,
                   allow_p03_c4_delta: bool = False) -> dict:
    errors: list[str] = []
    preserved = 0
    authorized_changes: list[str] = []
    authorized_p02_changes: list[str] = []
    authorized_c4_changes: list[str] = []
    p02_blobs = {}
    if allow_p03_c4_delta:
        for name, expected_hash in P03_C4_ORIGINALS.items():
            path = root / name
            if (path.is_symlink() or not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash):
                errors.append(f"Frozen C4 presentation changed: {name}")
    if allow_p02_c0_delta:
        p02_blobs = {
            name: subprocess.check_output(["git", "show", f"{P02_CODE_SHA}:{name}"], cwd=root)
            for name in sorted(P02_C0_ORIGINALS)
        }
        for name, expected in p02_blobs.items():
            path = root / name
            if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
                errors.append(f"Frozen P02 input changed: {name}")
    paths = subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", BASELINE], cwd=root,
    ).decode("utf-8").rstrip("\0").split("\0")
    for name in paths:
        if name in EDITABLE_ORIGINALS:
            continue
        expected = subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=root)
        path = root / name
        regular = path.is_file() and not path.is_symlink()
        if not regular or path.read_bytes() != expected:
            if (allow_p03_c4_delta and name in P03_C4_ORIGINALS and regular
                    and hashlib.sha256(path.read_bytes()).hexdigest() == P03_C4_ORIGINALS[name]):
                authorized_c4_changes.append(name)
            elif (allow_p02_c0_delta and name in P02_C0_ORIGINALS and regular
                    and path.read_bytes() == p02_blobs[name]):
                authorized_p02_changes.append(name)
            elif allow_presentation_delta and name in PRESENTATION_ORIGINALS and regular:
                authorized_changes.append(name)
            else:
                errors.append(f"Preserved baseline changed: {name}")
        else:
            preserved += 1
    protocol = audit_protocol_baseline(root) if allow_p02_c0_delta or allow_p03_c4_delta else None
    if protocol:
        errors.extend(protocol["errors"])
    return {"errors": errors, "preserved_original_files": preserved,
            "authorized_presentation_changes": authorized_changes,
            "authorized_p02_c0_changes": authorized_p02_changes,
            "authorized_p03_c4_changes": authorized_c4_changes,
            "p03_c4_authorization": {
                "contract": P03_C4_AUTHORIZATION,
                "exact_paths_sha256": dict(P03_C4_ORIGINALS),
            } if allow_p03_c4_delta else None,
            "p02_c0_authorization": {
                "contract": P02_AUTHORIZATION, "frozen_code_sha": P02_CODE_SHA,
                "exact_paths_sha256": {name: hashlib.sha256(blob).hexdigest()
                                       for name, blob in p02_blobs.items()},
            } if allow_p02_c0_delta else None,
            "protocol_invariance": protocol}


def audit(root: Path, *, allow_presentation_delta: bool = False,
          allow_p02_c0_delta: bool = False,
          allow_p03_c4_delta: bool = False) -> dict:
    baseline = audit_baseline(root, allow_presentation_delta=allow_presentation_delta,
                              allow_p02_c0_delta=allow_p02_c0_delta,
                              allow_p03_c4_delta=allow_p03_c4_delta)
    errors = baseline["errors"]

    managed = 0
    for integration, expected_count in (("codex", 10), ("speckit", 18)):
        manifest = json.loads((root / f".specify/integrations/{integration}.manifest.json").read_text(encoding="utf-8"))
        if manifest.get("version") != "1.2.3" or manifest.get("integration") != integration:
            errors.append(f"Unexpected manifest identity: {integration}")
        files = manifest["files"]
        if len(files) != expected_count:
            errors.append(f"Unexpected managed file count: {integration}")
        for name, expected_hash in files.items():
            path = (root / name).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                errors.append(f"Missing or invalid managed path: {name}")
                continue
            # The official manifest hashes normalized text (CRLF -> LF).
            content = path.read_text(encoding="utf-8").encode("utf-8")
            if hashlib.sha256(content).hexdigest() != expected_hash:
                errors.append(f"Managed content changed: {name}")
            managed += 1

    actual_skills = {p.parent.name.removeprefix("speckit-")
                     for p in (root / ".agents/skills").glob("speckit-*/SKILL.md")}
    if actual_skills != SKILLS:
        errors.append("Unexpected official skill set")
    for name in sorted(SKILLS & actual_skills):
        text = (root / f".agents/skills/speckit-{name}/SKILL.md").read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"Missing skill frontmatter: {name}")
            continue
        frontmatter = text.split("---", 2)[1]
        if f'name: "speckit-{name}"' not in frontmatter or 'description: "' not in frontmatter:
            errors.append(f"Invalid skill name/description: {name}")

    scripts = sorted((root / ".specify/scripts/python").glob("*.py"))
    if len(scripts) != 6:
        errors.append("Expected six official Python scripts")
    for path in scripts:
        ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    options = json.loads((root / ".specify/init-options.json").read_text(encoding="utf-8"))
    if any(options.get(k) != v for k, v in {
        "integration": "codex", "script": "py", "ai_skills": True, "speckit_version": "1.2.3",
    }.items()):
        errors.append("Initialization options differ from the approved setup")
    return {"status": "PASS" if not errors else "FAIL", "baseline": BASELINE,
            "preserved_original_files": baseline["preserved_original_files"],
            "authorized_presentation_changes": baseline["authorized_presentation_changes"],
            "authorized_p02_c0_changes": baseline["authorized_p02_c0_changes"],
            "authorized_p03_c4_changes": baseline["authorized_p03_c4_changes"],
            "p03_c4_delta_enabled": allow_p03_c4_delta,
            "p03_c4_authorization": baseline["p03_c4_authorization"],
            "p02_c0_delta_enabled": allow_p02_c0_delta,
            "p02_c0_authorization": baseline["p02_c0_authorization"],
            "protocol_invariance": baseline["protocol_invariance"],
            "presentation_delta_enabled": allow_presentation_delta, "managed_files": managed,
            "official_skills": len(actual_skills), "python_scripts": len(scripts),
            "errors": errors,
            "scope": "repository integrity and generated assets; no operational or scientific approval"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-presentation-delta", action="store_true",
                        help="Allow only the six existing presentation/test files authorized by feature 003 CLOSE01.")
    parser.add_argument("--allow-p02-c0-delta", action="store_true",
                        help="Allow exactly three P02 C0 paths at their frozen input bytes; require C1 protocol invariance.")
    parser.add_argument("--allow-p03-c4-delta", action="store_true",
                        help="Allow only three exact C4 presentation hashes; require frozen protocol bytes.")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        report = audit(Path(__file__).resolve().parents[2],
                       allow_presentation_delta=args.allow_presentation_delta,
                       allow_p02_c0_delta=args.allow_p02_c0_delta,
                       allow_p03_c4_delta=args.allow_p03_c4_delta)
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError) as exc:
        report = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)
