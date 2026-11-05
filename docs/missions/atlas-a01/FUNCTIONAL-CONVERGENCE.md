# ATLAS_A01_FUNCTIONAL_CONVERGENCE_HANDOFF — implementação

Este recibo registra o incremento ATLAS-A01-FIX antes da qualificação remota. O parecer terminal deve citar o SHA exato e os runs/reviews na PR #32; este arquivo não promove um gate pendente.

## Fonte e escopo

Repositório `thalesvalente/Atlas`, branch autorizada `fix/atlas-a01-visual-parity-20261104`, PR Draft #32. Fonte inicial `f6bed418a611c5254d3cd6c8fa814e71c8591c48`, tree `f27e41590dc2bf83c0abfb60769f0b52b960fbaf`, parent `ee86e8d6f0589712dded681d5f0daf0ac61760e1`. Base #25 `32a0b1aeb33406cf6fbbc6b16946bd203073ced5` preservada. Publicação fast-forward com lease; não houve lock distribuído, somente revalidação e reserva pública de ownership.

Fonte CHAT autenticada por arquivo e conferência Git blob; não é checkout integral. Clone falhou por DNS, download de arquivo completo não disponível pelo conector. Nenhum host privado, corpus, instalação, nova credencial, merge, release, deploy ou migração. `NATIVE_SUBAGENTS_NOT_AVAILABLE`; implementação e revisão autoral sequenciais não são auditoria independente.

## Correções e rastreabilidade

| Finding | Implementação | Contraprova / limite |
|---|---|---|
| F-01 | `recordExecutionState`: own-key `execution_state → status → result_state → result_group`; `result` apenas fallback legado. Tabela e detalhe usam a mesma seleção. | AUSENTE, NULL, vazio, false, zero e precedência contraditória; sem fabricar estado científico. |
| F-02 | Busca sobre o payload completo com decodificador lexical existente; cache fraco por ocorrência/revisão. | Objetos, arrays arbitrários, escapes, inteiros grandes, decimais, expoentes, zero negativo e conteúdo hostil inerte. |
| F-03 | Projeto=`project`, execução=`run_id`, estágio=`stage`, admissão=`admission` da tabela; núcleo=`nucleus_id` da linha. | Sem aliases inferidos. Opções somente da população carregada, chaves tipadas, combinação AND, limpeza, paginação e retorno contextual. |
| F-04 | Compactação escopada de catálogos/registros; larguras proporcionais, metadados compactos, texto integral, região rolável acessível. | Chromium sintético desktop/mobile; comparação final OLD/NEW com corpus privado permanece LOCAL/PENDING. |

Semântica F-03 baseada em `src/r4/presentation/atlas_assets/tables-coverage.js` de R4 `2895d95f81a0436636227d02b504ed1dad3f2e36`. As opções não transplantam sua perda histórica de valores falsy. Null/ausência/vazio e tipos distintos não são fundidos.

Fluxo: contrato/fonte → RED → núcleo e regressões → integração dos filtros/densidade → revisão autoral → CI e Codex por SHA → inspeção visual humana. Um único writer. Descriptor 0.2.0, produtor, Caderno, contratos C2/ARC-09, P03 e manifestos históricos não foram editados.

## Execução e evidência

Ambiente CHAT: Node 22.16.0 e Python 3.13.5. `node --test scripts/qa/test_native_a01_fix.mjs`: RED inicial 23 FAIL esperados + 6 controles PASS; GREEN dos mesmos 29 casos: 29 PASS. Sete casos de filtros adicionais produziram RED 7 FAIL / 29 PASS, depois GREEN 36/36 sem SKIP. `python -m unittest discover -s tests/viewer -p test_native_notebook_a01_fix.py -v` executou a suíte JavaScript via descoberta existente. Sintaxe JS/Python verificada. Detalhes e hashes dos logs estão em `FUNCTIONAL-EVIDENCE.json`.

Browser HTTP local: `BLOCKED`, `net::ERR_BLOCKED_BY_ADMINISTRATOR` antes dos testes. Ensaio offline por DOM injection de módulos de apresentação, DTO sintético e CSS-base auxiliar: 10 checks PASS, zero erros/requests externos, exportações JSON/CSV conferidas. **Esse ensaio não é aplicação instalada, não valida o servidor/DTO e não atesta os stylesheets completos.** As medidas desse ensaio não são prova de paridade visual real.

A nova suíte instalada usa o exportador real, viewer instalado, fonte sintética e hashes antes/depois, com 205 linhas, referências, filtros tipados, retorno contextual, exports e viewports 1440/390/320. É chamada de forma aditiva pelo runner existente depois dos checks originais. Nenhum workflow/pin foi alterado nem teste anterior removido. Os 36 testes são também descobertos por `scripts/run_checks.py` em `tests/viewer`.

Spec Kit: AGENTS, constituição, spec/plan/tasks/contrato 004 e skill versionada de implementação foram lidos; foi usada análise equivalente para o bug localizado, preservando baselines. CLI `specify` não instalada: `NOT_RUN`, sem instalação. Checks Spec Kit remotos devem qualificar o SHA sucessor, não reutilizar verde antigo.

## Gates e próximo aceite

G1/G2: evidência RED/GREEN local; G3/G4/G6: testes sintéticos implementados, qualificação instalada PENDING_CI neste recibo; G5: diff restrito à apresentação/testes próprios, sem novas entradas HTTP ou execução de conteúdo; G7/G9: PENDING por SHA final; G8: solicitar `@codex review` no SHA final e tratar findings; G10: handoff LOCAL abaixo. Não declarar sucesso final antes dos gates terminais.

A próxima inspeção LOCAL deve reaproveitar capturas existentes e revalidar somente F05 (filtros), F07 (catálogos), F10 (registros/estados) e buscas afetadas. Comparar densidade, títulos/IDs, NULL/ausentes/vazio, navegação, teclado e leitura em larguras reais. Não publicar dados privados. `HUMAN_ACCEPTANCE=PENDING` e `INDEPENDENT_REVIEW_NOT_PROVEN` para auditoria humana; Codex é um gate separado, não aceite humano.
