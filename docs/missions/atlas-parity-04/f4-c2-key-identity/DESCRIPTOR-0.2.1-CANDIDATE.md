# Adendo candidato — atlas-legacy-presentation 0.2.1

**Estado:** `UNAPPROVED_VERSIONED_PROPOSAL`. O contrato aprovado `atlas-legacy-presentation/0.2.0` e a ADR-0003 v0.2 `APPROVED_SCOPED` permanecem intocados. Não há implementação, migração, aprovação científica ou decisão ARC-09. F2 técnico: `c3ea1e82938fd61cc5a22fee973352715a5bb527`; schema executável de referência: blob `e87767710b6eafd32d57fc68d5294610b0038571` em `INPUT-SHAS.json`.

## Delta — normativo apenas para uma FUTURA 0.2.1

1. **Despacho fechado.** JSON Schema Draft 2020-12 separado, `$id="urn:atlas:proposal:legacy-presentation:0.2.1"`. Envelope: `format="atlas-legacy-presentation"`, `version="0.2.1"`, `authority="LEGACY_DERIVED"`. `$id` é propriedade do schema, não do envelope. Preservar `additionalProperties:false`, todos os campos existentes e limites 0.2.0. Versão ausente, híbrida ou desconhecida rejeita atomicamente; sem downgrade/coerção.
2. **Campos existentes de `$defs.node`.** `identity`, `kind`, `original_type`, `entity_status`, `label_literal`, `family_literal`, `parent_key_literal`, `parent`, `tree_state`, `external_reference` e `binding_gap` já são requeridos em 0.2.0 e continuam requeridos. `node.parent` é `$defs.reference`, não um objeto novo. `node.parent_key_literal` continua `$defs.nullable_text`: string ou null, até 65.536 caracteres.
3. **Dois campos novos no nó.** `node.source_key_literal`: string não vazia de até 2048 caracteres ou null; opcional na sintaxe, semanticamente obrigatório e não nulo para todo nó ORIGINAL `SOURCE_ENTITY` oriundo de `lineage_graph.nodes[]`. Copiar exatamente a `key` original, sem trim, casefold, NFC, coerção, hash, ordinal ou fallback por `ui_id`. `identity.locator` e prova da origem vinculam índice, objeto, bytes e campo. Nos outros nós/coleções/stubs: ausente ou null, sem participação no índice estrutural. Toda `key` original ausente, null, vazia, não string, maior que 2048 ou duplicada no grafo/snapshot causa rejeição atômica da importação R4 v5.

   `node.parent_key_presence`: enum `ABSENT`, `EXPLICIT_NULL`, `PRESENT`; opcional na sintaxe, semanticamente obrigatório para todo nó ORIGINAL de `lineage_graph.nodes[]`. Ausência da propriedade original produz `ABSENT`; JSON null produz `EXPLICIT_NULL`; string com comprimento de 1 a 65.536 produz `PRESENT`. Nos dois primeiros casos `parent_key_literal=null`; no terceiro, a string original integral. `parent_key:""`, número, booleano, objeto, array ou string maior que 65.536 causam **REJECT_ATOMIC**, sem emitir nó, referência ou descriptor parcial e sem atribuir presença a um valor inválido. Uma string só de espaços é não vazia e permanece literal: não aplicar trim. Nos demais nós, omitir `parent_key_presence`, sem inferir proveniência estrutural. Nunca inferir presença a partir do literal nullable, título ou `ui_id`.
