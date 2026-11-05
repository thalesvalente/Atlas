# Plano — Feature 005

## Technical Context
JavaScript ES modules/DOM/SVG, Python stdlib e servidor de loopback existentes. Nenhuma nova dependência de runtime. Chromium/Playwright disponíveis ou runners existentes; registrar bloqueios do executor distintamente de falha de produto. Ambiente CHAT Linux, nenhum comando no host Windows. Windows é qualificado apenas pelos runners autorizados.

## Constitution Check
ARC-01–09 preservadas: visualização e índices derivados, produtor separado, DTO/protocolo inalterados, nenhuma aprovação científica ou limpeza. P03, C2-B/C2-K/C4-K/ARC-09 fora do ownership. Manifesto histórico A01 não é repinado. Novos módulos são servidos por entradas estáticas fixas; nenhum endpoint novo recebe paths. A sucessão exata do pin de `server.py`, se necessária para essas rotas, conserva a baseline e adiciona contraprovas de mutação; não libera runtime arbitrário.

## PLAN / DAG / Ownership
O0 reconciliação+spec → O1 (modelo/retenção || integração UI || testes browser; pesquisa oficial em paralelo) → O2 composição por root → O3 regressões/browser+revisão não autora+Actions no SHA final → O4 handoff e aceite posterior.

| Owner nativo | Branch/worktree | Escrita exclusiva |
| --- | --- | --- |
| root | feat/atlas-experiment-triage-20261105 / atlas | Feature005, HTML/CSS/controller, extensão aditiva da árvore, rotas estáticas e gate exato, CI e integração |
| triage_domain | work/atlas-triage-domain-20261105 / wt-domain | native_triage_model.js, native_retention.js, test_native_triage.mjs |
| triage_browser_tests | test/atlas-triage-browser-20261105 / wt-browser-triage | fixture/harness novos; adaptação de navegação dos harness browser existentes sem retirar asserts |
| ux_research_review | sessão não autora, leitura | fontes oficiais e revisão adversarial da composição |

Todos partem do SHA aceito 8e0e400d5220efceb6dd881772e5b07825442970. Integrar commits com cherry-pick -x; sem mexer branches anteriores, limpar worktrees ou force-push. Identidade técnica Git Codex não é assinatura humana independente.

## Research / decisões
Navegação sem role=menu, duas camadas; desktop 260 px em coluna reservada, recolhida liberando espaço; mobile painel modal temporário com foco confinado/retornado. Filtros contextuais recolhíveis, chips sempre visíveis. Barra de lote em fluxo sticky com rolagem e sem cobrir detalhes/minimapa. Reconhecimento, visibilidade de estado e prevenção de erros orientam apresentação tipada e intenções explícitas.

Fontes oficiais: [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/), [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [APG disclosure navigation](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/), [APG dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/), [Carbon left panel](https://www.carbondesignsystem.com/building-blocks/core/components/ui-shell-left-panel/guidelines), [Carbon filtering](https://www.carbondesignsystem.com/building-blocks/core/patterns/filtering), [Carbon data table](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines). Critérios normativos e escolhas do Atlas separados no checklist; nenhuma alegação de certificação WCAG.

## Modelo e contratos de interação
`createTriageModel(source,presentation)` indexa DTOs e fornece tipos, facets tipadas, search com motivos, baseline e diagnósticos. `recordExecutionState/Presentation` são autoridade de apresentação da execução. `SelectionLedger` guarda lote/anotações/intenções por fonte+revisão+digest+UID+tipo; bind de novo snapshot invalida. `buildRetentionPlan` e `buildDossier` geram objetos inertes, com JSON original lexical para verificação, status PROPOSAL_ONLY, DELETE_AUTHORIZED=NO e verificações pendentes. A vista não dereferencia filesystem ou URLs.

A busca global tem destino próprio na navegação; o campo de busca também conserva filtros das vistas já existentes. Localizar na árvore funciona diretamente em registros; demais tipos oferecem referência declarada única ou explicam vínculo não comprovado. Cliques de foco abrem detalhe, checkbox só altera lote. Visíveis = janela renderizada e cartões dentro da câmera, nunca filhos recolhidos; filtrados = população integral da área ativa. Comparação/dossiê/plano mostram somente lote explícito; filtro não o redefine.

## Spec Kit e testes
Skills specify/plan versionadas e scripts oficiais 1.2.3 usados; `specify` CLI ausente neste executor: NOT_RUN, sem instalação. Feature explícita `specs/005-experiment-triage`, `SPECIFY_FEATURE_NO_PERSIST=1`. Template oficial resolvido; setup_plan/setup_tasks/check_prerequisites reais. Constituição e seletor global intactos. Pesquisa/modelo/contratos reunidos neste plano para evitar duplicação.

RED de divergência/ausências antes de implementar → testes puros → browser tarefa+adversariais → suíte de aplicação e native existente → normal/-O Windows/Ubuntu Actions. QA não autora inspeciona código e evidências, sem autodeclarar revisão humana. READBACK em evidência de missão; fechamento em handoff vinculado ao SHA terminal.

## Quickstart e rollback
Abrir o Atlas pelo launcher existente com pacote público válido, ir a Busca global, filtrar execução, marcar lote, comparar e preparar plano. Dados reais só por binding LOCAL posterior. Testes reproduzíveis constarão do handoff após execução. Rollback é retornar ao SHA aceito da aplicação; nenhuma alteração de fonte exige reversão.
