# Tasks: configuração portátil de fontes

Owner de integração: P00. `[P]` indica áreas distintas; não autoriza dois writers
no mesmo arquivo. Status abaixo refere-se a evidência observada, sem aceite Windows.
Revisão não autora e hashes: [qa-review.md](qa-review.md). T019/T020 são
pré-publicação neste snapshot; o recibo terminal da PR sucederá este estado.
T021 permanece `LOCAL_TEST_NOT_RUN`, mesmo que CI Windows venha a passar.

## Phase 1: Setup

- [x] T001 P00 confirmar base/branch `feat/atlas-portable-source-config-20261110` em `specs/008-portable-source-config/spec.md` (FR-018).
- [x] T002 P01 ler constituição, ADR e specs 001/004/007; fixar contrato em `specs/008-portable-source-config/plan.md` (FR-001–018).

## Phase 2: Foundational

- [x] T003 P01 executar scripts Spec Kit sem persistir `.specify/feature.json` e registrar em `specs/008-portable-source-config/plan.md` (FR-018).
- [x] T004 P01 analisar spec/plan/tasks, critérios e contraprovas em `specs/008-portable-source-config/checklist.md` (FR-001–018).

## Phase 3: User Story 1 — Configurar e reutilizar (P1)

Critério independente: zero fontes sem config; salvar 1/16 fontes sintéticas e
reutilizar em outra chamada; limpar; resumir sem paths; bytes científicos intactos.

- [x] T005 [P] [US1] P02 implementar schema/local padrão, API load/save/resolve/summary e persistência em `packages/atlas/src/atlas_viewer/source_config.py` (FR-001–004, FR-007–012, FR-015).
- [x] T006 [US1] P02 adicionar comandos `config set/show/clear` em `packages/atlas/src/atlas_viewer/__main__.py` (FR-004, FR-015).
- [x] T007 [US1] P02 cobrir primeira execução, round-trip, lista vazia/1/16/17, duplicação e resumo em `tests/viewer/test_source_config.py` (FR-003–004, FR-007–008, FR-010, FR-015, FR-017).
- [x] T008 [P] [US1] P03 implementar gestão explícita sem servidor em `scripts/atlas_launch.py` e `scripts/ABRIR-ATLAS.ps1` (FR-004, FR-016).
- [x] T009 [US1] P03 cobrir gestão e passagem de argumentos em `tests/viewer/test_native_notebook_source_config_launcher.py` (FR-004, FR-016–017).

## Phase 4: User Story 2 — Mudar caminhos (P1)

Critério independente: fonte removida falha; seleção substituída abre; relativos,
Unicode e espaços têm resolução previsível; gravação falha sem perder arquivo anterior.

- [x] T010 [US2] P02 completar validações de caminhos/schema, dedup e destino protegido em `packages/atlas/src/atlas_viewer/source_config.py` (FR-005–011).
- [x] T011 [US2] P02 testar relocação, inacessibilidade, JSON inválido, links/destino em pacote, Unicode/relativos e falhas write/fsync/replace em `tests/viewer/test_source_config.py` (FR-005–011, FR-015, FR-017).
- [x] T012 [US2] P03 documentar formato, precedência, troca de disco e operação em outro computador no `README.md` e guia operacional da feature (FR-001–006, FR-016).

## Phase 5: User Story 3 — Preservar seleção explícita (P1)

Critério independente: source explícita funciona com configuração inválida;
no-config não lê arquivo; seleção vazia não vaza fontes para processo filho.

- [x] T013 [US3] P02 integrar resolução em serve/dossier, `--config`/`--no-config`, mantendo inspect em `packages/atlas/src/atlas_viewer/__main__.py` (FR-002–003, FR-013–014).
- [x] T014 [US3] P02 testar CLI/resolução e ausência de R4 em `tests/viewer/test_source_config.py` ou `tests/viewer/test_source_config_cli.py` (FR-002–003, FR-012–015, FR-017).
- [x] T015 [US3] P03 congelar seleção do subprocesso e preservar legado opt-in em `scripts/atlas_launch.py` (FR-008, FR-013–014).
- [x] T016 [US3] P03 testar Unicode, limite com adaptador, seleção vazia e precedência em `tests/viewer/test_native_notebook_source_config_launcher.py` (FR-005, FR-008, FR-013–014, FR-017).

## Phase 6: Review, publicação e handoff

- [x] T017 P00 integrar, criar/executar `scripts/qa/portable_source_config_smoke.py`, executar suites novas e regressões pertinentes via `scripts/run_checks.py`; registrar comandos/exit/ambiente/SHA no recibo da feature (FR-017–018).
- [x] T018 P01 revisar código P02/P03 sem autoria, executar contraprovas e registrar parecer real para `specs/008-portable-source-config/checklist.md` (FR-001–018).
- [ ] T019 P00 publicar commits da feature e PR Draft para development, observar CI e Codex Review elegível; registrar SHA e limitações no handoff (FR-018).
- [ ] T020 P00 entregar handoff autocontido para testes isolados Python/PowerShell 5.1/7 com pacote sintético, checkout seguro e recibo no Windows (FR-016–018).
- [ ] T021 Executor Windows executar posteriormente handoff e devolver recibo de configuração/relocação/instalação: `LOCAL_TEST_NOT_RUN` (FR-016–017; gate separado da implementação CHAT).

## Dependencies & Execution Order

T001–T004 precedem implementação. P02 (T005–007, T010–011, T013–014) e P03
(T008–009, T012, T015–016) trabalham em paralelo após API congelada. Dentro de cada
área, o mesmo owner mantém a sequência e suas dependências. P01 acompanha crosswalk.
T017 depende de ambas as frentes; T018 revisa a composição; T019 exige revisão e
testes relatados; T020 inclui SHA publicado; T021 é execução posterior no Windows.

## Implementation Strategy

Entregar primeiro configuração/reutilização, completar relocação e negativos,
então compatibilidade/subprocesso. Testes são funcionais com fixtures sintéticas,
sem obrigar RED fabricado. Guard histórico de apresentação mantém seus pins e
escopo; autorização da feature 008 não reescreve manifestos históricos.
