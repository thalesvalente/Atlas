# Decisão de integração — P06
**P06_QA_READY_AWAITING_INPUTS**. A entrega concreta é a branch QA da PR Draft #6.
Não existe candidata de composição nesta execução. A última consulta de entradas
em 27/10/2026 11:45:07 America/Fortaleza encontrou main fixa, quatro branches
históricas, P06 e somente a PR #6 aberta; não recebeu handoff P02.

Menor conjunto coerente selecionado: P02 + P06, sob o contrato vigente.
P01/P03 entram somente se recebidos, compatíveis e necessários; sua ausência
não bloqueia C0 artificialmente. Nenhuma branch em movimento foi integrada.
O SHA do código QA P06 consta explicitamente em INPUT-SHAS.json e deve entrar
na composição futura, incluindo testes, workflow e agregadores reais.

| Dimensão | Decisão |
|---|---|
| CODE_CANDIDATE_VERIFIED | FALSE — candidata composta não criada; QA baseline tem provas próprias por SHA |
| CI_FINAL_SHA | Novo commit documental deve ter status próprio; ver recibo externo da PR |
| BROWSER_ENGINEERING | Baseline e cenário adicional d21 PASS_SCOPED em Chromium de engenharia |
| REAL_COHORT_PACKAGE | INPUT_MISSING/P04, sem execução |
| LOCAL_BASELINE_OPERATION | NOT_RUN_BY_P06; recibo LOCAL-REAL01 anterior é atribuído |
| FINAL_CANDIDATE_ON_USER_HOST | NOT_RUN |
| HUMAN_PROMOTION | NOT_AUTHORIZED_NOT_RUN |

A ADR-0002 v1.0 já foi aceita como direção de estabilização na PR #5/recibo
6406839421; preservar os bytes históricos, sem pedir o aceite novamente.
Aceite de direção não é release, aprovação científica, promoção canônica ou
autorização de formato novo.

Próxima ação mínima: receber handoff sanitizado P02 com SHA/tree/paths/testes;
congelar essa entrada junto do SHA QA P06, compor em branch candidata própria,
testar os bytes compostos e obter nova revisão independente. Não repetir estudos
encerrados nem esperar continuamente pelas outras frentes. Resultado terminal
pendente de CI será identificado por run/SHA, sem simulação de PASS.
