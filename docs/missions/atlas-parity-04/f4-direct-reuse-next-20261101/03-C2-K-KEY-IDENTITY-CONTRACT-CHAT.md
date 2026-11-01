# AP04-F4-C2-K-KEY-IDENTITY-CONTRACT-CHAT-01 — decisão arquitetural para a árvore real

`orq.audit@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions; documentação/contratos **somente**. **Raciocínio: Extra High**, selecionado pelo operador.  
**Repositório:** `thalesvalente/Atlas`. **Branch nova e exclusiva pré-criada:** `docs/atlas-parity04-f4-key-identity-20261101`, baseada no SHA F2 qualificado `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.
**Resultado:** `C2_K_IDENTITY_DECISION_READY_FOR_HUMAN_REVIEW`; **não** `APPROVED` nem `G4/G5/G6`.

## O que exige decisão

O código legado R4 tem três campos **distintos** em `lineage_graph.nodes[]`: `key` (identidade estrutural interna à fonte), `ui_id` (identidade de apresentação derivada), `native_id` (identidade nativa quando comprovada). `parent_key` e `edges.from_key/to_key` referem-se a **key**, não necessariamente ao native_id. F1 observou 2.911 nós, 1.595 relações e 858 parent keys explícitos que resolvem no contexto legado. O descriptor aprovado 0.2.0 resolve `reference.declared_id` por `identity.native_id` único no contexto. Assim, o mapeador C2 pode perder uma ligação visual legítima sem poder inventar native_id.

**Não é permitido** copiar key para native_id, inferir que ui_id é ID científico, resolver por nome/título, ignorar colisões, ou inventar Project/Experiment. `unmapped_fields`/gaps preservam texto mas não necessariamente a navegação original. Isso é uma incompatibilidade real de representação, não apenas falta de testes.

## Fontes fixadas

- `thalesvalente/R4-RNF-RES-FIX`, privado, `5c145615c8a1bd601351badddccaf3acea474ed2`: `experiment_lineage.py` (key/ui_id/native_id, parent_key, from_key/to_key, proof), `atlas_scientific_scope.py` e `experiment_lineage_presentation.py`.
- F2 contrato aprovado `c3ea1e82938fd61cc5a22fee973352715a5bb527`, `EPHEMERAL-PRESENTATION-CONTRACT.md`, `IDENTITY-AND-LOSS-POLICY.md`, ADR-0003 v0.2 com `APPROVED_SCOPED` PR #15 comentário `6539419419`; schema exato em `tools/atlas_legacy_presentation/descriptor.schema.json` SHA C2 `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`.
- C0 adendo reader003 `d498504cd2c4d230088f86e04e55624bbe32df79`.
- C1 F3A escalável `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`; F3B `72118073cc72b4d3cdca21fcc64c18cf742ae384`; C2 mapeador v5 `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`.
- AP04-POR-v1.0-draft, ARC-01–09 e seus gates G0–G9.

## Ownership e trabalho de arquitetura

**Pode escrever exclusivamente** `docs/missions/atlas-parity-04/f4-c2-key-identity/` com `RESULT.md`, `INPUT-SHAS.json`, `CURRENT-CONTRACT-COUNTEREXAMPLES.md`, `OPTIONS-AND-RISK.md`, `DESCRIPTOR-0.2.1-CANDIDATE.md` ou anexo mínimo de mesma semântica, `COMPATIBILITY-AND-MIGRATION-LESS.md`, `DECISION-REQUEST.md`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`.

**Não escrever** `EPHEMERAL-PRESENTATION-CONTRACT.md` histórico, ADR-0003 original, `GATES.json`, adendo C0 reader003, qualquer JSON schema executável, renderer F3A, parser C2, histórico de manifests, branch PR #18 ou PRs #15/16/17/19. Subagentes A comparação semântica, B opções e negatives, C revisão independente somente leitura; revisor real sem autoria, não simular.

## Alternativas a comparar, de forma executável

**O0 — sem alterar descriptor 0.2.0:** verificar se campos já aprovados permitem transportar `source key` e resolver parent/edges **sem usar native_id, sem violar `validate_descriptor` e sem perdas**. Produzir contraexemplos completos inventados: A) key diferente de native_id; B) key igual a native_id de outro registro; C) dois snapshots com mesma key; D) 50 colisões; E) key ausente/null. Se não passar todos, O0 é insuficiente.

**O1 — adendo semântico versionado delimitado para apresentação:** adicionar propriedade opcional original `source_key_literal` (ou referência equivalente com nome exato a definir) em node, e um tipo de referência de chave estrutural separado de native_id (por exemplo `reference_basis=SOURCE_STRUCTURAL_KEY` com `target_navigation_id` endereçando ocorrência ORIGINAL única e `source_id/snapshot_id`, mais `declared_key_literal`), preservando proof/evidence_locator. Não promover à ciência, não alterar Caderno. Discriminar key/source_ui_id/native_id, colisões não resolvíveis, parent_key declarado e link de UI derivado. Avaliar se versão deve ser **0.2.1** e como falha atômica rejeitar payload errado.

**O2 — camada de navegação somente UI anexada ao descriptor:** analisar se sidecar isolado é suficiente sem segunda fonte de autoridade. Por ser mudança de contrato/entrada ou schema, exigir ARC-09. Se causar dois formatos concorrentes, registrar custo/risco e não chamar solução mais simples automaticamente.

**O3 — reexecutar renderer antigo inteiro ou levar `r4.*` ao novo viewer:** contraria a separação O1/O3 aprovada; usar apenas como alternativa recusada/condicionada a nova decisão arquitetural.

Escolha recomendada deve minimizar diferença, manter backward compatibility com F3A/F3B, preservar JSON Schema Draft2020-12 fechado, revisão sintática e semântica do descriptor, quotas/TTL, unknowns/ausências, source/snapshot e `LEGACY_DERIVED`. Contrato 003 do C0 deve conservar exclusividade Caderno no Catalog/SDK. HL7/FHIR continua FUTURE_CAPABILITY_ONLY.

## Critérios de aceite documental

Gerar uma única solicitação humana clara e versionada por SHA: aprovar ou rejeitar atualização de contrato exclusiva de **navegação estrutural legada**. Incluir migrations de testes no viewer F3A e no leitor C2, comportamento de rejeição de versões desconhecidas, invalidação de tokens e atualização C3/C4. A aprovação da transferência de código privado NÃO é autorização para alterar descriptor/ADR; não inferir novo escopo.

Produzir fixtures originais inventadas (sem IDs/literais privados) que demonstrem árvore com parent_key resolvida e native_id ausente sem falsificar native_id. Nenhum teste de fonte real ou mudança de produto por K. Publique o parecer independente, os docs e os hashes Git; se a CI global de docs rejeitar novos paths, registre impasse de sucessão para C4, sem afrouxar guardas.

**Estado terminal:** `C2_K_IDENTITY_DECISION_READY_FOR_HUMAN_REVIEW` somente com contrato candidato/risco e review. Se O0 for demonstravelmente suficiente sem mudança, `C2_K_NO_CONTRACT_CHANGE_REQUIRED_VERIFIED`, com testes formais que provem compatibilidade; caso contrário nenhuma implementação da proposta antes de aprovação ARC-09. Sem merge, release, deploy, migração, limpeza ou alteração R4.

**END-OF-AP04-F4-C2-K-PROMPT — COMPLETE**
