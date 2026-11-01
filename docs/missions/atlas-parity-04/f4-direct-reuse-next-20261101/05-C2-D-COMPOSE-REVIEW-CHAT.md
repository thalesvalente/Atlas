# AP04-F4-C2-D-COMPOSE-REVIEW-CHAT-01 — compor parser R4 verdadeiro e isolamento nativo

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions e escrita. **Raciocínio recomendado: Extra High**, selecionado manualmente pelo operador.  
**Repositório:** `thalesvalente/Atlas`. **Branch existente e ÚNICA de integração C2:** `feat/atlas-parity04-f4-external-reader-20261031`, PR Draft #18. Não criar clone/worktree/branch adicional.  
**Resultado-alvo:** `C2_D_REAL_V5_READER_READY_FOR_HOST_PROOF` se parser real, transposição fiel, política OS e revisão/CI focal estiverem comprovados; caso contrário `C2_D_BLOCKED_EXACT`, sem alegar G4.

## 1. Pré-requisitos observáveis

Antes de alterar qualquer arquivo, confirmar por Git SHA/tree/parent:
- Baseline F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`.
- C2 original (histórico congelado) `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`, tree `f268d4cf450cf5baa73c5d51e34fc0d6fba3a59f`, manifesto de 22 entradas fixado.
- C2 v5 inicial `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, tree `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df`; **C2-A final deverá ser posterior** e qualificado no SHA próprio.
- C2-B `feat/atlas-parity04-f4-c2-os-isolation-20261101`: SHA final, testes OS executados, resultados e review reais, sem escrita em A.
- C2-K `docs/atlas-parity04-f4-key-identity-20261101`: parecer e decisão técnica. Se K exigir alterar descriptor 0.2.0, a **aprovação humana ARC-09 versionada da alteração** é PRÉ-CONDIÇÃO para código de novo schema e para declarar navegação completa. A aprovação anterior de transferência de código privado NÃO é aprovação de novo descriptor.
- L0 LOCAL: se houver testemunho autorizado da fonte real, usar SOMENTE o handoff sanitizado e sua decisão de liberação, sem solicitar bytes do corpus neste CHAT. Se L0 ainda não autorizado/executado, adaptar com base no código v5 fixado, mas nunca alegar compatibilidade dos arquivos Windows reais.
- Fontes: AP04-POR F4/G4/G5, ARC-01–09, ADR-0003 v0.2 `APPROVED_SCOPED` comentário PR15 `6539419419`, C0 adendo `d498504cd2c4d230088f86e04e55624bbe32df79`, C1 `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, F3B `72118073cc72b4d3cdca21fcc64c18cf742ae384` e R4 fonte privada `5c145615c8a1bd601351badddccaf3acea474ed2`.

Se C2-A ou B ainda tiver writer ativo, não iniciar composição. Não trocar a base silenciosamente. Um resultado K proposto não deve ser tratado como aprovado.

## 2. Ownership D depois dos congelamentos

D é o único writer final da PR #18, com autorização para:
- `tools/atlas_legacy_presentation/reader.py`, `__main__.py` e wrapper/entrypoint de produção;
- introduzir **exatamente os módulos novos do owner B** por blob Git revisado: `tools/atlas_legacy_presentation/os_...`; **não** editar o conteúdo importado sem nova autoria/revisão explícita;
- `scripts/qa/atlas_parity04_f4_c2_v5_evidence.py` ou sucessor `..._c2_d_...` que cubra paths precisos e toda ancestry, sem modificar manifesto antigo;
- workflow focal C2, novos testes integrados prefixados `test_atlas_parity04_f4_c2_d_...`, recibos `docs/missions/atlas-parity-04/f4-c2-composition/`.

A preservação de módulos parser/mapeador C2-A e históricos F1/F2 é obrigatória; se um finding exigir modificar A, registrar novo ownership, teste negativo e revisão independente, não editar silenciosamente. Não tocar shell, F3A/F3B, SDK, Catalog, servidor, reader003 original, Caderno, R4, PR15/16/17/19 ou guards globais C4.

**Composição Git sem história falsa:** como o verificador C2 exige história linear, não fazer merge commit de B por conveniência nem rebase/force. Inspecionar todos os commits B, rejeitar paths temporários não autorizados, conferir SHA/tree/parent/blob/mode, e adicionar os arquivos B à PR18 por commit NORMAL de um pai com OIDs exatos e recibo `SOURCE-BLOB-PROVENANCE.json`. Declare expressamente que B **não é ancestral Git da PR18**; sua identidade fica recuperável por ref/SHA e prova de igualdade dos blobs, sem chamar isso merge. O integrador F4-C3 tratará toda fonte da mesma maneira por SHA.

Subagentes: A integração worker/acquisition, B CI/ameaças, C **revisão independente read-only de todo o SHA final**, com coordenador único writer, quando ferramentas nativas verdadeiras existirem. Caso contrário executar sequencialmente, marcar QA pendente e não simular revisão.

## 3. Engenharia real de aquisição protegida

1. `reader.prepare` deve consumir **o export R4 `r4-experiment-viewer-v5`** já produzido (`index.html` com `script#data` ou JSON real declarado), nunca o perfil fictício de origem. `ATLAS-ATUAL.html` é ponteiro, não seguir automaticamente, alvos precisam de autorização exata. Manter perfil inventado somente para testes em função/flag isolada, **recusar uso do modo sintético com acervo real**.
2. Antes de abrir a fonte, invocar supervisor/worker B com confinamento OS verificado, Job Object/limite 256 MiB + deadline wall de 30 s + restrição independente de filesystem/rede. Se algum controle não estiver disponível ou validado na plataforma da execução, **falhar antes de abrir** com códigos `HARD_BUDGET_UNVERIFIED` ou `OS_ISOLATION_UNVERIFIED`. Não usar checagem cooperativa como substituto.
3. Allowlist exata por fonte/snapshot, sem descoberta/varredura, symlink/reparse/hardlink/UNC/device/ADS/traversal; mesma-handle identity/hash/size/mtime antes e depois; scratch privado fora dos originais e repo, escrita atômica, TTL≤3600s e cleanup restrito a derived files próprios.
4. Parser e mapper reais de A devem conservar `records` e `lineage_graph.nodes` distintos, tabelas, ID/células e relações, missing/null, gaps, colisões e 28 RF não admitidas conforme fonte selecionada — nunca usar contagens F1 como validação universal de qualquer outro snapshot.
5. Resolver source-key somente com semântica aprovada e prova inequívoca. Se o contrato 0.2.0 não expressar parent_key estrutural, manter gaps e **bloquear afirmação de árvore real integral** até K ser aprovado e implementado por SHA. Não fabricar `native_id`. Se atualização v0.2.1 aprovada, implementar somente diff aprovado com validação de versão e regressão do 0.2.0.
6. `Legacy-derived` não é autorização científica, confiabilidade ou compatibilidade HL7/FHIR. Não introduzir `r4.*` no wheel Atlas/SDK; independência dos wheels, Caderno/RO-Crate/Process Run deve continuar provada.

