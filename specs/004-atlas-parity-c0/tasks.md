# Tarefas P06
## Phase 1: Contrato e preparação
- [X] T001 Conferir base/tree, PR #5, contratos e ausência inicial de inputs (FR-001/007).
- [X] T002 Reservar 004 nos agregadores e escrever spec/plan/checklist/análise (FR-008).
- [X] T003 Separar compatibilidade, autoria de testes e revisão nativa independente (FR-006/007).

## Phase 2: QA material
- [X] T004 Implementar invariância e contraprovas de corrupção/adição/remoção (FR-001/006).
- [X] T005 Implementar cenários semânticos sobre APIs reais e fixtures sintéticas (FR-002/003).
- [X] T006 Implementar prova wheel/HTTP e workflow por SHA com helpers reais (FR-004/005).
- [X] T007 Obter e registrar resultado terminal dos testes/CI nos bytes novos (FR-005).

## Phase 3: Fechamento
- [X] T008 Obter revisão independente real do delta final e resolver findings (FR-006/007).
- [X] T009 Fazer consulta final; compor apenas se houver entradas necessárias concretas (FR-007).
- [X] T010 Publicar resultado, inputs, matriz, decisão, handoff e manifesto sanitizados (FR-008).

Checkbox de implementação não declara execução PASS. Pendências externas devem
ser registradas com run/SHA exatos; ausência de inputs não exige espera contínua.

## Phase 4: Convergence
- [X] T011 Fechar a lacuna FR-002 de pacote válido trocado/links obsoletos com
  scripts/qa/atlas_parity02_p06_browser.py e .mjs e chamada explícita em CI.
  Revisão estática PASS_SCOPED no d21; execução PASS_SCOPED pertence ao run 40523433530,10 checks.


## Phase 5: Convergence — ATLAS-PARITY-03-C1

T001–T011 acima são recibos históricos da frente P06, atribuídos aos seus SHAs.
Esta fase registra os gaps recebidos pela composição C1, sem reescrever aqueles IDs.

- [X] T012 Congelar P02/P06 por SHA/tree/manifests e preservar ancestry por merge (FR-007; missing).
- [X] T013 Reparar auditoria com autorização exata dos três blobs P02 e negativas de governança/protocolo (FR-001/006; partial).
- [X] T014 Reparar H06-01/02/03 por identidade fonte+ID, métrica e coluna (FR-002/003/009; partial).
- [X] T015 Conectar consumidor externo, coleção zero-skips e browser P02 com fontes/recibos (FR-004/005/010; missing).
- [X] T016 Validar agregadores 004 e helpers oficiais sem ponteiro concorrente (FR-011; partial).
- [X] T017 Executar todos os gates no SHA composto e resolver RED reproduzível P06 sem alterar runtime congelado (FR-005/009; partial).
- [X] T018 Obter revisão independente por SHA e publicar os oito artefatos finais, distinguindo recibo externo do commit autorreferente (FR-007/008; partial).

### Recibo de convergência C1

T017 concluída no código `af393e4c0cca19161f49bf9d847bd22617be15fb`, com os três workflows SUCCESS e cinco jornadas browser. T018 registra a revisão independente desse código e esta publicação dos oito artefatos. O commit documental que contém o recibo requer sua própria revisão por SHA e novos runs; essa confirmação terminal é externa na PR #11, sem atribuir resultados entre SHAs.
