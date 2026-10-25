# Análise pré-implementação — REUSE-01

FR-01/02 → R002/R005/R006: prova deve usar API real do produtor; parser próprio não comprova reaproveitamento.
FR-03/05 → R007: preservação de campos selecionados, perdas explícitas, referências não reabertas, sem aprovação científica.
FR-04 → barreira público/privado e ensaio do viewer sem produtor instalado.
FR-06 → R005/R007/R008: fixtures sintéticas pelo pipeline original, SDK público e CI por SHA.
FR-07 → R006/R010: pacote pequeno e nenhum clone/worktree no host.

Não há desvio de arquitetura. A direção anterior de ler diretamente o índice por outro parser foi supersedida para esta candidata ainda não integrada. O histórico Git conserva os resultados anteriores; novos testes devem demonstrar a substituição.

## Análise pré-implementação CLOSE01 — 2026-10-25

| Requisito | Tarefas | Teste/evidência prevista |
|---|---|---|
| FR-14 | T023–T025 | RED instalado; seção separada no navegador |
| FR-15 | T024–T027 | objeto/lista, repetição/ordem, IDs iguais entre fontes |
| FR-16 | T024/T026/T027 | alvo ausente rejeitado; digest declarado/calculado, payload ausente |
| FR-17 | T024–T027 | lista ausente/vazia, mistura de relações e estados preservados |
| FR-18 | T025–T027 | HTML/URI como texto, navegação interna da mesma fonte, zero acesso externo |
| FR-19 | T025/T027 | foco/teclado, IDs longos, 390 pixels/200%, captura real |
| FR-20 | T024/T026–T028 | pacote antigo, reconstrução, bytes iguais, instalação sem R4, normal/-O |
| FR-21 | T021/T028/T029 | recibos históricos e novo SHA; tabela de integração e decisão humana |
| SC-04–07 | T023–T029 | RED/GREEN, navegador, isolamento/bytes e publicação/revisão |

Cobertura: 8/8 requisitos novos e 4/4 critérios associados a tarefas. Nenhuma
ambiguidade essencial, duplicação material ou conflito com ARC-01–09. Nenhuma tarefa
nova sem requisito. A análise é somente leitura; este registro foi consolidado pelo
coordenador na documentação autorizada. Implementação liberada após RED real; nenhum
teste ou checkbox documental é tomado como resultado antecipado.
