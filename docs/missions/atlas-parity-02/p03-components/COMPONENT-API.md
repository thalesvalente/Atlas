# Component API — P03 / versão de apresentação 1

**API experimental, explícita e descartável.** Não define formato obrigatório do Caderno,
exportador de produtor, leitor de carrier ou extensão persistida. Os módulos são opt-in;
importar JavaScript não monta UI nem registra listeners globais.

## 1. Tabela candidata

Arquivo: `packages/atlas/src/atlas_viewer/static/parity02_p03_table.js`.
Estilo: `parity02_p03_table.css`, com seletores limitados a `.atlas-p03-table`.

```javascript
validateTable(descriptor); // retorna a mesma entrada validada; não congela/muta
formatCell(value, column, missingReason); // string de apresentação
sortRows(descriptor, columnId, direction = "asc");
filterRows(descriptor, {columnId, operator, value});
renderTable(document, descriptor, {sort, filter}); // section desconectada
```

Exemplo positivo, sintético:

```json
{
  "version": "p03-table/1",
  "semantic_status": "CANDIDATE_PRESENTATION",
  "synthetic": true,
  "title": "Medições sintéticas",
  "columns": [
    {"id": "count", "label": "Contagem", "type": "integer", "unit": "1", "precision": 0},
    {"id": "value", "label": "Valor", "type": "decimal", "unit": "mg/L", "precision": 2}
  ],
  "rows": [
    {"id": "r1", "cells": {"count": "9007199254740993", "value": "0.123456789012345678901"}},
    {"id": "r2", "cells": {"count": 0, "value": null}, "missing_reasons": {"value": "Não medido"}}
  ]
}
```

Tipos: `string`, `integer`, `decimal`, `boolean`. `decimal` é nome desta API candidata,
não valor novo de `cp:valueType`. Título e pelo menos uma coluna são obrigatórios; linhas
podem ser vazias. `description`, `synthetic`, `unit`, `precision` e `missing_reasons` são
opcionais. Identidade de linha é local ao descritor: o integrador qualifica a fonte quando
compõe descritores. Campos não declarados são recusados, sem descarte silencioso.

### Política de valores

Strings numéricas preservam grafia, zeros iniciais/finais, sinais e expoentes. Integer
aceita string inteira decimal ou Number seguro. Decimal aceita string decimal finita na
gramática documentada no módulo ou Number finito, recusando Number inteiro inseguro.
Não há coerção de booleano/string vazia para número. Ausência é célula omitida ou null;
zero, false e string vazia permanecem valores. Motivo de ausência não pode acompanhar valor
presente. Unidade ausente fica não declarada, sem assumir unidade adimensional.

**Fronteira de transporte:** a validação não recupera um decimal já arredondado antes da
chamada. Fidelidade lexical exige string antes de JSON/JavaScript. Inteiros Python devem
ser preservados antes do transporte. Esta escolha de apresentação não relaxa o perfil
persistido, que mantém os tipos e restrições atuais. Precisão é metadado; nunca arredonda.

Ordenação usa coeficiente BigInt/escala decimal para comparação numérica, é estável e
mantém ausências no fim nos dois sentidos. Strings têm ordem lexical determinística UTF-16;
booleanos false/true. Filtros: eq (todos), contains (string, sensível a caixa), lt/lte/gt/gte
(numéricos), is_missing/is_present (sem value). Não existe conversão de unidade.
Retornos mantêm as referências dos objetos de linha; arrays de resultados são novos.

### Limites e erros

| Limite | Valor |
|---|---:|
| Linhas / colunas | 1000 / 32 |
| Células declaradas, linhas × colunas | 20000 |
| Texto por célula/descrição | 8192 unidades UTF-16 |
| Texto agregado | 1000000 unidades UTF-16 |
| Identificador | 256 unidades UTF-16 |
| Título/rótulo/motivo de ausência | 1024 unidades UTF-16 |
| Unidade / literal numérico | 128 / 256 caracteres |
| Magnitude de expoente | 1000 |
| Precisão | inteiro entre 0 e 100 |

`TableInputError` expõe `code` e `path`. Códigos: INVALID_DESCRIPTOR, INVALID_VALUE,
INVALID_TYPE, INVALID_OPTION, INVALID_DOCUMENT, UNSUPPORTED_VERSION, UNSUPPORTED_SEMANTICS,
UNKNOWN_COLUMN, DUPLICATE_ID, UNSAFE_NUMBER, INCOMPATIBLE_FILTER e LIMIT_EXCEEDED.
Objeto acessor/array com hooks não é dado JSON admitido. Não fornecer Proxy ou objeto
executável: a API é para dados explícitos, não um sandbox de JavaScript arbitrário.

Negativos verificáveis em `table-invalid.json`: Number 9007199254740992, booleano como
inteiro, HTML como decimal, ID duplicado, versão desconhecida e semântica nativa inventada.
Um limite excedido falha; não trunca nem pagina silenciosamente.

### DOM

