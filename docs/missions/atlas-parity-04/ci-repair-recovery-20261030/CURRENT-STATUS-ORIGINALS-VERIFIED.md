# AP04 — Artefatos originais recuperados, verificados e persistidos no Git

**Estado atualizado em 2026-10-30:** `ORIGINAL_ARTIFACTS_VERIFIED_AND_GIT_PERSISTED`. O arquivo `ORIGINAL-ARTIFACTS-STATUS.json` anterior permanece como recibo histórico válido do período em que os bytes não estavam acessíveis.

## Originais agora disponíveis

| Arquivo | SHA-256 conferido | Git blob SHA-1 conferido |
|---|---|---|
| [Patch](originals/ATLAS-PARITY04-DOC-CI-REPAIR-01.patch) | `d25540bce2a90dbf099ca38b82528b645ea49c92fd86d04438d5f1b7a58b83b8` | `d6ab785bc75634f8248e525580d01cf25b809d18` |
| [ZIP completo de engenharia e evidências](originals/ATLAS-PARITY04-DOC-CI-REPAIR-01-blocked-exact.zip) | `5788215d2267902988e141fa6db5a9434564b18204356a3a6d80a3dd2a883752` | `2dd4fc9f1f3ca425f00b3fb16de1ae1c4d5cb158` |
| [Instruções de aplicação originais](originals/APPLY-INSTRUCTIONS.md) | `59a915dd9e239f7bdc4be43b4447501bfc7290b57fdc1c4cfb01e425116d57c9` | `88ca9d498b744054498763f2401895f541783cb1` |

O ZIP passou a verificação de CRC (48 membros) e todas as 34 entradas do manifesto interno. O patch separado é byte a byte idêntico ao contido no ZIP. O patch contém 19 paths exatos (5 alterados, 14 novos). O arquivo `ORIGINALS-VERIFIED.json` distingue essas verificações de CI e revisão independente, que **não foram executadas neste registro**.

A verificação automática não encontrou segredos nem caminhos privados de host. Ela não substitui revisão humana de conteúdo.

## O que NÃO foi feito

- Nenhum patch foi aplicado na PR Draft #14.
- Nenhum teste Windows/Ubuntu, navegador, Spec Kit ou QA independente foi atribuído ao SHA de reparo.
- Não houve mudança de código, plano AP04-POR-v1.0-draft, ADR-0003, protocolo, manifestos históricos ou pins.
- Nenhuma worktree/clone nova, merge, release, deploy, promoção, migração ou operação em experimentos privados.

## Próximo ato

Consuma `NEXT-AGENT-INSTRUCTIONS.md` e os bytes originais desta branch. Aplique o patch exclusivamente à branch já existente da PR #14 após conferir sua baseline, faça testes e publicações por SHA e obtenha CI terminal e revisão independente. Não use o ZIP temporário do chat como dependência operacional.