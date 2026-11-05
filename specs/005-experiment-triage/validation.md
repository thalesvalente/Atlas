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

## Limites e qualificação terminal

O executor CHAT executa Python e Node em Linux. Não executa comandos no host Windows. Windows e otimização são qualificados pelos runners já existentes, com domínio/escopo adicionais da Feature 005. O lançamento local de Chromium está bloqueado pela política AF_UNIX; a superfície CUA também não alcança o servidor isolado. Esses bloqueios não foram convertidos em PASS.

O SHA terminal publicado, suas árvores, runs, artefatos, review e matriz final de resultados serão reconciliados no handoff da PR. Uma árvore idêntica confirma os bytes publicados, mas não transfere automaticamente CI/review de um SHA para outro. O recibo distingue commits de implementação no executor, commits publicados pelo conector, SHA testado e HEAD documental.

O gate futuro LOCAL limita-se a identificar baselines reais, vincular referências físicas, inventariar arquivos/dependências, medir espaço e testar o plano exportado. Nenhuma dessas verificações concede exclusão. `DELETE_AUTHORIZED=NO` permanece obrigatório.
