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


def audit_baseline(root: Path, *, allow_presentation_delta: bool = False) -> dict:
    errors: list[str] = []
    preserved = 0
    authorized_changes: list[str] = []
    paths = subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", BASELINE], cwd=root,
    ).decode("utf-8").rstrip("\0").split("\0")
    for name in paths:
        if name in EDITABLE_ORIGINALS:
            continue
        expected = subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=root)
        path = root / name
        if not path.is_file() or path.read_bytes() != expected:
            if allow_presentation_delta and name in PRESENTATION_ORIGINALS and path.is_file():
                authorized_changes.append(name)
            else:
                errors.append(f"Preserved baseline changed: {name}")
        else:
            preserved += 1
    return {"errors": errors, "preserved_original_files": preserved,
            "authorized_presentation_changes": authorized_changes}


def audit(root: Path, *, allow_presentation_delta: bool = False) -> dict:
    baseline = audit_baseline(root, allow_presentation_delta=allow_presentation_delta)
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
            "presentation_delta_enabled": allow_presentation_delta, "managed_files": managed,
            "official_skills": len(actual_skills), "python_scripts": len(scripts),
            "errors": errors,
            "scope": "repository integrity and generated assets; no operational or scientific approval"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-presentation-delta", action="store_true",
                        help="Allow only the six existing presentation/test files authorized by feature 003 CLOSE01.")
    args = parser.parse_args()
    try:
        report = audit(Path(__file__).resolve().parents[2],
                       allow_presentation_delta=args.allow_presentation_delta)
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError) as exc:
        report = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)
