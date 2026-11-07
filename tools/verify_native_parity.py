"""Offline native-view field parity against an explicitly pinned projection.

An externally supplied hash/revision constrains the comparison. It is not a
signature, a global inventory, browser evidence or scientific acceptance.
Never executes a producer or writes a source. Reports contain paths/types only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from caderno_protocol.storage import _regular_bytes, _strict_json
from atlas_viewer.native_notebook import MAX_NATIVE_LOGICAL_BYTES, json_bytes, read_source


def fields(value, pointer=''):
    """Include containers and every scalar, keeping JSON types and presence."""
    kind = ('null' if value is None else 'boolean' if isinstance(value, bool)
            else 'integer' if isinstance(value, int) else 'number' if isinstance(value, float)
            else 'string' if isinstance(value, str) else 'array' if isinstance(value, list) else 'object')
    yield pointer, kind, hashlib.sha256(json_bytes(value)).hexdigest()
    children = enumerate(value) if isinstance(value, list) else value.items() if isinstance(value, dict) else []
    for key, child in children:
        escaped = str(key).replace('~', '~0').replace('/', '~1')
        yield from fields(child, pointer + '/' + escaped)


def verify(*, projection: Path, package: Path, expected_sha256: str, expected_revision: str,
           include_fields: bool = True) -> dict:
    if not re.fullmatch('[0-9a-f]{64}', expected_sha256) or not expected_revision:
        raise ValueError('EXPLICIT_SOURCE_PINS_REQUIRED')
    source_bytes = _regular_bytes(Path(projection), MAX_NATIVE_LOGICAL_BYTES)
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError('PROJECTION_PIN_MISMATCH')
    source = _strict_json(source_bytes)
    integration = source.get('atlas_integration')
    if not isinstance(integration, dict) or integration.get('notebook_revision') != expected_revision:
        raise ValueError('REVISION_PIN_MISMATCH')
    state, exported = read_source(Path(package), 'explicit-package')
    if state['status'] != 'READY' or exported is None:
        raise ValueError('PACKAGE_NOT_READY')
    if state['revision'] != expected_revision:
        raise ValueError('REVISION_PIN_MISMATCH')
    # Compare every value, type and key, not population counts. Canonical bytes
    # also distinguish bool/int, NULL/absence, numeric/string and list ordering.
    canonical = json_bytes(source)
    if exported != canonical:
        raise ValueError('PROJECTION_CONTENT_MISMATCH')
    rows, count, field_digest = [], 0, hashlib.sha256()
    for pointer, kind, digest in fields(source):
        count += 1
        field_digest.update(json_bytes([pointer, kind, digest]) + b'\n')
        if include_fields:
            rows.append({'pointer': pointer, 'type': kind, 'value_sha256': digest,
                         'available_in_source': 'PASS', 'imported': 'PASS',
                         'searchable_navigable': 'NOT_RUN', 'exportable': 'PASS'})
    return {'version': 'atlas-native-parity/1', 'status': 'PASS_SCOPED',
            'authentication': 'EXPLICIT_PIN_MATCH_ORIGIN_NOT_INFERRED',
            'projection_bytes_sha256': actual_sha256,
            'canonical_projection_sha256': hashlib.sha256(canonical).hexdigest(),
            'package_metadata_sha256': state['metadata_sha256'],
            'expected_revision': expected_revision, 'entries': len(state['entries']),
            'field_count': count, 'fields': rows, 'field_index_sha256': field_digest.hexdigest(),
            'field_detail': 'INCLUDED' if include_fields else 'OMITTED_EXPLICITLY',
            'functional_browser': 'NOT_RUN',
            'global_completeness': 'NOT_PROVEN', 'scientific_acceptance': 'NOT_EVALUATED',
            'retirement_authorized': False, 'DELETE_AUTHORIZED': 'NO'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--projection', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--expected-revision', required=True)
    parser.add_argument('--report', type=Path, required=True, help='New private report; never overwrite')
    parser.add_argument('--summary-only', action='store_true', help='Compare every field but omit individual paths from report')
    args = parser.parse_args(argv)
    try:
        destination = args.report.resolve()
        for source_root in (args.projection.resolve().parent,
                            args.package.resolve() if args.package.is_dir() else args.package.resolve().parent):
            if destination == source_root or destination.is_relative_to(source_root):
                raise ValueError('REPORT_MUST_BE_DISJOINT_FROM_SOURCES')
        report = verify(projection=args.projection, package=args.package,
                        expected_sha256=args.expected_sha256, expected_revision=args.expected_revision,
                        include_fields=not args.summary_only)
        # A report may be large; stdout carries only the compact receipt.
        with args.report.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({key: value for key, value in report.items() if key != 'fields'}))
        return 0
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
