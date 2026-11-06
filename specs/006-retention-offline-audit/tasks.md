# Tasks — Feature 006 / N02

## Phase 1: Recovery and contract

- [x] T001 Recuperar branches, PRs, commits e recibos; documentar escopo em spec.md.
- [x] T002 Executar helpers Spec Kit e definir contrato em contracts/local.md.
- [x] T003 Verificar N03, aceites A01/T015, CI e review sem reexecução.

## Phase 2: US1 — Importação vinculada

- [x] T004 [P] [US1] Registrar RED de componente ausente em scripts/qa/test_retention_audit.mjs.
- [x] T005 [US1] Validar plano/snapshot/inventário e lexemas em tools/atlas_retention_audit.mjs.
- [x] T006 [P] [US1] Exercitar positivos e contradições na suíte scripts/qa/test_retention_audit.mjs.

## Phase 3: US2 — Leitura física delimitada

- [x] T007 [US2] Implementar CLI e resolução física autorizada em tools/atlas_retention_audit.mjs.
- [x] T008 [P] [US2] Provar negativos FS e proteção de compartilhamento/backup em scripts/qa/test_retention_audit.mjs.

## Phase 4: US3 — Composição e qualificação

- [x] T009 [P] [US3] Adicionar matriz Windows/Ubuntu em .github/workflows/atlas-retention-audit.yml.
- [x] T010 [US3] Revisar independentemente produto/contrato e corrigir findings em tools/atlas_retention_audit.mjs.
- [x] T011 [US3] Compor N02/N03 e executar prechecks de domínio, integração, negativos e A01/F005; browser terminal em G13.
- [x] T012 [US3] Convergir spec/plan/tasks/código/testes e registrar em validation.md.

## Gates externos terminais

G13 — publicar branch própria/PR Draft e qualificar Actions no SHA composto.
G14 — Codex Review no SHA composto e tratamento dos findings materiais.
G15 — handoff LOCAL com SHA/tree/comandos e limites do inventário privado.

Esses gates terão recibo externo posterior ao commit; não se afirma PASS antes de
execução e não se altera SHA revisado apenas para atualizar caixas. Aceite humano
LOCAL e corpus real não são tarefas executáveis no CHAT.

## Dependencies and parallel work

T001→T002; T003 em paralelo à recuperação; T004→T005; T006/T008 por owner de testes;
T007 depende contrato; T009 separado; T010 após código; T011 após N02 e N03 qualificadas;
T012 após testes; G13/G14 podem ocorrer em paralelo no mesmo SHA; G15 depois.
