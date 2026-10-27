# Contrato de navegação P02

Asset local `/parity02_p02_state.js` exporta global `AtlasParity02State` e CommonJS
para testes Node. API: defaults/key/flatten/filterRuns/sortRuns/parse/stringify.
Hash v=1 contém scope, view, run, selected, q e filtros. Parâmetros desconhecidos,
duplicados, valores fora das enumerações, limites e IDs desconhecidos geram aviso.
Scope divergente/ausente em link identificado rejeita qualquer resolução de entidade.

`parse(hash,catalog)` retorna `{route,warnings,rejected,reason}`. `route` contém
`{view,detail,selected,filters}`. `stringify(route,catalog)` produz hash canônico.
Views: explore/compare/timeline/lineage/sources/dossier. Ordenação padrão por título
com desempate por fonte/ID. Dados entram via textContent/createTextNode.

URL é compartilhável dentro da sessão e snapshot. Filtros e IDs da consulta ficam
visíveis no endereço do navegador; nenhuma URL externa é resolvida. Reiniciar
servidor expira o binding. O hash não autentica conteúdo nem autoriza acesso.

Pontos P03: componentes futuros montam nos contêineres das views, usam o catálogo
e a rota validados; novos assets entram em allowlist/packaging por integração P06.
Não há implementação P03 copiada nesta candidata.
