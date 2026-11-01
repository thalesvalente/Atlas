# F4 C2 — implementação do parser real Atlas R4 v5

**Autorização:** o operador concedeu explicitamente permissão para reutilizar e transferir o código necessário de `thalesvalente/R4-RNF-RES-FIX` (privado) para `thalesvalente/Atlas` (público), em 2026-10-31. A autorização não transfere experimentos, segredos, arquivos de corpus, paths locais ou direitos de terceiros. Revisão de licença e privacidade permanece obrigatória.

**Fonte de código por SHA:** R4 `5c145615c8a1bd601351badddccaf3acea474ed2`, especificamente `src/r4/campaigns/atlas.py`, `notebook_projection.py` e `presentation/atlas_assets/template.html`. As regras de validação foram adaptadas para um módulo público original sem importar `r4.*`, chamar produtores ou executar scripts.

**Implementado nesta etapa:** `parser.parse_source(..., source_profile="r4-v5")` extrai JSON inerte de `<script id="data" type="application/json">` e reconhece exatamente `r4-experiment-viewer-v5`; `legacy_v5.py` verifica arrays/identidades/referências e mantém **records e lineage_graph como populações distintas**. `inspect_legacy_projection()` devolve apenas contagens e estados sanitizados, não dados de uma fonte privada.

**O que NÃO foi implementado ainda:** conversão integral para descriptor 0.2.0; aquisição real, execução com limites duros de 256 MiB/30 s e isolamento FS/rede por SO. `reader.prepare` e a CLI permanecem fail-closed para dados reais; G4/G5/G6 não são qualificados. Não usar `--synthetic-fixture` com legado real.

**Teste:** o conjunto `test_atlas_parity04_f4_c2_real_v5.py` usa valores inventados com o FORMATO REAL de exportação; não cria um novo perfil de origem sintético. Exercita HTML inerte, chaves duplicadas, rejeições, lexemas numéricos, separação de 159 records e grafo de 2911 nós e nulidade do native_id.

**Próxima etapa de engenharia:** mapear o grafo e as tabelas para o descriptor 0.2.0, preservando native_id distinto das chaves `key`/`ui_id`, gaps e a identidade source/snapshot/occurrence. Confirmar se `reference.target_navigation_id` em 0.2.0 pode transportar parent_key explícito quando `native_id` é ausente; se não puder, preparar atualização de contrato por ARC-09, sem falsificar native IDs.

**CI real:** conferir o SHA publicado em GitHub Actions. Os 6 gates globais históricos devem permanecer fail-closed até sucessão exata na F4 C4. Nenhum patch em manifesto histórico ou bypass.
