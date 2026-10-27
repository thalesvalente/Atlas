"""Drive a synthetic valid-package replacement in engineering CI Chromium.

Only the fixture driver replaces metadata. Viewer requests remain read-only.
No user corpus or host installation is an input to this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
import urllib.request

PREFIX = "urn:caderno:synthetic-environment:"


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    root = Path(__file__).resolve().parents[2]
    case = work / "parity02-p06-swap"
    case.mkdir(exist_ok=False)
    sources = []
    for label in ("A", "B"):
        source = case / label
        shutil.copytree(root / "examples/environmental/sample", source)
        metadata = source / "ro-crate-metadata.json"
        doc = json.loads(metadata.read_text(encoding="utf-8"))
        runs = [e for e in doc["@graph"] if e.get("@type") == "CreateAction"]
        for run in runs:
            run["name"] = run["name"] + " [P06-" + label + "]"
        runs[0]["mentions"] = [{"@id": runs[1]["@id"]}]
        metadata.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
        sources.append(source)
    replacement = json.loads((sources[0] / "ro-crate-metadata.json").read_text(encoding="utf-8"))
    replacement_text = (json.dumps(replacement, ensure_ascii=False)
                        .replace(PREFIX, "urn:atlas:parity02:p06:replacement:")
                        .replace("[P06-A]", "[P06-A-NEW]")) + "\n"
    replacement_file = case / "replacement.json"
    replacement_file.write_text(replacement_text, encoding="utf-8")
    before = [hashes(source) for source in sources]
    expected = [dict(record) for record in before]
    expected[0]["ro-crate-metadata.json"] = hashlib.sha256(replacement_text.encode("utf-8")).hexdigest()
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    validation = case / "validation"
    shutil.copytree(sources[0], validation)
    (validation / "ro-crate-metadata.json").write_text(replacement_text, encoding="utf-8")
    subprocess.run([str(python), "-I", "-m", "caderno_protocol", str(validation)],
                   check=True, cwd=work / "outside-source", capture_output=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = "http://127.0.0.1:" + str(port)
    command = [str(python), "-I", "-m", "atlas_viewer", "serve"]
    for source in sources:
        command.extend(["--source", str(source)])
    command.extend(["--port", str(port)])
    server = subprocess.Popen(command, cwd=work / "outside-source",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    report_path = work / "parity02-p06-browser-report.json"
    try:
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError("Installed engineering viewer failed to start")
            try:
                with urllib.request.urlopen(url + "/api/catalog", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.1)
        else:
            raise TimeoutError("Engineering viewer did not become ready")
        result = subprocess.run([
            "node", str(root / "scripts/qa/atlas_parity02_p06_browser.mjs"),
            "--url", url, "--metadata", str(sources[0] / "ro-crate-metadata.json"),
            "--replacement", str(replacement_file), "--report", str(report_path),
        ], check=False, cwd=root)
        mutation_expected = [hashes(source) for source in sources] == expected
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {
            "status": "FAIL", "error": "Browser produced no receipt"}
        report.update(
            tested_sha=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            source_mutation="SYNTHETIC_FIXTURE_DRIVER_METADATA_ONLY",
            source_bytes_equal_to_driver_expected=mutation_expected,
            installed_wheels=json.loads((work / "clean-install-report.json").read_text(encoding="utf-8"))["wheel_sha256"],
            host_browser="NOT_RUN", full_parity_denominator="UNKNOWN",
        )
        if result.returncode or not mutation_expected:
            report["status"] = "FAIL"
        report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0 if report["status"] == "PASS_SCOPED" else 1
    finally:
        server.terminate()
        try:
            server.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.communicate(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
