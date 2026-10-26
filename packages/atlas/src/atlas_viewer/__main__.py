"""Explicit local input only; output is presentation, never source mutation."""
from __future__ import annotations

import argparse
import json

from .catalog import Catalog
from .server import make_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas — consulta local de registros científicos")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Abrir interface local somente leitura")
    serve.add_argument("--source", action="append", default=[], help="Pacote ou metadados explicitamente autorizados")
    serve.add_argument("--port", type=int, default=8765)
    inspect = sub.add_parser("inspect", help="Inspecionar uma fonte pelo protocolo")
    inspect.add_argument("source")
    dossier = sub.add_parser("dossier", help="Enviar dossiê derivado ao stdout")
    dossier.add_argument("--source", action="append", default=[])
    args = parser.parse_args(argv)
    paths = [args.source] if args.command == "inspect" else args.source
    try:
        catalog = Catalog(paths)
    except ValueError as exc:
        parser.error(str(exc))
    if args.command == "serve":
        if not 0 <= args.port <= 65535:
            parser.error("Porta fora do intervalo 0–65535.")
        server = make_server(catalog, args.port)
        print(f"Atlas candidato: http://127.0.0.1:{server.server_address[1]} — somente leitura", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    data = catalog.dossier() if args.command == "dossier" else catalog.snapshot()
    print(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if all(s["status"] == "READY" for s in data["sources"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
