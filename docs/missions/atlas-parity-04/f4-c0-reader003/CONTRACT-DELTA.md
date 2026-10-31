# Delta e matriz de impacto — contrato 003 AP04 v0.2

Owner/writer: coordenador C0 /root; contribuições de análise nativa A e B, sem escrita. Data: 2026-10-31.
PLAN observado: 296a47245059fa473715fd4fcf9bf96011c19f44, tree 2b8eaac88578899852c71d32c5f2244455f6441b, parent 54bb16d350f7bc34fafb95438bd64a2397d58bf3. Blobs/objetos: INPUT-SHAS.json, OUTPUT-OBJECTS.json, manifesto e envelope Git.

## Conflito resolvido pela decisão humana, sem reescrever a história

O reader003 histórico (blob eb4feb7b4f829d97b048fc9d343861d9297ec04b) tem duas restrições globais: entrada exclusiva Caderno e proibição de caminho/endpoint/schema/perfil. File API também é nova entrada no viewer. O adendo não oculta essa contradição: sucede o alcance global dessas restrições SOMENTE no painel O3 selecionado manualmente, apoiado na ADR-0003 v0.2 APPROVED_SCOPED por versão/SHA/comentário 6539419419. Demais usos continuam integralmente no contrato histórico. Nenhum fallback/reconciliação entre vias.

| Fronteira | Antes preservado | Exceção/obrigação nova | Evidência C0 / prova futura |
|---|---|---|---|
| reader003 | Caderno-exclusivo, bytes congelados | Precedência local O3 por adendo novo versionado | Revisão documental C; nenhum reader alterado |
| Caderno→SDK→Catalog→API C4 | Via científica existente exclusiva | Nenhuma ingestão do descriptor | Blobs idênticos; regressão runtime C3/C4 NOT_RUN |
| O1 externo LOCAL | Não integra runtime Atlas | Leitura autorizada explícita de projeção preexistente; JSON privado temporário | Contrato; C2/L1 executam e qualificam separadamente |
| O3 opcional | Não existe implementação por C0 | File API manual; validação atômica; painel segregado RAM/TTL | C3 futuro, não executado C0 |
| Schema descriptor | Blob F2 25d79a11171c157bd3c7e0f98d1449a78237fd9c | Herança por referência, shape + 11 invariantes extras | Nenhum schema novo ou versão alterada |
| Segurança HTTP | CSP/Host/Origin/no-store/nosniff existentes | Apenas assets fixos futuros; zero endpoint novo/upload | C3/C4 futuros, nada de server.py alterado |
| Identidade | IDs nativos com origem; contexto próprio Caderno | Tokens sessão/fonte/snapshot/ocorrência legados independentes | N01–N09/N18 em C3/C4 |
| Interoperabilidade | RO-Crate1.3/ProcessRun0.6/Caderno0.1.0a1 | Nenhum pin/schema/contexto modificado | Inspeção Git; testes posteriores |
| HL7/FHIR | Capacidade opcional por domínio | Sem perfil/versão/IG/implementação alegados | UNKNOWN até futura missão própria |
| Fonte/R4/privacidade | Sem importação privada, origem intacta | Nenhum acesso ou publicação de fonte em C0 | Só fontes documentais públicas do repo |
| Plano/GATES/F1/F2 | História e estados por época | Nenhuma mudança ou promoção | Imutabilidade por blobs/tree |

## D-001–D-020 e ARC

