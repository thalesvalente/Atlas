# O0–O3: alternativas, riscos e fronteiras

**Estado de O1:** `UNAPPROVED_VERSIONED_PROPOSAL`. Conclusão: `O0_INSUFFICIENT_O1_RECOMMENDED_CONDITIONALLY`. O contrato vigente continua 0.2.0; a proposta não autoriza implementação.

| Opção | Navegação e fidelidade | Decisão |
|---|---|---|
| O0 — descriptor 0.2.0 | Unmapped fields preserva literais, mas não prova ponte estrutural; UI não pode contornar native-only | Insuficiente como solução integral; fallback seguro com gaps |
| O1 — 0.2.1 tipada e segregada | Índice original por fonte/snapshot/key e prova literal; native ID permanece separado | Recomendada condicionalmente a ARC-09 e revisão independente |
| O2 — sidecar UI | Segunda entrada, fonte de resolução e ciclo de vida; risco de split-brain | Não preferida; também exigiria ARC-09 |
| O3 — renderer R4/import r4.* | Acopla produtor/host ao viewer e viola segregação ARC-04/07 | Rejeitada sem nova arquitetura aprovada |

**Delta completo:** O1 adiciona `node.source_key_literal`, `node.parent_key_presence`, `reference.reference_basis` e `reference.declared_key_literal`. `node.parent` e `node.parent_key_literal` já são obrigatórios em 0.2.0. Presença distingue ABSENT/EXPLICIT_NULL/PRESENT; parent vazio, inválido ou acima de 65.536 rejeita atomicamente. A key original ausente/inválida/duplicada também rejeita; nunca fabricar uma key.

## Mitigações mandatórias

1. Identidade: key é estrutural, ui_id/navigation_id são derivados e temporários; nenhum preenche native_id. Todo envelope permanece LEGACY_DERIVED.
2. Namespaces: índice SOURCE_STRUCTURAL_KEY somente em nós ORIGINAIS comprovados de lineage_graph, por fonte/snapshot; excluir records, tables, assets, stubs e derivados.
3. Ambiguidade: duplicidade estrutural rejeita o input; colisão nativa permanece COLLISION, sem primeiro/último/mais completo.
4. Ausência: NULL_ENDPOINT exige declared_id, declared_key_literal e target_navigation_id null; presença/prova distinguem omissão e null. Referência válida sem alvo é UNRESOLVED/ORPHAN; ciclo tem gap TREE_CYCLE, não é ORPHAN nem novo tree_state. Root exige declaração explícita consistente.
5. Causalidade: link navegável não muda MEMBER_OF/ORGANIZATIONAL_MEMBERSHIP para DECLARED_LINEAGE, autenticidade ou ciência aceita. Preservar direção, prova e repetições.
6. Regressão: Python/F3A/F3B devem alinhar dispatch e regras somente após aprovação; executar CI/browser próprios e preservar bindings nativos, tokens segregados e export fiel.
7. Limites: schema fechado, 32 MiB, 10.000 nós, 100.000 relações, 128 tabelas e demais quotas; TTL máximo 3600 s, RAM-only, sem URI/rede automática. Excesso rejeita o todo, sem truncamento.
8. Contexto e privacidade: source/snapshot segregam, não autenticam. Troca de importação/sessão e expiração invalidam links; não publicar dados privados ou abrir fontes por URI.
9. Governança/rollback: revisão não autora e decisão humana no objeto imutável; aprovação 0.2.0 não aprova 0.2.1. Rollback recusa 0.2.1 e descarta só derivado próprio, nunca fonte.
10. CI: guard de paths K continua bloqueio de P02/C4; não alterar pins, manifests históricos, allowlist ou continue-on-error para obter verde.

Caderno 0.1.0a1, RO-Crate 1.3, Process Run 0.6, reader003 e SDK/Catalog permanecem independentes. HL7/FHIR é FUTURE_CAPABILITY_ONLY. Sem novos tipos Project/Experiment artificiais, migração, retirada, limpeza, poderes de host ou aprovação científica.
