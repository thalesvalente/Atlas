# Contrato de reparo fora do ownership F3A

AP04-F3A-CHAT-GRAPH-01, PR Draft16. Este documento registra impedimentos observados; não altera ou concede autorização para editar controles históricos. O componente só pode receber prontidão isolada após CI focal e revisão próprios. Não há G5 PASS.

## Evidência observada em e56b2f3a406be52ab8edc33270834c1cf54c9d75

A revisão C leu os logs reais independentemente. Os gates não falham todos pela mesma razão:

| Controle | Run/job observado | Falha atribuída |
|---|---|---|
| AP04 documentação | run41173070367 / job124454926468 | Repair history contains unauthorized paths: docs/missions/atlas-parity-04/f3a-graph/INPUT-SHAS.json e PLAN.md |
| P06 | run41173070458 / job124454926557 | Mesma recusa do histórico/delta F2 |
| 003 | run41173070571 / job124454926848 | Mesma recusa do histórico/delta F2 |
| P03 portable/Spec | run41173070266 / jobs124454925579,124454925444 | Mesma recusa do histórico/delta F2 |
| ATLAS021 installed | run41173070357 / job124454925947 | Mesma recusa do histórico/delta F2 |
| C4 composição | run41173070379 / job124454925891 | C4_INPUT_SUMMARY: Composition may not add/remove inherited fixtures; nova fixture F3A é adição fora do inventário congelado |
| ATLAS021 source | run41173070357 / job124454926065 | Discovery inclui novo test_atlas_parity04_f3a_graph; browser não encontra pacote playwright (ERR_MODULE_NOT_FOUND); casos novos falham, sem substituir por skips |

Os IDs são localizáveis por https://github.com/thalesvalente/Atlas/actions/runs/RUN/job/JOB (substituir os inteiros da tabela). As mesmas famílias serão confrontadas novamente no HEAD terminal pelo fechamento externo da PR. Um erro posterior diferente não herda esta atribuição automaticamente.

## Ato mínimo do integrador/owner aplicável

Preparar missão autorizada de sucessor de controles que:

1. Fixe base F2 e HEAD F3A por SHA/tree/blobs e preserve os controles/manifests originais nos objetos históricos. Confronte a direção AP04-POR, ARC/ADRs, limites de F4 e todos os IDs herdados.
2. Admita o delta F3A exato (JS/CSS, cinco arquivos B e recibos enumerados), com ancestry de pai único e manifest completo, sem autorização genérica por diretório e sem legitimar alteração proibida depois revertida.
3. Distinga a fixture nova sintética do inventário histórico C4; preserve os blobs originais e execute seus oráculos em suas épocas apropriadas.
4. Qualifique a coleção e tooling novos realmente: manter todos os IDs antigos e novos sem skips/omissões; instalar Playwright e Chromium pinados no ambiente que executar os novos testes ou definir dispatch explícito com coleção provada. Não reduzir a regressão a contagens mínimas nem tratar ERR_MODULE_NOT_FOUND como recusa de autoria.
5. Execute Windows/Ubuntu normal/-O, SDK/viewer instalados e C4 browser conforme seus gates atuais no SHA sucessor e obtenha revisão independente desse SHA.
6. Somente depois avalie integração F4 e G5. Alteração de reader003/entrada File API, shell, distribuição ou demais controles exige ownership/autorização próprios; a prontidão do componente F3A não os altera.

F3A não escreveu workflows existentes, scripts globais, C4/P06/P03/AP04/F2, protocolo, reader003, shell ou R4. Não há bypass ou reclassificação de falhas como PASS. Nenhum merge/release/deploy/promoção é parte do reparo implícito.
