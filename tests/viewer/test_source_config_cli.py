"""CLI contract for synthetic persisted sources, without starting host services."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from atlas_viewer import __main__ as cli

ROOT = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


class SourceConfigCLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="atlas-config-cli-synthetic-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "synthetic source á"
        shutil.copytree(ROOT / "examples/environmental/sample", self.source)
        self.config = self.root / "settings.json"
        environment = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "xdg"),
                                             "LOCALAPPDATA": str(self.root / "local")})
        environment.start()
        self.addCleanup(environment.stop)

    def run_cli(self, arguments):
        output, error = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            try:
                code = cli.main(arguments)
            except SystemExit as exc:
                code = exc.code
        return code, output.getvalue(), error.getvalue()

    def test_config_commands_never_start_server_or_echo_paths_by_default(self):
        with patch.object(cli, "make_server", side_effect=AssertionError("SERVER_STARTED")):
            code, output, error = self.run_cli(["config", "set", "--source", str(self.source),
                                                "--config", str(self.config)])
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["source_count"], 1)
            self.assertNotIn(str(self.root), output + error)
            code, output, error = self.run_cli(["config", "show", "--config", str(self.config), "--show-paths"])
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["sources"], [str(self.source.resolve())])
            code, output, error = self.run_cli(["config", "clear", "--config", str(self.config)])
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["source_count"], 0)

    def test_configured_dossier_matches_explicit_legacy_command(self):
        self.assertEqual(self.run_cli(["config", "set", "--source", str(self.source),
                                       "--config", str(self.config)])[0], 0)
        direct = self.run_cli(["dossier", "--source", str(self.source)])
        saved = self.run_cli(["dossier", "--config", str(self.config)])
        self.assertEqual(direct[0], 0, direct[2])
        self.assertEqual(saved[0], 0, saved[2])
        a, b = json.loads(direct[1]), json.loads(saved[1])
        self.assertEqual(a["sources"], b["sources"])
        self.assertEqual(a["authority"], "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL")

    def test_default_config_is_used_without_flags_and_no_config_forces_empty(self):
        self.assertEqual(self.run_cli(["config", "set", "--source", str(self.source)])[0], 0)
        saved = self.run_cli(["dossier"])
        empty = self.run_cli(["dossier", "--no-config"])
        self.assertEqual(saved[0], 0, saved[2])
        self.assertEqual(empty[0], 0, empty[2])
        self.assertEqual(len(json.loads(saved[1])["sources"]), 1)
        self.assertEqual(json.loads(empty[1])["sources"], [])

    def test_explicit_source_is_recovery_route_for_broken_config(self):
        self.config.write_bytes(b"malformed")
        code, output, error = self.run_cli(["dossier", "--config", str(self.config),
                                            "--source", str(self.source)])
        self.assertEqual(code, 0, error)
        self.assertEqual(len(json.loads(output)["sources"]), 1)
        self.assertEqual(self.config.read_bytes(), b"malformed")

    def test_serve_resolves_saved_sources_before_constructing_server(self):
        self.run_cli(["config", "set", "--source", str(self.source), "--config", str(self.config)])
        observed = []
        class Server:
            server_address = ("127.0.0.1", 0)
            def serve_forever(self): pass
            def server_close(self): observed.append("closed")
        def create(catalog, port):
            observed.append((str(catalog.sources[0].path), port))
            return Server()
        with patch.object(cli, "make_server", side_effect=create):
            code, _, error = self.run_cli(["serve", "--config", str(self.config), "--port", "0"])
        self.assertEqual(code, 0, error)
        self.assertEqual(observed, [(str(self.source.resolve()), 0), "closed"])

    def test_invalid_configuration_fails_before_server_with_safe_actionable_error(self):
        self.config.write_text('{"version":1,"sources":["private-missing"]}', encoding="utf-8")
        with patch.object(cli, "make_server", side_effect=AssertionError("SERVER_STARTED")):
            code, output, error = self.run_cli(["serve", "--config", str(self.config)])
        self.assertEqual(code, 2)
        self.assertIn("ATLAS_SOURCE_NOT_FOUND", error)
        self.assertIn("atlas config set", error)
        self.assertNotIn("private-missing", error)
        self.assertNotIn(str(self.root), error)
        self.assertNotIn("Traceback", error)
        self.assertEqual(output, "")

    def test_inspect_keeps_protocol_reporting_and_does_not_load_configuration(self):
        with patch.object(cli, "resolve_sources", side_effect=AssertionError("CONFIG_READ")):
            code, output, error = self.run_cli(["inspect", str(self.source)])
            self.assertEqual(code, 0, error)
            self.assertEqual(json.loads(output)["sources"][0]["status"], "READY")
            code, output, error = self.run_cli(["inspect", str(self.root / "missing")])
            self.assertEqual(code, 2, error)
            self.assertEqual(json.loads(output)["sources"][0]["status"], "UNAVAILABLE")

    def test_configuration_flags_conflict_and_set_requires_explicit_source(self):
        for args in (["serve", "--config", str(self.config), "--no-config"],
                     ["config", "set", "--config", str(self.config)]):
            with self.subTest(args=args):
                self.assertEqual(self.run_cli(args)[0], 2)
        self.assertFalse(self.config.exists())


if __name__ == "__main__":
    unittest.main()
