# Validação da ponte reaproveitada

1. No contexto privado do produtor, obtenha uma projeção pelo pipeline existente, somente onde essa aquisição já estiver permitida.
2. Entregue a projeção capturada ao adaptador, com seleção explícita e digest. Ele não deve reabrir fontes.
3. Valide o pacote com o SDK Caderno e abra-o com a instalação Atlas já existente, usando `atlas_viewer inspect` e `serve --source`.
4. Confira IDs, estados originais, revisão independente do resultado, métricas, referências e perdas do recorte.

Não executar novamente os comandos antigos de interpretação direta de índice. O guia privado acompanha a revisão da ponte e define as pré-condições; este documento não autoriza leitura de acervo, publicação, migração ou exclusão.

O runtime, o perfil e o schema públicos permanecem inalterados. Nenhum requisito de BIM ou SHACL é adicionado.
