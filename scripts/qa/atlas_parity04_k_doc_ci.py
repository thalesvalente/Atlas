"""C4: exact, additive C2-K documentary succession; never architectural approval.

The trusted harness and the documentary source have separate Git identities.
No manifest supplied by K can authorize paths, executable code or new commits.
The original F2 auditor runs unmodified on its immutable epoch; this auditor
then checks every K commit and the entire final delta against that epoch.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = 'docs/missions/atlas-parity-04/f4-c4-k-successor/SOURCE-POLICY.json'
POLICY_SHA256 = '25f35f3deb7c2b355d3e62081129b50fe23a85cd7edb207ccf09bb5954a742e9'
GUARD_PATH = 'scripts/qa/atlas_parity04_k_doc_ci.py'
HARNESS_ROOT = 'docs/missions/atlas-parity-04/f4-c4-k-successor/'
HARNESS_MANIFEST = HARNESS_ROOT + 'MANIFEST.sha256'
HARNESS_PATHS = frozenset({GUARD_PATH, POLICY_PATH, HARNESS_MANIFEST,
    HARNESS_ROOT + 'README.md', 'tests/qa/test_atlas_parity04_k_doc_ci.py',
    '.github/workflows/atlas-parity04-k-successor.yml'})
BASELINE_SHA = '54bb16d350f7bc34fafb95438bd64a2397d58bf3'
BASELINE_TREE = '1372dd532b2323fc1ebaa5c2f00b6d537c636dc9'
K_ROOT = 'docs/missions/atlas-parity-04/f4-c2-key-identity/'
K_PATHS = frozenset(K_ROOT + name for name in (
    'COMPATIBILITY-AND-MIGRATION-LESS.md', 'CURRENT-CONTRACT-COUNTEREXAMPLES.md',
    'DECISION-REQUEST.md', 'DESCRIPTOR-0.2.1-CANDIDATE.md', 'HANDOFF.json',
    'INDEPENDENT-REVIEW.md', 'INPUT-SHAS.json', 'MANIFEST.sha256',
    'OPTIONS-AND-RISK.md', 'RESULT.md', 'SYNTHETIC-IDENTITY-FIXTURES.json',
))
MAX_OBJECT_BYTES = 4 * 1024 * 1024
MAX_TREE_ENTRIES = 10000
MAX_EPOCHS = 128


class GuardError(RuntimeError):
    """Fail-closed gate with a stable, attributable error code."""


def require(condition, message):
    if not condition:
        raise GuardError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def exact_sha(value):
    require(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{40}', value) is not None,
            'EXACT_SHA_REQUIRED')
    return value


def safe_path(value):
    require(isinstance(value, str) and bool(value), 'NONCANONICAL_PATH')
    pure = PurePosixPath(value)
    require(bool(pure.parts) and not pure.is_absolute() and value == pure.as_posix()
            and all(p not in {'.', '..'} for p in pure.parts)
            and not any(c in value for c in ('\\', ':', '\x00', '\r', '\n', '\t')),
            'NONCANONICAL_PATH: ' + repr(value))
    return value


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'DUPLICATE_JSON_KEY: ' + key)
        result[key] = value
    return result


def decode_policy(raw, expected_digest):
    require(len(raw) <= MAX_OBJECT_BYTES, 'POLICY_TOO_LARGE')
    require(digest(raw) == expected_digest, 'POLICY_DIGEST_NOT_AUTHORIZED')
    data = json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda _v: require(False, 'NONFINITE_JSON_VALUE'))
    require(raw == canonical(data), 'POLICY_NOT_CANONICAL')
    required = {'schema', 'baseline', 'source_sha', 'epochs', 'files', 'manifest_path',
                'frozen_documents', 'historical_guards', 'authority'}
    require(isinstance(data, dict) and set(data) == required, 'POLICY_KEYS_DIFFER')
    require(data['schema'] == 'atlas-c4-k-source-policy/1', 'POLICY_SCHEMA_DIFFERS')
    require(data['authority'] == {'proposal': '0.2.1', 'implementation_authorized': False,
            'architectural_approval': False, 'scientific_approval': False}, 'POLICY_AUTHORITY_DIFFERS')
    epochs = data['epochs']
    require(isinstance(epochs, list) and 0 < len(epochs) <= MAX_EPOCHS, 'POLICY_EPOCH_COUNT')
    for item in [data['baseline']] + epochs:
        require(isinstance(item, dict) and set(item) == {'sha', 'tree', 'parent'}, 'POLICY_EPOCH_KEYS')
        for field in ('sha', 'tree', 'parent'):
            exact_sha(item[field])
    previous = data['baseline']['sha']
    for item in epochs:
        require(item['parent'] == previous, 'POLICY_HISTORY_NOT_LINEAR')
        previous = item['sha']
    require(data['source_sha'] == previous, 'POLICY_SOURCE_NOT_TERMINAL')
    files = data['files']
    require(isinstance(files, list) and len(files) == len(K_PATHS), 'POLICY_FILE_COUNT')
    paths = []
    for item in files:
        require(isinstance(item, dict) and set(item) == {'path', 'mode', 'blob', 'sha256'}, 'POLICY_FILE_KEYS')
        paths.append(safe_path(item['path']))
        require(item['mode'] == '100644', 'POLICY_MODE_NOT_REGULAR')
        exact_sha(item['blob'])
        require(re.fullmatch(r'[0-9a-f]{64}', item['sha256']) is not None, 'POLICY_HASH_FORMAT')
    require(paths == sorted(K_PATHS), 'POLICY_PATHS_NOT_EXACT')
    require(data['manifest_path'] == K_ROOT + 'MANIFEST.sha256', 'POLICY_MANIFEST_PATH')
    require(len(data['frozen_documents']) == 19, 'POLICY_FROZEN_DOCUMENT_COUNT')
    require(data['baseline']['sha'] == BASELINE_SHA and data['baseline']['tree'] == BASELINE_TREE,
            'POLICY_BASELINE_DIFFERS')
    return data


def git_env():
    env = {key: value for key, value in os.environ.items()
           if not key.startswith('GIT_') and key not in {'PYTHONPATH', 'PYTHONHOME'}}
    env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0',
               PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    return env


def run_git(root, *args, timeout=60):
    result = subprocess.run(['git', '--no-replace-objects', '-c', 'core.fsmonitor=false',
                             *args], cwd=root, env=git_env(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout, check=False)
    require(result.returncode == 0, 'GIT_READ_FAILED: ' + ' '.join(args)
            + ': ' + result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout


def read_object(root, oid, kind):
    exact_sha(oid)
    require(kind in {'blob', 'commit', 'tree'}, 'OBJECT_KIND_NOT_ALLOWED')
    size = int(run_git(root, 'cat-file', '-s', oid))
    require(0 <= size <= MAX_OBJECT_BYTES, 'OBJECT_TOO_LARGE')
    raw = run_git(root, 'cat-file', kind, oid)
    require(len(raw) == size, 'OBJECT_SIZE_DIFFERS')
    actual = hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(actual == oid, 'OBJECT_HASH_DIFFERS')
    return raw


def verify_epoch(root, epoch):
    raw = read_object(root, epoch['sha'], 'commit')
    headers, separator, _ = raw.partition(b'\n\n')
    require(separator == b'\n\n', 'COMMIT_HEADER_MALFORMED')
    lines = headers.split(b'\n')
    trees = [line[5:].decode('ascii') for line in lines if line.startswith(b'tree ')]
    parents = [line[7:].decode('ascii') for line in lines if line.startswith(b'parent ')]
    require(trees == [epoch['tree']] and lines[0] == b'tree ' + epoch['tree'].encode(),
            'COMMIT_TREE_DIFFERS: ' + epoch['sha'])
    require(parents == [epoch['parent']], 'COMMIT_PARENT_DIFFERS: ' + epoch['sha'])
    read_object(root, epoch['tree'], 'tree')


def tree_entries(root, sha):
    exact_sha(sha)
    raw = run_git(root, 'ls-tree', '-r', '--full-tree', '-z', sha)
    records = {}
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        path = safe_path(name.decode('utf-8'))
        require(path not in records, 'DUPLICATE_GIT_PATH')
        mode, kind, oid = meta.decode('ascii').split()
        exact_sha(oid)
        records[path] = (mode, kind, oid)
        require(len(records) <= MAX_TREE_ENTRIES, 'TREE_ENTRY_LIMIT')
    return records


def differences(before, after):
    return {path: (before.get(path), after.get(path)) for path in before.keys() | after.keys()
            if before.get(path) != after.get(path)}


def check_change_scope(changes, allowed, *, additions_only=False):
    require(set(changes) <= set(allowed), 'UNAUTHORIZED_HISTORY_PATH: '
            + ', '.join(sorted(set(changes) - set(allowed))))
    for path, (old, new) in changes.items():
        require(new is not None, 'REMOVAL_OR_RENAME_FORBIDDEN: ' + path)
        require(new[:2] == ('100644', 'blob')
                and (old is None or old[:2] == ('100644', 'blob')), 'NONREGULAR_MODE: ' + path)
        require(not additions_only or old is None, 'FINAL_PATH_NOT_ADDITIVE: ' + path)


def verify_manifest(raw, expected_files, manifest_path):
    entries = {}
    for line in raw.decode('utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        require(match is not None, 'MANIFEST_FORMAT')
        hashed, path = match.groups()
        safe_path(path)
        require(path not in entries and path != manifest_path, 'MANIFEST_DUPLICATE_OR_SELF')
        entries[path] = hashed
    require(set(entries) == set(expected_files) - {manifest_path}, 'MANIFEST_INVENTORY_DIFFERS')
    require(raw == ''.join(entries[p] + '  ' + p + '\n' for p in sorted(entries)).encode('utf-8'),
            'MANIFEST_NOT_CANONICAL')
    require(all(entries[p] == expected_files[p]['sha256'] for p in entries), 'MANIFEST_HASH_DIFFERS')
    return entries


def verify_source(root, policy, source_sha):
    """Validate immutable objects only. A working-tree file is never source evidence."""
    exact_sha(source_sha)
    require(source_sha == policy['source_sha'], 'SOURCE_SHA_NOT_AUTHORIZED')
    require(run_git(root, 'rev-parse', '--is-shallow-repository').strip() == b'false', 'SHALLOW_HISTORY')
    require(not run_git(root, 'for-each-ref', '--format=%(refname)', 'refs/replace').strip(), 'REPLACE_REFS_PRESENT')
    grafts = run_git(root, 'rev-parse', '--git-path', 'info/grafts').decode().strip()
    graft_path = Path(grafts) if Path(grafts).is_absolute() else Path(root) / grafts
    require(not graft_path.exists(), 'GRAFTS_PRESENT')
    baseline = policy['baseline']
    verify_epoch(root, baseline)
    run_git(root, 'merge-base', '--is-ancestor', baseline['sha'], source_sha)
    expected_history = [(e['sha'], e['parent']) for e in policy['epochs']]
    actual_history = [tuple(line.split()) for line in run_git(
        root, 'rev-list', '--reverse', '--parents', baseline['sha'] + '..' + source_sha).decode().splitlines()]
    require(actual_history == expected_history, 'HISTORY_NOT_EXACT')
    original = tree_entries(root, baseline['sha'])
    previous = original
    changes_by_commit = []
    allowed = {item['path'] for item in policy['files']}
    require(len(allowed) == len(policy['files']) == 11 and allowed == K_PATHS, 'SOURCE_PATHS_NOT_EXACT')
    for epoch in policy['epochs']:
        verify_epoch(root, epoch)
        current = tree_entries(root, epoch['sha'])
        changes = differences(previous, current)
        check_change_scope(changes, allowed)
        changes_by_commit.append({'sha': epoch['sha'], 'tree': epoch['tree'],
                                  'parent': epoch['parent'], 'paths': sorted(changes)})
        previous = current
    changes = differences(original, previous)
    require(set(changes) == allowed, 'FINAL_DELTA_NOT_EXACT')
    check_change_scope(changes, allowed, additions_only=True)
    files = {item['path']: item for item in policy['files']}
    blobs = {}
    for path, item in files.items():
        require(previous.get(path) == ('100644', 'blob', item['blob']), 'SOURCE_BLOB_OR_MODE_DIFFERS: ' + path)
        raw = read_object(root, item['blob'], 'blob')
        require(digest(raw) == item['sha256'], 'SOURCE_SHA256_DIFFERS: ' + path)
        blobs[path] = raw
    manifest = verify_manifest(blobs[policy['manifest_path']], files, policy['manifest_path'])
    for item in policy['frozen_documents']:
        path = item['path']
        require(original.get(path) == previous.get(path) == ('100644', 'blob', item['blob']),
                'FROZEN_DOCUMENT_DIFFERS: ' + path)
        require(digest(read_object(root, item['blob'], 'blob')) == item['sha256'], 'FROZEN_DOCUMENT_HASH_DIFFERS')
    for item in policy['historical_guards']:
        require(original.get(item['path']) == previous.get(item['path']) == ('100644', 'blob', item['blob']),
                'HISTORICAL_GUARD_DIFFERS')
        require(digest(read_object(root, item['blob'], 'blob')) == item['sha256'], 'HISTORICAL_GUARD_HASH_DIFFERS')
    return {'status': 'PASS_EXACT_K_DOCUMENTARY_SUCCESSOR', 'source_sha': source_sha,
            'source_tree': policy['epochs'][-1]['tree'], 'source_parent': policy['epochs'][-1]['parent'],
            'baseline': baseline, 'history': changes_by_commit,
            'files': policy['files'], 'manifest_entries': manifest,
            'frozen_document_count': len(policy['frozen_documents']),
            'unchanged_baseline_paths': len(original), 'source_kind': 'IMMUTABLE_GIT_OBJECTS',
            'historical_pins_modified': False, 'runtime_changed': False}


def verify_historical_f2(root, policy):
    """Run the original auditor on its own epoch; preserve that result's SHA."""
    parent = Path(tempfile.mkdtemp(prefix='atlas-c4-k-'))
    checkout = parent / 'baseline'
    output = parent / 'baseline.json'
    junit = parent / 'baseline.xml'
    registered = False
    try:
        run_git(root, 'worktree', 'add', '--detach', str(checkout), policy['baseline']['sha'])
        registered = True
        path = 'scripts/qa/atlas_parity04_f2_doc_ci.py'
        pin = next(item for item in policy['historical_guards'] if item['path'] == path)
        require(digest((checkout / path).read_bytes()) == pin['sha256'], 'BASELINE_EXECUTABLE_NOT_PINNED')
        flags = ['-O'] if sys.flags.optimize else []
        result = subprocess.run([sys.executable, *flags, str(checkout / path), 'audit',
                                 '--output', str(output), '--junit', str(junit)],
                                cwd=checkout, env=git_env(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=180, check=False)
        require(output.is_file(), 'BASELINE_RECEIPT_MISSING')
        report = json.loads(output.read_text(encoding='utf-8'))
        require(result.returncode == 0 and report.get('status') == 'PASS',
                'BASELINE_F2_REJECTED: ' + str(report.get('error', result.stderr.decode('utf-8', 'replace'))))
        require(report.get('tested_sha') == policy['baseline']['sha']
                and report.get('tested_tree') == policy['baseline']['tree'], 'BASELINE_RECEIPT_IDENTITY_DIFFERS')
        return report
    finally:
        if registered:
            # No --force: an unexpected dirty checkout remains visible as a failure.
            run_git(root, 'worktree', 'remove', str(checkout))
        for file in (output, junit):
            if file.is_file() and not file.is_symlink():
                file.unlink()
        if not any(parent.iterdir()):
            parent.rmdir()


def harness_identity(root=ROOT):
    sha = run_git(root, 'rev-parse', 'HEAD').decode().strip()
    tree = run_git(root, 'rev-parse', 'HEAD^{tree}').decode().strip()
    records = tree_entries(root, sha)
    baseline_records = tree_entries(root, BASELINE_SHA)
    run_git(root, 'merge-base', '--is-ancestor', BASELINE_SHA, sha)
    previous_sha, previous_records = BASELINE_SHA, baseline_records
    for line in run_git(root, 'rev-list', '--reverse', '--parents', BASELINE_SHA + '..' + sha).decode().splitlines():
        values = line.split()
        require(len(values) == 2 and values[1] == previous_sha, 'HARNESS_HISTORY_NOT_LINEAR')
        current = tree_entries(root, values[0])
        check_change_scope(differences(previous_records, current), HARNESS_PATHS)
        previous_sha, previous_records = values[0], current
    changes = differences(baseline_records, records)
    require(set(changes) == HARNESS_PATHS, 'HARNESS_DELTA_NOT_EXACT')
    check_change_scope(changes, HARNESS_PATHS, additions_only=True)
    evidence = {}
    for path in sorted(HARNESS_PATHS):
        target = root / path
        require(target.is_file() and not target.is_symlink(), 'HARNESS_FILE_NOT_REGULAR')
        item = records.get(path)
        require(item is not None and item[:2] == ('100644', 'blob'), 'HARNESS_FILE_NOT_COMMITTED: ' + path)
        raw = target.read_bytes()
        require(raw == read_object(root, item[2], 'blob'), 'HARNESS_WORKTREE_DIFFERS: ' + path)
        evidence[path] = {'blob': item[2], 'sha256': digest(raw)}
    verify_manifest((root / HARNESS_MANIFEST).read_bytes(), evidence, HARNESS_MANIFEST)
    return {'sha': sha, 'tree': tree, 'files': evidence,
            'owned_paths': sorted(HARNESS_PATHS), 'historical_paths_unchanged': len(baseline_records)}


def audit(root=ROOT, source_sha=None):
    report = {'status': 'FAIL', 'scope': 'C4_K_DOCUMENTARY_SUCCESSION_ONLY',
              'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'platform': platform.system(), 'python': platform.python_version(),
              'optimization': sys.flags.optimize, 'run_id': os.environ.get('GITHUB_RUN_ID'),
              'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
              'architectural_approval': False, 'scientific_approval': False,
              'descriptor_0_2_1_implementation_authorized': False,
              'composition_qualified': False, 'legacy_consumer_workflows_requalified': False}
    try:
        root = Path(root).resolve()
        policy = decode_policy((ROOT / POLICY_PATH).read_bytes(), POLICY_SHA256)
        report['harness'] = harness_identity()
        source_sha = source_sha or policy['source_sha']
        report['source'] = verify_source(root, policy, source_sha)
        report['historical_f2'] = verify_historical_f2(root, policy)
        report['status'] = 'PASS'
        report['source_sha'] = source_sha
        report['source_tree'] = report['source']['source_tree']
        report['limitations'] = [
            'Source documentary succession only; not implementation or scientific acceptance.',
            'Historical F2 proof keeps its own SHA; it is not relabeled as the new source.',
            'Existing consumer workflow routing and independent review remain separate gates.',
        ]
    except (GuardError, OSError, ValueError, TypeError, KeyError, StopIteration, subprocess.SubprocessError) as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
    return report


def write_receipt(output, junit, report):
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_bytes(canonical(report))
    temporary.replace(output)
    junit.parent.mkdir(parents=True, exist_ok=True)
    suite = ET.Element('testsuite', name='C4-K-documentary-source', tests='1',
                       failures='0' if report['status'] == 'PASS' else '1', errors='0', skipped='0')
    props = ET.SubElement(suite, 'properties')
    for name, value in [('harness_sha', report.get('harness', {}).get('sha', 'UNKNOWN')),
                        ('source_sha', report.get('source_sha', 'UNKNOWN')),
                        ('source_tree', report.get('source_tree', 'UNKNOWN'))]:
        ET.SubElement(props, 'property', name=name, value=value)
    case = ET.SubElement(suite, 'testcase', classname='C4KSuccessor', name='exact_documentary_source')
    if report['status'] != 'PASS':
        ET.SubElement(case, 'failure', message=report.get('error', 'Gate failed'))
    ET.ElementTree(suite).write(junit, encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit'])
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--source-sha')
    parser.add_argument('--output', type=Path, default=Path('.test-output/atlas-parity04-k/SOURCE.json'))
    parser.add_argument('--junit', type=Path, default=Path('.test-output/atlas-parity04-k/source.xml'))
    args = parser.parse_args()
    report = audit(args.repo, args.source_sha)
    write_receipt(args.output.resolve(), args.junit.resolve(), report)
    print('C4_K_SUCCESSOR=' + json.dumps({key: report.get(key) for key in
          ('status', 'source_sha', 'source_tree', 'harness', 'error')}, separators=(',', ':')))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
