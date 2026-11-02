#!/usr/bin/env python3
"""Launch the NEW installed Atlas; optionally prepare one legacy Caderno locally.

The external R4 adapter is invoked as a *separate* process. The installed Atlas
runtime does not import R4 or read legacy ledgers. Nothing writes to the Caderno.
Session outputs are temporary derived caches, not migrations or source authority.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser


def _validated_source(value: str) -> str:
    path = Path(value).expanduser().absolute()
    if not path.exists():
        raise ValueError("ATLAS_SOURCE_NOT_FOUND")
    return str(path)



def _safe_adapter_reason(stderr: str) -> str:
    """Return only structural codes, never source paths or free-form private data."""
    for line in reversed(stderr.splitlines()[-20:]):
        try:
            result = json.loads(line)
        except ValueError:
            continue
        if not isinstance(result, dict) or result.get("status") != "BLOCKED":
            continue
        message = result.get("error")
        if not isinstance(message, str):
            return "DETAILS_LOCAL_ONLY"
        if re.fullmatch(r"[A-Z][A-Z0-9_:-]{2,159}", message):
            return message
        prefix = "No module named '"
        if message.startswith(prefix) and message.endswith("'"):
            module = message[len(prefix):-1]
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_.]{0,79}", module):
                return "PYTHON_MODULE_MISSING:" + module
        return "DETAILS_LOCAL_ONLY"
    return "DETAILS_LOCAL_ONLY"


def _prepare_legacy(code_value: str, notebook_value: str, session: Path) -> str:
    code = Path(code_value).expanduser().absolute()
    notebook = Path(notebook_value).expanduser().absolute()
    if not (code / "src/r4/campaigns/atlas.py").is_file():
        raise ValueError("ATLAS_LEGACY_PRODUCER_NOT_FOUND")
    if not notebook.is_dir():
        raise ValueError("ATLAS_LEGACY_NOTEBOOK_NOT_FOUND")
    # The existing R4 project() API calls validate_root(root), which requires
    # R4-WORKSPACE.json. Merely pointing at a folder of notebook files does
    # not satisfy that producer contract.
    if not (notebook / "R4-WORKSPACE.json").is_file():
        raise ValueError("ATLAS_LEGACY_R4_WORKSPACE_MARKER_MISSING")
    exporter = Path(__file__).resolve().parents[1] / "tools/export_native_notebook.py"
    if not exporter.is_file():
        raise ValueError("ATLAS_EXTERNAL_ADAPTER_NOT_FOUND")
    package = session / "derived-package"
    command = [
        sys.executable, "-I", "-B", str(exporter),
        "--r4-code", str(code), "--notebook-root", str(notebook),
        "--output", str(package),
    ]
    completed = subprocess.run(command, text=True, encoding="utf-8",
                               errors="replace", capture_output=True, check=False)
    if completed.returncode:
        # Never emit notebook values or a private source path in an HTTP log.
        safe_reason = _safe_adapter_reason(completed.stderr)
        raise RuntimeError("ATLAS_LEGACY_EXPORT_BLOCKED:" + safe_reason +
                           " (exit " + str(completed.returncode) + "); " +
                           "execute the external adapter locally if details " +
                           "are needed.")
    try:
        receipt = json.loads(completed.stdout)
    except ValueError as exc:
        raise RuntimeError("ATLAS_LEGACY_ADAPTER_RECEIPT_INVALID") from exc
    if receipt.get("status") != "EXPORTED" or not (package / "ro-crate-metadata.json").is_file():
        raise RuntimeError("ATLAS_LEGACY_PACKAGE_NOT_PUBLISHED")
    print("ATLAS_LEGACY_ADAPTER_READY: consulta derivada local; " +
          "Caderno original permanece intacto.", flush=True)
    return str(package)


def _start_viewer(sources: list[str], port: int, view: str, no_open: bool,
                  probe_only: bool) -> int:
    # Reject an occupied port before launching; the product itself binds only
    # loopback, so it cannot expose this notebook outside the local computer.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", port))
    cmd = [sys.executable, "-I", "-m", "atlas_viewer", "serve", "--port", str(port)]
    for source in sources:
        cmd.extend(("--source", source))
    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL)
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError("ATLAS_NOVO_SERVER_TERMINATED")
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/api/notebook" if view == "Notebook"
                    else f"http://127.0.0.1:{port}/api/catalog", timeout=2,
                ) as response:
                    catalog = json.load(response)
                observed = catalog.get("sources")
                if not isinstance(observed, list):
                    raise RuntimeError("ATLAS_NOVO_RESPONSE_INVALID")
                if sources and not any(s.get("status") == "READY" for s in observed):
                    raise RuntimeError("ATLAS_SELECTED_SOURCE_NOT_READY")
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(.1)
        else:
            raise RuntimeError("ATLAS_NOVO_START_TIMEOUT")
        url = f"http://127.0.0.1:{port}" + ("/notebook" if view == "Notebook" else "/")
        print("ATLAS_NOVO_READY: " + url, flush=True)
        if not sources:
            print("ATLAS_EMPTY_CATALOG: nenhuma fonte declarada; sem dados inventados.", flush=True)
        if not no_open and not probe_only:
            webbrowser.open(url)
        if probe_only:
            return 0
        code = process.wait()
        if code != 0:
            raise RuntimeError("ATLAS_NOVO_SERVER_EXIT_" + str(code))
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas novo + adaptador local opcional")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--view", choices=("Notebook", "Protocol"), default="Notebook")
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--probe-only", action="store_true",
                        help="Inicia, confere API e encerra somente o servidor criado")
    parser.add_argument("--legacy-code-root")
    parser.add_argument("--legacy-notebook-root")
    options = parser.parse_args(argv)
    if not 1024 <= options.port <= 65535:
        parser.error("ATLAS_INVALID_PORT")
    if bool(options.legacy_code_root) != bool(options.legacy_notebook_root):
        parser.error("ATLAS_LEGACY_REQUIRES_BOTH_EXPLICIT_ROOTS")
    if len(options.source) + bool(options.legacy_code_root) > 16:
        parser.error("ATLAS_MAX_16_EXPLICIT_SOURCES")
    scratch: tempfile.TemporaryDirectory[str] | None = None
    try:
        selected = [_validated_source(source) for source in options.source]
        if options.legacy_code_root:
            # This derived session cache belongs to this invocation only;
            # its original source is never moved, migrated or overwritten.
            scratch = tempfile.TemporaryDirectory(prefix="atlas-new-local-session-")
            selected.append(_prepare_legacy(options.legacy_code_root,
                                            options.legacy_notebook_root,
                                            Path(scratch.name)))
        return _start_viewer(selected, options.port, options.view,
                             options.no_open, options.probe_only)
    except (OSError, ValueError, RuntimeError) as exc:
        print("ATLAS_NOVO_BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    finally:
        if scratch is not None:
            # The only removed tree is our own TemporaryDirectory, after
            # the Atlas child has exited. No user-selected path is removed.
            try:
                scratch.cleanup()
            except OSError:
                print("ATLAS_TEMP_CLEANUP_INCOMPLETE: derived session retained.",
                      file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
