"""Prove the installed lineage renderer with synthetic browser component data.

No projection/producer/private corpus is opened by this component harness.
The final product routes and host journey are checked separately.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.resources import files
import json
from pathlib import Path
import subprocess

import atlas_viewer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    installed = Path(atlas_viewer.__file__).resolve().parent
    if installed.is_relative_to(root / "packages"):
        raise RuntimeError("INSTALLED_RENDERER_REQUIRED")
    static = Path(str(files("atlas_viewer").joinpath("static")))
    report_path = work / "browser-p01-lineage.json"
    result = subprocess.run([
        "node", str(root / "scripts/qa/browser_p01_lineage.mjs"),
        "--module-dir", str(static), "--report", str(report_path),
    ], cwd=root, check=False)
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["tested_sha"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        report["installed_module_sha256"] = {
            name: hashlib.sha256((static / name).read_bytes()).hexdigest()
            for name in ("native_lineage.js", "native_navigation.js")
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
