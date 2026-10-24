# Tasks: ATLAS021 — candidata independente

Input: spec.md, plan.md, research.md, data-model.md e contracts/interface.md.
Checklist é qualidade de requisito; caixa de tarefa é trabalho efetivamente verificado.

## Phase 1 — Setup

- [x] T001 ORQ: revalidar capacidades/visibilidade e registrar bootstrap mínimo em docs/coordination/publication-policy.md.
- [x] T002 ORQ: instalar Spec Kit1.2.3 isolado e fixar estado em .specify/toolchain.json e .specify/feature.json.
- [x] T003 ORQ: registrar ARC-01–09 em .specify/memory/constitution.md, docs/architecture/ADR-0001-atlas-protocol-producers-storage.md e docs/coordination/AB-CONTRACT.md.

## Phase 2 — Foundational

- [x] T004 A1: pesquisar finalistas, pins/licenças e prova comparativa em research/protocol-options.md; ADR-0002 como proposta.
- [x] T005 A4: checklist independente da spec em specs/001-atlas021-protocol-interface/checklists/requirements.md e security-architecture.md.
- [x] T006 ORQ: analisar cobertura em specs/001-atlas021-protocol-interface/analysis.md e traceability.md antes da implementação UI.

## Phase 3 — US1: explorar fontes

- [x] T007 [P] [US1] A1: SDK/semântica/versões/contextos e limites em packages/protocol; validar sem instalar UI (FR-001/008/009/012/013).
- [x] T008 [P] [US1] A4: negativas e auditoria em scripts/qa/architecture_audit.py e tests/qa (FR-009/013/014).
- [x] T009 [US1] A2: CLI/servidor/snapshot imutável em packages/atlas/src/atlas_viewer (FR-001/002/007/019/020).
- [x] T010 [US1] A2: busca/filtros/estados/detalhe em packages/atlas/src/atlas_viewer/static (FR-002/003/012/015).
- [x] T011 [US1] A4: instalação wheel limpa sem R4/UI no SDK e fontes intactas em scripts/qa (FR-005/007/009/020, SC-001/005).

## Phase 4 — US2: comparar e apresentar

- [x] T012 [US2] A2: comparação por identidade/tipo/unidade, timeline e linhagem em packages/atlas/src/atlas_viewer/static/app.js (FR-004/005).
- [x] T013 [US2] A2: dossiê derivado, metadados e limites em packages/atlas/src/atlas_viewer (FR-006/012/014).
- [x] T014 [P] [US2] A4: navegador real teclado/mobile/XSS/sem rede em scripts/qa/browser.mjs (FR-013/015, SC-003/004).

## Phase 5 — US3: interoperar e reconstruir

- [x] T015 [P] [US3] A1: exportador ambiental independente em examples/environmental e seus testes (FR-010).
- [x] T016 [P] [US3] A3: adaptador privado aditivo, fixtures reais do reader e transformação em tools/atlas021 no repositório privado (FR-010/011).
- [x] T017 [US3] A4: validar ambos e abrir na mesma instalação, evidência privada sanitizada sem copiar corpus ao público (FR-010/011, SC-002).
- [x] T018 [US3] A2/A4: reconstrução, mudança detectada e IDs colidentes em tests/viewer e tests/qa (FR-007/019/020).

## Phase 6 — Cross-cutting

- [x] T019 ORQ: CI normal/-O Windows/Ubuntu e UI real em .github/workflows/atlas021.yml (FR-018).
- [x] T020 A4: revisão independente de arquitetura/conformidade/privacidade em docs/reviews (ARC-01–09).
- [ ] T021 ORQ: commits, PRs Draft e solicitação Codex no SHA final; evidências em docs/verification (FR-018, SC-006).
- [x] T022 ORQ/A3: A-DATA-REQUIREMENTS, disposição por IDs conhecidos e handoff privado em docs/coordination (FR-016).
- [x] T023 ORQ: convergência e marcos em specs/001-atlas021-protocol-interface/convergence.md (SC-001–006).
- [ ] T024 Operador: aceite humano da versão da ADR-0002 em docs/architecture (FR-017; PENDING_HUMAN, não bloquear protótipos autorizados).
- [ ] T025 Operador: promoção canônica do produto exato após paridade, release/rollback; PENDING_HUMAN e fora da candidata.

## Dependencies and parallel execution

T001–T003 → T004/T005 → T006. Pesquisa/protótipos públicos e inspeção privada são
independentes; implementação do contrato candidato e UI dependem de API acordada.
T007/T008/T016 em workspaces distintos; A2 usa API pública e dados próprios. T009–T013
são sequenciais no mesmo pacote. T011/T014/T017 são verificações independentes após
pacotes. T019–T023 após integração, correções e revisão; T024/T025 não são simuladas.

## Implementation Strategy

Provar leitura e fonte intacta, acrescentar comparação/apresentação, integrar produtores,
empacotar, testar independentemente e publicar Draft. Resolver falhas concretas;
não repetir E2E completa do produtor legado nem alterar arquitetura para acelerar.

## Evidence freeze before publication

T019 marks the workflow implementation, not a successful remote run. T021 remains open
until Draft PRs, CI and actual review are tied to the published SHA. T022 covers the
requirements/mapping/disposition deliverables with individual historical sources
UNKNOWN; receipt of B-INVENTORY is not fabricated. Final remote evidence is recorded
append-only in the PRs and private coordination handoff. T024/T025 remain human gates.

## Phase 7: Convergence

- [ ] T026 ORQ: concluir publicação Draft, executar CI e obter resultado real de review/Codex no SHA publicado per FR-018, SC-006, T021 (partial; HIGH).
- [ ] T027 ORQ: publicar handoff append-only com commits/árvores exatos, perfil/digest, consumidores e pendências per FR-016, SC-006, AB-CONTRACT-1.0 (partial; MEDIUM).
