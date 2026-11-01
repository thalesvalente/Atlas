# Adendo candidato — atlas-legacy-presentation 0.2.1

**Estado:** `UNAPPROVED_VERSIONED_PROPOSAL`. Este documento atualiza **somente a candidata documental** já existente. O contrato aprovado `atlas-legacy-presentation/0.2.0` e a ADR-0003 v0.2 `APPROVED_SCOPED` permanecem intocados. Não há implementação, migração, aprovação científica ou decisão ARC-09. O contrato base F2 é o commit `c3ea1e82938fd61cc5a22fee973352715a5bb527`; a forma executável 0.2.0 publicada depois é apenas a referência para identificar os campos existentes.

## Delta de versão e schema — normativo apenas PARA UMA FUTURA 0.2.1

1. **Despacho fechado:** o schema JSON Schema Draft 2020-12 da nova versão, se aprovado e implementado separadamente, terá `$id="urn:atlas:proposal:legacy-presentation:0.2.1"`; o **envelope de dados** terá `format="atlas-legacy-presentation"`, `version="0.2.1"` e `authority="LEGACY_DERIVED"`. `$id` pertence ao **schema**, NÃO é novo campo do envelope. Os objetos continuam com `additionalProperties:false`. 0.2.0 conserva integralmente seu `$id`, schema, bytes e regras.
2. **`$defs.node` existente:** `identity`, `kind`, `original_type`, `entity_status`, `label_literal`, `family_literal`, `parent_key_literal`, `parent`, `tree_state`, `external_reference` e `binding_gap` **já são requeridos em 0.2.0 e continuam requeridos em 0.2.1**. `node.parent` já referencia `$defs.reference` e **não é objeto novo**. `node.parent_key_literal` já usa `$defs.nullable_text` (string ou null, até 65.536 caracteres), sem remapeamento silencioso.
3. **Campos novos no nó (somente na futura 0.2.1):** `$defs.node.properties.source_key_literal` é **opcional** com `type:["string","null"]`, `minLength:1` para string e `maxLength:2048`. Deve ser uma cópia exata, sem trim/casefold/NFC ou coerção, do `lineage_graph.nodes[i].key` original; `identity.locator` e o recibo de origem autorizada vinculam nó, índice, bytes e campo. É **obrigatório semanticamente**, presente e não nulo, em cada `SOURCE_ENTITY` oriundo de `lineage_graph.nodes[]`. Nos nós de outras coleções ou stubs é ausente ou null e jamais cria índice estrutural. **Outro campo novo:** `node.parent_key_presence`, enum `ABSENT`, `EXPLICIT_NULL` ou `PRESENT`, opcional na sintaxe e obrigatório semanticamente em todo nó ORIGINAL `lineage_graph.nodes[]`. É determinado pela presença/tipo de `parent_key` nos bytes autorizados da fonte: ausente → `ABSENT`, JSON null → `EXPLICIT_NULL`, string não vazia → `PRESENT`. Nos dois primeiros casos `node.parent_key_literal=null`; no terceiro, conserva a string original. É proibido inferir presença por `ui_id`, título, ordinal ou `node.parent_key_literal` isoladamente. Toda key original faltante/null/vazia/não string/maior que 2048 ou duplicada no grafo do snapshot produz **REJECT ATÔMICO** na importação R4 v5; não criar key de `ui_id`, título, ordinal, path ou hash.
4. **`$defs.reference` existente:** preserva como requeridos `source_id`, `snapshot_id`, `declared_id`, `target_navigation_id`, `resolution`, `evidence_locator`. Acrescenta como **requeridos em toda referência 0.2.1**, inclusive `node.parent`, `node.external_reference` (quando não nula), bindings de tabelas/linhas/ativos e `relation.from/to`: `reference_basis` (enum `NATIVE_ID` ou `SOURCE_STRUCTURAL_KEY`) e `declared_key_literal` (string não vazia de comprimento ≤65.536 ou null), respeitando os 65.536 caracteres já permitidos por `$defs.nullable_text` em `node.parent_key_literal`. Somente a chave INDEXÁVEL `node.source_key_literal` continua limitada a 2048 caracteres: referência original mais longa permanece fiel, porém `UNRESOLVED` sem truncamento. A propriedade `declared_id` continua string/null, e `target_navigation_id` continua navigation ID/null. Não aceitar campos desconhecidos nem mistura de versões.
5. **`NATIVE_ID`:** `declared_key_literal=null` obrigatório; `declared_id` conserva exclusivamente o ID nativo literal ou null conforme 0.2.0. A busca permanece por ID nativo único no contexto fonte/snapshot e ocorrência original; colididos mantêm `COLLISION`, externos declarados mantêm `EXTERNAL_DECLARED`, sem escolher candidato. Bindings de records, runs, tabelas, rows e assets e referências fora de `lineage_graph` permanecem nesta base. Nunca resolver por key, `ui_id`, label, hash, filename ou ordem.
6. **`SOURCE_STRUCTURAL_KEY`:** `declared_id=null` obrigatório; `declared_key_literal` copia sem alterar o literal `parent_key`, `from_key` ou `to_key` original, ou null quando o endpoint é explicitamente nulo. Para uma chave não nula, `source_id` e `snapshot_id` **não nulos e exatamente iguais** aos do envelope; `evidence_locator` precisa identificar o campo de origem. Um índice separado `(source_id,snapshot_id,source_key_literal)` considera **somente** nós `SOURCE_ENTITY` oriundos de `lineage_graph.nodes[]`, com provas de `key` e `identity.locator`, nunca records, stubs, native IDs ou nós derivados. `RESOLVED` só é válido quando há exatamente uma ocorrência ORIGINAL com aquela chave, o `target_navigation_id` aponta para essa mesma ocorrência e a prova é verificável. Nenhuma referência pode atravessar fonte, snapshot, importação ou sessão. Se o literal válido não tem alvo, inclusive literal com mais de 2048 caracteres que não cabe no índice de `source_key_literal`, o status é `UNRESOLVED` e target null; endpoint explicitamente null exige `NULL_ENDPOINT` com ambos os literais declarados e target null. Chave estrutural duplicada, ausência/invalidade de contexto, falsa prova, alvo derivado ou stub, `COLLISION` ou `EXTERNAL_DECLARED` sob esta base causam rejeição atômica, não resolução heurística.
7. **`node.parent`, ausência/null e raiz:** `node.parent` permanece campo **obrigatório** do tipo `$defs.reference`; `node.parent_key_literal` permanece campo **obrigatório** do tipo `$defs.nullable_text` (string/null, até 65.536 caracteres). Para nós originais de linhagem, `parent_key_presence` distingue formas que `parent_key_literal=null` sozinho não representa:

   | Campo na origem R4 | Presença | Literal no nó | `node.parent` (obrigatório) | `tree_state` |
   |---|---|---|---|---|
   | `parent_key` string não vazia | `PRESENT` | string literal | `reference_basis=SOURCE_STRUCTURAL_KEY`, `declared_id=null`, `declared_key_literal` igual ao campo original, `RESOLVED` só para alvo original único, senão `UNRESOLVED`; locator do campo | `PARENT_RESOLVED` se válido; `ORPHAN` se não localizado |
   | `parent_key: null` explícito | `EXPLICIT_NULL` | null | `reference_basis=SOURCE_STRUCTURAL_KEY`, `declared_id=null`, `declared_key_literal=null`, `target_navigation_id=null`, `resolution=NULL_ENDPOINT`, locator do campo presente | `ROOT_DECLARED` só com `root=true` original comprovado; caso contrário `PARENT_UNKNOWN` |
   | `parent_key` ausente | `ABSENT` | null | mesmos campos de `NULL_ENDPOINT`, mas locator para campo AUSENTE e prova de ausência no objeto fonte | `ROOT_DECLARED` só com `root=true` original comprovado; caso contrário `PARENT_UNKNOWN` |

   `PARENT_RESOLVED` exige `node.parent.resolution=RESOLVED`, alvo original único e `target_navigation_id` correto na mesma fonte/snapshot/importação. Para base estrutural, `node.parent_key_literal === node.parent.declared_key_literal`; sob `NATIVE_ID`, obedecer à igualdade nativa de 0.2.0. Uma chave declarada válida sem alvo permanece `ORPHAN` e `binding_gap=true`. `ROOT_DECLARED` requer evidência explícita de `root=true` e `binding_gap=false`; não inferir raiz da omissão/null. `PARENT_UNKNOWN` conserva lacuna; `RUN_EXTERNAL_ISOLATED` exige prova externa válida conforme 0.2.0, nunca é fallback automático. `parent_key_presence` não muda lookup de records/assets para base estrutural. Ciclos exigem `TREE_CYCLE`/gap, sem fabricar árvore acíclica.
