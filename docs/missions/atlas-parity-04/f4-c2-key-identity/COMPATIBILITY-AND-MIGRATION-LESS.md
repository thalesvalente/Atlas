# Compatibilidade e testes futuros — SEM migração

0.2.0 conserva bytes, schema e semântica. Seu consumidor rejeita 0.2.1. O1 é `UNAPPROVED_VERSIONED_PROPOSAL`: os quatro campos novos são `node.source_key_literal`, `node.parent_key_presence`, `reference.reference_basis` e `reference.declared_key_literal`. `node.parent` e `node.parent_key_literal` já são requeridos em 0.2.0. A versão futura exige dispatch separado/fechado e importação atômica; sem downgrade, alias ou preenchimento de native ID.

Não reescrever acervo R4, Caderno/SDK/Catalog, reader003, manifestos históricos, caches científicos, worktrees ou snapshots. UI legada permanece segregada, File API em memória; operações do host continuam fora do runtime.

## Owners futuros, somente após os gates aplicáveis

| Owner | Obrigação |
|---|---|
| C2-A/D | Índice exclusivamente original de `lineage_graph.nodes[]`, prova de key/parent/from/to, schema/semântica fechados, preservação de native ID e unmapped fields |
| F3A C1 | Validação JS e navegação alinhadas; clique/reveal, expansão, zoom, minimapa, teclado e ciclos; comparar com baseline F1 sanitizada do payload selecionado: 2.911 nós, 1.595 relações, 858 parent keys explícitos resolvidos — não fixtures sintéticos nem R4 global |
| F3B | Dispatch, tokens fonte/snapshot/sessão e export fiel; tabela sem native ID não vira entidade admitida |
| C3 | Composição somente depois de C2-D/C0/C1/F3B congelados e ARC-09, sem antecipação nesta K |
| P02/C4 | Sucessor estritamente scoped dos guards/CI, sem relaxar histórico/pins; provar no SHA final e conservar G5 aberto até evidência |
| LOCAL L1/F5 | G4/G6 dependem de host Windows e autorização própria para leitura privada; fixtures não qualificam o corpus |

## Suíte red/green a executar FUTURAMENTE

1. A: key do pai diferente de native ID; B complementa pai com native null. Resolver estruturalmente, preservando native original.
2. B: key textual igual a records.id; não selecionar o registro de outro namespace.
3. C1/C2: mesma key em snapshots distintos, sem resolução cruzada e com invalidação de tokens stale.
4. D: 50 grupos nativos colidentes, 150 keys distintas, 50 pais explícitos e 50 edges; native lookup permanece COLLISION.
5. E/F: key original ausente/null/vazia/não string/>2048/duplicada rejeita atomicamente, sem fallback. G: referência válida sem alvo permanece UNRESOLVED/ORPHAN/gap.
6. J/K/L e matriz PKEY: distinguir parent ausente/null/presente; vazio, não string e excesso de limite rejeitam. NULL_ENDPOINT tem declared_id, declared_key_literal e target_navigation_id null. ROOT_DECLARED exige root booleano true comprovado e ausência/null de parent; root=true com parent não nulo rejeita. Referência longa até 65.536 conserva o literal, sem truncamento.
7. M: allOf/if/then exige declared_key_literal=null em NATIVE_ID e declared_id=null em SOURCE_STRUCTURAL_KEY; prova, contexto e alvo original também são obrigatórios.
8. Aliases via ui_id, label, hash, path ou ordem não resolvem referências. Derivados/stubs não entram no índice estrutural.
9. H/I: ciclos preservam refs RESOLVED, tree_state=PARENT_RESOLVED e gap TREE_CYCLE com contagem exata; TREE_CYCLE não é tree_state. MEMBER_OF permanece organizacional e não causal. Conservar direção, repetições, nulls e gaps.
10. Versões: regressões 0.2.0 intactas; 0.2.1 somente após implementação autorizada; versões inválidas rejeitadas antes da UI.
11. Quotas: 32 MiB, 10.000 nós, 100.000 relações, 128 tabelas, TTL máximo 3600 s e demais limites existentes; HTML inerte, sem URI/rede automática.
12. Interoperabilidade: Caderno 0.1.0a1, RO-Crate 1.3, Process Run 0.6 e reader003 intactos; HL7/FHIR FUTURE_CAPABILITY_ONLY.

**Estado da suíte de produto acima: NOT_RUN.** O inventário contém 14 oráculos JSON, dez principais A/B/C1/C2/D/E/F/G/H/I e quatro suplementares J/K/L/M. A matriz PKEY em CURRENT é documental e não aumenta essa contagem. A checagem Python em INDEPENDENT-REVIEW inspeciona arquivos/oráculos, não executa o descriptor 0.2.1. Não confundir essa inspeção com RED/GREEN do produto, CI cross-OS, browser, aprovação ou revisão independente.

Sessão/importação/TTL invalida links, sem remapeamento por título. Rollback futuro recusa 0.2.1 e mantém 0.2.0 com lacunas honestas; descarta apenas derivados temporários próprios, nunca fontes.
