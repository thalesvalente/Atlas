# Tasks — Feature 004

## Phase 1 — contrato e planejamento
- [x] T001 Reconciliar PR/HEAD, constituição e skills reais; registrar decisões em plan.md.
- [x] T002 Definir formato opcional e critérios de equivalência em contracts/native-view.md.

## Phase 2 — produtor e representação
- [x] T003 [US1] Implementar projeção genérica sem perda e pacote fragmentado em tools/export_native_notebook.py.
- [x] T004 [US1] Reutilizar a API original R4 project com raízes explícitas, saída nova/disjunta e sem mutações em tools/export_native_notebook.py. O ramo operacional está implementado; execução contra o Caderno privado está em T016.
- [x] T005 [US1] Ler apenas payloads File verificados com quotas em packages/atlas/src/atlas_viewer/native_notebook.py.

## Phase 3 — experiência nativa
- [x] T006 [US2] Registrar endpoints fixos e navegação nativa em server.py e static/index.html.
- [x] T007 [US2] Integrar busca/filtros, árvore navegável, seleção e detalhes em static/native_notebook.js e native_graph.js.
- [x] T008 [US2] Reutilizar P03 em tabelas paginadas com valores exatos e exportações.
- [x] T009 [US2] Apresentar recursos/dossiês, linha do tempo, cobertura e coleções adicionais.
- [x] T010 [US1] Entregar comando único com preflight em scripts/ABRIR-ATLAS-NATIVO.ps1 e quickstart.md.

## Phase 4 — análise / verificação / convergência
- [x] T011 [US3] Testar exportação, leitura, preservação e negativos em tests/viewer/test_native_notebook*.py; acrescentar regressões dos findings no mesmo conjunto.
- [x] T012 [US3] Exercitar a UI instalada em scripts/qa/browser_native_notebook.mjs e Actions. Execução observada 41387198946 no SHA 38f566bc7b519e97a5b42665794c83196af2a99d, incluindo navegador e screenshots; sucessor exige nova qualificação terminal.
- [x] T013 Executar setup_plan.py, setup_tasks.py e check_prerequisites.py reais do Spec Kit na CI sem alterar .specify/feature.json; quatro células Windows/Ubuntu normal/-O no run 41387198946.
- [x] T014 Reconciliar tarefas e análise spec↔código↔testes em analysis.md; recibo terminal é publicado na conversa da PR #23 sem assinatura circular em commit.
- [x] T015 [US3] Parecer independente obtido na candidata de convergência PR #25: Codex no código efad09d, completed/zero findings; P05 não autora requalificou três findings com contraprovas próprias. O sucessor documental exige seu próprio recibo terminal, sem aprovação inferida.
- [x] T016 [US3] Experiência comparada no Windows com o Caderno real, referência original sobre o mesmo snapshot, navegação bilateral, exports exatos e fontes preservadas; dados privados permanecem locais. Aceite humano não é atribuído por este teste.

## Dependências / recibos
T001/T002 → T003/T004 → T005 → T006–T009 → T010–T013 → T014/T015 → T016. O primeiro ciclo teve um writer e NATIVE_SUBAGENTS_NOT_AVAILABLE; a Phase 5 usou agentes nativos reais com ownership exclusivo e um integrador. T015/T016 receberam provas de engenharia; a promoção e o aceite humano mantêm gates próprios. O recibo terminal da PR #25 fixa o HEAD final, CI, Codex e QA, sem assinatura circular em commit.

