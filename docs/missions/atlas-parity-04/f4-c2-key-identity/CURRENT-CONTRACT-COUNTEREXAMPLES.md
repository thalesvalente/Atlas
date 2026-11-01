# Contraprovas estáticas da identidade — sem dados de origem

**Nomes, IDs, literais, snapshots e grafos aqui são todos INVENTADOS.** O arquivo `SYNTHETIC-IDENTITY-FIXTURES.json` contém as formas JSON do perfil de origem e os oráculos candidatos. Nenhum representa dado privado ou teste real de 0.2.1.

## Invariantes do contrato hoje

`lineage_graph.nodes[].key` é único na população estrutural do snapshot; `ui_id` é derivado; `native_id` pode ser null. Em 0.2.0, objetos `$defs.node` e `$defs.reference` são fechados; o contrato só conhece `declared_id` e referência `RESOLVED` baseada em native_id único no contexto. `target_navigation_id` sozinho não é prova; o validador e F3A comparam `declared_id` ao native_id. `unmapped_fields` retém texto, não o converte em link.

## Matriz

| Caso | Entrada original inventada | O0 / 0.2.0 | O1 proposto / 0.2.1 |
|---|---|---|---|
| **A** | Pai `key=p-A` / `native_id=native-A`; filho `parent_key=p-A` | Não há native_id=p-A; `UNRESOLVED`, pai existe mas não navega | Resolver por chave estrutural p-A ao pai ORIGINAL; native-A permanece native-A |
| **B** | Pai de grafo `key=rec-B` / `native_id=null`; outro `records[].id=rec-B` | Resolver por native escolheria registro errado; o C2 atual recusa entrada por namespace | Índice separado `lineage_graph.nodes[]` aponta apenas pai correto |
| **C** | Snapshots C1/C2, ambos com `key=shared-C`, pais distintos | Associação por texto sem contexto criaria cross-snapshot; 0.2 não resolve native null | Endereçar (`source_id`, `snapshot_id`, key) e invalidar links antigos |
| **D** | 50 pares de nós com native_id duplicado, chaves estruturais diferentes; 50 filhos explicitamente vinculados | Native ID por si só tem `COLLISION`; chave dos filhos não corresponde ao índice nativo | 50 pais navegáveis por key única; pesquisas pelos 50 native IDs permanecem `COLLISION` |
| **E** | Nó original sem `key`; outro nó declara `parent_key=missing-E` | Parser R4 v5 rejeita a entrada (key obrigatória) | Rejeição **atômica** do payload, sem emitir descriptor parcial nem inventar key de `ui_id`/label |
| **F** | Dois nós com `key=duplicate-F` no mesmo snapshot | Parser R4 v5 recusa | Mesmo erro atômico, jamais escolher primeiro/último |
| **G** | Nós válidos `key=root-G`, `key=child-G`; filho declara `parent_key=absent-G` | Referência nativa não resolve | `UNRESOLVED`, target null, `ORPHAN` e `binding_gap=true`; sem pai inventado |
| **H** | `cycle-H-1.parent_key=cycle-H-2` e `cycle-H-2.parent_key=cycle-H-1` | Ciclo precisa permanecer explícito | Ambos os alvos podem ser estruturalmente únicos, mas `TREE_CYCLE`/gap impede declarar árvore íntegra |
| **I** | `MEMBER_OF` de `member-I` para `group-I` por `from_key/to_key` | Native-only perde link se `native_id=null` | Ambos endpoints navegam por chave; `ORGANIZATIONAL_MEMBERSHIP` permanece não causal |

## Contraexemplo mínimo A

O pai tem `{key:"p-A",native_id:"native-A",ui_id:"ui-p-A"}`; filho, `{key:"c-A",native_id:null,parent_key:"p-A"}`. A ligação é declarada por `parent_key` e tem alvo estrutural literal único; não é prova de native_id. Marcar `reference.declared_id="p-A"`, `resolution="RESOLVED"` e `target_navigation_id` do pai violaria o `semantics.py` e o F3A 0.2.0. Copiar `key` a `native_id` é falsificação de identidade científica. Deixar `UNRESOLVED` é seguro, porém perde o clique legítimo. **O0 não satisfaz simultaneamente fidelidade, navegação e validação estrita.**

