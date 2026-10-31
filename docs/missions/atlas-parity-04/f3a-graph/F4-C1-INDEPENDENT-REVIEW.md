# Revisão independente nativa — F4 C1

Revisor C, `/root/c_review`: subagente nativo real, somente leitura, sem autoria de código/testes/recibos ou publicação da branch. ORQ registra o parecer; não se trata de assinatura ou aceite humano.

## Parecer técnico por SHA

**PASS_SCOPED_FOR_COMPOSITION**, SHA `913e4038b817916c9a728e18b8cd780ade36b9f0`, tree `7eabeffd019f206641412c56a29ab705ad15b4d3`. C leu fontes/QA, comparou ownership e verificou independentemente os quatro logs e os jobs do [run 41213311466](https://github.com/thalesvalente/Atlas/actions/runs/41213311466). Windows: 124572607114/O0 e 124572607413/O1. Ubuntu: 124572607388/O0 e 124572607335/O1. Cada célula executou 30 testes e 24 jornadas, incluindo o conjunto herdado de 22/17, com zero falhas, erros, skips ou I/O indevido e SHA/tree corretos.

Schema literal 0.2.0 preservado. Modelo/índice de 2.911/1.595, pais explícitos, foco DOM materializado, desenho limitado, minimapa geométrico, anomalias e ocorrências, textos/URIs inertes e stale/snapshot/TTL/dispose foram confrontados. Nenhum finding bloqueante permanece aberto nesse SHA técnico. Cada novo HEAD exige CI/revisão próprias; a revisão terminal do HEAD documental será registrada externamente no PR #16.

## Findings fechados

- C1-MINI-01: o minimapa com proporção padrão comprimira a árvore alta numa faixa de aproximadamente 1 px; simples mudança de pan podia aceitar câmera fora do grafo. O sucessor usa preserveAspectRatio none. O oráculo real mede 255,32/300 px, 175 marcas que somam 2.911 nós e câmera dentro dos limites/próxima à marca clicada. Fechado pela execução 913 em Windows/Ubuntu.
- C1-HARNESS-STRESS-01: as rodadas 7a629/e069 não foram qualificadas. O receipt tinha 23/24 jornadas; o stress fechou o browser e o Node permaneceu ativo até 600 s. Isso não demonstrava recusa do produto. O sucessor QA constrói o payload integral sequencialmente no renderer, transmite apenas contagens e retorna métricas pequenas, conserva os prazos do produto/Python, registra progresso e mantém falhas de cleanup como FAIL. Os resultados 24/24 e 30/30 nas quatro células fecharam o finding no SHA técnico.

## Limites e composição

10.000 nós/0 relações foram aceitos. 10.001 nós foram recusados por array quota. O stress de 10.000/100.000, com 81.008.070 bytes, foi recusado atomicamente pelo limite de 600.000 valores em 1,3925–2,1144 s e também excede 32 MiB. Isso não prova 100.000 relações válidas dentro da quota. A limitação auxiliar segue como REAL_VALUE_CAP_GATE_INTEGRATOR_REQUIRED; não alterar quotas silenciosamente. UsedJSHeapSize é observação quantizada, sem qualificar hard heap de 256 MiB. G5/G6 e fonte real continuam não qualificados.

C conferiu a cadeia de parent único e os 14 paths do delta C1 contra F3A: seis arquivos de produto/QA e oito documentos novos. Controles, fixture e históricos foram preservados; F3B/shell/protocolo/R4/reader003 não foram alterados. O PLAN f229239e/tree e610173b foi considerado COMPATIBLE_SCOPED, sem desvio AP04/ARC. As decisões de windowing, minimapa e harness são compatíveis com o plano autorizado.
