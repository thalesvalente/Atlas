# Atlas — instruções de contribuição

Preserve a direção arquitetural ARC-01–09 na constituição e ADR-0001.
Use branches próprias, commits em português e PRs Draft. Não faça merge, release,
deploy nem alteração de licença sem aprovação específica.

Protocolo (`packages/protocol`) é independente da interface (`packages/atlas`).
A interface não executa experimentos, não aprova ciência e não migra ou apaga fontes.
Estado derivado nunca se torna autoridade científica. Não importe código de produtores
privados nem publique conteúdo privado sem manifesto e liberação específicos.

Use somente fixtures sintéticas ou fontes públicas com licença verificada. Releia
`specs/001-atlas021-protocol-interface` antes de alterar contratos. Sem chamadas pagas.

Spec Kit 1.2.3: instale em ambiente isolado. A feature ativa em `.specify/feature.json`
independe da branch. ORQ é o único writer desse estado durante esta missão.
