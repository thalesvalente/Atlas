"""Run the graph acceptance suite against the exact installed candidate assets."""
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
        raise RuntimeError("INSTALLED_GRAPH_REQUIRED")
    static = Path(str(files("atlas_viewer").joinpath("static")))
    names = ("native_graph.js", "native_notebook.css")
    for name in names:
        if (static / name).read_bytes() != (root / "packages/atlas/src/atlas_viewer/static" / name).read_bytes():
            raise RuntimeError("INSTALLED_GRAPH_CANDIDATE_MISMATCH")
    result = subprocess.run([
        "node", str(root / "scripts/qa/browser_native_graph.mjs"),
        "--static-root", str(static), "--report-dir", str(work),
    ], cwd=root, check=False)
    report_path = work / "after-graph-report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["scope"] = "INSTALLED_NATIVE_GRAPH_SYNTHETIC_NOT_PRIVATE_HOST_PARITY"
        report["installed_assets_equal_candidate"] = True
        report["installed_asset_sha256"] = {
            name: hashlib.sha256((static / name).read_bytes()).hexdigest() for name in names
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
