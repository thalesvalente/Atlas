# Feature 004 — Caderno na experiência nativa do Atlas

Data: 2026-11-02. Branch: `feat/atlas-original-ui-local-bridge-20261102`, PR #23. Direção: solicitação explícita do operador para planejar, criar tasks e implementar integração nativa; não confundir a ponte HTML anterior com paridade.

## User Scenarios & Testing

### US1 — Abrir os registros do Caderno existente (P1)
O operador aponta o código R4 já instalado e a raiz do Caderno. O exportador externo reutiliza `r4.campaigns.atlas.project`, a mesma projeção que alimenta o renderer antigo, e publica um pacote novo consumível pelo Atlas sem R4 instalado no viewer. Não renderiza nem executa HTML de entrada, não modifica o Caderno, não migra fontes e não chama provedores.
Aceite: abrir o pacote no Atlas exibe revisão, registros, nós, relações, tabelas e recursos; campo original não consumido permanece acessível no detalhe/exportação. Fonte alterada ou pacote inválido não recebe READY.

### US2 — Navegar sem iframe (P1)
O operador navega por árvore, registros, tabelas, recursos/dossiês, linha do tempo e cobertura usando componentes nativos da aplicação. Busca, filtros, seleção, paginação, zoom e exportação funcionam sobre o snapshot escolhido, sem executar JavaScript legado.
Aceite: identidade estrutural, ID científico, ocorrências repetidas, ausência/null, números exatos e estado declarado permanecem distintos. Toda página informa população total versus seleção; nada é descartado silenciosamente por top-N. O Atlas original continua referência operacional externa.

### US3 — Comparar e conservar (P1)
A exportação registra contagens e a revisão original; o operador pode cotejá-las com o Atlas antigo. A aplicação nunca concede aprovação científica. A suíte de navegador verifica a implementação, mas não substitui comparação com dados reais no Windows.
Aceite: hashes de fontes de teste permanecem iguais; renderer não usa iframe/srcdoc/innerHTML/eval; roda instalado sem pacote R4. Teste real do acervo e aceite humano são registrados separadamente.

## Requirements

- FR-001: reutilizar a API original de projeção do produtor somente em ferramenta externa; não importar `r4.*` no wheel Atlas.
- FR-002: usar o perfil Caderno 0.1.0a1/RO-Crate já existente, com payload File de apresentação versionado; não alterar contexto, schema ou semântica do protocolo.
- FR-003: manter o payload genérico, independente de nomes de projeto e domínios RF/RNF/RES; o adaptador externo conhece a fonte, o viewer conhece apenas entradas de apresentação.
- FR-004: separar uid de apresentação, native_id e source_key; colisões e pais não resolvidos são visíveis, não se fabricam relações científicas.
- FR-005: preservar todos os valores originais em JSON textual e apresentar números como texto lexical, sem round-trip pelo Number do navegador; não preencher ausências.
- FR-006: ler somente fontes fixadas na CLI e payloads declarados com digest verificado; nenhuma rota recebe caminho arbitrário, nenhuma URL é baixada automaticamente.
- FR-007: respeitar os limites existentes do protocolo sobre bytes armazenados (metadados 2 MiB, File individual 8 MiB, agregado 32 MiB); para apresentações que excedam 32 MiB sem compressão, transportar blocos JSON em Files zlib versionados com limites separados de expansão (8 MiB/bloco e 256 MiB total), dupla verificação de hash/tamanho, sequência, contagem e digest original; falhar sem truncamento se a compressão não couber.
- FR-008: renderizar texto e SVG próprios; não executar HTML importado. Links de documentos são referências explícitas, não autorização de acesso automático.
- FR-009: reutilizar o componente público P03 de tabelas e o servidor/SDK existentes; integrar em vez de clonar o R4.
- FR-010: entregar launcher com uma chamada operacional, spec/plan/tasks rastreáveis, testes e CI vinculados ao SHA final; sem merge/release/deploy.
- FR-011: iniciar o Atlas NOVO sem R4 ou Caderno legado instalado por `scripts/ABRIR-ATLAS.ps1`, com fontes fixadas do protocolo público ou vazio declarado; manter `ABRIR-ATLAS-NATIVO.ps1` como opção de compatibilidade do produtor legado, não entrada principal.
- FR-012: o mesmo lançador principal deve permitir fonte histórica explicitamente escolhida via `-LegacyCodeRoot` e `-LegacyNotebookRoot`, invocando o adaptador fora do processo Atlas para criar uma projeção derivada temporária, abrindo a UI nova com o acervo sem exigir uma exportação manual. Falha do adaptador ou do produto propaga código não zero; sem cópia para GitHub, migração persistente, escrita no Caderno ou descoberta de fontes.

- FR-013: para grafos com mais de 180 nós, a árvore abre com até 24 irmãos por nível e ramos internos recolhidos; busca e navegação revelam qualquer nó mesmo fora do foco inicial, sem descartar dados, confundir IDs nem inventar relações.

## Reuso visual do renderer histórico (FR-014)

FR-014: a interface nova deve oferecer a navegação familiar ao Atlas R4 por
mapa de temas/famílias, com cartões, agrupamentos, zoom, minimapa e detalhe da
ocorrência, usando SOMENTE a projeção nativa já verificada. Não executar HTML
legado, importar `r4.*`, inserir dados privados, inventar temas, relações ou
identidades. Um mapa editorial somente é usado quando explicitamente declarado
na fonte; na ausência dele, a vista usa colunas neutras com famílias literais.
A árvore estrutural integral permanece acessível no mesmo painel e é
selecionável independentemente. A transferência se limita aos algoritmos
visuais autorizados na PR #18; o produto continua independente.

SC-008: em fixture sintética, alternar mapa R4→famílias literais→árvore
estrutural, expandir famílias e acessar o detalhe da ocorrência exata; nenhuma
chamada externa, erro JS ou perda de bytes. Com o acervo real, comparar o mapa
temático do Atlas novo com o R4 para a mesma revisão e validar visualmente
separadamente no Windows.

## Clarifications

O operador autorizou implementar esta integração, não copiar o acervo privado para o GitHub. A saída é derivada local em diretório novo, fora do código e do Caderno. A extensão é conteúdo de File, não novo protocolo científico. O modo operacional não depende de flag synthetic. Dados inventados aparecem somente nos testes automatizados. Não há alteração da feature ativa global do Spec Kit.

## Success Criteria

SC-001: pacote externo abre na UI nativa sem R4 no ambiente do viewer. SC-006: projeção de engenharia cujo JSON de apresentação supera 32 MiB é consumida integralmente via transporte comprimido, mantendo 32 MiB de limite do pacote armazenado; metadados comprimidos adulterados são recusados. SC-002: todas as coleções e contagens do input são preservadas e consultáveis. SC-003: navegação/tabelas/exportações verificadas em navegador real. SC-007: em 1202 nós sintéticos, foco inicial com 25 itens, expansão progressiva com 49 e busca alcançando o último nó. SC-004: zero mutações de fontes. SC-005: comparação com acervo real e revisão independente não recebem PASS sem execução observada.
