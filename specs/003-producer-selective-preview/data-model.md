# Dados — projeção do produtor → Caderno

| Conceito | Responsável | Resultado interoperável |
|---|---|---|
| Aquisição/normalização | Pipeline existente do produtor | Projeção capturada, não criada pelo viewer |
| Identificadores | Produtor + adaptador | IDs absolutos com namespace e mapa reversível |
| Estado técnico/revisão | Fonte, preservados separadamente | Vocabulário Caderno conservador + literais originais |
| Métrica/parâmetro | Fonte tipada | PropertyValue quando tipo/unidade forem conhecidos |
| Referência sem direção | Fonte | File e menção declarada; não inventar input/output |
| Derivação tipada | Projeção existente | Relação mapeada apenas quando a semântica estiver definida |
| Dados fora do recorte | Fonte/manifesto | Contagem e lacuna, sem registros artificiais |
| Pacote resultante | Adaptador | Metadados + fonte selecionada + manifesto; estado derivado |

O arquivo de fonte selecionada não é um segundo protocolo nem o ledger original. Ele permite conferir a transformação; o contrato de troca continua sendo o Caderno.

## Modelo derivado aditivo CLOSE01

`runs[].related_references` é uma lista de `{id, name, types, description,
declared_digest, availability}` resolvida exclusivamente nas entidades do próprio
Package. `name` usa ID como fallback; `types` tem ordem estável; `availability`
copia a observação do leitor, ou `{"status":"UNVERIFIED"}` se não houver observação.
O digest declarado é separado de `availability.sha256`, calculado quando disponível.
Deduplicação por ID preserva a primeira menção, sem filtrar referências que também
estejam em inputs/outputs. A UI mantém o contexto da fonte do run; lista ausente em
modelo antigo equivale ao estado vazio, não a erro de protocolo.

Esse campo não é serialização persistida nem estado científico. Metadados sem payload
não viram conteúdo verificado. `Catalog.rebuild()` substitui apenas o índice em memória.