4. **Dois campos novos por referência.** Preservar os seis requeridos `source_id`, `snapshot_id`, `declared_id`, `target_navigation_id`, `resolution`, `evidence_locator`; acrescentar como requeridos `reference.reference_basis` (`NATIVE_ID` ou `SOURCE_STRUCTURAL_KEY`) e `reference.declared_key_literal` (string de 1 a 65.536 caracteres ou null). Isso inclui `node.parent`, `node.external_reference` quando não nula, bindings de tabelas/linhas/ativos e `relation.from/to`. `source_key_literal` indexável continua limitado a 2048: referência mais longa não é truncada nem convertida em chave válida.
5. **Base `NATIVE_ID`.** `declared_key_literal=null`; `declared_id` conserva apenas o ID nativo literal ou null. Resolução por ID nativo ORIGINAL único no mesmo contexto fonte/snapshot, nunca por chave estrutural, `ui_id`, label, hash, filename ou ordem. Colisões continuam `COLLISION`; externos declarados continuam `EXTERNAL_DECLARED`, sem escolher ocorrência. Records, runs, tabelas, rows, assets e referências fora de `lineage_graph` mantêm essa base e as regras 0.2.0.
6. **Base `SOURCE_STRUCTURAL_KEY`.** `declared_id=null`. `declared_key_literal` copia exatamente `parent_key`, `from_key` ou `to_key`, ou é null conforme o caso sem endpoint abaixo. Para toda referência estrutural, inclusive sem endpoint, `source_id` e `snapshot_id` são não nulos e iguais aos do envelope; `evidence_locator` e prova autorizada identificam o campo/objeto original. O índice separado `(source_id,snapshot_id,source_key_literal)` contém somente nós ORIGINAIS de `lineage_graph.nodes[]` comprovados como `SOURCE_ENTITY`: nunca records, stubs, IDs nativos ou nós derivados. A presença de um nó na coleção, isoladamente, não prova que seja original.

   `RESOLVED` exige exatamente um alvo ORIGINAL com aquela key, navigation ID dessa ocorrência e prova verificável. Literal válido não encontrado, inclusive de 2049 a 65.536 caracteres, produz `UNRESOLVED`, `target_navigation_id=null`, preservando o literal. **`NULL_ENDPOINT` exige explicitamente `declared_id=null`, `declared_key_literal=null` e `target_navigation_id=null`.** Para parent ausente ou null, a diferença fica em `parent_key_presence` e na prova, não nesses três campos nulos. Null não significa órfão, raiz nem erro de tipo. Keys duplicadas, contexto inválido, prova falsa, alvo derivado/stub, `COLLISION` ou `EXTERNAL_DECLARED` nessa base rejeitam atomicamente. Proibido atravessar fonte, snapshot, importação ou sessão.
7. **Tabela total de parent para nó ORIGINAL de linhagem.** `node.parent` e `node.parent_key_literal` permanecem obrigatórios. Todos os casos aceitos abaixo usam `reference_basis=SOURCE_STRUCTURAL_KEY`, `declared_id=null` e o contexto/prova do item 6.

   | Campo na origem | `parent_key_presence` | Literal no nó / referência | Resolução e target | `tree_state` e lacuna |
   |---|---|---|---|---|
   | Propriedade ausente | `ABSENT` | ambos null | `NULL_ENDPOINT`, target null; locator identifica o campo ausente e a prova verifica sua ausência no objeto | `PARENT_UNKNOWN`, `binding_gap=true`, salvo raiz explícita abaixo |
   | `parent_key:null` | `EXPLICIT_NULL` | ambos null | `NULL_ENDPOINT`, target null; prova do campo presente com null | `PARENT_UNKNOWN`, `binding_gap=true`, salvo raiz explícita abaixo |
   | String 1–65.536, alvo original único | `PRESENT` | mesma string original, sem normalização | `RESOLVED`, target dessa ocorrência | `PARENT_RESOLVED`; `binding_gap` depende do ciclo, conforme abaixo |
   | String 1–65.536, sem alvo | `PRESENT` | mesma string original | `UNRESOLVED`, target null | `ORPHAN`, `binding_gap=true` |
   | `parent_key:""` | não emitido | não emitido | `REJECT_ATOMIC`; não é `NULL_ENDPOINT` | não emitido |
   | Número, booleano, objeto ou array | não emitido | não emitido | `REJECT_ATOMIC`; não converter em texto/null | não emitido |
   | String maior que 65.536 | não emitido | não emitido | `REJECT_ATOMIC`; não truncar | não emitido |

   `ROOT_DECLARED` só é permitido nas duas primeiras linhas com `root` booleano `true` original comprovado; então `binding_gap=false` para a ligação parental. Não inferir raiz por omissão/null, tipo, label ou ordem; conservar lacunas não parentais separadamente. `root=true` junto de parent não nulo é contraditório e rejeita atomicamente; não apagar a referência. Ausência não tem valor para dereferenciar: conferir a propriedade ausente no objeto autorizado, não inventar prova de um ponteiro existente.

   `PARENT_RESOLVED` exige alvo original único e `node.parent_key_literal == node.parent.declared_key_literal`. Para `NATIVE_ID`, conservar a igualdade nativa 0.2.0. Ciclos preservam as referências individualmente `RESOLVED` e o `tree_state=PARENT_RESOLVED`, mas todos e somente os membros cíclicos recebem `binding_gap=true`; fora do ciclo, `binding_gap=false` para esse estado. Registrar exatamente um gap `TREE_CYCLE` com contagem dos membros cíclicos, incluindo autociclo; não classificar descendentes inocentes como cíclicos. **`TREE_CYCLE` é código de gap, não novo valor de `tree_state` nem `ORPHAN`.** Nunca fabricar uma árvore acíclica. `RUN_EXTERNAL_ISOLATED` requer a prova externa válida de 0.2.0 e não é fallback para parent ausente/inválido.
