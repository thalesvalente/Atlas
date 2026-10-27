# Contrato de integração — P03 → P06

## Identidade exata da entrega

| Referência | SHA |
|---|---|
| Código e harness testados | `6c412c36e1dbe11711daa15c6d8727fbe94fa0ad` |
| Árvore do código | `f9cac8cba86763c2ff98f883e33962648fc01004` |
| Baseline | `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5` |
| Árvore-base | `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59` |
| Congelamento de 25 arquivos | SHA-256 `5d656a75e89cf2834f3217724b8014bd75aa8dda1d162ba3ecd0f6b4df377d43` |

PR Draft [#7](https://github.com/thalesvalente/Atlas/pull/7), branch
`work/atlas-parity02-p03-components-20261027`. Este contrato está em commit documental
posterior ao código. Resolver seu SHA pelo commit que contém este arquivo; não inserimos
o SHA do próprio commit dentro dele. `evidence/CODE-BINDING.json` liga os mesmos 25 hashes
revisados/testados aos blobs do commit de código e comprova identidade com a árvore publicada.

**Estado:** P03_COMPONENTS_VERIFIED_NOT_COMPOSED. **VISIBLE_IN_MAIN_APP=false.**
Composição pertence a P06 em candidata separada, respeitando o ownership do shell de P02.
P03 não importou branches em movimento de P01/P02 nem depende de decisão futura para existir.

## Entradas, dependências e limites

Contratos completos em COMPONENT-API.md. Python >=3.11 e biblioteca padrão; JavaScript ES
modules/BigInt/DOM, sem biblioteca de runtime. Node 24 é dependência dos testes; Playwright
com Chromium existente é dependência opcional do gate de navegador, não dos componentes.

- Tabela: descritor p03-table/1, semântica candidata explícita, até 1000 linhas/32 colunas/
  20000 células, limites de texto/número adicionais. Não é parser de CSV ou formato persistido.
- Metadados: project_metadata(read_model, source_key, entity_ids opcional), somente projeção
  existente validada. Não fornece acesso a arquivos, carrier, produtor ou rede.
- Produto/documento rico: p03-candidate/1 com synthetic=true e semantic_kind explícito.
  Estes componentes continuam demonstradores. Nenhum File atual recebe esse papel por dedução.
- Renderers devolvem elementos desconectados; chamador controla montagem e ciclo de vida.
- Erros têm code/path e devem aparecer como falhas de apresentação sem invalidar/reescrever fontes.
- Origem, disponibilidade, integridade e ciência permanecem eixos distintos; um descritor
  fornecido por alguém não autentica esse alguém.

## Pontos mínimos de composição por P06/P02

| Área de ownership P02 | Alteração mínima a considerar na candidata integradora |
|---|---|
| static/index.html ou shell sucessor | Carregar os dois CSS e reservar região semântica; não ativar demonstradores como capacidades nativas. |
| static/app.js ou módulo de composição | Importar os ES modules explicitamente e chamar renderers ao selecionar a fonte, mantendo controles/foco e retirando DOM anterior. |
| server.py:ASSETS | Acrescentar somente as quatro rotas JS/CSS nomeadas; manter allowlist, MIME e CSP. Nunca servir diretórios/payloads por wildcard. |
| catalog.py ou projeção de apresentação escolhida por P02 | Chamar project_metadata com read_model já validado e identidade explícita da fonte/snapshot; capturar MetadataError de modo visível. |
| packages/atlas/pyproject.toml | Nenhuma mudança necessária na baseline: static/*.js e static/*.css incluem os assets imediatos. Reconfirmar no wheel composto. |
| Testes/CI sob ownership P06 | Garantir Node 24 nos jobs que descobrem os wrappers e executar gates HTTP/browser reais da composição. |

Não alterar packages/protocol, contexto/schema/versão, exportador ou leitor de carrier.
A API pode ser composta usando uma projeção descartável do catálogo; sua forma não vira
contrato persistido obrigatório do Caderno.

### Transporte tipado e identidade

O catálogo atual já executa presentation_values() antes de JSON. Ao mapear métricas ou
parâmetros explicitamente escolhidos para a tabela candidata, reutilizar display_value
para números e strings. **Booleanos permanecem booleanos reais:** display_value contém
"false"/"true", que não são booleanos admitidos. Null/valor omitido permanece ausente com
motivo declarado. `number` do perfil pode ser mapeado explicitamente para `decimal` da
apresentação, sem mudar cp:valueType persistido. Não agrupar medidas de unidades distintas
como se fossem comparáveis nem calcular conversão silenciosa.

A identidade da linha é local ao descritor. P06 precisa manter a chave de fonte/snapshot
do shell e o ID declarado. Se compuser múltiplos snapshots da mesma fonte, deve distingui-los
explicitamente; não concatenar campos de maneira ambígua nem promover digest a autenticação.

## Exemplos representáveis hoje

1. `load_package` + `to_read_model` do exemplo público ambiental: quatro itens projetados
   no smoke instalado, sem R4 e sem alteração dos bytes da fonte.
2. Entidades File/referências declaradas com nome, tipo, descrição, formato, disponibilidade
   e digests; `report.pdf` continua File, sem rótulo documento rico.
3. Mentions em lista neutra, distintas de object/result/wasDerivedFrom.
4. Lista de PropertyValue já declarada pode ganhar apresentação tabular por mapeamento
   explícito do integrador; não comprova tabela genérica persistida.

Fixtures adversariais são sintéticas. Digests repetidos nas fixtures modelam estados
para testar apresentação; não são resultados de download ou inspeção de dados privados.

## Testes exigidos para a composição

- Conferir SHA e hashes, rodar testes focais e regressão sobre o SHA composto.
- Conferir wheel instalado, recursos HTTP permitidos e bloqueio das demais rotas.
- Testar dois pacotes com mesmo @id, reconstrução do índice e mudança de snapshot.
- Verificar números grandes antes de JSON, booleanos reais, null/ausência e unidades.
- Verificar que File/mentions não ganham semântica de produto/produção e que os eixos de
  estado permanecem separados.
- Executar browser real: tabela semântica, teclado/foco, overflow só no componente,
  largura 390, ampliação 200%, texto hostil e nenhuma requisição externa.
- Preservar fontes byte a byte; nenhum import de produtor ou ativação implícita.

Nesta execução: prova offline/DOM recorder PASS_SCOPED, **HTTP com socket e browser NOT_RUN**.
O sandbox recusou sockets; Chromium não está presente. Não há alegação de Windows, layout,
paridade legado ou integração. Estudo/P01 ausentes permanecem entradas a reconciliar.

## Próximo ato mínimo

P06 deve receber o commit de código e o commit documental da PR #7, conferir os manifests
e compor em sua candidata separada com os pontos P02 acima. Executar HTTP/browser num
ambiente já autorizado/capaz e vincular resultados ao SHA composto. Apenas depois disso pode
avaliar VISIBLE_IN_MAIN_APP; não existe autorização de merge/release nesta entrega.
