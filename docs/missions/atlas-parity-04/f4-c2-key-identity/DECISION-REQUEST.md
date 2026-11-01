# ARC-09 — pedido humano ÚNICO: atualização limitada 0.2.1

**Estado:** `INDEPENDENT_REVIEW_NOT_PROVEN` + `HUMAN_DECISION_PENDING`; esta pergunta é **condicional**, não pedido de assinatura antecipada. O SHA final deve ser conferido na PR antes de deliberar.
**Objeto exato:** diretório `docs/missions/atlas-parity-04/f4-c2-key-identity/` na branch `docs/atlas-parity04-f4-key-identity-20261101`, **commit SHA final da PR Draft**. Uma decisão só se aplica aos bytes daquele commit; branch móvel não serve como versão.
**Precedente:** `APPROVED_SCOPED` de 0.2.0 na PR#15, comentário `6539419419`, **NÃO** autoriza esta nova semântica ou implementação.

## Pergunta binária para aprovação ARC-09

**Após parecer de autor realmente independente no SHA exato, você APROVA ou REJEITA o adendo `atlas-legacy-presentation/0.2.1` exclusivamente para transporte/navegação de `parent_key` e `from_key/to_key` por `reference_basis=SOURCE_STRUCTURAL_KEY`, `node.source_key_literal`, `node.parent_key_literal` e `node.parent` já tipado, além de `reference.declared_key_literal`, sem promover `native_id`, segundo `DESCRIPTOR-0.2.1-CANDIDATE.md` e os negativos publicados?**

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

A revisão Copilot inicial registrou cinco findings contra o SHA anterior; correções autorais não substituem parecer de executor independente sobre o **novo SHA exato**. Até esse parecer, não solicitar ratificação de ARC-09. O status formal permanece `INDEPENDENT_REVIEW_NOT_PROVEN`. Silêncio, autoavaliação ou CI verde não são aprovação.
