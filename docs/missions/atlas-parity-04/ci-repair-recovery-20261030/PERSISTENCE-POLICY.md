# Regra de persistência para todas as próximas frentes Atlas

**Motivo:** o operador executa vários chats paralelos e não pode ser incumbido de baixar manualmente ZIPs entre sessões.

1. Toda entrega publicável deve ser persistida em **GitHub `thalesvalente/Atlas` antes do handoff**, em branch/PR de ownership específico. Registrar SHA completo, tree, parent, paths, hashes e link do PR/commit.
2. O Git é a fonte de verdade dos artefatos públicos: prompts, código, patches, testes, contratos, decisões, resultados sanitizados e manifestos suplementares. Um link `sandbox:/...` é conveniência de transferência, não fonte de verdade durável.
3. Patch/ZIP criados em sessão não podem ser declarados entregues se só existem num sandbox efêmero. Se o Git não aceitar binários ou a conexão for somente leitura, declarar `PERSISTENCE_BLOCKED` e manter o resultado explicitamente incompleto.
4. Evidência privada deve ficar em armazenamento **privado autorizado**, sem upload ao repositório público; versionar somente hashes e recibos sanitizados. Não registrar nomes/caminhos/IDs privados sem permissão.
5. Nunca empilhar gravações em uma mesma worktree. Priorizar branch existente e exclusividade de ownership; não criar worktrees/clones extras para contornar bloqueios.
6. Recibos por SHA: CI, parecer independente, browsers e QA de um SHA não são provas de outro. Handoffs finais sempre incluem provas terminais reais.
7. Mudança em `AP04-POR-v1.0-draft`: justificar, comparar decisões anteriores e obter aprovação aplicável, inclusive ARC-09 quando houver desvio. Não afrouxar gate/manifesto/pin por conveniência.
8. Fechamento de qualquer missão deve explicitar `PUBLIC_ARTIFACTS_GIT_PERSISTED=true/false` e `PRIVATE_ARTIFACTS_STORAGE_PERSISTED=true/false/NOT_APPLICABLE`.

**Observação:** esta política é proposta documental do handoff e não altera unilateralmente os gates arquiteturais ou a governança da PR #14.
