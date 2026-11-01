# AP04-F4-C2-A-REAL-V5-MAPPING-CHAT-02 — completar adaptação do leitor legado real

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions e escrita efetiva. **Raciocínio recomendado: Extra High**, selecionado manualmente pelo operador. Se não observável, `REASONING_EFFECTIVE=UNVERIFIED`.
**Repositório e branch exclusivos:** `thalesvalente/Atlas`, PR Draft #18, branch já existente `feat/atlas-parity04-f4-external-reader-20261031`. Sem novas worktrees/clones, sem branch paralela de autoria do componente A.
**Entrada técnica:** SHA `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, tree `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df`; validar o HEAD real antes da escrita, reconciliar alterações supervenientes por SHA e ancestry, não rebasear silenciosamente.
**Alvo restrito:** `C2_A_REAL_V5_MAPPING_QUALIFIED_SCOPED` com CI focal, contratos e revisão real; ou `C2_A_SOURCE_KEY_DECISION_REQUIRED`/`C2_A_BLOCKED_EXACT`.

## 1. Entradas obrigatórias e autorização

Ler no GitHub:
- R4 privado `thalesvalente/R4-RNF-RES-FIX`, commit `5c145615c8a1bd601351badddccaf3acea474ed2`: `src/r4/campaigns/atlas.py`, `notebook_projection.py`, `atlas_rf_sources.py`, `experiment_lineage.py`, `atlas_scientific_scope.py`, `presentation/atlas_assets/template.html`, `app.js`, `graph-layout.js` e `tables-coverage.js`.
- Atlas F1 sanitizada `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, F2 contrato/ADR `c3ea1e82938fd61cc5a22fee973352715a5bb527`, F4 C0 adendo reader003 `d498504cd2c4d230088f86e04e55624bbe32df79`, F4 C1 grafo escalado `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, F3B tabela `72118073cc72b4d3cdca21fcc64c18cf742ae384` e plano AP04-POR-v1.0-draft.
- C2 original PR #18 `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`, 22 hashes históricos; sucessor v5 `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, CI focal 4/4 run `41264209454`.

**O usuário autorizou expressamente reutilizar e transferir o código legado necessário do repositório R4 PRIVADO ao Atlas PÚBLICO.** Isso não autoriza transferir bytes de experimentos, RF literais, caminhos locais, credenciais, dados históricos privados, licenças de terceiros nem dependências desnecessárias. Antes de cada novo trecho literal: conferir direitos, privacidade, interfaces e escopo; registrar source path, SHA/blob e transformação. Não importar `r4.*` nos wheels novos nem executar o produtor legado.

A entrada REAL é `r4-experiment-viewer-v5`, embutida como JSON inerte em `script#data[type=application/json]` no HTML pré-gerado. `ATLAS-ATUAL.html` é ponteiro, não fonte de dados. O formato antigo de ensaio `atlas-legacy-synthetic-source/0.1.0` **não é formato de produção** e permanece só como teste.

## 2. Ownership: A é o único autor do mapeador

Pode modificar somente `tools/atlas_legacy_presentation/parser.py`, `legacy_v5.py`, `legacy_v5_descriptor.py`, novos módulos com prefixo `legacy_v5_`, testes `tests/qa/test_atlas_parity04_f4_c2_real_v5.py`, `tests/qa/test_atlas_parity04_f4_c2_v5_descriptor.py`, novos testes com prefixo `test_atlas_parity04_f4_c2_v5_`, workflow focal existente da C2 se absolutamente necessário, e recibos **novos/aditivos** em `docs/missions/atlas-parity-04/f4-c2-real-v5/`.

**Somente leitura:** `tools/atlas_legacy_presentation/reader.py`, `__main__.py`, módulos de isolamento OS (owner B), testes/workflow B, SDK, viewer, servidor/Catalog, Caderno/protocolo/reader003, código F3A/F3B, corpus privado, manifestos antigos e scripts globais. Owner B trabalha em outra branch com arquivos exclusivos. Coordenador único escritor na PR18. Até três subagentes REAIS se disponíveis: A1 parser, A2 QA, A3 revisão independente somente leitura; se indisponíveis, executar seguro sequencialmente e não alegar revisão nativa.

## 3. Implementação necessária

