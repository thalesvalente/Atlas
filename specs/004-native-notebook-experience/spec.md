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
- FR-007: respeitar os limites existentes: metadados 2 MiB, payload individual 8 MiB, agregado 32 MiB; particionar a exportação ou recusar sem truncamento.
- FR-008: renderizar texto e SVG próprios; não executar HTML importado. Links de documentos são referências explícitas, não autorização de acesso automático.
- FR-009: reutilizar o componente público P03 de tabelas e o servidor/SDK existentes; integrar em vez de clonar o R4.
- FR-010: entregar launcher com uma chamada operacional, spec/plan/tasks rastreáveis, testes e CI vinculados ao SHA final; sem merge/release/deploy.

## Clarifications

O operador autorizou implementar esta integração, não copiar o acervo privado para o GitHub. A saída é derivada local em diretório novo, fora do código e do Caderno. A extensão é conteúdo de File, não novo protocolo científico. O modo operacional não depende de flag synthetic. Dados inventados aparecem somente nos testes automatizados. Não há alteração da feature ativa global do Spec Kit.

## Success Criteria

SC-001: pacote externo abre na UI nativa sem R4 no ambiente do viewer. SC-002: todas as coleções e contagens do input são preservadas e consultáveis. SC-003: navegação/tabelas/exportações verificadas em navegador real. SC-004: zero mutações de fontes. SC-005: comparação com acervo real e revisão independente não recebem PASS sem execução observada.
