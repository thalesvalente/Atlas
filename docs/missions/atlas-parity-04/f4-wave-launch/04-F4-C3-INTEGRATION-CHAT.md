# AP04-F4-C3-INTEGRATION-CHAT-01 — compor F3A/F3B, leitor externo e painel legado segregado

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions e escrita. **Esforço:** Extra High, seleção MANUAL do operador.  
**Repositório:** `thalesvalente/Atlas`. **Branch exclusiva convencional pré-criada:** `integrate/atlas-parity04-f4-composition-20261031`.  
**Base Git:** F2 qualificada `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.  
**Resultado-alvo:** `F4_C3_INTEGRATED_CANDIDATE_GLOBAL_CI_PENDING`, somente se composição/QA focal passarem, **não** G5/G6 completo.

## Dependências rígidas — NÃO começar enquanto faltar

1. C0 `F4_C0_READER003_SCOPED_CONTRACT_REVIEWED` com SHA/tree/parent e parecer independente reais; adendo versionado e compatível com ADR aprovada.
2. C1 `F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION` com SHA/CI/revisão próprios e prova sintética navegável de **2.911 nós/1.595 relações**; não usar F3A anterior de 1.000 nós como se estivesse pronto.
3. C2 `F4_C2_EXTERNAL_READER_READY_FOR_LOCAL_QUALIFICATION` com código/tool de aquisição O1 fora do runtime e contrato de descriptor válido.
4. F3B qualificada PR #17 `72118073cc72b4d3cdca21fcc64c18cf742ae384`, tree `ac3dec6de49bf55dc25115bfb35dd364b1a2f690`, revisão independente e CI focal.
5. ADR-0003 v0.2 `APPROVED_SCOPED` na PR #15 comentário `6539419419`, pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527` e AP04-POR F4/G4/G5. **F5/G6 ou validação privada não são entradas deste CHAT.**

Sem input qualificado, registrar `F4_C3_DEPENDENCY_BLOCKED_EXACT` com SHA faltante; não simular dependências. Se houver necessidade de mudar objetivo/ordem/contratos, justificar e pedir aprovação aplicável antes da mudança.

## Ownership exclusivo e história Git

O integrador C3 é o único writer do **shell e composição**:
- `packages/atlas/src/atlas_viewer/static/index.html`, `app.js` e assets estritamente novos `parity04_f4_*`;
- `packages/atlas/src/atlas_viewer/server.py` **somente** se necessário adicionar nomes de assets FIXOS à allowlist, sem novo endpoint/caminho genérico;
- scripts/testes/fixtures prefixados `atlas_parity04_f4_c3_*`, workflow focal isolado `atlas-parity04-f4-integration.yml` se necessário;
- `docs/missions/atlas-parity-04/f4-c3-integration/` para composição, recibos e manifesto.

Não modificar código F3A scaled, F3B, C2, C0, `Catalog`, SDK, protocolo, `reader.md` histórico, F1/F2, R4 ou guardas globais de CI. Reparos de controles globais são ownership de C4, **após** congelar C3.

Compor as fontes F3A/C1, F3B, C0 e C2 por objetos Git com **ancestry completa preservada**. O integrador pode realizar merge técnico **somente dentro da branch F4**, com pais/árvores explícitos, sem squash/cherry-pick que perca proveniência; **não** fazer merge das PRs em main, fechar outras PRs ou usar force/rebase. Nenhuma nova worktree/clone persistente. Dois agentes não podem alterar a mesma worktree; A shell/estado, B harness/browser, C revisão independente somente leitura, coordenador único writer.

## Produto a implementar efetivamente

