# Implementation Plan: ATLAS021-A-POC-R4-FOCO01

Data: 2026-10-24. [Spec](spec.md).
Branch de integração: feat/atlas021-poc-r4-foco01-20261024.

## Summary

Reusar SDK, viewer e exportadores. Acrescentar receita persistente privada,
fortalecer harness genérico de interface e fechar negativas faltantes.
Nenhuma mudança de arquitetura, runtime do produto, perfil, schema ou licença.

## Technical Context

Python3.12 de ensaio; runtime existente baseado em stdlib.
Ferramentas isoladas: build1.3.0, setuptools80.9.0, wheel0.45.1,
jsonschema4.25.1, Spec Kit1.2.3.
CI mantém Windows/Ubuntu × normal/-O e Chromium. Versão efetiva do navegador
local é registrada sem equipará-la automaticamente ao pin de CI.
Snapshots diretório/ZIP, catálogo em memória; nenhum backend novo.

## Constitution Check

ARC-01–09, ADR-0001/0002 e documento do perfil ficam byte a byte preservados.
A issue #2 delimita esta feature, sem alterar constituição1.0.0.
PUBLIC-SOURCE-TRANSFER=[]; nenhum hook de extensão registrado.

## Project Structure and Ownership

| Owner | Repo | Arquivos | Resultado |
|---|---|---|---|
| ORQ-A | público | specs/002-atlas021-poc-r4, workflow e recibos públicos | requisitos, integração, CI, entrega |
| A2 | público | scripts/qa/browser.mjs, README e guia demo | UI por fonte e receita independente |
| A3 | privado | namespaces do adaptador e feature sucessora | comando persistente, matriz e recibos |
| A4 | público | teste focal QA, parecer e checklist security-architecture | negativas e revisão independente |

A2/A4 têm worktrees isoladas. A3 materializa blobs privados verificados, sem
inventar checkout completo. ORQ é único publicador; main e outras frentes intactas.

## Execution and Verification

1. Revalidar baselines e fontes primárias; conservar recibos históricos.
2. Aplicar ciclo Spec Kit ao delta sob contratos existentes.
3. Demo privada por initialize/plan_import/apply_import/read_model; consumir
   snapshot em wheels públicos instalados em venv vazio.
4. UI por fonte via harness genérico, sem condicionais R4 no viewer.
5. Negativas faltantes e suítes afetadas; reusar prova normativa se bytes intactos.
6. Branches/PRs Draft sucessoras empilhadas nas candidatas, CI por HEAD, Codex
   e revisão independente. Pin privado ao SHA público exato.
7. Evidência final append-only nas PRs e handoff privado para evitar auto-referência
   do SHA de um documento que ainda seria alterado.

## Risk and Reversibility

Risco: comparação provar só ambiental. Mitigação: par compatível por fonte e
novo cenário sintético R4 explicitamente declarado, default antigo preservado.
Risco: recibo de SHA errado. Mitigação: comparar identidade com checkout/manifestos.
Risco: exposição. Mitigação: mapas/corpus/recibos privados ficam privados.
Reverter feature não transforma nem remove fonte.
Resultados históricos não contam como novos; falhas reais não recebem PASS.
