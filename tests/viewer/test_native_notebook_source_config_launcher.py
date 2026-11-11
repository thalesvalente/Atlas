"""Portable selections through the real launcher/backend; synthetic inputs only."""
from __future__ import annotations

from contextlib import chdir, redirect_stderr, redirect_stdout
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from atlas_viewer import source_config


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = ROOT / "scripts/atlas_launch.py"
MAIN = runpy.run_path(str(LAUNCHER_PATH))["main"]
NAMESPACE = MAIN.__globals__


def digests(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def unused_port():
    while True:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        if port not in {18768, 18770, 18772}:
            return port


class SourceSelectionLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="atlas-source-selection-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "pacote com espaços e ação"
        shutil.copytree(ROOT / "examples/environmental/sample", self.source)
        self.before = digests(self.source)
        self.config = self.root / "preferências locais" / "sources.json"
        self.environment = {
            "LOCALAPPDATA": str(self.root / "app-data"),
            "XDG_CONFIG_HOME": str(self.root / "xdg-config"),
        }
        self.env_patch = patch.dict(os.environ, self.environment)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def invoke(self, args, *, viewer=None):
        output, error = StringIO(), StringIO()
        viewer = viewer or Mock(return_value=0)
        with patch.dict(NAMESPACE, {"_start_viewer": viewer}):
            with redirect_stdout(output), redirect_stderr(error):
                code = MAIN(args)
        return code, output.getvalue(), error.getvalue(), viewer

    def configure(self, source=None, *, default=False):
        args = ["--configure", "--source", str(source or self.source)]
        if not default:
            args += ["--config", str(self.config)]
        code, output, error, viewer = self.invoke(args)
        self.assertEqual(code, 0, error)
        self.assertIn("ATLAS_CONFIG_SAVED", output)
        viewer.assert_not_called()

    def test_first_use_is_empty_without_writing_a_default_config(self):
        code, _, error, viewer = self.invoke([])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [])
        self.assertFalse((self.root / "app-data").exists())
        self.assertFalse((self.root / "xdg-config").exists())

    def test_save_default_reuse_and_source_bytes_stay_unchanged(self):
        self.configure(default=True)
        code, _, error, viewer = self.invoke([])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(self.source)])
        self.assertEqual(digests(self.source), self.before)

    def test_config_file_with_relative_source_uses_its_parent_not_cwd(self):
        self.config.parent.mkdir()
        self.config.write_text(json.dumps({
            "version": 1, "sources": ["../" + self.source.name],
        }), encoding="utf-8")
        elsewhere = self.root / "outro diretório"
        elsewhere.mkdir()
        with chdir(elsewhere):
            code, _, error, viewer = self.invoke(["--config", str(self.config)])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(self.source)])

    def test_explicit_source_does_not_read_malformed_selected_config(self):
        self.config.parent.mkdir()
        self.config.write_text("{broken", encoding="utf-8")
        code, _, error, viewer = self.invoke([
            "--source", str(self.source), "--config", str(self.config),
        ])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(self.source)])
        self.assertEqual(self.config.read_text(encoding="utf-8"), "{broken")

    def test_move_then_reconfigure_replaces_saved_path(self):
        self.configure()
        moved = self.root / "novo disco" / "caderno sintético"
        moved.parent.mkdir()
        shutil.move(str(self.source), str(moved))
        blocked, _, error, viewer = self.invoke(["--config", str(self.config)])
        self.assertEqual(blocked, 2)
        self.assertIn("ATLAS_SOURCE_NOT_FOUND", error)
        self.assertNotIn(str(self.source), error)
        self.assertIn("--configure", error)
        viewer.assert_not_called()
        self.configure(moved)
        code, _, error, viewer = self.invoke(["--config", str(self.config)])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(moved)])
        self.assertEqual(digests(moved), self.before)

    def test_show_is_redacted_until_paths_are_explicitly_requested(self):
        self.configure()
        before = self.config.read_bytes()
        code, output, error, viewer = self.invoke([
            "--show-config", "--config", str(self.config),
        ])
        self.assertEqual(code, 0, error)
        self.assertEqual(json.loads(output)["source_count"], 1)
        self.assertNotIn(str(self.source), output)
        self.assertNotIn(str(self.config), output)
        viewer.assert_not_called()
        code, output, error, viewer = self.invoke([
            "--show-config", "--show-paths", "--config", str(self.config),
        ])
        self.assertEqual(code, 0, error)
        shown = json.loads(output)
        self.assertEqual(shown["sources"], [str(self.source)])
        viewer.assert_not_called()
        self.assertEqual(self.config.read_bytes(), before)

    def test_clear_saved_selection_never_deletes_source(self):
        self.configure()
        code, output, error, viewer = self.invoke([
            "--clear-sources", "--config", str(self.config),
        ])
        self.assertEqual(code, 0, error)
        self.assertIn("ATLAS_CONFIG_CLEARED", output)
        viewer.assert_not_called()
        self.assertEqual(json.loads(self.config.read_text(encoding="utf-8"))["sources"], [])
        code, _, error, viewer = self.invoke(["--config", str(self.config)])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [])
        self.assertEqual(digests(self.source), self.before)

    def test_no_config_starts_empty_even_with_saved_sources(self):
        self.configure(default=True)
        code, _, error, viewer = self.invoke(["--no-config"])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [])
        code, _, error, viewer = self.invoke(["--no-config", "--source", str(self.source)])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(self.source)])

    def test_conflicting_modes_fail_without_writes_or_server(self):
        cases = [
            ["--configure"], ["--show-paths"],
            ["--configure", "--show-config", "--source", str(self.source)],
            ["--no-config", "--config", str(self.config)],
            ["--clear-sources", "--no-config"],
            ["--clear-sources", "--source", str(self.source)],
            ["--show-config", "--source", str(self.source)],
            ["--configure", "--source", str(self.source),
             "--legacy-code-root", "explicit-code", "--legacy-notebook-root", "explicit-notebook"],
        ]
        viewer = Mock(return_value=0)
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(SystemExit) as raised:
                    self.invoke(args, viewer=viewer)
                self.assertEqual(raised.exception.code, 2)
        viewer.assert_not_called()
        self.assertFalse(self.config.exists())

    def test_excess_explicit_sources_fail_before_accessing_backend(self):
        args = [value for _ in range(17) for value in ("--source", "not-opened")]
        with patch.object(source_config, "resolve_sources") as resolver:
            with self.assertRaises(SystemExit) as raised:
                self.invoke(args)
        self.assertEqual(raised.exception.code, 2)
        resolver.assert_not_called()

    def test_saved_sixteen_plus_legacy_fails_before_exporting(self):
        selected = []
        for number in range(16):
            directory = self.root / ("source-" + str(number))
            shutil.copytree(self.source, directory)
            selected.append(str(directory))
        source_config.save_sources(selected, self.config)
        prepare = Mock()
        with patch.dict(NAMESPACE, {"_prepare_legacy": prepare}):
            code, _, error, viewer = self.invoke([
                "--config", str(self.config), "--legacy-code-root", "explicit-code",
                "--legacy-notebook-root", "explicit-notebook",
            ])
        self.assertEqual(code, 2)
        self.assertIn("ATLAS_MAX_16_EXPLICIT_SOURCES", error)
        prepare.assert_not_called()
        viewer.assert_not_called()

    def test_legacy_only_does_not_inherit_default_selection_or_persist_cache(self):
        self.configure(default=True)
        prepare = Mock(return_value="explicit-temporary-export")
        with patch.dict(NAMESPACE, {"_prepare_legacy": prepare}):
            code, _, error, viewer = self.invoke([
                "--legacy-code-root", "explicit-code", "--legacy-notebook-root", "explicit-notebook",
            ])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], ["explicit-temporary-export"])
        self.assertEqual(source_config.resolve_sources(), [str(self.source)])

    def test_legacy_can_append_to_explicit_config_without_saving_export(self):
        self.configure()
        before = self.config.read_bytes()
        prepare = Mock(return_value="explicit-temporary-export")
        with patch.dict(NAMESPACE, {"_prepare_legacy": prepare}):
            code, _, error, viewer = self.invoke([
                "--config", str(self.config), "--legacy-code-root", "explicit-code",
                "--legacy-notebook-root", "explicit-notebook",
            ])
        self.assertEqual(code, 0, error)
        self.assertEqual(viewer.call_args.args[0], [str(self.source), "explicit-temporary-export"])
        self.assertEqual(self.config.read_bytes(), before)

    def test_operating_system_errors_do_not_disclose_paths(self):
        viewer = Mock(side_effect=PermissionError(13, "denied", str(self.source)))
        code, _, error, _ = self.invoke(["--source", str(self.source)], viewer=viewer)
        self.assertEqual(code, 2)
        self.assertIn("ATLAS_LOCAL_IO_FAILED", error)
        self.assertNotIn(str(self.source), error)
        self.assertNotIn("Traceback", error)

    def test_child_empty_selection_is_frozen_and_first_use_has_guidance(self):
        class Child:
            stopped = False

            def poll(self):
                return 0 if self.stopped else None

            def terminate(self):
                self.stopped = True

            def wait(self, timeout=None):
                return 0

        child = Child()
        output = StringIO()
        with patch.object(NAMESPACE["subprocess"], "Popen", return_value=child) as spawn:
            with patch.object(NAMESPACE["urllib"].request, "urlopen", return_value=StringIO("ready")):
                with redirect_stdout(output):
                    code = NAMESPACE["_start_viewer"]([], unused_port(), "Notebook", True, True)
        self.assertEqual(code, 0)
        command = spawn.call_args.args[0]
        self.assertIn("--no-config", command)
        self.assertNotIn("--source", command)
        self.assertIn("ATLAS_EMPTY_CATALOG", output.getvalue())
        self.assertIn("--configure --source", output.getvalue())
        self.assertTrue(child.stopped)


