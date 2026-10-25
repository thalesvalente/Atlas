"""Read-only audit of official Spec Kit assets and preserved Atlas baseline."""
from __future__ import annotations

import ast
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


def audit(root: Path) -> dict:
    errors: list[str] = []
    preserved = 0
    paths = subprocess.check_output(
        ["git", "ls-tree", "-rz", "--name-only", BASELINE], cwd=root,
    ).decode("utf-8").rstrip("\0").split("\0")
    for name in paths:
        if name in EDITABLE_ORIGINALS:
            continue
        expected = subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=root)
        path = root / name
        if not path.is_file() or path.read_bytes() != expected:
            errors.append(f"Preserved baseline changed: {name}")
        else:
            preserved += 1

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
            "preserved_original_files": preserved, "managed_files": managed,
            "official_skills": len(actual_skills), "python_scripts": len(scripts),
            "errors": errors,
            "scope": "repository integrity and generated assets; no operational or scientific approval"}


if __name__ == "__main__":
    try:
        report = audit(Path(__file__).resolve().parents[2])
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError) as exc:
        report = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    sys.exit(0 if report["status"] == "PASS" else 1)
