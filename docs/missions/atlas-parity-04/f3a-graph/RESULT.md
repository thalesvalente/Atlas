# Resultado — AP04-F3A-CHAT-GRAPH-01

Plano AP04-POR-v1.0-draft preservado; prompt oficial 23e776d5b94e1e075275d28e41b5e9214a52cffe. REASONING_EFFECTIVE=UNVERIFIED. Autorização arquitetural limitada ao pacote ADR-0003 v0.2/descriptor 0.2.0 c3ea1e82938fd61cc5a22fee973352715a5bb527, comentário 6539419419 da PR 15; autorização atual exclusivamente F3A.

**F3A_GRAPH_COMPONENT_READY_FOR_F4**, exclusivamente para o componente sintético isolado no SHA 7008fa5a98b7036b7f97161ee808a422b2ce9ae1, tree 3d8a6c00259655ecc65376cf2ccfc03554d68476. A prontidão do commit que contém estes recibos exige seus próprios runs e revisão; fechamento externo verificável na [PR Draft 16](https://github.com/thalesvalente/Atlas/pull/16).

## Entrega e validação

ES module e CSS isolados, API mount/setData/select/getState/dispose, descriptor 0.2.0 fechado, hierarquia explícita sem níveis inventados, seleção source/snapshot/occurrence/nav_id com nonce de sessão, expansão/recolhimento, pan/zoom/reset/ajustar/minimapa, teclado/foco, relações tipadas com direção literal. Nenhum módulo F3B nem shell principal é importado. A fixture original sintética contém 109 nós/210 relações, 50 grupos de IDs colidentes, 22 endpoints null, 75 não resolvidos, 40 grupos repetidos/41 excedentes e Run fonte isolado+stub separado com binding_gap.

Run focal [41173213797](https://github.com/thalesvalente/Atlas/actions/runs/41173213797) completed/success, quatro células Windows/Ubuntu × Python normal/-O. Em cada célula: 22 testes e 17 jornadas Chromium 151.0.7922.34, zero falhas/errors/skips, zero requests externos/page errors/storage. A árvore de 1.000 nós levou 633–1.391ms, e 4.000 relações 380–765ms. Capturas a 1440/390/320 CSS px e JSON/JUnit foram publicados por célula.

Os recibos de browser, testes, custódia e screenshots/JSON/JUnit são atribuídos ao SHA/tree realmente executado. Os JSON em Git são extraídos do stdout dos próprios runners, retirando timestamps e linhas unittest concorrentes identificáveis; não alteram os artefatos originais. ZIP/PNG/XML binários não foram abertos nem pixels inspecionados manualmente. Código do serializer, logs, oráculos DOM/gestos/teclado, metadata/hash/tamanho e publicações dos artefatos foram confrontados. Não se afirma zoom nativo 200%, leitor de tela integral, certificação WCAG ou hard heap 256MiB no browser.

## PLAN → EXECUTE → REVIEW

PLAN a49d2cc foi publicado antes do código. A /root/logic_a escreveu exclusivamente JS/CSS; B /root/qa_b escreveu os cinco paths testes/fixture/harness/workflow; ORQ publicou os recibos/commits por Git Data API com pai único/lease; C /root/review_c foi revisor nativo real independente, somente leitura. Sem agentes simulados ou clones/worktrees/branches adicionais. O checkout do operador permaneceu sem escrita; duas leituras preliminares falharam no launcher antes de executar código/comando no checkout.

A revisão encontrou e fechou C-001 fit integral, C-002 calendário real, C-003 JSON interno/unmapped cells, C-004 foco legível após fit e C-005 invalidação após reload. Fonte e contraprovas foram corrigidas nos owners exclusivos. Datas inexistentes/24h, referências ambíguas/cross-context/stubs, nav promovido, versão extra/unknown, validação NOT_RUN, TTL/profundidade/nonfinite e células incoerentes são recusados com erro visível e estado vazio. 1.000 nós e 4.000 relações são ensaiados positivamente; excessos até 10.001/100.001 são recusados integralmente.

Os candidatos não qualificados permanecem auditáveis: f51bc5318b700f2bd8d24080ea7519cd1c29c5de teve workflow focal inválido sem jobs (run41172937230; causa inferida da posição de runner.temp em jobs.env, corrigida no step env); e56b2f3a406be52ab8edc33270834c1cf54c9d75 executou browser real com 13/17 jornadas PASS e 4 erros no harness textContent(), gerando 5 failures nos 22 testes (inclui sumário), sem skips. As quatro chamadas foram corrigidas sem afrouxar os oráculos. CI-EVIDENCE preserva esses ciclos e as execuções posteriores.

C emitiu PASS independente sobre o SHA técnico e os quatro logs próprios, sem finding bloqueante aberto. INDEPENDENT-REVIEW.md registra escopo, correções e limitações. O SHA posterior que contém estes recibos requer fechamento próprio por CI/revisão; não herda este PASS automaticamente.

## PAR antes/depois e gates

As colunas globais abaixo conservam os estados literais AP04, sem revalidar ou substituir a baseline. A contribuição nova é sintética e isolada; nenhuma linha recebe RECOVERED_VERIFIED ou paridade completa.

| PAR | Antes literal | Depois global preservado | Contribuição F3A / lacuna |
|---|---|---|---|
| PAR-001 | NOT_RECOVERED | NOT_RECOVERED | F3A synthetic isolated SVG tree; real tree and F4 pending |
| PAR-002 | NOT_RECOVERED | NOT_RECOVERED | Outside F3A; no recovery or revalidation claimed |
| PAR-003 | INPUT_AVAILABILITY_UNKNOWN | INPUT_AVAILABILITY_UNKNOWN | Outside F3A; no recovery or revalidation claimed |
| PAR-004 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | Session/source/snapshot/occurrence selection in component; integrated table journey pending |
| PAR-005 | NOT_RECOVERED | NOT_RECOVERED | Outside F3A; no recovery or revalidation claimed |
| PAR-006 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | Outside F3A; no recovery or revalidation claimed |
| PAR-007 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | Typed relation occurrences/null/unresolved/collision/repeats retained synthetically; real graph pending |
| PAR-008 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | Outside F3A; no recovery or revalidation claimed |
| PAR-009 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | Outside F3A; no recovery or revalidation claimed |
| PAR-010 | NOT_RECOVERED | NOT_RECOVERED | Outside F3A; no recovery or revalidation claimed |
| PAR-011 | CONTRACT_DECISION_PENDING | CONTRACT_DECISION_PENDING | Outside F3A; no recovery or revalidation claimed |
| PAR-012 | BASELINE_VERIFIED | BASELINE_VERIFIED | Frozen base blobs preserved; focal CI only, global integrated G5 not qualified |
| PAR-013 | ARCHITECTURE_REQUIREMENT_ONLY | ARCHITECTURE_REQUIREMENT_ONLY | Outside F3A; no recovery or revalidation claimed |
| PAR-014 | OBSERVED_PARTIAL | OBSERVED_PARTIAL | Outside F3A; no recovery or revalidation claimed |
| PAR-015 | BASELINE_VERIFIED_SCOPE | BASELINE_VERIFIED_SCOPE | Synthetic inert values/context invalidation tested; no new private-source integrity observation |

G2 recebe somente prova funcional sintética do componente isolado. G4 importação/abertura e G5 integrado não qualificados; G6 privado não executado; G7 paridade não qualificada; G8/G9 sem autorização. G1/F1 é referência histórica, não nova leitura nesta missão. A decisão humana posterior da ADR é registrada sem reescrever os estados históricos PROPOSED/PENDING.

Os gates globais falham por razões distintas: delta F2 congelado, inventário de fixtures C4 e descoberta de novos testes sem Playwright no workflow antigo. GLOBAL-GATE-REPAIR-CONTRACT.md registra runs/jobs/causas e o ato mínimo do integrador. Nenhum gate foi desligado, contornado ou convertido em PASS; o alvo desta missão é estritamente prontidão do componente isolado.

## Limites e confronto de decisões

O render admite 1.000 nós/4.000 relações com deadline de 30s e erro inteiro sem truncamento. O payload F1 sanitizado informa 2.911 nós, portanto excederia o componente atual e não foi executado. F4 deverá resolver essa capacidade antes de demonstração real. O objeto de entrada já está emRAM; orçamento de abertura/parse/heap 256MiB da F2 pertence ao fluxo externo futuro, não está certificado por F3A. Contrato completo em GRAPH-CONTRACT.md.

D-001–006: UI/protocolo/fontes separados, derivado não científico, manutenção externa e aprovação arquitetural por versão/SHA preservados. D-007–011: direção RO-Crate 1.3/Process Run 0.6/Caderno 0.1.0a1, baseline C4, retenção e roadmap BIM/IFC/IDS/SHACL preservados. D-012–020: campanha continua sem reiniciar/migrar, árvore útil sintética e demais funções permanecem pendentes, leitura externa futura sem fonte reescrita, HL7/FHIR futuro por domínio sem conformidade, R4/F6 não iniciado, branch única/sem clones, PAR/gates confrontados, históricos preservados.

A validação local do descriptor comprova forma e invariantes de fronteira/células/referências, não prova origem, literalidade da fonte, autenticidade ou ciência; flagsPASS recebidas não promovem esses eixos. Não houve File API, roteamento árvore→tabela, adaptação privada, alteração no protocolo/reader003/Catalog/server/shell, R4, dados privados, chamada paga, merge/release/deploy/promoção/migração/limpeza ou licença. A PR 16 permanece Draft contra a branch F2 explícita; PR 15/F3B não foram editadas.
