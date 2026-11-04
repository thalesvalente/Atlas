# A01 — porte da apresentação v6.1

O operador rejeitou a apresentação da candidata cosmética da PR #32 e solicitou
o reaproveitamento efetivo do código antigo. Esta sucessão porta funções de
layout e cartões, CSS e composição de navegação, detalhes, tabelas e catálogos.
A base funcional da PR #25 permanece preservada. Aceite humano: **PENDING**.

## Origem, autorização e limites

Origem: `thalesvalente/R4-RNF-RES-FIX`, commit
`2895d95f81a0436636227d02b504ed1dad3f2e36`, apresentação Atlas v6.1.
Autorização do proprietário:
https://github.com/thalesvalente/Atlas/pull/18#issuecomment-6552216866.
O manifesto sucessor `REUSE-MANIFEST.json` fixa arquivos, blobs, funções,
classificação de reuso e hashes dos destinos. O manifesto C2/v5 e os componentes
P03 históricos não são alterados. Não se declara uma licença geral de software.

| Componente original | Destino | Tratamento |
| --- | --- | --- |
| `graph-cards.js`: SVG seguro, títulos, temas e famílias | `native_legacy_tree.js` | Funções reutilizadas ou adaptadas; texto/SVG via DOM, UIDs de ocorrência |
| `graph-layout.js`: geometria, links, câmera e minimapa | `native_legacy_tree.js` | Porte da geometria e câmera; somente endpoints unívocos de registros |
| `app.js`: normalização, filtros e índice | `native_legacy_model.js`, `native_legacy_views.js`, `native_notebook.js` | Filtros/índice com a mesma população; aliases e lexemas preservados |
| `template.html`, `style.css`, `theme.css` | `native_notebook.html`, `native_legacy*.css` | Estrutura adaptada e folhas de estilo portadas com escopo; HTML executável excluído |
| `records-products.js`: detalhes e tabela de registros | `native_legacy_views.js` | Composição portada para DOM seguro, estados declarados e referências internas |
| `tables-coverage.js`: leitura de tabelas e relações | `native_legacy_views.js`, `native_notebook.js` | Leitura organizada e ordem reversível; P03 congelado disponível como inspeção |
| `historical-catalog.js`: catálogos tipados | `native_legacy_views.js`, `native_notebook.js` | Coleções separadas, busca, população e detalhes; sem acesso automático a arquivos |

## Adaptações necessárias

O DTO verificado e o transporte Native View continuam sendo a única entrada.
Não há iframe, execução de HTML histórico, importação do runtime produtor,
descoberta de worktrees, leitura arbitrária de arquivos ou abertura automática
de URLs. HTML por interpolação é substituído por `textContent` e criação de DOM.
Números científicos nunca passam por `Number`: o adaptador conserva seus lexemas,
inclusive em metadados estruturados. Ausência, NULL, texto vazio e UNKNOWN não
recebem estados substitutos. Colisões entre registros e objetos técnicos usam
a mesma resolução da navegação nativa; não se filtra um candidato para fabricar
unicidade. Fontes com entradas escalares permanecem consultáveis.

Famílias mantêm chaves tipadas separadas do rótulo: número/texto, ausência/NULL e
nomes literais homônimos não se fundem no filtro nem no mapa editorial. Pares de
famílias usam tuplas reversíveis, inclusive para nomes com NUL. O retorno de uma
referência reconstrói as opções do contexto anterior antes de restaurar filtros.

A árvore editorial passa a ser a entrada principal. O modo técnico continua
explícito e conserva a expansão progressiva de grafos grandes. Tema/família é
organização de leitura, não causalidade. Árvore editorial, índice, registros e
relações de registros usam os mesmos filtros. O contexto técnico integral é
rotulado e separado. Os catálogos incluem `products` e todas as coleções de
recursos já aceitas pelo exportador.

As tabelas mostram identificação, núcleo, nome, descrição e critérios antes das
demais colunas, quando presentes. Quando os cinco campos estão declarados, a leitura essencial mostra esses cinco; o total e a opção de todas as colunas são explícitos. A ordem original pode ser restaurada. Cabeçalhos
e células permanecem literais, inclusive problemas de codificação existentes na
fonte. As colunas têm largura legível e rolagem horizontal; não são comprimidas
para caber simultaneamente. JSON conserva os JSON/lexemas originais. CSV conserva
a ordem e a representação literal das células, com quoting e neutralização de
fórmulas declarados. A inspeção P03 usa seus blobs congelados inalterados.

Os detalhes apresentam execução, publicação, admissão, revisão, documentação,
produtos e relações antes da inspeção técnica. O painel não reduz a largura da
árvore/tabela; em tela pequena ocupa uma faixa inferior com rolagem própria.
Ao focar um registro, a câmera considera a região visível livre desse painel;
no celular, traz o mapa à área útil antes de enquadrar o cartão acima dos detalhes.
Isso adapta a câmera original à composição com sobreposição, sem encobrir a seleção.
Títulos sem espaços quebram em linhas; o título integral permanece no nome
acessível, na descrição SVG, nos detalhes e nas exportações.
Filtros e opções editoriais móveis recolhem ao entrar no breakpoint e podem ser reabertos. O cabeçalho evita repetir a introdução para manter o mapa alcançável.

O catálogo recupera execução/estágio/escopo declarados antes das identidades
opacas; IDs integrais e publicação/revisão continuam em seções semânticas de
inspeção. Avisos de tabela priorizam a explicação da fonte e evitam NULL sem
rótulo. A tinta dos textos pequenos e ordinais SVG foi adaptada para contraste
mínimo 4.5:1 nos fundos testados, preservando os acentos originais.

## Validação e integração

`node scripts/qa/test_native_legacy.mjs` cobre os casos adversariais do adaptador e
dos componentes portados, com dados inventados. A suíte instalada de aplicação
exercita também os modos explícitos técnico e P03, inspeção, retorno contextual,
cancelamento, foco, teclado, ausência/NULL, exportações exatas e resoluções móveis.
Os ensaios nativos/P02 e as suítes de arquitetura/protocolo continuam obrigatórios.
Os pins exatos e testes negativos do servidor são mantidos.

Capturas OLD/NEW, projeção real, estados de câmera e inventários privados ficam
somente no pacote LOCAL do operador. Sua execução e parecer visual técnico são
registrados no handoff local, separados do code review e do aceite humano.
Capturas sintéticas da CI são somente regressões de engenharia; não substituem
a comparação real. CI/review devem ser vinculados ao SHA final da PR Draft #32.
Integração proposta: revisão da PR #32 sobre a branch da PR #25, sem alterar,
mesclar ou publicar a baseline em nome do operador. Não há release, deploy,
migração, descriptor 0.2.1, liberação C2-B/ARC-09 ou aceite científico.