## Rejeições exigidas para 0.2.1

- Referência `SOURCE_STRUCTURAL_KEY` com `declared_id != null`, `declared_key_literal` ausente, alvo stub, locator ausente, source/snapshot diferente ou destino não pertencente a `lineage_graph.nodes[]`: FAIL.
- Referência nativa com `declared_key_literal != null`, colisão de native com destino eleito, ou alias por ui_id/title/hash/ordinal: FAIL.
- Structural key duplicada na coleção/snapshot ou key original ausente/null/vazia/não string/>2048: rejeição integral do payload R4 v5. A referência G com chave **alvo ausente**, mas input válido, é `UNRESOLVED`; não confundir com E. Nunca preencher key nem criar pai/Project/Experiment.
- `node.parent` e `node.parent_key_literal` já são requeridos em 0.2.0 e continuam em 0.2.1; `source_key_literal` só é opcional no schema (semanticamente obrigatório em nó original `lineage_graph`). `PARENT_RESOLVED` sob `SOURCE_STRUCTURAL_KEY` exige `node.parent_key_literal == node.parent.declared_key_literal`, alvo SOURCE_ENTITY original único, prova de campo e navigation_id da ocorrência. Sob `NATIVE_ID`, as invariantes nativas de 0.2.0 permanecem.
- `MEMBER_OF` é organizacional, não causal; outros tipos e `causal_status` mantêm distinção. Repetições, null endpoints, órfãos, Run isolado e ciclos seguem explícitos; `H` não vira árvore acíclica e `I` não recebe prova causal por conseguir navegar.
- Desconhecidos, tamanhos acima de quota, cross-session, nova importação/TTL: rejeitar ou invalidar, sem subconjunto apresentado como completo.

**Casos adicionais G/H/I:** inventados e também incluídos nos oráculos JSON; `G` distingue referência a alvo inexistente de entrada sem key, `H` testa ciclo apesar de endpoints resolvidos e `I` testa navegação sem causalidade. Sem execução de validator 0.2.1.

**Método:** leitura dos códigos nos SHAs de `INPUT-SHAS.json` e contraprovas de invariantes. Não foi executado `validate_descriptor`, F3A, F3B, nem ensaio com origem privada. Os casos são **oráculos para testes futuros**, não relatório PASS.

## Oráculos suplementares J–M (inteiramente inventados, não executados)

- **J — pai ausente:** nó de linhagem sem propriedade `parent_key`; `parent_key_presence=ABSENT`, `parent_key_literal=null`, `node.parent` obrigatório com `reference_basis=SOURCE_STRUCTURAL_KEY`, `declared_id=null`, `declared_key_literal=null`, `resolution=NULL_ENDPOINT`, `target_navigation_id=null`; `PARENT_UNKNOWN` sem `root=true` original.
- **K — null explícito:** `parent_key:null`; `parent_key_presence=EXPLICIT_NULL` e referência `NULL_ENDPOINT`, sem perder a diferença para J. Apenas declaração comprovada `root=true` autoriza `ROOT_DECLARED`.
- **L — referência longa:** `parent_key` de 3000 caracteres é preservada integralmente em `parent_key_literal` e `declared_key_literal` (limite 65.536); nenhuma chave indexável de nó excede 2048, portanto `UNRESOLVED`, `ORPHAN`, `binding_gap=true`. Não truncar nem inventar `native_id`.
- **M — base mista:** com `NATIVE_ID`, `declared_key_literal` não null é rejeitado; com `SOURCE_STRUCTURAL_KEY`, `declared_id` não null é rejeitado. São negativos do futuro schema `allOf/if/then`, não testes instalados.

Esses oráculos serão executados por C2/F3A somente após decisão ARC-09; documentação estática não constitui CI 0.2.1 nem revisão independente.
