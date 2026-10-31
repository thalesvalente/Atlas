# AP04-F2-DOC-CI-REPAIR-01 — reparo em qualificação

Estado: STAGE_MATRIX_CANDIDATE_PENDING_REAL_CI. Não é AP04_F2_DOCUMENTATION_CI_QUALIFIED.

PLAN: prompt obrigatório 8abf556c6c39fcc54855391f2eeef3d8a8615985 conferido integralmente; C4/AP04/F1/F2 e dezenove documentos por SHA/tree/parent/blob/hash/mode reconciliados. Dezenove paths exatos fixados antes da edição. A responde pelo novo guard/testes; B por seis controles de CI; ORQ pelos onze recibos; C é independente, somente leitura e sem autoria. O plano AP04-POR e os gates científicos permanecem intactos.

## Reparo e evidência real

A sucessão por épocas corrigiu a recusa dos cinco documentos F1 e catorze F2 pelo guard AP04 histórico. A autoria AP04 é verificada nos objetos Git originais, os documentos F1/F2 ficam congelados e o reparo posterior ao terminal 04373bb9 é restrito ao inventário exato. Guard/testes/manifests históricos, produto, protocolo e fontes não foram reescritos.

No primeiro SHA 9777d1a2dc58ab803b92b518d1e0a70ba0f8847e, cinco workflows passaram e ATLAS021 foi cancelado nas duas células Windows instaladas. AP04 passou 23+27 casos nas quatro células; Ubuntu instalado comprovou 218 IDs. O recibo completo permanece no CI-EVIDENCE.json do ancestral f642660d e é referenciado pelo blob/hash, sem ocultar os cancelamentos.

No segundo SHA f642660d6b1782ff4e3cebb90b09398df5e57734, a leitura em lote preservou todos os oráculos e passou 23+31 casos AP04 nas quatro células. Cinco workflows passaram. Foram 32 jobs success e um cancelled: ATLAS021 Windows otimizado 124427862969 foi cancelado na suíte instalada após 15m13s, com limite de 15 minutos. Fonte passou 12+135+75 casos; QA levou 429.908s. Três células instaladas comprovaram 222 IDs únicos (191 herdados +31), sem perdas/duplicações/skips/loader errors/falhas; a otimizada Windows ficou incompleta. Quatro browsers C4 passaram nos 31 checks. Esse SHA também não foi qualificado.

## Correção do orçamento de CI

ATLAS021 agora declara uma matriz fechada source/installed: quatro células completas de fonte e quatro instaladas, no mesmo HEAD/tree, com os mesmos OS, modos Python, timeout de 15 minutos, fail-fast=false e lista ordenada dos dez uses/pins. Source executa run_checks inteiro. Installed executa clean_install, a suíte completa fora do checkout, todos os IDs herdados/novos, wheel/assets e upload atribuído ao SHA. Nenhum teste foi removido, filtrado, substituído ou marcado skip. Etapas da fase inativa serão SKIPPED por roteamento; os casos da fase ativa continuam exigindo zero skips/falhas/loader errors. Browser e referência permanecem idênticos.

A redistribuição das duas verificações já obrigatórias foi revisada por C como compatível com AP04-POR, sem mudar F0–F6/PAR/GATES/arquitetura. Não houve ampliação de timeout nem alteração de pin. O guard novo autoriza somente cinco revisões anteriores de controles efetivamente publicadas e revisadas em 9777/f642, verificadas independentemente por Git. Nenhum candidato não integrado é autorizado.

Há 32 métodos novos definidos, preservando os 31 anteriores e acrescentando contraprova da matriz e dez mutações de perda de eixos, seleção, comandos ou recibos. A execução deste candidato ainda está pendente.

## Revisão e fechamento

C-001/C-002/C-003 foram fechados no primeiro SHA; C-004, pin histórico preenchido no lugar errado em candidato não integrado, foi corrigido antes de alterar a branch e fechado nas quatro células AP04 do f642. C revisou os três novos blobs A/B sem finding bloqueante de código, mantendo a execução e revisão terminal pendentes.

CI-EVIDENCE.json registra os ciclos, IDs, jobs, artefatos e limitações reais. Screenshots/JSON/JUnit são conferidos por identidade, fontes congeladas, recibos/logs e uploads; ZIP/PNG/XML não foram abertos nem pixels inspecionados. O comparador externo offline conserva seus skips e negativo esperados, sem certificação Caderno/Process Run ou alegação de zero skip global externo.

O commit que contém estes recibos exige seus próprios seis workflows completed/success e parecer independente do SHA terminal. A conclusão externa na PR #15 evita ciclo de auto-hash. A PR permanece Draft; ADR-0003 v0.2/descriptor 0.2.0 continuam propostos e G4 pendente. Sem File API/F3–F6, R4, migração, merge/release/deploy/promoção/limpeza ou aceite científico.
