"""Run the P02 synthetic browser proof from an installed consumer, without polling.

Example: INSTALLED_PYTHON -I atlas_parity02_p02_run_browser.py --report REPORT.json
The two fixture packages are read directly, hashed before/after, never rewritten.
The server is this process's loopback-only child thread; no host service is used.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import subprocess
import tempfile
import threading

import atlas_viewer
import caderno_protocol
from atlas_viewer.catalog import Catalog
from atlas_viewer.server import make_server


def hashes(sources):
    return {source.name: {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(source.rglob("*")) if path.is_file()}
            for source in sources}


def font_provenance(required: bool) -> dict:
    matcher = shutil.which("fc-match")
    if matcher is None:
        if required:
            raise RuntimeError("CJK/emoji proof requires fontconfig and installed fonts")
        return {"status": "NOT_AVAILABLE", "scope": "font provisioning observation only"}
    records = []
    for label, codepoint in (("CJK U+65E5", 0x65E5), ("emoji U+1F9EA", 0x1F9EA)):
        result = subprocess.run([matcher, "-f", "%{file}\n%{family}\n%{style}\n",
                                 ":charset=" + format(codepoint, "x")],
                                check=True, capture_output=True, text=True, encoding="utf-8")
        selected = result.stdout.splitlines()
        if len(selected) < 2 or not Path(selected[0]).is_file():
            raise RuntimeError("Font selection failed for " + label)
        selected_file = Path(selected[0])
        query = subprocess.run(["fc-query", "--format", "%{charset}\n", str(selected_file)],
                               check=True, capture_output=True, text=True, encoding="utf-8")
        intervals = [part.split("-") for part in query.stdout.split()]
        covered = any(int(bounds[0], 16) <= codepoint <= int(bounds[-1], 16)
                      for bounds in intervals)
        if required and not covered:
            raise RuntimeError("Selected font lacks required glyph " + label)
        records.append({"requested_glyph": label, "family": selected[1],
                        "style": selected[2] if len(selected) > 2 else "",
                        "filename": selected_file.name,
                        "sha256": hashlib.sha256(selected_file.read_bytes()).hexdigest(),
                        "charset_contains_requested_glyph": covered})
    return {"status": "PASS_SCOPED" if all(record["charset_contains_requested_glyph"] for record in records)
            else "INCOMPLETE", "fonts": records,
            "scope": "fontconfig-selected installed fonts and declared glyph coverage; not accessibility certification"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--code-sha", required=True)
    parser.add_argument("--require-fonts", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    report_path = args.report.resolve()
    tested_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    if args.code_sha != tested_sha:
        raise RuntimeError("Browser --code-sha must equal the actual checkout HEAD")
    fonts = font_provenance(args.require_fonts)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    (report_path.parent / "font-provenance.json").write_text(
        json.dumps(fonts, indent=2) + "\n", encoding="utf-8")
    viewer_location = Path(atlas_viewer.__file__).resolve()
    protocol_location = Path(caderno_protocol.__file__).resolve()
    if viewer_location.is_relative_to(repo) or protocol_location.is_relative_to(repo):
        raise RuntimeError("This proof requires SDK/viewer installed outside the source checkout")
    if importlib.util.find_spec("r4") is not None:
        raise RuntimeError("This proof requires an environment without R4")
    fixtures = repo / "tests/fixtures/atlas_parity02/p02"
    sources = [fixtures / "source-a", fixtures / "source-b"]
    before = hashes(sources)
    catalog = Catalog(sources)
    snapshot = catalog.snapshot()
    if not all(source["report"]["valid"] for source in snapshot["sources"]):
        raise RuntimeError("Both public synthetic sources must validate")
    server = make_server(catalog, 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    command = ["node", str(repo / "scripts/qa/atlas_parity02_p02_browser.mjs"),
               "--url", f"http://127.0.0.1:{server.server_address[1]}",
               "--report", str(report_path), "--code-sha", args.code_sha]
    if args.screenshots:
        command.extend(["--screenshots", str(args.screenshots.resolve())])
    try:
        with tempfile.TemporaryDirectory(prefix="atlas-p02-consumer-") as directory:
            result = subprocess.run(command, cwd=directory, check=False, timeout=240)
        immutable = hashes(sources) == before
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["source_tree_dirty"] = bool(subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, text=True).strip())
            report["font_provenance"] = fonts
            screenshot_dir = args.screenshots.resolve() if args.screenshots else report_path.parent / "p02-screenshots"
            report["screenshot_sha256"] = {
                name: hashlib.sha256((screenshot_dir / name).read_bytes()).hexdigest()
                for name in report.get("screenshots", []) if (screenshot_dir / name).is_file()}
            if report.get("status") == "PASS_SCOPED" and len(report["screenshot_sha256"]) != 6:
                report["status"] = "FAIL"
                report["error"] = "The C0 proof must preserve exactly six PNG captures"
            report["consumer"] = {"viewer_import_outside_checkout": True,
                                  "sdk_import_outside_checkout": True,
                                  "r4_installed": False,
                                  "python_optimized": bool(__import__("sys").flags.optimize)}
            report["source_package_sha256"] = before
            report["source_package_bytes_unchanged"] = immutable
            if not immutable:
                report["status"] = "FAIL"
                report["error"] = "Source package bytes changed during browser verification"
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not report_path.exists():
            return 1
        return 0 if result.returncode == 0 and immutable and report["status"] == "PASS_SCOPED" else 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
