# Tasks — Feature 005

## O0 — Reconciliação e Spec Kit
- [x] T001 Revalidar PR32, aceite, SHA/tree, CI/review, branches/owners e contratos.
- [x] T002 Criar Feature005 com template/scripts oficiais, sem estado global; spec/plan/checklists e API de integração.

## O1 — Incrementos paralelos
- [ ] T003 [P] [US1] Reproduzir divergência de execução e ausências reais com testes RED.
- [ ] T004 [P] [US1] Implementar modelo tipado de busca/facetas/baselines e negativos.
- [ ] T005 [P] [US1] Implementar lateral responsiva, busca global, filtros contextuais e localizar.
- [ ] T006 [P] [US2] Implementar ledger e controles de lote sincronizados, revisão e comparação.
- [ ] T007 [P] [US3] Implementar dossiê/plano inerte, intenções, proteção fail-closed e exportação.
- [ ] T008 [P] Criar fixture 1200+, tarefas T01–T10 e browser em cinco viewports; adaptar navegação dos harness anteriores sem enfraquecê-los.

## O2/O3 — Composição e qualificação
- [ ] T009 Integrar commits com autoria/linhagem, revisar escopo e preservar baselines/P03.
- [ ] T010 GREEN unitários/integração/regressões, precisão, CSP, ausência de mutações e R4.
- [ ] T011 Browser QA com teclado/toque/foco/minimapa e checklist de acessibilidade.
- [ ] T012 Revisão adversarial de agente não autor e correção de findings reproduzíveis.
- [ ] T013 Publicar PR Draft empilhada; CI Windows/Ubuntu normal/-O no SHA final e Codex Review terminal.

## O4 — Handoff
- [ ] T014 Matriz spec↔código↔testes, resultados reais, HEAD/tree/parent, limitações LOCAL e estado final.
- [ ] T015 Aceite humano desta feature (gate posterior, não concedido pelo executor).

Dependência: T001→T002→(T003–T008)→T009→(T010–T012)→T013→T014; T015 separado. Não parar num plano enquanto houver engenharia autorizada executável.
