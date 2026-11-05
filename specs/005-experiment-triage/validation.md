# Validação e rastreabilidade — Feature 005

Missão `ATLAS-NAV-RETENTION-01`. Toda fixture e todo exemplo publicado são inventados. O aceite A01 continua limitado ao SHA `8e0e400d5220efceb6dd881772e5b07825442970`, tree `5e63684b266bebb983a02cf68c4f17d365d854a2`, PR Draft #32. A Feature 005 exige aceite próprio posterior.

## Matriz spec ↔ implementação ↔ testes

| Requisito | Implementação principal | Evidência executável |
| --- | --- | --- |
| FR-001 / G2 | `native_notebook.html`, `native_triage_ui.js:initSidebar`, CSS de integração | Browser G2 e G11 nas cinco larguras; regressão A01/LQA |
| FR-002 / G3 | `native_triage_model.js:search/diagnose`, `native_triage_ui.js:resultCard`, controller `locateEntry` | Domínio M1/M11/M1.1, motivos/lexemas; browser T01/T03 e diagnóstico |
| FR-003 / G4 | Facetas tipadas e `recordExecutionState`; controller `matches` | Domínio execução/NULL/ausente/data; browser T02/G4; regressão UI de tipo e data em linhas |
| FR-004 / G5 | `baselineDesignation`, anotações vinculadas à revisão, vista Baselines | Domínio fonte/nome/referência/conflito; browser G5; regressão UI após anotar/remover |
| FR-005 / G6 | `SelectionLedger`, checkboxes e `selectionChanged`, contagens | Domínio identidade/revisão/drift; browser T04/revisão/1200+; regressão UI após desmarcar |
| FR-006 / G7 | Barra de lote, `renderSelected`, comparação e referências | Browser T05/G11; regressão UI de foco e seleção |
| FR-007 / G8 | `native_retention.js`, `renderPlan`, dossiê/exportação | Domínio plano/dossiê/linhas integrais; browser T06/dossiê; regressão exportação atual |
| FR-008 / G9 | Intenções enumeradas, proteção fail-closed, lacunas e medições pendentes | Domínio baseline/falha/backup/forja; browser T07/T08; exemplo JSON sintético |
| FR-009 / G11 | HTML nativo, modal temporário, chips, paginação e foco | Browser 1440×1200, 1024×900, 800×1000, 390×844, 320×740; checklist de acessibilidade |
| FR-010 / G13 | Sem mutação de DTO/protocolo; três assets estáticos fixos; exportação inerte | Guard de escopo + negativos; testes Native/A01; browser T09/T10/hostil e hashes antes/depois |
| FR-011 / G14–15 | Feature própria, workflow próprio, PR Draft empilhada, revisão não autora | Actions no SHA publicado, recibo Codex Review e handoff final na PR |

## Execução reproduzível

```bash
node --test --test-reporter=tap scripts/qa/test_native_triage.mjs
node --test --test-reporter=tap scripts/qa/test_native_triage_ui.mjs
node --test --test-reporter=tap scripts/qa/test_native_legacy.mjs
node --test --test-reporter=tap scripts/qa/test_native_navigation.mjs
python -m unittest discover -s tests/viewer -p 'test_native_notebook*.py' -v
python tests/qa/test_native_triage_scope.py -v
python scripts/qa/speckit_audit.py --allow-presentation-delta
python scripts/qa/run_native_triage_browser.py --work .ci-native-triage
```

O runner browser exige o pacote Atlas instalado fora do checkout, compara os hashes de todos os assets instalados com o candidato, usa dois snapshots sintéticos, registra SHA/tree e hashes das fontes, e recusa ambiente com R4 instalado. O mesmo oráculo pode mirar uma baseline imutável por `--repo`; falha ao iniciar Chromium é `BLOCKED`, jamais RED funcional.

## RED e revisão não autora

O RED inicial demonstrou execução `FAILED` exibida pela A01 enquanto o filtro documental priorizava `result_group=published`. A Feature 005 mantém esse grupo como dimensão documental e adiciona execução coerente com o indicador. Ausências de módulo/controles também foram registradas como ausências reais, separadas do bloqueio de browser do executor.

