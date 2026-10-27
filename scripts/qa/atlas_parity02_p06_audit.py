"""Verify byte identity of the frozen protocol, input corpus and governance.

This is a read-only engineering check. It grants no scientific or operational
approval and never accepts an exemption file from a component branch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = "c2d00fb137cac1d62d6b7cb045ddbe055355a4c5"
PROTECTED_PREFIXES = (
    "packages/protocol/", "examples/", ".agents/", ".specify/memory/",
    ".specify/scripts/", ".specify/templates/", ".specify/integrations/",
    ".specify/workflows/", "docs/architecture/", "docs/protocol/",
)
PROTECTED_FILES = (
    "AGENTS.md", ".specify/init-options.json", ".specify/integration.json",
    ".specify/toolchain.json", ".specify/UPSTREAM-LICENSE.txt",
)


def protected(name: str) -> bool:
    return name in PROTECTED_FILES or name.startswith(PROTECTED_PREFIXES)


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def audit(root: Path, baseline: str = BASELINE) -> dict:
    entries = git(root, "ls-tree", "-rz", "--full-tree", baseline).split(b"\0")
    expected = {}
    for entry in entries:
        if not entry:
            continue
        header, raw_name = entry.split(b"\t", 1)
        name = raw_name.decode("utf-8")
        mode, kind, oid = header.split()
        if protected(name) and kind == b"blob":
            expected[name] = (mode, oid.decode("ascii"))
    if not any(name.startswith("packages/protocol/") for name in expected):
        raise ValueError("Frozen baseline has no protocol; refusing an empty audit")
    errors, digests = [], {}
    for name, (mode, oid) in sorted(expected.items()):
        path = root / name
        original = git(root, "cat-file", "blob", oid)
        if path.is_symlink() or not path.is_file():
            errors.append({"path": name, "reason": "MISSING_OR_NONREGULAR"})
        elif mode != b"100644" and mode != b"100755":
            errors.append({"path": name, "reason": "UNSUPPORTED_BASELINE_MODE"})
        elif path.read_bytes() != original:
            errors.append({"path": name, "reason": "BYTES_CHANGED"})
        digests[name] = hashlib.sha256(original).hexdigest()
    # Include tracked additions and nonignored untracked files. Git's existing
    # ignores exclude build metadata and Python caches, while every versioned
    # protected file remains subject to the frozen-byte check.
    listed = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    actual = {name.decode("utf-8") for name in listed.split(b"\0")
              if name and protected(name.decode("utf-8"))}
    for name in sorted(actual - expected.keys()):
        errors.append({"path": name, "reason": "UNEXPECTED_PROTECTED_FILE"})
    return {
        "status": "FAIL" if errors else "PASS_SCOPED",
        "baseline_sha": baseline,
        "tested_sha": git(root, "rev-parse", "HEAD").decode("ascii").strip(),
        "tested_tree": git(root, "rev-parse", "HEAD^{tree}").decode("ascii").strip(),
        "protected_files": len(expected), "baseline_sha256": digests,
        "errors": errors,
        "scope": "protocol/input/governance bytes; no authenticity or human approval",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.repo.resolve())
    encoded = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
