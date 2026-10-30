# Interoperabilidade, HL7/FHIR e padrões — proteção contra regressão

| Contrato | Situação comprovada | O que manter |
|---|---|---|
| RO-Crate 1.3 | Parte da direção aceita ADR-0002 | Pacotes, identidades, metadados, referências e recuperação independente do viewer |
| Process Run Crate 0.6 | Complemento previsto na ADR-0002 | Execuções e proveniência declarada |
| Caderno 0.1.0a1 | Perfil candidato, não release estável | SDK, schema/contexto, validação e independência do produtor/Atlas |
| JSON-LD e JSON Schema | Serialização/validação do perfil restrito | Preservar contextos e negativas de formato não suportado |
| PROV | Algumas relações declaradas de derivação | Não alegar conformidade PROV integral nem causalidade por associação |
| HL7 / HL7 FHIR | Exigência de capacidade futura reafirmada em 2026-10-30; implementação pública não comprovada | Arquitetura extensível por domínio de saúde, sem impor modelo clínico universal |
| BIM, IFC, IDS, SHACL | Roadmap anterior, não parte da PoC inicial | Conservar possibilidade futura, sem fingir implementação |

## HL7/FHIR não é sinônimo de Caderno

HL7 FHIR é padrão de intercâmbio eletrônico de informações de saúde. Pode coexistir com RO-Crate/Process Run, que organizam dados de pesquisa e proveniência. O Atlas não transforma automaticamente uma execução genérica em recursos clínicos.

Para decidir um adaptador FHIR serão necessários: caso de uso clínico, versão, Implementation Guide, recursos/perfis, identificadores, terminologias, consentimento/privacidade, proveniência e testes próprios. Nenhum deles foi aprovado em versão concreta nesta campanha. Não declarar FHIR conforme por ter uma opção no roadmap.

## Regras executáveis no futuro

- O Caderno funciona sem a UI e sem o R4; a UI funciona sem o modo legado.
- Nenhuma fonte legada fica rotulada RO-Crate ou FHIR conforme sem validação real do padrão e perfil anunciado.
- Adaptadores de domínio não alteram o protocolo base por conveniência.
- Estados, ausência, unidades, timestamps e origem não são inferidos para atender a uma tela.
- A aceitação de documentos/recursos clínicos requer controles de privacidade e autorização próprios.
- Novos relatórios de paridade discriminam IMPLEMENTADO, PLANEJADO, NÃO TESTADO e NÃO CONFORME, por padrão.

Referências externas: [HL7 FHIR](https://hl7.org/fhir/), [RO-Crate 1.3](https://www.researchobject.org/ro-crate/specification/1.3/), [Process Run Crate 0.6](https://www.researchobject.org/workflow-run-crate/profiles/0.6/process_run_crate/).

O aceite da ADR-0002 na PR #5 é de direção de estabilização, não ratificação de HL7, migração ou release.
