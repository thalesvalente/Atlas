# Implementation Plan: configuração portátil de fontes

**Branch**: `feat/atlas-portable-source-config-20261110`  
**Spec**: [spec.md](spec.md) · **Tasks**: [tasks.md](tasks.md)  
**Base**: `43f7aaafedac7e8b124188baa51b888cee74c13c` (development).

## Summary

Guardar preferências de caminhos no pacote Atlas, reutilizando o SDK para validar
pacotes e o catálogo para leitura. CLI e launchers compartilham a resolução; não
há alteração do protocolo científico ou descoberta de diretórios.

## Technical Context

Python 3.11+ e biblioteca padrão; SDK `caderno_protocol` já existente. Windows
PowerShell 5.1/7 e Linux. Sem instalação de ferramenta adicional. Caminhos
privados não integram fixtures, logs públicos, commits nem a configuração de exemplo.

### Contrato de configuração e resolução

Formato JSON UTF-8 estrito: `{"version":1,"sources":["CAMINHO_DO_PACOTE"]}`.
`version` é inteiro exato 1, não booleano. `sources` é lista ordenada de 0–16
strings não vazias; chaves desconhecidas/duplicadas e tipos inesperados falham.

| Origem | Localização/base | Ausência |
|---|---|---|
| `--source`/`-Source` | Relativo ao CWD da chamada | Sem argumento, consultar a próxima origem |
| `--config`/`-Config` | Caminho do JSON relativo ao CWD | Erro se indicado e não encontrado |
| Padrão Windows | `%LOCALAPPDATA%/Atlas/sources.json`; fallback `~/AppData/Local/Atlas/sources.json` | Catálogo vazio sem criar arquivo |
| Padrão Linux | `$XDG_CONFIG_HOME/atlas/sources.json`; fallback `~/.config/atlas/sources.json` | Catálogo vazio sem criar arquivo |
| `sources` editado no JSON | Caminhos relativos à pasta do próprio JSON | Fonte ausente/inacessível é erro |

Fonte CLI presente vence todas as configurações sem lê-las. `--no-config`
desabilita a leitura persistida; fontes explícitas continuam aceitas. A combinação
`--config` e `--no-config` é rejeitada como intenção contraditória. Nenhuma mescla.
Ao salvar via CLI, os caminhos relativos ao CWD são normalizados e persistidos
absolutos. Editar o JSON manualmente pode manter caminhos relativos portáteis.
Normalização não pode esconder symlink de entrada antes das rejeições do SDK.
Deduplicar por caminho normalizado, incluindo diretório e seu metadata; falhar
em duplicação, sem omitir silenciosamente entradas.

### API compartilhada (P02)

Em `packages/atlas/src/atlas_viewer/source_config.py`:

```python
class SourceConfigError(ValueError): ...
def resolve_sources(sources=None, config_path=None) -> list[str]: ...
def save_sources(sources, config_path=None) -> None: ...
def config_summary(config_path=None, *, show_paths=False) -> dict: ...
```

`resolve_sources(None, ...)` consulta configuração; `resolve_sources([], ...)`
representa seleção vazia explícita. Startup valida caminho/existência/tipo e
duplicados sem duplicar a leitura completa do pacote feita pelo catálogo.
`save_sources([])` persiste seleção vazia; demais gravações validam todos os
pacotes via SDK antes de criar/substituir configuração. Resumo padrão informa
estado/quantidade sem paths; `show_paths=True` é exposição local opt-in.

### Comandos e integração

- `atlas config set --source CAMINHO [--source OUTRO] [--config ARQUIVO]`
- `atlas config show [--config ARQUIVO] [--show-paths]`
- `atlas config clear [--config ARQUIVO]`
- `atlas serve` e `atlas dossier`: `--config` e `--no-config`; `inspect` inalterado.
- `scripts/atlas_launch.py`: `--config`, `--configure`, `--show-config`,
  `--show-paths`, `--clear-sources`, `--no-config`.
- `scripts/ABRIR-ATLAS.ps1`: equivalentes `-Config`, `-Configure`, `-ShowConfig`,
  `-ShowPaths`, `-ClearSources`, `-NoConfig`; manter parâmetros existentes.

