# Tarefas P01

Sintaxe de checklist aplicada do template Spec Kit 1.2.3. `[P]` indica arquivos
distintos; não concede escrita em outro workstream. IDs globais são qualificados por
`P01/` no handoff para evitar colisão com tarefas dos outros owners.

## Fase 1 — Base e desenho

- [x] T001 [US1] Fixar baseline/constituição/ADR/recibo em `docs/missions/atlas-parity-02/p01-contracts/EVIDENCE-REGISTER.md` (FR-P01-001).
- [x] T002 [P] [US1] Inventariar estudos e hashes em `docs/missions/atlas-parity-02/p01-contracts/INPUT-INVENTORY.json` (FR-P01-002).
- [x] T003 [US4] Aplicar spec/clarificações/plano/checklist no workstream e executar helpers com no-persist (FR-P01-011).

## Fase 2 — Pacote documental

- [x] T004 [P] [US1] Mapear capacidades nas sete camadas em `docs/missions/atlas-parity-02/p01-contracts/CAPABILITY-PARITY.csv` (FR-P01-003).
- [x] T005 [P] [US2] Redigir identidade, entidades, relações e tempo em `docs/contracts/atlas-parity-02/p01/PRESENTATION-CONTRACTS.md` (FR-P01-004,005,006).
- [x] T006 [P] [US3] Redigir cobertura/denominadores em `docs/contracts/atlas-parity-02/p01/COVERAGE-CONTRACT.md` (FR-P01-007).
- [x] T007 [US2] Classificar decisões e tarefas de outros owners em `docs/missions/atlas-parity-02/p01-contracts/DECISIONS-AND-GAPS.md` (FR-P01-008,009).

## Fase 3 — Executar e verificar

- [x] T008 [US3] Criar casos esperados e validar exemplos em `docs/contracts/atlas-parity-02/p01/examples/` e `validate_examples.py` (FR-P01-008,010).
- [x] T009 [US3] Executar prova focal do leitor vigente e verificar hashes/ownership no diretório `docs/missions/atlas-parity-02/p01-contracts/verification/` (FR-P01-010,012).
- [x] T010 [US4] Realizar revisão nativa independente sem autoria e registrar findings/fechamento em `docs/missions/atlas-parity-02/p01-contracts/INDEPENDENT-REVIEW.md` (FR-P01-011).

## Fase 4 — Convergir e entregar

- [ ] T011 [US4] Convergir spec/plano/tarefas e emitir RESULT/HANDOFF/MANIFEST em `docs/missions/atlas-parity-02/p01-contracts/` (FR-P01-012).
- [ ] T012 [US4] Publicar candidata em commit e PR Draft somente no Atlas e verificar estado remoto final (FR-P01-012).

## Dependências

T001–T003 antecedem a análise. T004, T005 e T006 são paralelizáveis por ownership.
T007 depende da leitura do código/contratos. T008 depende da semântica explicitada;
casos esperados são escritos antes do validador. T009 → T010 → T011 → T012.
Tarefas propostas a P02–P06 ficam em DECISIONS-AND-GAPS, com estado HANDOFF_PROPOSED;
não serão marcadas concluídas por P01.
