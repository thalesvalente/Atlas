# Revisão independente — AP04-F2-DOC-CI-REPAIR-01

Revisor nativo real: /root/review_c, somente leitura, sem autoria dos deltas.

Parecer de plano: compatível com AP04-POR, preservando validação dos controles históricos nos objetos originais e autorização do reparo posterior ao F2 terminal. C recusou tratar truncamento editorial isolado como impedimento de todo trabalho seguro. O operador publicou depois o prompt completo obrigatório, que C conferiu independentemente: blob 370a07b809c98f2bf771cfad0fe89427561bca2d, 11.285 bytes, SHA-256 7eeaa481a628d93f3af26dcf59f25f12eb8d8716d7bd2d51ecb06e30d3053201, oito seções e END presentes.

Riscos levantados antes da implementação: não reescrever manifesto AP04; provar semântica independente do overlay; cobrir classificação das épocas F1/F2 sem alegar CI retroativa; não esconder statement adicional nas linhas excluídas da tabela literal do preflight. Esses pontos integram a revisão técnica requerida.

Revisão da implementação e do SHA terminal: PENDING_PUBLICATION_AND_TERMINAL_CI. Nenhuma aprovação técnica final, humana, científica ou arquitetural é afirmada aqui. O fechamento externo na PR #15 deve identificar o SHA/tree exato, diffs, jobs, artefatos e findings.

Findings prévios identificados por C e corrigidos antes do primeiro commit técnico: C-001, isolamento de cenários negativos por checkpoint técnico positivo; C-002, runner de contraprovas independente no módulo de testes; C-003, autorização por hash de cada revisão intermediária dos controles, incluindo mudança ilícita seguida de reversão. O fechamento de execução desses findings exige os runs reais e revisão de C no SHA publicado.

## Primeiro SHA publicado e correção de desempenho

C conferiu o SHA 9777d1a2dc58ab803b92b518d1e0a70ba0f8847e / tree 37fe3132c3e4b6a4161af4956a0659189136c1c1: um pai 04373bb9…, diff exato 6M+13A, 526 blobs preservados, 37/37 entradas canônicas do manifesto recalculadas. C-001/C-002/C-003 foram fechados em fonte e execução nas quatro células AP04, com 23+27 casos por célula. A qualificação global não foi concedida: ATLAS021 Windows instalado foi cancelado pelo orçamento de 15 minutos, após fonte passar; os outros cinco workflows passaram.

C-004 foi encontrado em candidato não publicado da otimização: pin do teste anterior sobrescrito ao preencher a tabela atual. A fonte corrigida mantém somente os dois hashes exatos de controles revisados em 9777; preflight e nova contraprova duplicam as âncoras Git e verificam bytes antigos e atuais separadamente. C revisou 68ff00ad8722486fd67568f481212b80e59bdb43 / 7d03c30213a782ebd58b48d3635b07c53a65d9ba, sem finding bloqueante de código. C-004 está corrigido na fonte; execução do novo SHA permanece pendente.

O batch parser preserva todas as verificações de OID/tipo/tamanho/framing/conteúdo, épocas, parents e história de controles, sem cache PASS nem redução de IDs. Timeout/pins/controles B permanecem intactos. O uso de hashes de versões anteriores é autorização exata dos bytes revisados, nunca uma allowlist de pasta ou autorização por overlay recalculado.

Limite de inspeção: fontes, logs/recibos, contagens, hashes, nomes e uploads de artefatos/screenhots conferidos; nenhum ZIP/PNG/XML literal ou avaliação manual de pixels. Não se afirma certificação externa completa: o comparador de referência offline registra seus skips e negativo esperados. O fechamento terminal exige revisão de C e CI do SHA que contiver os recibos finais.

## Segundo ciclo e matriz de suítes completas

C confirmou no f642 as quatro células AP04 (23+31), os pins anteriores e C-004 nominalmente passando. C-001–C-004 estão fechados em fonte/execução desse SHA; isso não concede qualificação global, pois a instalada Windows otimizada foi cancelada e wheel/assets não terminaram.

A divisão ATLAS021 por stage literal source/installed foi considerada compatível com AP04-POR: oito células obrigatórias, quatro fontes completas e quatro instaladas completas, mesmo HEAD/tree/OS/-O, timeout15, isolamento/assets e dez pins/ordem preservados. Etapas da fase inativa não equivalem a skips de casos. A lista anterior de actions não foi duplicada. C revisou b0ab10b1b1102af5b4fc8c12b63563744591c35f e A a50911b8f21ce6242e533b36924d1e4434c78f0a / da9bd3128fe144a8e0c7b9cd48751dc8f01745dc, sem finding bloqueante de código.

Os cinco estados anteriores de controle são exclusivamente os publicados em 9777/f642 (quatro hashes A mais o workflow antigo); a contraprova reconcilia commits, blobs e bytes. Os 31 métodos anteriores foram preservados; o novo método cobre oito células e dez mutantes. São 32 métodos definidos, sem afirmar execução antes da CI real. O fechamento da nova matriz e do SHA que contiver recibos finais permanece pendente.