## Correções de revisão
- [x] R001 Preservar native_id explicitamente nulo e conferir campos/células de apresentação contra raw_json.
- [x] R002 Compartilhar a política de alteração/reindexação explícita do Catalog; GET nativo não promove pacote substituído a READY.
- [x] R003 Manter o alvo DOM entre cliques e delegar handlers da árvore em elementos estáveis; eliminar retenção de nós descartados pelo AbortSignal.
- [x] R004 Recompor o detalhe/exportação da tabela a partir das linhas verificadas sem JSON.parse que arredonde números, e testar em Chromium em scripts/qa/browser_native_notebook.mjs.
- [x] R005 Construir pacotes em staging privado no mesmo filesystem e publicar atomicamente sem substituição; falha de fsync mantém staging para inspeção e permite retry em tests/viewer/test_native_notebook.py.
- [x] R006 Revisão independente de R004/R005 requalificada por Codex e P05, incluindo exportação por ocorrência e publicação atômica; CI verde isolada não foi usada como aprovação.
- [x] R007 Rejeitar raw_json não canônico, ainda que sintaticamente válido e rehachado, antes de expor tabela como READY em packages/atlas/src/atlas_viewer/native_notebook.py; regressão em tests/viewer/test_native_notebook.py.
- [x] R008 Usar prefixo curto fixo para staging em tools/export_native_notebook.py, aceitando basename válido de 240 bytes em filesystem POSIX.
- [x] R009 Implementar launcher próprio `scripts/ABRIR-ATLAS.ps1` sem imports/discovery de R4, com fontes explícitas do protocolo, modo vazio honesto e seleção de rota; atualizar README/quickstart/CI.
- [x] R010 Atlas NOVO validado visualmente no Windows com pacote derivado do Caderno real; capturas desktop/mobile inspecionadas por P05 e coordenação, sem publicação do corpus.
- [x] R011 Permitir abertura do Caderno legado em uma chamada no Atlas novo via processos separados, projetando apenas para cache temporário. Corrigir P1 de aspas PowerShell 5.1, P2 de exit code e cobrir a sessão com testes em tests/viewer/test_native_notebook_launcher.py e CI.
- [x] R012 Leitura real no Windows e navegação bilateral conferidas: renderer original em composição privada sobre o mesmo snapshot, sem executar build/save_lineage nem escrever no acervo. O HTML histórico de revisão anterior não foi confundido com a população atual.
- [x] R013 Implementar transporte comprimido Native View V2 (Files zlib) em `tools/export_native_notebook.py` e `native_notebook.py`, mantendo o SDK/protocolo e teto de 32 MiB armazenados; decomprimir sob limites de 8 MiB/bloco e 256 MiB lógico. Testar >32 MiB sintéticos, reconstrução sem perdas e adulteração de tamanho/hash; não modificar acervo R4.
- [x] R014 Transporte comprimido consumiu o Caderno real integralmente, sem NATIVE_AGGREGATE_LIMIT_NO_TRUNCATION; revisão, recomposição, tabelas/exports e integridade foram conferidos. CI normal/-O Windows/Ubuntu e Codex qualificados no código efad09d; recibo terminal próprio obrigatório no sucessor documental.
- [x] R015 Corrigir preflight de grande volume: `scripts/atlas_launch.py` verifica apenas `/notebook` (pequeno) durante startup; `--probe-only` realiza uma única verificação integral, com timeout estendido e sem novas requisições concorrentes. Contraprovas em `tests/viewer/test_native_notebook_launcher.py`.

- [x] R016 Foco inicial progressivo de árvores grandes no `native_graph.js`: 24 irmãos por nível, branches internas recolhidas, cartões legíveis e pesquisa sem perda. Regressão Playwright em `scripts/qa/browser_native_notebook.mjs` com 1202 nós e último descendente.

## Phase 5 — fechamento funcional ATLAS-FINAL-CLOSE

Os recibos desta fase reconciliam T015/T016 e R006/R010/R012/R014/R016;
não reabrem T001–T014 nem tornam um recibo antigo prova de um SHA novo.

