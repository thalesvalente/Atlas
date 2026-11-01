# AP04-F4-C3-INTEGRATE-REAL-ATLAS-CHAT-02 — integrar árvore e RF do export verdadeiro

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions e escrita. **Raciocínio recomendado: Extra High**, selecionado manualmente pelo operador.
**Repo:** `thalesvalente/Atlas`. **Branch de integração já existente** `integrate/atlas-parity04-f4-composition-20261031`, base inicial F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`/tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`. Não criar worktrees/clones e não alterar branches dos owners.
**Resultado:** `F4_C3_REAL_V5_INTEGRATED_CANDIDATE_GLOBAL_CI_PENDING` com CI focal e revisão independente; caso contrário `F4_C3_DEPENDENCY_BLOCKED_EXACT` ou `F4_C3_BLOCKED_EXACT`. Não declarar G4/G5/G6 pelo resultado focal.

## 1. Só começar quando as dependências forem verificadas

Antes de implementar, conferir **por SHA/tree/parents e recibos reais**:

- F4-C0 contrato reader003 aprovado e revisado `d498504cd2c4d230088f86e04e55624bbe32df79`, tree `4f0c6360d429507af1946a094c27b790c9894477`;
- F4-C1 grafo real-shape sintético escalável `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, tree `1ba41dd01b118a008ca33061131e9181a2600548`, 2.911 nós/1.595 relações navegáveis, sem perda; limite auxiliar 600.000 valores explicitado;
- F3B tabelas PR #17 `72118073cc72b4d3cdca21fcc64c18cf742ae384`, tree `ac3dec6de49bf55dc25115bfb35dd364b1a2f690`;
- **C2-D** integração do leitor real v5 + isolamento OS sob SHA final, qualificada para teste LOCAL, com manifesto antigo C2 preservado. Não usar o SHA v5 `e349a09d439d292011bca4c0994cf8ab3e3fbf9f` sozinho para alegar C2 pronta: nessa revisão os hard limits e FS/rede ainda estavam não qualificados;
- C2-K: se o mapeamento source-key / native_id exigir uma extensão do descriptor 0.2.0, exigir aprovação humana ARC-09 específica, schema e validadores **versionados e qualificados**. O `APPROVED_SCOPED` anterior de ADR-0003 v0.2 só aprova a via O1/O3, não qualquer mudança futura de contrato;
- Leitura LOCAL L0 da estrutura F1, quando autorizada: só handoff sanitizado, jamais bytes de RF/HTML para CHAT. A prova operacional privada L1 pode ocorrer em paralelo **depois de C2-D**, não é pretexto para inventar dados reais neste CHAT.

Se C2-D ainda estiver `C2_D_BLOCKED_EXACT`, não implementar File API por cima de um leitor impossível de operar e declarar integrada: realizar apenas diff/planejamento seguro, retornar `F4_C3_DEPENDENCY_BLOCKED_EXACT`. C0/C1/F3B não precisam ser refeitas.

## 2. Plano, autorização e ownership

Ler AP04-POR-v1.0-draft F4/G4/G5, D-001–D-020, PAR-001–015, ARC-01–09, ADR-0001/0002, ADR-0003 v0.2 `APPROVED_SCOPED` comentário PR15 `6539419419` e o contrato 003 aditivo. O operador autorizou transferir o código legado R4 NECESSÁRIO para Atlas público; isso NÃO autoriza publicar corpus, chamar R4 no browser/server ou quebrar separação Caderno. Preservar RO-Crate 1.3, Process Run 0.6 e Caderno 0.1.0a1; HL7/FHIR apenas extensão futura por domínio.

**Ownership ÚNICO C3:** shell `packages/atlas/src/atlas_viewer/static/index.html`, `app.js`, novos assets com prefixo `parity04_f4_`, `server.py` apenas se for necessário servir nomes exatos de assets estáticos e sem abrir endpoint. Testes/fixtures/harness prefixados `atlas_parity04_f4_c3_` e workflow focal próprio `atlas-parity04-f4-integration.yml` quando requerido; docs `docs/missions/atlas-parity-04/f4-c3-integration/`.

**Não editar:** F3A, F3B, C2 parser/OS, C0 adendo original, `Catalog`, SDK, Caderno, protocolo, reader003 histórico, R4, manifests/guards globais P06/P03/AP04/C2 ou branches dos outros owners. O owner C4 só recebe o SHA C3 congelado.

Compor por Git objetos/imput SHAs preservados: especificar cada `source_commit`, árvore, paths, blobs, autoria e hashes no `COMPOSITION-MAP.md`; não ocultar cherry-picks ou fingir ancestry que não existe. Para branches com pais distintos, a operação de merge técnico dentro da branch F4 **somente** quando permitida pela topologia/ownership revisados; nunca merge em main, fechar PRs, squash para apagar proveniência, rebase ou force. Revisor deve avaliar conflitos antes de publicar.

Subagentes: A UI/estado/callsites, B Browser/CI/contraprovas, C revisão independente somente leitura no SHA final, com coordenador único writer. Se não há subagentes verdadeiros, fazer trabalho seguro e registrar pendência de QA, não inventar paralelismo.

## 3. Produto executável esperado

1. O Atlas C4 continua operando com Caderno pela via existente. Acrescentar **painel opcional segregado** “Apresentação legada — derivada” sem alterar `Catalog`, SDK ou endpoints. Nenhum descriptor, nenhuma ferramenta R4: viewer funciona como antes. Parser externo O1 não entra na distribuição do viewer nem é invocado pela UI.
2. **Entrada File API explícita:** usuário escolhe um arquivo JSON temporário gerado pelo C2-D. Front-end valida versão/profile/authority/quota/schema/semântica antes de divulgar um único dado. Nada de upload ao servidor, fetch de URI de origem, `file://`, varredura de disco, worker carregando HTML/JS do arquivo, localStorage/sessionStorage/IndexedDB ou fonte em logs. Aplicar política CSP/Origin/Host/no-store/nosniff já fixada; se precisar novo endpoint ou origem, pedir autorização contratual, não fazer.
3. Validar o descriptor 0.2.0 fechado ou sucessor EXPRESSAMENTE aprovado, incluindo chaves duplicadas antes do JSON.parse quando relevante, depth20, 32 MiB, até 10k nós/100k relações, 128 tabelas/100k linhas, literais/lexemas, TTL≤3600, fonte/snapshot/importação/ocorrência e estados `LEGACY_DERIVED`. Falha atômica, sem dataset parcial nem continuar seleção stale.
4. Carregar árvore SVG C1 escalável e tabelas F3B **por assets fixos**, sem importar `r4.*`. Apresentar registros, grafo de linhagem e linhas RF sem confundir 159 records e 2.911 lineage nodes. Desenhar janela SVG até limite real de render sem truncar modelo; zoom/pan/minimapa/busca/reveal/teclado e reflow 1440/390/320.
5. Navegar por `source_id`+`snapshot_id`+`occurrence`+`navigation_id`+`session_id`, apenas com relações/parent_key explicitamente comprovadas. Jamais associar `native_id` por igualdade de rótulo, `key` ou `ui_id`. Se extensão K estiver aprovada, usar referência estrutural com basis explícito e validação. Se não houver vínculo completo com Run externo, mostrar `binding_gap`, sem criar Project/Experiment/Run científico novo.
6. Tabelas devem mostrar ID original quando comprovado, núcleo/módulo, Nome, Descrição, Critérios de Aceitação; 28 RF não admitidas sem ID nativo, quatro tabelas sem `record_id` válido, RNF/RES somente quando declaradas, produtos e File separados. Busca/filtro/ordenação/paginação/detalhe/export JSON fiel/CSV seguro continuam válidos. URL/HTML fonte permanece TEXTO inerte.
7. A nova interface nunca afirma integridade de fonte ou revisão científica pela simples apresentação. `UNKNOWN_UPSTREAM`/`GLOBAL_UNPROVEN` e `MISSING` não viram zero ou total da história. Expiração/reimportação limpa RAM/tokens sem alterar Caderno. Clicar em evidência externa não executa ou abre caminho privado automaticamente.
8. **Limites reais de C1:** 600.000 valores visitados podem rejeitar um descriptor que cumpra contagens F2. Teste fronteiras sintéticas 599999/600000/600001, tipos/bytes/profundidade/linhas; se rejeitar payload legítimo dentro de 32MiB, corrigir algoritmo dentro do escopo ou solicitar revisão versionada, sem cortar arestas e declarar PASS.
9. Sem regredir SDK/viewer instalado fora do checkout, C4 pacote Caderno, browsers, URL hash/deep links, foco/teclado, segurança de CSV e CSP. UI só pode consumir arquivo explicitamente escolhido e validado.