| Decisões | Atendimento e limite |
|---|---|
| D-001 / ARC-01–03 | UI, protocolo e armazenamento separados; LEGACY_DERIVED descartável, sem autoridade |
| D-002 / ARC-04–05 | Sem r4.*; RF/RNF/RES opcionais; Caderno sem legado e SDK sem UI |
| D-003 / ARC-06 | Shape, semântica, integridade, origem, autenticação e ciência em eixos distintos |
| D-004 / ARC-07 | O1 externo; sem reconstruir leitor Windows, poderes do host ou manutenção na UI |
| D-005 / ARC-08 | CA-01 continua referência provisória; nenhuma fonte retirada ou promoção |
| D-006 / ARC-09 | Exceção explícita aprovada no pacote c3ea1e8; C0 versiona/revisa antes de integrar |
| D-007 | Direção RO-Crate1.3/ProcessRun0.6/Caderno0.1.0a1 preservada; sem release |
| D-008/D-009 | C4 e F1 são evidências históricas escopadas; C0 não comprova paridade nem reaproveita CI |
| D-010 | TTL/cache próprio não concede retenção física/G9 |
| D-011 | BIM/IFC/IDS/SHACL seguem roadmap, sem implementação C0 |
| D-012/D-013 | Continuidade AP04; árvore/RF/gaps preservados; sem recuperar UI nesta missão documental |
| D-014/D-015 | Sem reorganização/conversão em massa; leitura temporária externa contratada |
| D-016 | Ponto de extensão HL7/FHIR mantido sem falso rótulo conforme |
| D-017 | Evolução produtora R4 pertence a F6, fora de C0 |
| D-018 | Branch convencional preexistente; sem clones/worktrees |
| D-019 | Este confronto por decisões, PAR e gates é parte da entrega |
| D-020 | Nenhum histórico/experimento apagado ou movido |

## PAR e gates: contribuição apenas documental

| PAR | Contribuição C0 | Pendência preservada |
|---|---|---|
| PAR-001/002/004 | Identidade e vínculo explícito entre componentes, sem caminho inventado | UI/linha literal/jornada C3/F5; Run isolado e quatro tabelas desvinculadas |
| PAR-003 | RNF/RES opcionais; não inferir disponibilidade | INPUT_AVAILABILITY_UNKNOWN |
| PAR-005/006 | File ≠ produto; papel/vínculo; URI inerte, disponibilidade distinta | Jornadas de produtos/documentos não recuperadas por C0 |
| PAR-007/008 | Relações/direções/órfãos/tempos e gaps sem inferência | Browser e linha temporal não executados |
| PAR-009/010 | UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN; denominadores null; armazenamento consultivo | Sem exaustividade, limpeza ou percentual inventado |
| PAR-011 | Contrato versionado/revisável resolve dependência arquitetural delimitada | O1 real, host e G4 dependem C2/L1 |
| PAR-012 | Fronteiras/bytes preservados, prova de isolamento exigida | G5 depende C3/C4 no SHA integrado |
| PAR-013 | HL7/FHIR futuro por domínio | Sem versão/IG/perfis/implementação/conformidade |
| PAR-014/015 | Fidelidade/negativos/token/literalidade obrigatórios | F5/G6 e nova imutabilidade real não executados |

Nenhum PAR recebe RECOVERED_VERIFIED por C0. Critérios/pesos P0/P1 e PAR-005–010 permanecem no plano. G1 é disponibilidade histórica F1; aprovação arquitetural posterior é APPROVED_SCOPED, não G4 operacional. G2/G3/G4/G5/G6/G7 não são qualificados; G8/G9 não autorizados. GATES.json e cabeçalhos F1/F2 permanecem byte-idênticos.

## Contraprovas documentais efetivamente examinadas

- Confundir File API com nenhuma entrada adicional: rejeitado expressamente, resolvido por sucessão local aprovada.
- Aplicar exceção ao SDK/endpoint/Catalog: rejeitado, só O3 manual.
- Criar schema/perfil Caderno: rejeitado, descriptor F2 por blob fixado.
- Navigation ID admitir RF ou stub resolver entidade: rejeitado; 28 native_id null e Run SOURCE_ENTITY isolado preservados.
- Digest/CI/revisão promover autenticidade, ciência ou gates: rejeitado.
- Ausência de prova virar PASS: campo sem evidência UNKNOWN; runtime NOT_RUN.
- Alterar guard histórico para aceitar o adendo: vedado; sucessão CI ownership C4.

São verificações do texto, sem execução adversarial de produto. Lista executável futura em SECURITY-AND-ROLLBACK.md. Não houve mudança de AP04-POR, alternativas técnicas implementadas ou necessidade de solicitar desvio. Se nova interpretação ampliar escopo, parar antes de agir.
