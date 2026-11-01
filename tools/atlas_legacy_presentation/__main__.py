"""Production CLI fails before filesystem access; synthetic API is test-only."""
import argparse
import json
import sys
from .errors import ReaderError
from .reader import prepare


def main():
    parser = argparse.ArgumentParser(description='External acquisition/G4 BLOCKED pending a qualified native worker. No private paths are inspected.')
    parser.add_argument('--source', required=True)
    parser.add_argument('--allow', action='append', required=True)
    parser.add_argument('--scratch', required=True)
    parser.add_argument('--ttl-seconds', type=int, default=3600)
    parser.add_argument('--synthetic-fixture', action='store_true', help='Deprecated on CLI: does not authorize caller-selected files. Synthetic tests use the internal fixture API only.')
    args = parser.parse_args()
    try:
        if args.synthetic_fixture:
            # Preserve the historical payload-free CLI failure code, but do not
            # create scratch or open caller-selected bytes under a test label.
            raise ReaderError('IO_UNVERIFIED')
        prepare(args.source, args.allow, args.scratch, ttl_seconds=args.ttl_seconds)
        # No returning capability is implemented in this revision.
        raise ReaderError('OS_ISOLATION_UNVERIFIED')
    except (ReaderError, OSError) as error:
        print(json.dumps({'status': 'F4_C2_BLOCKED_EXACT', 'code': error.code if isinstance(error, ReaderError) else 'IO_UNVERIFIED'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
