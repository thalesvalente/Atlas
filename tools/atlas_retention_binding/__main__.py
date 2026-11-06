"""Command-line entry point. The only output is a JSON report on stdout."""

import argparse
from contextlib import ExitStack
import json

from .binding import build_report
from .contracts import MAX_DOCUMENT_BYTES, Rejected, require
from .filesystem import authorized_roots, read_pinned_document
from .inventory import Inventory
from .plan import read_plan

MAX_SEGMENTS = 32
MAX_CHAIN_BYTES = 256 * 1024 * 1024


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Rejected("INVALID_ARGUMENTS")


def arguments(argv):
    parser = Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--inventory", required=True, action="append")
    parser.add_argument("--inventory-sha256", required=True, action="append")
    parser.add_argument("--root", required=True, action="append", metavar="ALIAS=ABSOLUTE_PATH")
    return parser.parse_args(argv)


def verify(args):
    require(0 < len(args.inventory) == len(args.inventory_sha256) <= MAX_SEGMENTS,
            "INVALID_INVENTORY_CHAIN")
    document, _ = read_pinned_document(args.plan, args.plan_sha256, "PLAN")
    source, items = read_plan(document)
    del document
    inventory = Inventory(source)
    remaining = MAX_CHAIN_BYTES
    for path, pin in zip(args.inventory, args.inventory_sha256, strict=True):
        document, size = read_pinned_document(path, pin, "INVENTORY", limit=min(remaining, MAX_DOCUMENT_BYTES))
        inventory.append(document, pin)
        remaining -= size
        del document
    selected = inventory.select(items)
    with ExitStack() as stack:
        roots = authorized_roots(stack, args.root)
        report = build_report(inventory, items, selected, roots)
    return {**report, "plan_sha256": args.plan_sha256, "inventory_head_sha256": inventory.parent}


def main(argv=None):
    try:
        result = verify(arguments(argv))
        exit_code = 0
    except Rejected as exc:
        result = {"status": "REJECTED", "error": str(exc)}
        exit_code = 2
    result["schema"] = "atlas-retention-binding-report/1"
    result["DELETE_AUTHORIZED"] = "NO"
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
