# Spec Kit e execução efetiva — FOCO01

Data de referência do usuário: 2026-10-24 (America/Fortaleza).
Quatro agentes nativos totais: ORQ-A, a2_public_demo, a3_private_adapter,
a4_independent_qa. Limite observado: coordenador + três subagentes simultâneos.
Não se afirma mudança de modelo ou esforço não exposto pelos recibos.

## Baseline e materialização

Atlas PR1 revalidada Draft no commit 228fee0af13b15cfacd97b9b122a395b86be10fe,
árvore ae5cb18bce8bb46942f8c6a3a7e5120c707e8106. Issue2 consultada; par privado
e main privados conferidos e registrados exclusivamente no privado.
Git CLI inicial sem conectividade; connector GitHub disponível. Recuperados 89
blobs públicos em base64, verificados por hash Git, reconstruídas todas as árvores
e o commit exato (não um commit local que se passa pelo original).
Worktrees isoladas A2/A4; integrador em branch própria. Nenhuma ref remota alterada
durante esta etapa. Blobs privados verificados separadamente.

## Toolchain e comandos oficiais reais

Não havia specify no PATH. Cache existente continha specify-cli1.2.3; instalado
offline em ambiente isolado com dependências realmente presentes, sem mudar pins
do produto. Uma tentativa inicial selecionou rich15 sem bytes em cache; instalação
corrigida usando rich13.9.4 compatível, sem alegar sucesso daquela tentativa.

Comandos efetivamente executados:

```sh
specify version
specify init tooling/speckit-scaffold --non-interactive --integration codex --integration-options='--skills' --ignore-agent-tools --script py
python .specify/scripts/python/resolve_template.py constitution-template --json
python .specify/scripts/python/create_new_feature.py --json --number 2 --short-name atlas021-poc-r4 'Demonstração reproduzível R4 para Caderno para Atlas sem expansão de domínio'
python .specify/scripts/python/check_prerequisites.py --json --paths-only
python .specify/scripts/python/setup_plan.py --json
python .specify/scripts/python/setup_tasks.py --json
```

Init ocorreu somente em scaffold novo. Diretórios oficiais ausentes de helpers/
templates foram copiados sem sobrescrever constitution.md/.specify existente.
Não foi usado init --force. Estado da feature é local por checkout, não branch.
Não há hooks de extensão registrados. Git branch continua própria de integração.

## Aplicação do ciclo

| Etapa | Modo real | Artefato |
|---|---|---|
| constitution | skill oficial lida, baseline preservada, resolver real | constitution1.0.0 e Constitution Check |
| specify | helper real + autoria de agente | spec.md e requirements.md |
| clarify | skill oficial + fontes primárias, zero perguntas | clarifications.md |
| plan | helper real + análise | plan/research/data-model/contracts/quickstart |
| checklist | skill oficial, revisão independente A4 | security-architecture.md |
| tasks | helper real + autoria ORQ | tasks.md |
| analyze | helper de pré-requisitos + análise ORQ/A4 | analysis/traceability |
| implement | alterações reais A2/A3/A4 em ownership próprio | commits e diffs |
| verify/test | processos reais, wheels, HTTP/browser, CI | recibos por ambiente/SHA |
| converge | skill oficial e confronto requisito/evidência | convergence.md |
| independent review | A4 e Codex remotos | pareceres e PRs |
| delivery | publicação Draft e coordenação privada | recibos append-only |

As skills são instruções aplicadas pelos agentes; dispatch nativo de comandos
Codex CLI: NOT_RUN (CLI ausente). Helpers/CLI acima são execuções reais.
Não se chama aplicação manual de invocação nativa. Inspeção e testes complementares
da baseline aconteceram em paralelo à documentação do delta, sob requisitos da
feature001 e missão; esta cronologia não é reescrita como uma execução serial.

## Evidência final

Contagens, binários, hashes e falhas de ambiente são preservados em recibos próprios.
A matriz final será referenciada na PR deste HEAD, sem atribuir execuções anteriores
ao novo commit. Não se publicam paths internos, corpus ou mapas privados neste log.
