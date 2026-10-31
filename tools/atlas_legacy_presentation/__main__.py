"""Explicit, test-only synthetic CLI. Real legacy acquisition is blocked."""
import argparse
import json
import sys
from pathlib import Path
from .errors import ReaderError
from .reader import prepare, private_scratch


def main():
    parser = argparse.ArgumentParser(description='External synthetic qualification only; real acquisition/G4 BLOCKED. No qualified OS isolation or hard budget.')
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--allow', action='append', type=Path, required=True)
    parser.add_argument('--scratch', type=Path, required=True, help='Separate parent; creates a private operation subdirectory.')
    parser.add_argument('--ttl-seconds', type=int, default=3600)
    parser.add_argument('--synthetic-fixture', action='store_true', help='TEST ONLY: operator asserts invented fixture. This does not prove provenance or isolation. Never use for L1 acervo.')
    args = parser.parse_args()
    try:
        if not args.synthetic_fixture:
            raise ReaderError('HARD_BUDGET_UNVERIFIED')
        output = prepare(args.source, args.allow, private_scratch(args.scratch), ttl_seconds=args.ttl_seconds, synthetic_fixture=True)
        print(json.dumps({'status': 'SYNTHETIC_DESCRIPTOR_ONLY', 'output': str(output), 'g4': 'BLOCKED', 'hard_budget': 'HARD_BUDGET_UNVERIFIED', 'os_isolation': 'OS_ISOLATION_UNVERIFIED', 'cleanup': 'No crash cleanup guarantee; TTL must be enforced by consumer.'}))
        return 0
    except ReaderError as error:
        print(json.dumps({'status': 'F4_C2_BLOCKED_EXACT', 'code': error.code}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