1. Tela original C4 e pacote Caderno continuam íntegros, com catálogo, filtros, metadados, tabelas P03, links e CSS próprios. Nova área opcional **“Apresentação legada (derivada)”** está segregada; nada mistura identidades entre Caderno e legado.
2. Entrada **explícita por File API** em navegador, escolhida pelo usuário, aceita apenas descriptor `atlas-legacy-presentation` 0.2.0 validado. Sem upload ao server, localStorage/sessionStorage/IndexedDB, serviço remoto, endpoint HTTP, backend reader ou descoberta de arquivos. C2 O1 somente gera JSON fora do viewer; a interface não executa C2 nem lê sua fonte.
3. Carregamento atômico com schema Draft2020-12 fechado e invariantes semânticas, quotas F2 (32 MiB, depth20, 10k nós, 100k relações etc), 60min TTL, tokens fonte/snapshot/ocorrência/sessão e `LEGACY_DERIVED`. JSON inválido ou quota excedida não mostra dataset parcial. Não anunciar hard heap 256 MiB/30s se não houver imposição medida na fronteira real.
4. Carregar componentes F3A scaled e F3B pelos assets fixos, sem `r4.*` nem dependência do Caderno. Colocar lado a lado árvore SVG e tabelas, alternando projeto/experimento/execução apenas por **relações declaradas**. `graph-selection` e `atlas-f3b-select` têm sessões independentes: implementar tradução neutra segura por fonte/snapshot/occurrence, sem assumir igualdade de nonce ou confiar em títulos.
5. Navegação de nó→execução→tabela→linha→evidência **apenas quando comprovadamente ligada**. Se F1 tem Run externo isolado e `binding_gap`, exibir o gap e permitir abrir a tabela sem inventar ancestralidade. Quatro tabelas desvinculadas continuam consultáveis; 28 RF não admitidas permanecem não admitidas. Eventos orfãos/colisões/null/unresolved/repeated visíveis. Não promover File a produto sem papel.
6. Segurança: construir DOM com texto inerte (`textContent`), CSV/JSON conforme F3B, nenhuma URI externa executável; CSP/Origin/Host/no-store/nosniff preservados. `server.py` serve só assets estáticos exatos, nunca arquivo privado por URL. Limpar RAM/tokens na troca de contexto/TTL/dispose, preservar Caderno.
7. UX real com zoom/pan/minimapa, teclado/foco, 1440/390/320 CSS px, conteúdo longo, filtros/paginação e status de origem/cobertura. Indicadores não permitem `UNKNOWN` ou integridade virar aprovação científica; global_total desconhecido permanece UNKNOWN.
8. Instalação SDK/viewer fora do checkout sem R4; viewer Caderno funciona **sem** qualquer descriptor ou tool externa. Testar regressões de pacote, links stale e casos adversariais sem acesso privado.

## QA e fechamento C3

CI focal com **fixtures sintéticas** de F2/F3A/F3B/C2, incluindo grafo 2.911 nós/1.595 relações e várias tabelas, execução browser instalada Windows/Ubuntu normal/`-O` quando aplicável, zero skips/falhas, JSON/JUnit/screenshots SHA-bound. Verificar atomicidade File API, segurança e C4 intacto. Não atribuir G3 real ou G6: nenhuma RF real no CHAT.

Gates históricos globais podem falhar por sucessão de paths/fixtures/tooling. **Não alterar auditorias/manifestos congelados para calá-los**, mas registrar `GLOBAL_CI_PENDING_EXACT` e passar o ownership de controle para C4. C3 só encerra `F4_C3_INTEGRATED_CANDIDATE_GLOBAL_CI_PENDING` com CI focal/independent review no SHA terminal (ou `BLOCKED_EXACT` com prova).

Persistir no Git `COMPOSITION-MAP.md` (pais/árvores/deltas), `RESULT.md`, `INPUT-SHAS.json`, `UI-SECURITY.md`, `BROWSER-RECEIPT.json`, `NEGATIVE-TESTS.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`, todos sob `docs/missions/atlas-parity-04/f4-c3-integration/`. Sem ZIP transitório como único handoff.

Nenhuma fonte privada, R4, migração, F5/F6, merge em main, release, deploy, promoção, limpeza ou aprovação científica.

**END-OF-F4-C3-PROMPT — COMPLETE**
