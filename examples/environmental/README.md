# Produtor ambiental independente — somente dados sintéticos

Este exportador usa o contrato público do Caderno e não importa qualquer
adaptador privado. Os valores, pessoas/equipes e medições são fictícios.
Há 2 projetos, 3 experimentos e 4 execuções; os estados são COMPLETED,
PARTIAL, FAILED e UNKNOWN, com revisão UNKNOWN/HOLD, valores ausentes,
unidades, entradas/saídas e derivação.

Instale o SDK candidato e execute em diretório **novo**:

```bash
python examples/environmental/export.py output-environmental
python -m caderno_protocol output-environmental
```

`sample/` contém o resultado positivo versionado. O campo `datePublished` é uma
data declarada do snapshot sintético, e não uma coleta real. O arquivo externo
em example.invalid não é baixado nem sua disponibilidade é presumida.

Para testar referência local ausente ou digest incorreto, os testes trabalham
com uma cópia temporária e alteram/removem um payload dessa cópia. Não se altera
o fixture positivo ou uma fonte científica para gerar o estado de demonstração.

O exportador recusa sobrescrever um diretório existente. A saída pertence ao
ensaio; exportar não executa um experimento real nem aprova ciência.
