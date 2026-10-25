"""Start the installed wheel, exercise it in Chromium, then close only our child."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True, type=Path)
    scenario = parser.add_mutually_exclusive_group()
    scenario.add_argument("--adversarial", action="store_true")
    scenario.add_argument("--related-references", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    root = Path(__file__).resolve().parents[2]
    source = work / "environmental-crate"
    sources = [source]
    report = work / "browser-report.json"
    extra = []
    if args.adversarial:
        source = work / "adversarial-crate"
        subprocess.run([str(python), "-I", str(root / "scripts/qa/make_adversarial_fixture.py"),
                        str(source), "--repo", str(root)], check=True, cwd=work)
        report = work / "browser-adversarial-report.json"
        extra = ["--expected-exact-integer", "9007199254740993"]
        sources = [source]
    if args.related_references:
        sources = []
        for label in ("A", "B"):
            source = work / ("related-references-" + label.lower())
            subprocess.run([str(python), "-I", str(root / "scripts/qa/make_related_references_fixture.py"),
                            str(source), "--repo", str(root), "--label", label], check=True, cwd=work)
            sources.append(source)
        report = work / "browser-related-references-report.json"
        extra = ["--expect-related-references", "true"]
    def source_hashes():
        return {source.name: {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in source.rglob("*") if p.is_file()} for source in sources}
    before = source_hashes()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    command = [str(python), "-I", "-m", "atlas_viewer", "serve"]
    for source in sources:
        command.extend(["--source", str(source)])
    command.extend(["--port", str(port)])
    process = subprocess.Popen(command,
                               cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("Installed viewer failed to start")
            try:
                with urllib.request.urlopen(url + "/api/catalog", timeout=1) as response:
                    if response.status == 200:
                        catalog = json.load(response)
                        break
            except OSError:
                time.sleep(0.1)
        else:
            raise TimeoutError("Installed viewer did not become ready within ten seconds")
        expected = sum(len(s["read_model"]["runs"]) for s in catalog["sources"] if s["read_model"])
        if args.related_references and (len(catalog["sources"]) != 2 or expected != 8):
            raise RuntimeError("Both complete synthetic source packages must be consumed")
        result = subprocess.run(["node", str(root / "scripts/qa/browser.mjs"), "--url", url,
                                 "--expected-sources", str(len(catalog["sources"])),
                                 "--expected-runs", str(expected), "--report", str(report), *extra],
                                check=False, cwd=root)
        immutable = source_hashes() == before
        if report.exists():
            receipt = json.loads(report.read_text(encoding="utf-8"))
            install = json.loads((work / "clean-install-report.json").read_text(encoding="utf-8"))
            receipt["tested_head"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            receipt["source_tree_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
            receipt["installed_wheel_sha256"] = install["wheel_sha256"]
            receipt["installed_consumer"] = install["viewer"]
            receipt["source_package_bytes_unchanged"] = immutable
            if not immutable:
                receipt["status"] = "FAIL"
                receipt["error"] = "Source package bytes changed during browser verification"
            report.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result.returncode if immutable else 1
    finally:
        process.terminate()
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
