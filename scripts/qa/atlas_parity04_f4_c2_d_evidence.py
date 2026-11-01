"""C2-D successor audit: immutable baselines, every commit, exact B blobs.

Read-only Git audit. It does not qualify production, source identity, Windows
confinement or human approval. No manifest/pin is rewritten by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
F2 = '54bb16d350f7bc34fafb95438bd64a2397d58bf3'
ORIGINAL = '258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7'
V5 = 'e349a09d439d292011bca4c0994cf8ab3e3fbf9f'
A = 'c52215f73292435a2db3525cd7a8b226f13672d7'
B = 'bc5b634dd05d822983a8b8d5ec9c247bf47b3e4d'
K = 'ab22a78eb22af4ef9651cdd8f652c3cb2755e947'
PINS = {
    F2: ('1372dd532b2323fc1ebaa5c2f00b6d537c636dc9', 'bd2166651f159e70a8165e0f12c8ad2a3270a0d6'),
    ORIGINAL: ('f268d4cf450cf5baa73c5d51e34fc0d6fba3a59f', '9bbf6891433bbe1457a818afcd42ead44d95a07e'),
    V5: ('1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df', '136e3663ffa4be9b0294b7a2d8a6f5f1ae567104'),
    A: ('ef37bddc1362b9f4201403253264338ee9a5a745', 'dcd219bf592f47590413424adfdf6513a0daa18f'),
    B: ('73fa6e6e069fef970d17b5e13480351c001ca618', '29f0e144e7470794df721806ed1485d50000a05b'),
    K: ('316e2cafd2baddbfdac6885b1ab9676cd7563bf8', F2),
}
DOC = 'docs/missions/atlas-parity-04/'
TOOL = 'tools/atlas_legacy_presentation/'
WF = '.github/workflows/atlas-parity04-f4-c2-reader.yml'
SCRIPT = 'scripts/qa/atlas_parity04_f4_c2_d_evidence.py'
MANIFEST = DOC + 'f4-c2-reader/MANIFEST.sha256'
MANIFEST_SHA256 = 'e5c459a2a5bb974cbdea5f38cd6ba8060c212e919900b6ee56dd9bc17a75c1f7'
V5_ALLOWED = frozenset({WF, DOC + 'f4-c2-reader/REAL-V5-TRANSFER-AND-IMPLEMENTATION.md',
    TOOL + 'parser.py', TOOL + 'legacy_v5.py', TOOL + 'legacy_v5_descriptor.py',
    'tests/qa/test_atlas_parity04_f4_c2_real_v5.py',
    'tests/qa/test_atlas_parity04_f4_c2_v5_descriptor.py',
    'scripts/qa/atlas_parity04_f4_c2_v5_evidence.py'})
A_DOCS = {'CI-EVIDENCE.json', 'HANDOFF.json', 'INDEPENDENT-REVIEW.md',
          'MANIFEST.sha256', 'NEGATIVE-TESTS.json', 'PLAN.md',
          'REAL-V5-FIELD-MAPPING.md', 'RESULT.md', 'SOURCE-KEY-GAPS.md'}
A_ALLOWED = frozenset({DOC + 'f4-c2-real-v5/' + p for p in A_DOCS} | {
    TOOL + 'legacy_v5.py', TOOL + 'legacy_v5_descriptor.py',
    'tests/qa/test_atlas_parity04_f4_c2_v5_descriptor.py'})
B_MODULES = frozenset(TOOL + p for p in ('os_supervisor.py', 'os_worker.py',
    'os_linux_isolation.py', 'os_windows_job.py', 'os_windows_acl.py'))
B_DOCS = {'CI-EVIDENCE.json', 'HANDOFF.json', 'INDEPENDENT-REVIEW.md', 'MANIFEST.sha256',
          'NEGATIVE-TESTS.json', 'OS-POLICY-AND-CAPABILITIES.md', 'RESULT.md', 'THREAT-MODEL.md'}
B_ALLOWED = frozenset(set(B_MODULES) | {DOC + 'f4-c2-os-sandbox/' + p for p in B_DOCS} | {
    '.github/workflows/atlas-parity04-f4-c2-os-sandbox.yml',
    'scripts/qa/atlas_parity04_f4_c2_os_evidence.py',
    'tests/qa/test_atlas_parity04_f4_c2_os_sandbox.py'})
D_DOCS = {'RESULT.md', 'INPUT-SHAS.json', 'COMPOSITION-OBJECTS.json',
          'SOURCE-BLOB-PROVENANCE.json', 'SECURITY-AND-HARD-BUDGETS.json',
          'NEGATIVE-TESTS.json', 'CI-EVIDENCE.json', 'INDEPENDENT-REVIEW.md',
          'HANDOFF.json', 'MANIFEST.sha256', 'COMMIT-PATHS-AUDIT.json'}
D_ALLOWED = frozenset(set(B_MODULES) | {DOC + 'f4-c2-composition/' + p for p in D_DOCS} | {
    TOOL + 'reader.py', TOOL + '__main__.py', TOOL + 'production.py', SCRIPT, WF,
    'tests/qa/test_atlas_parity04_f4_c2_d_composition.py',
    'tests/qa/test_atlas_parity04_f4_c2_d_evidence.py'})


class AuditFailure(RuntimeError):
    pass


def must(ok: bool, code: str) -> None:
    if not ok:
        raise AuditFailure(code)


def git(*args: str, raw: bool = False):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, timeout=45)
    must(result.returncode == 0, 'GIT_READ_FAILED:' + args[0])
    return result.stdout if raw else result.stdout.decode('utf-8').strip()


def ancestor(base: str, head: str) -> bool:
    result = subprocess.run(['git', 'merge-base', '--is-ancestor', base, head],
                            cwd=ROOT, capture_output=True, timeout=45)
    must(result.returncode in (0, 1), 'ANCESTRY_OBJECT_UNAVAILABLE')
    return result.returncode == 0


def entry(sha: str, path: str) -> dict:
    raw = git('ls-tree', '-z', sha, '--', path, raw=True)
    must(raw.count(b'\0') == 1, 'EXACT_BLOB_MISSING:' + path)
    metadata, found = raw[:-1].split(b'\t', 1)
    mode, kind, oid = metadata.decode('ascii').split()
    must(found.decode('utf-8') == path and mode == '100644' and kind == 'blob',
         'BLOB_TYPE_OR_MODE_INVALID:' + path)
    return {'path': path, 'mode': mode, 'blob': oid}


def changes(parent: str, revision: str) -> list[tuple[str, str]]:
    parts = git('diff', '--name-status', '-z', '--no-renames', parent, revision,
                raw=True).decode('utf-8').split('\0')
    must(parts[-1] == '', 'DIFF_NOT_NUL_TERMINATED')
    parts.pop()
    must(len(parts) % 2 == 0, 'DIFF_FORMAT_INVALID')
    return list(zip(parts[::2], parts[1::2]))


def check_change(status: str, path: str, allowed: frozenset[str]) -> None:
    must(status in ('A', 'M') and path in allowed,
         'UNAUTHORIZED_HISTORY_PATH:' + status + ':' + path)


def audit_phase(name: str, base: str, head: str, allowed: frozenset[str]) -> dict:
    must(ancestor(base, head), name + ':ANCESTRY_INVALID')
    revisions = git('rev-list', '--reverse', base + '..' + head).splitlines()
    previous = base
    commits = []
    for revision in revisions:
        parents = git('show', '-s', '--format=%P', revision).split()
        must(parents == [previous], name + ':NONLINEAR_HISTORY:' + revision)
        rows = []
        for status, path in changes(previous, revision):
            check_change(status, path, allowed)
            row = {'status': status, **entry(revision, path)}
            if name == 'D' and path in B_MODULES:
                must(row['blob'] == entry(B, path)['blob'], 'B_IMPORT_MODIFIED:' + path)
            rows.append(row)
        commits.append({'sha': revision, 'parents': parents,
                        'tree': git('rev-parse', revision + '^{tree}'), 'changes': rows})
        previous = revision
    must(previous == head, name + ':HISTORY_INCOMPLETE')
    return {'phase': name, 'base': base, 'head': head, 'commits': commits,
            'commit_count': len(commits), 'status': 'PASS'}


def historical_manifest(head: str) -> frozenset[str]:
    raw = git('show', ORIGINAL + ':' + MANIFEST, raw=True)
    must(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, 'HISTORICAL_MANIFEST_DIGEST')
    must(git('show', head + ':' + MANIFEST, raw=True) == raw, 'HISTORICAL_MANIFEST_CHANGED')
    paths = set()
    for line in raw.decode('utf-8').splitlines():
        expected, separator, path = line.partition('  ')
        must(separator == '  ' and re.fullmatch('[a-f0-9]{64}', expected) is not None
             and path not in paths and path != MANIFEST and not path.startswith('/')
             and '..' not in path.split('/'), 'HISTORICAL_MANIFEST_INVALID')
        must(hashlib.sha256(git('show', ORIGINAL + ':' + path, raw=True)).hexdigest()
             == expected, 'HISTORICAL_BLOB_DIGEST:' + path)
        entry(ORIGINAL, path)
        paths.add(path)
    must(len(paths) == 22, 'HISTORICAL_MANIFEST_ENTRY_COUNT')
    return frozenset(paths)


def verify(stage: str) -> dict:
    head = git('rev-parse', 'HEAD')
    expected = os.getenv('ATLAS_CHECKOUT_SHA')
    must(not expected or head == expected, 'CHECKOUT_SHA_MISMATCH')
    objects = []
    for sha, (tree, parent) in PINS.items():
        must(git('rev-parse', sha + '^{tree}') == tree and
             git('show', '-s', '--format=%P', sha) == parent, 'PIN_OBJECT_MISMATCH:' + sha)
        objects.append({'sha': sha, 'tree': tree, 'parents': [parent]})
    historical = historical_manifest(head)
    phases = [audit_phase('original', F2, ORIGINAL, historical | {MANIFEST}),
              audit_phase('v5-initial', ORIGINAL, V5, V5_ALLOWED),
              audit_phase('A', V5, A, A_ALLOWED),
              audit_phase('B', V5, B, B_ALLOWED),
              audit_phase('D', A, head, D_ALLOWED)]
    must(not ancestor(B, head), 'B_MUST_BE_IMPORTED_BY_BLOB_NOT_MERGE')
    imported = []
    for path in sorted(B_MODULES):
        source = entry(B, path)
        row = {'source_sha': B, 'source_path': path, **source,
               'sha256': hashlib.sha256(git('show', B + ':' + path, raw=True)).hexdigest()}
        if stage == 'composed':
            current = entry(head, path)
            must(current == source, 'B_BLOB_NOT_IDENTICAL:' + path)
            row['target_blob'] = current['blob']
            row['equality'] = 'PASS'
        else:
            row['equality'] = 'NOT_IMPORTED_PREFLIGHT_ONLY'
        imported.append(row)
    schema = TOOL + 'descriptor.schema.json'
    must(entry(head, schema)['blob'] == entry(ORIGINAL, schema)['blob'], 'SCHEMA_CHANGED')
    for path in (TOOL + 'legacy_v5.py', TOOL + 'legacy_v5_descriptor.py', TOOL + 'parser.py'):
        must(entry(head, path)['blob'] == entry(A, path)['blob'], 'A_COMPONENT_CHANGED:' + path)
    return {'schema': 'ap04-c2-d-audit-v1', 'stage': stage, 'commit': head,
            'tree': git('rev-parse', head + '^{tree}'),
            'parents': git('show', '-s', '--format=%P', head).split(),
            'objects': objects, 'phases': phases, 'source_blob_provenance': imported,
            'B_is_git_ancestor': False, 'historical_manifest_entries_verified': 22,
            'historical_manifest_sha256': MANIFEST_SHA256,
            'ownership': 'PASS_EVERY_COMMIT_EXACT_PATHS',
            'production_acquisition': 'BLOCKED', 'host': 'HOST_UNVERIFIED',
            'source_key': 'ARC09_DECISION_PENDING', 'source_bytes_real': 'NOT_ACCESSED',
            'independent_review': 'PENDING_DISTINCT_EXECUTOR',
            'python_optimized': bool(sys.flags.optimize)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default=ORIGINAL)
    parser.add_argument('--stage', choices=('preflight', 'composed'), default='preflight')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--junit')
    args = parser.parse_args()
    try:
        must(args.base == ORIGINAL, 'BASE_OVERRIDE_NOT_ALLOWED')
        report = verify(args.stage)
        if args.junit:
            root = ET.parse(args.junit).getroot()
            cases = list(root.iter('testcase'))
            failures = [t for t in cases if t.find('failure') is not None or t.find('error') is not None]
            skipped = [t for t in cases if t.find('skipped') is not None]
            report['tests'] = {'collected': len(cases), 'passed': len(cases)-len(failures)-len(skipped),
                               'failed': len(failures), 'skipped': len(skipped),
                               'skip_reasons': [{'test': t.get('name'), 'reason': t.find('skipped').get('message')} for t in skipped]}
            must(not failures and len(cases)-len(skipped) >= 49, 'TESTS_FAILED_OR_INCOMPLETE')
        out = ROOT / '.test-output/atlas-parity04-f4-c2-d'
        out.mkdir(parents=True, exist_ok=True)
        (out / 'audit.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        print(('' if args.json else 'C2_D_EVIDENCE=') + json.dumps(report, sort_keys=True))
        return 0
    except (AuditFailure, OSError, ValueError, subprocess.SubprocessError, ET.ParseError) as exc:
        print(json.dumps({'status': 'BLOCKED_EXACT', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
