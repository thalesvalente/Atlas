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
