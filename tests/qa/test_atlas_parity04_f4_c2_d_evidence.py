"""Current-byte successor manifest checks; historical manifests stay immutable."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.qa import atlas_parity04_f4_c2_d_evidence as audit

MANIFEST = audit.DOC + 'f4-c2-composition/MANIFEST.sha256'


def verify_manifest(raw: bytes, inventory: list[dict]) -> None:
    parsed = {}
    for line in raw.decode('utf-8').splitlines():
        match = re.fullmatch(r'([a-f0-9]{64})  ([^\r\n]+)', line)
        audit.must(match is not None, 'SUCCESSOR_MANIFEST_SYNTAX')
        digest, path = match.groups()
        audit.must(path not in parsed and not path.startswith('/') and
                   '\\' not in path and '..' not in path.split('/'),
                   'SUCCESSOR_MANIFEST_PATH')
        parsed[path] = digest
    expected = {row['path']: row['sha256'] for row in inventory}
    audit.must(len(expected) == len(inventory) and set(parsed) == set(expected),
               'SUCCESSOR_MANIFEST_COVERAGE')
    audit.must(parsed == expected, 'SUCCESSOR_MANIFEST_DIGEST')


def inventory_current() -> list[dict]:
    rows = []
    paths = audit.git('diff', '--name-only', audit.F2, 'HEAD').splitlines()
    for path in sorted(paths):
        if path == MANIFEST:
            continue
        identity = audit.entry('HEAD', path)
        raw = audit.git('show', 'HEAD:' + path, raw=True)
        rows.append({**identity, 'size': len(raw),
                     'sha256': hashlib.sha256(raw).hexdigest()})
    audit.must(bool(rows), 'EMPTY_SUCCESSOR_INVENTORY')
    return rows


class SuccessorManifestCounterproofs(unittest.TestCase):
    def setUp(self):
        self.rows = [{'path': 'tools/invented.py', 'sha256': 'a' * 64}]
        self.valid = ('a' * 64 + '  tools/invented.py\n').encode('ascii')

    def test_exact_inventory_is_accepted(self):
        verify_manifest(self.valid, self.rows)

    def test_missing_extra_and_duplicate_entries_are_rejected(self):
        for raw in (b'', self.valid + b'b' * 64 + b'  extra.py\n', self.valid * 2):
            with self.assertRaises(audit.AuditFailure):
                verify_manifest(raw, self.rows)

    def test_stale_digest_is_rejected(self):
        with self.assertRaisesRegex(audit.AuditFailure, 'DIGEST'):
            verify_manifest(self.valid.replace(b'a', b'c', 1), self.rows)

    def test_unsafe_paths_and_bad_syntax_are_rejected(self):
        for path in ('../x.py', '/x.py', 'tools\\x.py'):
            with self.assertRaises(audit.AuditFailure):
                verify_manifest(('a' * 64 + '  ' + path + '\n').encode(), self.rows)
        with self.assertRaises(audit.AuditFailure):
            verify_manifest(b'not-a-digest  tools/invented.py\n', self.rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--inventory-only', action='store_true')
    mode.add_argument('--require-manifest', action='store_true')
    args = parser.parse_args()
    try:
        head = audit.git('rev-parse', 'HEAD')
        inventory = inventory_current()
        output = ROOT / '.test-output/atlas-parity04-f4-c2-d'
        output.mkdir(parents=True, exist_ok=True)
        report = {'commit': head, 'tree': audit.git('rev-parse', 'HEAD^{tree}'),
                  'scope': 'all_changed_paths_F2_to_HEAD_except_manifest_itself',
                  'base': audit.F2, 'inventory': inventory,
                  'production': 'BLOCKED', 'host': 'HOST_UNVERIFIED'}
        exists = bool(audit.git('ls-tree', 'HEAD', '--', MANIFEST))
        if exists:
            raw = audit.git('show', 'HEAD:' + MANIFEST, raw=True)
            verify_manifest(raw, inventory)
            report['manifest'] = {'status': 'PASS', 'entries': len(inventory),
                                  'sha256': hashlib.sha256(raw).hexdigest()}
        else:
            audit.must(args.inventory_only, 'SUCCESSOR_MANIFEST_MISSING')
            report['manifest'] = {'status': 'NOT_PUBLISHED_TECHNICAL_INVENTORY_ONLY'}
        observed = json.loads((output / 'audit.json').read_text(encoding='utf-8'))
        native = json.loads((output / 'b-observed.json').read_text(encoding='utf-8'))
        wheels = json.loads((ROOT / '.test-output/atlas-parity04-f4-c2/independence.json').read_text(encoding='utf-8'))
        audit.must(observed['commit'] == native['tested_commit'] == wheels['commit'] == head,
                   'RECEIPTS_NOT_CURRENT_HEAD')
        audit.must(native['gate_exit_code'] == 0 and native['python_optimize'] == 0,
                   'NATIVE_TEST_GATE_OR_DRIVER_OPTIMIZATION')
        audit.must(wheels['status'] == 'PASS' and all(v == 'PASS' for v in wheels['checks'].values()),
                   'WHEEL_INDEPENDENCE_NOT_PASS')
        audit.must(observed.get('tests', {}).get('failed') == 0, 'CURRENT_JUNIT_NOT_PASS')
        report['current_receipts'] = {'same_sha': True, 'native_gate': 'PASS',
                                      'native_test_driver_optimize': 0,
                                      'wheel_independence': 'PASS'}
        (output / 'inventory.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        print(json.dumps({'status': 'PASS_TECHNICAL_INVENTORY' if args.inventory_only else 'PASS_CURRENT_MANIFEST',
                          'commit': head, 'entries': len(inventory), 'manifest': report['manifest']}))
        return 0
    except (audit.AuditFailure, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'status': 'BLOCKED_EXACT', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
