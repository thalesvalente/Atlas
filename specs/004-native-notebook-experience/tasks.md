# Tasks — Feature 004

## Phase 1 — contrato e planejamento
- [x] T001 Reconciliar PR/HEAD, constituição e skills reais; registrar decisões em specs/004-native-notebook-experience/plan.md.
- [x] T002 Definir formato opcional e critérios de equivalência em specs/004-native-notebook-experience/contracts/native-view.md.

## Phase 2 — produtor e representação
- [ ] T003 [US1] Implementar projeção genérica sem perda e pacote fragmentado em tools/export_native_notebook.py.
- [ ] T004 [US1] Reutilizar a API original R4 project com raízes explícitas, saída nova/disjunta e sem mutações em tools/export_native_notebook.py.
- [ ] T005 [US1] Ler apenas payloads File verificados, com limite individual 8 MiB e agregado 32 MiB, em packages/atlas/src/atlas_viewer/native_notebook.py.

## Phase 3 — experiência nativa
- [ ] T006 [US2] Registrar endpoints fixos e navegação nativa em packages/atlas/src/atlas_viewer/server.py e static/index.html.
- [ ] T007 [US2] Integrar busca/filtros, árvore navegável, seleção e detalhes em packages/atlas/src/atlas_viewer/static/native_notebook.js.
- [ ] T008 [US2] Reutilizar P03 em tabelas paginadas com valores exatos e exportações em packages/atlas/src/atlas_viewer/static/native_notebook.js.
- [ ] T009 [US2] Apresentar recursos/dossiês, linha do tempo, cobertura e coleções adicionais em packages/atlas/src/atlas_viewer/static/native_notebook.js.
- [ ] T010 [US1] Entregar comando único com preflight em scripts/ABRIR-ATLAS-NATIVO.ps1 e quickstart.md.

## Phase 4 — análise / verificação / convergência
- [ ] T011 [US3] Testar exportação, leitura, preservação de valores e negativos em tests/viewer/test_native_notebook.py.
- [ ] T012 [US3] Exercitar a UI instalada em scripts/qa/browser_native_notebook.mjs e Actions no SHA final.
- [ ] T013 Executar os scripts Spec Kit da feature 004 na CI sem alterar .specify/feature.json.
- [ ] T014 Publicar resultado factual/revisão na PR #23, reconciliar tasks e emitir specs/004-native-notebook-experience/analysis.md.
- [ ] T015 [US3] Obter parecer independente sobre o SHA terminal na PR #23; não marcar aprovado por autoria própria.
- [ ] T016 [US3] Comparar a experiência com o Caderno real no host, usando quickstart.md, sem enviar dados privados.

## Dependências e ordem
T001/T002 → T003/T004 → T005 → T006–T009 → T010–T013 → T014/T015 → T016. Adaptador e desenho visual poderiam ser paralelos após O0, mas não há subagentes reais nesta sessão; execução sequencial. T015/T016 não bloqueiam a publicação de candidata Draft, mas bloqueiam aprovação integral e promoção. Não fabricar checks para fechar todas as caixas.