## 4. Testes e provas por SHA

Windows/Ubuntu × Python normal/-O para parser/mapeador, 51 casos iniciais + testes A e B completos + negativos de execução de arquivo, timeout real, memória, rede/FS, filhos, TOCTOU, source-key colidente, 2911/1595 e 5 tabelas. **Nenhum teste simulado de OS substitui prova real**. Sem skips em testes aplicáveis; o único skip ACL-Windows-no-Ubuntu deve continuar claramente contextualizado, não passar como zero skip global.

Verificador de sucessão: preservar manifesto 22 entradas C2 original por SHA; revisar commits A e B, explicitando B por blob provenance; CI de cada novo HEAD/commit final; zero alteração transitória fora de ownership, mesmo revertida. Guards AP04/P06/C4 globais podem rejeitar novos paths: não desligá-los, transferir reparo ao F4-C4 após composição.

Entregar `RESULT.md`, `INPUT-SHAS.json`, `COMPOSITION-OBJECTS.json`, `SOURCE-BLOB-PROVENANCE.json`, `SECURITY-AND-HARD-BUDGETS.json`, `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`, código e testes em Git. Revisão independente no SHA final e recibos externos de Actions na PR18. Um commit posterior de fechamento exige novo SHA e QA/CI.

**Estados:**
- `C2_D_REAL_V5_READER_READY_FOR_HOST_PROOF` somente se parsing v5, contrato, imposição OS em runner, CI focal e revisão passarem. Isso ainda NÃO é G4 LOCAL.
- `C2_D_CODE_COMPOSED_HOST_GATE_UNVERIFIED` quando código seguro está publicado, mas faltam provas OS/host. Isso não satisfaz a dependência C3 de C2 qualificada.
- `C2_D_SOURCE_KEY_DECISION_PENDING` quando a árvore real exige decisão K; não liberar navegação global.
- `C2_D_BLOCKED_EXACT` para blockers restantes, com caminho/SHA/contraprova e ato mínimo.

**Não executar acervo privado neste CHAT, F4-C3/C4/F5, reprocessamento R4, migração, merge main, release, deploy, promoção, limpeza ou alteração de fontes.**

**END-OF-AP04-F4-C2-D-PROMPT — COMPLETE**
