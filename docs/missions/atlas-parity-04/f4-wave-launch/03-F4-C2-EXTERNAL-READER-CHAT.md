# AP04-F4-C2-EXTERNAL-READER-CHAT-01 — ferramenta O1 externa, sem converter acervo

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions (sem host privado). **Esforço:** Extra High, seleção manual.  
**Destino:** `thalesvalente/Atlas`, branch convencional própria pré-criada `feat/atlas-parity04-f4-external-reader-20261031`, da F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3` (tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`).  
**Referências:** F1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, contrato/ADR0.2 `c3ea1e82938fd61cc5a22fee973352715a5bb527` e aprovação `APPROVED_SCOPED` comentário PR #15 `6539419419`.  
**Meta:** `F4_C2_EXTERNAL_READER_READY_FOR_LOCAL_QUALIFICATION`. Isso NÃO comprova G4 com legado real.

## Contrato e limites

O1 exige processo **LOCAL externo** ao runtime/distribuição do Atlas, com leitura somente de projeções legadas preexistentes e explicitamente autorizadas. O2 migração em massa foi rejeitado nesta etapa. O3 File API/painel é responsabilidade C3. Preservar ARC-01–09, AP04-POR F4, RO-Crate 1.3/Process Run 0.6/Caderno 0.1.0a1 e HL7/FHIR como capacidade futura, não como implementação.

**Ownership exclusivo:** `tools/atlas_legacy_presentation/` (tool original público, fora dos wheels e sem import R4), harness/testes/fixtures sintéticas `atlas_parity04_f4_c2_*`, `.github/workflows/atlas-parity04-f4-c2-reader.yml` se necessário e recibos `docs/missions/atlas-parity-04/f4-c2-reader/`. Não tocar shell, reader003, Catalog/server/SDK, F3A/F3B, F1/F2, manifests/guards globais ou projeto R4. Subagentes A parser, B QA/segurança, C revisor independente, coordenador único writer. Sem worktree/clone/branch extra.

## Implementar, não apenas planejar

1. Criar utilitário/CLI explícito que aceite **arquivo exato** pré-autorizado + allowlist de paths exatos + scratch privado separado. Proibir varredura de drive, glob, recursão, execução de pipeline R4/HTML/JS, links externos, provider, symlink/reparse/traversal/UNC/device e leitura fora da allowlist. Não reconstruir/copiar o leitor Windows suspenso.
2. Parser JSON/JSON-LD ou JSON embutido em HTML **inerte** somente quando delimitado por formato conhecido. Se o payload exigir executar script ou depender de schema privado não observado, emitir `SOURCE_FORMAT_UNSUPPORTED` e pedir uma amostra estrutural **sanitizada** para a L1, sem inventar mapping no Git.
3. Transformar **em memória** `records`, `edges`, `result_tables`, `product_items`, `resource_documents` (somente campos comprovados) num JSON **temporário** descriptor `atlas-legacy-presentation` 0.2.0 com identidade fonte/snapshot/ocorrência, `LEGACY_DERIVED`, status e perdas. Nunca inventar record_id, native_id, categoria, vínculo árvore→RF, relações causais, aprovação científica ou quantidade global.
4. Preservar tabelas/linhas/cabeçalhos e ordinais, literais, lexemas de números, unidade/precisão, MISSING ≠ null ≠ vazio ≠ zero, linhas não admitidas, 4 tabelas sem record vinculado, Run externo isolado, null endpoints, unresolved, colisões, repetidos, `unmapped_fields`, `gaps` e denominador UNKNOWN. Campo impossível de preservar exige recusa/relatório claro, não truncamento silencioso.
5. Aplicar JSON Schema Draft2020-12 aprovado e **validação semântica** adicional de referências, identidades, fontes/snapshots, quotas, estados e tipo das células. Os exemplos F2 são sintéticos e não prova de compatibilidade com bytes do R4; a L1 fará essa validação LOCAL.
6. Verificar SHA-256/tamanho/mtime da origem antes e depois, rejeitar mudança durante leitura. Escrita única em scratch temporário privado por operação explícita/atomicamente, TTL até 60 min, remover apenas derivados próprios, nunca tocar fonte. Hash não prova autenticidade.
7. Implementar limites de bytes/quota propostos em F2: 3 fontes/64MiB cada/192MiB total, descriptor 32MiB, depth20, 10k nós/100k relações, 128 tabelas, 100k linhas, etc. Orçamento duro de 256MiB/30s por abertura: usar mecanismos verificáveis por SO ou marcar `HARD_BUDGET_UNVERIFIED` e bloquear G4, sem apresentar timeout cooperativo como isolamento duro.

## Provas e saída

Testes Windows/Ubuntu × normal/`-O` exclusivamente com fixtures **inventadas** e negativas: HTML/JS hostil inerte, paths não allowlisted, traversal/symlink/reparse, fonte modificada durante leitura, quota excedida, schema inválido, string numérica/inteiro grande, null/missing, quatro tabelas sem vínculo, 28 não admitidas e source+snapshot collisions. Não executar dados privados no CHAT.

Construir SDK/viewer públicos em isolamento sem a ferramenta; provar que Atlas e Caderno instalam/executam **sem** esse utilitário e que ele não entra no wheel. CI focal por SHA, JSON/JUnit, review independente C sem autoria, dados sintéticos somente. A CI global pode rejeitar novos paths por guard congelado; registrar o impasse para C4, não enfraquecer controles.

Publicar código/testes e `RESULT.md`, `INPUT-SHAS.json`, `READER-CONTRACT.md`, `SECURITY-AND-LIMITS.json`, `NEGATIVE-TESTS.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` no Git da branch C2, com SHA/tree/parent e verificação própria. Nada de ZIP somente em sandbox.

**Sucesso:** `F4_C2_EXTERNAL_READER_READY_FOR_LOCAL_QUALIFICATION` = tool público qualificado sobre fixtures, **não** geração de descriptor real/aceite G4/G5/G6. Se faltar o schema de fonte ou imposição segura de orçamento, `F4_C2_BLOCKED_EXACT` e contrato de input mínimo para L1, sem fingir funcionalidade. Não começar F3/F5/F6 ou migrar R4.

**END-OF-F4-C2-PROMPT — COMPLETE**
