"""Run and collect the composed suite from installed wheels outside the checkout.

This P06 composition gate preserves the legacy suite scope while rejecting skips
and recording unique test identities. It does not operate a user's host.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SUITES = ("packages/protocol/tests", "tests/qa", "tests/viewer")


def case_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from case_ids(item)
        else:
            yield item.id()


def probe(repo: Path, work: Path) -> dict:
    import atlas_viewer
    import caderno_protocol

    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=repo, text=True,
    ).strip()
    if dirty:
        raise RuntimeError("Exact-SHA installed evidence requires a clean checkout")

    imports = {
        "viewer": str(Path(atlas_viewer.__file__).resolve()),
        "sdk": str(Path(caderno_protocol.__file__).resolve()),
    }
    if repo == work or work.is_relative_to(repo):
        raise RuntimeError("Consumer workspace must be outside the checkout")
    if Path.cwd().resolve().is_relative_to(repo):
        raise RuntimeError("Installed suite must run outside the checkout")
    if any(Path(location).is_relative_to(repo) or
           not Path(location).is_relative_to(Path(sys.prefix).resolve())
           for location in imports.values()):
        raise RuntimeError("SDK and viewer must resolve to the isolated installation")
    if importlib.util.find_spec("r4") is not None:
        raise RuntimeError("R4 must not be installed")
    try:
        schema_tool = importlib.metadata.version("jsonschema")
    except importlib.metadata.PackageNotFoundError:
        schema_tool = None
    architecture = subprocess.run([
        sys.executable, "-I", * (["-O"] if sys.flags.optimize else []),
        str(repo / "scripts/qa/architecture_audit.py"), str(repo),
        "--protocol", "packages/protocol/src/caderno_protocol",
        "--viewer", "packages/atlas/src/atlas_viewer", "--viewer-module", "atlas_viewer",
    ], check=False, capture_output=True, text=True, encoding="utf-8")
    report = {
        "status": "PASS_SCOPED", "scope": "installed integrated suite outside checkout; zero skips",
        "tested_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=repo, text=True).strip(),
        "python": sys.version.split()[0], "optimization": sys.flags.optimize, "platform": sys.platform,
        "consumer_outside_checkout": True, "r4_absent": True, "installed_modules": imports,
        "test_only_dependencies": {"jsonschema": schema_tool},
        "architecture_exit_code": architecture.returncode, "suites": [],
        "test_ids": [], "unique_test_cases": 0,
        "counting": "Each collected case counted once; OS/mode runs are executions, not new identities.",
    }
    log = io.StringIO()
    log.write(architecture.stdout + architecture.stderr)
    if architecture.returncode:
        report["status"] = "FAIL"
    for relative in SUITES:
        directory = repo / relative
        loader = unittest.TestLoader()
        suite = loader.discover(str(directory), pattern="test_*.py", top_level_dir=str(directory))
        ids = list(case_ids(suite))
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        record = {"suite": relative, "collected": len(ids), "tests": result.testsRun,
                  "failures": len(result.failures), "errors": len(result.errors),
                  "skipped": len(result.skipped), "loader_errors": loader.errors, "test_ids": ids}
        report["suites"].append(record)
        report["test_ids"].extend(ids)
        if (not result.wasSuccessful() or result.skipped or loader.errors
                or result.testsRun == 0 or result.testsRun != len(ids)):
            report["status"] = "FAIL"
    report["unique_test_cases"] = len(set(report["test_ids"]))
    report["total_executed"] = sum(suite["tests"] for suite in report["suites"])
    if report["unique_test_cases"] != report["total_executed"]:
        report["status"] = "FAIL"
        report["error"] = "Duplicate case IDs or collection/execution mismatch"
    (work / "parity02-p06-installed-checks.log").write_text(log.getvalue(), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--install-test-tools", action="store_true",
                        help="Install pinned jsonschema in the test consumer after clean-install isolation proof")
    args = parser.parse_args()
    repo, work = args.repo.resolve(), args.work.resolve()
    if args.probe:
        report = probe(repo, work)
        (work / "parity02-p06-installed-checks.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items() if key != "test_ids"}, indent=2))
        return 0 if report["status"] == "PASS_SCOPED" else 1
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if args.install_test_tools:
        subprocess.run([str(python), "-I", "-m", "pip", "install", "jsonschema==4.25.1"],
                       cwd=work / "outside-source", check=True)
    command = [str(python), "-I", "-X", "utf8"]
    if sys.flags.optimize:
        command.append("-O")
    command.extend([str(Path(__file__).resolve()), "--repo", str(repo), "--work", str(work), "--probe"])
    completed = subprocess.run(command, cwd=work / "outside-source", check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
