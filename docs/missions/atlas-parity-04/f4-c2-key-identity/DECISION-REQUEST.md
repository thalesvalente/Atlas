# ARC-09 — objeto imutável e pergunta condicional

**Estado:** INDEPENDENT_REVIEW_NOT_PROVEN + ARC09_HUMAN_DECISION_PENDING. A proposta 0.2.1 não foi aprovada e não foi implementada. Não solicitar ratificação antes do parecer independente e dos gates aplicáveis.

## Identidade exata, sem autorreferência de commit

**Commit do objeto normativo:** `d5bdc86ef68cad2f5d503945ca788c3a74df4839`.
**Tree desse commit:** `c362df15ffebc1a0fd94f387ee9aacc47e94fc5b`.
**Parent:** `508ccb257a44dc66da13d1edfec7f00ef5231d09`.

O objeto de ARC-09 é exclusivamente o conjunto de cinco arquivos abaixo nesse commit, dentro de `docs/missions/atlas-parity-04/f4-c2-key-identity/`. Não é a branch móvel nem todo o estado histórico dos recibos em seu parent. Este recibo é sucessor documental e não altera os cinco blobs. O SHA/tree/parent do HEAD publicado e o review desse HEAD ficam no recibo append-only da PR #21; o parecer deve confirmar também a igualdade desses blobs com o objeto congelado. Isso evita tentar inserir em um arquivo o SHA do próprio commit que o contém.

| Arquivo normativo | Git blob SHA-1 |
|---|---|
| COMPATIBILITY-AND-MIGRATION-LESS.md | `351335256804a41a4f0638c0943937e5ef9cced3` |
| CURRENT-CONTRACT-COUNTEREXAMPLES.md | `1504abff97f25431a50cafe280c2c8e94450ec14` |
| DESCRIPTOR-0.2.1-CANDIDATE.md | `b3fb57b91263e6ea7686039f46400eecf30815b9` |
| OPTIONS-AND-RISK.md | `a3b43305f78926675113b1012520bfb92ceed31a` |
| SYNTHETIC-IDENTITY-FIXTURES.json | `49dc02a5fed21d9f6cca074e8511dd006f6fda2c` |

Os respectivos SHA-256 constam de HANDOFF.json; MANIFEST.sha256 protege o pacote documental atual. INPUT-SHAS.json preserva a proveniência histórica. Qualquer alteração nesses cinco blobs exige novo objeto congelado, revisão e decisão; não estender uma aprovação a bytes posteriores. Recibos não conferem autorização.

## Pergunta binária única — ainda não submetida à ratificação

Após parecer comprovadamente não autor no HEAD publicado e igualdade com o objeto acima, **APROVA ou REJEITA o adendo atlas-legacy-presentation/0.2.1 exclusivamente para transporte/navegação estrutural legada**, com `node.source_key_literal`, `node.parent_key_presence`, `reference.reference_basis` e `reference.declared_key_literal`, preservando parent/parent_key_literal já requeridos, native_id nativo e as regras de ausência/null/tipo/ciclo/limite documentadas?

APPROVED_SCOPED 0.2.0 da PR #15/comentário 6539419419 NÃO autoriza esta semântica. Uma aprovação futura autoriza somente implementação posterior testada e revisada pelos owners C2/F3A/F3B, com gates próprios. NÃO aprova C3 antecipado, extensão Caderno, conteúdo privado, G4/G5/G6, F5, confiança científica, merge, release, deploy, migração, limpeza ou alteração R4.

## Modelo não assinado

```text
ARC-09 / AP04 F4 C2-K: APROVO [ou REJEITO]
Descriptor: atlas-legacy-presentation/0.2.1
Escopo: cinco blobs normativos acima; LEGACY_DERIVED
Commit do objeto: d5bdc86ef68cad2f5d503945ca788c3a74df4839
Tree do objeto: c362df15ffebc1a0fd94f387ee9aacc47e94fc5b
Parecer independente: <executor distinto, SHA completo do recibo revisado, findings>
Restrições adicionais: <texto ou nenhuma>
```

Silêncio, publicação, CI verde, bot ou autoavaliação não são aprovação. O parecer deve apontar findings reproduzíveis e distinguir CI de sucessão, revisão independente e decisão humana.
