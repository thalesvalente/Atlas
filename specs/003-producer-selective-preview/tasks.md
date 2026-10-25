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
- [ ] T020 Obter QA/semântica independentes e publicar somente recibos sanitizados por PR pertinente; registrar revisão por SHA em convergence.md (FR-12, FR-13).

Dependências: T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020. Revisores reais somente leitura podem trabalhar em paralelo; coordenador é único escritor. MVP: US1 seguida da conferência de US2. Falha de aquisição bloqueia T017/T018; não fabricar pacote nem visualização. R011 é o gate histórico retomado por estas tarefas; R012 continua fora da autorização de execução.

T020: QA e semântica locais concluídos no escopo declarado. Publicação final e revisão externa do novo HEAD documental são conciliadas por recibo append-only da PR após o commit; não se antecipa revisão externa por checkbox.
