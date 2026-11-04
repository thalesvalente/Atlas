# ATLAS-FINAL-CLOSE — contrato e matriz única

Data local: 2026-11-04. **Código da composição qualificado; aceite humano pendente.**
Base: PR23 `a1b45d2f361c1900c7c8569b32def2601a3d4464` → PR24
`7c72d9c863871f3541eadb6aac85cab864ad559f`, com reuso seletivo dos handoffs
PR26/PR27 e correções autorais. Integração exclusiva em
`integrate/atlas-final-close-20261103`, [PR Draft #25](https://github.com/thalesvalente/Atlas/pull/25).

O código qualificado é `0cd96bce6f275a187ed2baf790793b77b5ae18e3`: CI 14/14,
Codex completed/zero findings e P05 não autora PASS. Este encerramento é somente
documental; o HEAD resultante exige atestação dos 32 arquivos executáveis,
Actions/Codex próprios e recibo da inicialização real. O SHA final fica no
recibo terminal da PR, sem assinatura circular em commit. Recibos anteriores
permanecem históricos e não qualificam o sucessor por suposição.

## Método observado

Spec Kit CLI 1.2.3 e integração Codex conferidos no Windows; setup_plan.py,
setup_tasks.py e check_prerequisites.py realmente executados com Feature004
explícita e NO_PERSIST, sem alteração de feature.json. Checklist de requisitos:
5/5 completo. Constitution ARC-01–09, ADR0001/0002 e AP04 lidos.
Darwin local `adw_local` 0.0.1 executou doctor somente leitura e gerou plano
auxiliar pinado ao spec/blob/base para o recorte de código; esse plano não foi
despachado nem usado para criar agentes/worktrees. A tentativa de incluir
workflow foi recusada como PROTECTED_SCOPE, sem mudar a política. O auxiliar não possui o
compilador de prompt V0/v0.03 neste ambiente. Nenhum prompt compilado é alegado
como execução; TASKGEN/Source Bridge não são necessários para estes patches.
PLAN/EXECUTE/REVIEW/INTEGRATE/QA/HANDOFF são coordenados em chat, com subagentes
nativos reais P01/P02/P03 e ownership isolado. Nenhum arquivo Darwin é alterado.

## Matriz reconciliada

IMPLEMENTADA significa código presente; TESTADA exige prova observada no escopo
declarado; ABERTA exige trabalho/prova; BLOQUEADA identifica gate externo;
FORA DO ACEITE preserva alternativa/futuro sem promovê-lo a funcionalidade pronta.

| Item existente | Estado qualificado | Owner / evidência e escopo |
|---|---|---|
| T001–T014; R001–R005/R007–R009/R011/R013/R015 | TESTADA | Reuso PR23/24, sem reabertura. P05: 119 testes por modo normal/-O (118 PASS/1 SKIP), instalação independente e negativos. |
| R016 / FR013 / PAR001 / T018 | TESTADA | P01: foco progressivo, rótulos largos contidos, busca/seleção/teclado/pan/zoom/minimapa; P05 conferiu a árvore real e o último nó. |
| US2 busca/filtros/demais telas; SC002 / T019 | TESTADA | P02: busca tabular e global da árvore, filtros, coleções vazias/globais. P05: sete áreas × 1440/390/320, sem overflow ou erros materiais. |
| Finding4446002065 / FR010–012 / T020 | TESTADA | P03: supervisor compatível compartilhado, sem preflight integral repetitivo; PowerShell 5.1 real normal/-O, falhas propagadas e fonte intacta. |
| T015 / R006 / review de R014 | TESTADA | Codex completed/zero findings em 0cd96bc; P05 não autora requalificou os findings registrados, com contraprovas próprias. Novo HEAD requer novo recibo, não aprovação herdada. |
| T016 / R010 / R012 / host de R014 / PAR014 | TESTADA | Windows real: comando e comparação funcional/visual/integridade; 174 registros/2911 nós/5 tabelas152 linhas/912 recursos nesta revisão, não tetos. Referência original composta privadamente sobre o mesmo snapshot, não build oficial novo. |
| PAR002/PAR003 tabelas originais | TESTADA | Cinco tabelas, primeiras/últimas linhas, JSON de ocorrência e linhas SHA-exatos, CSV protegido e cinco downloads CSV reais byte-exatos contra oracle Python independente; duas tabelas declaradas vazias mantidas vazias. |
| PAR004 navegação contextual / T023 | TESTADA | P05 executou no Caderno real nó→registro→tabela→linha/evidência→retorno ao nó original, com fonte/revisão e detalhe exato. Aliases são declarados; ambiguidades exigem escolha. |
| PAR005 produtos/grupos/versões; PAR006 documentos/dossiês | TESTADA | Coleções/metadados nativos consultáveis e vínculos declarados no host; URIs permanecem referências, sem download automático ou disponibilidade inventada. |
| PAR007 grafo de linhagem tipada / T024 | TESTADA | P01 e P05: grafo navegável com tipos, busca integral, endpoints/candidatos e janelas explícitas; resolver tipado/scoped compartilhado com os detalhes, sem causalidade inferida. |
| PAR008 timeline; PAR009 cobertura; PAR010 armazenamento consultivo | TESTADA | P05 conferiu visões e campos reais; datas/ausências, contagens e observações preservadas, sem denominador histórico ou comando de limpeza inventado. |
| PAR011 acesso externo; PAR012 independência/padrões; PAR015 integridade | TESTADA | project() externo, viewer/SDK sem R4 instalado, fontes iguais antes/depois, exports íntegros e negativos HTTP/quotas/alteração de snapshot. |
| Findings4462233813/4462233818/4462287582 | TESTADA | Contraprovas FAIL antes/PASS depois: chave composta sem fallback, namespaces idênticos grafo/detalhe e busca global da árvore sem índice como contexto. P05 e Codex independentes. |
| T025 regressão Ctrl+clique | TESTADA | O timeout repetido do runner foi tratado ativando/focando a origem e registrando cada link; clique real e negativas mantidos. Job Linux foi requalificado nas Actions de 0cd96bc, SUCCESS. |
| PR16 F3A; PR17 F3B | FORA DO ACEITE | Reuso seletivo: componente público P03 já incorporado por blob; F3A descriptor0.2.0 não substitui identidade estrutural da NativeView. Sem merge indiscriminado. |
| PR18/19/20/21/22 C2-D/reader003/C2-B/C2-K/L0 | FORA DO ACEITE | Alternativas separadas, BLOQUEADAS nas próprias frentes. C2-B6a3a32bf tem AppContainer mas CI41374978935 falha checker histórico, finding4438318889 e aquisição zero-byte não qualificada. C2-K508ccb25 é proposta não aprovada, CI41361052428 falha guard e revisão ainda tem finding parent_key. Nenhum path/implementação/documentação C2-K entra na candidata004. |
| PAR013 HL7/FHIR; issue2 BIM/IFC/IDS/SHACL | FORA DO ACEITE | Extensibilidade/futuro, sem alegar conformidade implementada. |
| PR26 / T026–T027 / labels e cancelamento | TESTADA | Grade legível, busca integral e medição limitada sem perda; API idempotente cancela só a notificação pendente. 15 checks do grafo e nove cancelamentos obrigatórios na aplicação; 12 casos reais P05 de foco/timer em 1440/390/320. |
| PR27 / T028 / aplicação global | TESTADA | Foco/seleção, NULL/vazio/ausente/UNKNOWN, populações, falhas HTTP e reindexação explícita; 51 checks exclusivos no pacote instalado, 32 arquivos públicos iguais. |
| Findings4463040279/4463092564/4463092566 e paginação P05 | TESTADA | Acionador recriado/UID, treeitem e setas, fechamento antes dos 600 ms e registro real de índice157 na página correta. Três casos reais de paginação; 15 casos sintéticos adicionais dos quatro tipos, sem atribuir prova real aos demais. |
| T029 / composição única 0cd96bc | TESTADA | CI 14/14, cinco harnesses com 105 checks, 119 testes por modo normal/-O (118 PASS/1 SKIP Windows), Codex sem findings e P05 não autora. Sucessor documental exige atestação/CI/review e recibo Windows próprios. |
| Aceite funcional humano | ABERTA | Conferência e decisão do operador sobre a candidata exata; nenhum agente assina em nome humano. É o gate de promoção funcional após o recibo terminal do sucessor documental. |
| Estabilização ADR0002 e G8/G9 | FORA DO ACEITE | Estabilizar protocolo, merge/release/deploy, migração/retirada mantêm autorizações próprias; esta missão não as concede. |

## Checklist de entrega para aceite

- [x] Código 0cd96bc integrado com autoria preservada; PR Draft #25 e Actions 14/14.
- [x] 105 checks de navegador, regressões/negativos e exports exatos; fontes preservadas.
- [x] Codex e P05 não autora sem findings materiais no código; sucessor exige atestação por bytes, nova CI/review e recibo terminal.
- [x] Comparação funcional, visual e de integridade no Caderno real Windows, incluindo os três findings da composição.
- [ ] Conferência e decisão humana sobre árvore, buscas/seleção, tabelas/exports e demais telas da candidata exata.

O recibo terminal, após qualificar o sucessor documental e o comando Windows,
autoriza o estado de engenharia **ATLAS_READY_FOR_USER_ACCEPTANCE**. A última
caixa continua sendo decisão humana; nenhum agente a assina.

## Limites observados

As contagens de 174 registros, 2911 nós, cinco tabelas/152 linhas e 912 recursos
descrevem a revisão testada; não são tetos. Duas tabelas declaradas estão vazias.
A referência do renderer original é uma composição privada com os mesmos
assets e snapshot verificado, não um build oficial novo. Nenhum conteúdo ou
captura real foi publicado em Git/Actions.

Um preflight de cold-start do harness scratch P05 falhou antes do browser com
BadStatusLine; uma nova execução isolada passou. A causa não foi provada e a
primeira tentativa não é registrada como PASS. O recibo de QA preserva essa
limitação; o comando final recebe smoke independente no PowerShell 5.1.
Merge, release, deploy, migração, limpeza e estabilização ARC-09 mantêm
autorizações próprias e ficam fora deste aceite funcional.
