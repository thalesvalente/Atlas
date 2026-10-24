# Converge — fechamento por evidências exatas

Missão ATLAS021-A-POC-R4-FOCO01. Data de referência: 2026-10-24.
Escopo funcional implementado e revisado independentemente; a conclusão de
publicação/CI/Codex/handoff será registrada append-only nas PRs e coordenação privada.

## Resultado antes da publicação

| Gate | Evidência disponível | Estado neste arquivo |
|---|---|---|
| POC_R4_EXPORT | caminho real com fonte sintética, comparação semântica e carrier idêntico; recibos privados | PASS_SCOPED local |
| POC_ATLAS_IMPORT | SDK/viewer wheels em venvs vazios; mesmo viewer, sem produtor, readback/reindex | PASS_SCOPED local |
| POC_UI_R4 | UI real com cada fonte; ausências e comparação compatível própria | PASS_SCOPED local, recibo privado |
| POC_NEGATIVE_TESTS | 71 testes públicos por modo, mais negativas produtoras no privado | PASS_SCOPED local |
| POC_CI_REVIEW | A4 sem P1/P2 aberto; CI e Codex remotos precisam do SHA publicado | PENDING_PUBLICATION |
| POC_SCOPE_LOCK | ADRs/constituição/perfil/packages sem alteração, dois produtores existentes | PASS_SCOPED |
| POC_HANDOFF_B | contrato e conteúdo preparados; publicar após fixar par final | PENDING_PUBLICATION |

POC_TECHNICAL_READY ainda não é declarado true por este documento pré-publicação.
T014–T016 não são encerradas pelo código ou pelo revisor local. O recibo final
append-only deve citar os dois SHAs, árvores, perfil/digest, jobs/URLs, resultado
Codex de cada HEAD, revisão A4, ausência de findings abertos e locator do handoff.
Esse recibo fecha as três tarefas sem alterar os próprios HEADs verificados.

## Cobertura e diferenças em relação à baseline

O produto candidato foi reaproveitado. Incrementos: comando privado persistente,
variante sintética comparável mantendo default, harness que percorre todas as
execuções/relações/ausências e compara por fonte, três negativas públicas faltantes,
documentação de reprodução/mapeamento e recibos. Pacotes runtime/schema não mudaram.

Analyze: dez FR, quatro NFR e quatro SC ligados a dezesseis tarefas; sem contradição
constitucional ou ambiguidade bloqueante. Checklists: 12 requisitos do autor e
14 critérios de segurança/arquitetura revisados por A4; não são testes de runtime.

Testes de referência RO-Crate anteriores mantêm seus próprios SHAs e limites.
O workflow herdado pode executá-los novamente; registrar seu resultado efetivo sem
confundi-lo com certificação integral Process Run0.6.

## Decisões independentes

ADR-0002 v1.0/perfil0.1.0a1 permanece PENDING_HUMAN. Merge, release/licença,
estabilização, promoção canônica, dados reais e operações físicas não foram
aprovados. PUBLIC-SOURCE-TRANSFER=[]. Dependência histórica do runtime não é
disposição total dos arquivos. Conteúdo/consumidores/recuperabilidade históricos
continuam desconhecidos quando não há prova, preservados no handoff privado.

## Regra de atualização

Mudança de código, protocolo, snapshot ou pin do par exige revalidação proporcional.
Não transferir CI/Codex de um HEAD anterior. Correções de review devem produzir
novo commit, testes afetados e revisão do novo HEAD antes de declarar gate completo.
