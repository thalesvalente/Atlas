# F2 — Checklist do gate de decisão arquitetural

**Estado neste commit:** PROMPT_ONLY_NOT_RUN. Nenhuma ADR aprovada e nenhum adaptador implementado.

| ID | Condição de F2 | Estado inicial |
|---|---|---|
| F2-01 | Plano AP04, C4 e F1 fixados por SHA/tree/parent, sem dados privados importados | NOT_RUN |
| F2-02 | Leitor Caderno-exclusivo do contrato 003 confrontado com ARC-04/07/09 | NOT_RUN |
| F2-03 | Opções O1–O5 comparadas, escolha justificada e rollback | NOT_RUN |
| F2-04 | Proposta de contrato efêmero neutro, com exemplos sintéticos e limites | NOT_RUN |
| F2-05 | Hierarquia e relacionamentos explícitos; órfãos não promovidos a ancestrais | NOT_RUN |
| F2-06 | Quatro tabelas sem record_id, 28 RF não admitidas e binding_gap mantidos | NOT_RUN |
| F2-07 | Colisões, relações null/não resolvidas e repetidos representáveis sem perda | NOT_RUN |
| F2-08 | RF literal, categoria ausente, File/produto, estados e cobertura preservados | NOT_RUN |
| F2-09 | Segurança de paths, origens, HTML/CSV, limites, cache e fonte modificável tratada | NOT_RUN |
| F2-10 | Não regressão RO-Crate/Process Run/Caderno e HL7/FHIR futuro sem false PASS | NOT_RUN |
| F2-11 | ADR-0003 v0.2 continua PROPOSED; decisão ARC-09 explícita e versionada | NOT_RUN |
| F2-12 | Plano F0–F6 e PAR/Gates preservados, sem mudança silenciosa | NOT_RUN |
| F2-13 | Contraprovas/expectativas futuras documentadas sem simular execução | NOT_RUN |
| F2-14 | Revisão real independente do SHA terminal ou indisponibilidade honesta | NOT_RUN |
| F2-15 | Saídas documentais persistidas em Git com SHA/tree/parent e ownership estrito | NOT_RUN |
| F2-16 | F3A/F3B/F4/F5/F6, produto/runtime e acervo não foram alterados | NOT_RUN |
| F2-17 | Pergunta de decisão humana específica e vinculada à versão/SHA pronta | NOT_RUN |

**Status permitido:** `F2_ARCHITECTURE_DECISION_READY_FOR_HUMAN_REVIEW` / `F2_REVIEW_PENDING` / `F2_INPUT_BLOCKED_EXACT` / `F2_CONTRACT_BLOCKED_EXACT`.

`F2_ARCHITECTURE_DECISION_READY_FOR_HUMAN_REVIEW` não concede aprovação da ADR-0003, não qualifica G4 e não é paridade funcional. Árvore SVG e RF visual ainda dependem de F3/F4/F5.
