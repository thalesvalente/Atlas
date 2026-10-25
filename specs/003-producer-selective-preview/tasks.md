# Tarefas — correção REUSE-01

## Especificação e desenho
- [x] R001 Conferir direção do usuário e ARC-01–09; manter ADR-0002 pendente.
- [x] R002 Comparar APIs legadas e identificar duplicação no adaptador anterior.
- [x] R003 Atualizar spec, clarificações, pesquisa, plano, dados, contrato e checklist.
- [x] R004 Analisar consistência entre fronteiras, retenção e interoperabilidade.

## Execução e convergência técnica
- [x] R005 Registrar teste RED da ponte exigida sobre a baseline, com recibos privados.
- [x] R006 Implementar adaptador privado sobre projeção existente e superseder o leitor paralelo sem I/O.
- [x] R007 Provar SDK/viewer independentes, origem preservada no ensaio e limites semânticos.
- [x] R008 Executar helpers oficiais e CI focal, com SHAs/ambientes explícitos.
- [x] R009 Obter revisão independente da implementação e da especificação; registrar escopo por SHA.
- [x] R010 Publicar convergência e guia revisado, sem atribuir os resultados a dados reais.

O fechamento documental não altera SDK/viewer/perfil. CI/review posteriores deste commit documental são registrados de forma append-only na PR; não se atribui antecipadamente a eles o PASS da implementação anterior.

## Gates separados e ainda abertos
- [x] R011 Aquisição e piloto no host real executados no incremento LOCAL-REAL01; limites e resultado genérico em convergence.md.
- [ ] R012 ADR-0002, merge e promoção: decisões humanas separadas.

## Phase 1: LOCAL-REAL01 — preparação delimitada
- [x] T013 Reconfirmar revisões, checkout limpo, runtime e controles de origem; registrar proveniência em evidência local ignorada (FR-08, FR-09, FR-12).
- [x] T014 Documentar o delta operacional em spec.md, plan.md, clarifications.md e checklist; executar helpers oficiais sem persistir feature (FR-08–13).

## Phase 2: LOCAL-REAL01 — US1 aquisição e conversão
- [x] T015 [US1] Determinar a menor rota existente de aquisição e seu alcance; registrar chamada ou bloqueio em evidência local ignorada (FR-08, FR-13).
- [x] T016 [US1] Verificar distribuição privada e imports por manifesto, preservando instalação pública (FR-09).
- [x] T017 [US1] Capturar projeção operacional e converter a seleção exata em pacote novo; preservar mapeamentos/perdas no manifesto (FR-10, FR-12).

## Phase 3: LOCAL-REAL01 — US2/US3 consumo e fechamento
- [x] T018 [US2] Validar pacote com SDK/CLI instalados e conferir tela, estados e lacunas, registrando limites em evidência local ignorada (FR-11).
- [x] T019 [US3] Entregar comando de repetição e gestão da instância loopback, com evidência delimitada da estabilidade das fontes/runtime (FR-09, FR-13).
- [x] T020 Obter QA/semântica independentes e publicar somente recibos sanitizados por PR pertinente; registrar revisão por SHA em convergence.md (FR-12, FR-13).

Dependências: T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020. Revisores reais somente leitura podem trabalhar em paralelo; coordenador é único escritor. MVP: US1 seguida da conferência de US2. Falha de aquisição bloqueia T017/T018; não fabricar pacote nem visualização. R011 é o gate histórico retomado por estas tarefas; R012 continua fora da autorização de execução.

T020: QA e semântica locais concluídos no escopo declarado. Publicação final e revisão externa do novo HEAD documental são conciliadas por recibo append-only da PR após o commit; não se antecipa revisão externa por checkbox.

Conciliação CLOSE01: T020 fechada com recibo LOCAL-REAL01 #5#issuecomment-6404206290,
Codex #5#issuecomment-6404222103 e CIs 40239890476/40239890514. SHAs e escopos exatos
em `convergence.md`; não houve repetição do piloto.

## Phase 4: CLOSE01 — especificação e prova inicial

- [x] T021 Reconciliar piloto/T020 e requisitos FR-14–21 em spec.md, plan.md e convergence.md.
- [x] T022 Analisar contrato e qualidade em data-model.md, contracts/reader.md, checklists/requirements.md e analysis.md antes do código.
- [x] T023 [US4] Registrar RED real da omissão na baseline instalada em tests/viewer/test_related_references.py (FR-14, SC-04).

## Phase 5: CLOSE01 — US4 referências relacionadas

- [x] T024 [P] [US4] Acrescentar related_references em packages/protocol/src/caderno_protocol/read_model.py; resolução exclusiva no pacote, primeira ordem e observações sem promoção (FR-14–17).
- [x] T025 [P] [US4] Renderizar seção/estado vazio com identidade da fonte e texto inerte em packages/atlas/src/atlas_viewer/static/app.js e style.css (FR-14–19).
- [x] T026 [US4] Provar casos semânticos, negativos, identidade, reconstrução e bytes em tests/viewer/test_related_references.py, com consumidor instalado sem R4 (FR-15–20, SC-04/06).
- [ ] T027 [US4] Exercitar teclado, foco, 390 pixels e 200% em scripts/qa/browser.mjs, scripts/ci/run_browser.py e fixture sintética; publicar captura/recibo da CI pelo HEAD (FR-18–20, SC-05).

## Phase 6: CLOSE01 — revisão e convergência

- [ ] T028 Executar helpers oficiais e gates Windows/Ubuntu normal/-O em .github/workflows/atlas003-speckit.yml e atlas021.yml; testar opt-in estrito em scripts/qa/speckit_audit.py e tests/qa/test_speckit_presentation_audit.py, registrando SHAs reais (FR-20/21).
- [ ] T029 Revisar independentemente o delta, tratar achados e atualizar convergence.md, resumo/recibo da PR #5 e decisão da cadeia/ADR-0002 sem aceitá-la (FR-21, SC-07).

Dependências novas: T021 → T022 → T023 → T024/T025 → T026/T027 → T028/T029.
A escreve somente read_model.py; B testes/fixture/scripts de navegador e atlas021.yml;
coordenador UI/docs/atlas003-speckit.yml/Git; C somente revisão. Nenhuma escrita
concorrente nos mesmos arquivos. MVP é US4; tarefas históricas não são reexecutadas.

T027–T029 têm implementação/harness entregues e revisão nativa pré-publicação;
seu fechamento depende das evidências pós-commit. O recibo append-only CLOSE01 na
PR #5, por SHA integral, registra o resultado final sem gerar commit apenas para
checkbox/PASS. Ver `convergence.md` para alcance e estados reais.

## Phase 7: Convergence — reflow em 200%

- [ ] T030 [US4] Diagnosticar a geometria do transbordamento em 200% no navegador da CI em scripts/qa/browser.mjs e corrigir somente o layout responsável em packages/atlas/src/atlas_viewer/static/style.css; conservar o gate e obter prova visual final (FR-19/SC-05, partial).
