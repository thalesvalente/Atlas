# Contraprovas estáticas da identidade — sem dados de origem

**Nomes, IDs, literais, snapshots e grafos aqui são todos INVENTADOS.** O arquivo `SYNTHETIC-IDENTITY-FIXTURES.json` contém as formas JSON do perfil de origem e os oráculos candidatos. Nenhum representa dado privado ou teste real de 0.2.1.

## Invariantes do contrato hoje

`lineage_graph.nodes[].key` é único na população estrutural do snapshot; `ui_id` é derivado; `native_id` pode ser null. Em 0.2.0, objetos ``$defs.node` e ``$defs.reference` são fechados; o contrato só conhece `declared_id` e referência `RESOLVED` baseada em native_id único no contexto. `target_navigation_id` sozinho não é prova; o validador e F3A comparam `declared_id` ao native_id. `unmapped_fields` retém texto, não o converte em link.

## Matriz

| Caso | Entrada original inventada | O0 / 0.2.0 | O1 proposto / 0.2.1 |
|---|---|---|---|
| **A** | Pai `key=p-A` / `native_id=native-A`; filho `parent_key=p-A` | Não há native_id=p-A; `UNRESOLVED`, pai existe mas não navega | Resolver por chave estrutural p-A ao pai ORIGINAL; native-A permanece native-A |
| **B** | Pai de grafo `key=rec-B` / `native_id=null`; outro `records[].id=rec-B` | Resolver por native escolheria registro errado; o C2 atual recusa entrada por namespace | Índice separado `lineage_graph.nodes[]` aponta apenas pai correto |
| **C** | Snapshots C1/C2, ambos com `key=shared-C`, pais distintos | Associação por texto sem contexto criaria cross-snapshot; 0.2 não resolve native null | Endereçar (`source_id`, `snapshot_id`, key) e invalidar links antigos |
| **D** | 50 pares de nós com native_id duplicado, chaves estruturais diferentes; 50 filhos explicitamente vinculados | Native ID por si só tem `COLLISION`; chave dos filhos não corresponde ao índice nativo | 50 pais navegáveis por key única; pesquisas pelos 50 native IDs permanecem `COLLISION` |
| **E** | key de nó omitida/null; `parent_key=unknown-E` | `UNRESOLVED` | Continua `UNRESOLVED`; não inventa key de ui_id/label/ordinal |
| **F** | Dois nós com `key=duplicate-F` no mesmo snapshot | Parser R4 v5 recusa | Mesmo erro atômico, jamais escolher primeiro/último |

## Contraexemplo mínimo A

O pai tem ``{key:"p-A",native_id:null,ui_id:"ui-p-A"}`; filho, ``{key:"c-A",native_id:null,parent_key:"p-A"}`. A ligação é declarada por `parent_key` e tem alvo estrutural literal único; não é prova de native_id. Marcar `reference.declared_id="p-A"`, `resolution="RESOLVED"` e `target_navigation_id` do pai violaria o `semantics.py` e o F3A 0.2.0. Copiar `key` a `native_id` é falsificação de identidade científica. Deixar `UNRESOLVED` é seguro, porém perde o clique legítimo. **O0 não satisfaz simultaneamente fidelidade, navegação e validação estrita.**

## Rejeições exigidas para 0.2.1

- Referência `SOURCE_STRUCTURAL_KEY` com `declared_id != null`, `declared_key_literal` ausente, alvo stub, locator ausente, source/snapshot diferente ou destino não pertencente a `lineage_graph.nodes[]`: FAIL.
- Referência nativa com `declared_key_literal != null`, colisão de native com destino eleito, ou alias por ui_id/title/hash/ordinal: FAIL.
- Structural key duplicada na coleção/snapshot: rejeição integral. Chave nula ou ausente: não auto preencher nem criar pai/Project/Experiment.
- Parent `PARENT_RESOLVED` exige `parent_key_literal == reference.declared_key_literal`, alvo SOURCE_ENTITY original único, prova de campo e navigation_id de ocorrência.
- `MEMBER_OF` é organizacional, não causal; outros tipos e `causal_status` mantêm distinção. Repetições, null endpoints, órfãos, Run isolado e ciclos seguem explícitos.
- Desconhecidos, tamanhos acima de quota, cross-session, nova importação/TTL: rejeitar ou invalidar, sem subconjunto apresentado como completo.

**Método:** leitura dos códigos nos SHAs de `INPUT-SHAS.json` e contraprovas de invariantes. Não foi executado `validate_descriptor`, F3A, F3B, nem ensaio com origem privada. Os casos são **oráculos para testes futuros**, não relatório PASS.
