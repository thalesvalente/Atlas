# ATLAS-PARITY-03-C2 — qualificação real dos componentes P03

**Resultado do código fixado:** `C2_P03_QUALIFIED_FOR_COMPOSITION`.
**Código qualificado:** `dc43653d4e06c1f5500437a42b2fb9e2df426dd6`.
**Árvore:** `0dd3331f1f873a634f286fdfdb703c1a76a87406`.
**Entrega:** [PR Draft #10](https://github.com/thalesvalente/Atlas/pull/10),
branch `qa/atlas-parity03-c2-p03-gates-20261027`.

`VISIBLE_IN_MAIN_APP=false`. `REASONING_EFFECTIVE=UNVERIFIED`.
Data: 27/10/2026, America/Fortaleza.

Esta qualificação cobre os componentes P03 em um harness explícito e isolado.
O commit que contém este documento é posterior ao código: **seus próprios CI e
parecer são registrados pelo SHA exato no fechamento da PR #10 e na conversa**.
Não há transferência automática dos resultados abaixo para outro SHA. Essa
separação evita inserir o SHA de um commit dentro dos próprios bytes.

## Entradas e preservação

| Objeto | Identidade |
|---|---|
| Código/harness P03 | `6c412c36e1dbe11711daa15c6d8727fbe94fa0ad` |
| Árvore do código | `f9cac8cba86763c2ff98f883e33962648fc01004` |
| Handoff da PR Draft #7 | `ead1f753f52f22035326b7366dd2231c62775765` |
| Árvore do handoff | `624c1ad386666ed2db046a05b0a66530a5ee24c1` |
| Manifesto P03 SHA-256 | `10e6142468aabdd6e8454665207fd8050ff4f64d6b3dcfd9cde81d699ac71e77` |

Os **25 arquivos congelados**, as **56 entradas do manifesto original** e os
**219 arquivos herdados** permanecem idênticos. Nenhum componente original precisou
mudar. Os novos scripts, workflow e documentos ficam no ownership C2.

Permanecem intactos protocolo/contexto/schema/versão, shell, catálogo, servidor,
package-data, workflows globais, outras frentes e ponteiro global de feature.
ARC-01–09 e a independência do Caderno foram preservados. A direção aceita da
ADR-0002 foi reconhecida, sem inferir novas autorizações.

## Gates portáveis executados no código qualificado

| Gate | Linux normal | Linux `-O` | Windows normal | Windows `-O` |
|---|---:|---:|---:|---:|
| Métodos SDK + P03 coletados/executados | 47/47 | 47/47 | 47/47 | 47/47 |
| Skips, erros e falhas | 0 | 0 | 0 | 0 |
| Build setuptools 80.9.0 | PASS | PASS | PASS | PASS |
| Módulos/recursos do wheel comparados por blob | 22 | 22 | 22 | 22 |
| SDK/viewer instalados fora do checkout | PASS | PASS | PASS | PASS |
| Verificações HTTP reais | 47 PASS | 47 PASS | 47 PASS | 47 PASS |

São 12 métodos SDK e 35 P03. O teste antes pulado,
`test_sdk.ContractAndRoundTrip.test_profile_schema_matches_positive_fixture`,
passou com `jsonschema==4.25.1` test-only. A mesma coleção foi repetida em quatro
configurações; não são 188 testes únicos. Wrappers Python invocam subtestes Node,
que também não são somados novamente.

Build usa setuptools 80.9.0, build 1.3.0 e wheel 0.45.1 já fixados no produto/CI.
Os wheels são construídos de cópias sem acesso ao índice; todos os módulos/assets
conferem com os blobs Git. SDK sozinho e viewer com SDK instalam em dois venvs
novos externos, com `-I`, propagação de `-O`, ausência de R4 e do checkout em
`sys.path`. Fontes, fixture e modelo projetado não mudam.

O HTTP usa socket real em `127.0.0.1` no runner, oito rotas exatas, MIME/CSP,
nosniff e no-store. Negativas incluem wildcard, traversal simples/codificado/duplo,
aliases, query/fragmento, URI absoluta, payload, rota desconhecida, métodos,
Host/Origin, Host duplicado, GET com corpo e Transfer-Encoding. Audit guard Python
admite somente IPs loopback, sem mudar firewall, ACL ou política do host.

## Navegador real focal

| Ambiente | Browser existente | Checks | Screenshots |
|---|---|---:|---:|
| Linux | Chrome/Chromium 156.0.8078.47 | 19/19 PASS | 6 |
| Windows | Chrome/Chromium 156.0.8078.48 | 19/19 PASS | 6 |

Node 24 e Playwright 1.62.1 dirigiram o Chromium já instalado; o workflow focal
não baixou navegador. Os checks cobrem:

- Tabela/caption/cabeçalhos de linha e coluna; identidade preservada.
- Transporte, ordenação e filtro tipados: strings lexicais, grandes inteiros,
  decimais, booleanos reais e rejeição de tipos indevidos.
- Null, omissão, string vazia e motivo; tipo, unidade e precisão declarados.
- File como artefato, mentions neutra e disponibilidade/digests/ciência separados.
- Produto/documento sintéticos, incluindo rejeição de synthetic=false.
- Teclado, Tab, foco visível e saída; 1440,390 e 320 CSS px.
- Tabela máxima de 1.000 × 20, scroll horizontal e vertical por teclado, ambos contidos.
- Text spacing em 320px, sem perda de texto ou clipping observado.
- HTML, texto, URI e identidade hostis inertes.
- Zero erros de página/console, requests externos, WebSockets ou rotas locais
  desconhecidas no contexto observado; fontes/fixtures preservadas.

**Zoom nativo real200%: NOT_RUN.** O controlador disponível não comprova essa
operação. CSS zoom, deviceScaleFactor e CDP page scale não foram usados como
substitutos. Trata-se da limitação condicional explicitamente permitida na missão,
separada de skips de testes coletados.

A observação de rede cobre requests/WebSockets do contexto Playwright, com service
workers bloqueados; não captura tráfego background de todo Chromium. A instalação
prévia de ferramentas também não é declarada livre de rede.

## RED encontrado e resolvido

O SHA inicial `97151e0e17c3d8afc70aad91a5c488cd831eb171`, run
[40546112894](https://github.com/thalesvalente/Atlas/actions/runs/40546112894),
falhou nos dois browsers em 320px, após 13 checks PASS. A largura intrínseca de um
select expandia o grid do label: no Linux, a página media 337px para viewport de 320px;
a tabela já estava contida entre x=31 e x=289.

A correção alterou somente a nova CSS do harness: `minmax(0,1fr)`,
`min-inline-size:0`, select limitado ao container e checkbox com quebra de linha.
Nenhum hidden/clip, componente congelado ou oráculo foi alterado. A revisão
independente examinou causa, patch e screenshots. A execução integral no SHA
qualificado comprovou largura externa de 320px e 19/19 checks nos dois sistemas.
Ver `RED-AND-CORRECTION.json`.

## CI, revisão e artefatos

| Workflow no SHA dc43653d… | Run | Resultado |
|---|---|---|
| P03 isolated qualification | [40546494721](https://github.com/thalesvalente/Atlas/actions/runs/40546494721) | completed/success; 8/8 jobs |
| Produto ATLAS021 | [40546494687](https://github.com/thalesvalente/Atlas/actions/runs/40546494687) | completed/success |
| Spec Kit global | [40546494736](https://github.com/thalesvalente/Atlas/actions/runs/40546494736) | completed/success |

Spec Kit 1.2.3 teve CLI, integração e helpers reais no subworkstream C2,
Linux/Windows, com SPECIFY_FEATURE_NO_PERSIST=1. Redação/análise manual é
distinguida de comandos executados em `SPEC-KIT-METHOD.json`.

Três agentes nativos reais: /root/packaging_http, /root/browser_semantics e
/root/independent_review. O terceiro não tem autoria no delta. Parecer do código:
`PASS_SCOPED_CODE_REVIEW`, zero findings bloqueantes. Nenhum parecer representa
aprovação humana, científica ou de merge.

Oito ZIPs Actions, recibos de JOB-SUMMARY e 12 PNGs tiveram hashes conferidos.
`ARTIFACT-INDEX.json` registra IDs, links, SHA-256 e expiração, com retenção de 30 dias.
Os JSONs consolidados permanecem versionados. `MANIFEST.sha256` cobre arquivos
C2 e exclui a si próprio.

## Handoff para composição

Consumir os 25 arquivos P03 vinculados aos inputs e esta qualificação. A entrega
mantém `VISIBLE_IN_MAIN_APP=false` e `main_server_assets_qualified=false`.
File/mentions conservam semântica; demonstradores não viram capacidades nativas.

A mesma contenção vertical exige embedding explícito: o harness usa
`max-block-size:min(60vh,28rem)`. A correção dos controles pertence ao harness.
O verificador C2 exige o snapshot de 219 arquivos; não é gate genérico para uma
árvore C1 composta.

**Menor próximo ato:** compor em candidata autorizada separada e executar seu
HTTP/browser no próprio SHA. Sem promoção de gate focal a browser global, merge,
release, deploy, promoção canônica, extensão de protocolo ou aprovação científica.
