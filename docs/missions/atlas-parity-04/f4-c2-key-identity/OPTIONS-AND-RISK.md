# O0–O3: comparação de alternativas e riscos

| Opção | Reconstitui parent/edges? | Fidelidade e custo | Decisão |
|---|---|---|---|
| **O0** — descriptor 0.2.0 sem mudança | Não nos casos A/B/C/D; `unmapped_fields` preserva literais, não ponte validada | Seguro/fail-closed, mas hierarquia navegável incompleta. Fazer link na UI ignorando `validate_descriptor` seria mudança oculta de semântica | **Insuficiente como solução integral**; pode continuar fallback com gaps |
| **O1** — 0.2.1 com chave estrutural tipada | Sim quando `key` original for única e prova explicitar `parent_key` ou `from_key/to_key`; null/ambíguas não se resolvem | Mudança pequena mas exige atualização coordenada de schema/semântica Python/F3A/F3B, testes e ARC-09 | **Recomendada com decisão humana prévia** |
| **O2** — sidecar UI de navegação | Possível, mas gerencia segunda entrada e duas fontes de resolução/TTL | Maior risco de split-brain, versões/índices divergentes, precisa ARC-09 também | **Não preferida** |
| **O3** — renderer R4 ou `r4.*` no novo viewer | Pode reutilizar apresentação histórica | Contraria limite externo O1→File API O3, ARC-04/07, Caderno e isolamento de produto | **Rejeitada sem nova arquitetura aprovada** |

**Compatibilidade de shape:** `node.parent` e `node.parent_key_literal` já são obrigatórios no schema 0.2.0; O1 adiciona somente `node.source_key_literal` e os dois campos tipados de `$defs.reference`, sem substituir os campos antigos. A key original é obrigatória nos nós R4 v5, e duplicidade/ausência rejeita atomicamente.

## Riscos com mitigação mandatória em O1

1. **Promoção indevida à ciência:** `source_key_literal`/`declared_key_literal` nunca entram em `native_id`; `ui_id` não vira native nem navigation_id durável. `LEGACY_DERIVED` em todo payload.
2. **Colisão de namespaces:** índice SOURCE_STRUCTURAL_KEY estritamente nos nós originais de `lineage_graph`, por source/snapshot, sem usar records, tables, assets ou `identity.native_id`.
3. **Ambiguidade:** duplicata key estrutural provoca erro de entrada; colisão native continua `COLLISION`. Não escolher ocorrência por ordem/completude.
4. **Causalidade falsa:** link navegacional não muda `ORGANIZATIONAL_MEMBERSHIP` em `DECLARED_LINEAGE`; preservar provas e direção dos edges.
5. **Regressão:** F3A JS e `semantics.py` hoje rejeitam link não-nativo; atualizar somente depois da aprovação e medir em CI/browser; F3B mantém tokens segregados e export fiel.
6. **Envelope:** preservar JSON Schema Draft2020-12 fechado, 32MiB, 10.000 nós, 100.000 relações, 128 tabelas, limites de strings/lexema, TTL≤3600s, RAM-only. Quota excedida rejeita importação inteira.
7. **Contextos:** source/snapshot não autenticam ciência, mas segregam navegação. Expiração, troca de importação e sessão invalidam links.
8. **Governança:** ARC-09 exige revisão realmente independente e decisão versionada no SHA; aceite 0.2.0 PR#15 não aprova 0.2.1.
9. **Rollback:** recusar 0.2.1, manter 0.2.0; descartar somente derivado temporário próprio, não fonte.
10. **CI documental:** guard de paths exatos pode rejeitar esta pasta; não afrouxar controles/pins, remeter sucessão justificada a C4.

Caderno 0.1.0a1, RO-Crate 1.3, Process Run 0.6, reader003, SDK/Catalog continuam independentes; HL7/FHIR `FUTURE_CAPABILITY_ONLY`. Sem novos tipos Project/Experiment, sem status científico aprovado e sem poderes de migração/retention.
