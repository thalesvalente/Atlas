# Avisos de terceiros

Este arquivo registra materiais públicos incorporados à candidata. Não escolhe uma
licença para o Atlas, seu SDK ou seus exportadores novos. Direitos e avisos dos
autores originais permanecem aplicáveis aos materiais identificados abaixo.

## Contexto RO-Crate

`packages/protocol/src/caderno_protocol/resources/ro-crate-1.3-context.jsonld`
é uma cópia sem alteração do contexto de ResearchObject/ro-crate, tag `1.3.0`,
commit `22fbd7e098ccd2839c80967e363a2201528a2efe`, caminho
`docs/_specification/1.3/context.jsonld`.

- Fonte: https://github.com/ResearchObject/ro-crate/blob/1.3.0/docs/_specification/1.3/context.jsonld
- Licença: Apache License 2.0, reproduzida em `resources/APACHE-2.0.txt`.
- Atribuição: contribuidores e organizações identificados na especificação RO-Crate;
  aviso específico em `resources/NOTICE.txt`.
- Integridade dos bytes: catálogo de contextos e `docs/protocol/profile-manifest.json`.

## Exemplo oficial Process Run Crate

`examples/upstream/process-run-0.6/ro-crate-metadata.json` foi preservado sem alteração
de ResearchObject/workflow-run-crate, tag `0.6.0`, commit
`3c5b530c3d2784169e461d3273855a6b3a57246e`, caminho
`docs/profiles/0.6/process_run_crate/example1/ro-crate-metadata.json`.

- Fonte: https://github.com/ResearchObject/workflow-run-crate/blob/0.6.0/docs/profiles/0.6/process_run_crate/example1/ro-crate-metadata.json
- O repositório upstream usa Apache-2.0; a licença integral acompanha o exemplo em
  `LICENSE.txt`. Os metadados originais declaram CC0-1.0 para seu dataset.
- Atribuição e limites: `examples/upstream/process-run-0.6/NOTICE.md`.
- Fotografias e preview HTML não foram incorporados. O exemplo serve a um ensaio
  negativo de compatibilidade e não é apresentado como positivo do perfil Caderno.

## Ferramentas de desenvolvimento e pesquisa

Spec Kit `1.2.3` foi instalado separadamente da aplicação, a partir da distribuição
oficial. Os auxiliares e skills gerados localmente não compõem o runtime distribuído.
Fonte/licença upstream: https://github.com/github/spec-kit/tree/v1.2.3 (MIT).
A infraestrutura oficial gerada em `.specify/` e as skills em `.agents/skills/`
são versionadas para revisão e reprodução, sem alteração de seu conteúdo gerenciado.
O texto MIT upstream acompanha a infraestrutura em `.specify/UPSTREAM-LICENSE.txt`.

`jsonschema`, `roc-validator`, `rocrate`, Playwright e ferramentas de build são
dependências explícitas dos ensaios. Não são incorporadas como código do viewer
ou do SDK. Versões, origens e limites estão em `research/protocol-options.md`,
`docs/protocol/conformance.md` e nos workflows.

Nenhuma fonte privada, fixture derivada de fonte privada, caminho de host ou histórico
privado foi incorporado a esta árvore pública. A inspeção privada separada para
compatibilidade é declarada em `docs/coordination/publication-policy.md`; não há
alegação de processo clean-room.
