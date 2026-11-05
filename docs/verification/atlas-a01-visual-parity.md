# A01 — paridade visual Native View 004

## Sucessão atual — porte da apresentação v6.1

A continuação solicitada pelo operador porta código autorizado da apresentação
original: funções de layout/cartões/câmera, CSS com escopo e composição segura de
índice, detalhes, tabelas, produtos e relações. A árvore editorial é a entrada
principal; estrutura técnica e P03 congelado são opções explícitas de inspeção.
Tabelas recuperam a leitura essencial de cinco campos quando declarados, com
ordem original integral reversível. O mesmo filtro governa registros e relações.
Detalhes preservam área útil e a navegação móvel mantém mapa e filtros acessíveis.

Origem, autorização, adaptações e manifesto de transferência estão em
[REUSE-AND-PARITY](../missions/atlas-a01/REUSE-AND-PARITY.md) e
[REUSE-MANIFEST](../missions/atlas-a01/REUSE-MANIFEST.json).
Regressões de ausência/NULL, identidade, números, referências, exportação,
segurança e foco continuam obrigatórias. Evidência real fica LOCAL, separada da
CI sintética e do code review. HUMAN_ACCEPTANCE=PENDING, sem merge/release/deploy.

## Registro histórico — candidata cosmética 0611e188 (sucedida)

O texto abaixo descreve exclusivamente a candidata anterior e suas limitações,
antes da solicitação de porte real. Não descreve a implementação sucessora.

### Problema e comportamento resultante

A candidata `32a0b1a` ocupava a maior parte da primeira tela com navegação,
metadados e filtros, especialmente no celular. A árvore estrutural também
misturava a exploração de registros com uma população muito maior de objetos.

A apresentação agora usa um cabeçalho compacto, navegação móvel horizontal,
população/revisão em disclosure acessível e uma organização opcional por famílias
declaradas. A estrutura integral continua sendo o padrão. Os grupos `ui-family:*`
são contêineres temporários de apresentação: não entram nas fontes, no protocolo,
nos IDs científicos, nos detalhes exatos ou nas exportações. Detalhes priorizam
identidade original, estado, fonte, revisão, pointer e navegação contextual; todos
os campos e o JSON original continuam disponíveis. Os blobs P03 são preservados.

### Escopo e integração

Branch própria baseada no HEAD documental da PR #25. PR Draft empilhada na branch
`integrate/atlas-final-close-20261103`; não altera a PR #25. Integração posterior
exige inspeção do diff e requalificação da composição pelo integrador.

Ownership: `native_application.css`, `native_notebook.html/js`, regressões de
aplicação/Native/P02 e este registro. Sem mudanças no produtor, fontes científicas,
protocolo, descriptor 0.2.0, proposta 0.2.1 ou estado ativo do Spec Kit.

### Evidência e limites

O Atlas antigo foi executado com sua API oficial de build, sem copiar seu renderer
para o produto novo, com saída derivada isolada e fonte explícita somente leitura.
A projeção embarcada foi comparada aos bytes restaurados/verificados pelo Native;
apenas o link derivado de linhagem acrescentado pelo build antigo foi excluído da
igualdade. Capturas reais OLD/NEW e matriz de reprodução permanecem locais e
privadas. Nenhum dado, captura, hash de fonte ou caminho privado entra nesta PR.

As regressões públicas usam somente fixtures inventadas: geometria desktop/móvel,
disclosure, famílias, retorno contextual, foco/Escape, cancelamento de seleção
pendente, paginação, null/ausência, números exatos, exports e ausência de rede
externa. Testes automatizados não representam aceite visual humano.

Diferenças remanescentes incluem a proposta temática/editorial do legado e sua
apresentação específica de produtos/relatos. A visão por famílias não declara
equivalência dessa proposta, nem atribui causalidade científica. Detalhes móveis
continuam no fluxo da página para permitir interação com a árvore sem obstrução.

HUMAN_ACCEPTANCE=PENDING. Sem merge, release, deploy ou promoção de gates
científicos. CI e review devem ser vinculados ao SHA final, separadamente da
comparação privada e da nova inspeção humana.