## 4. CI, revisão e recibos

CI focal Windows/Ubuntu × normal/-O, Playwright/Chromium REAL e screenshots/JSON/JUnit SHA-bound, todos os testes F3A/F3B/C4 relevantes e casos adversariais. Construir fixture de ENTRADA com **forma real de R4 v5 e valores inventados**, transformada via C2-D para descriptor (não `atlas-legacy-synthetic-source` como fonte produtiva). Provar navegação de 2.911 nós, 1.595 relações e cinco tabelas com 152 linhas sintéticas, escolha/troca de arquivo, invalidação stale, campos RF, null/collisions/unbound e Caderno independente.

Os seis workflows globais antigos podem rejeitar os paths de produto ainda não autorizados: não editar guard P06/AP04/F2/C4 para verde; registrar causa e entregar à C4. `F4_C3_REAL_V5_INTEGRATED_CANDIDATE_GLOBAL_CI_PENDING` exige CI **focal** e revisão independente real no SHA final; **não significa** G4 LOCAL, G5 global ou G6 com RF real.

Persistir na branch F4 código/testes e `RESULT.md`, `INPUT-SHAS.json`, `COMPOSITION-MAP.md`, `READER003-DELTA.md`, `SECURITY-AND-ROLLBACK.md`, `BROWSER-RECEIPT.json`, `NEGATIVE-TESTS.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` sob `docs/missions/atlas-parity-04/f4-c3-integration/`. Publicar por commit/tree/parent verificáveis, sem download manual de ZIP.

Se dados privados forem necessários para confirmar comportamento, entregar pedido LOCAL exato, não simular browser com o acervo. Não iniciar F5/F6, merge em main, release, deploy, promoção, migração, limpeza ou alteração R4.

**END-OF-AP04-F4-C3-PROMPT — COMPLETE**
