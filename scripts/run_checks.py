"""Run meaningful package, architectural, input-boundary and HTTP checks."""
from pathlib import Path
import importlib.util
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
    collector_path = root / "scripts/qa/atlas_parity02_p06_installed_checks.py"
    spec = importlib.util.spec_from_file_location("atlas_composed_collection", collector_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Composed test collector is unavailable")
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    report = {"optimized": bool(sys.flags.optimize), "suites": [], "status": "PASS"}
    for relative in ["packages/protocol/tests", "tests/qa", "tests/viewer"]:
        directory = root / relative
        loader = unittest.TestLoader()
        suite, frozen_f2 = collector.discover_suite(root, directory, loader)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        report["suites"].append({"suite": relative, "tests": result.testsRun,
                                 "failures": len(result.failures), "errors": len(result.errors),
                                 "skipped": len(result.skipped)})
        if frozen_f2 is not None:
            report["suites"][-1]["frozen_f2_test_source"] = frozen_f2
        report["suites"][-1]["loader_errors"] = loader.errors
        if not result.wasSuccessful() or result.testsRun == 0 or loader.errors:
            report["status"] = "FAIL"
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
