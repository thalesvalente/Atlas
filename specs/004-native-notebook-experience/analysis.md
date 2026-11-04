# Feature 004 — análise de consistência e revisão

## Escopo entregue

O caminho principal agora é `Caderno → API original project() do produtor → exportador externo → File de apresentação no pacote Caderno existente → API nativa → DOM/SVG/P03`. Não é um iframe nem cópia do renderer privado. A rota transitória /original passa a ser uma orientação inerte: executar HTML selecionado não é necessário para a integração e os findings de navegação/exfiltração desse caminho são eliminados removendo sua execução. O R4, seu launcher e seus HTMLs no host não são removidos.

## Rastreabilidade

| Requisito | Implementação | Evidência de engenharia |
|---|---|---|
| FR001–003 / US1 | tools/export_native_notebook.py; import da instalação escolhida; native-view como File | test_native_notebook.py: protocolo normal, ZIP/diretório e reconstrução; scripts oficiais Spec Kit |
| FR004–005 | native_values.py; pointers/raw_json; UIDs por ocorrência | teste de null explícito, número 9007199254740993, missing/null, duplicidades e display adulterado |
| FR006–007 | native_notebook.py e server.py; fontes fixas, digest, quotas e Catalog compartilhado | HTTP origem/Host/caminho, payload alterado, pacote substituído válido e reindexação explícita |
| FR008–009 / US2 | native_notebook.js, native_graph.js, P03 por blob | Chromium instalado: navegação, 1202 nós, zoom/minimapa, duas fontes, 127 linhas, CSV/JSON, mobile |
| FR010 / US3 | launcher, quickstart, tasks, Actions | PowerShell parse Windows; CI normal/-O; revisão Codex; host real separado |

Os números acima são dados inventados de engenharia para testar escala e fidelidade, não contagens do Caderno privado. O fluxo operacional não contém flag synthetic. As referências documentais externas são consultáveis como metadados, não abertas automaticamente pelo servidor.

## Execução e revisão observadas

No SHA técnico 38f566bc7b519e97a5b42665794c83196af2a99d: native run41387198946 (5jobs), ATLAS021 run41387198953 (6jobs) e Spec Kit run41387198967 (2jobs) concluíram sucesso. Setup_plan.py, setup_tasks.py, check_prerequisites.py foram realmente executados sem alterar a feature global. O sucessor que contém este relatório exige a própria CI; o SHA/run final fica no recibo da PR23, não é herdado deste resultado.

