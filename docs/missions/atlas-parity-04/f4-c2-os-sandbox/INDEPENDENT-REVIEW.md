# AP04 F4-C2-B — revisão independente

**Status**: `INDEPENDENT_REVIEW_NOT_PERFORMED`; não há parecer independente aprovador.

Na sessão autora não foram expostas ferramentas nativas reais de `spawn_agent`, `send_message` ou `wait` nem equivalentes de delegação. O código e os testes foram escritos pelo mesmo executor; inspeções do próprio autor não contam como QA independente. Runs automáticos da CI atestam execução, não independência de análise de segurança. Uma revisão GitHub Copilot somente contará se houver comentário/parecer identificável, com autor distinto, SHA final e escopo claro.

**Autoavaliação não independente**:
- Confirmada por diff GitHub a adição/edição apenas dos sete paths novos da branch, sem alteração de C2-A nem fonte privada.
- `Job Object` realmente limita recursos, não FS/rede: Windows bloqueado para aquisição.
- Linux Landlock/seccomp e memory VAS testados em fixtures, mas não foram testados crash do supervisor, todas as corridas de handle, fontes reais e host do operador.
- Nenhuma simulação de resultado de revisão nativa ou autorização humana.
- Diferenças de métricas de memória e as lacunas têm registro explícito nos outros recibos.

**Pedido de QA distinto (owner exclusivo read-only)**: inspecionar os blobs exatos no SHA terminal desta branch; reproduzir todos os testes GitHub em `windows-latest` e `ubuntu-latest` e `PYTHONOPTIMIZE=0/1`; verificar que Job Object não declara FS/rede, que os child handles/cancelamento funcionam, que Landlock/seccomp não permite acesso fora da allowlist, que timeout/OOM deixam zero descriptors e que os testes exercitam negação real; identificar lacunas com reproduções e emitir parecer assinado por autor distinto no próprio SHA. Não implementar C2-A, não mesclar PR #18, não aprovar G4.
