# PLAN — AP04-F3A-CHAT-GRAPH-01

Plano vinculante AP04-POR-v1.0-draft preservado. Prompt oficial completo no commit 23e776d5b94e1e075275d28e41b5e9214a52cffe, blob edea2253d82943ae1772d9eeae11578b930f4f38. Base congelada 54bb16d350f7bc34fafb95438bd64a2397d58bf3, tree 1372dd532b2323fc1ebaa5c2f00b6d537c636dc9, parent bd2166651f159e70a8165e0f12c8ad2a3270a0d6. Branch única feat/atlas-parity04-f3a-graph-20261031. REASONING_EFFECTIVE=UNVERIFIED.

## Decisão e escopo

A decisão humana https://github.com/thalesvalente/Atlas/pull/15#issuecomment-6539419419 aprova ADR-0003 v0.2 e descriptor 0.2.0 somente no pacote técnico c3ea1e82938fd61cc5a22fee973352715a5bb527, tree 986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c. Os estados anteriores dos controles congelados descrevem outra época e permanecem intactos. A instrução atual autoriza exclusivamente F3A.

Componente SVG genérico isolado: dados in-memory, hierarquia explícita, seleção neutra source/snapshot/occurrence/nav_id/sessão, expandir/recolher, pan/zoom/reset/ajustar/minimapa, teclado e responsividade. Relações tipadas conservam direção e endpoints, colisões/órfãos/stubs/Run isolado/gaps. Texto/URI inertes. API mount/setData/select/dispose sem File API, storage, rede, runtime principal ou roteamento F3B. Dados exclusivamente sintéticos. SDK/protocolo/reader003/Catalog/server/shell não recebem alterações.

## Ownership nativo real

- A /root/logic_a: exclusivamente packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.js e parity04_f3a_graph.css.
- B /root/qa_b: tests/qa/test_atlas_parity04_f3a_graph.py, tests/fixtures/atlas_parity04_f3a_graph.json, scripts/qa/atlas_parity04_f3a_browser.mjs, scripts/qa/atlas_parity04_f3a_ci.py e .github/workflows/atlas-parity04-f3a-graph.yml.
- C /root/review_c: revisão independente, somente leitura, sem autoria dos deltas.
- ORQ /root: exclusivamente recibos em docs/missions/atlas-parity-04/f3a-graph/ e publicação da branch por Git Data API com parent único e lease.

A/B entregam blobs; somente ORQ move a ref. Nenhum checkout, clone, worktree novo ou branch adicional. A instrução oficial foi obtida antes de qualquer escrita. Duas tentativas preliminares de leitura local falharam no launcher MXC ao enumerar D: (os error 1005); nenhum comando do checkout nem leitura de arquivo foi executado e isso não constitui evidência de qualificação.

## EXECUTE e oráculos

1. Ler constituição ARC-01–09, ADR-0001/0002, ADR-0003 v0.2, specs/001, plano/PAR/GATES, F1 sanitizado, F2 contrato/identidade/rastreabilidade e exemplos/N01–N24 em refs imutáveis.
2. Implementar API e CSS encapsulados, modelo sem inferência de identidade/causalidade; validar descriptor fechado e invariantes, quotas e erros visíveis sem truncamento.
3. Testes Python normais/-O e Chromium real Ubuntu/Windows, 1440/390/320 CSS px, teclado/foco, interações, adversariais, expiração/reimportação, schema e limites. Emitir JSON/JUnit/screenshots por SHA/tree, sem skips.
4. Workflow dedicado focal somente, sem alterar gates globais; provar paths/blobs históricos preservados. Recusa histórica de autoria será atribuída separadamente e não é G5 PASS.
5. Publicar commit técnico e PR Draft explicitamente contra docs/atlas-parity04-f2-legacy-contract-20261030. Não editar PR15/F3B.
6. C revisa SHA/tree/código/CI/browser/performance/acessibilidade; corrigir findings nos mesmos owners. Persistir recibos/manifesto e repetir CI/revisão no HEAD que os contém. Fechamento externo na PR evita auto-hash.

## REVIEW e autoridade

C revisou o plano como compatível, sem desvio necessário. Riscos a confrontar: schema fechado/invariantes, resolução única contextual sem first-match, invalidação setData/TTL, ciclos sem recursão infinita, DOM orçamento visível sem truncamento, ausência de setas quando direção UNKNOWN, banner de autoridade/validação/gaps/expiração/autenticidade/ciência.

Resultado somente F3A_GRAPH_COMPONENT_READY_FOR_F4 se gate focal e revisão do HEAD terminal completos; senão F3A_BLOCKED_EXACT. G2 é qualificação sintética isolada; G5 integrado, G6 privado e paridade real não demonstrados. PAR-001/004/007 recebem contribuição sintética isolada, sem fechar a matriz global; PAR-012/015 mantêm seus limites. PAR-005–010 e demais lacunas permanecem. Sem merge/release/deploy/promoção/migração/limpeza/licença/R4/fontes privadas. HL7/FHIR permanece extensão futura por domínio, sem conformidade afirmada.
