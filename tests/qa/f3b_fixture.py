"""Fixture pública sintética reproduzível; nenhuma leitura de acervo ou rede."""
from __future__ import annotations
import copy
import json
import re
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'docs/missions/atlas-parity-04/f2-legacy-contract/EPHEMERAL-PRESENTATION-CONTRACT.md'
CASES = ROOT / 'tests/fixtures/atlas_parity04_f3b_cases.json'
NOW = int(datetime(2026, 10, 30, 12, 2, tzinfo=timezone.utc).timestamp() * 1000)
TABLE = 'nav:a-table'


def cell(kind, literal, unit=None, precision=None):
    if kind == 'missing':
        return dict(type=kind, literal=None, lexeme=None, unit=None, precision=None, absence='MISSING')
    if kind == 'null':
        return dict(type=kind, literal=None, lexeme='null', unit=None, precision=None, absence='NULL')
    return dict(type=kind, literal=literal,
                lexeme=json.dumps(literal, ensure_ascii=False) if kind == 'string' else literal,
                unit=unit, precision=precision, absence=None)


def identity(native, nav, ordinal, locator):
    return dict(native_id=native, navigation_id=nav, navigation_id_kind='DERIVED_FOR_PRESENTATION',
                occurrence=ordinal, locator=locator)


def null_binding():
    return dict(source_id=None, snapshot_id=None, declared_id=None, target_navigation_id=None,
                resolution='NULL_ENDPOINT', evidence_locator=None)


