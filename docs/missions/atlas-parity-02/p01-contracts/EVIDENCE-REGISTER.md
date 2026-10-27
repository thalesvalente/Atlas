# Registro de evidências — ATLAS-PARITY-02-P01

**Natureza:** registro autoral desta frente, baseado em fontes públicas fixadas e inventário sanitizado das entradas. **Base:** `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`; árvore `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`. **Responsável pela arqueologia:** subagente nativo `/root/archaeology`. Nenhum estudo A/B/C/D integral foi identificado para reutilização; o trabalho de C0 continua apoiado no contrato e no código público.

O inventário legível por máquina está em [INPUT-INVENTORY.json](INPUT-INVENTORY.json). Seus hashes permitem conferir bytes. Eles não autenticam autoria, data, permissão ou aceite científico.

## 1. Baseline e método de leitura

**E001 — FATO OBSERVADO:** o preflight do coordenador confirmou `main` no SHA da missão, sem sucessor naquele momento: [commit da baseline](https://github.com/thalesvalente/Atlas/commit/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5). A listagem pública inicial apresentou cinco branches históricas/main e nenhuma PR aberta. A árvore não continha `specs/004-*`; não havia colisão de feature observável nessa base.

A clonagem pelo terminal falhou por indisponibilidade da conexão. O coordenador materializou o snapshot pelo conector GitHub e verificou os 162 blobs por hash Git/tamanho, a árvore e o objeto de commit exato. O checkout local é shallow; não se afirma possuir o histórico integral. Esta frente leu os arquivos fixados, sem examinar outras conversas, host do operador ou diretórios privados.

A observação final de remoto e o SHA documental pertencem ao handoff do coordenador. Um novo estado remoto não altera retroativamente esta baseline nem as evidências aqui atribuídas.

## 2. Estudos anteriores: disponibilidade real

| Entrada | Bytes integrais | Autor/origem e versão observáveis | Hash | Decisões importadas |
|---|---|---|---|---|
| A | `INPUT_MISSING` | Nome citado na missão; autor e versão desconhecidos | Não fornecido e não calculado | Nenhuma |
| B | `INPUT_MISSING` | Nome citado na missão; autor e versão desconhecidos | Não fornecido e não calculado | Nenhuma |
| C — estudo | `INPUT_MISSING` | Resumo relatado pela missão; autor e versão do estudo desconhecidos | Esperado `f8d274ffe5ac043005b2c27779286638a86c7c2aff3e30ee64a4497b434b110b`; **não verificado** | Nenhuma; não foram importados requisitos C-UX |
| C — handoff | `INPUT_MISSING` | Nome/hash relatados pela missão; autor e versão desconhecidos | Esperado `e8c7b1b3a8eb0a276d94e98f94b9d1477e555d305ebee62d99ec48ee93f5650e`; **não verificado** | Nenhuma |
| D | `INPUT_MISSING` | Nome citado na missão; autor e versão desconhecidos | Não fornecido e não calculado | Nenhuma |

**I001 — fonte da instrução:** anexo de missão recebido, 11.639 bytes, SHA-256 `06504e440516bc84659d3343c8f0795eefb112aeb85d5797dac6d9632b3adec8`. O anexo não foi transferido para o repositório. Seu resumo de C relata C0 sem mudança de protocolo, doze jornadas e contratos de apresentação. Isso é **relato de resumo**, não leitura do estudo, aprovação nem catálogo recuperado de jornadas. As jornadas e contratos deste pacote são análises novas rastreadas às fontes públicas.

A busca delimitada foi feita uma vez: dois anexos textuais e seis archives, com 10.771 nomes de entradas inspecionados (10.747 em ZIP, 24 em 7z). Nenhum nome correspondente a ATLAS-PARITY-01 ou aos estudos/handoffs A–D foi localizado. As referências no próprio prompt não são arquivos de estudo. A listagem de 7z usou `libarchive` já disponível, sem instalação ou extração. Não foram reutilizados bytes de código privado.

**Limite da busca:** ausência de estudo identificado nesse universo não prova inexistência global nem exclui conteúdo com nome não reconhecível ou arquivo aninhado. Os nomes/hashes dos archives sem relevância pública foram omitidos. `docs/coordination/A-DATA-REQUIREMENTS.md` e a antiga coordenação A/B são artefatos de outra missão; seus nomes não os tornam estudos A/B de ATLAS-PARITY-01.

## 3. Precedência dos recibos e divergências

**E006 — recibo posterior:** [PR #5, comentário 6406839421](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421), autor observado `thalesvalente`, publicado/atualizado em `2026-10-26T02:24:54Z` (`2026-10-25T23:24:54-03:00`). Corpo UTF-8 observado: 8.227 bytes; SHA-256 `52f6b013ddedeb17bb98a0acfa10f84f98b08d3789486cf766e96cf8783cefde`. O digest exclui HTML e envelope da API; não substitui a atribuição do próprio GitHub.

O recibo e a mensagem do merge registram o aceite de **ADR-0002 v1.0 em `e985ea3124b7a3cd241ee2dbc88b5ad50688373c` como direção de estabilização**. Os estados históricos `PENDING_HUMAN` da constituição, ADR, perfil, manifesto e features antecedem esse recibo. Permanecem preservados byte a byte. Não cabe pedir novamente o mesmo aceite nem descrever a direção como ainda sem decisão.

| Dimensão | Evidência prevalente | Conclusão restrita |
|---|---|---|
| Arquitetura ARC-01–09 | E003/E004 + missão atual | Preservar independência; decisão técnica compatível continua delegada |
| Escolha ADR-0002 v1.0 | E006 posterior + mensagem do merge E001 | Direção de estabilização aceita na versão fixada |
| Bytes persistidos do Caderno | E014/E016 fixados na baseline | Não alterados por esta campanha; o rótulo histórico não reescreve o recibo |
| Release estável / promoção / ciência | Limites expressos em E006 | Nenhuma autorização nova é derivada desse aceite |
| Especificação de apresentação P01 | Autoria desta frente e missão atual | Candidata revisável; não é norma aprovada por outra frente |
| CI e piloto prévios | Relatos atribuídos em E006 | Provas históricas, com SHA e ambiente próprios; não contam como testes novos |

**Divergência de apresentação observável:** `catalog.py:17` ainda contém a mensagem genérica de que a estabilização depende de aceite humano. É texto histórico de runtime, não recibo de revogação. Uma correção compatível de rótulo deve distinguir a direção já aceita das etapas de estabilização/publicação ainda abertas, sob ownership de produto P02. P01 registra o gap e preserva o arquivo.

## 4. Fontes públicas lidas e fixadas

Todas as URLs abaixo fixam o SHA `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`. `READ_FULL` significa texto integral examinado; `READ_TARGETED` limita a leitura às partes pertinentes; recursos marcados apenas por hash tiveram bytes disponíveis, sem alegação de auditoria semântica integral. Conferência dos arquivos não é execução de teste.

| Evidência | Fonte e finalidade | Escopo de inspeção | SHA-256 |
|---|---|---|---|
| E002 | [AGENTS.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/AGENTS.md) — Instruções de contribuição | `READ_FULL` | `83c362467736d67364342fdd0777bd8de171755ffb676ad38a5b0f000b89eb1e` |
| E003 | [.specify/memory/constitution.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/.specify/memory/constitution.md) — Constituição ARC-01–09 | `READ_FULL` | `5792e1cf6aec64bd2409867ce14139ce7bfcbf11c20226871a3f85dd7a8e913b` |
| E004 | [docs/architecture/ADR-0001-atlas-protocol-producers-storage.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/architecture/ADR-0001-atlas-protocol-producers-storage.md) — Separação Atlas/Caderno/produtores/armazenamento | `READ_FULL` | `5f9a44e6b773bad819a33bef32a6e5ab34694fa4d9760624f94587c7f17bb662` |
| E005 | [docs/architecture/ADR-0002-protocol-candidate.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/architecture/ADR-0002-protocol-candidate.md) — Proposta histórica ADR-0002 v1.0 | `READ_FULL` | `67a539e23d5d369f5e242069a29d9ea8d05315ee82b4e23faaa68dea0a27bac8` |
| E007 | [specs/001-atlas021-protocol-interface/spec.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/001-atlas021-protocol-interface/spec.md) — Feature 001: requisitos, interface e read model | `READ_FULL` | `8b3edcff89de737cfaf330824d9013fbc5eb2023959c224b37a5c6399475eae3` |
| E007 | [specs/001-atlas021-protocol-interface/contracts/interface.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/001-atlas021-protocol-interface/contracts/interface.md) — Feature 001: requisitos, interface e read model | `READ_FULL` | `9048be669ccb08af12a922d3bf8712c72e53ae1b825a908f75c7aab026027633` |
| E007 | [specs/001-atlas021-protocol-interface/data-model.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/001-atlas021-protocol-interface/data-model.md) — Feature 001: requisitos, interface e read model | `READ_FULL` | `e53b403b6739e61670ba89d6811f1e36023679b4cc201f72704a4b8a85d4190f` |
| E008 | [specs/002-atlas021-poc-r4/spec.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/002-atlas021-poc-r4/spec.md) — Feature 002: transporte, perdas e demonstração | `READ_FULL` | `67aca7d9b069874cb60a4b2b8b1be2ef0795eb7641c7b02d8a66abfb2778bc5b` |
| E008 | [specs/002-atlas021-poc-r4/contracts/demo.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/002-atlas021-poc-r4/contracts/demo.md) — Feature 002: transporte, perdas e demonstração | `READ_FULL` | `9be83bc47ebb3b0d729438774e037650761bb1988e04d42d90a462e02be41ab9` |
| E009 | [specs/003-producer-selective-preview/contracts/reader.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/contracts/reader.md) — Contrato público de consumo 003 | `READ_FULL` | `13e5ebfd680d7cb29cbe61e748077b9e767f8b4666c167bb4c6ec4cf5e564fba` |
| E010 | [packages/protocol/src/caderno_protocol/read_model.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/read_model.py) — Projeção pública descartável | `READ_FULL` | `d312dbb04fa9f9a69ac5383fb94f3f570f0ea4eb2020d44f9a8e1d7a28e36013` |
| E011 | [packages/protocol/src/caderno_protocol/model.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/model.py) — Validador vigente: referências, tipos, estados e tempos | `READ_TARGETED` | `4803f211c9db0713ffe067e6b4b3223b4af6c87e7ab499e53b908f59a8556ed6` |
| E011 | [packages/protocol/src/caderno_protocol/storage.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/storage.py) — Validador vigente: referências, tipos, estados e tempos | `READ_TARGETED` | `1d2cabaf39e8b38815daed37e515a0e52cdc8d4b37a1e0110522b1d0149f5a67` |
| E012 | [packages/atlas/src/atlas_viewer/catalog.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/catalog.py) — Catálogo: fontes ordinais, observações e contagens | `READ_FULL` | `2afcf20bb5f7a7270367afa9547495b77ff65ae0e626986bee65ff2b0323d0c3` |
| E013 | [packages/atlas/src/atlas_viewer/static/app.js](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/static/app.js) — UI: busca, filtros, detalhe, comparação, tempo, linhagem e referências | `READ_FULL` | `6a68dedffc82a6bac563592544cf62ccabb079feee4681676604f1046b97d7fb` |
| E014 | [packages/protocol/src/caderno_protocol/resources/schema.json](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/resources/schema.json) — Recursos persistidos preservados: disponibilidade dos bytes e digests | `BYTES_HASHED_NOT_FULL_SEMANTIC_REVIEW` | `03a85b4c5c8da312e3b9413b5365531b80f397c33993a70f277b8197c4781f66` |
| E014 | [packages/protocol/src/caderno_protocol/resources/context-catalog.json](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/resources/context-catalog.json) — Recursos persistidos preservados: disponibilidade dos bytes e digests | `BYTES_HASHED_NOT_FULL_SEMANTIC_REVIEW` | `463242e640c3396fb1dc318c3dde15191292a123a7a12e46e2d202a20137a46a` |
| E014 | [packages/protocol/src/caderno_protocol/resources/ro-crate-1.3-context.jsonld](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/resources/ro-crate-1.3-context.jsonld) — Recursos persistidos preservados: disponibilidade dos bytes e digests | `BYTES_HASHED_NOT_FULL_SEMANTIC_REVIEW` | `5a3df1a43185501db4d45cdde5a478c57eeb1d673eedfe400488fc4c4b21dd91` |
| E015 | [specs/003-producer-selective-preview/spec.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/spec.md) — Feature 003: requisitos e mapeamento | `READ_FULL` | `5bb61f6cae016fcbb202ed494e38938df26c531d8da405fb8bc66d6b50e36225` |
| E015 | [specs/003-producer-selective-preview/data-model.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/data-model.md) — Feature 003: requisitos e mapeamento | `READ_FULL` | `b35b81edab4448a312e1c8ba5ba2dee31bdee3a4e1fd094c77756d8617635a82` |
| E016 | [docs/protocol/0.1.0a1.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/protocol/0.1.0a1.md) — Perfil público e manifesto de digests | `READ_TARGETED` | `76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e` |
| E016 | [docs/protocol/profile-manifest.json](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/protocol/profile-manifest.json) — Perfil público e manifesto de digests | `READ_TARGETED` | `cd2d3b596453c2deafe096bef7c82c65c317fda7531f1a5a4ffbd0acb644de80` |
| E017 | [.specify/toolchain.json](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/.specify/toolchain.json) — Descritores da instalação Spec Kit 1.2.3 | `READ_FULL` | `ae47f66efe51a71a8da2d04dd48a66a544463460309c77ba7505ea5b94a33983` |
| E017 | [.specify/integration.json](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/.specify/integration.json) — Descritores da instalação Spec Kit 1.2.3 | `READ_FULL` | `976306f1f2ca586abc751302c6e87eedbc10fa94bc1643c981e94402fae189e4` |
| E018 | [tests/viewer/test_related_references.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/tests/viewer/test_related_references.py) — Testes existentes: referência e proteção de apresentação numérica | `READ_TARGETED_NOT_EXECUTED_BY_ARCHAEOLOGY` | `c0f24d5fb49ba1076cec8237c7860ae5297ebdfc7fe6f40b2b1c95dd8de1741d` |
| E018 | [tests/viewer/test_catalog_server.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/tests/viewer/test_catalog_server.py) — Testes existentes: referência e proteção de apresentação numérica | `READ_TARGETED_NOT_EXECUTED_BY_ARCHAEOLOGY` | `887279b0643c7e872ff84f1e22bcf80690b5dff9c9b55d0f5c731cb9f764c20d` |

## 5. Fatos de capacidade e perdas observáveis

- **Identidade:** E012, `catalog.py:65`, enumera fontes na ordem declarada como `source-1`, `source-2` etc.; E013, `app.js:6,18–19,26`, contextualiza a identidade pelo par fonte/ID. Há separação entre pacotes, mas nenhum link estável após reordenação é demonstrado.
- **Preservação e apresentação:** E010, `read_model.py:40–80`, conserva projetos, experimentos, artefatos, relações e todas as `entities`. Só `CreateAction` vira run (`56–57`). E013, `app.js:19,90`, oferece detalhe navegável para run, enquanto demais entidades aparecem como texto. Uma propriedade conservada no grafo não é automaticamente exposta pela interface.
- **Capacidades existentes:** E013, `app.js:42,89–95`, implementa busca/filtros de runs, tabelas de métricas/parâmetros, comparação por propriedade/tipo/unidade, timeline e linhagem. Não são funcionalidades ausentes. A timeline usa a coleção de runs, enquanto os filtros atuam na lista de exploração; a abrangência entre vistas merece apresentação explícita.
- **Referências relacionadas:** E009; E010, `read_model.py:27–38,71`; E013, `app.js:48–88`. `mentions` permanece relação neutra, deduplicada por alvo na ordem inicial dentro do pacote. Não cria input/output/derivação ou aprovação.
- **Tempo:** E012 distingue indexação e observação em `catalog.py:101–102,131–132`; E010 separa publicação do snapshot (`78`) dos tempos de execução (`67–68`). E013, `app.js:31`, rotula `indexed_at` como índice observado. Isso não torna tempo de evento, criação do arquivo e observação equivalentes.
- **Números e tabelas:** E011 valida `PropertyValue` tipado, unidade e motivo de ausência; E012, `catalog.py:39–50`, conserva o inteiro textual para JavaScript; E013, `app.js:89,92`, mostra tipos/unidades/precisão e separa incompatibilidades. A referência a um CSV não prova existência de contrato universal de tabela tipada/ordenada ou parser no viewer.
- **Cobertura:** contagens em E013, `app.js:30,45,97`, dizem respeito às fontes/runs carregadas ou filtradas. Não existe prova do denominador do acervo original a partir dessas contagens. Aquisição, projeção, seleção e conversão são etapas separadas em E009/E015; seus totais permanecem desconhecidos sem recibo correspondente.

Esses fatos sustentam a matriz de paridade. Classificações de gap e contratos propostos são inferências/propostas explícitas; não recuperam a semântica de estudos que não foram lidos.

## 6. Reaproveitamento de testes sem atribuição indevida

O recibo E006 reporta CI de produto [40246678115](https://github.com/thalesvalente/Atlas/actions/runs/40246678115) e Spec Kit [40246678113](https://github.com/thalesvalente/Atlas/actions/runs/40246678113) no HEAD `e985ea3124b7a3cd241ee2dbc88b5ad50688373c`, e identidade de árvore com a main integrada. Esta arqueologia **leu o recibo**; não reexecutou esses jobs nem transformou seu status histórico em CI dedicada ao SHA P01. A contagem histórica de 86 testes por célula não é somada entre sistemas operacionais, modos e reruns como novos casos únicos.

O piloto operacional pertence ao recibo LOCAL-REAL01 citado pela PR, não a esta sessão CHAT. A prova visual sintética anterior não é prova de UI dos contratos propostos. Os testes efetivos da candidata, os casos positivos/negativos, a revisão independente e o SHA exato ficam em `RESULT.md` e `HANDOFF.json`. O inventário das fontes nunca substitui esses resultados.

## 7. Continuidade mínima

Os estudos ausentes são lacuna de entrada, não bloqueio total de C0. Implementações compatíveis podem consumir os contratos candidatos e os exemplos sustentados no código vigente. Receber A/B/C/D completos permitiria conferir autoria/versão/digest e reconciliar diferenças sem substituir silenciosamente este pacote. Propostas que exijam novo formato persistido ou desvio arquitetural permanecem separadas para decisão e ADR quando aplicável.