O renderer valida antes de criar nós. Retorna section com table/caption/thead/tbody,
th scope=col/row e aria-sort quando ordenada. Região role=region, tabindex=0 e aria-label
identifica rolagem horizontal. CSS contém overflow no componente e foco visível. Textos
usam textContent; nenhum URI vira link. Chamador controla controles, montagem, remoção e
foco. DOM-recorder comprova estrutura/comportamento; layout/teclado real exigem navegador.

## 2. Metadados do contrato atual

Python: `packages/atlas/src/atlas_viewer/parity02_p03_metadata.py`.

```python
project_metadata(read_model, source_key, *, entity_ids=None)
```

Entrada: projeção `to_read_model` já obtida pelo consumidor existente, e chave opaca/estável
de snapshot fornecida explicitamente. A função não abre fonte ou payload, não faz rede e
não altera input. Valida dados usados pela apresentação; não substitui o SDK do protocolo.
Seleção padrão: entidades File e alvos de mentions de CreateAction. `entity_ids` permite
seleção explícita de outras entidades declaradas, sem dedução de papel.

Saída `p03-metadata/1`, `semantic_status=DERIVED_CURRENT_CONTRACT`:

| Campo | Conteúdo |
|---|---|
| source | key, name, metadata_sha256 recebido do leitor |
| items[].identity | objeto source_key/id, sem concatenação ambígua |
| items[].kind | artifact se File declarado, senão entity |
| name/types/description/media_type | declarações preservadas em entities |
| availability | declared e observed separados |
| digests | declared_sha256 e calculated_sha256 separados |
| relations | input/output/derived_from corroborados no grafo |
| mentions | relação mention neutra, separada |

`object` só produz input e `result` só produz output quando declarados em CreateAction;
`prov:wasDerivedFrom` conserva direção. Toda referência precisa resolver no mesmo grafo.
Projeções contraditórias, observações divergentes e relações injetadas são recusadas.
Digest calculado só é copiado quando recebido; a função não calcula bytes nem infere
integridade de strings. Observação ausente vira UNVERIFIED, campos ausentes permanecem null.
A projeção não autentica quem forneceu o read model; proveniência confiável continua
responsabilidade do chamador/SDK e não é conferida por um rótulo no descritor.

JavaScript: `parity02_p03_artifacts.js` + `parity02_p03_artifacts.css`.

```javascript
validateMetadata(descriptor); // valida/copia os campos apresentados
renderMetadata(document, descriptor); // section desconectada
```

Limites: 10000 entidades Python; 200 itens selecionados; 5000 relações distintas do grafo;
10000 cópias nos cartões JS porque uma relação pode aparecer em ambos endpoints; 64 tipos;
16384 codepoints por texto; 2048 por ID/chave da fonte. IDs maiores ou maior acervo podem
exigir seleção/paginação futura explícita. A projeção falha em vez de omitir silenciosamente.
`MetadataError` expõe code/path: FIELD_TYPE, LIMIT, DUPLICATE_ID, REFERENCE_SHAPE,
UNRESOLVED_ENTITY, INCONSISTENT_READ_MODEL, SOURCE_MISMATCH, DIGEST_FORMAT, STATUS_VALUE,
SEMANTIC_KIND, RELATION_KIND, RELATION_IDENTITY, DESCRIPTOR_VERSION e DOCUMENT_REQUIRED.

## 3. Produto/documento candidato

```javascript
validateCandidate(descriptor);
renderCandidate(document, descriptor);
```

Obrigatórios: version=p03-candidate/1, semantic_status=CANDIDATE_PRESENTATION,
synthetic=true, semantic_kind=product|document, identity={source_key,id}, title.
Opcionais: description; fields=[{label,value}]; sections=[{title,text}]. Textos podem ser
null; números em campos ricos devem ser explicitamente strings. Máximo100 campos e100
seções, com limites de texto acima. synthetic diferente de true gera SYNTHETIC_REQUIRED.

`document-candidate.json` e `artifact-product-candidate.json` declaram semântica sintética;
`artifact-descriptor.json` mostra File report.pdf que permanece artefato. Não há markdown
ativo, HTML ativo, anexos abertos, navegação externa ou execução de documento.

## 4. Harness e reprodução

`python scripts/qa/atlas_parity02_p03_harness.py --port 8766` monta só fixtures nomeadas e
serve allowlist fixa em 127.0.0.1. Não acessa catálogo/carrier/fontes privadas. A página mostra
contrato atual versus candidatos e controles de ordem/filtro; exemplo máximo gera1000×20
células sintéticas. Ctrl+C encerra o processo. Não há persistência ou serviço instalado.

`node scripts/qa/atlas_parity02_p03_browser.mjs <saida.json>` executa prova Playwright se
biblioteca e Chromium já existirem. Não baixa nem instala browser. PORT, sandbox e rede não
são reconfigurados; P03_PYTHON e P03_BROWSER_EXECUTABLE selecionam ferramentas já disponíveis.
Ausência de ferramenta produz NOT_RUN e exit2, sem alegar PASS. A demonstração só pode ser
atestada visualmente quando esse gate realmente executar.