8. **Relações.** Só os endpoints com origem comprovada em `lineage_graph.edges[].from_key/to_key` usam a base estrutural, cada um com sua própria prova. Null explícito conserva os três campos nulos do item 6; endpoint estrutural ausente, vazio, não string ou acima de 65.536 rejeita atomicamente, sem fallback para `from/to` derivado. Literal válido sem alvo é `UNRESOLVED`, sem fabricar nó ou pai. Conservar `kind_literal`, `semantics`, `direction`, `evidence_locator`, `issues`, `repeat_group`, `repeat_occurrence` e `binding_gap`. Repetições incluem base e literal na comparação, sem fundir namespaces. `MEMBER_OF` continua `ORGANIZATIONAL_MEMBERSHIP`, não `DECLARED_LINEAGE`, causalidade ou autenticidade. Navegação pode existir com `native_id=null`.
9. **Autoridade e limites.** `key` é estrutural; `ui_id` é derivado R4; `identity.navigation_id` é `DERIVED_FOR_PRESENTATION`, temporário e não persistente; `native_id` conserva o literal nativo comprovado ou null. Sintaxe, semântica, comparação literal, autenticidade e aprovação científica são eixos separados. Preservar 32 MiB, 10.000 nodes, 100.000 relations, 128 tables, demais quotas 0.2.0, TTL máximo 3600 s, RAM-only, sem rede/URI automática. Shape inválido, quota excedida, mistura de versões ou prova inválida recusa toda a importação, nunca subconjunto apresentado como completo. Não extrapolar F1 selecionada para o acervo R4 global.

## Fragmento ilustrativo do delta de schema — NÃO instalado

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

O recorte não é schema completo nem validador executável. Conservar todas as propriedades, `$defs`, fechamento e invariantes existentes; as condições `allOf/if/then` não substituem a prova semântica, a presença na fonte ou a tabela do item 7. Não instalar nem executar a versão proposta nesta missão.

## Governança

O consumidor 0.2.0 continua aceitando somente 0.2.0 e rejeita 0.2.1. O1 é proposta tipada e segregada, não atalho de UI. Implementação futura por owners C2/F3A/F3B depende de ARC-09 explícita, independente e vinculada aos bytes congelados em `HANDOFF.json`/`DECISION-REQUEST.md`, além de seus próprios testes. G4/G5/G6 não estão atendidos. Guard F2 e sucessão pertencem a P02/C4. Nenhuma mudança em produto, schema executável, ADR histórica, reader003, Caderno, protocolo, R4, guard ou manifesto histórico é autorizada por este documento.
