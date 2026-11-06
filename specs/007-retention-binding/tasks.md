# Tasks — Feature 007

## Setup e contrato

- [x] T001 Reconciliar SHA, owners, refs e exportador em `specs/007-retention-binding/plan.md`.
- [x] T002 Especificar a interface e suas premissas em `specs/007-retention-binding/contracts/local-inventory.md`.

## US1 — Reconciliação autenticada

- [x] T003 [US1] Rodar RED do plano publicado, identidade adulterada, revisão, UID e pin em `tests/atlas_retention_binding/test_binding.py`.
- [x] T004 [US1] Validar contrato, identidade lexical e cadeia em `tools/atlas_retention_binding/plan.py` e `tools/atlas_retention_binding/inventory.py`.

## US2 — Resolução sob raízes autorizadas

- [x] T005 [US2] Rodar RED de caminhos, arquivos ausentes, links e aliases em `tests/atlas_retention_binding/test_binding.py`.
- [x] T006 [US2] Implementar leitura ancorada em `tools/atlas_retention_binding/filesystem.py` e nos adaptadores da plataforma.

## US3 — Proteção e relatório

- [x] T007 [US3] Rodar RED de proteção, dependências, backup e estimativa em `tests/atlas_retention_binding/test_binding.py`.
- [x] T008 [US3] Entregar o relatório e a CLI em `tools/atlas_retention_binding/__main__.py`.

## Qualificação

- [x] T009 Executar GREEN normal e otimizado em Windows e Ubuntu conforme `specs/007-retention-binding/quickstart.md`.
- [x] T010 Qualificar negativos de substituição, desvio de raiz e duplicidade de evidência em `tests/atlas_retention_binding/`.
- [ ] T011 Verificar Actions e solicitar uma Codex Review no head da Draft conforme `specs/007-retention-binding/plan.md`.
- [ ] T012 Entregar o handoff com SHA, tree, evidências e lacunas para LOCAL conforme `specs/007-retention-binding/contracts/local-inventory.md`.

T001 → T002 → RED (T003, T005, T007) → T004 → T006 → T008 → T009–T010 → T011–T012. Resultados externos ficam no recibo do SHA candidato.
