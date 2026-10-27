# ATLAS-PARITY-03-C1 — revisão nativa independente

## Identidade e veredito R1

- Revisor nativo real: `/root/independent_review`.
- Autoria em código, testes, workflows, agregadores e documentos da candidata: **nenhuma**. Este parecer temporário é entregue ao coordenador para transcrição atribuída.
- Código composto revisado: `df56eb6338626d1671d1882d0d745c02a1f48406`.
- Árvore: `9f808e84f7bfd367bdec84e74daab1c2977f38be`.
- Pai de composição: `4bfe0040c273d35719fc6e3de5e81d1fe9e40b65`, árvore `d02432046d4bb7945cfd39581f674d7252bc415b`.
- **Veredito de código: PASS_SCOPED; zero findings bloqueantes abertos.**
- `REASONING_EFFECTIVE=UNVERIFIED`; o seletor não é observável pelo revisor.

O parecer abrange os objetos Git indicados e a leitura dos controles de engenharia. Não declara CI ou browser aprovados, nem concede aceite humano, aprovação científica, merge, release ou promoção. CI no SHA final e revisão documental final permanecem gates separados.

## Método e fontes examinadas

Foram lidos AGENTS, constituição ARC-01–09, ADR-0002, os handoffs/RESULT/manifests P02 e P06, P06-INTEGRATION, contrato de navegação P02, arquitetura/matriz/decisão P06, os scripts existentes de instalação e browser, o runtime P02 pertinente e todos os caminhos do delta C1 de R1. Os drafts dos autores foram inspecionados antes da publicação; a comparação posterior contra os blobs de R1 confirmou apenas normalização de uma linha vazia final e o guard adicional de checkout limpo no runner instalado, ambos revisados.

As verificações de objetos, manifests e invariância foram feitas por `git show`, `git ls-tree`, `git diff`, `git merge-base --is-ancestor` e SHA-256 dos blobs, sem alterar o repositório. Três auditorias somente leitura foram executadas com `python -B`. O revisor não executou a suíte de sockets, servidor, browser ou comandos no host do usuário e não consultou repetidamente o estado remoto.

## Topologia, conteúdo congelado e ownership

