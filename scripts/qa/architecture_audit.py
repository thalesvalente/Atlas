"""Independent dependency-boundary audit for the Atlas candidate.

This detects static imports (including literal importlib imports), package metadata
couplings and prohibited runtime capabilities. It complements execution in a
fresh virtual environment; it cannot prove behavior of arbitrary dynamic code.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import tomllib
from pathlib import Path


def imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
        elif isinstance(node, ast.Call) and node.args:
            func = node.func
            dynamic = (isinstance(func, ast.Name) and func.id == "__import__") or (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "importlib"
                and func.attr == "import_module"
            )
            if dynamic and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                names.add(node.args[0].value)
    return names


def normalize_package(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(requirement: str) -> str:
    return normalize_package(re.split(r"[\[\s<>=!~;@]", requirement.strip(), maxsplit=1)[0])


def audit_tree(
    root: Path,
    protocol_paths: list[Path],
    viewer_paths: list[Path],
    viewer_modules: set[str],
    forbidden_modules: set[str] = frozenset({"r4"}),
) -> list[dict[str, str]]:
    """Audit only declared production directories, never imported fixtures."""
    findings: list[dict[str, str]] = []
    for role, directories in (("protocol", protocol_paths), ("viewer", viewer_paths)):
        for directory in directories:
            if not directory.is_dir():
                findings.append({"code": "MISSING_PACKAGE", "path": str(directory.relative_to(root)), "detail": role})
                continue
            for source in sorted(directory.rglob("*.py")):
                if source.is_symlink():
                    findings.append({"code": "SOURCE_SYMLINK", "path": str(source.relative_to(root)), "detail": role})
                    continue
                try:
                    imports = imports_in(source)
                except (SyntaxError, UnicodeError) as exc:
                    findings.append({"code": "SOURCE_PARSE", "path": str(source.relative_to(root)), "detail": type(exc).__name__})
                    continue
                for imported in sorted(imports):
                    top = imported.split(".", 1)[0]
                    if top in forbidden_modules or (role == "protocol" and top in viewer_modules):
                        findings.append({"code": "FORBIDDEN_IMPORT", "path": str(source.relative_to(root)), "detail": imported})
                # These runtime process capabilities conflict with the viewer's
                # read-only interpretation role, regardless of producer name.
                if role == "viewer":
                    for imported in sorted(imports & {"subprocess", "pty", "pexpect"}):
                        findings.append({"code": "VIEWER_PROCESS_EXECUTION", "path": str(source.relative_to(root)), "detail": imported})
    for package_dir in {p.parent.parent for p in protocol_paths + viewer_paths}:
        pyproject = package_dir / "pyproject.toml"
        if not pyproject.is_file():
            continue
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        forbidden_dist = {normalize_package(n) for n in forbidden_modules}
        for dep in data.get("project", {}).get("dependencies", []):
            if requirement_name(dep) in forbidden_dist:
                findings.append({"code": "FORBIDDEN_DEPENDENCY", "path": str(pyproject.relative_to(root)), "detail": dep})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--protocol", action="append", required=True)
    parser.add_argument("--viewer", action="append", required=True)
    parser.add_argument("--viewer-module", action="append", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    findings = audit_tree(root, [root / p for p in args.protocol], [root / p for p in args.viewer], set(args.viewer_module))
    print(json.dumps({"status": "ARCHITECTURE_DEVIATION_HOLD" if findings else "PASS_SCOPED", "findings": findings}, indent=2))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
