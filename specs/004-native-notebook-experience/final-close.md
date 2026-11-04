# ATLAS-FINAL-CLOSE — contrato e matriz única

Data local: 2026-11-03. Estado inicial: **PARTIAL / engenharia em execução**.
Base: PR23 `a1b45d2f361c1900c7c8569b32def2601a3d4464` seguida de PR24
`7c72d9c863871f3541eadb6aac85cab864ad559f`. Integração exclusiva em
`integrate/atlas-final-close-20261103`; o SHA final e seus recibos terminais
serão publicados na conversa da PR, evitando assinatura circular no commit.

## Método observado

Spec Kit CLI 1.2.3 e integração Codex conferidos no Windows; setup_plan.py,
setup_tasks.py e check_prerequisites.py realmente executados com Feature004
explícita e NO_PERSIST, sem alteração de feature.json. Checklist de requisitos:
5/5 completo. Constitution ARC-01–09, ADR0001/0002 e AP04 lidos.
Darwin local `adw_local` 0.0.1 executou doctor somente leitura; não possui o
compilador de prompt V0/v0.03 neste ambiente. Nenhum prompt compilado é alegado
como execução; TASKGEN/Source Bridge não são necessários para estes patches.
PLAN/EXECUTE/REVIEW/INTEGRATE/QA/HANDOFF são coordenados em chat, com subagentes
nativos reais P01/P02/P03 e ownership isolado. Nenhum arquivo Darwin é alterado.

## Matriz reconciliada

IMPLEMENTADA significa código presente; TESTADA exige prova observada no escopo
declarado; ABERTA exige trabalho/prova; BLOQUEADA identifica gate externo;
FORA DO ACEITE preserva alternativa/futuro sem promovê-lo a funcionalidade pronta.

| Item existente | Estado inicial | Owner / evidência ou trabalho material |
|---|---|---|
| T001–T014; R001–R005/R007–R009/R011/R013/R015 | TESTADA | Código já incorporado em PR23/24; baseline local normal PASS (117 testes, 2 skips). Requalificar integrada, sem reabrir implementação. |
| R016 / FR013 / PAR001 | IMPLEMENTADA | PR24: foco25→49, busca integral; CI13/13 e Codex sem findings em7c72. P01 verifica rótulos largos e navegação no sucessor. |
| US2 busca/filtros/demais telas e SC002 | ABERTA | P02: contraprovas de busca de tabela, coleções e responsividade. |
| Finding4446002065 / FR010–012 | ABERTA | P03: launcher compat ainda repetia API integral; reaproveitar supervisor corrigido. |
| T015 / R006 / parte review de R014 | ABERTA | Codex+P05 no SHA integrado; reviews antigos não são aprovação do sucessor. |
| T016 / R010 / R012 / parte host de R014 / PAR014 | ABERTA | Windows real: comando, projeção, confronto funcional/visual e integridade; referência observada174registros/2911nós/5tabelas152linhas/912recursos não é teto. |
| PAR002/PAR003 tabelas originais; PAR004 navegação | IMPLEMENTADA | Payload original, P03 table e detalhe/export por ocorrência; P02/P05 verificam filtros/linhas reais sem publicar conteúdo. |
| PAR005 produtos/grupos/versões; PAR006 documentos/dossiês | IMPLEMENTADA | Coleções/metadados nativos genéricos; vínculos somente quando declarados; conferir acessibilidade no host. |
| PAR007 relações; PAR008 timeline; PAR009 cobertura; PAR010 armazenamento consultivo | IMPLEMENTADA | Visões e campos declarados preservados; sem inferir causalidade, denominador, disponibilidade externa ou comandos de limpeza. |
| PAR011 acesso externo; PAR012 independência/padrões; PAR015 integridade | IMPLEMENTADA | NativeView004 reutiliza project() externo; viewer/SDK independentes; requalificar fontes imutáveis e negativos. |
| PR16 F3A; PR17 F3B | FORA DO ACEITE | Reuso seletivo: componente público P03 já incorporado por blob; F3A descriptor0.2.0 não substitui identidade estrutural da NativeView. Sem merge indiscriminado. |
| PR18/19/20/21/22 C2-D/reader003/C2-B/C2-K/L0 | BLOQUEADA | P04 reconcilia alternativas separadas. Nenhum path/implementação/documentação C2-K não aprovada entra na candidata. |
| PAR013 HL7/FHIR; issue2 BIM/IFC/IDS/SHACL | FORA DO ACEITE | Extensibilidade/futuro, sem alegar conformidade implementada. |
| Estabilização ADR0002, aceite humano, G8/G9 | BLOQUEADA | Aceite/protocolo, merge/release/deploy e retenção têm autorizações próprias; esta missão não as concede. |

## Checklist de entrega para aceite

- [ ] Um SHA integrado, PR Draft e Actions terminais nesse SHA.
- [ ] Regressões/negativos/Chromium sem erros materiais; fontes preservadas.
- [ ] Codex e QA P05 não autora com recibos no SHA exato.
- [ ] Comparação funcional, visual e de integridade no Caderno real Windows.
- [ ] Conferência humana da árvore, busca, seleção, tabelas/exports e demais telas.

Os quatro primeiros qualificam engenharia para **ATLAS_READY_FOR_USER_ACCEPTANCE**.
O último é decisão humana posterior; não é fabricado pelo coordenador.
