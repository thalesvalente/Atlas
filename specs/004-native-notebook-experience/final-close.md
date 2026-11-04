# ATLAS-FINAL-CLOSE — contrato e matriz única

Data local: 2026-11-03. **Código funcional qualificado; aceite humano pendente.**
Base: PR23 `a1b45d2f361c1900c7c8569b32def2601a3d4464` seguida de PR24
`7c72d9c863871f3541eadb6aac85cab864ad559f`. Integração exclusiva em
`integrate/atlas-final-close-20261103`; o SHA final e seus recibos terminais
são publicados na [PR Draft #25](https://github.com/thalesvalente/Atlas/pull/25),
evitando assinatura circular no commit. O código efad09d recebeu CI 13/13,
Codex e P05 sem findings materiais. Este encerramento somente documental exige
atestação dos bytes executáveis e CI/Codex próprios no HEAD resultante; o recibo
terminal informa o estado vigente e não herda qualificação por suposição.

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
| T015 / R006 / review de R014 | TESTADA | Codex completed/zero findings em efad09d; P05 não autora requalificou três findings. Novo HEAD requer novo recibo, não aprovação herdada. |
| T016 / R010 / R012 / host de R014 / PAR014 | TESTADA | Windows real: comando e comparação funcional/visual/integridade; 174 registros/2911 nós/5 tabelas152 linhas/912 recursos nesta revisão, não tetos. Referência original composta privadamente sobre o mesmo snapshot, não build oficial novo. |
| PAR002/PAR003 tabelas originais | TESTADA | Cinco tabelas, primeiras/últimas linhas, JSON de ocorrência e linhas SHA-exatos, CSV protegido; duas tabelas declaradas vazias mantidas vazias. |
| PAR004 navegação contextual / T023 | TESTADA | P05 executou no Caderno real nó→registro→tabela→linha/evidência→retorno ao nó original, com fonte/revisão e detalhe exato. Aliases são declarados; ambiguidades exigem escolha. |
| PAR005 produtos/grupos/versões; PAR006 documentos/dossiês | TESTADA | Coleções/metadados nativos consultáveis e vínculos declarados no host; URIs permanecem referências, sem download automático ou disponibilidade inventada. |
| PAR007 grafo de linhagem tipada / T024 | TESTADA | P01 e P05: grafo navegável com tipos, busca integral, endpoints/candidatos e janelas explícitas; resolver tipado/scoped compartilhado com os detalhes, sem causalidade inferida. |
| PAR008 timeline; PAR009 cobertura; PAR010 armazenamento consultivo | TESTADA | P05 conferiu visões e campos reais; datas/ausências, contagens e observações preservadas, sem denominador histórico ou comando de limpeza inventado. |
| PAR011 acesso externo; PAR012 independência/padrões; PAR015 integridade | TESTADA | project() externo, viewer/SDK sem R4 instalado, fontes iguais antes/depois, exports íntegros e negativos HTTP/quotas/alteração de snapshot. |
| Findings4462233813/4462233818/4462287582 | TESTADA | Contraprovas FAIL antes/PASS depois: chave composta sem fallback, namespaces idênticos grafo/detalhe e busca global da árvore sem índice como contexto. P05 e Codex independentes. |
| T025 regressão Ctrl+clique | TESTADA | O timeout repetido do runner foi tratado ativando/focando a origem e registrando cada link; clique real e negativas mantidos. Job Linux em efad09d terminou SUCCESS. |
| PR16 F3A; PR17 F3B | FORA DO ACEITE | Reuso seletivo: componente público P03 já incorporado por blob; F3A descriptor0.2.0 não substitui identidade estrutural da NativeView. Sem merge indiscriminado. |
| PR18/19/20/21/22 C2-D/reader003/C2-B/C2-K/L0 | FORA DO ACEITE | Alternativas separadas, BLOQUEADAS nas próprias frentes. C2-B6a3a32bf tem AppContainer mas CI41374978935 falha checker histórico, finding4438318889 e aquisição zero-byte não qualificada. C2-K508ccb25 é proposta não aprovada, CI41361052428 falha guard e revisão ainda tem finding parent_key. Nenhum path/implementação/documentação C2-K entra na candidata004. |
| PAR013 HL7/FHIR; issue2 BIM/IFC/IDS/SHACL | FORA DO ACEITE | Extensibilidade/futuro, sem alegar conformidade implementada. |
| Aceite funcional humano | ABERTA | Conferência e decisão do operador sobre a candidata exata; nenhum agente assina em nome humano. É o próximo gate de promoção. |
| Estabilização ADR0002 e G8/G9 | FORA DO ACEITE | Estabilizar protocolo, merge/release/deploy, migração/retirada mantêm autorizações próprias; esta missão não as concede. |

## Checklist de entrega para aceite

- [x] Código integrado efad09d, PR Draft #25 e Actions 13/13; sucessor documental exige recibo terminal próprio.
- [x] Regressões/negativos/Chromium sem erros materiais; fontes preservadas.
- [x] Codex e QA P05 não autora qualificaram o código; atestação do sucessor por bytes, com nova CI/review.
- [x] Comparação funcional, visual e de integridade no Caderno real Windows.
- [ ] Conferência humana da árvore, busca, seleção, tabelas/exports e demais telas.

Os quatro primeiros qualificam engenharia para **ATLAS_READY_FOR_USER_ACCEPTANCE**.
O último é decisão humana posterior; não é fabricado pelo coordenador.
