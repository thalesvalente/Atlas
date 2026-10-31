# AP04-F4-C1-GRAPH-SCALE-CHAT-01 — árvore utilizável com 2.911 nós

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/Actions. **Esforço:** Extra High, o operador seleciona manualmente.  
**Destino:** `thalesvalente/Atlas`; **reutilizar branch existente F3A** `feat/atlas-parity04-f3a-graph-20261031`, PR Draft #16, sem novas branches, worktrees ou clones.  
**Base:** `f0d39787e3fb93bfd70ad096824505ba298c6881`, tree `e0d293bd9de6b78c12934bc395b5f0ab5981563f`. F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, ADR/descriptor técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527` `APPROVED_SCOPED`. F1 G1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`.  
**Meta:** `F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION`, **não** G5/G6 e não prova com fonte real.

## Diagnóstico e escopo do plano

F3A qualificou SVG, pan, zoom, minimapa, teclado e identidade, mas seu orçamento próprio limita a renderização a **1.000 nós/4.000 relações**. F1 encontrou **2.911 nós/1.595 arestas**; logo a árvore atual recusa o tamanho da fonte já qualificada. A F4 precisa corrigir essa lacuna, mantendo o envelope do descriptor 0.2.0 de **10.000 nós e 100.000 relações**. Não reduzir quotas, falsificar agrupamentos nem ampliar o plano AP04 sem decisão.

Verifique AP04-POR F4, PAR-001/004/007/012/015, G2/G5, F1 sanitizada, F2 N01–N24 e `GRAPH-CONTRACT.md`/`GLOBAL-GATE-REPAIR-CONTRACT.md` da F3A. O dado real F1 não deve entrar no CHAT público.

## Ownership e paralelismo

Modificar somente `packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.js`/`.css`, testes/fixtures/harness com prefixo F3A, workflow focal F3A se indispensável, e documentos **novos/sucessores** em `docs/missions/atlas-parity-04/f3a-graph/`. Manter os recibos históricos por SHA; novo SHA exige CI e revisão próprias.

F3B, shell `index.html/app.js`, reader003, Catalog/server/SDK, protocolo, R4, guards, workflows globais, manifestos históricos e ramo F4 integrador são **somente leitura**. Agente A lógica/algoritmo SVG, B fixture/browser/CI e C revisão nativa independente; coordenador único writer por branch, sem sobreposição. Ausência de agentes não é autorização para simular review.

## Engenharia e testes de escalabilidade

- Suportar fixture **100% sintética** com 2.911 nós, 1.595 relações e hierarquia explícita; todos os nós precisam continuar **localizáveis e navegáveis**, inclusive quando não estiverem simultaneamente no DOM. Expansão progressiva, viewport/windowing, minimapa agregado e índice de navegação são alternativas; não descartar qualquer nó nem inventar ancestrais. Explicar a diferença entre total declarado, total carregado, elementos SVG renderizados e seleção atual.
- Testar primeiro/meio/último nó, ramo recolhido, nó órfão, Run externo isolado, id duplicado e 22 endpoint-null/75 unresolved/50 colisões/ocorrências repetidas representativos. Seleção mantém `source_id/snapshot_id/nav_id/occurrence/session_id`; `native_id` nulo não ganha admissão. Hierarquia não vira causalidade.
- Pan/zoom/fit, minimapa e teclado Tab/setas/Home/End/Enter/Escape devem continuar utilizáveis em árvore grande e 1440/390/320 CSS px. Foco e seleção devem sobreviver à virtualização quando possível; falhas visíveis, não sucesso falso. Texto/URI hostis permanecem inertes.
- O envelope 10.000/100.000 não obriga 100.000 SVG simultâneos: implementar limites de desenho por viewport sem truncamento semântico. Stress sintético e caso 10.001 nós devem demonstrar aceitação dentro do envelope **ou recusa conforme limite REAL explicitamente documentado**; qualquer discrepância com o descriptor aprovado não pode ser silenciada e deve ir ao gate do integrador. Medir latência, contagem renderizada, comportamento de memória/DOM e deadline, sem alegar hard heap 256MiB do browser se não medido.
- Invalidação de token stale, troca de snapshot, TTL, `dispose`, ausência de network/storage/script inject. Testes DOM/Chromium reais, não apenas AST.

Reexecutar os **22 testes F3A e 17 jornadas Chromium** herdados, somando os de escala, nas quatro células Windows/Ubuntu × normal/`-O`, zero falhas/erros/skips; registrar métricas e JSON/JUnit/capturas por SHA. Revisão independente no HEAD final. Os gates globais congelados podem rejeitar a nova autoria: **não** relaxá-los; sua sucessão exata pertence à C4 após composição. Não transferir PASS de F3A anterior ao SHA novo.

`F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION` significa navegação sintética do volume F1 sem perdas; não é G6 nem paridade com corpus privado. Bloqueio com causa exata deve resultar em `F4_C1_GRAPH_SCALE_BLOCKED_EXACT` e próximo ato mínimo. Sem merge, release, deploy, migração, alteração R4, worktrees/clones.

**END-OF-F4-C1-PROMPT — COMPLETE**
