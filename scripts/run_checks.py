"""Run meaningful package, architectural, input-boundary and HTTP checks."""
from pathlib import Path
import json
import subprocess
import sys
import unittest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    guard = subprocess.run([
        sys.executable, str(root / "scripts/qa/architecture_audit.py"), str(root),
        "--protocol", "packages/protocol/src/caderno_protocol",
        "--viewer", "packages/atlas/src/atlas_viewer", "--viewer-module", "atlas_viewer",
    ], check=False)
    if guard.returncode:
        return guard.returncode
    report = {"optimized": bool(sys.flags.optimize), "suites": [], "status": "PASS"}
    for relative in ["packages/protocol/tests", "tests/qa", "tests/viewer"]:
        directory = root / relative
        suite = unittest.TestLoader().discover(str(directory), pattern="test_*.py", top_level_dir=str(directory))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        report["suites"].append({"suite": relative, "tests": result.testsRun,
                                 "failures": len(result.failures), "errors": len(result.errors),
                                 "skipped": len(result.skipped)})
        if not result.wasSuccessful() or result.testsRun == 0:
            report["status"] = "FAIL"
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