8. **Relações:** apenas os endpoints `relations[].from/to` cuja origem comprovada é `lineage_graph.edges[].from_key/to_key` utilizam `SOURCE_STRUCTURAL_KEY`. Cada endpoint usa seu próprio `reference_basis` e prova de campo, preservando nulos, órfãos e `binding_gap`. Conservar `kind_literal`, `semantics`, `direction`, `evidence_locator`, `issues`, `repeat_group` e `repeat_occurrence`; assinatura de repetição e comparação incluem base e literal declarados para não fundir namespaces. `MEMBER_OF` continua `ORGANIZATIONAL_MEMBERSHIP`, não `DECLARED_LINEAGE`, causalidade ou autenticação. A ligação visual pode existir mesmo com `native_id=null`.
9. **Preservação e rejeição:** `ui_id` de R4 é derivado; `identity.navigation_id` de Atlas também é `DERIVED_FOR_PRESENTATION` e temporário; não são ID nativo nem entre si um identificador persistente. `native_id` permanece o literal científico comprovado ou null. Separar validade sintática, semântica, comparação de literais, autenticidade e aprovação científica. Versão ausente, híbrida, desconhecida, shape inválido, referência incompatível, colisão de key, prova falsa ou quotas excedidas causam FAIL sem importação parcial. Preservar limites 0.2.0 (32 MiB descriptor, ≤10.000 nodes, ≤100.000 relations, ≤128 tables, TTL≤3600 s, somente RAM, sem rede/URI automática), proteção de conteúdo privado e sessão. Nenhuma extrapolação das contagens F1 para o R4 universal.

