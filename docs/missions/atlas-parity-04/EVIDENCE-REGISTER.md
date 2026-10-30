# Registro de evidências e limites — 2026-10-30

## Fontes primárias públicas

- E01 — [Constituição ARC-01–09 no SHA C4](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/.specify/memory/constitution.md). Regras de arquitetura e governança.
- E02 — [ADR-0001](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/architecture/ADR-0001-atlas-protocol-producers-storage.md). Interface, protocolo, produtores e armazenamento.
- E03 — [ADR-0002 v1.0](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/architecture/ADR-0002-protocol-candidate.md). Texto histórico PROPOSED/PENDING_HUMAN.
- E04 — [PR #5 / recibo de aceite](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421). Aceite posterior como direção de estabilização, não release nem ciência.
- E05 — [Contratos P01](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/contracts/atlas-parity-02/p01/PRESENTATION-CONTRACTS.md). O que é representável, o que exige contrato e o que permanece desconhecido.
- E06 — [Matriz P01](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/missions/atlas-parity-02/p01-contracts/CAPABILITY-PARITY.csv). Mapeamento da paridade por camada, não prova de todas as jornadas legadas.
- E07 — [Feature 004 C0](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/specs/004-atlas-parity-c0/spec.md). Incremento parcial já planejado, com preservação das restrições.
- E08 — [PR Draft #13 C4](https://github.com/thalesvalente/Atlas/pull/13). SHA final 72d9b94e613a57c82a5afd309796f44b271e2185; CI 6 workflows/31 jobs, nenhuma paridade integral/release.
- E09 — [Decisão de integração C4](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/missions/atlas-parity-03/c4-full-convergence/INTEGRATION-DECISION.md). Gate local diferido e limites.
- E10 — [Perfil Caderno](https://github.com/thalesvalente/Atlas/blob/72d9b94e613a57c82a5afd309796f44b271e2185/docs/protocol/0.1.0a1.md). Forma candidata restrita, não FHIR.
- E11 — [HL7 FHIR oficial](https://hl7.org/fhir/), [RO-Crate 1.3 oficial](https://www.researchobject.org/ro-crate/specification/1.3/) e [Process Run Crate 0.6](https://www.researchobject.org/workflow-run-crate/profiles/0.6/process_run_crate/). Padrões externos, não prova de implementação.

## Observações e fontes de escopo restrito

- E12 — Captura fornecida pelo usuário em 2026-10-30: C4 abriu localmente com 1 projeto, 1 experimento e 2 execuções; árvore hierárquica antiga e tabela RF literal ausentes. Não equivale a replay completo vinculado por SHA e não será publicada como imagem privada.
- E13 — Leitura permitida apenas para análise do legado privado: árvore SVG com temas/famílias, zoom/pan/minimapa; tabela de RF com IDs, núcleo, descrição, critérios de aceite; catálogos de produtos/documentos e cobertura. Nenhum byte de código, caminho privado ou dado científico foi transferido para Atlas público.
- E14 — Direção explícita do usuário em 2026-10-30: já estamos recuperando paridade; acelerar com leitura legada, sem migração em massa; manter padrões e HL7/FHIR; R4 depois; não criar worktrees; confrontar resultados com o registro.

## Lacunas e conflitos temporais

- Estudos A/B/C/D completos não foram inspecionados nesta revisão por bytes íntegros; não reivindicar todas as conclusões desses artefatos.
- Denominador da paridade e total do legado: UNKNOWN_UPSTREAM, não inferido por P04.
- HL7/FHIR: não há implementação/versão/perfil demonstrados no Atlas C4; o requisito de preservação da capacidade é explícito, porém não equivale a PASS de conformidade.
- ADR-0002: o cabeçalho histórico PENDING_HUMAN precede o recibo da PR #5, que aceita a direção; a assinatura de release/upgrade não foi concedida.
- O bloqueio WinError 10013 registrado em L2 pertence à missão/ambiente anteriores, não significa que toda execução de navegador no Windows falhe. A observação posterior da C4 deve ser registrada separadamente.
- Limpeza/migração, liberação de fontes privadas, aprovação científica e promoção permanecem não autorizadas.
