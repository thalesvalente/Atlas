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
- [ ] T015 [US3] Obter parecer independente sem findings materiais no SHA terminal da PR #23. Codex examinou 38f566 e apontou ID nulo e duplo clique; correções implementadas nesta revisão exigem requalificação, não aprovação própria.
- [ ] T016 [US3] Comparar a experiência com o Caderno real no host, usando quickstart.md, sem enviar dados privados.

## Dependências / recibos
T001/T002 → T003/T004 → T005 → T006–T009 → T010–T013 → T014/T015 → T016. Um writer, execução sequencial; NATIVE_SUBAGENTS_NOT_AVAILABLE. Implementado/testado não equivale a aceite privado. T015/T016 bloqueiam aprovação integral e promoção, não a publicação da candidata Draft.

## Correções de revisão
- [x] R001 Preservar native_id explicitamente nulo e conferir campos/células de apresentação contra raw_json.
- [x] R002 Compartilhar a política de alteração/reindexação explícita do Catalog; GET nativo não promove pacote substituído a READY.
- [x] R003 Manter o alvo DOM entre cliques e delegar handlers da árvore em elementos estáveis; eliminar retenção de nós descartados pelo AbortSignal.
- [x] R004 Recompor o detalhe/exportação da tabela a partir das linhas verificadas sem JSON.parse que arredonde números, e testar em Chromium em scripts/qa/browser_native_notebook.mjs.
- [x] R005 Construir pacotes em staging privado no mesmo filesystem e publicar atomicamente sem substituição; falha de fsync mantém staging para inspeção e permite retry em tests/viewer/test_native_notebook.py.
- [ ] R006 Confirmar revisão independente de R004/R005 no SHA final; uma execução de CI verde não conclui este gate.
- [x] R007 Rejeitar raw_json não canônico, ainda que sintaticamente válido e rehachado, antes de expor tabela como READY em packages/atlas/src/atlas_viewer/native_notebook.py; regressão em tests/viewer/test_native_notebook.py.
- [x] R008 Usar prefixo curto fixo para staging em tools/export_native_notebook.py, aceitando basename válido de 240 bytes em filesystem POSIX.
