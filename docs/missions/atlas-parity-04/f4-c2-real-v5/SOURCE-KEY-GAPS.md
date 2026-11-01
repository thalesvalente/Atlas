# SOURCE_KEY_DECISION_REQUIRED — decisão K/ARC-09

R4 A10 define dimensões distintas: `nodes[].key` é chave estrutural, `ui_id` é navegação derivada e `native_id` é opcional e científico. `parent_key` e `edges[].from_key/to_key` referenciam **key**, mas descriptor 0.2.0 resolve `declared_id` pelo conjunto de **native_id** em nós/tabelas/ativos. Uma igualdade textual com ID de outro record ou coleção não demonstra vínculo.

Implementado: refs só RESOLVED quando o proprietário estrutural possui native_id igual à key e é único no contexto de nativos. Quando não, o adapter conserva parent_key_literal e o campo original tipado em unmapped_fields, adiciona gaps como `SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE`, `SOURCE_GRAPH_KEY_NOT_NATIVE_REFERENCE`, `SOURCE_KEY_NAMESPACE_COLLISION`; vínculo permanece UNRESOLVED ou NULL_ENDPOINT (neste caso o literal original **não era nulo**, somente a referência nativa 0.2.0 não é exprimível). Nenhum ID é fabricado ou resolvido contra outra coleção. Colisões nativas globais ficam COLLISION, sem escolha arbitrária.

**Decisão exigida da frente K:** versão ARC-09/F2 com referência explícita de namespace structural_key/lineage_graph e regra de cardinalidade, ou manter descriptor 0.2.0 com gaps declarados e sem alegar árvore totalmente reconstruída. A decisão é humana/versionada, não alteração silenciosa deste owner.

Outros gaps persistentes: 4 de 5 tabelas F1 sem record_id resolúvel; 28 UNADMITTED_NATIVE_RF sem native_id; RNF/RES não inferidas; run externo isolado não fecha percurso árvore→RF; File permanece File; contagens F1 não são totais globais. Owner B ainda precisa provar isolamento OS, 256MiB/30s duros e aquisição real. Nenhum G4/G5/G6 ou F4-C3 é autorizado.
