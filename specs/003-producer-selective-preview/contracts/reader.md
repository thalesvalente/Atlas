# Contrato público de consumo — REUSE-01

O Atlas recebe exclusivamente snapshots do perfil Caderno 0.1.0a1. Não recebe índices internos, módulos Python ou caminhos de worktrees de produtores.

O adaptador pode consumir uma projeção já obtida no produtor. Aquisição e transformação são etapas separadas: a segunda não autoriza a primeira nem repete resolução de fontes.

Preservar distinções entre estado técnico, revisão, conformidade, disponibilidade e autenticidade. Referências sem direção não podem virar entradas/saídas experimentais. Metadados fora do modelo visual mínimo permanecem no pacote e no manifesto com limites explícitos.

Erros de schema, identidade, seleção, precisão ou destino não são convertidos em PASS. Mudança do protocolo requer decisão própria; este incremento não a concede.

## Apresentação CLOSE01

O modelo derivado pode acrescentar `runs[].related_references` conforme `data-model.md`.
O leitor existente admite objeto `@id` e lista de referências; alvo inexistente gera
`MISSING_REFERENCE` e não é indexado pelo Atlas. A UI mostra **Referências relacionadas**
separadamente e conserva ausência como estado vazio. O mesmo ID em outra fonte nunca
resolve a menção corrente. Textos e URIs são inertes; links internos reutilizam o
contexto fonte/ID. Não acrescentar caminho de leitura, endpoint, schema ou perfil.

Os estados de disponibilidade vêm do leitor sem promoção: digest declarado não é
digest comparado; `MISSING` descreve somente o pacote observado; `EXTERNAL_UNRESOLVED`
não é download nem prova de indisponibilidade na origem. Referências sem observação
continuam `UNVERIFIED`. Nenhum desses estados autentica origem ou aceita ciência.
