# Tarefas da convergência 18/18

Ledger desta missão, owner P00. Os ledgers originais das Features 001/004 e seus
estados históricos permanecem intactos. O guard real recusou append na baseline
protegida da Feature 001; suas regras e pins não foram ampliados. Esta rastreabilidade
equivalente atende ao escopo de bugfix sem reescrever os planos anteriores.
As marcações abaixo registram código e oráculos entregues/testados no escopo
de código-fonte; a qualificação de instalação/browser/CI pertence ao gate O4
do recibo terminal, sem PASS antecipado.

- [x] C18-T001 Validar a cadeia física, a origem efetiva e o cache dos três módulos do produtor antes da execução no adaptador externo; preservar namespaces/imports relativos legítimos e restaurar `sys.path`, com regressões sintéticas normal/-O em `tests/viewer/test_native_notebook_producer_origin.py`; 004 FR-001/006, ARC-07 (contradicts; HIGH). Guarda de origem, sem sandbox ou reativação O1.
- [x] C18-T002 Vincular seleção, detalhe e preferências de projeto/experimento ao snapshot do catálogo; invalidar todo o contexto em rebuild/reinício e preservar simples GET de verificação; `scripts/qa/test_protocol_snapshot.mjs` e oráculo de browser instalado em `browser.mjs`, 001 FR-007/019/020 (partial; HIGH).
- [x] C18-T003 Serializar GET/POST, preservar reindexação solicitada durante consulta e recuperar a fila após falha; 001 FR-007/020 (contradicts; HIGH).
- [x] C18-T004 Distinguir indexação, consulta e publicação declarada; reconciliar README com os recibos humanos exatos; 001 FR-005/012/017 (partial; MEDIUM).

O0 → três frentes O1 → matriz/revisão O2 → C18-T001–004 por P00 → três revisores
não autores + CI no SHA publicado → portabilidade/recibo terminal. Testes de
código-fonte no Chat não são instalação de wheel nem execução de Chromium.

O recibo terminal da PR qualifica o SHA completo depois da revisão não autora e
dos Actions; não se marca gate humano como cumprido por teste sintético.
