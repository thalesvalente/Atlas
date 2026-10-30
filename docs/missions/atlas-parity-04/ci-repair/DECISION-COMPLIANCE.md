# Conformidade com decisões e gates

## D-001–D-020

| Decisão | Estado | Evidência desta frente |
|---|---|---|
| D-001 | `COMPLIANT` | No change to Atlas/Caderno/storage separation. |
| D-002 | `COMPLIANT` | No R4 import or producer-name coupling; only CI controls changed. |
| D-003 | `COMPLIANT` | Engineering CI remains distinct from authenticity, state and scientific approval. |
| D-004 | `COMPLIANT` | No compatibility reader, migration, deletion or runtime change implemented. |
| D-005 | `COMPLIANT` | C4 and historical objects are immutable; no paridade/promotion claim. |
| D-006 | `COMPLIANT` | ADR-0003 remains proposed; the repair does not implement the architectural option. |
| D-007 | `COMPLIANT` | ADR-0002 direction remains untouched and no release is authorized. |
| D-008 | `COMPLIANT` | No complete-parity claim is made. |
| D-009 | `COMPLIANT` | C4 evidence is preserved but not transferred to the successor SHA. |
| D-010 | `COMPLIANT` | No cleanup, retention action, worktree deletion or physical change. |
| D-011 | `COMPLIANT` | No BIM/IFC/IDS/SHACL implementation or claim. |
| D-012 | `OUT_OF_SCOPE_PRESERVED` | Repair only unblocks documentation CI; no restart or parity implementation. |
| D-013 | `OUT_OF_SCOPE_PRESERVED` | No legacy UI feature implementation in this mission. |
| D-014 | `COMPLIANT` | No corpus reorganization or bulk conversion. |
| D-015 | `OUT_OF_SCOPE_PRESERVED` | No legacy reader is implemented; proposal remains pending. |
| D-016 | `COMPLIANT` | HL7/FHIR possibility is neither removed nor claimed implemented. |
| D-017 | `COMPLIANT` | No R4 change. |
| D-018 | `COMPLIANT` | No remote clone/worktree; only temporary synthetic Git repositories for tests. |
| D-019 | `COMPLIANT` | This file and RESULT explicitly reconcile the repair with the plan. |
| D-020 | `COMPLIANT` | No experiment/history moved or deleted. |

## ADRs

- ADR-0001 e ADR-0002: nenhum byte alterado por este delta.
- ADR-0003: os nove documentos originais são verificados por blob/bytes; estado obrigatório `PROPOSED_NOT_APPROVED`.
- Nenhuma ADR futura ou prefixo `docs/architecture/` foi liberado.

## HL7/FHIR

A capacidade futura permanece apenas uma direção registrada. Nenhum recurso, perfil, versão, guia de implementação, conformidade clínica ou claim HL7/FHIR foi introduzido.

## G0–G9

Os valores de `GATES.json` são byte-idênticos à baseline documental: G0 `DOCUMENTATION_DRAFT`; G1–G3 `NOT_RUN`; G4 `ARCHITECTURAL_DECISION_PENDING`; G5 `C4_BASELINE_ONLY`; G6 `USER_OBSERVATION_PARTIAL`; G7 `NOT_QUALIFIED`; G8/G9 `NOT_AUTHORIZED`. O reparo de CI não promove nenhum gate.

## Mudança de plano

`NONE`. O delta implementa o mecanismo de sucessor/overlay previsto na missão, sem alterar PAR-001–PAR-015 ou o plano AP04 original.

## Retomada PUBLISH-REVIEW-03

O ajuste de executor usa apenas o checkout e ambiente de engenharia existentes, autorizado pelo operador após o bloqueio anterior. A correção dos dois defeitos do patch permanece no ownership dos mesmos guard/testes/recibos; não altera objetivo, aceite ou fronteira arquitetural.

PAR-001–PAR-011, PAR-013–PAR-014: nenhum avanço funcional. PAR-012/PAR-015: apenas provas novas de não regressão/integridade no SHA técnico 54ffea9e8fe2ed5cde071a8ec52fbcbff857df60, com seis workflows/33 jobs terminais success; o commit dos recibos requer seus próprios gates. Nenhum estado da matriz ou de GATES.json é promovido. Os nove documentos e manifestos históricos permanecem byte-idênticos.

ARC-01–09 e ADR-0001 permanecem intactos por bytes e sem mudança arquitetural. A rejeição local por CRLF não autoriza normalizar arquivos congelados; nenhum desses arquivos foi escrito. A aprovação técnica da CI não promove G0–G9, a matriz PAR nem o host para uso operacional.
