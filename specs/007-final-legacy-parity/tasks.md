# Tasks

## Phase 1: Reconciliar
- [x] T001 Conferir main/PR38/ARC/Spec Kit e capturas protegidas (FR-001/005).
- [x] T002 Reproduzir colisões reais do CSV protegido com contraprova (FR-003).

## Phase 2: Implementar
- [x] T003 Testar e implementar exportação CSV tipada reversível (FR-003).
- [x] T004 Testar e implementar oráculo com pins de bytes/revisão (FR-001/002/004).

## Phase 3: Qualificar
- [x] T005 Executar regressões e instalação isolada sem R4 (SC-001/002).
- [x] T006 Qualificar CI e revisão do SHA publicado (SC-003).
- [x] T007 Entregar matrizes, contraprovas e decisão limitada de retirada (FR-005).

T006 recebeu 19/19 Actions SUCCESS e Codex completed/zero findings em
`29380daa17ae97151eb6db5239cc3f0df337f89f`. O sucessor documental recebe recibo
terminal próprio na PR Draft #39. T007 significa entrega de parecer limitado,
incluindo BLOCKED/NOT_RUN, sem conceder paridade plena ou retirada.

## Phase 4: Continuação de uso real e consumidores

- [x] T008 Reconciliar #39, main R4, checkout existente e ownership; preservar
  Caderno e alterações alheias (FR-007/008, plan: escopo congelado).
- [x] T009 [P] [US1] Atualizar PAR-001–015 e roteiro/evidência Chrome em recibos
  privados P01; corrigir apenas defeitos materiais nos componentes Atlas (FR-006/007, SC-004).
- [x] T010 [P] [US2] Separar produtor/renderer e entrypoints/aliases em
  src/r4/campaigns/notebook_query_projection.py, atlas.py e cli.py no R4 (FR-008).
- [x] T011 [US2] Substituir launcher/CLI/migração, testes e documentação R4;
  preservar nove assets e fallback, reconciliar C01–C09 (FR-009, SC-005).
- [x] T012 [US2] Qualificar contratos, negativos, cold start/refresh e consumo
  Atlas independente com fixtures isoladas em tests R4 (FR-010).
- [ ] T013 Qualificar diff final por QA P03, CI Windows/Ubuntu e Codex Review nas
  PRs Draft correspondentes; recibos próprios por SHA (FR-011).
- [x] T014 Integrar matrizes/contratos, ordem e rollback em handoff privado P00;
  conferir Git/processos/limpeza e manter decisões humanas separadas (SC-006).
- [x] T015 [US2] Atualizar tools/export_native_notebook.py, guardas dos launchers,
  README e testes de fronteira para consumir somente a API produtora (FR-008/009).
- [x] T016 [US1] Corrigir defeitos relatados pelo operador: separar seleção/título
  no catálogo e tornar desmarcar todos acessível em native_notebook.html,
  native_triage_ui.js e native_legacy_integration.css, com RED/GREEN e regressão
  sintética; conferir RNF/RES contra o snapshot sem inventar conteúdo (FR-006/007).

US1 e US2 seguem independentes após T008; bloqueio de Chrome não interrompe US2.
T013 depende de T010–T012; T014 preserva qualquer pendência factual de US1.
T015 também precede T013 e consome o contrato estabilizado por T010.
T016 decorre do teste manual parcial; sua correção técnica não concede aceite humano.
Conclusão de T009 significa entrega da matriz/roteiro/recibo, não Chrome PASS.

## Phase 5: Refinar a aplicação após reteste

- [ ] T017 [US1] Compactar identidade/seleção no catálogo em
  native_triage_ui.js/native_legacy_views.js/native_legacy_integration.css e
  preservar guardas de espaço, overflow e foco em testes Node/Chromium (FR-012).
- [ ] T018 [US1] Separar populações declaradas da fonte de agregações e estado
  local na visão geral e navegação, com testes ausência/zero em
  native_legacy_model.js/native_triage_ui.js/native_notebook.js (FR-013, SC-007).
- [ ] T019 [US1] Acrescentar agrupamento reversível por núcleo declarado à leitura
  de tabelas em native_notebook.js/native_legacy_model.js e testes de filtros,
  paginação, campos e JSON/CSV integral (FR-014, SC-008).
- [ ] T020 Qualificar T017–T019 por QA não autora, instalação, CI e Codex Review
  no novo SHA; reconciliar matrizes e handoff privados sem herdar PASS de 191304d
  (SC-007/008, FR-011).

T017–T019 compartilham P01 como único writer; T020 depende das três entregas.
