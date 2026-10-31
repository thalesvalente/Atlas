# PLAN — AP04-F4-C1-GRAPH-SCALE-CHAT-01

Plano AP04-POR-v1.0-draft preservado; execução autorizada pelo prompt do operador em 2026-10-31. Prompt imutável: c4f1204d75222c1a72678d22f1a4b23f1a33ab8f, docs/missions/atlas-parity-04/f4-wave-launch/02-F4-C1-GRAPH-SCALE-CHAT.md, blob 907273e6d3f458d21ce8b2f128a538e387288e3a. Base F3A: f0d39787e3fb93bfd70ad096824505ba298c6881, tree e0d293bd9de6b78c12934bc395b5f0ab5981563f. Reutilizar branch feat/atlas-parity04-f3a-graph-20261031 e PR Draft16, base F2 54bb16d350f7bc34fafb95438bd64a2397d58bf3.

## Escopo e arquitetura

Corrigir recusa de 1.000 nós/4.000 relações do componente isolado para navegar fixture integral sintética de 2.911 nós/1.595 relações. Descriptor 0.2.0 aprovado no pacote c3ea1e82938fd61cc5a22fee973352715a5bb527 e aceite PR15#issuecomment-6539419419 permanece inalterado. ARC-01–09, ADR-0001 e specs/001 foram confrontados. Nenhum desvio de plano/arquitetura identificado; mudança que o exija será submetida antes de implementar.

Manter modelo/índice completos; desenho SVG por janela/viewport com teto independente de registros carregados, relações com detalhe integral e minimapa geométrico agregado claramente derivado. Todos os nós são localizáveis por índice genérico e navigation_id; revelar somente ancestrais explícitos e materializar o foco antes de focar. Contagens distinguem total declarado/carregado, nós expandidos, SVG desenhado e seleção. Colapso não apaga dados. Hierarquia não vira causalidade; native_id nulo continua nulo.

Preservar API, identidades source_id/snapshot_id/nav_id/occurrence/session_id, token stale/TTL/setData/dispose, texto/URI inertes, ausência de network/storage/script. Quotas descriptor 32MiB/profundidade20/10.000 nós/100.000 relações mantidas. Limites reais auxiliares de trabalho/cópia e prazo30s não serão escondidos; recusa atômica deve ser documentada e encaminhada ao integrador. Não afirmar hard heap256MiB do browser.

## Owners nativos reais e publicação

A /root/a_graph: algoritmo JS/CSS F3A; B /root/b_scale_qa: testes, fixture/gerador, harness e gate focal com prefixo F3A; C /root/c_review: revisão independente, somente leitura, sem autoria. ORQ /root é único writer da branch, publica commits em português por Git Data API com parent único e expected_sha. A/B podem fornecer blobs, sem mover refs. Sem novas branches, worktrees ou clones.

Documentos históricos e seus recibos/manifestos não serão editados; novos sucessores somente em docs/missions/atlas-parity-04/f3a-graph/. Ownership somente JS/CSS F3A, QA F3A e workflow focal se indispensável. F3B, shell, Caderno/protocolo, R4, reader003, Catalog/server/SDK, controles globais e integrador são leitura.

## EXECUTE

1. Índice completo + windowing/desenho limitado, busca/revelação, teclado/foco e minimapa; teste pequeno mantém cobertura herdada.
2. Gerar fixture100% sintética 2.911/1.595 com hierarquia explícita e casos22 endpoint-null/75 unresolved/50 colisões/ocorrências repetidas; preservar fixture histórica.
3. Reexecutar 22 testes e17 jornadas Chromium herdados mais escala: primeiro/meio/último, colapso/órfão/Run externo, duplicate ID e native_id nulo, 1440/390/320px, pan/zoom/fit/minimapa/Tab/setas/Home/End/Enter/Escape, stale/snapshot/TTL/dispose e hostis.
4. Stress10.000/100.000 e recusa10.001; registrar aceitação ou limite real exato, DOM/latência/memória observável/deadline; sem aprovação por truncamento.
5. Sucessor focal preserva conjunto herdado e manifesta delta autorizado exato; Windows/Ubuntu × normal/-O, zero falhas/errors/skips; JSON/JUnit/PNG e custódia SHA/tree. Terminal local indisponível antes de qualquer comando (MXC enumeração D: os error1005); execução remota Actions não equivale a teste local.
6. Revisão C no SHA técnico; corrigir findings, persistir evidências e repetir CI/revisão no HEAD final. Fechamento externo do PR vincula HEAD final sem auto-hash.

## REVIEW e confronto AP04-POR

C revisou os requisitos/arquitetura como compatíveis, sem necessidade de nova autorização para escala in-memory. Revisor deve confrontar código/CI/recibos do novo SHA, sem herdar PASS F3A.

PAR-001: árvore sintética em escala; PAR-004: contexto do componente, fluxo integrado ainda pendente; PAR-007: relações declaradas/ocorrências preservadas; PAR-012 e PAR-015: contribuições focais, não G5 global nem prova de fonte real. G2 sintético apenas; G5/G6 não qualificados; C4 possui sucessão exata dos gates globais conforme GLOBAL-GATE-REPAIR-CONTRACT histórico. PAR-005–010 e demais lacunas não são fechadas. Sem merge/release/deploy/migração/limpeza/licença, ciência ou fonte privada.

Resultado permitido: F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION somente com evidência focal completa e revisão do HEAD final; senão F4_C1_GRAPH_SCALE_BLOCKED_EXACT com causa e próximo ato mínimo.
