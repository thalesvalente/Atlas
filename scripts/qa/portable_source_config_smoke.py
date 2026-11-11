"""Exercise installed Atlas configuration with disposable public synthetic data.

No operator configuration, producer, service, or scientific source is read.
The same command can run in an isolated Linux or Windows test installation.
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
import sys
import tempfile


def hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def run_smoke(repo: Path) -> dict:
    checks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="atlas-config-smoke-") as scratch:
        work = Path(scratch)
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env.update(XDG_CONFIG_HOME=str(work / "user-config"),
                   LOCALAPPDATA=str(work / "user-config"), PYTHONUTF8="1",
                   PYTHONDONTWRITEBYTECODE="1")
        prefix = [sys.executable, "-I", "-B", "-X", "utf8"]
        if sys.flags.optimize:
            prefix.append("-O")

        def call(stage: str, args: list[str], expected: int = 0,
                 *, module: bool = True) -> subprocess.CompletedProcess:
            command = prefix + (["-m", "atlas_viewer"] if module else []) + args
            result = subprocess.run(command, cwd=work, env=env, text=True,
                                    encoding="utf-8", capture_output=True, timeout=60)
            if result.returncode != expected:
                raise RuntimeError(f"{stage}: unexpected exit {result.returncode}")
            # Receipts and routine diagnostics must not expose local paths.
            if str(work) in result.stdout or str(work) in result.stderr:
                raise RuntimeError(f"{stage}: local path disclosed")
            checks.append(stage)
            return result

        def dossier(stage: str, args: list[str], count: int) -> None:
            data = json.loads(call(stage, ["dossier", *args]).stdout)
            sources = data["sources"]
            if len(sources) != count or any(s["status"] != "READY" for s in sources):
                raise RuntimeError(f"{stage}: incorrect source selection")
            if any(s["scientific_approval"] != "NOT_EVALUATED" for s in sources):
                raise RuntimeError(f"{stage}: scientific authority changed")

        call("installed_without_r4", ["-c",
             "import importlib.util, pathlib, sys, atlas_viewer, caderno_protocol; "
             "sys.exit(0 if importlib.util.find_spec('r4') is None "
             "and pathlib.Path(atlas_viewer.__file__).is_relative_to(sys.prefix) "
             "and pathlib.Path(caderno_protocol.__file__).is_relative_to(sys.prefix) else 3)"],
             module=False)
        dossier("first_use_empty", [], 0)
        call("show_missing_default", ["config", "show"])
        source = work / "pacote com espaços e ação"
        shutil.copytree(repo / "examples/environmental/sample", source)
        original = hashes(source)
        call("configure_one", ["config", "set", "--source", str(source)])
        dossier("persisted_source_reused", [], 1)
        call("show_redacted", ["config", "show"])

        moved = work / "novo disco sintético" / "pacote com ação"
        moved.parent.mkdir()
        source.rename(moved)
        call("missing_saved_source", ["dossier"], expected=2)
        call("replace_moved_path", ["config", "set", "--source", str(moved)])
        dossier("moved_path_reused", [], 1)

        malformed = work / "malformed.json"
        malformed.write_text('{"version":', encoding="utf-8")
        call("malformed_config_rejected", ["dossier", "--config", str(malformed)], expected=2)
        dossier("explicit_source_overrides_malformed_config",
                ["--config", str(malformed), "--source", str(moved)], 1)
        call("duplicate_source_rejected", ["config", "set", "--source", str(moved),
                                           "--source", str(moved)], expected=2)
        call("too_many_sources_rejected", ["config", "set"] +
             [part for _ in range(17) for part in ("--source", str(moved))], expected=2)
        dossier("failed_updates_preserve_configuration", [], 1)

        relative = work / "relative-config" / "sources.json"
        relative.parent.mkdir()
        relative.write_text(json.dumps({"version": 1,
            "sources": ["../novo disco sintético/pacote com ação"]}), encoding="utf-8")
        dossier("relative_to_config_directory", ["--config", str(relative)], 1)
        second = work / "segundo pacote"
        shutil.copytree(moved, second)
        call("configure_multiple", ["config", "set", "--source", str(moved),
                                     "--source", str(second)])
        dossier("multiple_sources_reused", [], 2)
        call("reject_config_inside_source", ["config", "set", "--config",
             str(moved / "preferences.json"), "--source", str(moved)], expected=2)
        if (moved / "preferences.json").exists():
            raise RuntimeError("reject_config_inside_source: scientific package changed")

        empty = work / "empty-config.json"
        empty.write_text('{"version":1,"sources":[]}', encoding="utf-8")
        for stage, config in (("launcher_reuses_relative_config", relative),
                              ("launcher_empty_does_not_reload_default", empty)):
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            if port in {18768, 18770, 18772}:
                raise RuntimeError("Excluded operational port allocated; retry smoke")
            result = call(stage, [str(repo / "scripts/atlas_launch.py"),
                "--config", str(config), "--port", str(port), "--view", "Protocol",
                "--no-open", "--probe-only"], module=False)
            if "ATLAS_NOVO_READY" not in result.stdout:
                raise RuntimeError(f"{stage}: no readiness receipt")
            if config == empty and "ATLAS_EMPTY_CATALOG" not in result.stdout:
                raise RuntimeError(f"{stage}: selection was not empty")

        call("clear_saved_sources", ["config", "clear"])
        dossier("cleared_selection_empty", [], 0)
        if hashes(moved) != original or hashes(second) != original:
            raise RuntimeError("source_immutability: synthetic source bytes changed")
        checks.append("source_bytes_unchanged")
    return {"status": "PASS_SCOPED", "scope": "installed-portable-source-configuration",
            "python": sys.version.split()[0], "platform": sys.platform,
            "checks": checks, "check_count": len(checks),
            "data": "PUBLIC_SYNTHETIC_FIXTURE_ONLY",
            "windows_runtime": "CURRENT_HOST" if os.name == "nt" else "LOCAL_TEST_NOT_RUN",
            "powershell": "NOT_RUN_BY_THIS_SCRIPT", "scientific_acceptance": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        report = run_smoke(args.repo.resolve())
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
        # Exception details can contain subprocess paths; keep the public receipt safe.
        report = {"status": "FAIL", "error_type": type(exc).__name__,
                  "stage": str(exc).split(":", 1)[0] if isinstance(exc, RuntimeError)
                  else "SMOKE_EXCEPTION", "operator_windows": "LOCAL_TEST_NOT_RUN"}
    rendered = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    if args.receipt:
        args.receipt.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
