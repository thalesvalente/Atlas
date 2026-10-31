# RESULT — AP04-F3B-CHAT-TABLES-01

Data2026-10-31. Técnico: **F3B_TABLE_COMPONENT_READY_FOR_F4**, somente componente genérico sobre fixture inventada. Estado AP04: **PARTIAL_PARITY_WITH_GAPS**. O HEAD documental que contém este arquivo só recebe fechamento terminal após CI/revisão próprias registradas na PR17.

## Identidade, autorização e execução

BaseF2:54bb16d350f7bc34fafb95438bd64a2397d58bf3/tree1372dd532b2323fc1ebaa5c2f00b6d537c636dc9. Prompt23e776d5b94e1e075275d28e41b5e9214a52cffe. Plano AP04-POR-v1.0-draft, ARC01–09 e D001–020 preservados. ADR0003v0.2/descriptor0.2.0 APPROVED_SCOPED pelo comentário6539419419, pacote c3ea1e82938fd61cc5a22fee973352715a5bb527. Esta execução autoriza somente F3B.

PLAN publicado emc0076fcf3fdbb6e26b225e816dc153d93149366c. Código em b29eb124064238276b7d485daa052120eab7b1d1; reparos de revisão em8f1da3af0f1b9e981d64d4fa5fd7b8010c904b0c. Técnico qualificado **aa804815a173bf091108c1a81410f1b0f2f838ca**, tree19f87d1dda3b1e75fbec70817612dcb9893bda83, parent8f1da3af0f1b9e981d64d4fa5fd7b8010c904b0c. O último técnico altera só teste/manifesto; JS/CSS mantêm os reparos de8f1. Histórico linear fast-forward com lease, sem rebase/force.

Ownership real: /root/model_a JS/CSS; /root/qa_b fixtures/testes; /root/review_c somente leitura, sem autoria, revisão independente; /root único writerGit e autor dos recibos/workflow. REASONING_EFFECTIVE=UNVERIFIED. A seleção manual de esforço não foi observada.

Ambiente qualificador: conectorGitHub e Actions. Tentativa inicial de execução local falhou antes de leituras/escritas/testes e não foi evidência qualificadora. Nenhuma troca de checkout, worktree ou clone local/persistente; Actions usa checkout efêmero por SHA.

## Entrega funcional e coleção

Renderer independente com tabela semântica/caption/th/headers, filtros rotulados, busca, ordenação explicitamente tipada e comparável, paginação com totais, detalhe integral, seleção efêmera e exportações JSON fiel/CSV seguro. Mantém cabeçalhos/ordem/tipos/literais/lexemas/unidades/precisão/ausência e estados científicos separados. RF/RNF/RES são opcionais. JSON não é bytes originais nem autenticidade; CSV é transformação declarada. API/limites em TABLE-CONTRACT.md.

Coleção100% sintética:5tabelas/46linhas(16RF admitidas apenas por identidade sintética,28RF não admitidas,1RNF,1RES);4tabelas não vinculadas,1tabela conhecida vazia,2nós fonte+1stub externo,1relação,1File. Categoria missing/null/vazia/zero/UNKNOWN distinta. Gaps e Run externo permanecem. Não reproduzF1; F1 foi lida somente pela síntese sanitizada.

## Antes/depois perante AP04

| PAR | Antes literal | Contribuição F3B e evidência | Depois e lacuna |
|---|---|---|---|
| PAR-002 | NOT_RECOVERED | Campos RF/filtro/detalhe/exportação, testes01–06/09/11 no técnico | PARTIAL_NOT_EQUIVALENT: componente sintético, nenhuma RF real integrada |
| PAR-003 | INPUT_AVAILABILITY_UNKNOWN | Mesmo renderer RNF/RES somente declaradas, teste08 | INPUT_AVAILABILITY_UNKNOWN do acervo; engenharia sintética comprovada |
| PAR-004 | PARTIAL_NOT_EQUIVALENT | Token fonte/snapshot/sessão/ocorrência e evento neutro; testes12–15/19/22 | PARTIAL_NOT_EQUIVALENT: sem caminho contínuo árvore→RF; F4 não feita |
| PAR-005/006 | NOT_RECOVERED / PARTIAL_NOT_EQUIVALENT | File não promovido a produto; URI/HTML inertes, testes08/10 | Estados históricos mantidos; nenhuma recuperação de produtos/dossiês |
| PAR-012 | BASELINE_VERIFIED |545blobs base idênticos, assets isolados, CI focal própria | PARTIAL_NOT_EQUIVALENT desta fase; G5global não qualificado |
| PAR-015 | BASELINE_VERIFIED_SCOPE | Fonte sintética não muda, JSON fiel, colisões/ausências/recusas e stale links testados | PARTIAL_NOT_EQUIVALENT do acervo: fonte privada/global não reobservadas |

