# Validação sintética

Na raiz do Atlas, execute em Windows e Linux com Python 3.12 ou superior.

```text
python -B -m unittest discover -s tests/atlas_retention_binding -v
python -B -O -m unittest discover -s tests/atlas_retention_binding -v
```

Os testes criam arquivos temporários inventados e exercitam a CLI com o exemplo exportado da Feature 005. O contrato documenta a invocação com evidências entregues pela N01-R. [Inventário e CLI](contracts/local-inventory.md)
