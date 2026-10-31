# AP04-F3A-CHAT-GRAPH-01 — recuperar árvore gráfica hierárquica e interativa

`seai.pipeline@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub e GitHub Actions, com escrita efetiva. Sem host Windows e sem acervo privado.  
**Esforço:** **Extra High** ou maior disponível, selecionado MANUALMENTE pelo operador; se não observável, registrar `REASONING_EFFECTIVE=UNVERIFIED`.  
**Destino único:** `thalesvalente/Atlas`. **Branch pré-criada** `feat/atlas-parity04-f3a-graph-20261031`; não criar outras branches/worktrees/clones.  
**Base congelada:** SHA `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`, PR Draft #15 qualificada.  
**Resultado-alvo:** `F3A_GRAPH_COMPONENT_READY_FOR_F4`, somente com gates isolados completos e revisão real; caso contrário `F3A_BLOCKED_EXACT`. NÃO declarar paridade real ou G6.

## 1. Decisões vinculantes e precedência

Confronte `AP04-POR-v1.0-draft` e `ACTION-PLAN.md` F3A, PAR-001/PAR-004/PAR-007/PAR-012/PAR-015 e G2/G5; ARC-01–09, ADR-0001/0002 e ADR-0003 v0.2 aprovada **apenas no escopo** da decisão humana vinculada ao pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527`. Decisão na PR #15, comentário `6539419419`. Confronte F1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7` e F2 `EPHEMERAL-PRESENTATION-CONTRACT.md`, `IDENTITY-AND-LOSS-POLICY.md`, `PARITY-TRACEABILITY.md`, exemplos sintéticos e N01–N24. A aprovação arquitetural não é autorização de F4, migração ou mudança do R4.

**Esta execução está autorizada exclusivamente para F3A; não iniciar F3B/F4/F5/F6.** O código F3A deve ser genérico, reutilizável e testável sem File API, sem integração ao shell principal e sem dataset real. Não alterar Caderno/RO-Crate/Process Run, reader003, `Catalog`, `server.py` nem importar `r4.*`. HL7/FHIR permanece extensão futura por domínio, sem fingir conformidade. Qualquer desvio necessário do plano ou de decisão vinculante: justificar, documentar impactos/alternativas, solicitar aprovação aplicável ANTES da mudança.

## 2. Ownership exclusivo — contrato de paralelismo

O owner F3A pode editar apenas:
- `packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.js`
- `packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.css`
- `tests/qa/test_atlas_parity04_f3a_graph.py` e testes auxiliares **com prefixo f3a**;
- `tests/fixtures/atlas_parity04_f3a_*` exclusivamente sintéticas, quando necessárias;
- `scripts/qa/atlas_parity04_f3a_*` como harness isolado;
- `docs/missions/atlas-parity-04/f3a-graph/` para recibos/manifesto;
- workflow dedicado `.github/workflows/atlas-parity04-f3a-graph.yml` somente se houver forma estritamente autorizada de qualificação sem afrouxar gates globais.

**Somente leitura:** shell `static/index.html`, `static/app.js`, CSS global, servidor, catálogo, protocolo, C4, workflows existentes, controles P06/P03/AP04/F2, F1 e F2, toda a branch F3B. Não alterar paths compartilhados mesmo para “aparecer na UI”; integração é ownership F4. Coordenador único writer da branch; até três subagentes nativos reais sob ownership A lógica/layout, B QA/browser (arquivos distintos), C revisor independente somente leitura. Sem ferramentas nativas: execução sequencial e `NATIVE_SUBAGENTS_NOT_AVAILABLE`, nunca revisão simulada.

Uma branch não é worktree: usar operações GitHub sobre refs próprias, sem alternar ou modificar o checkout do operador. Não criar worktrees ou clones persistentes.

## 3. Engenharia funcional efetiva

Entregar componente gráfico SVG **interativo**, não screenshot/diagrama estático, consumindo **somente o formato candidato `atlas-legacy-presentation` 0.2.0** por API de componente in-memory, com fixtures 100% sintéticas.