- [x] T017 Fixar contrato, DAG e ownership em plan.md; conferir Spec Kit 1.2.3 real, baseline/PRs e checkout preservado.
- [x] T018 [P] [US2] P01 qualificada: rótulos extensos contidos sem perda de identidade; grafo, busca, teclado, pan/zoom/minimapa e contraprovas de escala no browser instalado.
- [x] T019 [P] [US2] P02 qualificada: filtros/busca tabular e global da árvore, coleções vazias/globais, vínculos e reflow 320/390/1440; regressões reproduziram falhas antes e passaram depois.
- [x] T020 [P] [US1] Supervisor compatível corrigido e testado no PowerShell 5.1 real: preflight leve compartilhado, um Python, argv seguro, ProbeOnly e propagação de falhas, sem escrita no Caderno.
- [x] T021 Commits integrados com cherry-pick -x e autoria preservada; código efad09d recebeu 13/13 jobs SUCCESS Windows/Ubuntu, normal/-O, Chromium, instalação e Spec Kit. Todo HEAD sucessor exige nova qualificação terminal.
- [x] T022 Código efad09d com Codex e P05 sem findings materiais; comparação real funcional/visual/integridade e recibo Draft 6619584326 publicados. A matriz e checklist estão em final-close.md; recibo final próprio do sucessor encerra a missão.
- [x] T023 [US2] PAR004 demonstrada no Caderno real: nó→registro→tabela→linha/evidência→Voltar três vezes ao nó original; detalhes/exports exatos, fonte/revisão preservadas e ambiguidades não resolvidas automaticamente.
- [x] T024 [US2] PAR007 entregue: grafo de relações tipadas, busca integral, seleção de endpoints, paginação, teclado/pan/zoom; um resolver tipado/scoped compartilhado com os detalhes, sem causalidade inferida.
- [x] T025 [US3] Regressão Ctrl+clique requalificada no Linux em efad09d: origem explicitamente ativada/focada entre abas, diagnóstico por link, clique real/negativas preservados; ATLAS021 41750468913 terminou 6/6 SUCCESS.

## Phase 6 — composição do handoff funcional da árvore PR #26

- [x] T026 Integrar 76875b4/f985276 e a correção de medição limitada 84e9382, preservando autoria/API/identidades: grade de ramos, escala legível mínima de 85%, minimapa, caminho ancestral e busca integral. O código aa4a25f recebeu sua própria CI 13/13, Codex e P05 no Caderno real; esse recibo permanece histórico.
- [x] T027 Incluir o grafo instalado na CI e requalificar a composição. O código final 0cd96bc inclui a API aditiva cancelPendingSelection() de 84b032c, que cancela somente a notificação pendente; 15 gates do grafo e nove contraprovas obrigatórias de cancelamento na aplicação passaram. Seleção visual, câmera, teclado, locate e destroy foram preservados.

## Phase 7 — aplicação não gráfica e fechamento da composição

- [x] T028 Integrar seletivamente a PR #27 (c636f29/40388b5) e o reparo autoral 28892df sobre a base do integrador d9b05c5. Entregues foco/seleção/estados vazios, NULL versus vazio/ausência/UNKNOWN, reflow e exports exatos. Rota CSS única e pin exato de server.py mantêm os negativos do auditor. Nenhum delta de protocolo, leitor, launcher ou blobs P03.
- [x] T029 Qualificar 0cd96bce6f275a187ed2baf790793b77b5ae18e3: 14/14 Actions Windows/Ubuntu normal/-O, 105 verificações Chromium/Chrome, Codex completed/zero findings e P05 não autora. P05 executou 119 testes por modo, 13 grupos no host, 21 viewports, 12 casos reais de foco/timer e três de paginação do registro tardio; exports exatos e fontes intactas. O encerramento documental exige atestação dos 32 arquivos e CI/review próprios no HEAD resultante; o recibo terminal da PR #25 fixa o SHA e o comando real, sem assinatura circular em commit.

Os findings 4463040279, 4463092564, 4463092566 e P05_REAL_RECORD_PAGINATION_2a381 foram corrigidos com contraprovas antes/depois. O teste real de paginação confirmou registros; recursos/relações/coleções receberam contraprovas sintéticas, sem alegação de reprodução real nesses tipos. T015/T016 e R006/R010/R012/R014/R016 permanecem quitadas no escopo de engenharia. Aceite humano e promoção mantêm gates próprios.

- [x] R017 Portar os algoritmos e apresentação visual de temas/famílias do R4 para módulo de apresentação no `native_graph.js` com CSS isolado no `native_notebook.css`, com esquema genérico e sem `r4.*` no runtime. Preservar a árvore estrutural, valores e relações verificadas. Adicionar teste de navegação por famílias no browser sintético.
- [ ] R018 Conferir a equivalência visual e navegacional do mapa temático da candidata no Windows com o renderer R4 para o MESMO snapshot, sem publicar dados privados; não confundir CI sintética com aceite visual humano.
