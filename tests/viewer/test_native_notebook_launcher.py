"""Standalone Atlas process boundary and opt-in legacy adapter launcher.

No actual R4 code or real Caderno data is available in public CI. The local
producer double only proves argv boundaries and installed viewer integration.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import socket
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = runpy.run_path(str(ROOT / "scripts/atlas_launch.py"))


def unused_port():
    with socket.socket() as socket_probe:
        socket_probe.bind(("127.0.0.1", 0))
        return socket_probe.getsockname()[1]


class AtlasNewLauncherTests(unittest.TestCase):
    def test_installed_new_product_starts_without_r4_or_a_caderno(self):
        output = StringIO()
        with redirect_stdout(output):
            code = LAUNCHER["main"]([
                "--port", str(unused_port()), "--no-open", "--probe-only",
            ])
        self.assertEqual(code, 0)
        self.assertIn("ATLAS_NOVO_READY: http://127.0.0.1:", output.getvalue())
        self.assertIn("ATLAS_EMPTY_CATALOG", output.getvalue())

    def test_legacy_adapter_starts_new_product_and_does_not_write_notebook(self):
        with tempfile.TemporaryDirectory(prefix="atlas-source-with-spaces-") as temp:
            root = Path(temp)
            code = root / "producer checkout with spaces"
            campaigns = code / "src/r4/campaigns"
            campaigns.mkdir(parents=True)
            (campaigns / "atlas.py").write_text(
                "from pathlib import Path\n"
                "def project(root):\n"
                "    assert Path(root).is_dir()\n"
                "    return {'records': [{'id': 'local-legacy-registry'}], "
                "'atlas_integration': {'notebook_revision': 'double-only'}}\n",
                encoding="utf-8",
            )
            notebook = root / "notebook source with spaces"
            notebook.mkdir()
            marker = notebook / "R4-WORKSPACE.json"
            marker.write_text('{"workspace_name":"R4"}', encoding="utf-8")
            # A source file must remain byte-for-byte unchanged after reading.
            record = notebook / "original-record.txt"
            record.write_bytes(b"historical-source-must-remain-intact")
            output = StringIO()
            with redirect_stdout(output):
                actual = LAUNCHER["main"]([
                    "--port", str(unused_port()), "--no-open", "--probe-only",
                    "--legacy-code-root", str(code),
                    "--legacy-notebook-root", str(notebook),
                ])
            self.assertEqual(actual, 0)
            self.assertIn("ATLAS_LEGACY_ADAPTER_READY", output.getvalue())
            self.assertIn("ATLAS_NOVO_READY", output.getvalue())
            self.assertEqual(record.read_bytes(), b"historical-source-must-remain-intact")
            self.assertEqual(sorted(notebook.iterdir()), sorted([record, marker]))

    def test_mismatched_legacy_args_fail_before_accessing_any_source(self):
        error = StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit) as captured:
            LAUNCHER["main"](["--legacy-code-root", "private"])
        self.assertEqual(captured.exception.code, 2)
        self.assertIn("ATLAS_LEGACY_REQUIRES_BOTH_EXPLICIT_ROOTS", error.getvalue())

    def test_invalid_source_never_starts_local_server(self):
        with tempfile.TemporaryDirectory() as directory:
            error = StringIO()
            with redirect_stderr(error):
                code = LAUNCHER["main"]([
                    "--source", str(Path(directory) / "missing"),
                    "--port", str(unused_port()), "--probe-only",
                ])
            self.assertEqual(code, 2)
            self.assertIn("ATLAS_SOURCE_NOT_FOUND", error.getvalue())

    def test_missing_workspace_marker_fails_before_running_producer(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            code = root / "code"
            (code / "src/r4/campaigns").mkdir(parents=True)
            (code / "src/r4/campaigns/atlas.py").write_text(
                "raise AssertionError('must not load')", encoding="utf-8"
            )
            notebook = root / "legacy-only-folder"
            notebook.mkdir()
            with self.assertRaisesRegex(ValueError, "ATLAS_LEGACY_R4_WORKSPACE_MARKER_MISSING"):
                LAUNCHER["_prepare_legacy"](str(code), str(notebook), root)
            self.assertEqual(list(notebook.iterdir()), [])

    def test_adapter_reports_safe_error_codes_without_private_paths(self):
        classifier = LAUNCHER["_safe_adapter_reason"]
        self.assertEqual(
            classifier('{"status":"BLOCKED","error":"R4_WORKSPACE_REQUIRED"}'),
            "R4_WORKSPACE_REQUIRED",
        )
        self.assertEqual(
            classifier('{"status":"BLOCKED","error":"NATIVE_ENTRY_LIMIT"}'),
            "NATIVE_ENTRY_LIMIT",
        )
        self.assertEqual(
            classifier('{"status":"BLOCKED","error":"No module named ' + "'yaml'" + '"}'),
            "PYTHON_MODULE_MISSING:yaml",
        )
        self.assertEqual(
            classifier('{"status":"BLOCKED","error":"[Errno 2] H:\\\\private\\\\records"}'),
            "DETAILS_LOCAL_ONLY",
        )
        self.assertEqual(classifier("traceback from private data"), "DETAILS_LOCAL_ONLY")

    def test_server_nonzero_exit_propagates_failure(self):
        # Source code/py subprocess need not be launched: verify the outcome
        # contract directly with a product-level process factory double.
        from unittest.mock import patch
        class NonzeroServer:
            def __init__(self):
                self.done = False
            def poll(self):
                return 9 if self.done else None
            def wait(self, timeout=None):
                self.done = True
                return 9
            def terminate(self):
                self.done = True
            def kill(self):
                self.done = True
        launcher = LAUNCHER["_start_viewer"]
        namespace = launcher.__globals__
        fake_response = type("Response", (), {
            "__enter__": lambda self: self,
            "__exit__": lambda self, *_: None,
        })()
        response = StringIO(json.dumps({"sources": []}))
        fake_response.read = response.read
        with patch.object(namespace["subprocess"], "Popen", return_value=NonzeroServer()):
            with patch.object(namespace["urllib"].request, "urlopen", return_value=fake_response):
                with self.assertRaisesRegex(RuntimeError, "ATLAS_NOVO_SERVER_EXIT_9"):
                    launcher([], unused_port(), "Notebook", True, False)


if __name__ == "__main__":
    unittest.main()
