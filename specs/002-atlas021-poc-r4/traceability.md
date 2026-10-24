# Traceability — PoC focal

| Requisito | Tarefas | Código/documento | Evidência/gate |
|---|---|---|---|
| FR-P01 | T005 | comando persistente privado | POC_R4_EXPORT |
| FR-P02/05 | T006/T008 | mapa privado; browser.mjs | equivalência/ausência/estados |
| FR-P03 | T007/T012 | clean_install.py; worker privado existente | POC_ATLAS_IMPORT |
| FR-P04 | T008/T010 | browser.mjs | POC_UI_R4 |
| FR-P06 | T011/T012 | test_poc_required_boundaries.py + regressões existentes | POC_NEGATIVE_TESTS |
| FR-P07 | T009 | README/guia demo pública | POC_SCOPE_LOCK |
| FR-P08 | T001/T012–T014 | recibos locais, PR/CI/review por SHA | POC_CI_REVIEW |
| FR-P09 | T015 | JSON versionado privado + recibo da publicação | POC_HANDOFF_B |
| FR-P10 | T002/T004/T012 | constituição, ADRs, digests preservados | POC_SCOPE_LOCK |
| NFR-P01 | T010/T012/T014 | matriz CI e Playwright | plataforma/modo/versão exatos |
| NFR-P02 | T007/T011 | worker/hash/leitor limitado | fontes intactas e loopback |
| NFR-P03 | T011/T012 | reaproveitamento provas da feature001 | cobertura proporcional |
| NFR-P04 | T005/T008/T010 | saídas de erro dos runners | nenhuma falha rotulada PASS |

ARC-01/02/04: produto/SDK não mudam; adaptador privado separado.
ARC-03/05: instalação limpa, índice reconstruível, duas fontes.
ARC-06: tipos, estados, ausências e autoridade do dossiê verificados.
ARC-07/08/09: nenhum ato físico, promoção ou mudança arquitetural.
