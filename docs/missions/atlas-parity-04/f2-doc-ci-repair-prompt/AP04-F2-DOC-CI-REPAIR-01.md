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
4. Preservar sem alterações `scripts/qa/atlas_parity02_p06_audit.py`, seu RED histórico para ADR-0003 e a exceção AP04 por **path e blob específicos**, sem liberação de `docs/architecture
