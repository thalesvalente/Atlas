# Compatibilidade e testes futuros — SEM migração

## Despacho de versões (somente após aprovação)

- `0.2.0` continua com bytes, schema e semântica originais; consumidor atual rejeita 0.2.1, nunca tenta aceitar alias por chave.
- Futuro `0.2.1` deve ter schema fechado **separado**, version + `$id` exatos, discriminante obrigatório por referência e transação atômica. Version ausente, híbrida, desconhecida ou nova propriedade no 0.2.0 = FAIL; nenhuma autocorreção, downgrade ou preenchimento de native_id.
- Nunca alterar/reescrever acervo R4, Caderno/SDK/Catalog, reader003, manifestos históricos, caches científicos, worktrees ou snapshots anteriores. Arquivos legados continuam fora do runtime Atlas; UI segregada File API única em memória conforme aceite anterior.

## Mudanças futuras condicionadas a ARC-09

| Owner futuro | Obrigação verificável |
|---|---|
| C2-A/D reader | Implementar índice estrutural somente em `lineage_graph.nodes` do mesmo snapshot, parser/validator Draft2020-12 com fail-closed, prova `key`/`parent_key`/`from_key`/`to_key` e regressões de `native_id`/`unmapped_fields` |
| F3A C1 renderer | Alterar somente após decisão a regra `RESOLVED` do JS e schema versionado, preservar clique/reveal, expansão, zoom, minimapa, teclado e ciclos; medir contra a **baseline sanitizada F1 do payload qualificante** (2.911 nós, 1.595 relações, 858 parent keys explícitos resolvidos), não contra fixtures sintéticos ou o R4 global |
| F3B table | Dispatch/version, tokens fonte/snapshot/sessão e export fiel; nenhuma tabela sem native se torna entidade admitida |
| C3 | Integração só após C2-D, C0, C1 e F3B congelados, gate ARC-09 atendido se extensão aprovada; não antecipar nesta K |
| C4 | Sucessão exata de guards/CI sem relaxar proteção histórica ou trocar pins; G5 vinculada ao SHA real da candidata |
| LOCAL L1/F5 | G4/G6 exigem host Windows, autorização exata de leitura privada, sandbox/zero escrita na origem; não inferir PASS de fixtures |

## Suite red/green a executar FUTURAMENTE

1. A: pai key≠native e pai native=null; `RESOLVED` estrutural com native original inalterado.
2. B: colisão textual `key` vs `records.id`, sem link acidental ao registro.
3. C: snapshots distintos com mesma key; rejeitar cross-snapshot, tokens stale.
4. D: 50 pares native duplicados e 50 `parent_key` explícitos; native lookup COLLISION, structural lookup único.
5. E/F: key original ausente/null/vazia/duplicada/não string/>2048: **rejeição atômica** do input, sem fallback de UI. G: key de origem válida, mas parent_key aponta para alvo ausente: `UNRESOLVED` + `ORPHAN`/gap.
6. Ausência e null explícito de `parent_key` precisam de `parent_key_presence=ABSENT` versus `EXPLICIT_NULL`; em ambos os casos `node.parent` continua referência obrigatória `NULL_ENDPOINT`. `ROOT_DECLARED` exige `root=true` declarado, não omissão. Referência de 2049–65536 caracteres permanece literal e `UNRESOLVED` quando não pertence ao índice estrutural (máximo 2048), sem truncamento.
7. O schema futuro aplica `allOf/if/then` para rejeitar bases misturadas: `NATIVE_ID` exige `declared_key_literal=null`; `SOURCE_STRUCTURAL_KEY` exige `declared_id=null`. O validador semântico também confere source/snapshot, evidência e alvo original único.
8. Aliasing proibido: ligação via `ui_id`, label, hash, path ou ordenação rejeitada.
7. Tipos/direção/causalidade: I (`MEMBER_OF`) resolve endpoints estruturais mas continua organizacional/não causal; relações sem provas permanecem UNKNOWN; repetições, stubs e gaps conservados. H: ciclo de `parent_key` detectado (`TREE_CYCLE`) mesmo com referências individualmente resolvidas.
8. Versão: 0.2.0 segue passando seus testes; 0.2.1 só depois de implementação explícita, versões inválidas rejeitam antes da UI.
9. Quotas: 32MiB, 10k nós, 100k edges, 128 tabelas, TTL≤3600, profundidade/literal, inerte, no URI/network.
10. Regressão de interoperabilidade: Caderno 0.1.0a1, RO-Crate 1.3, Process Run 0.6 intactos; HL7/FHIR FUTURE_CAPABILITY_ONLY.

**Estado destes testes:** apenas oráculos documentados, **não executados**. Sessão/expiração invalida tokens, e eventual rollback futuro mantém 0.2.0 com erro honesto de perda de navegação, descartando apenas derivados temporários próprios.
