"""Start the installed wheel, exercise it in Chromium, then close only our child."""
from __future__ import annotations

import argparse
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
    parser.add_argument("--adversarial", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    python = work / "viewer-env" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    root = Path(__file__).resolve().parents[2]
    source = work / "environmental-crate"
    report = work / "browser-report.json"
    extra = []
    if args.adversarial:
        source = work / "adversarial-crate"
        subprocess.run([str(python), "-I", str(root / "scripts/qa/make_adversarial_fixture.py"),
                        str(source), "--repo", str(root)], check=True, cwd=work)
        report = work / "browser-adversarial-report.json"
        extra = ["--expected-exact-integer", "9007199254740993"]
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen([str(python), "-I", "-m", "atlas_viewer", "serve", "--source",
                                str(source), "--port", str(port)],
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
        return subprocess.run(["node", str(root / "scripts/qa/browser.mjs"), "--url", url,
                               "--expected-sources", str(len(catalog["sources"])),
                               "--expected-runs", str(expected), "--report", str(report), *extra],
                              check=False, cwd=root).returncode
    finally:
        process.terminate()
        try:
            process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
