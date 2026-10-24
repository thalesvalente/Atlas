# ATLAS021 — revisão independente da candidata pública

**Data:** 24/10/2026. **Revisor:** agente nativo A4, distinto dos autores do SDK (A1) e da interface (ORQ/A2). **Versão:** `0.1.0a1`. **Parecer:** `PASS_SCOPED` para o conjunto de fontes identificado por hashes no [recibo de verificação](A4-local-verification.json).

Este parecer cobre a candidata técnica e suas fronteiras. O aceite humano da ADR-0002, a promoção canônica, release, migração e retirada continuam separados. A revisão local não substitui CI nem Codex no SHA publicado.

**Atualização posterior:** o Codex encontrou um P2 de descompressão no SHA então publicado. O adendo abaixo registra a reprodução independente, a variante LZMA e a correção local verificada. Os resultados originais mantêm seus hashes e alcance; a conclusão remota depende do novo SHA.

## Resultado e escopo

Foram construídos wheels a partir de cópias do código e instalados em dois ambientes novos, fora da árvore de fontes. O primeiro contém somente o SDK; nele a interface e qualquer produtor legado estão ausentes. O segundo contém SDK e interface, sem o produtor legado. Os comandos foram executados com isolamento Python (`-I`) e sem `PYTHONPATH` de produto.

A fonte ambiental foi gerada pelo exportador independente real, com quatro execuções declaradamente sintéticas. O Atlas instalado apresentou os registros parseados, filtros, detalhe, comparação, timeline, linhagem, fontes e dossiê. A reconstrução do índice manteve o conteúdo e os bytes da fonte. A interface recebeu apenas fontes explicitamente indicadas.

A inspeção do runtime e a auditoria AST não encontraram importações do produtor legado, dependência SDK→UI, execução de processos pelo viewer ou comandos de migração/retirada. A validação semântica está no SDK. O modelo da UI e seus índices são derivados; preferências são locais ao navegador.

| Verificação executada por A4 | Resultado | Alcance |
|---|---|---|
| Testes independentes de arquitetura e conformidade | **41 PASS normal e 41 PASS `-O`**, sem skips | SDK instalado; exportador real; contratos positivos e negativos |
| Instalação limpa e CLI | **PASS** | SDK sem UI/produtor; viewer sem produtor; inspect/dossier/rebuild; fonte intacta |
| Browser adversarial no wheel final | **21 verificações PASS** | Chromium 151.0.7922.34, Playwright 1.62.1; desktop 1440px e mobile 390px |
| Auditoria AST do runtime | **PASS_SCOPED**, nenhum achado | Importações diretas e helpers locais, imports dinâmicos literais, metadata de dependências |
| Precisão no viewer instalado com `-O` | **PASS** | Inteiro 9007199254740993 preservado no modelo textual e no JSON do dossiê |

A suíte independente cobre contexto/versão desconhecidos, IDs duplicados, relações ausentes/cíclicas, tipos/unidades, UNKNOWN/HOLD, sintético, timestamps, JSON duplicado/não finito, precisão decimal, integridade adulterada, payload ausente, ausência de rede, traversal, ZIP inseguro, symlink e orçamento agregado. Há oito testes adversariais do próprio detector de arquitetura: eles demonstram que violações conhecidas não produzem PASS vazio.

O navegador exercitou a aplicação instalada sobre dados parseados. Os testes incluíram teclado, foco visível, nomes de controles, filtros, comparação, dossiê baixado, Host/Origin, allowlist de fontes e bloqueio de métodos mutantes. Não houve erro JavaScript nem requisição externa durante as verificações. [Captura desktop](../verification/desktop.png) e [captura mobile](../verification/mobile.png) mostram a baseline visual sintética; o recibo final adicional cobre a correção de precisão sem mudança estética.

## Achados acionáveis resolvidos

- **SDK:** URI malformada podia escapar como exceção e o orçamento de leitura precisava valer também para o total de payloads em diretório. O autor corrigiu ambos; os negativos independentes passaram.
- **Comparação:** métricas distintas com a mesma identidade/tipo/unidade eram sobrescritas dentro de um run. A interface passou a manter os múltiplos IDs/valores. O browser verificou 24.5 e 999.25 simultaneamente, além de unidade incompatível apresentada separadamente.
- **Precisão:** a revisão coordenada identificou risco de arredondamento de decimais na importação e inteiros no JavaScript. O SDK rejeita decimais cuja representação suportada perderia valor. A UI usa `display_value` textual, preservando o valor tipado no servidor, e baixa os bytes do dossiê sem reserializar números no navegador. O teste independente exigiu o inteiro **9007199254740993** exato no detalhe, na comparação e no token numérico do JSON bruto exportado.
- **Requisitos:** a divergência inicial sobre ZIP foi resolvida antes da implementação UI: leitura limitada em memória, sem extração. Aceitar a extensão `.eln` não declara conformidade com o perfil ELN.

