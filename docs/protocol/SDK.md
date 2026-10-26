# SDK independente do Caderno

Distribuição `caderno-protocol==0.1.0a1`, Python >=3.11, sem dependências de
runtime. O pacote não importa a interface nem qualquer produtor. Validade
científica, autenticidade, disponibilidade, integridade e sintaxe permanecem
campos/escopos distintos.

```python
from caderno_protocol import load_package, to_read_model

package = load_package("pacote-explicitamente-autorizado")
print(package.report.to_dict())
model = to_read_model(package)
```

| API | Resultado e responsabilidade |
|---|---|
| `validate_document(dict)` | `ValidationReport`; forma restrita, semântica do perfil, grafo e IDs; não lê payloads |
| `load_package(path)` | `Package(document, metadata_sha256, report, payload_status, source_name)`; lê somente a fonte indicada e seus payloads locais permitidos |
| `to_read_model(package)` | Dicionário derivado com `source`, `projects`, `experiments`, `runs`, `artifacts`, `relations`, `entities`, `authority` |
| `python -m caderno_protocol SOURCE` | Relatório JSON; exit 0 quando não há erros, 2 em erro; warnings continuam visíveis |

`ValidationIssue` contém `code`, `path` lógico e `message`. `ValidationReport`
contém `errors`, `warnings`, propriedade `valid` e `to_dict()`. Erros de fonte,
incluindo arquivo ausente, ficam no relatório, não viram um conjunto de dados
inventado. Um relatório sem erros ainda pode conter aviso de payload ausente,
tempo desconhecido ou leitura limitada; consumidores devem exibir os avisos.

Projetos têm `id`, `name`, `description`; experimentos acrescentam `project_id`.
Runs têm `id`, `name`, `description`, `project_id`, `experiment_id`, `status`,
`review_status`, `synthetic`, `timestamp_origin`, `started_at`, `ended_at`,
`metrics`, `parameters`, `inputs`, `outputs`, `artifacts`, `agent_id`,
`instrument_id`, `derived_from`. Métricas/parametros têm `id`, `name`,
`property_id`, `value`, `type`, `unit`, `precision`, `missing_reason`.

Esse dicionário é uma projeção descartável. `entities` conserva os valores
originais para inspeção; ele não é um formato de publicação concorrente.
Propriedades fora dos campos exibidos permanecem no documento original.
Nenhuma função grava índices, executa anexos ou altera metadados de origem.

`load_package` rejeita decimais cujo valor mudaria no roundtrip suportado pelo
Python (`Decimal(literal) != Decimal(str(float(literal)))`), incluindo overflow
e underflow com perda. O relatório usa `SOURCE_INVALID`; os bytes permanecem
intactos. Inteiros não são convertidos em float. `validate_document`, quando
recebe um dicionário já criado pelo chamador, não pode recuperar precisão que
esse chamador perdeu antes da chamada; use `load_package` para validar bytes.

## Erros que o consumidor deve tornar compreensíveis

| Situação | Exemplos de códigos |
|---|---|
| Fonte inacessível/inválida | `SOURCE_INACCESSIBLE`, `SOURCE_INVALID`, `SOURCE_UNSAFE` |
| Versão ou semântica não reconhecida | `UNSUPPORTED_VERSION`, `UNSUPPORTED_PROFILE`, `UNSUPPORTED_CONTEXT`, `UNMAPPED_TERM` |
| Referência inválida | `MISSING_REFERENCE`, `UNSAFE_REFERENCE`, `ID_ALIAS_COLLISION` |
| Identidade/linhagem | `DUPLICATE_ID`, `DERIVATION_CYCLE`, `NAMESPACE_REQUIRED` |
| Informação científica incompleta | `UNKNOWN_TIME`, `MISSING_VALUE_REASON`, `REVIEW_STATUS` |
| Integridade/disponibilidade | `INTEGRITY_MISMATCH`, `SIZE_MISMATCH`, `PAYLOAD_MISSING`, `PAYLOAD_UNAVAILABLE`, `READ_BUDGET_EXCEEDED` |

## Validação externa e uso offline

O recurso JSON Schema é um contrato estrutural; aplicar somente esse schema não
valida o grafo. `research/validate_reference.py` aplica ferramenta externa à base
RO-Crate em ambiente de teste, enquanto os testes de QA verificam os limites do
perfil. Essa ferramenta externa não é importada pelo SDK nem pelo Atlas.

A cópia local do contexto possui digest verificado e licença própria. O SDK
nunca desreferencia URLs. Path explicitamente selecionado não confere
autorização de escrever no diretório, publicar seus digests ou ler qualquer
outra fonte histórica.
