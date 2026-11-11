"""Portable source preferences tested only with disposable synthetic packages."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from atlas_viewer import source_config as config

ROOT = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))


@contextmanager
def working_directory(path):
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def package_bytes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob("*") if p.is_file()}


class SourceConfigTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="atlas-config-synthetic-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "Pacote sintético com espaços áé"
        shutil.copytree(ROOT / "examples/environmental/sample", self.source)
        self.path = self.root / "preferences" / "sources.json"
        environment = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root / "xdg"),
                                             "LOCALAPPDATA": str(self.root / "local")})
        environment.start()
        self.addCleanup(environment.stop)

    def write_document(self, value):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(value), encoding="utf-8")

    def test_first_start_is_empty_and_does_not_create_configuration(self):
        default = config.default_config_path()
        self.assertEqual(config.resolve_sources(), [])
        self.assertEqual(config.config_summary()["source_count"], 0)
        self.assertFalse(config.config_summary()["configured"])
        self.assertFalse(default.parent.exists())

    def test_default_locations_are_user_scoped_on_both_platforms(self):
        with patch.object(config.sys, "platform", "win32"):
            self.assertEqual(config.default_config_path(), self.root / "local/Atlas/sources.json")
        with patch.object(config.sys, "platform", "linux"):
            self.assertEqual(config.default_config_path(), self.root / "xdg/atlas/sources.json")
        with patch.object(config.sys, "platform", "linux"), patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative"}):
            with self.assertRaisesRegex(config.SourceConfigError, "DEFAULT_LOCATION_INVALID"):
                config.default_config_path()

    def test_home_fallbacks_do_not_write(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "", "LOCALAPPDATA": ""}), patch.object(Path, "home", return_value=self.root):
            with patch.object(config.sys, "platform", "win32"):
                self.assertEqual(config.default_config_path(), self.root / "AppData/Local/Atlas/sources.json")
            with patch.object(config.sys, "platform", "linux"):
                self.assertEqual(config.default_config_path(), self.root / ".config/atlas/sources.json")

    def test_configure_reuse_unicode_and_keep_scientific_bytes(self):
        before = package_bytes(self.source)
        config.save_sources([str(self.source)], self.path)
        self.assertEqual(config.resolve_sources(config_path=self.path), [str(self.source.resolve())])
        raw = self.path.read_bytes()
        self.assertIn("sintético".encode(), raw)
        self.assertEqual(json.loads(raw), {"version": 1, "sources": [str(self.source.resolve())]})
        self.assertEqual(before, package_bytes(self.source))
        if os.name != "nt":
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_default_is_reused_and_explicit_config_overrides_it(self):
        other = self.root / "other package"
        shutil.copytree(self.source, other)
        config.save_sources([str(self.source)])
        config.save_sources([str(other)], self.path)
        self.assertEqual(config.resolve_sources(), [str(self.source.resolve())])
        self.assertEqual(config.resolve_sources(config_path=self.path), [str(other.resolve())])

    def test_explicit_selection_never_reads_config_even_if_missing_or_malformed(self):
        self.write_document({"not": "a config"})
        with patch.object(config, "_read_document", side_effect=AssertionError("CONFIG_READ")):
            self.assertEqual(config.resolve_sources([str(self.source)], self.path), [str(self.source.resolve())])
            self.assertEqual(config.resolve_sources([], self.path), [])

    def test_missing_explicit_config_does_not_silently_use_default(self):
        config.save_sources([str(self.source)])
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_NOT_FOUND"):
            config.resolve_sources(config_path=self.path)

    def test_new_path_after_move_can_be_saved_without_old_source(self):
        config.save_sources([str(self.source)], self.path)
        moved = self.root / "another disk synthetic"
        self.source.rename(moved)
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_SOURCE_NOT_FOUND"):
            config.resolve_sources(config_path=self.path)
        self.assertEqual(config.config_summary(self.path)["source_count"], 1)
        config.save_sources([str(moved)], self.path)
        self.assertEqual(config.resolve_sources(config_path=self.path), [str(moved.resolve())])

    def test_cli_relative_paths_are_persisted_absolute(self):
        with working_directory(self.root):
            config.save_sources([self.source.name], self.path.relative_to(self.root))
        self.assertEqual(json.loads(self.path.read_bytes())["sources"], [str(self.source.resolve())])

    def test_manually_edited_relative_paths_are_based_on_config_directory(self):
        self.write_document({"version": 1, "sources": ["../" + self.source.name]})
        with working_directory(self.source):
            self.assertEqual(config.resolve_sources(config_path=self.path), [str(self.source.resolve())])

    def test_strict_json_schema_and_version_reject_invalid_documents(self):
        cases = [([], "SCHEMA_INVALID"), ({}, "SCHEMA_INVALID"),
                 ({"version": 1, "sources": [], "extra": True}, "SCHEMA_INVALID"),
                 ({"version": True, "sources": []}, "VERSION_UNSUPPORTED"),
                 ({"version": 2, "sources": []}, "VERSION_UNSUPPORTED"),
                 ({"version": 1, "sources": "text"}, "SOURCES_INVALID"),
                 ({"version": 1, "sources": [None]}, "SOURCE_INVALID"),
                 ({"version": 1, "sources": [""]}, "SOURCE_INVALID"),
                 ({"version": 1, "sources": ["bad\x00path"]}, "SOURCE_INVALID"),
                 ({"version": 1, "sources": ["\ud800"]}, "SOURCE_INVALID")]
        for document, reason in cases:
            with self.subTest(reason=reason, document=document):
                self.write_document(document)
                before = self.path.read_bytes()
                with self.assertRaisesRegex(config.SourceConfigError, reason):
                    config.resolve_sources(config_path=self.path)
                self.assertEqual(self.path.read_bytes(), before)

    def test_malformed_duplicate_nonfinite_and_non_utf8_are_safe_errors(self):
        self.path.parent.mkdir()
        for raw in (b'{', b'{"version":1,"version":1,"sources":[]}',
                    b'{"version":NaN,"sources":[]}', b'\xff'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaises(config.SourceConfigError):
                    config.resolve_sources(config_path=self.path)

    def test_utf8_bom_from_manual_windows_edit_is_accepted(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b'\xef\xbb\xbf{"version":1,"sources":[]}')
        self.assertEqual(config.resolve_sources(config_path=self.path), [])

    def test_bounded_read_rejects_oversized_configuration(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b" " * (config.MAX_CONFIG_BYTES + 1))
        with self.assertRaisesRegex(config.SourceConfigError, "CONFIG_TOO_LARGE"):
            config.resolve_sources(config_path=self.path)

    def test_configuration_read_error_never_exposes_os_exception_paths(self):
        self.write_document({"version": 1, "sources": []})
        with patch.object(config.os, "open", side_effect=PermissionError("operator-private-location")):
            with self.assertRaisesRegex(config.SourceConfigError, "^ATLAS_CONFIG_READ_FAILED$"):
                config.resolve_sources(config_path=self.path)

    def test_count_checked_before_any_source_or_config_access(self):
        values = [str(self.root / f"not-opened-{i}") for i in range(17)]
        with patch.object(Path, "lstat", side_effect=AssertionError("SOURCE_ACCESSED")):
            with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_MAX_16"):
                config.save_sources(values, self.path)
        self.assertFalse(self.path.exists())

    def test_exactly_sixteen_distinct_sources_are_supported(self):
        values = []
        for index in range(16):
            source = self.root / f"synthetic-{index}"
            shutil.copytree(self.source, source)
            values.append(str(source))
        config.save_sources(values, self.path)
        # Windows TEMP may use an 8.3 alias; the contract persists canonical
        # absolute paths. Keep the original inputs and compare the exact order.
        expected = [str(Path(value).resolve()) for value in values]
        self.assertEqual(config.resolve_sources(config_path=self.path), expected)

    def test_duplicate_directory_metadata_and_dot_alias_are_rejected(self):
        aliases = [str(self.source), str(self.source / "."), str(self.source / "ro-crate-metadata.json")]
        for alias in aliases:
            with self.subTest(alias=alias):
                with self.assertRaisesRegex(config.SourceConfigError, "SOURCE_DUPLICATE"):
                    config.save_sources([str(self.source), alias], self.path)
        self.assertFalse(self.path.exists())

    @unittest.skipUnless(os.name == "nt", "Windows path case semantics")
    def test_windows_case_alias_is_duplicate(self):
        with self.assertRaisesRegex(config.SourceConfigError, "SOURCE_DUPLICATE"):
            config.resolve_sources([str(self.source), str(self.source).swapcase()])

    def test_missing_or_unreadable_source_has_safe_code(self):
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_SOURCE_NOT_FOUND"):
            config.save_sources([str(self.root / "operator-private-missing")], self.path)
        with patch.object(config.os, "open", side_effect=PermissionError("operator-private-location")):
            with self.assertRaisesRegex(config.SourceConfigError, "^ATLAS_SOURCE_INACCESSIBLE$"):
                config.resolve_sources([str(self.source)])

    def test_save_requires_a_compatible_package_and_preserves_invalid_source(self):
        broken = self.root / "invalid synthetic package"
        broken.mkdir()
        marker = broken / "ro-crate-metadata.json"
        marker.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_SOURCE_INVALID_PACKAGE"):
            config.save_sources([str(broken)], self.path)
        self.assertEqual(marker.read_bytes(), b"{}")
        self.assertFalse(self.path.exists())

    def test_zip_source_uses_existing_protocol_without_extraction(self):
        archive = self.root / "synthetic.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            for source in self.source.rglob("*"):
                if source.is_file():
                    stream.write(source, source.relative_to(self.source))
        before = archive.read_bytes()
        config.save_sources([str(archive)], self.path)
        self.assertEqual(config.resolve_sources(config_path=self.path), [str(archive.resolve())])
        self.assertEqual(archive.read_bytes(), before)

    def test_summary_redacts_paths_unless_explicitly_requested_and_is_read_only(self):
        config.save_sources([str(self.source)], self.path)
        before = self.path.read_bytes()
        with patch.object(config, "load_package", side_effect=AssertionError("PACKAGE_READ")):
            redacted = json.dumps(config.config_summary(self.path))
            local = config.config_summary(self.path, show_paths=True)
        self.assertNotIn(str(self.root), redacted)
        self.assertNotIn(self.source.name, redacted)
        self.assertEqual(local["sources"], [str(self.source.resolve())])
        self.assertEqual(local["config_path"], str(self.path))
        self.assertEqual(self.path.read_bytes(), before)

    def test_clear_changes_only_configuration_even_if_source_is_missing(self):
        config.save_sources([str(self.source)], self.path)
        before = package_bytes(self.source)
        config.save_sources([], self.path)
        self.assertEqual(config.resolve_sources(config_path=self.path), [])
        self.assertEqual(before, package_bytes(self.source))
        self.write_document({"version": 1, "sources": [str(self.root / "already moved")]})
        config.save_sources([], self.path)
        self.assertEqual(config.config_summary(self.path)["source_count"], 0)

    def test_save_never_overwrites_unrelated_or_malformed_existing_file(self):
        self.path.parent.mkdir()
        for before in (b"not configuration", b'{"scientific":"record"}'):
            self.path.write_bytes(before)
            with self.assertRaises(config.SourceConfigError):
                config.save_sources([str(self.source)], self.path)
            self.assertEqual(self.path.read_bytes(), before)

    def test_config_cannot_be_written_inside_selected_package_or_as_metadata(self):
        before = package_bytes(self.source)
        for target in (self.source / "preferences.json", self.source / "subdir/new.json",
                       self.source / "ro-crate-metadata.json"):
            with self.subTest(target=target):
                with self.assertRaises(config.SourceConfigError):
                    config.save_sources([str(self.source)], target)
        self.assertEqual(package_bytes(self.source), before)

    def test_arbitrarily_named_metadata_still_protects_its_package_directory(self):
        metadata = self.source / "manifest.json"
        shutil.copyfile(self.source / "ro-crate-metadata.json", metadata)
        before = package_bytes(self.source)
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_INSIDE_SOURCE"):
            config.save_sources([str(metadata)], self.source / "local-preferences.json")
        self.assertEqual(package_bytes(self.source), before)

    def test_clear_protects_previous_arbitrarily_named_metadata_package(self):
        metadata = self.source / "manifest.json"
        shutil.copyfile(self.source / "ro-crate-metadata.json", metadata)
        unsafe = self.source / "local-preferences.json"
        unsafe.write_text(json.dumps({"version": 1, "sources": ["manifest.json"]}), encoding="utf-8")
        before = package_bytes(self.source)
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_INSIDE_SOURCE"):
            config.save_sources([], unsafe)
        self.assertEqual(package_bytes(self.source), before)

    def test_clear_preserves_package_when_previous_metadata_alias_is_missing(self):
        metadata = self.source / "manifest.json"
        shutil.copyfile(self.source / "ro-crate-metadata.json", metadata)
        unsafe = self.source / "local-preferences.json"
        unsafe.write_text(json.dumps({"version": 1, "sources": ["manifest.json"]}), encoding="utf-8")
        metadata.unlink()
        before = package_bytes(self.source)
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_INSIDE_SOURCE"):
            config.save_sources([], unsafe)
        self.assertEqual(package_bytes(self.source), before)

    def test_empty_selection_cannot_create_config_beside_scientific_metadata(self):
        before = package_bytes(self.source)
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_INSIDE_SOURCE"):
            config.save_sources([], self.source / "local-preferences.json")
        self.assertEqual(package_bytes(self.source), before)

    def test_clear_does_not_write_configuration_embedded_in_previously_selected_source(self):
        unsafe = self.source / "preferences.json"
        unsafe.write_text(json.dumps({"version": 1, "sources": ["."]}), encoding="utf-8")
        before = unsafe.read_bytes()
        with self.assertRaisesRegex(config.SourceConfigError, "ATLAS_CONFIG_INSIDE_SOURCE"):
            config.save_sources([], unsafe)
        self.assertEqual(unsafe.read_bytes(), before)

    def test_symlinks_are_not_resolved_into_allowed_leaf_sources_or_configs(self):
        alias = self.root / "source-link"
        try:
            alias.symlink_to(self.source, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not grant symlink creation")
        with self.assertRaisesRegex(config.SourceConfigError, "SOURCE_UNSAFE"):
            config.resolve_sources([str(alias)])
        config.save_sources([str(self.source)], self.path)
        config_alias = self.root / "config-link.json"
        config_alias.symlink_to(self.path)
        before = self.path.read_bytes()
        for operation in (lambda: config.resolve_sources(config_path=config_alias),
                          lambda: config.save_sources([], config_alias)):
            with self.assertRaisesRegex(config.SourceConfigError, "CONFIG_FILE_UNSAFE"):
                operation()
        self.assertEqual(self.path.read_bytes(), before)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX special file")
    def test_special_configuration_file_is_rejected_without_blocking(self):
        self.path.parent.mkdir()
        os.mkfifo(self.path)
        with self.assertRaisesRegex(config.SourceConfigError, "CONFIG_FILE_UNSAFE"):
            config.resolve_sources(config_path=self.path)

    def test_write_fsync_and_replace_failures_preserve_previous_bytes(self):
        config.save_sources([str(self.source)], self.path)
        before = self.path.read_bytes()
        for target in ("Path.mkdir", "tempfile.mkstemp", "os.fsync", "os.replace"):
            with self.subTest(target=target):
                with patch("atlas_viewer.source_config." + target,
                           side_effect=OSError("operator-private-location")):
                    with self.assertRaisesRegex(config.SourceConfigError, "^ATLAS_CONFIG_WRITE_FAILED$"):
                        config.save_sources([], self.path)
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_partial_write_failure_removes_only_temporary_and_preserves_old_file(self):
        config.save_sources([str(self.source)], self.path)
        before = self.path.read_bytes()
        original = os.fdopen
        class FailingWrite:
            def __init__(self, stream): self.stream = stream
            def __enter__(self): return self
            def __exit__(self, *args): return self.stream.__exit__(*args)
            def write(self, value):
                self.stream.write(value[:4])
                raise OSError("private partial write")
        def fdopen(descriptor, mode):
            stream = original(descriptor, mode)
            return FailingWrite(stream) if mode == "wb" else stream
        with patch.object(config.os, "fdopen", side_effect=fdopen):
            with self.assertRaisesRegex(config.SourceConfigError, "CONFIG_WRITE_FAILED"):
                config.save_sources([], self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_no_directory_discovery_or_redundant_package_reads_during_resolution(self):
        config.save_sources([str(self.source)], self.path)
        with patch.object(Path, "glob", side_effect=AssertionError("SCAN")), \
             patch.object(Path, "rglob", side_effect=AssertionError("SCAN")), \
             patch.object(Path, "iterdir", side_effect=AssertionError("SCAN")), \
             patch.object(config, "load_package", side_effect=AssertionError("REPEATED_PACKAGE_READ")):
            self.assertEqual(config.resolve_sources(config_path=self.path), [str(self.source.resolve())])


if __name__ == "__main__":
    unittest.main()