1. Ler e mapear **campos reais**: `records`, `edges`, `result_tables`, `products`, `resources`, `product_items`, `product_groups`, `resource_documents`, `sources`, `source_crosswalk`, `frontiers`, `external_runs`, `dossier_*`, `lineage_graph` quando efetivamente presentes. Não criar novo envelope-fonte sintético para alimentar o mapeador.
2. Preservar a separação entre `records` e `lineage_graph.nodes`: F1 observou 159 registros e 2.911 nós de linhagem, não são a mesma população. Arestas de linhagem ≠ `records.edges`. Requisito positivo de regressão: fixture inventada com 2.911 nós, 1.595 relações e registros independentes.
3. `lineage_graph.nodes[].key`, `ui_id`, `native_id`, `parent_key` e `edges[].from_key/to_key` são dimensões diferentes. 858 parent keys explícitos resolvidos pela F1 podem depender da chave estrutural. O descriptor 0.2.0 está vinculado a native ID nas referências. **Nunca** preencher native_id a partir de key/ui_id, nem resolver por igualdade textual em outra coleção. Quando o formato aprovado não puder expressar o vínculo, preservá-lo em unmapped_fields/gaps e sinalizar `C2_A_SOURCE_KEY_DECISION_REQUIRED` para a frente K; não afirmar que a árvore foi integralmente restabelecida.
4. Em `result_tables[].rows[].cells` o R4 usa mapa de células literais, não o array inventado da C2 original. Preservar chaves e ordem observada, tipos/lexemas, ID, núcleo/módulo, Nome, Descrição e Critérios de Aceitação, categorias MISSING/null, linhas e ordinais; não deduplicar/ordenar por heurística. Quatro tabelas sem record_id resolúvel continuam consultáveis, sem vinculação fictícia.
5. O registro RF com ID nativo comprovado não equivale a aprovação científica. Os 28 `UNADMITTED_NATIVE_RF` devem conservar `native_id=null` e status; RNF/RES não são inferidas de nome de tabela ou MIME. Run externo isolado e binding_gap não viram percurso contínuo fabricado.
6. Ativos `File`, `Product`, `ProductGroup`, `ResourceDocument`/dossiês somente quando explicitamente declarados; `File` nunca promovido a `Product`. URI é texto inerte, sem seguir links. Campos não exibidos vão a `unmapped_fields`/gaps ou erro `UNREPRESENTABLE_SOURCE_FIELD`, nunca descarte silencioso.
7. Validação JSON Schema Draft2020-12 do descriptor 0.2.0 + invariantes semânticas, quotas de bytes/profundidade/linhas, native IDs, tokens e contexto fonte/snapshot/ocorrência, TTL. Não alargar schema sem decisão versionada ARC-09. Não relaxar G4 256 MiB/30 s e isolamento FS/rede. CLI/reader.prepare real permanece fail-closed até integração B e validação OS.
8. Reusar utilitários seguros de leitura/verificação, sem executar HTML/JS legado, o R4, provider ou pipeline; nada de varredura de diretórios. Compare o resultado com comportamentos antigos `graph-layout.js`/`tables-coverage.js`, mas preserve no novo UI a inércia dos dados em lugar do `innerHTML` ou `file://` antigo.

## 4. Testes, CI e handoff

Executar teste real focal com fixtures de **forma v5 real e valores inventados**, Windows/Ubuntu × Python normal e `-O`. Preservar os 51 testes do sucessor v5, acrescentar negativos de parent_key/native_id/ui_id, cross-collection collision, 2911/1595, 5 tabelas e 152 linhas inventadas, 28 não admitidas, campos ausentes, Unicode, inteiros maiores que 2^53, HTML duplicado/JS hostil, fontes parcialmente inválidas, atomicidade de transformação e não execução de links. Ser preciso com skip ACL Windows não aplicável no Ubuntu; não declarar zero skips universal sem prova.

CI focal do HEAD terminal com JUnit/JSON, hashes de todos os 22 objetos históricos por seu SHA original, lineage/paths exatos, ausência de R4 dos wheels e review independente real. Gates globais AP04/P06/C4 podem rejeitar novos paths: **não** mudar guards, pins ou manifests históricos; qualificação sucessora global pertence à C4 depois da composição.

Entregar código, testes e `RESULT.md`, `REAL-V5-FIELD-MAPPING.md`, `SOURCE-KEY-GAPS.md`, `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` em Git com commit/tree/parent e evidências. Sem autorizar F4-C3 antes das dependências.

Resultado escopado somente após provas reais; se a chave estrutural for intraduzível, **continuar a engenharia segura mas encerrar como decisão pendente**, sem inventar identidade. Sem merge em main, release, deploy, promoção, migração, alteração R4, leitura de acervo privado no CHAT ou novas worktrees/clones.

**END-OF-AP04-F4-C2-A-PROMPT — COMPLETE**
