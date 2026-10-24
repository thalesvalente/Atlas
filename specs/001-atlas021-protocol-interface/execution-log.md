# Registro do ciclo Spec Kit e execução — ATLAS021

Data: 2026-10-24. Toolkit: specify-cli **1.2.3**, release oficial `v1.2.3`.
Fonte: https://github.com/github/spec-kit/releases/tag/v1.2.3 .

## Preflight e execução efetiva

Nenhuma instalação prévia do toolkit ou AGENTS herdado foi encontrada neste workspace.
Python 3.12.14; Git 2.51.1; Node24.22.1; quatro agentes nativos totais.
Os agentes herdaram a configuração da sessão; o parâmetro de esforço efetivo não é
exposto pelos recibos, portanto não se afirma troca de modelo ou MAX/xHigh verificado.

Instalação ocorreu em ambiente de ferramentas isolado, por PyPI oficial e versão fixa.
Comandos oficiais executados, todos com saída real:

```sh
specify version
specify init --here --force --non-interactive --integration codex --integration-options='--skills' --ignore-agent-tools --script py
python .specify/scripts/python/resolve_template.py constitution-template --json
python .specify/scripts/python/create_new_feature.py --json --short-name atlas021-protocol-interface 'Atlas independente, protocolo interoperável e dois produtores'
python .specify/scripts/python/setup_plan.py --json
python .specify/scripts/python/check_prerequisites.py --json --paths-only
python .specify/scripts/python/setup_tasks.py --json
python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
```

O scaffold foi criado antes de preencher os artefatos. Não há hooks de extensão.
A integração instalada anuncia `$speckit-*`; a documentação geral mostra `/speckit-*`
para outra integração. As skills são instruções de agente, não executáveis do shell.
Neste ambiente elas foram lidas e aplicadas pelo coordenador; sua invocação nativa
em Codex CLI é **NOT_RUN**, pois o executável não estava disponível. Não se declara
"Spec Kit executado integralmente" como se todos os comandos de agente tivessem rodado.

O estado `.specify/feature.json` é local por checkout e aponta à feature desta missão;
permanece não versionado conforme a política do toolkit. `.specify/toolchain.json`
fixa a integração. Worktrees auxiliares não concorrem sobre esse estado.

## Artefatos e responsáveis

| Etapa | Execução | Evidência |
|---|---|---|
| constitution | Aplicação pelo ORQ da skill instalada | ARC-01–09 em constitution/ADR-0001 |
| specify | Auxiliar oficial + autoria ORQ | spec.md, FR-001–020, SC-001–006 |
| clarify | Análise pelo ORQ a partir da missão | clarifications.md; nenhum consentimento inventado |
| plan | Auxiliar oficial + análise/pesquisa delegada A1 | plan/research/data-model/contracts |
| checklist | Revisão independente A4 | checklists/requirements.md e security-architecture.md |
| tasks | Auxiliar oficial + tarefas ORQ | tasks.md; ownership exclusivo |
| analyze | Auxiliar oficial + análise ORQ/A4 | analysis.md e traceability.md |
| implement | Código real por ORQ/A2, A1 e A3 privado | commits por componente |
| verify/test | unittest, AST, wheels isolados, browser e CI | scripts/qa, docs/verification |
| converge | Comparação explícita requisitos/evidências/gates | convergence.md |
| independent review | A4 + Codex solicitado no GitHub | docs/reviews e PRs reais |

Nenhuma etapa documental autoriza promoção, operação física ou transferência privada.
