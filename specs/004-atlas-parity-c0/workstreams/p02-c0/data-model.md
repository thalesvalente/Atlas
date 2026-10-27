# Modelo derivado P02

Nenhum campo abaixo altera o protocolo persistido. Catálogo acrescenta `snapshot_id`
opaco e política de binding `SESSION_AND_SNAPSHOT`. Fonte acrescenta fingerprint
de snapshot e `coverage`: carregados verificáveis e contagens de população/seleção
desconhecidas. Índice antigo permanece estável se fonte mudar até rebuild explícito.

Estado UI: view, detail (chave JSON [fonte,id] ou null), selected (até quatro chaves),
filters (query/project/experiment/source/status/review/metrics/references/sort).
Histórico/hash é validado contra catálogo antes de resolver chaves.

Precisão de apresentação: `display_value` e `display_precision` são texto do servidor;
o valor numérico original permanece no modelo/dossiê. Ausência não vira zero.
