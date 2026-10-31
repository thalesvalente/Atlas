"""Closed descriptor schema and semantic checks; no source or network access."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
import json
import re
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from .errors import ReaderError


def _bad(code='DESCRIPTOR_SEMANTICS_INVALID'):
    raise ReaderError(code)


def _json(data):
    def reject(value):
        _bad()

    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                _bad()
            value[key] = item
        return value

    try:
        return json.loads(data, parse_float=Decimal, parse_constant=reject, object_pairs_hook=pairs)
    except (ValueError, UnicodeError, RecursionError):
        _bad()


def _tree(value, depth=0):
    if depth > 20:
        _bad('QUOTA_EXCEEDED')
    if isinstance(value, dict):
        for key, item in value.items():
            key.encode('utf-8', errors='strict')
            _tree(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _tree(item, depth + 1)
    elif isinstance(value, str):
        value.encode('utf-8', errors='strict')


def _time(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None or result.utcoffset() is None:
            _bad()
        return result
    except (ValueError, TypeError, AttributeError):
        _bad()


def _cell(cell):
    kind, raw, literal = cell['type'], cell['lexeme'], cell['literal']
    if literal is not None and len(literal.encode('utf-8')) > 65536:
        _bad('QUOTA_EXCEEDED')
    if raw is not None and len(raw.encode('utf-8')) > 131072:
        _bad('QUOTA_EXCEEDED')
    if kind == 'missing':
        return
    parsed = _json(raw)
    if kind == 'null':
        if parsed is not None:
            _bad()
    elif kind == 'string':
        if type(parsed) is not str or parsed != literal:
            _bad()
    elif kind == 'boolean':
        if type(parsed) is not bool or raw != literal:
            _bad()
    elif kind in ('integer', 'decimal'):
        if type(parsed) not in (int, Decimal) or raw != literal:
            _bad()
        if kind == 'integer' and not re.fullmatch(r'-?(0|[1-9][0-9]*)', raw):
            _bad()
        if kind == 'decimal' and not re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?', raw):
            _bad()
    elif kind in ('array', 'object'):
        expected = list if kind == 'array' else dict
        if type(parsed) is not expected or literal != raw:
            _bad()
        _tree(parsed)


def validate_descriptor(descriptor, schema, *, now=None):
    if schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema' or schema.get('$id') != 'urn:atlas:proposal:legacy-presentation:0.2.0':
        _bad('DESCRIPTOR_SCHEMA_INVALID')

    def local_refs(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == '$ref' and (not isinstance(item, str) or not item.startswith('#/')):
                    _bad('DESCRIPTOR_SCHEMA_INVALID')
                local_refs(item)
        elif isinstance(value, list):
            for item in value:
                local_refs(item)

    local_refs(schema)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(descriptor)
    except (SchemaError, ValidationError, TypeError):
        _bad('DESCRIPTOR_SCHEMA_INVALID')
    try:
        _tree(descriptor)
        encoded = json.dumps(descriptor, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    except (UnicodeError, ValueError, RecursionError):
        _bad()
    if len(encoded) > 33554432:
        _bad('QUOTA_EXCEEDED')
    d = descriptor
    source, snapshot = d['source']['source_id'], d['snapshot']['snapshot_id']
    snap = d['snapshot']
    observed, generated, expires = (_time(snap[k]) for k in ('observed_at', 'generated_at', 'expires_at'))
    if not observed <= generated < expires or (expires - generated).total_seconds() > 3600:
        _bad()
    if now is not None:
        current = _time(now) if isinstance(now, str) else now
        if current.tzinfo is None:
            _bad()
        if current >= expires:
            _bad('DESCRIPTOR_EXPIRED')
    if (snap['bytes_sha256'] is None) != (snap['digest_status'] == 'NOT_COMPUTED'):
        _bad()
    if not d['synthetic'] and (snap['binding_basis'] != 'OBSERVED_BYTES_AND_POLICY' or snap['digest_status'] != 'OBSERVED_BYTES'):
        _bad()
    nodes, tables, relations, assets = (d[k] for k in ('nodes', 'tables', 'relations', 'assets'))
    rows = [row for table in tables for row in table['rows']]
    if len(rows) > 100000 or len(nodes) > 10000 or len(relations) > 100000 or len(tables) > 128 or len(assets) > 10000:
        _bad('QUOTA_EXCEEDED')
    targets = nodes + tables + rows + assets
    all_objects = targets + relations
    navs = {}
    natives = defaultdict(list)
    occurrences = defaultdict(list)
    locators = set()
    for item in all_objects:
        identity = item['identity']
        nav = identity['navigation_id']
        if nav in navs or not identity['locator'] or identity['locator'] in locators:
            _bad()
        locators.add(identity['locator'])
        navs[nav] = item
        if identity['native_id'] is not None:
            occurrences[identity['native_id']].append(identity['occurrence'])
    for values in occurrences.values():
        if sorted(values) != list(range(len(values))):
            _bad()
    for item in targets:
        if item.get('entity_status') != 'DECLARED_EXTERNAL_REFERENCE':
            native = item['identity']['native_id']
            if native is not None:
                natives[native].append(item)

    def ref(value):
        declared, target, status = (value[k] for k in ('declared_id', 'target_navigation_id', 'resolution'))
        local = value['source_id'] == source and value['snapshot_id'] == snapshot
        candidates = natives.get(declared, []) if local else []
        if status == 'RESOLVED':
            if declared is None or not local or len(candidates) != 1 or candidates[0]['identity']['navigation_id'] != target or not value['evidence_locator']:
                _bad()
        elif status == 'NULL_ENDPOINT':
            if declared is not None or target is not None:
                _bad()
        elif status in ('UNRESOLVED', 'COLLISION'):
            if target is not None:
                _bad()
            if status == 'COLLISION' and (declared is None or not local or len(candidates) < 2):
                _bad()
            if status == 'UNRESOLVED' and candidates:
                _bad()
        elif status == 'EXTERNAL_DECLARED':
            if declared is None:
                _bad()
            if target is not None:
                stub = navs.get(target)
                if stub is None or stub.get('entity_status') != 'DECLARED_EXTERNAL_REFERENCE' or stub['identity']['native_id'] is not None:
                    _bad()

    for node in nodes:
        ref(node['parent'])
        external = node['entity_status'] == 'DECLARED_EXTERNAL_REFERENCE'
        if external:
            if node['kind'] != 'Run' or node['external_reference'] is None or node['external_reference']['resolution'] != 'EXTERNAL_DECLARED':
                _bad()
        if node['external_reference'] is not None:
            ref(node['external_reference'])
        if node['tree_state'] == 'PARENT_RESOLVED' and (node['parent']['resolution'] != 'RESOLVED' or node['binding_gap']):
            _bad()
        if node['tree_state'] == 'ROOT_DECLARED' and (node['parent']['declared_id'] is not None or node['binding_gap']):
            _bad()
        if node['tree_state'] == 'RUN_EXTERNAL_ISOLATED' and (node['kind'] != 'Run' or not node['binding_gap']):
            _bad()
        if node['parent']['resolution'] == 'RESOLVED':
            parent = navs[node['parent']['target_navigation_id']]
            if parent not in nodes or node['parent_key_literal'] != node['parent']['declared_id']:
                _bad()
    for table in tables:
        ref(table['record_binding'])
        if table['domain'] == 'UNKNOWN' and table['domain_origin'] != 'UNKNOWN':
            _bad()
        if table['domain'] in ('RF', 'RNF', 'RES') and table['domain_origin'] != 'DECLARED':
            _bad()
        if [c['ordinal'] for c in table['columns']] != list(range(len(table['columns']))):
            _bad()
        if [r['ordinal'] for r in table['rows']] != list(range(len(table['rows']))):
            _bad()
        for row in table['rows']:
            ref(row['run_binding'])
            if row['run_binding']['resolution'] == 'RESOLVED' and navs[row['run_binding']['target_navigation_id']].get('kind') != 'Run':
                _bad()
            if row['binding_gap'] != (row['run_binding']['resolution'] != 'RESOLVED'):
                _bad()
            if len(row['cells']) != len(table['columns']):
                _bad()
            for cell in row['cells']:
                _cell(cell)
            requirement = row['requirement']
            if requirement:
                fields = requirement['fields']
                if any(index is not None and index >= len(row['cells']) for index in fields.values()):
                    _bad()
                if requirement['admission'] == 'ADMITTED_NATIVE_RF' and fields['id'] is not None:
                    id_cell = row['cells'][fields['id']]
                    if id_cell['type'] != 'string' or id_cell['literal'] != requirement['native_id']:
                        _bad()
                if requirement['admission'] == 'UNADMITTED_NATIVE_RF' and row['identity']['native_id'] is not None:
                    _bad()
                category = fields['category']
                absent = category is None or row['cells'][category]['type'] in ('missing', 'null')
                if requirement['category_status'] == 'MISSING' and not absent:
                    _bad()
                if requirement['category_status'] == 'PRESENT' and absent:
                    _bad()
    repeat_groups = defaultdict(list)
    for relation in relations:
        ref(relation['from'])
        ref(relation['to'])
        if relation['binding_gap'] != (relation['from']['resolution'] != 'RESOLVED' or relation['to']['resolution'] != 'RESOLVED'):
            _bad()
        if relation['repeat_group'] is not None:
            repeat_groups[relation['repeat_group']].append(relation)
    for group in repeat_groups.values():
        if len(group) < 2 or [r['repeat_occurrence'] for r in group] != list(range(1, len(group) + 1)):
            _bad()
        signatures = {(r['kind_literal'], r['semantics'], r['direction'], r['from']['source_id'], r['from']['snapshot_id'], r['from']['declared_id'], r['to']['source_id'], r['to']['snapshot_id'], r['to']['declared_id']) for r in group}
        if len(signatures) != 1:
            _bad()
    for asset in assets:
        ref(asset['declared_binding'])
        if asset['original_type'] == 'File' and asset['kind'] != 'File':
            _bad()
        if asset['kind'] == 'Product' and (not asset['declared_product_role'] or asset['declared_binding']['declared_id'] is None):
            _bad()
    for item in d['unmapped_fields']:
        if item['owner_navigation_id'] is not None and item['owner_navigation_id'] not in navs:
            _bad()
        _cell(item['value'])
    expected = {'presentation_node_occurrences': len(nodes), 'source_nodes': sum(n['entity_status'] == 'SOURCE_ENTITY' for n in nodes), 'external_reference_stubs': sum(n['entity_status'] == 'DECLARED_EXTERNAL_REFERENCE' for n in nodes), 'tables': len(tables), 'rows': len(rows), 'relations': len(relations), 'assets': len(assets)}
    counts = d['coverage']['counts']
    if len({c['unit'] for c in counts}) != len(counts) or set(c['unit'] for c in counts) != set(expected):
        _bad()
    for count in counts:
        if count['loaded'] != expected[count['unit']] or count['selected'] != expected[count['unit']] or count['visible'] is not None:
            _bad()
