# Tasks — ATLAS021-A-POC-R4-FOCO01

Requisitos: [spec](spec.md). Plano: [plan](plan.md).
Caixa concluída significa evidência identificada; gates humanos são separados.

## Phase 1 — Setup

- [x] T001 ORQ revalidar baselines/issue2 e blobs em execution-log.md (FR-P08/10).
- [x] T002 ORQ executar helpers oficiais Spec Kit1.2.3 sem sobrescrever constituição; execution-log.md (FR-P10).
- [x] T003 ORQ especificar/clarificar/planejar delta em spec.md, plan.md e clarifications.md.
- [x] T004 A4 revisar requisitos/arquitetura em checklists/security-architecture.md e analysis.md.

## Phase 2 — US1 transporte demonstrável

- [x] T005 [P] [US1] A3 acrescentar comando persistente no namespace privado do adaptador e seus testes; destino existente deve ser recusado (FR-P01/NFR-P04).
- [x] T006 [US1] A3 registrar matriz observável e perdas no privado; ausência não é zero, UNKNOWN/HOLD não é aceite e tempo desconhecido fica ausente (FR-P02/05).
- [x] T007 [US1] A3 provar readback, imutabilidade e consumo em wheels instalados; recibos privados (FR-P03/NFR-P02).

## Phase 3 — US2 exploração e comparação

- [x] T008 [P] [US2] A2 fortalecer scripts/qa/browser.mjs para todos os runs/relações/ausências e par compatível por fonte (FR-P04/05).
- [x] T009 [US2] A2 documentar demo pública em README.md e guia público, usando produtor ambiental existente (FR-P07).
- [x] T010 [US2] A2/A3 executar UI pública e R4 nos ambientes respectivos, desktop/móvel e falha sem falso PASS (SC-P02/NFR-P04).

## Phase 4 — US3 evidência e revisão

- [x] T011 [P] [US3] A4 adicionar ID/tipo/ZIP de expansão controlada em tests/qa/test_poc_required_boundaries.py; 3 métodos normais/otimizados executados (FR-P06).
- [x] T012 [US3] ORQ executar regressões afetadas normal/-O e conferir perfil/ADRs; docs/verification/FOCO01-local.json (FR-P08/10).
- [x] T013 [US3] A4 revisar diffs finais em docs/reviews/A4-POC-FOCO01.md e parecer privado (FR-P08).
- [ ] T014 [US3] ORQ publicar branches/PRs Draft sucessoras, CI do par final e Codex por HEAD (POC_CI_REVIEW).
- [ ] T015 [US3] ORQ publicar recibo versionado AB-CONTRACT-1.0 no privado e handoff append-only à Frente B (FR-P09).
- [ ] T016 ORQ convergir matriz de requisitos/gates e entregar locators em convergence.md (SC-P04).

## Dependencies and parallel work

T001–T003 → T004. A2/A3/A4 examinam baseline e regressões existentes em paralelo;
novos checks refinam FR já definidos na feature001 e na missão.
T005–T007 privados e T008–T009 públicos são independentes; T010 depende de ambos.
T011 é negativa independente do harness. T012–T013 após integração; T014 fixa
o par publicado; T015–T016 fecham evidência. Só ORQ publica.
T014–T016 usam recibos append-only dos HEADs finais, sem ciclo de SHA autorreferente.

## Human gates outside these implementation tasks

ADR-0002/estabilização, licença/release, PR ready/merge, promoção canônica,
dados reais e atos físicos permanecem PENDING_HUMAN/NOT_APPROVED.
Não são tarefas de implementação incompletas a serem executadas pelo agente.
