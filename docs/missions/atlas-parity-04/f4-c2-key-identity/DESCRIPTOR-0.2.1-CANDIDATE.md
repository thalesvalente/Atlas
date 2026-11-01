# Adendo candidato — atlas-legacy-presentation 0.2.1

**Estado:** `UNAPPROVED_VERSIONED_PROPOSAL`. Não é schema executável, contrato aprovado, ADR substituta ou implementação; 0.2.0 permanece íntegro. Exige ARC-09 com SHA final e revisor distinto.

## Delta delimitado

1. Em envelope de NOVA versão: `version="0.2.1"` e ``$id="urn:atlas:proposal:legacy-presentation:0.2.1"`, `format` e `authority="LEGACY_DERIVED"` inalterados. Nenhum parse permissivo por versão desconhecida.
2. Adicionar em ``$defs.node` propriedade opcional `source_key_literal` = string não vazia ≤2048 ou null, apenas contendo `lineage_graph.nodes[].key` literal observado com locator; ausência/null não gera chave. Seu índice é exclusivo de `SOURCE_ENTITY` da coleção lineage do mesmo source/snapshot. `ui_id` permanece literal no `unmapped_fields`; nunca é `native_id`.
3. Em ``$defs.reference`, tornar **obrigatórias em 0.2.1** duas novas propriedades: `reference_basis` com enum `NATIVE_ID` | `SOURCE_STRUCTURAL_KEY` e `declared_key_literal` string não vazia ≤2048 ou null. Os seis campos antigos `source_id`, `snapshot_id`, `declared_id`, `target_navigation_id`, `resolution`, `evidence_locator` continuam requeridos. Objetos seguem `additionalProperties:false`.
4. `NATIVE_ID`: `declared_key_literal=null`, `declared_id` mantém as regras 0.2.0 de native_id único por contexto, collisions, stub/external e provas. Referências de record/run/table/asset seguem NATIVE_ID. Valores native jamais derivados de key, hash, filename, ui_id ou label.
5. `SOURCE_STRUCTURAL_KEY`: `declared_id=null`; `declared_key_literal` transporta exatamente `parent_key`/`from_key/to_key` (ou null em endpoint nulo). `RESOLVED` exige chave textual não vazia, mesmo (source_id,snapshot_id), alvo ORIGINAL `SOURCE_ENTITY` único em `descriptor.nodes[]` originado de `lineage_graph.nodes[]`, `node.source_key_literal` igual ao declarado, `target_navigation_id` da ocorrência original e `evidence_locator` do campo de origem. Não pode resolver por `native_id`, pela população `records[]`, por ui_id ou cross-snapshot.
6. `UNRESOLVED` para key declarada sem alvo, target null; `NULL_ENDPOINT` somente quando os dois campos declared são null e target null. Duplicidade da key de origem na coleção do snapshot é **erro atômico**, não escolher alvo; nativos duplicados permanecem `COLLISION` para referências NATIVE_ID. `EXTERNAL_DECLARED` segue a semântica do stub nativo original, nunca structural.
7. Em `node.parent`, se `reference_basis=SOURCE_STRUCTURAL_KEY`, `PARENT_RESOLVED` exige `parent_key_literal==declared_key_literal`, pai original único e prova. Preservar detecção de ciclos, `binding_gap` e navegação UI sem ocultar arestas originais; `ROOT_DECLARED` só com declaração original apropriada, não pela falta de chave.
8. Somente `relations` provenientes do grafo e com `from_key/to_key` usam basis estrutural; relações originais de outro domínio mantêm NATIVE_ID. Conservar `semantics`, `direction`, `evidence_locator`, `repeat_group`/`repeat_occurrence`, estados de endpoints e `binding_gap`. `MEMBER_OF` = pertencimento, jamais prova causal por si só.
9. `validation` distingue sintaxe, semântica, comparação, autenticidade e ciência. Origem/snapshot, unknowns, null, valores/lexemas, ófãos, Run original/stub e perdas permanecem. Quotas/TTL e privacidade mantidas.

## Fragmentos ilustrativos, não descriptor completo

```json
{
  "identity": {"native_id": null, "navigation_id":"nav:fixture:1",
    "navigation_id_kind":"DERIVED_FOR_PRESENTATION",
    "occurrence":0,"locator":"/lineage_graph/nodes/0"},
  "source_key_literal":"parent-fixture",
  "parent_key_literal":null
}
```

```json
{
  "reference_basis":"SOURCE_STRUCTURAL_KEY",
  "source_id":"synthetic-source","snapshot_id":"synthetic-snapshot",
  "declared_id":null,"declared_key_literal":"parent-fixture",
  "target_navigation_id":"nav:fixture:1","resolution":"RESOLVED",
  "evidence_locator":"/lineage_graph/nodes/1/parent_key"
}
```

Estes são FRAGMENTOS inventados, não payloads 0.2.1 validados. A prova de origem também deve demonstrar que `source_key_literal` veio do campo `key` daquele nó. Qualquer falsa igualdade com `native_id` de outra coleção é ignorada pela resolução estrutural.

## Autorização / compatibilidade

Nenhum novo `.schema.json`, validator, reader, módulo JS, AGENTS/ADR, contrato reader003, Caderno, Workflow, PR#18 ou R4 será alterado nesta missão. Aprovação separada ARC-09 é condição necessária, não suficiente para G4/G5/G6. O0 segue como modo 0.2.0 com gaps honestos se o pedido for rejeitado.
