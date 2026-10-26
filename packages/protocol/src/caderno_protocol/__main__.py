"""Validate an explicit local snapshot. Never writes or fetches the source."""
import argparse
import json
from . import load_package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    args = parser.parse_args()
    package = load_package(args.source)
    print(json.dumps({"metadata_sha256": package.metadata_sha256, "report": package.report.to_dict(),
                      "payloads": package.payload_status}, ensure_ascii=False, indent=2))
    return 0 if package.report.valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
