"""Inert parser for the original, public synthetic qualification format only."""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
import re
import uuid
from .errors import ReaderError

SOURCE_FORMAT = 'atlas-legacy-synthetic-source'
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_DESCRIPTOR_BYTES = 32 * 1024 * 1024
MISSING = object()


def fail(code='SOURCE_STRUCTURE_INVALID'):
    raise ReaderError(code)


def pointer(base, key):
    return base + '/' + str(key).replace('~', '~0').replace('/', '~1')


@dataclass
class ParsedSource:
    value: dict
    lexemes: dict


class _Embedded(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts = []
        self.count = 0
        self.closed = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and any(k == 'id' and v == SOURCE_FORMAT for k, v in attrs):
            if len(attrs) != 2 or dict(attrs) != {'type': 'application/json', 'id': SOURCE_FORMAT}:
                fail('SOURCE_FORMAT_UNSUPPORTED')
            self.count += 1
            self.active = True

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            self.closed += 1
            self.active = False


def parse_source(data: bytes, *, media_type='application/json') -> ParsedSource:
    if type(data) is not bytes:
        fail('SOURCE_JSON_INVALID')
    if len(data) > MAX_SOURCE_BYTES:
        fail('QUOTA_EXCEEDED')
    try:
        text = data.decode('utf-8', errors='strict')
    except UnicodeError:
        fail('SOURCE_JSON_INVALID')
    if media_type == 'text/html':
        html = _Embedded()
        html.feed(text)
        html.close()
        if html.count != 1 or html.closed != 1 or html.active:
            fail('SOURCE_FORMAT_UNSUPPORTED')
        text = ''.join(html.parts)
    elif media_type not in ('application/json', 'application/ld+json'):
        fail('SOURCE_FORMAT_UNSUPPORTED')
    lexemes = {}
    pos = 0
    decoder = json.JSONDecoder()
    number = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')

    def white():
        nonlocal pos
        while pos < len(text) and text[pos] in ' \t\r\n':
            pos += 1

    def read(path, depth):
        nonlocal pos
        if depth > 20:
            fail('QUOTA_EXCEEDED')
        white()
        start = pos
        if pos >= len(text):
            fail('SOURCE_JSON_INVALID')
        ch = text[pos]
        if ch == '{':
            pos += 1
            value = {}
            white()
            if pos < len(text) and text[pos] == '}':
                pos += 1
            else:
                while True:
                    white()
                    if pos >= len(text) or text[pos] != '"':
                        fail('SOURCE_JSON_INVALID')
                    key, pos = decoder.raw_decode(text, pos)
                    key.encode('utf-8', errors='strict')
                    if key in value:
                        fail('SOURCE_JSON_INVALID')
                    white()
                    if pos >= len(text) or text[pos] != ':':
                        fail('SOURCE_JSON_INVALID')
                    pos += 1
                    value[key] = read(pointer(path, key), depth + 1)
                    white()
                    if pos >= len(text):
                        fail('SOURCE_JSON_INVALID')
                    delimiter = text[pos]
                    pos += 1
                    if delimiter == '}':
                        break
                    if delimiter != ',':
                        fail('SOURCE_JSON_INVALID')
        elif ch == '[':
            pos += 1
            value = []
            white()
            if pos < len(text) and text[pos] == ']':
                pos += 1
            else:
                while True:
                    value.append(read(pointer(path, len(value)), depth + 1))
                    white()
                    if pos >= len(text):
                        fail('SOURCE_JSON_INVALID')
                    delimiter = text[pos]
                    pos += 1
                    if delimiter == ']':
                        break
                    if delimiter != ',':
                        fail('SOURCE_JSON_INVALID')
        elif ch == '"':
            value, pos = decoder.raw_decode(text, pos)
            if len(value.encode('utf-8', errors='strict')) > 65536:
                fail('QUOTA_EXCEEDED')
        else:
            match = number.match(text, pos)
            if match:
                raw = match.group()
                if len(raw) > 65536:
                    fail('QUOTA_EXCEEDED')
                value = Decimal(raw) if any(c in raw for c in '.eE') else int(raw)
                pos = match.end()
            else:
                value, pos = decoder.raw_decode(text, pos)
                if value is not None and type(value) is not bool:
                    fail('SOURCE_JSON_INVALID')
        lexemes[path] = text[start:pos]
        return value

    try:
        result = read('', 0)
        white()
        if pos != len(text):
            fail('SOURCE_JSON_INVALID')
    except (ValueError, UnicodeError, RecursionError, InvalidOperation):
        fail('SOURCE_JSON_INVALID')
    if not isinstance(result, dict) or result.get('format') != SOURCE_FORMAT or result.get('version') != '0.1.0' or result.get('synthetic') is not True:
        fail('SOURCE_FORMAT_UNSUPPORTED')
    return ParsedSource(result, lexemes)


def _cell(parsed, path, value=MISSING, *, unit=None, precision=None):
    if value is MISSING:
        return dict(type='missing', literal=None, lexeme=None, unit=unit, precision=precision, absence='MISSING')
    raw = parsed.lexemes[path]
    if value is None:
        kind, literal, absence = 'null', None, 'NULL'
    elif type(value) is bool:
        kind, literal, absence = 'boolean', raw, None
    elif type(value) is int:
        kind, literal, absence = 'integer', raw, None
    elif isinstance(value, Decimal):
        kind, literal, absence = 'decimal', raw, None
    elif isinstance(value, str):
        kind, literal, absence = 'string', value, None
    elif isinstance(value, list):
        kind, literal, absence = 'array', raw, None
    elif isinstance(value, dict):
        kind, literal, absence = 'object', raw, None
    else:
        fail()
    if (literal is not None and len(literal.encode('utf-8')) > 65536) or len(raw.encode('utf-8')) > 131072:
        fail('QUOTA_EXCEEDED')
    return dict(type=kind, literal=literal, lexeme=raw, unit=unit, precision=precision, absence=absence)


def transform(parsed, *, source_id, snapshot_id, access_policy_id, bytes_sha256, observed_at, generated_at, expires_at):
    src = parsed.value
    for key, expected in [('source_id', source_id), ('snapshot_id', snapshot_id), ('access_policy_id', access_policy_id)]:
        if not isinstance(expected, str) or not expected or src.get(key) != expected:
            fail('SOURCE_IDENTITY_MISMATCH')
    required = ['records', 'edges', 'result_tables', 'product_items', 'resource_documents']
    if any(not isinstance(src.get(key), list) for key in required) or not isinstance(src.get('scope'), str):
        fail()
    if len(src['records']) > 10000 or len(src['edges']) > 100000 or len(src['result_tables']) > 128 or len(src['product_items']) + len(src['resource_documents']) > 10000:
        fail('QUOTA_EXCEEDED')
    total_rows = 0
    for item in src['result_tables']:
        if not isinstance(item, dict) or not isinstance(item.get('columns'), list) or not isinstance(item.get('rows'), list):
            fail()
        if len(item['columns']) > 256:
            fail('QUOTA_EXCEEDED')
        total_rows += len(item['rows'])
    if total_rows > 100000:
        fail('QUOTA_EXCEEDED')
    session = uuid.uuid4().hex
    occurrence = Counter()
    objects = []
    unmapped = []
    pending = []

    def identity(item, path):
        if not isinstance(item, dict):
            fail()
        native = item.get('id')
        if native is not None and (not isinstance(native, str) or not native):
            fail()
        ordinal = occurrence[native] if native is not None else 0
        if native is not None:
            occurrence[native] += 1
        nav = f'nav:{session}:{len(objects)}'
        result = dict(native_id=native, navigation_id=nav, navigation_id_kind='DERIVED_FOR_PRESENTATION', occurrence=ordinal, locator=path)
        objects.append(result)
        return result

    def preserve(item, path, owner, structural=(), expected=()):
        for key, value in item.items():
            if key not in structural:
                locator = pointer(path, key)
                unmapped.append(dict(owner_navigation_id=owner, locator=locator, source_key_literal=key, value=_cell(parsed, locator, value)))

        for key in expected:
            if key not in item:
                unmapped.append(dict(owner_navigation_id=owner, locator=pointer(path, key), source_key_literal=key, value=_cell(parsed, pointer(path, key), MISSING)))

    nodes, tables, relations, assets = [], [], [], []
    for i, item in enumerate(src['records']):
        path = f'/records/{i}'
        ident = identity(item, path)
        kind = item.get('kind', 'Unknown')
        if not isinstance(item.get('label'), str):
            fail()
        node = dict(identity=ident, kind=kind, original_type=item.get('original_type', item.get('kind')), entity_status='SOURCE_ENTITY', label_literal=item['label'], family_literal=item.get('family'), parent_key_literal=(item.get('parent_id', {}).get('id') if isinstance(item.get('parent_id'), dict) else item.get('parent_id')), parent=None, tree_state='PARENT_UNKNOWN', external_reference=None, binding_gap=True)
        nodes.append(node)
        pending.append((node, item, path))
        preserve(item, path, ident['navigation_id'], expected=('id', 'kind', 'original_type', 'family', 'parent_id', 'root'))
    for i, item in enumerate(src['result_tables']):
        path = f'/result_tables/{i}'
        ident = identity(item, path)
        if not isinstance(item.get('title'), str):
            fail()
        columns = []
        for j, col in enumerate(item['columns']):
            if not isinstance(col, dict) or set(col) != {'key', 'header'}:
                fail()
            columns.append(dict(ordinal=j, native_key=col['key'], header_literal=col['header']))
            preserve(col, f'{path}/columns/{j}', ident['navigation_id'])
        rows = []
        for j, row in enumerate(item['rows']):
            rp = f'{path}/rows/{j}'
            rid = identity(row, rp)
            if not isinstance(row.get('cells'), list) or len(row['cells']) != len(columns):
                fail()
            cells = []
            for k, cell in enumerate(row['cells']):
                if not isinstance(cell, dict) or type(cell.get('present')) is not bool:
                    fail()
                cp = f'{rp}/cells/{k}'
                expected_keys = {'present', 'value', 'unit', 'precision'} if cell['present'] else {'present'}
                if set(cell) - expected_keys or (cell['present'] and 'value' not in cell):
                    fail()
                cells.append(_cell(parsed, cp + '/value', cell.get('value') if cell['present'] else MISSING, unit=cell.get('unit'), precision=cell.get('precision')))
                preserve(cell, cp, rid['navigation_id'], ('value',), expected=('unit', 'precision'))
            if row.get('requirement') is not None and not isinstance(row['requirement'], dict):
                fail()
            rr = dict(identity=rid, ordinal=j, cells=cells, requirement=row.get('requirement'), run_binding=None, binding_gap=True)
            rows.append(rr)
            pending.append((rr, row, rp))
            preserve(row, rp, rid['navigation_id'], ('cells', 'requirement'), expected=('id', 'run_id', 'requirement'))
            if 'requirement' in row:
                # Preserve raw requirement declaration, including lexical form.
                preserve({'requirement': row['requirement']}, rp, rid['navigation_id'])
        table = dict(identity=ident, title_literal=item['title'], domain=item.get('domain', 'UNKNOWN'), domain_origin='DECLARED' if 'domain' in item and item['domain'] != 'UNKNOWN' else 'UNKNOWN', record_binding=None, columns=columns, rows=rows)
        tables.append(table)
        pending.append((table, item, path))
        preserve(item, path, ident['navigation_id'], ('columns', 'rows'), expected=('id', 'domain', 'record_id'))
    for group in ('product_items', 'resource_documents'):
        for i, item in enumerate(src[group]):
            path = f'/{group}/{i}'
            ident = identity(item, path)
            if not isinstance(item.get('label'), str):
                fail()
            asset = dict(identity=ident, kind=item.get('kind', 'Unknown'), original_type=item.get('original_type', item.get('kind')), label_literal=item['label'], declared_product_role=item.get('product_role'), declared_binding=None, media_type_literal=item.get('media_type'), uri_literal=item.get('uri'), availability='DECLARED_ONLY', opened=False)
            assets.append(asset)
            pending.append((asset, item, path))
            preserve(item, path, ident['navigation_id'], expected=('id', 'kind', 'original_type', 'product_role', 'binding_id', 'media_type', 'uri'))
    index = defaultdict(list)
    for item in nodes + tables + [r for t in tables for r in t['rows']] + assets:
        native = item['identity']['native_id']
        if native is not None:
            index[native].append(item['identity']['navigation_id'])

    def reference(value, path):
        source, snapshot = source_id, snapshot_id
        if value is MISSING:
            return dict(source_id=source, snapshot_id=snapshot, declared_id=None, target_navigation_id=None, resolution='UNRESOLVED', evidence_locator=None)
        if isinstance(value, dict):
            if set(value) != {'source_id', 'snapshot_id', 'id'}:
                fail()
            source, snapshot, value = value['source_id'], value['snapshot_id'], value['id']
            if any(context is not None and not isinstance(context, str) for context in (source, snapshot)):
                fail()
        if value is not None and (not isinstance(value, str) or not value):
            fail()
        candidates = index[value] if value is not None and source == source_id and snapshot == snapshot_id else []
        status = 'NULL_ENDPOINT' if value is None else 'RESOLVED' if len(candidates) == 1 else 'COLLISION' if len(candidates) > 1 else 'UNRESOLVED'
        return dict(source_id=source, snapshot_id=snapshot, declared_id=value, target_navigation_id=candidates[0] if status == 'RESOLVED' else None, resolution=status, evidence_locator=path)

    for target, item, path in pending:
        if 'parent' in target:
            parent = reference(item.get('parent_id', MISSING), path + '/parent_id')
            target['parent'] = parent
            if item.get('root') is True:
                if 'parent_id' in item and item['parent_id'] is not None:
                    fail()
                target['tree_state'] = 'ROOT_DECLARED'
                target['binding_gap'] = False
            elif parent['resolution'] == 'RESOLVED':
                target['tree_state'] = 'PARENT_RESOLVED'
                target['binding_gap'] = False
            elif target['kind'] == 'Run':
                target['tree_state'] = 'RUN_EXTERNAL_ISOLATED'
            elif item.get('parent_id', MISSING) is not MISSING:
                target['tree_state'] = 'ORPHAN'
        elif 'record_binding' in target:
            target['record_binding'] = reference(item.get('record_id', MISSING), path + '/record_id')
        elif 'run_binding' in target:
            target['run_binding'] = reference(item.get('run_id', MISSING), path + '/run_id')
            target['binding_gap'] = target['run_binding']['resolution'] != 'RESOLVED'
        else:
            target['declared_binding'] = reference(item.get('binding_id', MISSING), path + '/binding_id')
    # Functional parent graph: retain cycles and mark every cyclic occurrence.
    by_nav = {node['identity']['navigation_id']: node for node in nodes}
    done, cycle_nodes = set(), set()
    for start in by_nav:
        chain, positions, cursor = [], {}, start
        while cursor in by_nav and cursor not in done:
            if cursor in positions:
                cycle_nodes.update(chain[positions[cursor]:])
                break
            positions[cursor] = len(chain)
            chain.append(cursor)
            parent = by_nav[cursor]['parent']
            cursor = parent['target_navigation_id'] if parent['resolution'] == 'RESOLVED' else None
        done.update(chain)
    for nav in cycle_nodes:
        by_nav[nav]['binding_gap'] = True
    repeats = Counter()
    repeat_keys = []
    for item in src['edges']:
        if not isinstance(item, dict):
            fail()
        # Include explicit semantic/direction/context fields in repeat identity.
        # Reject shapes before computing signatures; no Decimal/invalid coercion.
        for field in ('kind', 'semantics', 'direction'):
            if item.get(field) is not None and not isinstance(item[field], str):
                fail()
        for field in ('from', 'to'):
            value = item.get(field)
            if value is not None and not isinstance(value, (str, dict)):
                fail()
        reference(item.get('from', MISSING), '')
        reference(item.get('to', MISSING), '')
        key = json.dumps([(field in item, item.get(field)) for field in ('from', 'to', 'kind', 'semantics', 'direction')], sort_keys=True, ensure_ascii=True)
        repeat_keys.append(key)
        repeats[key] += 1
    seen = Counter()
    groups = {key: f'repeat:{i}' for i, key in enumerate(repeats) if repeats[key] > 1}
    for i, item in enumerate(src['edges']):
        path = f'/edges/{i}'
        ident = identity(item, path)
        left = reference(item.get('from', MISSING), path + '/from')
        right = reference(item.get('to', MISSING), path + '/to')
        key = repeat_keys[i]
        seen[key] += 1
        issues = sorted({r['resolution'] for r in (left, right) if r['resolution'] != 'RESOLVED'})
        if key in groups:
            issues.append('REPEATED_TRIPLE')
        relations.append(dict(identity=ident, kind_literal=item.get('kind'), semantics=item.get('semantics', 'UNKNOWN'), direction=item.get('direction', 'UNKNOWN'), **{'from': left, 'to': right}, evidence_locator=path, issues=issues, repeat_group=groups.get(key), repeat_occurrence=seen[key], binding_gap=left['resolution'] != 'RESOLVED' or right['resolution'] != 'RESOLVED'))
        preserve(item, path, ident['navigation_id'])
    preserve(src, '', None, tuple(required))
    counts = {'presentation_node_occurrences': len(nodes), 'source_nodes': len(nodes), 'external_reference_stubs': 0, 'tables': len(tables), 'rows': sum(len(t['rows']) for t in tables), 'relations': len(relations), 'assets': len(assets)}
    gap_counts = Counter()
    for node in nodes:
        if node['binding_gap']:
            gap_counts[node['tree_state']] += 1
    for table in tables:
        if table['record_binding']['resolution'] != 'RESOLVED':
            gap_counts['UNRESOLVED_RECORD_ID'] += 1
        for row in table['rows']:
            if row['requirement'] and row['requirement'].get('admission') == 'UNADMITTED_NATIVE_RF':
                gap_counts['UNADMITTED_NATIVE_RF'] += 1
    gap_counts['TREE_CYCLE'] = len(cycle_nodes)
    gap_counts['COLLISION'] = sum(len(v) > 1 for v in index.values())
    gaps = [dict(code=code, scope='selected synthetic payload', count=count, unit='occurrences', note='Preserved without inferred binding or scientific approval.') for code, count in gap_counts.items() if count]
    gaps.append(dict(code='RNF_RES_UNKNOWN', scope='upstream populations', count=None, unit='domain populations', note='No global denominator or upstream completeness assertion.'))
    return dict(format='atlas-legacy-presentation', version='0.2.0', authority='LEGACY_DERIVED', synthetic=True,
        source=dict(source_id=source_id, scope=src['scope'], original_format=SOURCE_FORMAT, original_profile_declared=src.get('original_profile_declared'), availability='OBSERVED_AVAILABLE', access_policy_id=access_policy_id, declared_scientific_review=src.get('declared_scientific_review')),
        snapshot=dict(snapshot_id=snapshot_id, binding_basis='SYNTHETIC_FIXTURE', bytes_sha256=bytes_sha256, digest_status='OBSERVED_BYTES' if bytes_sha256 is not None else 'NOT_COMPUTED', observed_at=observed_at, scientific_at=None, generated_at=generated_at, expires_at=expires_at, freshness='OBSERVED_SNAPSHOT_ONLY'),
        validation=dict(descriptor_schema='NOT_RUN', descriptor_semantics='NOT_RUN', literal_comparison='SOURCE_ROW_COMPARED', source_profile_assessment='NOT_ASSERTED', authenticity='NOT_VERIFIED', scientific_approval='NOT_EVALUATED'),
        policy=dict(source_access='EXTERNAL_EXACT_ALLOWLIST_ONLY', max_descriptor_bytes=MAX_DESCRIPTOR_BYTES, ttl_max_seconds=3600, browser_persistence='MEMORY_ONLY', automatic_uri_access=False),
        nodes=nodes, tables=tables, relations=relations, assets=assets, unmapped_fields=unmapped,
        coverage=dict(population='SYNTHETIC_FIXTURE', global_archive='UNKNOWN_UPSTREAM', global_history='GLOBAL_UNPROVEN', global_total=None, global_percentage=None, snapshot_overlap='NOT_SUMMED', counts=[dict(unit=unit, selected=count, loaded=count, visible=None, unavailable=0, unknown_reason='UI not executed; synthetic selection only.') for unit, count in counts.items()]), gaps=gaps)
