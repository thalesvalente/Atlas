# Clarificações P01

As instruções da missão resolveram as decisões necessárias; nenhuma nova autorização
foi inventada. A investigação dos bytes públicos refinou os seguintes pontos:

1. Spec Kit é 1.2.3 do Atlas. O workstream não é a feature 020 de outro produto.
2. O recibo posterior [PR #5, 6406839421](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421)
   aceita ADR-0002 v1.0 como direção; estados históricos permanecem intocados.
3. A/B/C/D integrais não foram encontrados no universo delimitado. O resumo de C e
   os dois hashes alegados não autorizam reconstruir doze jornadas ou requisitos C-UX.
4. `entities` preserva entidades genéricas; a UI não oferece detalhe genérico. Essa
   lacuna não equivale a ausência de representação no pacote.
5. A identidade atual `source-N + @id` é local ao catálogo e depende de sua ordem.
   Digest de metadados identifica bytes observados, não uma fonte global/autenticada.
6. Worksheets JSON de P01 são exemplos documentais derivados. Não são aceitos pelo
   leitor como novo formato Caderno, não são sidecars obrigatórios nem novas APIs.
7. `SPECIFY_FEATURE_DIRECTORY` e `SPECIFY_FEATURE_NO_PERSIST=1`, já suportados pelo
   helper oficial, direcionam a execução ao workstream sem escrever `.specify/feature.json`.
8. Propostas futuras de tabelas/marcos não bloqueiam apresentações compatíveis C0.
