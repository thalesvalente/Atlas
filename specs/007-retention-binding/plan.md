# Plano — Feature 007

## Technical Context

CLI offline em Python 3.12+ e biblioteca padrão, fora dos pacotes do Atlas. Leitura de arquivos locais regulares em Windows e Linux. Dados de teste inventados e o exemplo público da Feature 005.

## Constitution Check

ARC-01–09 aplicadas. Propostas, vínculos, digest, autenticação de origem, preservação física e decisão humana são evidências distintas. Atlas continua como interface. A N02 fica em `tools/atlas_retention_binding/**`, `tests/atlas_retention_binding/**` e `specs/007-retention-binding/**`.

## Reconciliação

A PR #33 está aberta em Draft sobre a #32. Sua ponta e a branch `feat/atlas-experiment-triage-20261105` apontam para `46e18bd5c90b922b78cf6731f83ceedc4c09df85`, tree `64a4f683b9f30329b67feedbf30aedcddd1b7d0e`. A N02 parte desse commit e mira a branch da #33. A reconciliação antes do push confirmou 007 livre nas refs remotas. A publicação paralela da Feature 006 reservou o número utilizado no RED inicial. O corpo histórico da #33 registra um candidato anterior. A verificação do head usa refs e recibos por SHA.

## Design

1. Conferir os bytes dos documentos com pins externos. Validar e reconciliar a cadeia de inventário, o plano e os DTOs antes de abrir dados do acervo.
2. Resolver referências do inventário sob handles de diretório. Hash e tamanho vêm do mesmo handle e o vínculo do nome é reconferido antes de aceitar o objeto.
3. Indexar os vínculos de todas as ocorrências para encontrar dependências fora da seleção. Relatar proteção e lacunas com contagem por arquivo físico verificado.
4. Registrar evidências de RED, GREEN, adversarial, CI e review no handoff externo ligado ao SHA terminal.

## Qualificação

O workflow `ATLAS021 candidate verification` roda em PRs e qualifica a regressão existente no head da proposta. Sua descoberta é restrita a `packages/protocol/tests`, `tests/qa` e `tests/viewer`. A suíte focal N02 roda separadamente em Windows e Ubuntu sem alteração dos workflows ou caminhos de teste de outras frentes. A qualificação deve distinguir essas duas evidências.

O contrato de integração está em [inventário e CLI](contracts/local-inventory.md). A execução sintética está em [quickstart](quickstart.md).
