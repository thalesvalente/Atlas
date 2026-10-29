# Validação determinística dos exemplos P01

**Estado:** contrato candidato de ensaio documental. O programa neste diretório não é
um novo validador Caderno, endpoint, modelo do produto ou formato obrigatório de sidecar.
Os valores são sintéticos. Fontes/observações dos worksheets demonstram obrigações;
o programa não autentica quem as declarou nem mede um acervo histórico.

## Executar

Na raiz do checkout, com Python 3:

```bash
python -B docs/contracts/atlas-parity-02/p01/validate_examples.py --suite
```

O corpus explícito está em [examples/cases.json](examples/cases.json). Cada caso tem
ID, arquivo, formato, validade esperada e lista exata de códigos. Uma negativa só
passa quando é recusada pelo motivo especificado. `--suite` retorna 0 se todos os
casos e probes passarem; qualquer divergência retorna 1. Para validar um arquivo:

```bash
python -B docs/contracts/atlas-parity-02/p01/validate_examples.py --file docs/contracts/atlas-parity-02/p01/examples/negative-mention-as-input.json
```

A negativa acima retorna 1 com `RELATION_SEMANTICS`. Não confundir a rejeição esperada
do arquivo com falha da suíte. JSON com chave duplicada ou número não finito é recusado,
inclusive expoente válido em JSON que exceda o intervalo finito do leitor (`1e999`).
Validação semântica não usa `assert`; Python otimizado mantém as mesmas decisões.

## Dois níveis de prova

1. **Contrato vigente:** fixtures `current-profile-*.json` são documentos reais do
   perfil atual, autorais e sintéticos. O programa chama `validate_document`,
   `load_package`, `to_read_model` e `Catalog` públicos inalterados. As negativas
   `negative-current-*` retornam os códigos do SDK com prefixo `SDK:`.
2. **Candidata documental:** os três kinds `ATLAS_P01_*_EXAMPLE` são worksheets
   distintos de `ro-crate-metadata.json`. São avaliados por restrições de apresentação,
   cobertura ou tabela explicitamente definidas abaixo; sua aceitação não modifica a
   aceitação do SDK. São `CANDIDATE`, `synthetic: true`, com autoridade
   `DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL`.

## Gramática demonstrada de apresentação

O envelope `ATLAS_P01_PRESENTATION_EXAMPLE` contém `catalog_scope`, `sources`,
`entities` e `relations`. `sources` declara `id`, digest de metadados,
`identity_scope: CURRENT_CATALOG` e `stable_across_reorder: false`. O digest refere
bytes; não fornece identidade global ou autenticidade. Os IDs de entidade são únicos
por `source_id + id`, permitindo repetição entre fontes.

Cada entidade declara tipos e papel de apresentação. `execution` corresponde a
`CreateAction`; `document` exige tipo documental explícito e `product` exige `Product`
neste ensaio restrito. `reference` não inventa papel especializado. A semântica de
tabela tipada/marco documental é `PERSISTED_EVOLUTION_REQUIRED` quando ensaiada; não
é imposta a arquivos tabelares ou datas que já possam ser mostrados como metadados.

As três classes são `CURRENT_CONTRACT`, `COMPATIBLE_PRESENTATION_CANDIDATE` e
`PERSISTED_EVOLUTION_REQUIRED`, conforme PRESENTATION-CONTRACTS. Um campo novo no
worksheet nunca demonstra que esse campo existe no Caderno ou no catálogo atual.

`time` mantém três objetos independentes: `event`, `file_created`, `observed`. O valor
ausente usa null, origem `UNKNOWN` e precisão `UNKNOWN`. Um valor conhecido usa o papel
correto (`DECLARED_EVENT`, `FILE_CREATED`, `OBSERVATION`), data literal para `day` ou
timestamp válido com fuso para `second`. A gramática não contempla todas as precisões
temporais possíveis; não preenche outras precisões silenciosamente.

Nas relações, `source` é o sujeito declarado e `target` o objeto declarado; ambos
contêm `source_id` e `id`. A visualização de `object` usa a seta alvo → execução,
mas não troca o sujeito da declaração original. O mapa aceito é:

| Predicado | Papel de apresentação | Sujeito exigido |
|---|---|---|
| mentions | reference | entidade declarada |
| object | input | execução |
| result | output | execução |
| prov:wasDerivedFrom | derived_from | entidade declarada |

