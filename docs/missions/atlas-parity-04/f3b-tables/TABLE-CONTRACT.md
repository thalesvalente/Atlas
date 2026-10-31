# Contrato do componente F3B

Componente isolado de apresentação em memória. Descriptor atlas-legacy-presentation0.2.0, schema F2 incorporado sem alteração; LEGACY_DERIVED. Não implementa abertura, File API, servidor, Catalog ou SDK.

## API pública

Carregar o asset fixo JS/CSS num harness próprio. AtlasF3BTables.mount(root, descriptor?, options?) retorna:
- setTables(descriptor): valida antes de trocar o dataset; retorna boolean; erro fica visível em role=alert. Descriptor deve declarar schema/semantics PASS; o componente ainda verifica schema e invariantes próprios. Não promove autenticidade/ciência.
- query({table,search,admission,sort,page,pageSize}): visão derivada; sort null restaura ordem original. Página basezero; tamanho1–100. Busca examina campos da linha e estados declarados.
- token(tableNavigation,rowNavigation?): retorna chave efêmera fonte/snapshot/sessão/tabela/linha/ocorrências.
- select(token): recusa token stale/forjado e emite um CustomEvent atlas-f3b-select neutro, com cópia independente do token. Sem integração F3A.
- getState(): cópia da visão/seleção, totais carregado/filtrado/visível, global_total null.
- exportJSON(): descriptor inteiro fiel em JSON tipado; conserva cells, lexemes, units, precision, absence, headers, ordinais, relações, unmapped_fields e gaps.
- exportCSV(tableNav?): todas as linhas da tabela carregada na ordem original, mesmo com filtro/página ativos. CSV derivado seguro; não é serialização fiel dos tipos.
- dispose(): invalida contexto/seleção, cancela timer e remove componente.

options.pageSize default10. options.now é relógio injetável somente para testes; produção usa Date.now. options.sortTypes é declaração externa explícita: {tableNav: {columnIndex: {type,unit}}}. Tipos aceitos:string/integer/decimal/boolean. A coluna inteira precisa concordar em tipo e unidade; null/missing vão ao fim e não viram valores. Inteiros/decimais usam comparação textual com expoentes BigInt, sem converter valores a Number. Unidade não é convertida.

## Fidelidade e segurança

Tabelas/linhas/colunas conservam ordem original. JSON literal mantém dados; nenhum filtro/sort altera fonte. Native IDs não são derivados de navegação/ordinal/nome. RF/RNF/RES só declaradas; native_id null de não admitida continua null. Quatro tabelas sintéticas não vinculadas permanecem consultáveis, com binding_gap/Run externo explícitos. IDs iguais em contextos diferentes não são fundidos. Reimportação mesmo do mesmo snapshot, mudança de fonte/snapshot, expiração e dispose invalidam tokens.

DOM usa createElement/textContent e propriedades fixas. HTML/URI/objetos são texto inerte; nenhum link ativo, execução de dados, storage persistente ou rede. Categoria MISSING, JSON null, string vazia, zero e UNKNOWN são distintos. File conserva tipo e papel declarado. Cabeçalhos th/scope/headers/caption; botões nativos/filtros rotulados/foco visível. Overflow horizontal/vertical da tabela é contido, rolável, sem remoção de colunas/dados.

CSV: cada campo entre aspas, aspas internas duplicadas, delimitador vírgula/linhas CRLF. Controles C0/C1/BOM dentro de campos viram texto literal \\uXXXX; prefixos de fórmula =,+,-,@ após whitespace/controles recebem apóstrofo. Headers também neutralizados. Unicode preservado; JSON conserva valores originais. UI exporta para textarea em memória somente por ação explícita, sem rede ou download automático.

## Quotas e limites da fase

32MiB UTF-8 descriptor; profundidade20; máximo128tabelas/256colunas/100000linhas agregadas/10000nós/100000relações/10000assets; literal64KiB/lexeme128KiB, além de limites schema. Rejeição atômica conserva snapshot anterior ainda válido; expirado é invalidado. Não há descarte silencioso por quota.

São quotas estruturais verificadas no componente. Não há promessa de limite duro de heap/deadline por processo. Aquisição externa e futura abertura F4 têm obrigações próprias256MiB/30s/allowlist/host; não foram implementadas nem qualificadas em F3B. Fonte não é monitorada: OBSERVED_SNAPSHOT_ONLY.

RO-Crate1.3/ProcessRun0.6/Caderno0.1.0a1 permanecem inalterados. HL7/FHIR é capacidade futura por domínio. Este componente não certifica dados, ciência, autenticidade ou conformidade desses padrões.
