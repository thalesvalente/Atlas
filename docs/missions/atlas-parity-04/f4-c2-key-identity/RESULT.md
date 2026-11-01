# AP04 F4 C2-K — resultado técnico e escopo

**Missão:** AP04-F4-C2-K-KEY-IDENTITY-CONTRACT-CHAT-01.
**Conclusão técnica:** `O0_INSUFFICIENT_O1_RECOMMENDED_CONDITIONALLY`.
**Gate de conclusão integral:** `INDEPENDENT_REVIEW_PENDING` e `ARC09_HUMAN_APPROVAL_PENDING`. Não reivindicar `C2_K_IDENTITY_DECISION_READY_FOR_HUMAN_REVIEW` sem revisão real por autor distinto.
**Autoridade:** `LEGACY_DERIVED`, não científica.

## Evidência verificável

R4 privado, **apenas código** no SHA `5c145615c8a1bd601351badddccaf3acea474ed2`: `experiment_lineage.py` usa `key` como identidade estrutural única e `bykey` para ligações; `ui_id` é identidade DERIVED_UI criada por `uid`; `native_id` pode ser null e só indica identidade nativa comprovada. `parent_key` e `edges.from_key/to_key` referem-se à `key`; as pontas gráficas de apresentação derivam `ui_id`. `experiment_lineage_sources.py` possui nós com chave original e native_id ausente, ligados a parent_key explícito. São **três namespaces distintos**.

O schema fechado 0.2.0 em `tools/atlas_legacy_presentation/descriptor.schema.json` (blob `e87767710b6eafd32d57fc68d5294610b0038571`) não admite `node.source_key_literal` ou `reference.reference_basis/declared_key_literal`. `semantics.py` (blob `c448663d84507178a8fb463d019a10a1a43f0cde`) exige `reference.declared_id` igual ao `identity.native_id` de UM alvo original no mesmo source/snapshot para `RESOLVED`. F3A repete a regra no JS. Portanto um `parent_key` verdadeiro não pode navegar ao pai com native_id null ou diferente sem violar o contrato.

C2 no SHA `e349a09d439d292011bca4c0994cf8ab3e3fbf9f` conserva key e ui_id em `unmapped_fields`, mas `ref()` busca nativos. O cenário sem native vira `UNRESOLVED` + `SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE`; se key textual se confunde com native_id de outra coleção, o mapeador recusa `R4_V5_PARENT_SCOPE_UNREPRESENTABLE`. Arestas `from_key/to_key` possuem proteção análoga. Isso protege a ciência, mas perde navegação explícita legítima. Não é falta de teste somente: é uma lacuna do modelo de referência.

F1 sanitizada `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7` informa 2.911 nós, 1.595 relações e 858 parent_keys explícitos resolvidos **no legado e no payload selecionado**. Esses números não demonstram paridade em 0.2.0, nem cobertura do acervo global. Os 50 negativos F1 não são a mesma coisa que os 50 pares inventados de nosso teste D.

## Decisão recomendada

**O1:** proposta mínima de descriptor `0.2.1`, sem alterar o 0.2.0 existente. Nó pode conservar `source_key_literal` original, e referências estruturais discriminam `SOURCE_STRUCTURAL_KEY` de `NATIVE_ID`; apontam via `target_navigation_id` derivado à ocorrência ORIGINAL única do mesmo source/snapshot. `native_id` permanece exatamente o literal comprovado, inclusive null; `ui_id` não se torna identificação científica. Requer ARC-09 **nova**, revisão independente e testes posteriores. O0 insuficiente; O2 sidecar duplica autoridade; O3 renderer antigo/import de `r4.*` contraria a segregação.

Arquivos no diretório atual: contraprovas, opções e riscos, candidata 0.2.1, compatibilidade sem migração, fixtures inventados, pedido único ARC-09, estado da revisão, SHAs e handoff com manifesto SHA256. Versão, código, schema executável, ADR/contratos históricos e R4 **não foram modificados**.

**Execução real nesta K:** consulta de Git/blobs versionados e verificação estática de invariantes e casos inventados. **Não executados:** Python `validate_descriptor`, renderer/browser, fontes de experimentos, host Windows, testes de produto nem CI da versão 0.2.1; não há implementação 0.2.1 ou evidência G4/G5/G6. Publicação dos docs não constitui aprovação, merge, release, deploy, migração ou limpeza.
