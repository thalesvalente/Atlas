"""C4-K author regression: pinned guard, synthetic Git attacks, zero skips.

This is executable author evidence, not an independent review attestation.
Synthetic policies deliberately rebind mutated object IDs to exercise semantic
checks, rather than merely relying on the production SHA allowlist.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = 'scripts/qa/atlas_parity04_k_doc_ci.py'
APPROVED_GUARD_SHA256 = '9073f060306095137e2db9fc2abc274d98da6bd847a9fae739c6bfb457391dd8'
raw = (ROOT / GUARD_PATH).read_bytes()
if hashlib.sha256(raw).hexdigest() != APPROVED_GUARD_SHA256:
    raise RuntimeError('C4_K_GUARD_SOURCE_NOT_AUTHORIZED_BEFORE_IMPORT')
spec = importlib.util.spec_from_file_location('c4_k_guard_under_test', ROOT / GUARD_PATH)
GUARD = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = GUARD
spec.loader.exec_module(GUARD)


class SyntheticRepo:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='atlas-k-negative-')
        self.root = Path(self.temporary.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'C4 synthetic fixture')
        self.git('config', 'user.email', 'c4-synthetic@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'core.symlinks', 'false')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.hooksPath', str(self.root / 'no-hooks'))
        self.write('README.md', b'Synthetic public fixture only.\n')
        self.commit('seed')
        self.frozen_paths = [f'docs/frozen/{i:02}.md' for i in range(19)]
        for path in self.frozen_paths:
            self.write(path, ('frozen:' + path + '\n').encode())
        self.guard_paths = ['scripts/qa/atlas_parity04_doc_ci.py',
                            'scripts/qa/atlas_parity04_f2_doc_ci.py']
        for path in self.guard_paths:
            self.write(path, b'# synthetic inert historical guard\n')
        self.write('packages/protocol/runtime.py', b'# unchanged runtime\n')
        self.base = self.commit('baseline')
        self.baseline = self.epoch(self.base)
        self.frozen = self.files(self.frozen_paths)
        self.historical = self.files(self.guard_paths)
        self.manifest_path = GUARD.K_ROOT + 'MANIFEST.sha256'
        for path in sorted(GUARD.K_PATHS - {self.manifest_path}):
            self.write(path, ('synthetic document:' + path + '\n').encode())
        self.refresh_manifest()
        self.source = self.commit('K documentary source')
        self.policy = self.current_policy()

    def close(self):
        self.temporary.cleanup()

    def git(self, *args, input=None):
        result = subprocess.run(['git', *args], cwd=self.root, env=GUARD.git_env(),
                                input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                check=False, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
        return result.stdout

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def commit(self, message, *, staged=False):
        if not staged:
            self.git('add', '-A')
        self.git('commit', '-q', '--allow-empty', '-m', message)
        return self.git('rev-parse', 'HEAD').decode().strip()

    def epoch(self, sha):
        values = self.git('show', '-s', '--format=%T%n%P', sha).decode().strip().splitlines()
        return {'sha': sha, 'tree': values[0], 'parent': values[1]}

    def files(self, paths, ref='HEAD'):
        records = GUARD.tree_entries(self.root, self.git('rev-parse', ref).decode().strip())
        result = []
        for path in sorted(paths):
            if path not in records:
                continue
            mode, kind, oid = records[path]
            raw = self.git('cat-file', kind, oid)
            result.append({'path': path, 'mode': mode, 'blob': oid, 'sha256': GUARD.digest(raw)})
        return result

    def current_policy(self):
        source = self.git('rev-parse', 'HEAD').decode().strip()
        shas = self.git('rev-list', '--reverse', self.base + '..' + source).decode().split()
        return {'baseline': self.baseline, 'source_sha': source,
                'epochs': [self.epoch(sha) for sha in shas],
                'files': self.files(GUARD.K_PATHS), 'manifest_path': self.manifest_path,
                'frozen_documents': self.frozen, 'historical_guards': self.historical}

    def refresh_manifest(self):
        raw = ''.join(GUARD.digest((self.root / path).read_bytes()) + '  ' + path + '\n'
                      for path in sorted(GUARD.K_PATHS - {self.manifest_path})).encode()
        self.write(self.manifest_path, raw)

    def stage_mode(self, path, mode, data=None, oid=None):
        if oid is None:
            oid = self.git('hash-object', '-w', '--stdin', input=data).decode().strip()
        self.git('update-index', '--add', '--cacheinfo', mode + ',' + oid + ',' + path)


class KSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.repo = SyntheticRepo()
        self.addCleanup(self.repo.close)

    def check(self, policy=None, source=None):
        policy = policy or self.repo.policy
        return GUARD.verify_source(self.repo.root, policy, source or policy['source_sha'])

    def reject(self, code, policy=None, source=None):
        with self.assertRaisesRegex(GUARD.GuardError, code):
            self.check(policy, source)

    def amend_manifest(self, raw):
        self.repo.write(self.repo.manifest_path, raw)
        self.repo.commit('manifest mutation')
        return self.repo.current_policy()

    def test_exact_positive_keeps_all_nineteen_frozen_documents(self):
        report = self.check()
        self.assertEqual(report['status'], 'PASS_EXACT_K_DOCUMENTARY_SUCCESSOR')
        self.assertEqual(report['frozen_document_count'], 19)
        self.assertFalse(report['runtime_changed'])
        self.assertFalse(report['historical_pins_modified'])

    def test_exact_authorized_two_commit_history(self):
        path = GUARD.K_ROOT + 'RESULT.md'
        self.repo.write(path, b'authorized successor document\n')
        self.repo.refresh_manifest()
        self.repo.commit('authorized K-only epoch')
        policy = self.repo.current_policy()
        self.assertEqual(len(self.check(policy)['history']), 2)

    def test_source_sha_must_be_authorized_exact_commit(self):
        self.reject('SOURCE_SHA_NOT_AUTHORIZED', source=self.repo.base)

    def test_branch_abbreviation_and_revision_expression_are_not_sha(self):
        for source in ('HEAD', self.repo.source[:12], self.repo.source + '^', '--all', 'A' * 40):
            with self.subTest(source=source):
                self.reject('EXACT_SHA_REQUIRED', source=source)

    def test_baseline_tree_mismatch(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['baseline']['tree'] = policy['epochs'][0]['tree']
        self.reject('COMMIT_TREE_DIFFERS', policy)

    def test_source_tree_mismatch(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['epochs'][0]['tree'] = policy['baseline']['tree']
        self.reject('COMMIT_TREE_DIFFERS', policy)

    def test_baseline_parent_mismatch(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['baseline']['parent'] = self.repo.source
        self.reject('COMMIT_PARENT_DIFFERS', policy)

    def test_source_parent_mismatch(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['epochs'][0]['parent'] = policy['baseline']['parent']
        self.reject('HISTORY_NOT_EXACT', policy)

    def test_extra_document_rejected_even_with_rebound_commit(self):
        self.repo.write(GUARD.K_ROOT + 'UNAUTHORIZED.md', b'extra\n')
        self.repo.commit('extra K document')
        self.reject('UNAUTHORIZED_HISTORY_PATH', self.repo.current_policy())

    def test_runtime_edit_rejected_even_with_rebound_commit(self):
        self.repo.write('packages/protocol/runtime.py', b'changed runtime\n')
        self.repo.commit('runtime alteration')
        self.reject('UNAUTHORIZED_HISTORY_PATH', self.repo.current_policy())

    def test_all_nineteen_historical_edits_rejected(self):
        for path in self.repo.frozen_paths:
            with self.subTest(path=path):
                isolated = SyntheticRepo()
                try:
                    isolated.write(path, b'tampered\n')
                    isolated.commit('one historical alteration')
                    policy = isolated.current_policy()
                    with self.assertRaisesRegex(GUARD.GuardError, 'UNAUTHORIZED_HISTORY_PATH'):
                        GUARD.verify_source(isolated.root, policy, policy['source_sha'])
                finally:
                    isolated.close()

    def test_historical_guard_edit_is_not_a_successor(self):
        self.repo.write(self.repo.guard_paths[0], b'# tampered\n')
        self.repo.commit('guard alteration')
        self.reject('UNAUTHORIZED_HISTORY_PATH', self.repo.current_policy())

    def test_transient_extra_path_then_revert_is_rejected(self):
        self.repo.write('temporary-bypass.py', b'pass\n')
        self.repo.commit('hidden intermediate alteration')
        (self.repo.root / 'temporary-bypass.py').unlink()
        self.repo.commit('erase final evidence')
        self.reject('UNAUTHORIZED_HISTORY_PATH', self.repo.current_policy())

    def test_transient_historical_edit_then_revert_is_rejected(self):
        path = self.repo.frozen_paths[0]
        self.repo.write(path, b'tampered\n')
        self.repo.commit('transient history edit')
        self.repo.git('restore', '--source', self.repo.base, '--', path)
        self.repo.commit('revert history edit')
        self.reject('UNAUTHORIZED_HISTORY_PATH', self.repo.current_policy())

    def test_unlisted_empty_intermediate_commit_is_rejected(self):
        self.repo.commit('unlisted empty intermediary')
        final = self.repo.commit('listed terminal')
        policy = self.repo.current_policy()
        policy['epochs'].pop(1)
        self.assertEqual(final, policy['source_sha'])
        self.reject('HISTORY_NOT_EXACT', policy)

    def test_unlisted_document_only_commit_is_rejected(self):
        self.repo.write(GUARD.K_ROOT + 'RESULT.md', b'changed\n')
        self.repo.refresh_manifest()
        self.repo.commit('unlisted K epoch')
        self.repo.commit('listed terminal')
        policy = self.repo.current_policy()
        policy['epochs'].pop(1)
        self.reject('HISTORY_NOT_EXACT', policy)

    def test_two_parent_commit_is_rejected(self):
        tree = self.repo.git('rev-parse', 'HEAD^{tree}').decode().strip()
        merge = self.repo.git('commit-tree', tree, '-p', self.repo.source, '-p', self.repo.base,
                              '-m', 'synthetic forbidden two-parent').decode().strip()
        policy = copy.deepcopy(self.repo.policy)
        policy['source_sha'] = merge
        policy['epochs'].append({'sha': merge, 'tree': tree, 'parent': self.repo.source})
        self.reject('HISTORY_NOT_EXACT', policy)

    def test_rename_is_rejected(self):
        source = GUARD.K_ROOT + 'RESULT.md'
        self.repo.git('mv', source, GUARD.K_ROOT + 'RENAMED.md')
        self.repo.commit('rename', staged=True)
        policy = self.repo.current_policy()
        policy['files'] = self.repo.policy['files']
        self.reject('UNAUTHORIZED_HISTORY_PATH', policy)

    def test_remove_then_restore_authorized_path_is_rejected(self):
        path = GUARD.K_ROOT + 'RESULT.md'
        raw = (self.repo.root / path).read_bytes()
        (self.repo.root / path).unlink()
        self.repo.commit('delete allowed document')
        self.repo.write(path, raw)
        self.repo.commit('restore allowed document')
        self.reject('REMOVAL_OR_RENAME_FORBIDDEN', self.repo.current_policy())

    def test_symlink_mode_is_rejected_without_host_symlink_permission(self):
        self.repo.stage_mode(GUARD.K_ROOT + 'RESULT.md', '120000', b'../../../../README.md')
        self.repo.commit('symlink', staged=True)
        self.reject('NONREGULAR_MODE', self.repo.current_policy())

    def test_executable_document_mode_is_rejected(self):
        self.repo.stage_mode(GUARD.K_ROOT + 'RESULT.md', '100755', b'#!/bin/sh\n')
        self.repo.commit('executable', staged=True)
        self.reject('NONREGULAR_MODE', self.repo.current_policy())

    def test_gitlink_document_mode_is_rejected(self):
        self.repo.stage_mode(GUARD.K_ROOT + 'RESULT.md', '160000', oid=self.repo.base)
        self.repo.commit('gitlink', staged=True)
        policy = self.repo.current_policy()
        self.reject('NONREGULAR_MODE', policy)

    def test_wrong_pinned_source_blob_is_rejected(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['files'][0]['blob'] = policy['files'][1]['blob']
        self.reject('SOURCE_BLOB_OR_MODE_DIFFERS', policy)

    def test_wrong_pinned_source_sha256_is_rejected(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['files'][0]['sha256'] = '0' * 64
        self.reject('SOURCE_SHA256_DIFFERS', policy)

    def test_frozen_pin_cannot_be_substituted(self):
        policy = copy.deepcopy(self.repo.policy)
        policy['frozen_documents'][0]['blob'] = policy['frozen_documents'][1]['blob']
        self.reject('FROZEN_DOCUMENT_DIFFERS', policy)

    def test_manifest_wrong_hash_rejected_even_when_manifest_blob_is_rebound(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes()
        self.reject('MANIFEST_HASH_DIFFERS', self.amend_manifest(b'0' * 64 + raw[64:]))

    def test_manifest_duplicate_entry(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes()
        self.reject('MANIFEST_DUPLICATE_OR_SELF', self.amend_manifest(raw + raw.splitlines(keepends=True)[0]))

    def test_manifest_self_inclusion(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes()
        raw += ('0' * 64 + '  ' + self.repo.manifest_path + '\n').encode()
        self.reject('MANIFEST_DUPLICATE_OR_SELF', self.amend_manifest(raw))

    def test_manifest_missing_entry(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes().splitlines(keepends=True)
        self.reject('MANIFEST_INVENTORY_DIFFERS', self.amend_manifest(b''.join(raw[1:])))

    def test_manifest_extra_entry(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes()
        self.reject('MANIFEST_INVENTORY_DIFFERS', self.amend_manifest(raw + b'0' * 64 + b'  README.md\n'))

    def test_manifest_noncanonical_order(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes().splitlines(keepends=True)
        self.reject('MANIFEST_NOT_CANONICAL', self.amend_manifest(b''.join(reversed(raw))))

    def test_manifest_crlf_not_silently_normalized(self):
        raw = (self.repo.root / self.repo.manifest_path).read_bytes().replace(b'\n', b'\r\n')
        self.reject('MANIFEST_NOT_CANONICAL', self.amend_manifest(raw))

    def test_manifest_traversal_dot_and_alias_paths(self):
        for path in ('../outside', './README.md', 'docs//evil', 'docs/../evil',
                     '/absolute', 'C:/absolute', 'docs\\evil', '.', ''):
            with self.subTest(path=path):
                with self.assertRaises(GUARD.GuardError):
                    GUARD.safe_path(path)

    def test_policy_digest_is_not_self_authorizing(self):
        policy = (ROOT / GUARD.POLICY_PATH).read_bytes()
        with self.assertRaisesRegex(GUARD.GuardError, 'POLICY_DIGEST_NOT_AUTHORIZED'):
            GUARD.decode_policy(policy + b' ', GUARD.POLICY_SHA256)

    def test_policy_extra_path_rejected_even_with_caller_rehash(self):
        policy = json.loads((ROOT / GUARD.POLICY_PATH).read_text(encoding='utf-8'))
        policy['files'][0]['path'] = GUARD.K_ROOT + 'EXTRA.md'
        raw = GUARD.canonical(policy)
        with self.assertRaisesRegex(GUARD.GuardError, 'POLICY_PATHS_NOT_EXACT'):
            GUARD.decode_policy(raw, GUARD.digest(raw))

    def test_policy_authority_promotion_is_rejected(self):
        policy = json.loads((ROOT / GUARD.POLICY_PATH).read_text(encoding='utf-8'))
        policy['authority']['implementation_authorized'] = True
        raw = GUARD.canonical(policy)
        with self.assertRaisesRegex(GUARD.GuardError, 'POLICY_AUTHORITY_DIFFERS'):
            GUARD.decode_policy(raw, GUARD.digest(raw))

    def test_policy_duplicate_json_keys_are_rejected(self):
        raw = b'{"schema":1,"schema":2}'
        with self.assertRaisesRegex(GUARD.GuardError, 'DUPLICATE_JSON_KEY'):
            GUARD.decode_policy(raw, GUARD.digest(raw))

    def test_policy_nonfinite_json_is_rejected(self):
        raw = b'{"schema":NaN}'
        with self.assertRaisesRegex(GUARD.GuardError, 'NONFINITE_JSON_VALUE'):
            GUARD.decode_policy(raw, GUARD.digest(raw))

    def test_replace_ref_is_rejected(self):
        self.repo.git('update-ref', 'refs/replace/' + self.repo.base, self.repo.source)
        self.reject('REPLACE_REFS_PRESENT')

    def test_graft_file_is_rejected(self):
        self.repo.write('.git/info/grafts', b'')
        self.reject('GRAFTS_PRESENT')

    def test_shallow_history_is_rejected(self):
        self.repo.write('.git/shallow', (self.repo.base + '\n').encode())
        self.reject('SHALLOW_HISTORY')

    def test_object_identity_is_rehashed_not_just_named(self):
        with self.assertRaisesRegex(GUARD.GuardError, 'OBJECT_SIZE_DIFFERS|OBJECT_HASH_DIFFERS|GIT_READ_FAILED'):
            GUARD.read_object(self.repo.root, self.repo.source, 'blob')

    def test_worktree_document_tampering_is_not_mistaken_for_committed_source(self):
        self.repo.write(GUARD.K_ROOT + 'RESULT.md', b'UNCOMMITTED TAMPER\n')
        report = self.check()
        self.assertEqual(report['source_kind'], 'IMMUTABLE_GIT_OBJECTS')
        self.assertEqual(report['source_sha'], self.repo.source)

    def test_production_policy_parses_with_exact_eleven_paths(self):
        policy = GUARD.decode_policy((ROOT / GUARD.POLICY_PATH).read_bytes(), GUARD.POLICY_SHA256)
        self.assertEqual({x['path'] for x in policy['files']}, GUARD.K_PATHS)
        self.assertEqual(len(policy['frozen_documents']), 19)


class ReceiptResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids = []

    def startTest(self, test):
        self.ids.append(test.id())
        super().startTest(test)


def run(output, junit):
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(KSuccessorTests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=ReceiptResult).run(suite)
    failed = {test.id(): detail for test, detail in result.failures + result.errors}
    passed = (result.wasSuccessful() and result.testsRun == len(result.ids) == len(set(result.ids))
              and result.testsRun > 0 and not result.skipped and not loader.errors
              and not result.expectedFailures and not result.unexpectedSuccesses)
    report = {'status': 'PASS' if passed else 'FAIL', 'tests_run': result.testsRun,
              'test_ids': result.ids, 'failures': len(result.failures), 'errors': len(result.errors),
              'skips': len(result.skipped), 'loader_errors': loader.errors,
              'optimization': sys.flags.optimize, 'guard_sha256': APPROVED_GUARD_SHA256,
              'policy_sha256': GUARD.POLICY_SHA256, 'author_validation_not_independent_review': True,
              'harness_sha': GUARD.run_git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
              'harness_tree': GUARD.run_git(ROOT, 'rev-parse', 'HEAD^{tree}').decode().strip(),
              'worktree_clean': not GUARD.run_git(ROOT, 'status', '--porcelain').strip(),
              'details': failed}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(GUARD.canonical(report))
    junit.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element('testsuite', name='C4-K-synthetic-regressions', tests=str(result.testsRun),
                      failures=str(len(result.failures)), errors=str(len(result.errors)), skipped=str(len(result.skipped)))
    for name in result.ids:
        case = ET.SubElement(root, 'testcase', classname='C4KRegression', name=name)
        matching = [detail for key, detail in failed.items() if key == name or key.startswith(name + ' (')]
        if matching:
            ET.SubElement(case, 'failure', message='See JSON receipt').text = '\n'.join(matching)
    ET.ElementTree(root).write(junit, encoding='utf-8', xml_declaration=True)
    print('C4_K_REGRESSIONS=' + json.dumps({k: report[k] for k in
          ('status', 'tests_run', 'optimization', 'failures', 'errors', 'skips', 'worktree_clean')}))
    return 0 if passed else 1


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--junit', type=Path, required=True)
    args = cli.parse_args()
    raise SystemExit(run(args.output.resolve(), args.junit.resolve()))