Estes estados de fase não apagam nem revalidam as baselines históricas. PAR001/007–011/013/014 continuam com owners/gates próprios. UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN, denominador global null e snapshots NOT_SUMMED mantidos. RO-Crate1.3, ProcessRun0.6 e Caderno0.1.0a1 intactos; HL7/FHIR futuro por domínio, sem implementação ou conformidade atual.

## Testes reais e revisão

[Gate focal técnico41173677346](https://github.com/thalesvalente/Atlas/actions/runs/41173677346), attempt1, quatro jobs completed/success: Windows/Ubuntu×Python normal/O1. Cada célula executou24testes top-level e380IDs de recibo distintos/iguais, zero falhas/erros/skips, Chromium151.0.7922.34. Total96execuções top-level/1520casos,12screenshots1440/390/320×900. Asserções executáveis de DOM/reflow/foco/teclado/zero erros de página-console/zero requisições externas da página. Quatro artefatos com JSON/JUnit/descriptor/screenhots e recibo de ownership; hashes e atribuição por SHA conferidos. B conferiu logsUbuntuO0/WinO1; C conferiu todos quatro e integridade. Sem inspeção manual de pixels/ZIP/XML literal.

C-001–004 corrigidos e fechados no técnico por revisão nativa real e testes. A tentativa inicialb29 falhou no pinPython inexistente; a8f1 falhou no teste de quota que amplificava células extensas no transporte, sem alegação de recusa atômica. A fixture negativa foi isolada; 129tabelas pequenas e33.554.433 bytes ASCII (32MiB+1byte) gerados no browser agora testam as quotas separadamente. Os limites de produto não foram relaxados.

## CI global e sucessão

[AP04 histórico no mesmo técnico](https://github.com/thalesvalente/Atlas/actions/runs/41173681607/job/124456718342) falha exatamente: GuardError: Repair history contains unauthorized paths: ['docs/missions/atlas-parity-04/f3b-tables/PLAN.md']. É uma proteção histórica de sucessãoF2; não foi afrouxada. CI-EVIDENCE.json conserva estados observados de outras famílias, inclusive qualquer in_progress, sem converter em PASS. Nenhuma alegaçãoG5global.

Owner/integrador futuro deve receber escopo próprio para qualificação sucessora/global com delta/história exatos e regressão no SHA integrado. F3B não muda P06/P03/AP04/F2/C4, pins/oráculos/gates históricos, nem usa continue-on-error/paths-ignore. PR15 permanece Draft; PR17 própria com base explícita F2 foi aberta para CI/QA.

## Limites, handoff e próximo ato

Nenhuma fonte privada/códigoR4 recebido ou publicado. Protocolo,reader003,server/Catalog/SDK,shell,F3A e controles/manifests históricos preservados. Nenhuma migração,reorganização,exclusão,licença,merge,release,deploy,promoção ou ciência.

Abertura externa/FileAPI não implementada: isolamento256MiB/30s, acessoallowlist/host e observação de fontes pertencem a F4; F3B aplica quotas estruturais em memória sem prometer heap/deadline duro. N14/N16 e fases de aquisição/integração não foram simuladas como testesPass.

HANDOFF.json e MANIFEST.sha256 são entrega durávelGit; imagens/JSON/JUnit estão nos artefatos Actions identificados por digest, com retenção publicada. O commit que contém os recibos exige novoCI e revisãoC; fechamento externo na [PR Draft17](https://github.com/thalesvalente/Atlas/pull/17) deve nomear o SHA/tree/parent terminal, run e parecer próprios. Nenhum commit posterior para registrar o próprio hash.

Próximo ato: integradorF4, sob autorização própria, consome componentes F3A/F3B qualificados, versiona/revisa contrato003 e respeita gatesF1/F2/segurança. Este resultado não iniciaF4 nem concede RF real/G6.
