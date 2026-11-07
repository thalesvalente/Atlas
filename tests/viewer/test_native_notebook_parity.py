"""Synthetic field/pin contraproofs; no private producer data or runtime."""
import hashlib
import importlib.util
from pathlib import Path
import runpy
import tempfile
import unittest
import contextlib
import io

from atlas_viewer.native_notebook import json_bytes

ROOT = Path(__file__).resolve().parents[2]
EXPORT = runpy.run_path(str(ROOT / 'tools/export_native_notebook.py'))['export']


class NativeParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = {'atlas_integration': {'notebook_revision': 'revision-new'},
                     'records': [{'id': 'same', 'v': None}, {'id': 'same', 'v': ''},
                                 {'id': 'other', 'v': 'UNKNOWN', 'large': 9007199254740993}],
                     'result_tables': [{'id': 'T', 'rows': [{'cells': {'x': None}}, {'cells': {}}]}],
                     'empty': [], 'unknown': None}
        self.source = self.root / 'projection.json'
        self.source.write_bytes(json_bytes(self.data))
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.package = self.root / 'package'
        EXPORT(self.data, self.package)
        spec = importlib.util.spec_from_file_location('native_parity_oracle', ROOT / 'tools/verify_native_parity.py')
        self.oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.oracle)

    def verify(self, **kwargs):
        args = dict(projection=self.source, package=self.package,
                    expected_sha256=self.digest, expected_revision='revision-new')
        args.update(kwargs)
        return self.oracle.verify(**args)

    def test_all_fields_types_presence_and_homonymous_ids_roundtrip(self):
        report = self.verify()
        self.assertEqual(report['status'], 'PASS_SCOPED')
        self.assertEqual(report['authentication'], 'EXPLICIT_PIN_MATCH_ORIGIN_NOT_INFERRED')
        self.assertEqual(report['functional_browser'], 'NOT_RUN')
        self.assertTrue(report['fields'])
        self.assertTrue(all(row['imported'] == 'PASS' and row['exportable'] == 'PASS' for row in report['fields']))
        self.assertTrue(all(row['searchable_navigable'] == 'NOT_RUN' for row in report['fields']))

    def test_wrong_source_pin_and_obsolete_expected_revision_fail_closed(self):
        for override, error in [({'expected_sha256': '0' * 64}, 'PROJECTION_PIN_MISMATCH'),
                                ({'expected_revision': 'revision-old'}, 'REVISION_PIN_MISMATCH')]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self.verify(**override)

    def test_self_consistent_different_package_is_not_parity(self):
        changed = {**self.data, 'records': [{'id': 'same', 'v': False}]}
        other = self.root / 'other'
        EXPORT(changed, other)
        with self.assertRaisesRegex(ValueError, 'PROJECTION_CONTENT_MISMATCH'):
            self.verify(package=other)

    def test_tampered_package_and_high_precision_source_are_rejected(self):
        payload = next((self.package / 'data').iterdir())
        payload.write_bytes(payload.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'PACKAGE_NOT_READY'):
            self.verify()
        self.source.write_bytes(b'{"records":[],"precise":0.123456789012345678901}')
        with self.assertRaises(ValueError):
            self.verify(expected_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_cli_never_adds_report_to_a_source_package(self):
        report = self.package / 'new-report.json'
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = self.oracle.main(['--projection', str(self.source), '--package', str(self.package),
                                     '--expected-sha256', self.digest, '--expected-revision', 'revision-new',
                                     '--report', str(report)])
        self.assertEqual(code, 2)
        self.assertIn('REPORT_MUST_BE_DISJOINT_FROM_SOURCES', output.getvalue())
        self.assertFalse(report.exists())


if __name__ == '__main__':
    unittest.main()
