# AP04-F4-L0-LOCAL-REAL-SOURCE-WITNESS-01 — testemunhar o export REAL já existente

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente obrigatório: Codex LOCAL no host Windows, não CHAT.** Raciocínio recomendado: **High** (Extra High opcional quando houver divergência estrutural), escolhido manualmente pelo operador.  
**Repositórios:** Atlas para leitura de contratos; R4 original e seus arquivos apenas nos caminhos efetivamente autorizados. **Não fazer checkout, worktree, clone, git clean, git reset, rebuild, migração, leitura de diretórios por glob ou scan de drives.**  
**Alvo restrito:** `F4_L0_REAL_SOURCE_SHAPE_WITNESSED_SCOPED`, ou `F4_L0_SOURCE_NOT_AUTHORIZED` / `F4_L0_STRUCTURAL_GAP_EXACT`. Este precursor **não** declara G4/G5/G6 ou compatibilidade operacional.

## 1. Escopo de leitura: conferir antes de abrir

Leia primeiro os recibos PRIVADOS já criados pela F1/G1 no host, vinculados ao pacote público sanitizado `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`. F1 identificou três arquivos exatos: uma captura JSON, um HTML de redirecionamento e o HTML alvo preexistente autorizado. **Não inferir novos caminhos nem expandir a lista.** Reutilizar apenas metadados/estrutura que já estejam nos recibos sem reabrir a fonte, quando suficientes.

**A autorização humana explícita de copiar código privado R4 para Atlas público NÃO concede por si só nova autorização para abrir arquivos científicos em F4.** Antes de qualquer releitura de fonte, confirmar uma autorização F4-L0 que identifique aqueles três paths exatos, operação read-only e finalidade de inspecionar FORMATO, com proibição de publicar dados privados. Se a mensagem do operador que iniciou L0 não autorizar esses paths por identidade, NÃO ler os arquivos; entregar `F4_L0_SOURCE_NOT_AUTHORIZED` junto do inventário dos recibos F1 realmente acessíveis.

O operador pode registrar no próprio início da execução, se desejar: "Autorizo para a F4-L0 apenas a leitura somente leitura dos três arquivos já identificados nos recibos privados F1, sob a mesma allowlist exata e limites de bytes; nenhuma outra fonte, modificação ou publicação de valores privados." O executor deve confirmar a identidade real dos três paths nos recibos, não interpretá-la como permissão de explorar pastas vizinhas.

## 2. Referências normativas e código-fonte observado

