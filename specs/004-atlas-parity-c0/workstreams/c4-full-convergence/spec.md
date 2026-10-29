# ATLAS-PARITY-03-C4R — convergência completa

## Objetivo e autorização

Compor C1/C2/C3 por SHA em branch própria e PR Draft. L2_BLOCKED_EXACT é terminal e satisfaz a entrada de engenharia; o gate operacional do host permanece separado. Max solicitado pelo operador; seletor não observável pelo agente, REASONING_EFFECTIVE=UNVERIFIED.

## User Scenarios & Testing

US1: Ao selecionar uma execução no shell C0, a pessoa consulta metadados existentes e escolhe explicitamente métricas/parâmetros para uma tabela derivada. Fonte, snapshot e identidade declarada distinguem IDs repetidos. display_value, booleanos, ausências, unidade e precisão conservam seu significado.

US2: Navegação por hash, filtros, teclado, foco e troca de pacote conservam o binding global de snapshot; contexto expirado é desmontado e requer nova seleção. Erro de apresentação fica visível sem modificar validade/fonte.

US3: O revisor confere corpus P01/C3 e provas de Windows/Ubuntu normal/-O no próprio SHA composto. O estudo C ausente e o denominador legado completo continuam desconhecidos.

## Requirements

FR-C4-01: Preservar ancestry de C1 326b92ae27effb6941801ed3e9af5c07aa90fb95, C2 f625f8be40156fd9fe4572a0ac2074910efd96cf e C3 c0b42a17710fdf3cef3ec4ea13c840796d57d18f, sem squash/rebase.
FR-C4-02: Importações explícitas; allowlist exata; montagem/desmontagem controladas; read_model já validado.
FR-C4-03: Exibir só metadados existentes e tabelas descartáveis de propriedades escolhidas; File continua File e mentions neutra.
FR-C4-04: Manter produto/documento ricos p03-candidate/1, tabela persistida universal e coverage ledger persistido fora do app principal.
FR-C4-05: Preservar packages/protocol, schemas/contexto/versão/exportador/carrier, fixtures e fontes herdadas.
FR-C4-06: Exigir CI própria do SHA, zero skips, wheels fora checkout, SDK sem viewer/R4, viewer sem R4, regressão C1, P01/C3, P03 focal e browser integrado.
FR-C4-07: Atribuir recibos L2 somente ao C1; LOCAL_C4_* = NOT_RUN e HOST_OPERATIONAL_READINESS=false. Não executar o host nem repetir loopback nesta missão.
FR-C4-08: Revisão independente real sem autoria, inclusive todos bytes C3 incorporados, matriz, workflow e recibos.

## Success Criteria

SC-C4-01: Gates completos e revisão final sem finding bloqueante no SHA C4, com artifacts identificados por SHA.
SC-C4-02: C4_FULL_CANDIDATE_READY_HOST_GATE_DEFERRED permite somente handoff/revisão humana. PR Draft, sem merge/release/deploy/promoção/ciência.
