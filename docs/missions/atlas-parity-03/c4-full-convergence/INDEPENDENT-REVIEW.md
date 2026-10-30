# Revisão independente — ATLAS-PARITY-03-C4R

Revisor nativo real `/root/independent_review`, sem autoria de arquivos ou commits. O coordenador registra aqui o parecer recebido; isso não transforma a redação deste registro em autoria do revisor no delta. Runtime: `/root/runtime_p03`; CI/QA: `/root/ci_contracts`; Git/documentação: `/root`.

**PASS_SCOPED_TECHNICAL_AND_ARTIFACT_REVIEW** no SHA `54461f7494df7c0e54a176cf7df3f16ee43e2edb`, tree `73e53237b1362dcd8b65b120acb4c47dfcdf8ba4`. Nenhum finding bloqueante remanescente nesse SHA. O commit documental que contém este registro exige CI e leitura independente próprias, reconciliadas externamente no fechamento exato da PR #13.

## Escopo efetivamente examinado

O revisor leu integralmente 95 arquivos P01/C3 (529620 bytes), corpus de 46 exemplos, 9 probes, 11 regressões, validador, runner, workflow, contratos, matrizes e recibos. Recalculou manifestos P01 82/82 e C3 11/11, conferiu 51/51 blobs técnicos e preservação dos 95 blobs no merge puro e na candidata final técnica. Leu ZIPs fonte C3 e os do próprio SHA C4; os relatórios normal/-O mantêm o hash canônico 53474dcf1eddf55880860c61d3b335df4de02765d8ebfdefb0979ce415d91e6c. UNKNOWN_UPSTREAM, denominador null, 0/0 indefinido e sidecar opcional seguem intactos. A lacuna independente C3 está fechada para todos os bytes incorporados neste SHA.

Conferiu a topologia de três pais, main/inputs fixados, os 39 blobs próprios C4 e o manifesto 38/38 com cobertura exata, proveniência 338/338 e origens corretas; protocolo e fixtures herdadas idênticos. Revisou os 8 paths runtime e 13 CI/QA, imports/allowlist, montagem/desmontagem, seleção explícita, números/booleanos/ausência/unidades/precisão, identidade por fonte/snapshot, File/mentions e demonstradores inativos.

Confirmou seis workflows e 31 jobs terminal success no SHA técnico e todos 26 ZIPs por size/digest API. Leu JSON/JUnit/logs internos e conferiu 42 PNGs por digest. Installed: 168 casos por célula Ubuntu/Windows normal/-O, 122 IDs C1 preservados, zero skips. P03 focal 47 casos por célula e 19 checks browser por SO. C4 integrado 31 checks por célula e 16 PNGs; zero externos/page errors/console errors e cópias sintéticas esperadas.

## Findings e disposições

- C4-R01: teste histórico de isolamento C2 incompatível com a composição. Fechado por adaptação explícita de um único teste, hash 3bed307fb7f9aec6b4d4929be2865a8344c66b3f0f2a7c0c9aa749661b9c7689; 24/25 e 55/56 bytes atuais preservados. Nenhum skip/exclusão; C2 histórico intacto.
- C4-QA-01–03: seletores de cabeçalho/lista de definições e freeze browser focal ainda preso ao contexto C2. Reparos próprios, sem alteração de valores esperados; d897 permanece RED.
- C4-QA-04: espera indevida por reescrita de URL obsoleta. Owning C1 conserva URL rejeitada com explicação; o teste passa a aguardar snapshot renderizado, preservando expiração de seleção e rejeição do link antigo.3e65 permanece RED.
- C4-R02[P2]: uppercase global de th convertia visualmente mg/L,µg/L e URNs. a21 passou CI mas não foi aceito. Fechado no SHA técnico indicado, por reset restrito ao embedding, computedStyle none, igualdade raw/rendered/declarado nos 6 IDs e unidades literais. O revisor leu os PNGs originais Ubuntu1440 cc8e0e4ac1ea79a9366baa31f638471d88131e5857cdfae6faf9a04d90ab6759 e Windows1440 75da68f95e567065ddb2509b254edbec77d491651d7e9629d52f09da1b976a7a, mais recortes de 320 px e erro LIMIT visível. As quatro receipts registram 71 estilos none e preservação lexical.

## Limites do parecer

Não houve execução de produto/testes/servidor local pelo revisor nem autoria de deltas. Seu escopo L2 foi somente a atribuição sanitizada C4. O coordenador leu diretamente HANDOFF/RESULT e conferiu os digests após autorização posterior do operador; não atribuímos ao revisor rehash de P04 ou validação privada.

LOCAL_C4_* permanece NOT_RUN e HOST_OPERATIONAL_READINESS=false. O parecer não aprova ciência, mantenedor, operação do host, merge/release/deploy/promoção ou WCAG/zoom nativo. Não transfere CI/revisão ao commit documental futuro; o fechamento desse SHA é externo e obrigatório.
