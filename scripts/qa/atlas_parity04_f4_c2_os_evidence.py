"""Observe actual JUnit outcome and GitHub SHA; cannot qualify missing tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import sys
import xml.etree.ElementTree as ET


def main() -> int:
    directory = Path(".test-output/atlas-parity04-f4-c2-os")
    directory.mkdir(parents=True, exist_ok=True)
    junit = directory / "junit.xml"
    metrics = None
    if junit.exists():
        try:
            root = ET.parse(junit).getroot()
            suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
            metrics = {k: sum(int(s.get(k, 0)) for s in suites)
                       for k in ("tests", "errors", "failures", "skipped")}
        except (ValueError, ET.ParseError):
            pass
    passed = (metrics is not None and metrics["tests"] > 0
              and metrics["errors"] == 0 and metrics["failures"] == 0)
    report = {
        "mission": "AP04-F4-C2-B-OS-SANDBOX-CHAT-01",
        "commit_sha": os.getenv("GITHUB_SHA", "LOCAL_NOT_GITHUB"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "runner_os": os.getenv("RUNNER_OS", platform.system()),
        "python": sys.version.split()[0],
        "optimize": sys.flags.optimize,
        "junit": metrics,
        "test_gate": "OBSERVED_PASS" if passed else "OBSERVED_FAILED_OR_MISSING",
        "production_acquisition": "PRODUCTION_ACQUISITION_BLOCKED",
        "host_qualification": "HOST_UNVERIFIED",
        "filesystem_network_windows":
            "OS_PROFILE_NOT_ENFORCED" if sys.platform == "win32"
            else "REQUIRES_OBSERVED_NEGATIVE_TESTS",
        "approval": "C2_B_OS_BLOCKED_EXACT",
        "independent_review": "NOT_PERFORMED_IN_THIS_SESSION",
        "fixtures": "INVENTED_ONLY",
    }
    (directory / "observed-ci.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"test_gate": report["test_gate"], "junit": metrics,
                      "approval": report["approval"],
                      "sha": report["commit_sha"]}, sort_keys=True))
    return 0 if metrics is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
