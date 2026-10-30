# Decisões reconciliadas — Atlas anterior, C4 e direção atual

**Data:** 2026-10-30. **Versão:** AP04-POR-v1.0-draft.  
**Precedência:** constituição ARC-01–09; ADR-0001; aceite posterior da ADR-0002 na PR #5; evidências por SHA das campanhas; diretrizes atuais do operador; propostas técnicas subordinadas a esses limites.

## Decisões anteriores preservadas

| ID | Conteúdo e fonte | Estado |
|---|---|---|
| D-001 | ARC-01–03 / ADR-0001: Atlas é interface independente; Caderno é contrato interoperável; armazenamento e indexação derivada são separados | VINCULANTE |
| D-002 | ARC-04/05: R4 é produtor externo; Atlas e SDK devem funcionar sem r4.* ou diretórios históricos; RF/RNF/RES não são tipos obrigatórios universais | VINCULANTE |
| D-003 | ARC-06: validade, integridade, origem declarada, autenticidade, estados e aprovação científica são eixos distintos | VINCULANTE |
| D-004 | ARC-07: manutenção, compatibilidade e leitor Windows suspenso NÃO entram no runtime principal; sem poderes de migração ou exclusão | VINCULANTE |
| D-005 | ARC-08: CA-01 permanece referência provisória até paridade e promoção humana; originais, históricos e Caderno legado são preservados | VINCULANTE |
| D-006 | ARC-09: desvio arquitetural exige ADR sucessora versionada, alternativas, riscos, revisão independente e aprovação humana explícita antes da implementação | VINCULANTE |
| D-007 | ADR-0002 v1.0: RO-Crate 1.3 + Process Run 0.6 + Caderno 0.1.0a1 foram aceitos como DIREÇÃO DE ESTABILIZAÇÃO na PR #5; o cabeçalho histórico PENDING_HUMAN é anterior ao recibo | ACEITE DELIMITADO; SEM RELEASE |
| D-008 | ATLAS-PARITY-01/02: C0 era primeiro incremento, não paridade completa; estudos integrais A/B/C/D nem sempre estavam disponíveis por bytes nas frentes | OBJETIVO DE PARIDADE EM ANDAMENTO |
| D-009 | ATLAS-PARITY-03 C4: código composto, CI 6 workflows/31 jobs no SHA final, P03 metadados/tabelas de propriedades; nenhum teste de paridade legada integral ou promoção | OBSERVADO NO SHA C4 |
| D-010 | Retenção, eliminação de experimentos e limpeza de worktrees são decisões físicas separadas, com revisão e autorização próprias | NÃO AUTORIZADAS NESTA FRENTE |
| D-011 | BIM/IFC/IDS/SHACL foram mencionados anteriormente como roadmap, não como parte implementada da PoC | ROADMAP |

## Direções explícitas do operador na conversa de 2026-10-30

| ID | Decisão funcional ou limite | Estado |
|---|---|---|
| D-012 | Continuar, não reiniciar, a recuperação de paridade com o Atlas legado | DIREÇÃO DO OPERADOR |
| D-013 | Recuperar árvore gráfica clicável, tabelas RF/RNF/RES e demais recursos antigos, mantendo e melhorando a C4 | DIREÇÃO DO OPERADOR |
| D-014 | NÃO gastar agora com reorganização de pastas, documentação histórica ou conversão persistida em massa para o novo padrão | DIREÇÃO DO OPERADOR |
| D-015 | Priorizar braço de leitura legada / adaptação rápida e temporária, sem alterar a origem | DIREÇÃO DO OPERADOR; IMPLEMENTAÇÃO TÉCNICA A DELIBERAR |
| D-016 | Preservar interoperabilidade e a possibilidade HL7/FHIR para domínios de saúde; não abandonar padrões existentes | DIREÇÃO DO OPERADOR; NENHUMA IMPLEMENTAÇÃO FHIR COMPROVADA |
| D-017 | Evoluir o R4 futuramente para produzir diretamente padrões interoperáveis; não nesta execução Atlas | DIREÇÃO FUTURA, FORA DE ESCOPO |
| D-018 | Priorizar branches e checkout existente; não criar worktrees/clones | DIREÇÃO DO OPERADOR |
| D-019 | Exigir confronto dos resultados de cada nova frente com este plano e matriz | DIREÇÃO DO OPERADOR |
| D-020 | Não apagar/mover experimentos ou históricos para melhorar a UI; preservação é gate separado | REAFIRMAÇÃO D-005/D-010 |

## Tensões identificadas; não resolver por interpretação conveniente

1. **Novo caminho de entrada × ARC-04/07:** a solução preferida é compatibilidade em ferramenta externa, mas aceitar novo formato de apresentação no viewer pode alterar a fronteira acordada. ADR-0003 é proposta, NÃO aprovação dessa alteração.
2. **Caderno apenas × leitura legada:** compatibilidade de apresentação temporária não torna fonte legada um pacote Caderno conforme; não mudar schema e versão do protocolo para fazê-la parecer conforme.
3. **C4 passou CI × paridade antiga:** CI verde do C4 não prova árvore ou RF literal; dados de P04 são um recorte.
4. **PENDING_HUMAN histórico × aceite posterior:** a ADR-0002 recebeu aceite de direção na PR #5, sem autorizar release, migração, extensões futuras ou ciência.
5. **HL7/FHIR obrigatório como possibilidade × implementação:** direção atual reserva capacidade e extensão por domínio, mas nenhuma versão, guia ou recursos FHIR específicos estão fixados.
6. **Pressão para liberar espaço × preservação:** intenção futura de retenção não autoriza excluir experimentos/worktrees nesta campanha.

## Decisões ainda abertas

- OPEN-01: contrato de projeção legada efêmera e fronteira técnica; revisão/aceite da ADR-0003 se houver desvio ARC-09.
- OPEN-02: qual fonte existente contém RF literais e hierarquia; confirmação de acesso sem publicação.
- OPEN-03: como servir uma projeção neutra para UI sem importar código privado ou acoplar núcleo à estrutura R4.
- OPEN-04: versão/perfis/casos de uso HL7/FHIR; direção preservada, conformidade não demonstrada.
- OPEN-05: denominador real da paridade do legado; deve ser medido, não deduzido de dois runs.
- OPEN-06: liberação expressa caso alguém proponha transferir bytes de código privado para repositório público.
- OPEN-07: atos de merge, release, promoção e exclusão física continuam independentes.

Novas decisões exigem ID, data, SHA, fonte, motivo, alternativas, impacto, revisor, autorização e quais decisões anteriores substituem. Não apagar histórico para melhorar status.
