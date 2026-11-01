# AP04 F4 C2-K — resultado técnico e escopo

**Missão:** AP04-F4-C2-K-KEY-IDENTITY-CONTRACT-CHAT-01.
**Conclusão técnica:** `O0_INSUFFICIENT_O1_RECOMMENDED_CONDITIONALLY`.
**Gate de conclusão integral:** `INDEPENDENT_REVIEW_NOT_PROVEN` e `ARC09_HUMAN_APPROVAL_PENDING`; resultado atual `C2_K_REVIEW_BLOCKED_EXACT`. Não reivindicar `C2_K_CONTRACT_CANDIDATE_REVIEWED` sem parecer distinto no SHA final.
**Autoridade:** `LEGACY_DERIVED`, não científica.

## Evidência verificável

R4 privado, **apenas código** no SHA `5c145615c8a1bd601351badddccaf3acea474ed2`: `experiment_lineage.py` usa `key` como identidade estrutural única e `bykey` para ligações; `ui_id` é identidade DERIVED_UI criada por `uid`; `native_id` pode ser null e só indica identidade nativa comprovada. `parent_key` e `edges.from_key/to_key` referem-se à `key`; as pontas gráficas de apresentação derivam `ui_id`. `experiment_lineage_sources.py` possui nós com chave original e native_id ausente, ligados a parent_key explícito. São **três namespaces distintos**.

O schema fechado 0.2.0 em `tools/atlas_legacy_presentation/descriptor.schema.json` (blob `e87767710b6eafd32d57fc68d5294610b0038571`) não admite `node.source_key_literal` ou `reference.reference_basis/declared_key_literal`. `semantics.py` (blob `c448663d84507178a8fb463d019a10a1a43f0cde`) exige `reference.declared_id` igual ao `identity.native_id` de UM alvo original no mesmo source/snapshot para `RESOLVED`. F3A repete a regra no JS. Portanto um `parent_key` verdadeiro não pode navegar ao pai com native_id null ou diferente sem violar o contrato.

C2 no SHA `e349a09d439d292011bca4c0994cf8ab3e3fbf9f` conserva key e ui_id em `unmapped_fields`, mas `ref()` busca nativos. O cenário sem native vira `UNRESOLVED` + `SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE`; se key textual se confunde com native_id de outra coleção, o mapeador recusa `R4_V5_PARENT_SCOPE_UNREPRESENTABLE`. Arestas `from_key/to_key` possuem proteção análoga. Isso protege a ciência, mas perde navegação explícita legítima. Não é falta de teste somente: é uma lacuna do modelo de referência.

F1 sanitizada `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7` informa 2.911 nós, 1.595 relações e 858 parent_keys explícitos resolvidos **no legado e no payload selecionado**. Esses números não demonstram paridade em 0.2.0, nem cobertura do acervo global. Os 50 negativos F1 não são a mesma coisa que os 50 pares inventados de nosso teste D.

## Disposição das cinco observações Copilot no SHA inicial

1. F1: a linha F3A da compatibilidade refere-se agora à **baseline sanitizada e escopada** de 2.911 nós/1.595 relações/858 parent keys; não são números sintéticos nem universais.
2. Markdown: normalizadas as crases dos campos em `DESCRIPTOR-0.2.1-CANDIDATE.md` e `CURRENT-CONTRACT-COUNTEREXAMPLES.md`.
3. Schema: explicado que `node.parent_key_literal` e `node.parent` são **ambos requeridos já em 0.2.0**; o delta declara `source_key_literal` e os novos campos requeridos de `reference`. `PARENT_RESOLVED` agora tem prova verificável, campo-irmão, base e alvo inequívocos.
4. Grafia: corrigido “órfãos”.
5. Handoff: `technical_conclusion` usa o mesmo token deste RESULT e hashes do manifest são recalculados para os arquivos efetivamente alterados.

**Contraprova adicional:** caso E de origem com key ausente exige rejeição atômica (o oráculo anterior confundia E com órfão válido); G exercita alvo ausente com key válida; H ciclo; I `MEMBER_OF` navegável e não causal. Os casos continuam inventados, não são testes executados do produto.

**Revisão independente no SHA corrigido:** `INDEPENDENT_REVIEW_NOT_PROVEN` até análise por executor distinto. A revisão Copilot no SHA inicial foi uma revisão real com cinco findings, não atesta as correções posteriores.

## Decisão recomendada

**O1:** proposta mínima de descriptor `0.2.1`, sem alterar o 0.2.0 existente. Nó pode conservar `source_key_literal` original, e referências estruturais discriminam `SOURCE_STRUCTURAL_KEY` de `NATIVE_ID`; apontam via `target_navigation_id` derivado à ocorrência ORIGINAL única do mesmo source/snapshot. `native_id` permanece exatamente o literal comprovado, inclusive null; `ui_id` não se torna identificação científica. Requer ARC-09 **nova**, revisão independente e testes posteriores. O0 insuficiente; O2 sidecar duplica autoridade; O3 renderer antigo/import de `r4.*` contraria a segregação.

Arquivos no diretório atual: contraprovas, opções e riscos, candidata 0.2.1, compatibilidade sem migração, fixtures inventados, pedido único ARC-09, estado da revisão, SHAs e handoff com manifesto SHA256. Versão, código, schema executável, ADR/contratos históricos e R4 **não foram modificados**.

**Execução real nesta K:** consulta de Git/blobs versionados e verificação estática de invariantes e casos inventados. **Não executados:** Python `validate_descriptor`, renderer/browser, fontes de experimentos, host Windows, testes de produto nem CI da versão 0.2.1; não há implementação 0.2.1 ou evidência G4/G5/G6. Publicação dos docs não constitui aprovação, merge, release, deploy, migração ou limpeza.
