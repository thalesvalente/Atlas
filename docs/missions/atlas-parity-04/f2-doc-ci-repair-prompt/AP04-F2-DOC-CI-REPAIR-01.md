# AP04-F2-DOC-CI-REPAIR-01 — sucessão documental F1/F2 com CI estrita

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub + GitHub Actions, com escrita real. **Não LOCAL.**  
**Esforço:** **Extra High**, escolhido manualmente pelo operador; não inventar o nível efetivo.  
**Destino Git único:** `thalesvalente/Atlas`, PR Draft #15, branch existente `docs/atlas-parity04-f2-legacy-contract-20261030`.  
**Meta:** `AP04_F2_DOCUMENTATION_CI_QUALIFIED`, apenas após CI terminal e revisão independente no SHA final.

## Entradas fixadas

- C4: `72d9b94e613a57c82a5afd309796f44b271e2185`, tree `0a622663ca40232d6143659f82cfe9ce43702e90`.
- AP04 plano/CI PR #14: `47c94d27aeb7717eebb30804f01cd2cd33507c8a`, tree `a02e8b6e6d82a743de4a31e9835c3d18e29d8947`.
- F1/G1: `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, tree `e0626cd274948a9303774593e20ca05fc1d32d62`.
- F2 técnico: `c3ea1e82938fd61cc5a22fee973352715a5bb527`, tree `986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c`.
- PR #15 HEAD F2: `04373bb910db2e6215cc8bc4212093b649e48456`, tree `611306f28557f5d9e27db49108880004399f5768`, parent `c3ea1e82938fd61cc5a22fee973352715a5bb527`.

Confirme todos os commits, árvores, parents, blobs e manifests antes de qualquer escrita. Leia `AP04-POR-v1.0-draft`, D-001–D-020, PAR-001–015, ARC-01–09, ADR-0001/0002/0003, F1/F2, `GATES.json` e `DECISION-REQUEST.md` pelos SHAs publicados. **ADR-0003 v0.2 e descriptor 0.2.0 continuam PROPOSED_NOT_APPROVED; G4 continua pendente.** Sem aprovação, implementação de File API, F3–F6 ou alteração do Caderno.

## Diagnóstico real do SHA F2 original

Seis workflows terminaram `failure`:
- AP04 documentation successor `41119159266` — `Unexpected path in complete C4 successor delta`.
- P06 frozen-boundary QA `41119159241` — guard AP04 recusa F1/F2.
- P03 isolated qualification `41119159203` — dispatch de CI falha no guard.
- C4 full composition `41119159306` — C4_INPUT_SUMMARY falha na sucessão.
- ATLAS003 Spec Kit `41119159205` — guard/dispatch.
- ATLAS021 `41119159228` — verificação instalada falha; browser/referência obtiveram sucesso parcial.

Raiz comum comprovada: `scripts/qa/atlas_parity04_doc_ci.py`, especialmente `verify_final_delta()` e `verify_linear_repair_history()`, só permite DOC_PATHS e REPAIR_PATHS da PR #14, negando os documentos F1/F2. Se houver falha independente depois, investigar sem mascarar.

## Política multiagente e ownership

Até três agentes nativos reais, quando disponíveis: A — Git/proveniência/guard e seus testes; B — dispatch/workflows/gates de CI com arquivos exclusivos; C — revisor independente somente leitura, sem autoria, no HEAD terminal. Coordenador único writer dos paths compartilhados. Se indisponíveis, executar engenharia segura sequencialmente, registrar `NATIVE_SUBAGENTS_NOT_AVAILABLE` e **não** afirmar revisão independente.

Não criar worktrees, clones, novas branches/PRs de implementação, merges, rebase ou force-push. Nenhum acesso ao host/acervo privado. Trabalho exclusivamente na branch existente da PR #15. Se o plano necessitar de mudança, preparar solicitação formal com justificativa, alternativas, efeitos e aprovação aplicável **antes** de implementar; não alterar silenciosamente AP04-POR.

## Engenharia requerida

1. Verificar por árvores Git **5 documentos F1** (2 prompts/insumos, 3 handoffs sanitizados) e **14 documentos F2** (2 insumos, 12 resultados). Ancorar os 19 caminhos **exatos** em SHAs, Git blobs, hashes, modos 100644 e genealogia. Não conceder permissão à pasta inteira.
2. Modelar épocas **C4 → AP04 original+reparo → F1 → F2 → novo reparo**. Congelar a história de F1/F2 e verificar todas as mudanças intermediárias, inclusive alteração ilícita revertida. Não aplicar retrospectivamente a allowlist exclusiva de reparo da PR #14 a commits legítimos F1/F2. Restringir o novo delta aos commits APÓS F2 terminal.
3. Criar sucessor/overlay **suplementar, canônico, fail-closed** para F1/F2 e paths técnicos do reparo, com ownership/purpose exatos; **nenhum manifesto histórico C1/C2/C3/C4/AP04/F1/F2 pode ser reescrito**. Recalcular hashes de overlay não deve permitir alterar fluxo semântico do guard, oráculos, testes ou dispatch; provar autorização independente de controle.
4. Preservar sem alterações `scripts/qa/atlas_parity02_p06_audit.py`, seu RED histórico para ADR-0003 e a exceção AP04 por **path e blob específicos**, sem liberação de `docs/architecture/**`, `.github/**`, `scripts/**`, `tests/**`, `docs/**`.
5. Manter `scripts/qa/atlas_parity02_p06_audit.py` inalterado e fail-closed; a exceção AP04 para ADR-0003 é somente path+blob histórico exato. `docs/architecture/` nunca vira allowlist ampla.
6. Preservar Spec Kit CLI 1.2.3, managed assets, pins SHA completos e controle `scripts/qa/speckit_audit.py` sem bypass.
7. Preservar C4, seus manifests e declarações `INPUTS`, `COMPOSITION`, `COMPOSITION_TREE`, `P03_C4_ADAPTERS`, `ASSETS`; nenhum teste ou oracle de produto pode ser enfraquecido.
8. Fazer dispatch por ancestry e identidade Git de P03 isolada, C4, AP04, F1 e F2; proibir `github.head_ref`, `github.ref_name` e nomes parecidos de branch como autorização.
9. Fixar antes da edição uma lista exata de arquivos/purposes de autoria do novo reparo F2, guard/CI/testes e recibos. Nenhum outro path ou diretório fica autorizado.
10. Não implementar neste reparo a ADR-0003, File API, UI legada, R4, Caderno, schema, protocolo ou migração; se houver desvio de plano, registrar solicitação, justificar e aguardar aprovação ANTES da implementação.

## 5. Contraprovas de segurança e teste negativo

Em repositórios sintéticos temporários, com Python normal e `-O`, testar pelo menos:

- PASS: C4/AP04/F1/F2 exatos, seus modos/parents/SHAs/árvores/manifests/blobs, com sucessor técnico legítimo restrito.
- RED: adicionar qualquer arquivo não autorizado nas épocas ou no novo reparo, inclusive `docs`, `scripts`, `.github`, `tests`, protocolo.
- RED: editar, excluir, renomear, usar symlink/gitlink ou mudar mode de qualquer um dos 19 documentos F1/F2.
- RED: commit temporário não autorizado, depois revertido, mesmo com árvore final aparentemente correta.
- RED: modificar ADR-0001/0002/0003, ADR-0003 candidata F2, constituição, GATES, plano, fixtures, Caderno, schema, contextos, skills, AGENTS.
- RED: editar/recalcular manifest histórico para legitimar bytes diferentes, ou overlay não canônico, duplicado, faltante, traversal, permissão de pasta ampla.
- RED: relaxar guard/dispatcher/oráculo e recalcular seu manifesto; a autorização independente deve falhar.
- RED: mudar C4 `INPUTS`, `P03_C4_ADAPTERS`, `ASSETS`, `COMPOSITION` ou remover teste adversarial.
- RED: branch lookalike sem ancestry, seleção errada de workflow, ação sem pin SHA completo, `continue-on-error`, `paths-ignore`, `|| true`, `if: false`, skip/xfail.
- RED: declarar ADR F2 APPROVED, G4 PASS, alterar reader003 sem decisão ARC-09, trocar o conjunto de testes herdados por um subconjunto ou usar recibos de SHA anterior.

Executar casos positivos e negativos com testes reais, 0 skips, JSON/JUnit atribuídos ao SHA e sem `assert` que seja eliminado em `-O` nos guards de segurança. Testes sintéticos NÃO substituem ações reais no GitHub.

## 6. CI terminal no SHA novo e revisão independente

Publicar o reparo por commits normais e fast-forward **somente na branch existente da PR Draft #15**. Sem novas PRs, worktrees, clones, rebase, force ou merge.

Os **seis workflows** originais precisam terminar `completed/success` no **mesmo SHA FINAL**:
- `ATLAS-PARITY-04 documentation successor` (run anterior `41119159266`);
- `ATLAS-PARITY-02 P06 frozen-boundary QA` (`41119159241`);
- `ATLAS-PARITY03 P03 isolated qualification` (`41119159203`);
- `ATLAS-PARITY-03 C4 full composition` (`41119159306`);
- `ATLAS003 Spec Kit contract checks` (`41119159205`);
- `ATLAS021 candidate verification` (`41119159228`).

Cobertura Windows/Ubuntu e Python normal/otimizado `-O`, zero skips/loader errors/falhas. Manter **todos os 191 IDs herdados** (168 C4 + 23 AP04), mais IDs novos de regressão, sem substituir/duplicar os originais. Não inventar número de testes caso a suíte aumente.

Validar SDK/viewer instalados fora do checkout, ausência de dependência R4, browser C4 integrado, HTTP/Chromium P03, navegador P06/troca de pacote, teclado, reflow, origem/CSP, Spec Kit 1.2.3 e ASSETS declarados. Conferir logs/JSON/JUnit/artefatos e screenshots no SHA executado; CI anterior não passa automaticamente no novo SHA. Uma falha nova deve ser diagnosticada, não silenciada.

Revisor independente nativo REAL, sem autoria, confere o SHA terminal com diffs e ancestry completos, contraprovas, manifestos, logs e todos os jobs. Se um commit posterior completar recibos, CI e revisão devem abranger esse SHA posterior.

Não confundir CI de engenharia com prontidão operacional LOCAL, aprovação científica ou conformidade HL7/FHIR.

## 7. Handoff público no Git e controle de escopo

Persistir, no mesmo ramo da PR #15, o código/QA e os documentos públicos necessários sob `docs/missions/atlas-parity-04/f2-doc-ci-repair/`:

- `RESULT.md`;
- `INPUT-SHAS.json`;
- `REPAIR-OWNERSHIP.json`;
- `SUCCESSOR-CONTRACT.md`;
- overlay e manifesto suplementar canônicos, sem alterar manifestos históricos;
- `NEGATIVE-TESTS.json`;
- `CI-EVIDENCE.json`;
- `DECISION-COMPLIANCE.md`;
- `INDEPENDENT-REVIEW.md`;
- `HANDOFF.json`;
- `MANIFEST.sha256`, sem auto-inclusão.

Cada path técnico modificado deve ter owner, propósito, teste/contraprova e autorização exata. Não publicar dados de corpus privado, RF literal, caminhos do Windows, URLs/IDs particulares ou documentos sensíveis. O usuário usa múltiplos chats, então NÃO depender de ZIP temporário ou download manual: **Git por SHA é a fonte durável**.

PR #15 fica aberta e Draft, sem merge, release, deploy, promoção, migração, R4, limpeza ou alteração da fonte. Documento técnico F2, ADR e DECISION-REQUEST não podem ser modificados para acomodar CI.

## 8. Critérios terminais e verificação do próprio prompt

**`AP04_F2_DOCUMENTATION_CI_QUALIFIED`** só quando os seis workflows passaram no MESMO SHA final, negativos e IDs herdados verificados, controles históricos preservados, revisor independente real sem findings bloqueantes e handoff público por SHA.

**`AP04_F2_DOC_CI_BLOCKED_EXACT`** quando houver bloqueio: registrar job/step/arquivo/SHA, razão, o trabalho ainda válido já publicado e menor ato autorizado. Não inventar CI, revisão ou sucesso.

ADR-0003 v0.2, descriptor 0.2.0, G4 e toda autorização de implementação de F3A/F3B/F4/F5/F6 continuam `PENDING_HUMAN_DECISION`; o pacote técnico vinculado é `c3ea1e82938fd61cc5a22fee973352715a5bb527`. CI verde não substitui a aprovação do usuário.

**Validação do texto de missão:** antes de agir, conferir os títulos iniciais `## Entradas fixadas`, `## Diagnóstico real`, `## Política multiagente` e `## Engenharia requerida`, as seções 5–8 e o marcador terminal abaixo. Se algum estiver ausente, declarar `PROMPT_SOURCE_TRUNCATED` e não usar versão parcial.

**END-OF-MISSION-PROMPT — AP04-F2-DOC-CI-REPAIR-01 — COMPLETE**
