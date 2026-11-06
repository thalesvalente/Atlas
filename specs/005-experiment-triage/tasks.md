# Tasks — Feature 005

## O0 — Reconciliação e Spec Kit
- [x] T001 Revalidar PR32, aceite, SHA/tree, CI/review, branches/owners e contratos.
- [x] T002 Criar Feature005 com template/scripts oficiais, sem estado global; spec/plan/checklists e API de integração.

## O1 — Incrementos paralelos
- [x] T003 [P] [US1] Reproduzir divergência de execução e ausências reais com testes RED.
- [x] T004 [P] [US1] Implementar modelo tipado de busca/facetas/baselines e negativos.
- [x] T005 [P] [US1] Implementar lateral responsiva, busca global, filtros contextuais e localizar.
- [x] T006 [P] [US2] Implementar ledger e controles de lote sincronizados, revisão e comparação.
- [x] T007 [P] [US3] Implementar dossiê/plano inerte, intenções, proteção fail-closed e exportação.
- [x] T008 [P] Criar fixture 1200+, tarefas T01–T10 e browser em cinco viewports; adaptar navegação dos harness anteriores sem enfraquecê-los.

## O2/O3 — Composição e qualificação
- [x] T009 Integrar commits com autoria/linhagem, revisar escopo e preservar baselines/P03.
- [x] T010 GREEN unitários/integração/regressões, precisão, CSP, ausência de mutações e R4 no candidato de produto `3a9e1e3d2727c69175768abb437bdcbc47cfabf0`.
- [x] T011 Browser QA com teclado/toque/foco/minimapa, seis viewports e checklist de acessibilidade no mesmo candidato.
- [x] T012 Revisão adversarial de agentes não autores; findings de domínio, composição e contraste corrigidos e contraprovas adicionadas.
- [x] T013a Publicar PR Draft empilhada #33 e qualificar o candidato de produto: 17/17 checks, Windows/Ubuntu normal/-O.
- **T013b — gate externo terminal:** CI e Codex Review do HEAD que inclui este fechamento documental. Resultado e SHA no recibo `ATLAS_EXPERIMENT_TRIAGE_HANDOFF` da [PR #33](https://github.com/thalesvalente/Atlas/pull/33). O PASS do produto não substitui esse gate.

## O4 — Handoff
- [x] T014a Matriz spec↔código↔testes, relatórios, screenshots sintéticos, hashes e limitações LOCAL versionados.
- **T014b — recibo externo terminal:** HEAD/tree/parent, checks e review finais reconciliados no mesmo handoff da PR, sem alterar o commit após sua qualificação.
- [ ] T015 Aceite humano desta feature (gate posterior, não concedido pelo executor).

Dependência: T001→T002→(T003–T008)→T009→(T010–T012)→T013→T014; T015 separado. Não parar num plano enquanto houver engenharia autorizada executável.

Os itens externos evitam autodeclarar CI/review antes da execução e evitam um ciclo de commits que altere o SHA recém-revisado. Consulte o recibo terminal para seu estado concluído ou bloqueado; o aceite humano T015 continua sendo um gate posterior próprio.