class PowerShellSourceConfigMixin:
    """Runs the actual script/interpreter on runtimes available to the runner."""
    executable = None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="atlas-ps-config-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "pacote com ação 漢字"
        self.other = self.root / "outro pacote com espaços"
        shutil.copytree(ROOT / "examples/environmental/sample", self.source)
        shutil.copytree(ROOT / "examples/environmental/sample", self.other)
        self.config = self.root / "preferências" / "sources.json"
        self.env = dict(os.environ)
        self.env.update({
            "PATH": str(Path(sys.executable).parent) + os.pathsep + self.env.get("PATH", ""),
            "LOCALAPPDATA": str(self.root / "app-data"),
            "XDG_CONFIG_HOME": str(self.root / "xdg"),
            "ATLAS_TEST_LAUNCHER": str(ROOT / "scripts/ABRIR-ATLAS.ps1"),
            "ATLAS_TEST_CONFIG": str(self.config),
            "ATLAS_TEST_SOURCE": str(self.source), "ATLAS_TEST_OTHER": str(self.other),
        })

    def invoke_ps(self, invocation):
        # Values travel in environment variables, never interpolated into
        # PowerShell source; arrays are parsed by PowerShell, not -File argv.
        harness = self.root / "invoke.ps1"
        harness.write_text(
            "$ErrorActionPreference = 'Stop'\n"
            "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding\n"
            "& $env:ATLAS_TEST_LAUNCHER " + invocation + "\n"
            "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n",
            encoding="utf-8",
        )
        return subprocess.run([
            self.executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(harness),
        ], env=self.env, capture_output=True, encoding="utf-8", errors="replace", timeout=90)

    def test_real_script_saves_two_unicode_sources_shows_and_clears(self):
        before = digests(self.source)
        result = self.invoke_ps(
            "-Configure -Config $env:ATLAS_TEST_CONFIG "
            "-Source @($env:ATLAS_TEST_SOURCE, $env:ATLAS_TEST_OTHER)"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        selected = json.loads(self.config.read_text(encoding="utf-8"))["sources"]
        self.assertEqual(selected, [str(self.source), str(self.other)])
        shown = self.invoke_ps("-ShowConfig -ShowPaths -Config $env:ATLAS_TEST_CONFIG")
        self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["sources"], selected)
        cleared = self.invoke_ps("-ClearSources -Config $env:ATLAS_TEST_CONFIG")
        self.assertEqual(cleared.returncode, 0, cleared.stdout + cleared.stderr)
        self.assertEqual(json.loads(self.config.read_text(encoding="utf-8"))["sources"], [])
        self.assertEqual(digests(self.source), before)

    def test_real_script_preserves_source_switch_and_protocol_probe(self):
        self.env["ATLAS_TEST_PORT"] = str(unused_port())
        result = self.invoke_ps(
            "-Source $env:ATLAS_TEST_SOURCE -NoConfig -View Protocol "
            "-NoOpen -ProbeOnly -Port ([int]$env:ATLAS_TEST_PORT)"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ATLAS_NOVO_READY", result.stdout)
        self.assertFalse(self.config.exists())

    def test_real_script_reports_missing_config_without_private_value(self):
        result = self.invoke_ps("-ShowConfig -Config $env:ATLAS_TEST_CONFIG")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(str(self.config), result.stdout + result.stderr)
        self.assertIn("ATLAS_NOVO_BLOCKED", result.stdout + result.stderr)


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell.exe"),
                     "PowerShell 5.1 is a Windows integration gate")
class PowerShell51SourceConfigTests(PowerShellSourceConfigMixin, unittest.TestCase):
    executable = shutil.which("powershell.exe")


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 runtime is not installed")
class PowerShell7SourceConfigTests(PowerShellSourceConfigMixin, unittest.TestCase):
    executable = shutil.which("pwsh")


if __name__ == "__main__":
    unittest.main()
