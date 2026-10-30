# ATLAS-PARITY-03-C4R — candidata completa com gate do host diferido

**C4_FULL_CANDIDATE_READY_HOST_GATE_DEFERRED** para o código `54461f7494df7c0e54a176cf7df3f16ee43e2edb`, tree `73e53237b1362dcd8b65b120acb4c47dfcdf8ba4`. C1+C2+C3 estão presentes por ancestry; P03 representável está visível no app principal; protocolo/fixtures/fontes públicas herdadas estão preservados. Revisão independente real: PASS técnico, sem finding bloqueante remanescente.

Este arquivo integra um commit documental posterior. Os resultados abaixo pertencem somente ao SHA técnico indicado. O próprio commit documental exige CI e revisão por seu SHA; seu fechamento exato fica na descrição da PR Draft #13 e na entrega da conversa, sem transferir resultados nem fabricar autorreferência de commit.

## Comportamento resultante

Metadados usam o read model já validado e identidade explícita de fonte/snapshot. O detalhe permite escolher métricas/parâmetros para tabelas derivadas; mantém display_value, booleanos reais, null/ausência, tipo, unidade, precisão e identidade de linha. Unidades incompatíveis ficam separadas. Erros de apresentação são visíveis e não alteram a validade ou os bytes da fonte. Foco, deep links, filtros e escolhas respeitam fonte/snapshot e expiram na reconstrução do índice.

Os quatro assets P03 e o projetor de metadados permanecem congelados. File continua File; mentions permanece neutra. Produto/documento rico p03-candidate/1, tabela persistida universal e coverage ledger persistido seguem inativos. Não houve mudança de protocolo, contexto, schema, versão, exportador ou carrier.

## CI própria do código qualificado

| Workflow | Run do SHA técnico | Resultado |
|---|---|---|
| ATLAS021 candidate verification | [40976245413](https://github.com/thalesvalente/Atlas/actions/runs/40976245413) | 6/6 success |
| ATLAS-PARITY-02 P06 frozen-boundary QA | [40976245206](https://github.com/thalesvalente/Atlas/actions/runs/40976245206) | 7/7 success |
| ATLAS-PARITY-03 P01 contract gate | [40976245315](https://github.com/thalesvalente/Atlas/actions/runs/40976245315) | 2/2 success |
| ATLAS-PARITY03 P03 isolated qualification | [40976245336](https://github.com/thalesvalente/Atlas/actions/runs/40976245336) | 8/8 success |
| ATLAS-PARITY-03 C4 full composition | [40976245322](https://github.com/thalesvalente/Atlas/actions/runs/40976245322) | 6/6 success |
| ATLAS003 Spec Kit contract checks | [40976245375](https://github.com/thalesvalente/Atlas/actions/runs/40976245375) | 2/2 success |

São seis workflows e 31/31 jobs success. Ubuntu/Windows × normal/-O executaram a mesma coleção de 168 casos únicos por célula, preservando os 122 IDs C1, sem skips/falhas/erros. A repetição por SO/modo não cria casos novos; os 47 casos focais P03 e seus 12 SDK se sobrepõem à coleção integrada e não são somados novamente.

P01/C3 executou 46 exemplos, 9 probes, 11 regressões e auditoria por modo, com matriz histórica de 28 linhas e 22 colunas preservada, UNKNOWN_UPSTREAM/denominador desconhecido/0÷0 indefinido/sidecar opcional. As 28 jornadas P01 não são atribuídas ao estudo C ausente. O revisor leu todos os 95 blobs C3/P01, os manifestos de 82 e 11 entradas e os 51 blobs técnicos; a lacuna independente C3 foi fechada no SHA técnico.

P03 focal passou 47 verificações HTTP por célula, JSON Schema real, build/install isolados e 19 checks browser por SO. Browser integrado C0+P03 passou 31 checks nas quatro células, com 16 PNGs próprios, zero requisições externas/page errors/console errors, texto hostil inerte, reflow em 1440, 390 e 320 CSS px, troca de pacote, IDs repetidos, teclado/foco e erro Metadata LIMIT visível com fonte READY. Foram conferidos os 26 ZIPs por size/SHA256, seus JSON/JUnit/logs e 42 PNGs por digest; a revisão visual fechou C4-R02.

## Reparos e integridade

A primeira rodada d897a8f8 terminou RED, com 24/31 jobs aprovados e a segunda, 3e65ac51, RED, com 27/31 jobs aprovados por incompatibilidades explícitas de harness. a21bacf3 passou 31/31, mas permaneceu não aceito por C4-R02: CSS global alterava visualmente a caixa de unidades/IDs. O reparo restrito ao embedding P03 e o novo oráculo real de tipografia/identidades passaram no código qualificado. Os estados anteriores não foram convertidos em PASS. Detalhes e runs estão em CI-EVIDENCE.json.

Somente o teste histórico que exigia P03 ausente do shell foi adaptado à composição autorizada: 24/25 arquivos congelados e 55/56 entradas P03 continuam atuais; a exceção tem path/hash explícitos. Manifestos e branches fonte não foram reescritos. BLOB-PROVENANCE.csv registra 338 paths diferentes da main; 39 paths de autoria C4 são cobertos pelo MANIFEST.sha256, excluindo apenas o próprio manifesto (38 entradas). Os dois arquivos de fechamento resolvem sua própria identidade pela tree que os contém.

## Gate local e limites

L2_BLOCKED_EXACT é terminal exclusivamente do C1. Instalação/offline normal/-O do C1 passaram no escopo dos recibos; HTTP/browser ficaram impedidos pela guarda herdada do WinError 10013, sem nova tentativa L2. Este CHAT não executou produto/teste/servidor no host. LOCAL_C4_INSTALLATION/OFFLINE/HTTP_BROWSER=NOT_RUN; HOST_OPERATIONAL_READINESS=false. CI não substitui o futuro replay LOCAL C4.

C4 comprova reflow nas larguras registradas, não zoom nativo de 200% nem certificação WCAG. O NOT_RUN nativo do P03 mantém sua exceção documentada e não é substituído por CSS zoom/device scale. Validade, integridade, autenticidade e ciência permanecem eixos separados. REASONING_EFFECTIVE=UNVERIFIED: a seleção manual Max não é observável pelo agente.

A PR permanece Draft. Este resultado permite somente handoff e revisão humana de código/evidências; não autoriza merge, release, deploy, promoção, mudança de licença ou ciência. Sem import r4.*, publicação P04, chamadas pagas ou remediação de ACL/firewall/sandbox do host.
