"""C2-D integration counterproofs; no real source acquisition or fake OS proof.

As a script, execute B's exact pinned test bytes in disposable runner scratch.
The B evidence helper is loaded by exact Git blob, never altered or committed
under another owner's path. All native B tests run on the COMPOSED modules.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
B_SHA = 'bc5b634dd05d822983a8b8d5ec9c247bf47b3e4d'
B_TEST = 'tests/qa/test_atlas_parity04_f4_c2_os_sandbox.py'
B_TEST_BLOB = '07c88fcf7b5d90a56a11138f6d500ba43a071e0a'
B_HELPER = 'scripts/qa/atlas_parity04_f4_c2_os_evidence.py'
B_HELPER_BLOB = '01d8d8f473f23e674a5486517b2426151c2be965'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.atlas_legacy_presentation import reader, production, os_supervisor
from tools.atlas_legacy_presentation.errors import ReaderError
from scripts.qa import atlas_parity04_f4_c2_d_evidence as audit


class Uninspectable:
    def __fspath__(self):
        raise AssertionError('PATH_EVALUATED_BEFORE_OS_GATE')
    def __len__(self):
        raise AssertionError('ALLOWLIST_EVALUATED_BEFORE_OS_GATE')
    def __iter__(self):
        raise AssertionError('ALLOWLIST_ITERATED_BEFORE_OS_GATE')


class CompositionCounterproofs(unittest.TestCase):
    def test_reader_calls_actual_B_gate_before_any_path_or_open(self):
        token = Uninspectable()
        with patch.object(os_supervisor, 'require_production_acquisition',
                          wraps=os_supervisor.require_production_acquisition) as gate:
            with patch.object(reader, '_lexical', side_effect=AssertionError('PATH_READ')):
                with patch.object(reader, '_open_read', side_effect=AssertionError('SOURCE_READ')):
                    with self.assertRaises(ReaderError) as caught:
                        reader.prepare(token, token, token)
        self.assertEqual(caught.exception.code, 'HARD_BUDGET_UNVERIFIED')
        gate.assert_called_once_with()

    def test_returning_B_guard_does_not_activate_production(self):
        with patch.object(os_supervisor, 'require_production_acquisition', return_value=True):
            with self.assertRaises(ReaderError) as caught:
                reader.prepare(Uninspectable(), Uninspectable(), Uninspectable())
        self.assertEqual(caught.exception.code, 'OS_ISOLATION_UNVERIFIED')

    def test_returning_D_guard_still_cannot_open_source(self):
        with patch.object(production, 'require_production_profile', return_value=True):
            with self.assertRaises(ReaderError) as caught:
                reader.prepare(Uninspectable(), Uninspectable(), Uninspectable())
        self.assertEqual(caught.exception.code, 'OS_ISOLATION_UNVERIFIED')

    def test_unexpected_B_failure_is_sanitized_and_closed(self):
        with patch.object(os_supervisor, 'require_production_acquisition',
                          side_effect=RuntimeError('DO_NOT_LEAK_PRIVATE_VALUE')):
            with self.assertRaises(ReaderError) as caught:
                production.require_production_profile()
        self.assertEqual(str(caught.exception), 'OS_ISOLATION_UNVERIFIED')

    def test_truthy_flag_is_not_literal_synthetic_override(self):
        for flag in (1, 'true', [], {'approved': True}):
            with self.subTest(flag=repr(flag)):
                with self.assertRaises(ReaderError) as caught:
                    reader.prepare(Uninspectable(), Uninspectable(), Uninspectable(),
                                   synthetic_fixture=flag)
                self.assertEqual(caught.exception.code, 'HARD_BUDGET_UNVERIFIED')

    def test_cli_does_not_create_scratch_or_open_source(self):
        with tempfile.TemporaryDirectory(prefix='atlas-c2d-invented-') as tmp:
            parent = Path(tmp)
            source = parent / 'DO_NOT_LEAK_PATH.html'
            source.write_bytes(b'<script>throw new Error("MUST_NOT_EXECUTE")</script>')
            scratch = parent / 'scratch-not-created'
            for flag, code in (([], 'HARD_BUDGET_UNVERIFIED'),
                               (['--synthetic-fixture'], 'IO_UNVERIFIED')):
                command = [sys.executable, '-m', 'tools.atlas_legacy_presentation',
                           '--source', str(source), '--allow', str(source),
                           '--scratch', str(scratch), *flag]
                result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                        text=True, timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stderr)['code'], code)
                self.assertNotIn('DO_NOT_LEAK', result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertFalse(scratch.exists())
                self.assertEqual(source.read_bytes(), b'<script>throw new Error("MUST_NOT_EXECUTE")</script>')

    def test_B_never_accepts_external_paths_even_after_composition(self):
        with self.assertRaises(TypeError):
            os_supervisor.run_synthetic_probe('success', source=Uninspectable())

    def test_A_parser_and_B_gate_coexist_without_production_claim(self):
        from tools.atlas_legacy_presentation.legacy_v5 import parse_legacy_export
        from tools.atlas_legacy_presentation.legacy_v5_descriptor import transform_legacy_v5
        source = {'schema': 'r4-experiment-viewer-v5',
                  'authority': 'PRESENTATION_ONLY_NO_CLEANUP_AUTHORITY',
                  'coverage': {'limits': []},
                  **{key: [] for key in ('records', 'edges', 'resources', 'products',
                                        'result_tables', 'frontiers', 'sources', 'source_crosswalk')}}
        raw = json.dumps(source).encode('utf-8')
        parsed = parse_legacy_export(raw, media_type='application/json')
        descriptor = transform_legacy_v5(parsed, source_id='invented-d',
            snapshot_id='invented-d-snapshot', access_policy_id='invented-d-policy',
            bytes_sha256=hashlib.sha256(raw).hexdigest(),
            observed_at='2026-11-01T00:00:00Z', generated_at='2026-11-01T00:00:00Z',
            expires_at='2026-11-01T00:30:00Z', synthetic_test=True)
        self.assertEqual(descriptor['source']['original_format'], 'r4-experiment-viewer-v5')
        self.assertEqual(descriptor['version'], '0.2.0')
        self.assertTrue(descriptor['synthetic'])
        self.assertEqual(descriptor['validation']['authenticity'], 'NOT_VERIFIED')
        with self.assertRaises(ReaderError):
            production.require_production_profile()

    def test_exact_B_blobs_and_A_components_in_candidate(self):
        result = audit.verify('composed')
        self.assertEqual(len(result['source_blob_provenance']), 5)
        self.assertTrue(all(row['equality'] == 'PASS' for row in result['source_blob_provenance']))
        self.assertFalse(result['B_is_git_ancestor'])
        self.assertEqual(result['historical_manifest_entries_verified'], 22)

    def test_pinned_collection_is_confined_to_its_exact_temporary_directory(self):
        with tempfile.TemporaryDirectory(prefix='atlas-c2d-collection-') as tmp:
            target = Path(tmp).resolve() / Path(B_TEST).name
            args = pinned_pytest_arguments(target, ROOT / '.test-output/b-junit.xml')
            self.assertEqual(args[0], str(target))
            self.assertIn('--rootdir=' + str(target.parent), args)
            self.assertIn('--confcutdir=' + str(target.parent), args)
            self.assertIn('--noconftest', args)
            self.assertEqual(args[args.index('-c') + 1], str(target.parent / 'pytest.ini'))
            self.assertNotIn(str(ROOT), args)


class AuditCounterproofs(unittest.TestCase):
    def test_transient_forbidden_path_is_rejected_even_if_later_reverted(self):
        for status, path in (('M', 'packages/atlas/src/atlas/server.py'),
                             ('D', 'tools/atlas_legacy_presentation/reader.py'),
                             ('A', 'docs/missions/atlas-parity-04/f4-c2-composition/unlisted.md')):
            with self.subTest(status=status, path=path):
                with self.assertRaises(audit.AuditFailure):
                    audit.check_change(status, path, audit.D_ALLOWED)

    def test_known_file_does_not_allow_arbitrary_status_or_prefix(self):
        for status in ('R100', 'C100', 'T', 'U', '?'):
            with self.assertRaises(audit.AuditFailure):
                audit.check_change(status, audit.SCRIPT, audit.D_ALLOWED)
        with self.assertRaises(audit.AuditFailure):
            audit.check_change('M', audit.SCRIPT + '/child', audit.D_ALLOWED)

    def test_mismatch_checkout_sha_is_rejected(self):
        with patch.dict('os.environ', {'ATLAS_CHECKOUT_SHA': '0' * 40}):
            with self.assertRaisesRegex(audit.AuditFailure, 'CHECKOUT_SHA_MISMATCH'):
                audit.verify('composed')

    def test_historical_manifest_tamper_is_rejected(self):
        original = audit.git
        def altered(*args, **kwargs):
            value = original(*args, **kwargs)
            if args == ('show', audit.ORIGINAL + ':' + audit.MANIFEST):
                return value + b'\n'
            return value
        with patch.object(audit, 'git', side_effect=altered):
            with self.assertRaisesRegex(audit.AuditFailure, 'HISTORICAL_MANIFEST_DIGEST'):
                audit.historical_manifest('HEAD')

    def test_B_modified_blob_is_rejected(self):
        original = audit.entry
        def altered(sha, path):
            row = original(sha, path)
            if sha != audit.B and path in audit.B_MODULES:
                return {**row, 'blob': '0' * 40}
            return row
        with patch.object(audit, 'entry', side_effect=altered):
            with self.assertRaisesRegex(audit.AuditFailure, 'B_IMPORT_MODIFIED|B_BLOB_NOT_IDENTICAL'):
                audit.verify('composed')

    def test_merge_commit_is_rejected(self):
        original = audit.git
        def altered(*args, **kwargs):
            value = original(*args, **kwargs)
            if args[:3] == ('show', '-s', '--format=%P'):
                return value + ' ' + audit.B
            return value
        with patch.object(audit, 'git', side_effect=altered):
            with self.assertRaisesRegex(audit.AuditFailure, 'NONLINEAR_HISTORY'):
                audit.audit_phase('D', audit.A, audit.git('rev-parse', 'HEAD'), audit.D_ALLOWED)


def pinned_bytes(path, expected):
    raw = audit.git('show', B_SHA + ':' + path, raw=True)
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
    if blob != expected:
        raise RuntimeError('PINNED_B_TEST_OBJECT_MISMATCH')
    return raw


def pinned_pytest_arguments(target, junit):
    return [str(target), '-v', '-o', 'addopts=',
            '-c', str(target.parent / 'pytest.ini'),
            '--rootdir=' + str(target.parent),
            '--confcutdir=' + str(target.parent), '--noconftest',
            '--junitxml=' + str(junit)]


def run_pinned_B():
    import pytest
    import scripts.qa
    helper = pinned_bytes(B_HELPER, B_HELPER_BLOB)
    test = pinned_bytes(B_TEST, B_TEST_BLOB)
    name = 'scripts.qa.atlas_parity04_f4_c2_os_evidence'
    module = types.ModuleType(name)
    module.__file__ = 'pinned-git:' + B_SHA + ':' + B_HELPER
    exec(compile(helper, module.__file__, 'exec'), module.__dict__)
    sys.modules[name] = module
    setattr(scripts.qa, 'atlas_parity04_f4_c2_os_evidence', module)
    output = ROOT / '.test-output/atlas-parity04-f4-c2-d'
    output.mkdir(parents=True, exist_ok=True)
    junit = output / 'b-junit.xml'
    with tempfile.TemporaryDirectory(prefix='atlas-c2d-pinned-b-') as tmp:
        target = Path(tmp).resolve() / Path(B_TEST).name
        target.write_bytes(test)
        (target.parent / 'pytest.ini').write_text('[pytest]\n', encoding='utf-8')
        previous = Path.cwd()
        try:
            # Windows runner checkout and TEMP can be on different drives.
            # Never let collection climb to C:\ or consume ambient conftest.
            os.chdir(target.parent)
            status = pytest.main(pinned_pytest_arguments(target, junit))
        finally:
            os.chdir(previous)
    report = {'source_sha': B_SHA, 'test_blob': B_TEST_BLOB,
              'test_sha256': hashlib.sha256(test).hexdigest(),
              'helper_blob': B_HELPER_BLOB,
              'helper_sha256': hashlib.sha256(helper).hexdigest(),
              'tested_commit': audit.git('rev-parse', 'HEAD'),
              'test_bytes_modified': False, 'exit_code': int(status),
              'platform': sys.platform, 'python_optimize': sys.flags.optimize,
              'production': 'BLOCKED', 'source': 'INVENTED_ONLY'}
    if junit.is_file():
        cases = list(ET.parse(junit).getroot().iter('testcase'))
        skipped = [t for t in cases if t.find('skipped') is not None]
        failed = [t for t in cases if t.find('failure') is not None or t.find('error') is not None]
        report['tests'] = {'collected': len(cases), 'passed': len(cases)-len(skipped)-len(failed),
                           'skipped': len(skipped), 'failed': len(failed),
                           'skip_reasons': [{'test': t.get('name'), 'reason': t.find('skipped').get('message')} for t in skipped]}
        expected_skip = 6 if sys.platform == 'linux' else 2 if sys.platform == 'win32' else -1
        if len(cases) != 24 or len(skipped) != expected_skip or failed:
            status = 2
    else:
        status = 2
    report['gate_exit_code'] = int(status)
    (output / 'b-observed.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('C2_D_PINNED_B=' + json.dumps(report, sort_keys=True))
    return int(status)


if __name__ == '__main__':
    raise SystemExit(run_pinned_B())
