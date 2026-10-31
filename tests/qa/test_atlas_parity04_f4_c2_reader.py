"""Original invented fixtures and counterproofs; unittest checks survive -O."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools.atlas_legacy_presentation.errors import ReaderError
from tools.atlas_legacy_presentation.parser import parse_source, transform
from tools.atlas_legacy_presentation.semantics import validate_descriptor
from tools.atlas_legacy_presentation import reader

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'tools/atlas_legacy_presentation/descriptor.schema.json').read_text(encoding='utf-8'))
NOW = '2026-10-31T03:05:00Z'


def fixture_source():
    names = ['module', 'title', 'big', 'decimal', 'numeric_text', 'null_value', 'empty', 'zero', 'missing', 'boolean', 'array', 'object']
    cells = [{'present': True, 'value': value} for value in ['Módulo inventado', '<img src=x onerror=synthetic()>', '__BIG__', '__DECIMAL__', '0.100', None, '', 0, None, False, '__ARRAY__', '__OBJECT__']]
    cells[8] = {'present': False}
    cells[3].update(unit='1', precision='21')
    requirement = {'kind': 'RF', 'native_id': None, 'admission': 'UNADMITTED_NATIVE_RF', 'admission_evidence_locator': None, 'fields': {'id': None, 'module': 0, 'title': 1, 'description': None, 'acceptance_criteria': None, 'category': None}, 'category_status': 'MISSING'}
    rows = [{'cells': copy.deepcopy(cells), 'requirement': copy.deepcopy(requirement)} for _ in range(28)]
    tables = [{'id': 'T0', 'title': 'RF inventadas', 'domain': 'RF', 'record_id': 'P', 'columns': [{'key': n, 'header': n} for n in names], 'rows': rows}]
    tables += [{'id': 'T'+str(i), 'title': 'Tabela vazia '+str(i), 'record_id': None, 'columns': [], 'rows': []} for i in range(1, 5)]
    return {'format': 'atlas-legacy-synthetic-source', 'version': '0.1.0', 'synthetic': True, 'source_id': 'synthetic-c2-qa', 'snapshot_id': 'synthetic-c2-qa-s1', 'access_policy_id': 'fixture-only-c2', 'scope': 'Dados inteiramente inventados pela QA C2', 'records': [{'id': 'P', 'kind': 'Project', 'label': 'Projeto sintético', 'root': True}, {'id': 'R', 'kind': 'Run', 'label': 'Run isolado'}, {'id': 'D', 'kind': 'Unknown', 'label': 'Colisão A'}, {'id': 'D', 'kind': 'Unknown', 'label': 'Colisão B'}], 'edges': [{'from': None, 'to': 'R', 'kind': 'related'}, {'from': 'D', 'to': 'MISSING', 'kind': 'related'}, {'from': 'R', 'to': 'MISSING', 'kind': 'related'}, {'from': 'R', 'to': 'MISSING', 'kind': 'related'}, {'from': 'R', 'to': {'id': 'P', 'source_id': 'other-source', 'snapshot_id': 'other-snapshot'}, 'kind': 'related'}], 'result_tables': tables, 'product_items': [{'id': 'FILE', 'label': 'File continua File', 'kind': 'File', 'original_type': 'File', 'product_role': 'report', 'binding_id': 'R', 'uri': 'https://example.invalid/never-open'}], 'resource_documents': [], 'extra_scientific_note': {'unobserved': True}}


def raw_source(value=None):
    raw = json.dumps(fixture_source() if value is None else value, ensure_ascii=False, separators=(',', ':'))
    return raw.replace('"__BIG__"', '9007199254740993').replace('"__DECIMAL__"', '0.123456789012345678901').replace('"__ARRAY__"', '[ 1, {"x" : 0.100} ]').replace('"__OBJECT__"', '{ "x" : 9007199254740993 }').encode('utf-8')


def descriptor(data=None):
    raw = raw_source() if data is None else data
    return transform(parse_source(raw), source_id='synthetic-c2-qa', snapshot_id='synthetic-c2-qa-s1', access_policy_id='fixture-only-c2', bytes_sha256=hashlib.sha256(raw).hexdigest(), observed_at='2026-10-31T03:00:00Z', generated_at='2026-10-31T03:01:00Z', expires_at='2026-10-31T03:31:00Z')


class ParserContraproofs(unittest.TestCase):
    def assert_code(self, code, operation):
        with self.assertRaises(ReaderError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)

    def test_schema_is_exact_approved_f2(self):
        contract = (ROOT / 'docs/missions/atlas-parity-04/f2-legacy-contract/EPHEMERAL-PRESENTATION-CONTRACT.md').read_text(encoding='utf-8')
        approved = json.loads(contract.split('~~~json\n'.replace('~', chr(96)), 1)[1].split('\n~~~'.replace('~', chr(96)), 1)[0])
        self.assertEqual(SCHEMA, approved)

    def test_literal_types_and_lexemes_are_not_coerced(self):
        d = descriptor()
        validate_descriptor(d, SCHEMA, now=NOW)
        cells = d['tables'][0]['rows'][0]['cells']
        self.assertEqual((cells[2]['type'], cells[2]['literal'], cells[2]['lexeme']), ('integer', '9007199254740993', '9007199254740993'))
        self.assertEqual(cells[3]['literal'], '0.123456789012345678901')
        self.assertEqual((cells[3]['unit'], cells[3]['precision']), ('1', '21'))
        self.assertEqual((cells[4]['type'], cells[4]['literal'], cells[4]['lexeme']), ('string', '0.100', '"0.100"'))
        self.assertEqual((cells[5]['type'], cells[5]['absence']), ('null', 'NULL'))
        self.assertEqual((cells[6]['type'], cells[6]['literal']), ('string', ''))
        self.assertEqual((cells[7]['type'], cells[7]['literal']), ('integer', '0'))
        self.assertEqual((cells[8]['type'], cells[8]['absence']), ('missing', 'MISSING'))
        self.assertEqual((cells[9]['type'], cells[9]['literal']), ('boolean', 'false'))
        self.assertEqual(cells[10]['lexeme'], '[ 1, {"x" : 0.100} ]')
        self.assertEqual(cells[11]['lexeme'], '{ "x" : 9007199254740993 }')

    def test_28_unadmitted_and_four_unbound_tables_preserved(self):
        d = descriptor()
        self.assertEqual(len(d['tables']), 5)
        self.assertEqual(sum(t['record_binding']['resolution'] != 'RESOLVED' for t in d['tables']), 4)
        rows = d['tables'][0]['rows']
        self.assertEqual(len(rows), 28)
        self.assertEqual([r['ordinal'] for r in rows], list(range(28)))
        self.assertTrue(all(r['identity']['native_id'] is None for r in rows))
        self.assertTrue(all(r['requirement']['admission'] == 'UNADMITTED_NATIVE_RF' and r['requirement']['native_id'] is None for r in rows))
        self.assertTrue(all(r['requirement']['category_status'] == 'MISSING' for r in rows))
        self.assertEqual([len(t['rows']) for t in d['tables']], [28, 0, 0, 0, 0])

    def test_collision_null_unresolved_and_repeat_occurrences(self):
        d = descriptor()
        self.assertEqual([n['identity']['native_id'] for n in d['nodes']].count('D'), 2)
        self.assertEqual(d['relations'][0]['from']['resolution'], 'NULL_ENDPOINT')
        self.assertEqual(d['relations'][1]['from']['resolution'], 'COLLISION')
        self.assertIsNone(d['relations'][1]['from']['target_navigation_id'])
        self.assertEqual(d['relations'][1]['to']['resolution'], 'UNRESOLVED')
        pair = d['relations'][2:4]
        self.assertEqual(pair[0]['repeat_group'], pair[1]['repeat_group'])
        self.assertIsNotNone(pair[0]['repeat_group'])
        self.assertEqual([r['repeat_occurrence'] for r in pair], [1, 2])
        self.assertEqual(d['relations'][4]['to']['resolution'], 'UNRESOLVED')
        self.assertIsNone(d['relations'][4]['to']['target_navigation_id'])

    def test_observed_isolated_run_and_file_retained(self):
        d = descriptor()
        run = next(n for n in d['nodes'] if n['identity']['native_id'] == 'R')
        self.assertEqual((run['kind'], run['entity_status']), ('Run', 'SOURCE_ENTITY'))
        self.assertTrue(run['binding_gap'])
        self.assertEqual(d['assets'][0]['kind'], 'File')
        self.assertFalse(d['assets'][0]['opened'])
        self.assertEqual(d['coverage']['global_archive'], 'UNKNOWN_UPSTREAM')
        self.assertIsNone(d['coverage']['global_total'])
        self.assertIsNone(d['coverage']['global_percentage'])
        self.assertTrue(any(x['source_key_literal'] == 'extra_scientific_note' for x in d['unmapped_fields']))

    def test_hostile_html_javascript_and_uri_are_inert(self):
        html = b'<html><script>throw new Error("SYNTHETIC_EXECUTION_FORBIDDEN")</script><script type="application/json" id="atlas-legacy-synthetic-source">' + raw_source() + b'</script></html>'
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            parsed = parse_source(html, media_type='text/html')
            d = descriptor()
            validate_descriptor(d, SCHEMA, now=NOW)
        self.assertIs(parsed.value['synthetic'], True)

    def test_unknown_format_and_ambiguous_html_refused(self):
        self.assert_code('SOURCE_FORMAT_UNSUPPORTED', lambda: parse_source(b'{"records":[]}'))
        self.assert_code('SOURCE_FORMAT_UNSUPPORTED', lambda: parse_source(b'<script>window.source={}</script>', media_type='text/html'))
        tag = b'<script type="application/json" id="atlas-legacy-synthetic-source">'+raw_source()+b'</script>'
        self.assert_code('SOURCE_FORMAT_UNSUPPORTED', lambda: parse_source(tag+tag, media_type='text/html'))

    def test_duplicate_keys_nonfinite_invalid_utf8_refused(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'\xff', b'{"x":"\\ud800"}']:
            with self.subTest(raw=repr(raw)):
                self.assert_code('SOURCE_JSON_INVALID', lambda raw=raw: parse_source(raw))

    def test_depth_and_column_quotas_refused(self):
        source = fixture_source()
        nested = 0
        for _ in range(25):
            nested = [nested]
        source['extra'] = nested
        self.assert_code('QUOTA_EXCEEDED', lambda: parse_source(raw_source(source)))
        source = fixture_source()
        source['result_tables'][0]['columns'] *= 22
        self.assert_code('QUOTA_EXCEEDED', lambda: descriptor(raw_source(source)))

    def test_multibyte_literal_byte_quota_refused(self):
        source = fixture_source()
        source['result_tables'][0]['rows'][0]['cells'][1]['value'] = 'é' * 32769
        self.assert_code('QUOTA_EXCEEDED', lambda: descriptor(raw_source(source)))

    def test_descriptor_schema_and_semantic_tampering_refused(self):
        d = descriptor()
        d['forbidden'] = True
        self.assert_code('DESCRIPTOR_SCHEMA_INVALID', lambda: validate_descriptor(d, SCHEMA, now=NOW))
        for mutate in [lambda d: d['relations'][0]['to'].update(source_id='other-source'), lambda d: d['relations'][0]['to'].update(snapshot_id='other-snapshot'), lambda d: d['relations'][0]['to'].update(declared_id='WRONG'), lambda d: d['nodes'][1]['identity'].update(navigation_id=d['nodes'][0]['identity']['navigation_id']), lambda d: d['tables'][0]['rows'][0]['cells'][2].update(lexeme='9007199254740992'), lambda d: d['tables'][0]['rows'][0].update(ordinal=99)]:
            d = descriptor()
            mutate(d)
            self.assert_code('DESCRIPTOR_SEMANTICS_INVALID', lambda d=d: validate_descriptor(d, SCHEMA, now=NOW))

    def test_expiration_and_ttl_refused(self):
        d = descriptor()
        self.assert_code('DESCRIPTOR_EXPIRED', lambda: validate_descriptor(d, SCHEMA, now='2026-10-31T04:00:00Z'))
        d['snapshot']['expires_at'] = '2026-10-31T04:01:01Z'
        self.assert_code('DESCRIPTOR_SEMANTICS_INVALID', lambda: validate_descriptor(d, SCHEMA, now=NOW))


class AcquisitionContraproofs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='atlas-parity04-f4-c2-synthetic-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source_dir = self.base / 'invented-source'
        self.source_dir.mkdir()
        self.source = self.source_dir / 'invented.json'
        self.source.write_bytes(raw_source())
        self.scratch = reader.private_scratch(self.base)

    def open_fixture(self, source=None, allowlist=None, scratch=None, **kw):
        return reader.prepare(self.source if source is None else source, [self.source] if allowlist is None else allowlist, self.scratch if scratch is None else scratch, synthetic_fixture=True, **kw)

    def assert_code(self, code, operation):
        with self.assertRaises(ReaderError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)

    def test_default_mode_blocks_before_any_source_read(self):
        with patch.object(reader, '_after_read', side_effect=AssertionError('Source must not be read')):
            self.assert_code('HARD_BUDGET_UNVERIFIED', lambda: reader.prepare(self.source, [self.source], self.scratch))
        args = [sys.executable, '-m', 'tools.atlas_legacy_presentation', '--source', str(self.base/'does-not-exist'), '--allow', str(self.base/'does-not-exist'), '--scratch', str(self.base/'does-not-exist')]
        done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(done.returncode, 2)
        self.assertEqual(json.loads(done.stderr)['code'], 'HARD_BUDGET_UNVERIFIED')

    def test_source_immutable_and_one_derived_file_only(self):
        before = (self.source.read_bytes(), self.source.stat().st_size, self.source.stat().st_mtime_ns)
        result = self.open_fixture()
        self.assertEqual((self.source.read_bytes(), self.source.stat().st_size, self.source.stat().st_mtime_ns), before)
        self.assertEqual(result.parent, self.scratch)
        d = json.loads(result.read_text(encoding='utf-8'))
        self.assertEqual(d['authority'], 'LEGACY_DERIVED')
        self.assertEqual(d['snapshot']['bytes_sha256'], hashlib.sha256(before[0]).hexdigest())
        self.assertEqual(len([p for p in self.scratch.iterdir() if p.is_file()]), 1)
        reader.cleanup_owned(result)
        self.assertFalse(result.exists())
        self.assertTrue(self.source.exists())

    def test_path_not_exactly_allowlisted(self):
        neighbor = self.source_dir / 'neighbor.json'
        neighbor.write_bytes(raw_source())
        self.assert_code('PATH_NOT_ALLOWED', lambda: self.open_fixture(source=neighbor))

    def test_traversal_refused_even_when_resolving_to_allowed_source(self):
        alias = self.source_dir / '..' / self.source_dir.name / self.source.name
        self.assert_code('UNSAFE_PATH', lambda: self.open_fixture(source=alias, allowlist=[alias]))

    def test_allowlist_limit_and_ttl_quota(self):
        self.assert_code('QUOTA_EXCEEDED', lambda: self.open_fixture(allowlist=[self.source] * 4))
        self.assert_code('QUOTA_EXCEEDED', lambda: self.open_fixture(ttl_seconds=3601))
        self.assert_code('QUOTA_EXCEEDED', lambda: self.open_fixture(ttl_seconds=0))

    def test_hardlink_refused(self):
        alias = self.source_dir / 'hardlink.json'
        os.link(self.source, alias)
        self.assert_code('UNSAFE_PATH', lambda: self.open_fixture())

    def test_symlink_leaf_refused(self):
        alias = self.source_dir / 'symbolic.json'
        try:
            alias.symlink_to(self.source)
        except OSError as exc:
            self.skipTest('OS runner cannot create symlink: '+str(getattr(exc, 'winerror', exc.errno)))
        self.assert_code('UNSAFE_PATH', lambda: self.open_fixture(source=alias, allowlist=[alias]))

    def test_symlink_or_reparse_ancestor_refused(self):
        alias = self.base / 'linked-directory'
        if os.name == 'nt':
            made = subprocess.run(['cmd', '/c', 'mklink', '/J', str(alias), str(self.source_dir)], capture_output=True, text=True, timeout=10)
            self.assertEqual(made.returncode, 0, made.stderr)
        else:
            alias.symlink_to(self.source_dir, target_is_directory=True)
        self.assert_code('UNSAFE_PATH', lambda: self.open_fixture(source=alias/self.source.name, allowlist=[alias/self.source.name]))

    def test_source_change_during_read_refused(self):
        def change(path):
            path.write_bytes(path.read_bytes()+b' ')
        with patch.object(reader, '_after_read', side_effect=change):
            self.assert_code('SOURCE_CHANGED', lambda: self.open_fixture())
        self.assertFalse(any(self.scratch.iterdir()))

    def test_source_replacement_during_read_refused(self):
        replacement = self.source_dir / 'replacement.json'
        replacement.write_bytes(self.source.read_bytes())
        with patch.object(reader, '_after_read', side_effect=lambda path: os.replace(replacement, path)):
            self.assert_code('SOURCE_CHANGED', lambda: self.open_fixture())

    def test_mtime_change_during_read_refused(self):
        def change(path):
            st = path.stat()
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1000000000))
        with patch.object(reader, '_after_read', side_effect=change):
            self.assert_code('SOURCE_CHANGED', lambda: self.open_fixture())

    def test_scratch_must_be_separate_from_source(self):
        with self.assertRaises(ReaderError) as caught:
            self.open_fixture(scratch=self.source_dir)
        self.assertIn(caught.exception.code, {'UNSAFE_PATH', 'SCRATCH_UNVERIFIED'})

    def test_cleanup_never_removes_foreign_file(self):
        foreign = self.scratch / 'foreign.json'
        foreign.write_text('invented unrelated file', encoding='utf-8')
        try:
            reader.cleanup_owned(foreign)
        except ReaderError:
            pass
        self.assertEqual(foreign.read_text(encoding='utf-8'), 'invented unrelated file')

    def test_cleanup_refuses_replaced_owned_identity(self):
        result = self.open_fixture()
        foreign = self.scratch / 'foreign.json'
        foreign.write_text('unowned synthetic replacement', encoding='utf-8')
        os.replace(foreign, result)
        try:
            reader.cleanup_owned(result)
        except ReaderError:
            pass
        self.assertEqual(result.read_text(encoding='utf-8'), 'unowned synthetic replacement')

    def test_unc_device_ads_and_glob_refused(self):
        for path in ['//server/share/file.json', r'\\?\C:\secret.json', str(self.source)+':stream', str(self.source)+'*', str(self.source)+'%2fother']:
            with self.subTest(path=path):
                self.assert_code('UNSAFE_PATH', lambda path=path: self.open_fixture(source=Path(path), allowlist=[Path(path)]))


if __name__ == '__main__':
    unittest.main()