- F1 sanitizada: `docs/missions/atlas-parity-04/f1-legacy-inventory/SANITIZED-HANDOFF.json`, SHA F1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`.
- Código produtor R4 PRIVADO SHA `5c145615c8a1bd601351badddccaf3acea474ed2`: `src/r4/campaigns/atlas.py` e `notebook_projection.py`, `experiment_lineage.py`, `atlas_rf_sources.py`, `presentation/atlas_assets/template.html` e `tables-coverage.js`.
- Adaptador Atlas C2-A `legacy_v5.py`/`legacy_v5_descriptor.py` na PR #18 a partir de `e349a09d439d292011bca4c0994cf8ab3e3fbf9f` (identificar HEAD efetivo pelo Git), descriptor aprovado F2 `c3ea1e82938fd61cc5a22fee973352715a5bb527`, contrato C0 `d498504cd2c4d230088f86e04e55624bbe32df79` e AP04-POR-v1.0-draft.
- O formato de origem é `r4-experiment-viewer-v5` quando declarado no arquivo real, e `lineage_graph` pode declarar `r4-experiment-lineage-a10-v1`. Não presumir compatibilidade somente porque o código fonte implementa essa revisão.

## 3. Observações concretas e limitadas

1. Conferir origem exata do HTML com redirect, o alvo **já identificado e autorizado** e, se disponível na mesma allowlist, recibo do build; não seguir links automaticamente nem abrir arquivos referenciados no conteúdo. Não invocar browser, scripts legados, `atlas.build`, notebooks, inferência, testes E2E, provider ou qualquer gerador.
2. Fazer extração inerte somente do único `<script type="application/json" id="data">` que o antigo produtor usava; se houver zero/múltiplos blocos, perfil inesperado, tag não inerte ou necessidade de executar JS, retornar `SOURCE_FORMAT_UNSUPPORTED`. A leitura JSON deve rejeitar chaves duplicadas, NaN/Infinity e UTF-8 inválido, sem modificar o arquivo.
3. Inspecionar **somente estrutura**: `schema`/`authority`, chaves top-level, tipos e cardinalidades, arrays records/edges/result_tables, mapping de `rows[].cells`, chaves `native_id`, `nucleus_id`, ID/descrição/critérios, ocorrências de `MISSING`, localização de `record_id`/`run_id` e `binding_gap`.
4. Inspecionar a **camada independente de linhagem**: `lineage_graph.schema`, `nodes[].key`, `ui_id`, `native_id`, `parent_key`, `edges[].from_key/to_key`, status/proof, campos opcionais e se as **858 parent keys** resolvem por source key mesmo quando native_id é nulo/diferente. Registrar contagens, jamais publicar valores, IDs privados ou pointers privados sem liberação.
5. Confrontar contagens da F1 no mesmo snapshot, sem forçar correspondência: 159 records, 2911 lineage nodes, 1595 edges, cinco tabelas de 39/85/28/0/0 linhas (152 total), 28 RF não admitidas, quatro tabelas sem `record_id` resolvido, 22 endpoints null, 75 unresolved, 50 colisões, grupos repetidos e Run isolado. Se arquivo mudou desde F1, declarar `SOURCE_DRIFT` e capturar prova privada; nunca editar a fonte para coincidir.
6. Confirmar somente leitura: SHA-256/tamanho/mtime/identidade dos três arquivos realmente lidos antes/depois, nenhuma escrita em original ou R4. Não executar `reader.prepare` em modo real nesta L0: o bloqueio HARD_BUDGET/OS_ISOLATION é legítimo até C2-B e L1. **Não usar `--synthetic-fixture` com bytes reais.**
7. Verificar se a estrutura da fonte REAL cabe no parsing/mapper C2-A (inclusive `source_key` com `native_id` ausente) e no envelope F2. Se falhar, registrar caso mínimo com valores TODOS INVENTADOS, localização privada do erro e estado `PROFILE_VARIANT_UNVERIFIED`/`KEY_BRIDGE_CONTRACT_REQUIRED`; não enviar bytes originais ao GitHub.
8. O resultado público deve ser sanitizado e conter apenas nomes estruturais não sensíveis já existentes no contrato público, tipos, contagens autorizadas, flags e contraexemplo inteiramente inventado; nunca caminho Windows, hash de fonte, tamanho identificador privado, literal RF, nome cliente, screenshot real ou payload.

## 4. Área de recibos e preservação

Usar exclusivamente a raiz privada de recibos previamente autorizada para F4, ignorada pelo Git, p.ex. `.local/atlas-parity04-f4-l0/` **somente se estiver sob path privado autorizado e gravável**, sem sobrescrever recibos F1 nem mudar ACL/configurações. Não criar worktrees/clones ou mexer no checkout de outros owners; se escrita privada negada, `WORKSPACE_WRITE_BLOCKED`.

Arquivos internos `SOURCE-SELECTION.private.json`, `SOURCE-STRUCTURE.private.json`, `SOURCE-INTEGRITY.private.json`, `PROFILE-COUNTEREXAMPLES.private.md`, `RESULT.private.md`, `INDEPENDENT-REVIEW.private.md` quando revisão real disponível e manifesto local. Arquivos exclusivamente públicos após sanitização/QA: `REAL-V5-SHAPE.sanitized.md`, `REAL-V5-SHAPE.sanitized.json`, `HANDOFF.sanitized.json`. Conteúdo dos arquivos privados deve permanecer no host; não usar arquivos anexados a outro chat para contornar a autorização.

Para persistência Git-first, um publisher CHAT separado pode receber apenas o handoff sanitizado **explicitamente aprovado para publicação** e publicá-lo em branch documental exclusiva, por SHA. Se o operador não liberou essa publicação, registrar `PUBLIC_SANITIZATION_NOT_AUTHORIZED` e preservar os bytes privadamente.

**PASS escopado:** perfil real e suas diferenças comprovados contra recibo/F1 e estrutura observada, integridade antes/depois e revisão de privacidade. Não afirma aquisição operacional isolada, compatibilidade do novo viewer, G4, G5, G6 ou ciência.

**END-OF-AP04-F4-L0-PROMPT — COMPLETE**
