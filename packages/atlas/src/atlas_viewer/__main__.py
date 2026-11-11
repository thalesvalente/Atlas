"""Explicit local input only; output is presentation, never source mutation."""
from __future__ import annotations

import argparse
import json

from .catalog import Catalog
from .server import make_server
from .source_config import config_summary, resolve_sources, save_sources, SourceConfigError


def _selection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", action="append", default=None,
                        help="Pacote ou metadados explicitamente autorizados; substitui a configuração")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--config", help="Arquivo JSON local de fontes")
    selection.add_argument("--no-config", action="store_true",
                           help="Não ler configuração; sem --source, abrir vazio")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas — consulta local de registros científicos")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Abrir interface local somente leitura")
    _selection_arguments(serve)
    serve.add_argument("--port", type=int, default=8765)
    inspect = sub.add_parser("inspect", help="Inspecionar uma fonte pelo protocolo")
    inspect.add_argument("source")
    dossier = sub.add_parser("dossier", help="Enviar dossiê derivado ao stdout")
    _selection_arguments(dossier)
    config = sub.add_parser("config", help="Gerenciar somente a configuração local de fontes")
    actions = config.add_subparsers(dest="config_action", required=True)
    set_config = actions.add_parser("set", help="Validar e salvar a seleção completa")
    set_config.add_argument("--source", action="append", required=True)
    show_config = actions.add_parser("show", help="Consultar seleção sem abrir fontes")
    show_config.add_argument("--show-paths", action="store_true",
                             help="Exibir caminhos privados somente neste terminal")
    clear_config = actions.add_parser("clear", help="Salvar seleção vazia sem apagar fontes")
    for action in (set_config, show_config, clear_config):
        action.add_argument("--config", help="Arquivo JSON local; padrão por usuário quando ausente")
    args = parser.parse_args(argv)
    try:
        if args.command == "config":
            if args.config_action in {"set", "clear"}:
                save_sources(args.source if args.config_action == "set" else [], args.config)
            print(json.dumps(config_summary(args.config,
                                           show_paths=getattr(args, "show_paths", False)),
                             ensure_ascii=False, indent=2, allow_nan=False))
            return 0
        if args.command == "inspect":
            paths = [args.source]
        else:
            explicit = (args.source or []) if args.no_config else args.source
            paths = resolve_sources(explicit, args.config)
        catalog = Catalog(paths)
    except SourceConfigError as exc:
        parser.error(str(exc) + "; use atlas config set --source CAMINHO (ou --config NOVO_ARQUIVO).")
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