Codex (`chatgpt-codex-connector`, autoria distinta) apontou no código nativo: native_id null convertido indevidamente (#4438861028) e duplo clique interrompido pela troca do nó (#4438861030). As correções preservam null, recalculam o display do raw_json e mantêm DOM por UID/delegação. Copilot identificou promoção silenciosa de fonte alterada (#4438857400); snapshot/export agora usam o Catalog antes/depois e exigem reindexação explícita. Links de navegação externa à view não recebem a classe funcional nav-button, corrigindo Ctrl+clique que apagava o painel de origem (#4438687850). Todos têm contraprovas, não apenas afirmações documentais.

## Reuso e preservação

P03: JS f4c2bab174576caf9a6a5d564cb34f0483f0e316 e CSS 0fe2568ec80e40825bcd3e08e0d1eade09d03c5f, de ead1f753f52f22035326b7366dd2231c62775765; bytes reutilizados. O manifesto e a frente originais não são alterados. R4 project() é chamado externamente, não incorporado ao wheel. Nenhuma alteração de packages/protocol, ADR, feature.json, dados reais ou PRs de outros owners. Não houve subagente nativo: NATIVE_SUBAGENTS_NOT_AVAILABLE, writer único sequencial.

## Limites e gates históricos do primeiro ciclo

A estrutura genérica conserva todas as coleções e valores, mas não confere automaticamente equivalência visual/operacional de todo link do Caderno privado. R4 project() é uma dependência operacional confiável do host escolhido; esse ramo não foi executado contra H: neste CHAT. Nenhuma leitura/cópia do corpus para Actions é autorizada. T016 permanece NOT_RUN. A revisão terminal deve examinar o sucessor corrigido; COMMENTED com findings não é aprovação e T015 fica pendente até parecer verificável sem achado material. CI verde qualifica a implementação no escopo executado, não promoção/migração/retirada.

## Reconciliação ATLAS-FINAL-CLOSE — 2026-11-03

O estado histórico acima foi superado pela prova observada do fechamento, sem
apagar seus limites. P01/P02/P03 executaram como agentes nativos reais com áreas
exclusivas; P04 reconciliou alternativas C2-B/C2-K e P05 executou QA não autora.
Um integrador aplicou commits por cherry-pick -x, sem merge de Draft.

No código efad09dfaeaadd93da87a4c64979f80b9678caa6: CI 41750468698 (5/5),
41750468913 (6/6) e 41750469060 (2/2) SUCCESS; Codex 6619316900 completed,
has_any_findings=false/has_unresolved_findings=false. P05 conferiu instalação
independente, 119 testes por modo normal/-O (118 PASS/1 SKIP), 12 grupos no
Caderno real, 21 casos de viewport e exports integrais/exatos. Três findings
foram efetivamente reproduzidos e corrigidos: fallback de chave composta,
namespace divergente entre grafo/detalhe e callback da busca global da árvore.

A referência visual usa os assets originais e o mesmo snapshot em composição
local privada, não um build oficial novo do legado. O HTML histórico existente
tinha revisão anterior e não foi usado como denominador. P05 e coordenação
inspecionaram imagens reais desktop/mobile; a jornada contextual completa foi
executada sem inventar vínculos, inclusive retorno à ocorrência original.

O encerramento daquele ciclo alterou somente documentação. Exige atestação de igualdade dos
bytes executáveis e suas próprias Actions/Codex no HEAD final, publicados na
PR #25. T015/T016 e R006/R010/R012/R014/R016 estão reconciliadas na matriz
[final-close.md](final-close.md); aceite humano permanece separado.

## Composição final de grafo e aplicação — 2026-11-04

O código 0cd96bce6f275a187ed2baf790793b77b5ae18e3 sucede os recibos históricos.
PR26/PR27 e correções por owner foram integradas com autoria/cherry-pick -x.
Foram corrigidos a medição quadrática de labels, foco em acionadores recriados
e treeitems, callbacks pendentes após fechar e paginação de alvos contextuais.
A API adicional cancelPendingSelection() cancela apenas notificação; seleção,
câmera, texto integral e identidade permanecem preservados. CI exige a API real.

Actions: 41766058052 (2), 41766058186 (6), 41766058176 (5) e 41766058128 (1),
todos SUCCESS no código acima. Codex completed sem findings, recibo 6621614930.
Cinco harnesses instalados passaram 105 checks (14/17/8/15/51), sem JS ou
requisições externas. P05 não autora verificou 32 arquivos iguais, 119 testes
por modo (118 PASS/1 SKIP Windows), 13 grupos no Caderno real, 21 viewports,
12 casos de foco/timer e três de paginação do registro real tardio; exports
globais/tabelas exatos. As 684 fontes/625162319 bytes ficaram sem deltas.

P05 e coordenação inspecionaram imagens reais desktop/mobile, tabelas e
Relações, além da referência original composta sobre o mesmo snapshot.
O teste sintético de paginação abrange quatro tipos; a reprodução real foi
em registros. Uma falha inicial de preflight do harness scratch seguida por
rerun isolado PASS permanece registrada, sem causa inferida ou apagamento.

Este último sucessor altera somente os ledgers da Feature004. Requer sua
própria CI/Codex, atestação dos 32 arquivos públicos e recibo do comando Windows;
o recibo terminal na PR25 fixa o HEAD final. T015/T016 e
R006/R010/R012/R014/R016 não são reabertas; aceite humano segue pendente.