- Navegação hierárquica projeto/família/experimento/stage/run quando **declarados**, sem inventar níveis faltantes. Grupos visuais “sem pai resolvido” são recursos da UI, não entidades científicas.
- Nós com seleção contextual por fonte/snapshot/ocorrência; expandir/recolher, pan/zoom por controles e gestos, reset/ajustar, minimapa navegável, estados de foco, zoom e seleção preservados; suporte teclado Tab, setas, Home/End, Enter/Escape e rótulos/aria acessíveis.
- Estrutura hierárquica explícita (`parent_key`) separada da linhagem tipada. Estilos/legenda distintos para **pertencimento**, derivação dirigida, input/output e menções neutras. Não inferir causalidade por título, profundidade ou vizinhança.
- Colisão de native_id não funde ocorrências; null endpoints e 75 relações unresolved permanecem representáveis. Órfãos e Run externo isolado permanecem isolados; não fabricar continuidade árvore→RF ou Project/Experiment.
- Labels hostis de texto/HTML/JS tratados como **texto inerte**, sem `innerHTML` ou interpretação de URL. Não seguir URI, não acessar rede externa, não ler pastas, não executar dados. Preservar identidades, ausência e avisos por vínculo.
- Layout com muitos nós/relações: limites propostos no descriptor (10.000 nós/100.000 relações), orçamento razoável de DOM/render e viewport; se ultrapassar a capacidade, exibir erro/limite visível, nunca truncar silenciosamente.
- Responsividade desktop, 390/320 CSS px, foco/teclado, contraste, texto longo e overflow; não afirmar zoom nativo 200% ou certificação WCAG sem prova própria.
- Uma seleção de nó deve produzir **evento neutro**, com fonte/snapshot/occurrence/nav_id, sem resolver entidade privada. A F4 fará roteamento para tabelas; F3A não importa módulo F3B.
- API clara `mount`, `setData`, `select`, `dispose` ou equivalente documentado, isolada do runtime principal e sem persistência em storage. Estado descartável por sessão/snapshot; expiração e troca de snapshot invalidam seleção/deep links.

## 4. Fixtures, testes adversariais e CI

Usar exclusivamente exemplos F2 sintéticos ou fixtures novas claramente sintéticas; não publicar nenhum payload histórico. Elaborar testes de:
- hierarquia de nós e pertencimento declarado, colapso/expansão, seleção, reset, pan, zoom e minimapa;
- keyboard traversal, Home/End, Enter/Escape e foco após mudança de layout;
- colisões dentro e entre fontes, nav_id derivado vs native_id, ids duplicados, 22 null endpoints, unresolved, repetidos, Run isolado, binding_gap;
- texto malicioso/URI `javascript:`/HTML, escala/extremos/limite, entradas inválidas, erro visível e ausência de execução;
- preservação de source+snapshot na seleção, invalidação após update e ausência de localStorage/requisições externas;
- Chromium real em Windows/Ubuntu quando Actions permitir, screenshots/JSON/JUnit, sem skips e sem substituir oráculos por snapshots cegos.

Testar modo Python normal/`-O` quando scripts Python estiverem envolvidos. Adotar testes focais isolados que provem o componente funcionando, **não apenas AST ou presença de arquivos**. O runner deve informar claramente qual SHA foi executado. Nenhum dado privado/Windows host é necessário.

**CI histórica C4 é congelada:** novos paths de produto podem ser recusados por gates globais de autoria. Não desativá-los/contorná-los. Qualificar componentes isolados e registrar a recusa global estritamente atribuída, sem declarar integração ou `G5_PASS`. Se a qualificação exigir uma alteração de controle fora do ownership, produzir contrato de reparo exato e solicitar ação do integrador/owner aplicável; não editar auditorias históricas para tornar o workflow verde. Não reivindicar `F3A_GRAPH_COMPONENT_READY_FOR_F4` se o próprio gate focal não estiver completo.

## 5. Entregáveis Git e revisão independente

- Código JS/CSS modular e provas funcionais reais, harness independente, fixtures sintéticas, cobertura negativa e scripts de execução.
- `RESULT.md`, `INPUT-SHAS.json`, `GRAPH-CONTRACT.md`, `BROWSER-RECEIPT.json`, `NEGATIVE-TESTS.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` sob a pasta F3A, com SHA/tree/parent, paths, blobs, testes, limitações e os estados PAR antes/depois.
- Revisão independente sobre HEAD final sem autoria, analisando código, CI, browser e impactos de performance/acessibilidade. Commit posterior de recibos exige fechamento próprio por SHA.
- Publicar tudo no Git da branch F3A por commits normais fast-forward. Se criar PR Draft for necessário para Actions/revisão, **basear explicitamente em `docs/atlas-parity04-f2-legacy-contract-20261030`**, documentar o vínculo com o SHA F2, não alterar PR #15 e manter Draft. Usar uma PR para F3A, não unir com F3B.
- Não depender de ZIP temporário ou download manual. Arquivos privados nunca entram no GitHub público.

**Fechamento:** `F3A_GRAPH_COMPONENT_READY_FOR_F4` apenas para o componente isolado qualificado, não árvore legada real recuperada. Se não houver runner/browser/QA real, `F3A_BLOCKED_EXACT` com trabalho já persistido e ato mínimo. Sem merge, release, deploy, promoção, migração, limpeza, alteração R4, nova worktree ou fonte privada.

**END-OF-F3A-PROMPT — COMPLETE**