def fixture():
    blocks = [json.loads(b) for b in re.findall(r'```json\s*\n(.*?)```', CONTRACT.read_text(encoding='utf-8'), re.S)]
    if len(blocks) != 3:
        raise ValueError('Expected frozen schema and two public synthetic examples')
    schema, example_a, example_b = blocks
    cases = json.loads(CASES.read_text(encoding='utf-8'))
    d = copy.deepcopy(example_a)
    d['source']['scope'] = 'Coleção sintética pública F3B: 5 tabelas, 46 linhas, sem replay F1'
    d['source']['original_profile_declared'] = 'RF RNF RES FHIR: rótulos inertes sem conformidade'
    t = d['tables'][0]
    t['title_literal'] = 'RF sintéticas <img src=https://invalid.example/title onerror=globalThis.__f3bPwned=1>'
    row_template = copy.deepcopy(t['rows'][0])
    extras = [('big', 'Inteiro >2^53'), ('dec', 'Decimal exato'), ('bool', 'Booleano'),
              ('numeric_text', 'String numérica'), ('null', 'JSON null'), ('empty', 'Vazio'),
              ('zero', 'Zero'), ('array', 'Array literal'), ('object', 'Objeto literal'),
              ('uri', 'URI inerte'), ('hostile', 'Payload literal'), ('long', 'Célula extensa'),
              ('header', '=HYPERLINK("https://invalid.example/header","x")')]
    for ordinal, (key, header) in enumerate(extras, 6):
        t['columns'].append(dict(ordinal=ordinal, native_key=key, header_literal=header))
    t['rows'] = []
    for i, offset in enumerate(cases['integer_offsets']):
        r = copy.deepcopy(row_template)
        nav = 'nav:a-row' if i == 0 else f'nav:a-row-{i}'
        native = 'ROW-SYN-COLLISION' if i >= 14 else f'ROW-SYN-{i}'
        r['identity'] = identity(native, nav, 1 if i == 15 else 0, f'/tables/0/rows/{i}')
        r['ordinal'] = i
        r['cells'][0] = cell('string', f'RF-SYN-{i+1:03}')
        r['requirement']['native_id'] = f'RF-SYN-{i+1:03}'
        r['requirement']['admission_evidence_locator'] = f'/tables/0/rows/{i}/id'
        if i % 5 == 1:
            r['cells'][5] = cell('null', None)
        elif i % 5 == 2:
            r['cells'][5] = cell('string', '')
            r['requirement']['category_status'] = 'PRESENT'
        elif i % 5 == 3:
            r['cells'][5] = cell('integer', '0')
            r['requirement']['category_status'] = 'PRESENT'
        elif i % 5 == 4:
            r['cells'][5] = cell('string', 'UNKNOWN')
            r['requirement']['category_status'] = 'UNKNOWN'
        r['cells'].extend([
            cell('integer', str(9007199254740993 + offset), '1'),
            cell('decimal', cases['decimals'][i], '1', '21'),
            cell('boolean', 'false' if i % 2 == 0 else 'true'),
            cell('string', '0.100'), cell('null', None), cell('string', ''), cell('integer', '0'),
            cell('array', '[1,"<svg onload=alert(1)>",null]'),
            cell('object', '{"__proto__":{"polluted":true},"html":"<script>x()</script>"}'),
            cell('string', cases['uris'][i % len(cases['uris'])]),
            cell('string', cases['hostiles'][i]), cell('string', cases['long_cell'] * 60000),
            cell('string', 'Unicode: ç é 😀; delimitador, aspas "')])
        t['rows'].append(r)
    # Original A binding relation still targets nav:a-row; preserve native ID used by it.
    t['rows'][0]['identity']['native_id'] = 'ROW-SYN-A'
    for idx, kind in ((1, 'RNF'), (2, 'RES')):
        derived = copy.deepcopy(t)
        derived['identity'] = identity(f'TABLE-SYN-{kind}', f'nav:{kind.lower()}-table', 0, f'/tables/{idx}')
        derived['title_literal'] = f'{kind} explicitamente declarada: fixture sintética'
        derived['domain'] = kind
        derived['record_binding'] = dict(source_id='synthetic-a', snapshot_id='fixture-a-1',
            declared_id=f'RECORD-MISSING-{kind}', target_navigation_id=None,
            resolution='UNRESOLVED', evidence_locator=f'/tables/{idx}/record_id')
        row = copy.deepcopy(derived['rows'][0])
        row['identity'] = identity(f'ROW-SYN-{kind}', f'nav:{kind.lower()}-row', 0, f'/tables/{idx}/rows/0')
        row['ordinal'] = 0
        row['cells'][0] = cell('string', f'{kind}-SYN-001')
        row['requirement'].update(kind=kind, native_id=f'{kind}-SYN-001', admission='NOT_EVALUATED',
                                  admission_evidence_locator=None)
        derived['rows'] = [row]
        d['tables'].append(derived)
    unadmitted = copy.deepcopy(example_b['tables'][0])
    unadmitted['rows'] = []
    unadmitted['record_binding']['source_id'] = 'synthetic-a'
    unadmitted['record_binding']['snapshot_id'] = 'fixture-a-1'
    for i in range(28):
        r = copy.deepcopy(example_b['tables'][0]['rows'][i % 2])
        r['identity'] = identity(None, f'nav:b-row-{i}', i, f'/tables/3/rows/{i}')
        r['ordinal'] = i
        unadmitted['rows'].append(r)
    unadmitted['identity']['locator'] = '/tables/3'
    d['tables'].append(unadmitted)
    d['tables'].append(dict(identity=identity(None, 'nav:unknown-table', 0, '/tables/4'),
        title_literal='RF RNF RES FHIR.csv: File não é produto; domínio não inferido',
        domain='UNKNOWN', domain_origin='UNKNOWN', record_binding=null_binding(),
        columns=[dict(ordinal=0, native_key='RF_filename', header_literal='RF RNF RES')], rows=[]))
    d['assets'][0].update(label_literal='RF FHIR.json', media_type_literal='application/fhir+json',
                           uri_literal='javascript:globalThis.__f3bPwned=1')
    d['unmapped_fields'] = [dict(owner_navigation_id=TABLE, locator='/tables/0/note',
        source_key_literal='note', value=cell('string', '<script>globalThis.__f3bPwned=1</script>'))]
    counts = {'presentation_node_occurrences': 3, 'source_nodes': 2, 'external_reference_stubs': 1,
              'tables': 5, 'rows': 46, 'relations': 1, 'assets': 1}
    for count in d['coverage']['counts']:
        count.update(selected=counts[count['unit']], loaded=counts[count['unit']], visible=None,
                     unknown_reason='Fixture sintética; UI ainda não executada; global desconhecido.')
    d['gaps'] = [dict(code=code, scope='Fixture pública F3B', count=n, unit=unit, note=note)
        for code,n,unit,note in [
            ('UNRESOLVED_RECORD_ID', 4, 'tables', 'Quatro tabelas não vinculadas; nenhum record inventado.'),
            ('UNADMITTED_NATIVE_RF', 28, 'rows', '28 ocorrências inventadas; native_id null; não é replay F1.'),
            ('RUN_EXTERNAL_ISOLATED', 1, 'declared external Run stubs', 'binding_gap permanece.'),
            ('DECLARED_COLLISION', 1, 'declared identity groups', 'Duas ocorrências retidas sem resolução automática.'),
            ('UNKNOWN_UPSTREAM', None, 'global population', 'Sem denominador global ou soma de snapshots.')]]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(d)
    if len(d['tables']) != 5 or sum(len(x['rows']) for x in d['tables']) != 46:
        raise ValueError('Synthetic fixture counts inconsistent')
    validate_synthetic(d)
    # PASS identifies this fixture construction+formal validation, never source comparison/science.
    d['validation']['descriptor_schema'] = 'PASS'
    d['validation']['descriptor_semantics'] = 'PASS'
    validator.validate(d)
    return d, schema, cases