A revisão não autora de domínio executou 42 testes após a correção de UX-DOM-01, além de 13 contraprovas de identidade, lexemas, revisão, referências e exportação. A explicação de uma designação conflitante agora prioriza o conflito; a nota do operador permanece separada.

A revisão da composição identificou quatro casos reproduzíveis: dossiê/controles de retenção desatualizados após desmarcar; tipo/data da linha substituídos indevidamente pelo contexto da tabela; resultados não reconciliados após anotação de baseline; contagens zeradas nos novos destinos. As correções têm regressões de métodos reais com DOM em memória. Esse teste não é evidência visual e não substitui Chromium.

## Histórico de qualificação pública

Falhas permanecem registradas; nenhuma execução antiga foi substituída por uma aprovação posterior.

| Candidato publicado | Resultado observado | Diagnóstico e correção |
| --- | --- | --- |
| `8748d580887e8e5ff453fc92bd0f7a243ba2ad85` | 11 checks PASS / 6 FAIL; triagem nova 20 grupos PASS | Guard precisava reconstruir os bytes históricos sem depender de objetos ausentes no checkout raso; área inicial e busca da árvore estavam obscurecidas. [Triagem](https://github.com/thalesvalente/Atlas/actions/runs/42107102447), [aplicação](https://github.com/thalesvalente/Atlas/actions/runs/42107101890), [native](https://github.com/thalesvalente/Atlas/actions/runs/42107102143). |
| `7800a48277f43ad2ecc24fc109ee44633713259a` | 14 checks PASS / 3 FAIL | A contagem esperada da busca usava somente 1216 IDs indexados, embora o snapshot contenha 1260 DTOs; duas exportações estavam cobertas pelo painel. O oráculo foi corrigido e a área dos controles foi reservada. [Triagem](https://github.com/thalesvalente/Atlas/actions/runs/42107927013), [aplicação](https://github.com/thalesvalente/Atlas/actions/runs/42107926919), [native](https://github.com/thalesvalente/Atlas/actions/runs/42107926873). |
| `2aaabcef01b12665b3f95e4b72ac822996b61556` | 15 checks PASS / 2 FAIL; triagem 22 grupos PASS e aplicação principal PASS_SCOPED | As exportações ficaram acessíveis. LQA-02 encontrou redução indevida de um caractere no estado do cartão; o harness Native encontrou leitura prematura da navegação durante resize mobile. Comprimentos A01 restaurados e helper passou a esperar o rótulo correspondente à media query. [Triagem](https://github.com/thalesvalente/Atlas/actions/runs/42109963590), [aplicação](https://github.com/thalesvalente/Atlas/actions/runs/42109963476), [native](https://github.com/thalesvalente/Atlas/actions/runs/42109963412). |

A auditoria não autora adicional encontrou contraste insuficiente em textos secundários e no foco do cabeçalho, além de uma contraprova geométrica em 1101 px com lateral e detalhes abertos. A correção local `160188c2005334d002a06dc1a0c3fa48afe20bd9` restaurou os rótulos, escureceu o texto secundário, distinguiu o foco sobre fundo escuro e tornou os tracks da busca flexíveis. A requalificação estática mediu no mínimo 4,9702:1 no subtítulo e 4,7631:1 no foco do cabeçalho. O agente não autor `final_regression_audit` confirmou esses valores no relatório real e inspecionou as sete imagens de tarefa/controles no candidato qualificado abaixo: UX-A11Y-01/02/03 `CLOSED_SCOPED`, zero findings materiais abertos nesse escopo.

Os dois harnesses de exportação mantiveram todos os asserts (57 Native e 136 Application). A espera conjunta pelo download e pelo clique elimina promises rejeitadas sem observador; falhas continuam reprovando o job e agora preservam screenshot e geometria do alvo. Não foram acrescentados cliques forçados ou retries para mascarar oclusão.

## Candidato de produto qualificado

SHA `3a9e1e3d2727c69175768abb437bdcbc47cfabf0`, tree `23b1c290aedf511c0903eaf9dd016296ec7ebe8b`: **17/17 checks PASS**. Os bytes do produto foram instalados fora do checkout e comparados com o candidato. O [pacote de evidências versionadas](evidence/README.md) conserva os relatórios originais, sete PNGs de tarefa/controles, hashes das fontes e o mapa de commits de implementação/publicação.

| Qualificação | Resultado | Run |
| --- | --- | --- |
| Triagem/retenção, domínio e UI em Windows/Ubuntu | 3 jobs PASS; domínio 42/42, UI 9/9, A01 36/36, escopo 2/2 | [42111583734](https://github.com/thalesvalente/Atlas/actions/runs/42111583734) |
| Browser da triagem | 23 grupos PASS; T01–T10; cinco viewports solicitados e 1101×900 adicional | mesmo run acima |
| Aplicação e A01/LQA | 63 checks principais + 12 grupos A01 PASS; nove casos de cancelamento gráfico | [42111583741](https://github.com/thalesvalente/Atlas/actions/runs/42111583741) |
| Native/P02/P01/grafo | 14 + 17 + 8 + 15 checks browser PASS; quatro jobs Windows/Ubuntu normal/-O PASS | [42111583767](https://github.com/thalesvalente/Atlas/actions/runs/42111583767) |
| Qualificação geral ATLAS021 | quatro jobs Windows/Ubuntu normal/-O, padrões públicos e viewer instalado PASS | [42111583839](https://github.com/thalesvalente/Atlas/actions/runs/42111583839) |
| Spec Kit/contratos | Windows e Ubuntu PASS | [42111583730](https://github.com/thalesvalente/Atlas/actions/runs/42111583730) |

No Chromium `151.0.7922.34`, filtrar os 1200 registros de volume levou 90 ms e selecionar os 1213 registros levou 36 ms no runner, abaixo do gate de 2 s. Isso caracteriza a fixture e esse ambiente; não é promessa de desempenho sobre corpus privado. A fonte tem 1260 DTOs no total, com a tabela RF de 39 linhas preservada integralmente.

As seis resoluções passaram em foco, toque onde aplicável, minimapa e cartão visível com 25/25 pontos de hit-test. Em 1101 px, quatro controles mantiveram 9/9 pontos sem interseção com detalhes. O navegador confirmou os contrastes calculados pela auditoria. Planejamento fez zero requisições HTTP, não instalou/importou R4 e manteve os hashes das quatro fontes. Nenhuma falha JavaScript ou requisição externa foi observada.

Recibo independente: `INDEPENDENT_AGENT_REVIEW_SCOPED=PASS`, revisão exclusivamente em leitura. CSS auditado `e43965b793b9cbd108bbaa5f424d74c1650a0a78`; harness dessa rodada `d36222e35621f5614456b94447907c16792d416f`; SHA-256 do relatório `6028395b47a3e149bd639ba6358d500ac7db2034f656a2d41525968625b7c4f7`. O fechamento adiciona uma contraprova de Shift+Tab no drawer; não altera bytes do produto. Essa prova é executada junto aos demais gates no SHA terminal, sem atribuir sua execução ao relatório anterior.

## Limites e qualificação terminal

O executor CHAT executa Python e Node em Linux. Não executa comandos no host Windows. Windows e otimização são qualificados pelos runners já existentes, com domínio/escopo adicionais da Feature 005. O lançamento local de Chromium está bloqueado pela política AF_UNIX; a superfície CUA também não alcança o servidor isolado. Esses bloqueios não foram convertidos em PASS.

Este fechamento documental preserva evidências do candidato de produto acima. O SHA que inclui a documentação, suas árvores, novos runs e Codex Review são reconciliados no recibo terminal `ATLAS_EXPERIMENT_TRIAGE_HANDOFF` da [PR #33](https://github.com/thalesvalente/Atlas/pull/33). Uma árvore idêntica confirma os bytes publicados, mas não transfere automaticamente CI/review de um SHA para outro. O recibo distingue commits de implementação no executor, commits publicados pelo conector, SHA testado e HEAD documental; a verificação externa permite manter imutável o commit qualificado.

O gate futuro LOCAL limita-se a identificar baselines reais, vincular referências físicas, inventariar arquivos/dependências, medir espaço e testar o plano exportado. Nenhuma dessas verificações concede exclusão. `DELETE_AUTHORIZED=NO` permanece obrigatório.