Gestão é exclusiva: configurar exige fonte, exibir/limpar não iniciam servidor,
`show-paths` só se aplica à exibição. O launcher repassa `--no-config` ao filho
para congelar inclusive a lista vazia. Modo legado sem fonte/config explícita
ignora padrão; outras seleções explícitas respeitam limite de 16 com adaptador.

### Persistência e limites de segurança

Validar tudo antes de modificar destino. Recusar destino que coincida com pacote
ou metadata, esteja dentro de fonte selecionada, seja link ou objeto impróprio.
Criar temporário exclusivo no diretório de destino, escrever e sincronizar o
arquivo, substituir com `os.replace`; limpar temporário próprio em falha.
Evitar publicar arquivo parcialmente gravado e conceder permissões locais
restritas quando suportado. Falhas anteriores à troca preservam bytes antigos.
Não há promessa de durabilidade contra falha física posterior à troca, trava
multioperador ou proteção total contra host adversarial. O SDK continua dono da
validação científica; a preferência nunca modifica ou autentica ciência.

## Constitution Check

| Princípios | Aplicação nesta feature |
|---|---|
| ARC-01/03 | Preferência local separada de fonte e identidade científica |
| ARC-02/06 | SDK/protocolo intactos; validade não concede autenticidade/aceite |
| ARC-04/05 | Sem import R4, descoberta ou dependências novas; pacotes independentes |
| ARC-07/08 | Somente JSON de preferências gravável, sem migração/retirada de fontes |
| ARC-09 / ADR-0001 | Solução compatível; nenhum desvio arquitetural ou gate humano presumido |

## Project Structure

- P01: `specs/008-portable-source-config/{spec,plan,tasks,checklist}.md`.
- P02: `packages/atlas/src/atlas_viewer/source_config.py`, `__main__.py` e `tests/viewer/test_source_config.py` e eventual `test_source_config_cli.py`.
- P03: `scripts/atlas_launch.py`, `scripts/ABRIR-ATLAS.ps1`, documentação operacional e `tests/viewer/test_native_notebook_source_config_launcher.py`.
- P00: `scripts/qa/portable_source_config_smoke.py`, composição, evidência final, publicação e handoff local; único integrador.

## Ordem, verificação e Spec Kit

O0 base/branch → O1 contrato → P02 e P03 paralelos, P01 crosswalk → composição
P00 → revisão não autora P01 + testes → PR Draft → handoff Windows.
Cada writer conserva ownership; revisor não altera o código auditado.

As skills locais specify/plan/tasks/analyze e scripts Python existentes foram
utilizados com `SPECIFY_FEATURE_DIRECTORY=specs/008-portable-source-config` e
`SPECIFY_FEATURE_NO_PERSIST=1`. `specify` CLI ausente: `NOT_RUN`, sem instalação.
O seletor `.specify/feature.json` permanece ausente. Hooks `extensions.yml`
ausentes. Templates resolvidos de verdade; não se cria documentação redundante.
Contratos/dados/decisões estão neste plano; checklist e tarefas completam o conjunto.

Testes cobrem FR-001–018 com fixtures temporárias: primeira execução, round-trip,
relocação, Unicode, relativos, precedence, ausência/invalidade, dedup/limite,
falhas de gravação/troca, isolamento de config, fontes imutáveis e processo filho.
O smoke `scripts/qa/portable_source_config_smoke.py` exercita subprocessos,
config isolada, persistência/reuso/relocação, relativos, múltiplas fontes, override,
negativos e imutabilidade com pacotes sintéticos. Instalação isolada usa wheels
do próprio projeto e tooling disponível, sem baixar novas dependências.
Regressões existentes de catálogo/launcher/instalação são reexecutadas conforme
risco. PowerShell real/instalação Windows: `LOCAL_TEST_NOT_RUN` até recibo.
Não usar portas 18768, 18770 ou 18772; testes devem escolher portas livres.

## Complexity Tracking

Nenhuma nova dependência, novo serviço, alteração do protocolo ou exceção a ARC.
Comandos adicionais são opt-in; inicialização normal nunca pede interação.
