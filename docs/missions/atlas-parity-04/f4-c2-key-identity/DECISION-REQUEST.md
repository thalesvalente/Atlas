# ARC-09 — pedido humano ÚNICO: atualização limitada 0.2.1

**Estado:** `INDEPENDENT_REVIEW_PENDING` + `HUMAN_DECISION_PENDING`.
**Objeto exato:** diretório `docs/missions/atlas-parity-04/f4-c2-key-identity/` na branch `docs/atlas-parity04-f4-key-identity-20261101`, **commit SHA final da PR Draft**. Uma decisão só se aplica aos bytes daquele commit; branch móvel não serve como versão.
**Precedente:** `APPROVED_SCOPED` de 0.2.0 na PR#15, comentário `6539419419`, **NÃO** autoriza esta nova semântica ou implementação.

## Pergunta binária para aprovação ARC-09

**Após parecer de autor realmente independente no SHA exato, você APROVA ou REJEITA o adendo `atlas-legacy-presentation/0.2.1` exclusivamente para transporte/navegação de `parent_key` e `from_key/to_key` por `reference_basis=SOURCE_STRUCTURAL_KEY`, `node.source_key_literal` e `reference.declared_key_literal` separados de `native_id`, segundo `DESCRIPTOR-0.2.1-CANDIDATE.md` e os negativos publicados?**

Aprovar autoriza **somente** implementação posterior, testada e revisada em C2/F3A/F3B pelos owners, após gates próprios. NÃO aprova C3 antecipado, extensão do Caderno, transferência de conteúdo privado, G4/G5/G6, F5, confiança científica, merge, release, deploy, migração, limpeza ou alteração R4.

**Modelo de registro (exemplo NÃO assinado):**

```text
ARC-09 / AP04 F4 C2-K: APROVO [ou REJEITO]
Descriptor: atlas-legacy-presentation/0.2.1
Escopo: somente navegação estrutural legada, LEGACY_DERIVED
SHA completo dos documentos revisados: <commit-git-40-hex>
Parecer independente: <revisor-distinto, local, SHA, findings>
Restrições adicionais: <texto ou nenhuma>
```

A revisão independente está documentada como PENDENTE em `INDEPENDENT-REVIEW.md`, não como realizada. Silêncio, autoavaliação ou CI verde não são aprovação.
