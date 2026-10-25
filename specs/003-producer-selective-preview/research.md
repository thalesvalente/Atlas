# Pesquisa focal e reutilização
- SDK público `caderno-protocol` 0.1.0a1: validar pacote RO-Crate restrito, sem busca remota.
- Viewer `atlas-viewer`: índice reconstruível, leitura e visualização independentes do produtor.
- Adaptador privado anterior: somente entradas sintéticas, explicitamente proibida a conversão de dados reais por aquela API.
- Índice de origem histórico: projeção registrada, não prova de autenticidade de todo o ledger nem garantia de que payloads referenciados estejam disponíveis.

**Escolha:** ponte privada nova e somente leitura sobre um índice explícito, preservando o exportador original; o Atlas consome metadados por contrato público. Não reconstruir os padrões nem introduzir segundo formato concorrente.