Alvos inexistentes, resolução cruzada entre fontes, duplicação contextual e menção
promovida a input são recusados. Este worksheet não autentica predicados nem cria
uma nova regra de validação persistida.

## Gramática demonstrada de tabela

O envelope `ATLAS_P01_TABLE_EXAMPLE` é uma proposta de obrigação para grade tipada
geral, classificada como `PERSISTED_EVOLUTION_REQUIRED`. `tables` contém ID local,
`column_order`, `columns`, `row_order` e `rows`. Cada coluna declara ID, identidade
semântica, tipo, unidade, precisão e contexto de medição; valores desconhecidos são
null. As ordens explícitas precisam coincidir com as listas, sem reordenação silenciosa.

Cada célula conserva `column_id`, `value`, `raw` e `missing_reason`. Valor ausente
é null, raw null e motivo não vazio. Valor conhecido tem motivo null. Booleano não
passa como inteiro; strings como `001` conservam o literal. Número e literal decimal
devem coincidir exatamente segundo `Decimal`; precisão declarada exige casas
preservadas no literal. O inteiro 9007199254740993 é ensaiado sem perda para double.
O programa não reconstrói uma representação lexical que já se perdeu na origem.

Uma comparação identifica tabela, coluna e linha em cada ponta. O resultado é:

- `INCOMPATIBLE` quando há conflito explícito em identidade semântica, tipo, unidade
  ou contexto; o ensaio quantitativo também recusa tipos não numéricos.
- `UNKNOWN` quando faltam dados de compatibilidade ou um valor a comparar.
- `COMPATIBLE` somente para valores numéricos conhecidos com os quatro campos
  conhecidos e iguais; isso não calcula diferenças, não converte unidades e não
  aprova cientificamente a comparação.

Os exemplos conservam uma linha ausente além de linhas conhecidas. A compatibilidade
é decidida para as células explicitamente selecionadas, não para toda tabela por
semelhança de nomes.

## Gramática demonstrada de cobertura

O envelope `ATLAS_P01_COVERAGE_EXAMPLE` declara `derived: true`,
`caderno_required: false`, escopo, observação com fuso e seleção com critério/unidade/ID.
`collection_total_inferred_from_loaded_runs` deve ser false. Isso não proíbe medir um
total na fonte; proíbe obtê-lo indevidamente da contagem de runs carregadas.

As sete camadas aparecem uma vez na ordem source/projection/selection/conversion/
package/read_model/interface. Cada medida tem unidade, escopo, `known`, `count`,
evidências, denominador e razão. Count conhecido é inteiro não negativo, com evidência
declarada; booleanos e frações são recusados. Unknown é null e exige motivo em uma
fronteira de perda/limitação associada. Não há inferência por acesso ausente.

Um denominador conhecido aponta a uma camada medida com mesmo escopo/unidade,
contagem igual à referenciada, relação `SUBSET_OF` e evidência de correspondência.
O numerador não pode excedê-lo. Denominador desconhecido é null, sem percentual.
`0/0` mantém razão null. Uma razão informada deve coincidir com os inteiros exatos;
transformações 1:N não são representadas como retenção de subconjunto neste ensaio.

Uma perda numérica exige as duas contagens conhecidas, unidade/escopo idênticos,
mapeamento `ONE_TO_ONE` e diferença coerente. Sem isso usa null com motivo. Esta
gramática não agrega populações nem tenta deduplicação global. A declaração de
`mapping_evidence` é checada como presença estrutural; sua veracidade continua sendo
obrigação da revisão da fonte. A prova de um ensaio não cobre todo o contrato geral.

## Probes do leitor público

Além dos casos declarados, a suíte confere nove observações do leitor vigente:

1. As 13 entidades da fixture sobrevivem em `entities`.
2. Documento, produto e arquivo tabular não criam runs adicionais.
3. Menções repetidas deduplicam em ordem e não criam relações experimentais.
4. Valor ausente, precisão e tempo desconhecido permanecem distintos.
5. Arquivo tabular tem metadados, sem grade inventada.
6. Dois pacotes com mesmos IDs mantêm títulos locais distintos.
7. Reordenação troca os bytes associados a `source-1`, demonstrando seu limite.
8. Fonte com alvo inexistente é inválida e não recebe read model.
9. As duas entradas sintéticas observadas permanecem byte-idênticas.

O resultado da suíte informa hashes do validador, manifesto de casos e cada fixture.
Os probes não são nove execuções de navegador e não são nove estudos de paridade.
As regressões de produto eventualmente reutilizadas/executadas têm recibos separados.