### Delta de schema ilustrativo (NÃO instalado)

```json
{
  "$id": "urn:atlas:proposal:legacy-presentation:0.2.1",
  "$defs": {
    "node": {
      "required": ["identity","kind","original_type","entity_status","label_literal","family_literal","parent_key_literal","parent","tree_state","external_reference","binding_gap"],
      "properties": {
        "source_key_literal": {"type":["string","null"],"minLength":1,"maxLength":2048},
        "parent_key_presence": {"enum":["ABSENT","EXPLICIT_NULL","PRESENT"]},
        "parent_key_literal": {"$ref":"#/$defs/nullable_text"},
        "parent": {"$ref":"#/$defs/reference"}
      }
    },
    "reference": {
      "required": ["source_id","snapshot_id","declared_id","target_navigation_id","resolution","evidence_locator","reference_basis","declared_key_literal"],
      "properties": {
        "reference_basis": {"enum":["NATIVE_ID","SOURCE_STRUCTURAL_KEY"]},
        "declared_key_literal": {"type":["string","null"],"minLength":1,"maxLength":65536}
      },
      "allOf": [
        {"if":{"properties":{"reference_basis":{"const":"NATIVE_ID"}},"required":["reference_basis"]},"then":{"properties":{"declared_key_literal":{"type":"null"}}}},
        {"if":{"properties":{"reference_basis":{"const":"SOURCE_STRUCTURAL_KEY"}},"required":["reference_basis"]},"then":{"properties":{"declared_id":{"type":"null"}}}}
      ]
    }
  }
}
```

O fragmento também ilustra condicionais JSON Schema Draft2020-12: a base `NATIVE_ID` exige `declared_key_literal=null`, enquanto `SOURCE_STRUCTURAL_KEY` exige `declared_id=null`. `allOf/if/then` é obrigatório no schema futuro completo, além das contraprovas semânticas de proveniência. O fragmento mostra **apenas os campos/required relevantes ao delta**: a implementação futura deverá conservar TODAS as propriedades, `additionalProperties:false`, `$defs` e invariantes de 0.2.0. Não usar esse recorte isolado como schema validador.

### Fragmento inventado de nó-filho e pai (NÃO descriptor completo)

```json
{
  "identity":{"native_id":null,"navigation_id":"nav:fixture:child",
              "navigation_id_kind":"DERIVED_FOR_PRESENTATION",
              "occurrence":0,"locator":"/lineage_graph/nodes/1"},
  "source_key_literal":"child-fixture",
  "parent_key_presence":"PRESENT",
  "parent_key_literal":"parent-fixture",
  "parent":{
    "reference_basis":"SOURCE_STRUCTURAL_KEY",
    "source_id":"source-fixture","snapshot_id":"snapshot-fixture",
    "declared_id":null,"declared_key_literal":"parent-fixture",
    "target_navigation_id":"nav:fixture:parent",
    "resolution":"RESOLVED",
    "evidence_locator":"/lineage_graph/nodes/1/parent_key"
  }
}
```

O nó alvo inventado tem `lineage_graph.nodes[0].key="parent-fixture"`, `native_id=null`, `source_key_literal="parent-fixture"`, `identity.navigation_id="nav:fixture:parent"` e locator `/lineage_graph/nodes/0`. A igualdade textual com algum ID de `records[]` não altera o alvo. A verificação do nó e a do vínculo dependem da mesma prova original autorizada.

## Governança e compatibilidade

0.2.0 existente continua aceito pelo **validador 0.2.0**, sem campos novos; um consumidor 0.2.0 deve rejeitar 0.2.1. Uma futura implementação 0.2.1, se aprovada, exigirá dispatch estrito por versão e testes no SHA final; nenhum downgrade/coerção. Nenhum schema executável, Python, JS, `AGENTS.md`, ADR histórica, reader003, Caderno, protocolo, R4, guard CI ou manifesto histórico é modificado por esta K. O guard F2 que rejeita os novos paths K exige sucessão sob C4, sem mudar pins para silenciar. ARC-09 com SHA final, revisão comprovadamente não autora e aprovação humana explícita são gates separados; G4/G5/G6 continuam pendentes.