Os testes não mudaram o resultado esperado para ocultar falhas. A fixture positiva ambiental foi conciliada com a validação upstream; o caso de payload ausente agora é produzido removendo um arquivo de uma cópia temporária sintética.

## Protocolo, evidência externa e limites

A4 leu a pesquisa, a ADR-0002, o manifesto e os recibos externos produzidos por A1. A validação de referência é declarada como checks REQUIRED de base RO-Crate, com skips explícitos de disponibilidade externa; não é certificação integral de Process Run 0.6, Caderno, ELN ou ciência. A igualdade comparativa de campos entre candidatos não é identidade de grafo RDF nem de bytes. O exemplo oficial que falha permanece registrado como negativo esperado, sem reescrever a fonte para obter aprovação.

A redução dos estados genéricos `actionStatus` é explícita; o estado exato do candidato fica em `cp:executionStatus`. O perfil e sua implementação são pré-release. Digest prova bytes observados, não autoria, data autêntica ou aceite científico.

A revisão e os ensaios do adaptador legado permanecem exclusivamente no repositório privado do produtor. O harness público genérico foi reutilizado em sua prova de dois produtores, sem trazer código, corpus, caminhos ou digests privados ao Atlas. Nenhuma transferência privada→pública é concedida por este parecer.

As verificações locais foram realizadas em Linux. Windows depende da matriz CI correspondente. O teste mobile usa viewport real de navegador, sem alegar ensaio em aparelho físico. A auditoria AST é uma verificação de fronteiras conhecida, não prova formal de todo comportamento dinâmico. A leitura segura não qualifica um host adversarial nem elimina todas as corridas possíveis de filesystem.

## Conclusão para integração

Não permanece achado de arquitetura aberto no conjunto local revisado. É adequado publicar a candidata como Draft, com a proposta de protocolo e os limites acima. O integrador deve conferir os hashes de fonte do recibo contra sua árvore final e vincular CI/Codex ao SHA publicado. A declaração de `A5 CI_REVIEW_EXACT_PASS` exige esses resultados reais. `A1 PROTOCOL_DECISION_ACCEPTED` e `A7 CANONICAL_PROMOTION_APPROVED` exigem as decisões humanas respectivas; nenhum teste desta revisão as substitui.

## Adendo — erros de descompressão, 24/10/2026

O [review Codex no SHA `6da9f056b21952072e385e54d2877ebea956b244`](https://github.com/thalesvalente/Atlas/pull/1#discussion_r4367903804) identificou um **P2**: dados DEFLATE corrompidos faziam `zlib.error` escapar do leitor e interromper o catálogo, inclusive quando outra fonte era válida. A4 reproduziu a falha em metadados e payload no wheel anterior. Na mesma fronteira, confirmou a variante de ZIP LZMA corrompido, com `LZMAError` não tratado.

A1 corrigiu as duas fronteiras em `ee02bd10a94fdd088244321e36cc03315c244663` e `39cf6e4fbbf7cc66ae37de22dd867810fd91512e`. A revisão independente confirmou capturas específicas dos erros, com importação opcional do codec LZMA. Não há captura genérica de todas as exceções nem alteração do perfil. O arquivo `storage.py` revisado possui SHA-256 `1d2cabaf39e8b38815daed37e515a0e52cdc8d4b37a1e0110522b1d0149f5a67`.

As duas novas regressões independentes criam ZIPs válidos pelo exportador ambiental, corrompem os bytes comprimidos e comprovam que o decoder real falha antes de testar o contrato do SDK. São **quatro casos concretos** — metadados e payload, cada um com DEFLATE e LZMA — executados em modo normal e `-O`, sem skips neste ambiente. Todos falham no wheel anterior e passam no código corrigido. O LZMA recebe skip explícito somente se o Python não possuir esse codec opcional.

Metadados ilegíveis passam a produzir `SOURCE_INVALID`; payload ilegível produz `UNAVAILABLE` e `PAYLOAD_UNAVAILABLE`, preservando os quatro registros e os outros anexos legíveis. A4 também executou os quatro cenários no viewer já instalado, selecionando explicitamente o SDK corrigido por caminho de fonte: `snapshot`, dossiê e reconstrução mantiveram a fonte boa e localizaram o diagnóstico na fonte danificada. Os ZIPs e a fonte original permaneceram byte a byte intactos. Isso é um ensaio focal de integração com o código corrigido, sem alegar nova instalação limpa ou novo browser.

O [recibo complementar](A4-decompression-review.json) preserva a identidade do código e o alcance dos ensaios. O [recibo anterior](A4-local-verification.json), os wheels e as capturas anteriores permanecem históricos, com seus hashes originais. A4 considera o reparo **`PASS_SCOPED` local**. A5 permanece pendente de CI e conclusão efetiva do Codex no próximo SHA publicado; este adendo não resolve a conversa remota nem concede os gates humanos A1/A7.