def validate_synthetic(d):
    def require(ok, why):
        if not ok:
            raise ValueError(why)
    tables = d['tables']
    objects = d['nodes'] + tables + [r for t in tables for r in t['rows']] + d['relations'] + d['assets']
    by_nav = {x['identity']['navigation_id']: x for x in objects}
    require(len(by_nav) == len(objects), 'duplicate navigation ID')
    native = Counter(x['identity']['native_id'] for x in objects if x['identity']['native_id'] is not None)
    require(all(x['identity']['native_id'] != x['identity']['navigation_id'] for x in objects), 'navigation promoted')
    def ref(r):
        kind = r['resolution']
        target = by_nav.get(r['target_navigation_id'])
        if kind == 'NULL_ENDPOINT':
            require(r['declared_id'] is None and r['target_navigation_id'] is None, 'invalid null binding')
        elif kind in ('UNRESOLVED', 'COLLISION'):
            require(r['target_navigation_id'] is None, 'ambiguous reference target chosen')
        elif kind == 'RESOLVED':
            require(target is not None and target.get('entity_status') != 'DECLARED_EXTERNAL_REFERENCE', 'resolved missing/stub')
            require(r['source_id'] == d['source']['source_id'] and r['snapshot_id'] == d['snapshot']['snapshot_id'], 'foreign resolution')
            require(target['identity']['native_id'] == r['declared_id'] and native[r['declared_id']] == 1, 'resolved native mismatch/collision')
        elif r['target_navigation_id'] is not None:
            require(target is not None and target.get('entity_status') == 'DECLARED_EXTERNAL_REFERENCE', 'external target is not stub')
    def walk(v):
        if isinstance(v, dict):
            if {'resolution', 'target_navigation_id', 'declared_id'} <= v.keys():
                ref(v)
            for value in v.values():
                walk(value)
        elif isinstance(v, list):
            for value in v:
                walk(value)
    walk(d)
    for t in tables:
        require([c['ordinal'] for c in t['columns']] == list(range(len(t['columns']))), 'column ordinal')
        require([r['ordinal'] for r in t['rows']] == list(range(len(t['rows']))), 'row ordinal')
        for r in t['rows']:
            require(len(r['cells']) == len(t['columns']), 'row width')
            q = r['requirement']
            if q:
                require(all(i is None or 0 <= i < len(r['cells']) for i in q['fields'].values()), 'requirement index')
                if q['admission'] == 'UNADMITTED_NATIVE_RF':
                    require(q['native_id'] is None and r['identity']['native_id'] is None, 'unadmitted native ID')
                if q['admission'] == 'ADMITTED_NATIVE_RF':
                    i = q['fields']['id']
                    require(i is not None and r['cells'][i]['literal'] == q['native_id'], 'admitted ID mismatch')
                i = q['fields']['category']
                if q['category_status'] == 'MISSING':
                    require(i is None or r['cells'][i]['type'] in ('missing', 'null'), 'missing category mismatch')
            for c in r['cells']:
                kind = c['type']
                if kind in ('missing', 'null'):
                    require(c['literal'] is None and c['absence'] == ('MISSING' if kind == 'missing' else 'NULL'), 'absence')
                    continue
                require(c['absence'] is None, 'present absence')
                if kind == 'string':
                    require(json.loads(c['lexeme']) == c['literal'], 'string lexeme')
                elif kind in ('integer', 'decimal'):
                    require(c['lexeme'] == c['literal'], 'numeric lexical loss')
                elif kind == 'boolean':
                    require(c['lexeme'] == c['literal'] and c['literal'] in ('true', 'false'), 'boolean')
                else:
                    parsed = json.loads(c['literal'])
                    require(isinstance(parsed, list if kind == 'array' else dict), 'structured literal type')
    expected = {'presentation_node_occurrences': len(d['nodes']),
                'source_nodes': sum(n['entity_status'] == 'SOURCE_ENTITY' for n in d['nodes']),
                'external_reference_stubs': sum(n['entity_status'] == 'DECLARED_EXTERNAL_REFERENCE' for n in d['nodes']),
                'tables': len(tables), 'rows': sum(len(t['rows']) for t in tables),
                'relations': len(d['relations']), 'assets': len(d['assets'])}
    require(all(c['loaded'] == expected[c['unit']] for c in d['coverage']['counts']), 'coverage count')
    require(sum(t['record_binding']['resolution'] != 'RESOLVED' for t in tables) == 4, 'unbound count')
    require(sum(r['requirement'] is not None and r['requirement']['admission'] == 'UNADMITTED_NATIVE_RF' for t in tables for r in t['rows']) == 28, 'unadmitted count')
    times = [datetime.fromisoformat(d['snapshot'][k].replace('Z', '+00:00')) for k in ('observed_at','generated_at','expires_at')]
    require(times[0] <= times[1] < times[2] and (times[2]-times[1]).total_seconds() <= 3600, 'TTL')
    require(d['coverage']['global_total'] is None and d['coverage']['global_percentage'] is None, 'invented global')