O commit de composição tem exatamente três pais, nesta ordem: baseline `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, head documental P02 `db6e8b64c28e756d0a2ff4fd1cd90f404c6c0533` e head documental P06 `9b0a500b6612d260a9f9bd8a4c8da1be4841cf48`. Os dois commits de código testados, `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990` e `d21d8a490b89995ae5707a7a53b469685416a383`, também são ancestrais de R1. As cinco consultas `merge-base --is-ancestor` retornaram 0.

A baseline contém 162 arquivos. P02 modifica/adiciona 56 caminhos; P06, 23; não há caminho alterado em comum. A união independente das árvores produz exatamente os 236 arquivos do merge `4bfe0040…`, sem conflito nem caminho adicional. Não há baseline substituta, squash ou integração P01/P03.

Os manifests foram verificados nos respectivos heads de origem:

| Entrada | Linhas válidas | SHA-256 do manifesto |
|---|---:|---|
| P02 | 55/55 | `7c27b4a93c7a02399b350262f2dd21f34e1350291a3ec8da292cced463b63178` |
| P06 | 22/22 | `2802e604cfc33508fb4f57ad15d8a58f40d859975f4d3d9fa891d2d333502236` |

Os manifests históricos permanecem byte-idênticos e continuam descrevendo seus inputs congelados, não o overlay C1. Em R1, os caminhos manifestados que mudam são exatamente os dois harnesses P02 (`atlas_parity02_p02_browser.mjs` e `atlas_parity02_p02_run_browser.py`), workflow P06, browser P06 e cinco agregadores 004. Essas mudanças têm ownership C1 e justificativa técnica explícita. Os sete paths de runtime P02 permanecem byte-idênticos. Nenhum arquivo de `packages/protocol`, `examples`, `.agents`, `.specify`, `docs/architecture`, `docs/protocol` ou AGENTS mudou contra a baseline. As fixtures P02 permanecem idênticas ao head P02.

O overlay R1 contém 17 caminhos, todos dentro do ownership autorizado: três workflows; auditoria global e negativas; harness global; harnesses P02/P06 e prova instalada; cinco agregadores 004. A revisão dos documentos finais deve manter esses deltas e justificativas explícitos.

## Gates reparados

### Auditoria Spec Kit

`scripts/qa/speckit_audit.py` mantém o default estrito. O opt-in `--allow-p02-c0-delta` é independente do opt-in histórico, não aceita paths fornecidos pelo caller e exige os bytes do P02_CODE_SHA em exatamente catalog.py, server.py e static/index.html. A autorização é verificada por objeto Git, não por prefixo de diretório. Rollback arbitrário para os bytes antigos, mudança livre nos três paths e adição/remoção no protocolo continuam rejeitados. O pin de todo o protocolo em c2 impede usar a exceção histórica de read_model.py para alterar o contrato nesta composição.

As 15 negativas/positivas de auditoria usam unittest.assert* e subprocessos Git reais sobre fixtures, portanto não desaparecem com `-O`. Cobrem default, separação de opt-ins, bytes não congelados, exclusão/remoção, sibling não autorizado, protocolo, constituição, ADRs, skills e CLI sem parâmetros arbitrários de exclusão/baseline.

Execução somente leitura pelo revisor sobre R1: default retornou FAIL/exit 1 esperado, com nove paths históricos alterados; os dois opt-ins retornaram PASS/exit 0, autorizando três blobs P02 e mantendo 12 arquivos de protocolo, 28 arquivos gerenciados, dez skills e seis scripts oficiais. A auditoria P06 retornou PASS_SCOPED/exit 0 para 64 arquivos protegidos, com SHA/tree de R1 explícitos.

### H06-01/02/03 e troca de pacote

O harness global localiza controles por `JSON.stringify([sourceId, runId])`, exige unicidade e confronta o conjunto de identidades apresentado com a API independentemente da ordenação. O detalhe confirma fonte/ID; texto principal da métrica e identificador secundário são testados separadamente. Valor, motivo de ausência, tipo, unidade e precisão permanecem exigidos. Comparações usam `th[scope=row]`, identificam as colunas pelos controles fonte+ID e verificam todos os valores e IDs de medições repetidas na coluna correta. Nenhum algoritmo de sort do produto foi copiado como oráculo.

A divergência semântica P06 foi corretamente resolvida no teste: o binding global P02 expira todas as seleções quando um pacote muda o snapshot. O harness agora exige seleção vazia e aviso, demonstra que B conserva snapshot/read_model, exige nova seleção explícita ligada ao snapshot novo e só então percorre a referência por teclado na fonte correta. Não se alterou o runtime congelado para satisfazer a antiga expectativa de seleção sobrevivente. A contraprova de estado é rotulada como Node sobre asset real, sem alegação de browser; o browser real continua obrigatório.

### Instalação, coleta e navegador

Os três workflows fazem checkout do head explícito da PR e conservam histórico necessário aos pins. Os consumidores são criados em RUNNER_TEMP fora do checkout. SDK-only e viewer são provados primeiro por clean_install; jsonschema==4.25.1 entra depois como ferramenta de teste no viewer-env, sem alterar dependência de runtime. Essa separação corrige o único finding preliminar encontrado pelo revisor: sem a ferramenta, o teste de JSON Schema faria skip no venv isolado.

O novo runner instalado exige checkout limpo, import paths sob sys.prefix e fora do repo, ausência de R4, coleta por IDs únicos e zero skips. Propaga `-O` explicitamente para subprocessos com `-I`, que ignora PYTHONOPTIMIZE. Não fixa uma contagem histórica como requisito. Os quatro cenários adicionais/repetidos de CI não são somados como novos unittest.

O workflow de produto chama os três cenários legados e P02; P06 mantém seu job separado. Os cenários posteriores têm execução mesmo após falha anterior, sem converter falha em sucesso. A jornada P02 exige SHA igual a HEAD, fontes CJK/emoji com hashes/cobertura declarada, versão Playwright e exatamente seis PNGs hashados; não flexibiliza o isolamento para `.ci-clean`. `native_zoom=NOT_RUN`, `css_zoom_used=false` e `wcag_certification=false` permanecem próprios do P02. O cenário legado CSS200 registra sua técnica separadamente.

### Spec Kit e arquitetura

A feature 004 foi agregada com P02/P06 concretos, IDs históricos de tarefa preservados e novos critérios explícitos. Helpers 003 e 004 usam `SPECIFY_FEATURE_DIRECTORY` e `SPECIFY_FEATURE_NO_PERSIST=1`; `.specify` permanece byte-idêntico. Os arquivos históricos de ADR conservam seus estados antigos, enquanto os agregadores reconhecem o aceite posterior da direção ADR-0002. Nenhuma alteração de schema, contexto, versão persistida, adaptador ou poder sobre dados foi encontrada.

## Findings e limites

- Finding preliminar resolvido: dependência jsonschema ausente no consumer de testes instalado causaria skip. Correção presente em R1, somente tooling de teste.
- Findings bloqueantes de código abertos: **nenhum**.
- CI/browser de R1: **não avaliados neste parecer**; os resultados serão confrontados por SHA quando recebidos do coordenador.
- Os 122 casos e os sete EPERM de socket informados pelo coordenador são evidência preliminar do ambiente de engenharia, não uma nova suíte executada por este revisor nem um PASS de Actions.
- Documentos finais C1 e commit que os contém: **revisão pendente por SHA**.
- Operação/browser no host do usuário: **NOT_RUN**.
- Merge, release, deploy, promoção, aprovação científica e acesso P04 privado: **fora deste parecer e não autorizados por ele**.

R1 pode prosseguir para os gates já autorizados. `C1_CORE_CANDIDATE_READY` só é justificável após os runs globais terminarem success no SHA final, evidências browser/instaladas desse objeto e revisão documental independente correspondente.

## Complemento R1 — inspeção independente dos primeiros artefatos Actions

Após a revisão de código, o coordenador disponibilizou os arquivos baixados dos artifacts R1 em `atlas-c1-artifacts/r1`. O revisor leu diretamente os JSONs/logs e recalculou hashes; não fez novas consultas remotas de CI. O resumo dessa inspeção está em `/tmp/atlas-c1-review-r1-receipts.json`.

Os sete ZIPs com IDs 12753560820, 12753376391, 12753301213, 12753052055, 12752632881, 12751964434 e 12751444152 têm SHA-256 igual ao digest retornado pela API e registrado pelo coordenador. Seus nomes pinam `df56eb6338626d1671d1882d0d745c02a1f48406`. Cada arquivo extraído foi comparado aos bytes do próprio ZIP; não houve divergência.

Três células da suíte instalada já tinham recibos completos disponíveis nessa leitura:

| Artifact | Plataforma/modo | Resultado | Coleção única | Falhas/erros/skips |
|---|---|---|---:|---|
| 12751444152 | Ubuntu / -O | PASS_SCOPED | 122 | 0/0/0 |
| 12751964434 | Windows / -O | PASS_SCOPED | 122 | 0/0/0 |
| 12752632881 | Ubuntu / normal | PASS_SCOPED | 122 | 0/0/0 |

Todos os três JSONs declaram o SHA/tree de R1 e têm o mesmo conjunto de 122 IDs: 12 SDK + 74 QA + 36 viewer. Os logs correspondentes registram essas três contagens e três finais OK, sem skips. O conjunto repetido em outro OS/modo é execução adicional dos mesmos casos, não novos casos únicos. Os import paths estão em `_temp/atlas-c1-portable/viewer-env`, fora do checkout; jsonschema 4.25.1 aparece apenas como ferramenta de teste. A célula Windows normal e o browser de produto não estavam nesse lote; seus resultados não foram inferidos.

O revisor comparou os hashes de 22 arquivos de origem em cada um dos oito recibos clean_install disponíveis com os blobs de R1. Todos coincidem. Os checks SDK sem viewer/R4, viewer sem R4, rebuild e fontes intactas são PASS_SCOPED nesses recibos. Em sete recibos wheel, os quatro assets HTTP/wheel correspondem aos quatro blobs estáticos de R1; os digests do wheel correspondem ao clean_install do mesmo artifact. Essa é inspeção de evidência Actions atribuída, não uma nova instalação feita pelo revisor.

Os quatro artifacts P06 também contêm os recibos de invariância: todos pinam SHA/tree R1 e baseline c2, registram 64 arquivos protegidos e zero erros. Foram lidos diretamente dos ZIPs.

O JSON do browser P06 declara `tested_sha=df56eb6…`, Chromium 151.0.7922.34, **14 checks PASS_SCOPED**, zero requisições externas e zero erros de página. Inclui expiração das seleções antigas, invariância de B, seleção nova com scope novo, teclado/foco e reflow390. A mutação da metadata é explicitamente do driver sintético e os bytes finais correspondem ao esperado; não há alegação de que a fixture A intencionalmente trocada permaneceu integralmente imutável. O screenshot real P06 foi aberto pelo revisor e é consistente com o cenário de detalhe B e viewport estreito; essa inspeção não é certificação WCAG, prova de zoom nativo ou prova do host do usuário.

Veredito permanece **PASS_SCOPED, zero findings bloqueantes de código**. O lote de evidências lido confirma as dimensões acima exclusivamente em R1; completion global, browser de produto/P02, Windows normal e SHA documental final ainda exigem os próprios recibos.

### Quarta célula instalada R1 — recebida posteriormente

O artifact **12751594186** trouxe Windows normal (`optimization=0`). O ZIP tem SHA-256 `3d1d7da78f483b6ae67bdab5b53f7e34abd336b1004a7ec6a28495cb28d3f5b0`, igual ao digest informado pelo coordenador; todos os arquivos extraídos correspondem ao ZIP. O recibo e o log pinam R1/tree9f808e84, registram 12 SDK + 74 QA + 36 viewer, **122 casos PASS, zero falhas/erros/skips**, com o mesmo conjunto de IDs das outras três células. Os 22 hashes de origem e os quatro assets também correspondem a R1, e o digest do wheel coincide com seu clean_install. Imports e execução continuam fora do checkout, sem R4, com jsonschema somente como tooling de teste.

Assim, as quatro células Ubuntu/Windows × normal/-O estão sustentadas por recibos R1 diretamente inspecionados. São 122 casos únicos executados em quatro combinações, não 488 casos diferentes. O resumo adicional está em `/tmp/atlas-c1-review-r1-windows-normal.json`. Browser global/P02 e validação do futuro commit documental permanecem separados e ainda pendentes deste parecer.

## Revisão independente R2 — remoção da instalação redundante de fontes

Novo objeto revisado: **`af393e4c0cca19161f49bf9d847bd22617be15fb`**, árvore **`e2a5731d0057f1676e4112d57061773a72e4fc6e`**, pai R1 `df56eb6338626d1671d1882d0d745c02a1f48406`. Veredito de código R2: **PASS_SCOPED, zero findings bloqueantes**.

O revisor leu o commit e seu diff exato: somente duas linhas removidas de `.github/workflows/atlas021.yml`, a atualização apt adicional e a instalação adicional de fonts-noto-cjk/fonts-noto-color-emoji. Nenhum runtime, harness, asserção, timeout, matriz, requisito de fonte ou destino de evidência foi alterado. `git diff --check` passou.

Foi lido o log real do job R1 **122337532297**, run **40546244411**. Ele registra Noto Color Emoji já instalado (linhas 334 e 528), instalação de WQY Zen Hei e IPA Gothic pelo passo Playwright (linhas 442 e 450), início do download adicional fonts-noto-cjk de 61,2 MB (linha 537) e cancelamento ao atingir o limite do job (linha 538). Os três cenários legados e P02 não foram executados nesse job R1; não recebem PASS de outra prova.

A remoção é uma correção de provisionamento sustentada pelo log: a plataforma já dispõe de fontes CJK e emoji e o harness P02 conserva `--require-fonts`, verificação de glifo por fontconfig, hashes da fonte selecionada, seis capturas e os demais controles. Se as fontes efetivamente disponíveis em R2 não cobrirem os glifos, o próprio gate continua falhando. O delta não substitui validação por uma suposição sobre o nome de pacote.

Os resultados executados de R1 permanecem atribuídos a R1. Este parecer de código não os promove a CI R2. A confirmação dos browsers e dos runs globais de R2 e a revisão do futuro SHA documental continuam pendentes de seus recibos específicos.

### Inspeção direta de nove artifacts R2

Foram disponibilizados nove artifacts exclusivos do SHA R2, provenientes dos runs de produto **40549157553** e P06 **40549157548**. O revisor recalculou os digests/tamanhos dos ZIPs, confrontou todos os arquivos extraídos com os bytes dos ZIPs e verificou SHA dos metadados, JSONs e logs. Todos correspondem a `af393e4c0cca19161f49bf9d847bd22617be15fb`; os recibos de suíte/invariância também fixam árvore `e2a5731d0057f1676e4112d57061773a72e4fc6e`. Nenhuma consulta remota nova foi feita pelo revisor.

| Artifact de suíte instalada R2 | Plataforma/modo | Casos únicos | Falhas/erros/skips |
|---|---|---:|---|
| 12754242448 | Ubuntu / normal | 122 | 0/0/0 |
| 12754067621 | Ubuntu / -O | 122 | 0/0/0 |
| 12754226741 | Windows / normal | 122 | 0/0/0 |
| 12755240040 | Windows / -O | 122 | 0/0/0 |

As quatro células têm exatamente o mesmo conjunto de 122 IDs (12 SDK + 74 QA + 36 viewer), três suites OK nos logs, imports externos, ausência de R4 e jsonschema 4.25.1 de teste. Nos nove recibos clean_install, 22 hashes de origem por recibo coincidem com Git R2 e as provas de isolamento/fontes são positivas. Nos oito recibos wheel, quatro assets por recibo coincidem com Git R2 e o digest do wheel corresponde ao clean_install do mesmo artifact. Os quatro recibos P06 de invariância (12755000473, 12754776303, 12754760913 e 12753831935) preservam 64 arquivos, zero erros.

O artifact P06 browser **12754092291** registra 14 checks PASS_SCOPED no SHA R2, Chromium 151.0.7922.34, zero requisições externas/erros de página e a mutação sintética esperada. Seus digests de wheels coincidem com o clean_install do mesmo artifact. O PNG tem SHA-256 `19ee285b685df57a30eae72353372dab2f0e8ddae43a5484305c4fb23235ae8c`.

Resumo verificável dessa inspeção: `/tmp/atlas-c1-review-r2-receipts.json`. As dimensões acima estão confirmadas por evidência R2; completion global e os três cenários browser de produto mais P02 permanecem pendentes enquanto seus recibos não forem recebidos. O veredito de código continua PASS_SCOPED, sem findings bloqueantes.


### Browser global e P02 R2 — evidência completa e inspeção visual

O artifact **12755316139**, run de produto **40549157553**, foi inspecionado diretamente. O ZIP de 8.261.871 bytes tem digest **`efe77cd9e84615d00d25b790b2dc8a8dbb3aa0a405af7cef2a2f2533181821ce`**, igual ao metadado disponibilizado. Todos os 19 arquivos extraídos coincidem com os membros do ZIP. Os três relatos legados fixam `tested_head=af393e4c0cca19161f49bf9d847bd22617be15fb`; P02 fixa o mesmo `code_sha`, e nenhum declara checkout sujo.

| Cenário no SHA R2 | Checks efetivamente PASS | Fontes / execuções | Requisições externas / erros de página |
|---|---:|---:|---:|
| Global normal | 20 | 1 / 4 | 0 / 0 |
| Global adversarial | 24 | 1 / 4 | 0 / 0 |
| Global referências relacionadas | 23 | 2 / 8 | 0 / 0 |
| P06 troca de pacote, artifact 12754092291 já inspecionado | 14 | cenário sintético de troca | 0 / 0 |
| P02 C0 | 23 | 2 / 28 | 0 / 0 |

Esses checks pertencem a jornadas browser e não aumentam a coleção de 122 unittest únicos. O relato normal exercita identidade fonte+ID, quatro detalhes, duas ausências, sete artefatos, 12 relações e uma comparação compatível. O adversarial acrescenta precisão textual acima de 2^53, medições repetidas e incompatibilidades de tipo/unidade. Referências relacionadas cobrem oito detalhes, 22 referências e duas navegações internas, preservando fonte, além do cenário CSS200 explicitamente identificado.

Os 22 hashes de origem do clean_install desse artifact coincidem com os blobs Git R2; os digests dos dois wheels coincidem nos três relatos legados e no clean_install. Os três consumidores declaram viewer/SDK instalados e R4 ausente, e os pacotes sintéticos permanecem byte-idênticos. P02 atesta imports de viewer e SDK fora do checkout, R4 ausente e fontes intactas; os quatro hashes de seus dois pacotes sintéticos também foram comparados diretamente com Git R2 e coincidem.

A jornada P02 registra **Chromium 151.0.7922.34** e **Playwright 1.62.1**. As 23 verificações incluem navegação por snapshot/fonte/ID e histórico, filtros Unicode, ordenação persistida, seleção escondida por filtros, métricas repetidas, unidade/tipo/precisão e ausência, conteúdo adversarial inerte, fallback seguro para snapshot velho/rota inválida, teclado/foco, reflow de 1440/390/320 CSS px e text spacing. As 147 amostras de contraste de texto sobre cores sólidas têm razão mínima observada **4,7432061135**, acima do limiar 4,5 exigido nesse recorte; não representam auditoria WCAG completa.

O `font-provenance.json` externo é idêntico ao objeto incorporado no relato P02. Fontconfig confirma cobertura de CJK U+65E5 em **WenQuanYi Zen Hei**, arquivo `wqy-zenhei.ttc`, SHA-256 `79c18ebe7b811951e8311bad7103ebeae8c337ed9988ea69e8a78a66cfe029b9`; e emoji U+1F9EA em **Unifont Upper**, arquivo `unifont_upper.otf`, SHA-256 `f9a49517cb5a06e02692b403bc21f96ea767128db52f089d31261a8968d3ace8`. Essa evidência demonstra disponibilidade/cobertura da seleção fontconfig; não determina a fonte escolhida por Chromium para cada glifo, nem deve ser reescrita como prova de Noto efetivamente renderizada.

O revisor abriu visualmente **as seis capturas reais P02** e recalculou seus hashes, todos iguais aos declarados:

| Captura | Dimensões | SHA-256 |
|---|---|---|
| c0-overview-1440.png | 1440 × 1000 | `8391475559bed79a9d7f4608af579a1f2a5bd43978489a2abb88f72049edb337` |
| c0-1440.png | 1440 × 9999 | `9739cdf8090e8f453fd7cbbe56e68d2e039e6838e9c7a9b1ac55a4fecdb37b47` |
| c0-390.png | 390 × 13885 | `f4449f80e801c29723283c74bb9e8c3fd62cf2f1c0fe65800d6aa429f0ec85a7` |
| c0-detail-390.png | 390 × 1000 | `fe02a03aeef11358bbe93fefba9b508d253c617a39d116f7ea9808d12c668b4a` |
| c0-320.png | 320 × 14489 | `03458492be7c6a06e4b12b91e852be2aef0ccb2b92033aad2b24859b10ca6229` |
| c0-320-text-spacing.png | 320 × 16137 | `683099fb7dfc442865bc68e4c732fb8de0053ce2de24fa0560bf17d5f8243e9d` |

A inspeção mostra estrutura consistente no overview e reflow geral nas capturas compridas. O close-up de detalhe390 apresenta japonês, grego e emoji visíveis, quebra do título sintético longo sem espaços, controle de fechar e estados PARTIAL, REJECTED e SINTÉTICO separados. Não foi encontrado bloqueio visual. A geometria de overflow e o comportamento de teclado/foco são sustentados pelas asserções executadas do harness; a leitura das imagens não substitui essas provas nem certifica todos os detalhes de uma página longa.

Nos quatro relatos de produto, `native_zoom=NOT_RUN` e `wcag_certification=false`. `css_zoom_used=false` em P02, normal e adversarial; **true somente no cenário legado de referências relacionadas**, que registra explicitamente CSS200. Nenhum teste do host do usuário foi executado ou alegado pelo revisor.

O resumo independente está em `/tmp/atlas-c1-review-r2-browser.json`. **Veredito R2 de código e evidências examinadas: PASS_SCOPED, zero findings bloqueantes abertos.** Os três workflows success foram comunicados pelo coordenador; o revisor validou diretamente os artifacts atribuídos e não fez nova consulta remota. A futura revisão documental/CI do SHA que contém o handoff permanece independente: os resultados R2 não são transferidos para outro commit.

## Vinculação da publicação documental

Este arquivo transcreve o parecer nativo atribuído; o coordenador não se apresenta como revisor independente. O próprio commit que o contém requer leitura independente por SHA e nova CI; esse recibo é publicado externamente na PR #11 após a criação do objeto, para não fabricar auto-referência ou transferir CI de outro SHA.
