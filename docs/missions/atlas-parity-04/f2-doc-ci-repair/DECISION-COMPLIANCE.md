# Confronto com AP04-POR-v1.0-draft

Plano/decisões/matriz/GATES mantêm os blobs publicados no SHA 47c94d27aeb7717eebb30804f01cd2cd33507c8a. O reparo modifica somente controles CI e seus novos recibos, sob a autorização específica AP04-F2-DOC-CI-REPAIR-01 no SHA 8abf556c6c39fcc54855391f2eeef3d8a8615985. Nenhuma mudança de ordem F0–F6, critérios PAR, gates ou arquitetura foi identificada como necessária. Não houve PLAN-DEVIATION-REQUEST nem desvio implementado.

## Decisões D-001–D-020

| ID | Preservação no reparo |
|---|---|
| D-001 | Interface/protocolo/armazenamento separados; runtime e APIs não alterados. |
| D-002 | Nenhum import R4 ou domínio RF obrigatório; instalação independente continua gate. |
| D-003 | CI/digest/origem e aprovação científica permanecem distintos. |
| D-004 | Nenhum leitor/compatibilidade do host entra no runtime; nenhum poder de migração. |
| D-005 | CA-01/históricos e fontes preservados; nenhuma promoção. |
| D-006 | ARC-09/ADR sucessora e aprovação humana antes de desvio; este reparo CI é compatível com o plano. |
| D-007 | Direção ADR-0002 recebida anteriormente não é release; perfil/pins/protocolo intactos. |
| D-008 | Paridade permanece trabalho em andamento; CI documental não comprova acervo integral. |
| D-009 | C4 congelada por SHA/tree e regressão atual, sem herança automática da CI antiga. |
| D-010 | Retenção e limpeza continuam fora do escopo e sem autorização. |
| D-011 | BIM/IFC/IDS/SHACL continuam roadmap; nenhuma implementação afirmada. |
| D-012 | Continuidade das épocas C4/AP04/F1/F2, sem reinício ou reescrita. |
| D-013 | Árvore/RF e demais recursos seguem suas fases; nenhum item foi concluído por este reparo. |
| D-014 | Nenhuma reorganização, conversão persistida ou migração em massa. |
| D-015 | Leitura externa efêmera continua proposta; nenhum adaptador ou entrada implementado. |
| D-016 | HL7/FHIR continua capacidade futura por domínio, sem conformidade alegada. |
| D-017 | Nenhuma alteração R4, produtor, pipeline ou fonte. |
| D-018 | Branch existente PR #15; nenhum clone/worktree/branch/PR adicional. |
| D-019 | Este confronto mantém D/PAR/G0–G9 por referência aos blobs originais. |
| D-020 | Nenhum experimento/histórico/fonte movido, apagado ou publicado. |

## PAR-001–PAR-015

A coluna de estado é a baseline literal AP04, não uma promoção pelo reparo. Os documentos F1/F2 que distinguem evidências posteriores permanecem imutáveis.

| ID | Baseline AP04 preservada | Limite atual |
|---|---|---|
| PAR-001 | NOT_RECOVERED | Árvore/UI não implementada; G2 não promovido. |
| PAR-002 | NOT_RECOVERED | RF literal privada não publicada; nenhuma prova de RF na UI. |
| PAR-003 | INPUT_AVAILABILITY_UNKNOWN | RNF/RES não inferidas de RF ou testes sintéticos. |
| PAR-004 | PARTIAL_NOT_EQUIVALENT | binding_gap e ausência de caminho contínuo F1 preservados. |
| PAR-005 | NOT_RECOVERED | Jornada de produtos permanece aberta. |
| PAR-006 | PARTIAL_NOT_EQUIVALENT | Documentos/dossiês continuam lacuna de jornada. |
| PAR-007 | PARTIAL_NOT_EQUIVALENT | Sem nova causalidade ou vínculos inventados. |
| PAR-008 | PARTIAL_NOT_EQUIVALENT | Datas/histórico não reinterpretados. |
| PAR-009 | PARTIAL_NOT_EQUIVALENT | UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN e denominadores preservados. |
| PAR-010 | NOT_RECOVERED | Armazenamento consultivo sem exclusão. |
| PAR-011 | CONTRACT_DECISION_PENDING | ADR-0003 v0.2/descriptor 0.2.0 e G4 pendentes. |
| PAR-012 | BASELINE_VERIFIED | Baseline histórica não promove o novo SHA; regressão CI atual é gate próprio. |
| PAR-013 | ARCHITECTURE_REQUIREMENT_ONLY | HL7/FHIR futuro, sem implementação ou conformidade. |
| PAR-014 | OBSERVED_PARTIAL | Browser público/sintético C4 não substitui demonstração LOCAL privada. |
| PAR-015 | BASELINE_VERIFIED_SCOPE | Integridade de blobs públicos verificada; acervo privado não reobservado. |

## Gates e autoridade

G0 segue documentação Draft; G1 conserva somente o PASS F1 escopado publicado, sem revalidar fontes. G2/G3 não foram executados nesta missão. G4 continua ARCHITECTURAL_DECISION_PENDING. G5 depende da CI real no SHA novo; G6 privado permanece observação parcial, não substituído por browser sintético. G7 não é qualificação de paridade. G8/G9 continuam NOT_AUTHORIZED.

ADR-0003 histórica e candidata v0.2 mantêm PROPOSED_NOT_APPROVED. Descriptor 0.2.0 e pergunta humana no SHA técnico c3ea1e82938fd61cc5a22fee973352715a5bb527 permanecem intactos. CI verde não altera a decisão PENDING_HUMAN_DECISION nem inicia File API/F3A/F3B/F4/F5/F6.

Protocolo, schema/contextos, reader003 Caderno-exclusivo, managed assets Spec Kit 1.2.3, auditor P06, ASSETS/INPUTS/COMPOSITION C4, fixtures, AGENTS e skills são protegidos. P06 continua RED histórico para a ADR-0003 exata; a exceção não libera diretório.

Merge, release, deploy, promoção, migração, R4, transferência de fonte privada, ciência, HL7/FHIR conforme e limpeza permanecem sem autorização.
