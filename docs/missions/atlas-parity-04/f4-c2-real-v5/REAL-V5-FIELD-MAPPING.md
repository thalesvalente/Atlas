# Mapeamento do exportador r4-experiment-viewer-v5

Fonte de produção: JSON **inerte** em `<script type="application/json" id="data">` do index.html R4 pré-gerado. `ATLAS-ATUAL.html` é somente ponteiro. `atlas-legacy-synthetic-source/0.1.0` é fixture antiga de teste, nunca nova entrada de produção. Descriptor-alvo: `atlas-legacy-presentation/0.2.0` fechado, sem ampliar schema ARC-09.

| Campo original | Destino do descriptor | Regra de conservação |
| --- | --- | --- |
| `records[]` | `nodes[]` | Record.id original; não confundir com população A10. Demais campos em unmapped_fields. |
| `edges[]` | `relations[]` | Endpoints de registros; tipos, provas, ordem, ocorrências e gaps preservados. |
| `lineage_graph.nodes[]` | `nodes[]` | kind/label, native_id declarado e parent_key_literal; key/ui_id preservados por pointer/lexema em unmapped_fields. |
| `lineage_graph.edges[]` | `relations[]` | from_key/to_key são chaves estruturais, não IDs nativos. Sem inferir relação quando não há binding comprovado. |
| `lineage_graph` (metadados não tipados) | `unmapped_fields` | Branches, contagens, colisões, retenção etc. com JSON Pointer original e gap. |
| `result_tables[].rows[].cells` | `tables[].rows[].cells` | Mapa literal, colunas na primeira ordem observada, ordinais e lexemas, MISSING/null/zero/string vazia e números acima de 2^53. |
| `result_tables[].rows[].native_id` | `identity.native_id`, RF | UNADMITTED_NATIVE_RF continua null, sem admissão científica. Categoria ausente não é inferida. |
| `result_tables[].record_id` | `record_binding` | Somente record.id único; tabelas desvinculadas mantidas pesquisáveis. |
| `resources[]` | `assets:File` | path/URI são texto, sem acesso. File nunca vira Product. |
| `products[]` e `product_items[]` | `assets` | Product requer papel e binding explicitamente declarados. |
| `product_groups[]`, `resource_documents[]`, `dossier_assessments[]`, `dossier_packages[]` | `assets` | Tipos distintos quando presentes; extras conservados. |
| `sources`, `source_crosswalk`, `frontiers`, `external_runs`, `coverage`, `dossier_batch` e demais campos | `unmapped_fields` | Tipos e lexemas com pointer e gaps, sem indicar história global. |

Linhagem de **código** R4 autorizado: repositório privado `thalesvalente/R4-RNF-RES-FIX`, SHA `5c145615c8a1bd601351badddccaf3acea474ed2`, lido sem abrir experimentos. Fonte/blobs: `src/r4/campaigns/notebook_projection.py` `6f9bbab047ec4af5802b2acffbab4a76032eacc4`; `atlas_rf_sources.py` `3470fc06cd5362b0aa468e57a6eca408b676a836`; `experiment_lineage.py` `da6697cd1b027acf482320f8e36d110c18beed29`; `atlas.py` `599652d947102a6b61cd9d9be37f4a4d84b92bb6`; `atlas_scientific_scope.py` `2860369beaae7ef2de9be0611b4be217705a6962`. Template `src/r4/presentation/atlas_assets/template.html` `cced3e3b2943272df0cac97f0123c0dce83dcbb2`, app.js `f38922c666b25d1a43d75cc1a3ad2456f07d348a`, graph-layout.js `1b6d4afa13a6a3b9f47779ad07636d3a52209e2c`, tables-coverage.js `c346b9414ce6d01d087d17bbfa2531911aaaef7b`. A lógica estrutural foi adaptada aos módulos públicos `legacy_v5.py` e `legacy_v5_descriptor.py`, sem transferir scripts executáveis, `innerHTML`, `file://`, credenciais, ID privado, dados de corpus, literal RF original, paths locais ou licenças de terceiros.

A F1 sanitizada observou **um** payload com 159 records, 2911 nós, 1595 arestas, 5 tabelas/152 linhas, 28 RF não admitidas e 858 parent_keys resolvidas. Os testes C2 reproduzem a **forma com valores inventados**; F1 não foi executada novamente e nenhum total global foi provado. A autenticação de fonte, limite operacional 256MiB/30s e isolamento OS/rede permanecem NÃO QUALIFICADOS.
