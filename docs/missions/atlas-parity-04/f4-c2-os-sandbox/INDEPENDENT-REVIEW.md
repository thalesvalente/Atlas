# AP04 F4 C2-B — revisão independente real e seu estado

**Subagentes nativos deste CHAT:** nenhum `spawn_agent` / delegação nativa real disponível; nenhum agente foi simulado.

**Revisor distinto de autoria:** `copilot-pull-request-reviewer[bot]` publicou três revisões identificáveis na [PR Draft #20](https://github.com/thalesvalente/Atlas/pull/20), incluindo o primeiro [review 5726283233](https://github.com/thalesvalente/Atlas/pull/20#pullrequestreview-5726283233), todas no estado `COMMENTED` / `Changes recommended` (não `APPROVED`). Revisor analisou SHAs anteriores; não se deve inferir aprovação do SHA técnico final a partir de um parecer anterior.

## Findings com evidência, correção e status de review

| Thread | Risco apontado pelo revisor | Correção executada por C2-B | Status |
|---|---|---|---|
| [4434295500](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295500) | arquitetura seccomp errada podia cair em default allow por truncamento de opcode | `BPF_RET` com `SECCOMP_RET_KILL_PROCESS` em campo `k` e teste da instrução | AWAITING_FINAL_REREVIEW |
| [4434295516](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295516), [4434317843](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317843) | ancestors symlink/junction/reparse sem verificação | `lstat` de cada ancestral em supervisor e worker, bit Windows `0x400`, testes reais de symlink e junction | AWAITING_FINAL_REREVIEW |
| [4434295523](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295523), [4434305776](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434305776) | origem de fixture arbitrária mesmo sob nomes parecidos | API pública sem parâmetros de paths; bytes inventados no interior de `TemporaryDirectory`, preflight de dono/tipo e recusa de chamadas externas | AWAITING_FINAL_REREVIEW |
| [4434305804](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434305804), [4434317872](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317872) | worker executável diretamente podia receber path privado | novo preflight no entrypoint do worker, verificação de PID parent, árvore sintética, symlinks e owner/ACL; contraprova chamada direta recusa | AWAITING_FINAL_REREVIEW |
| [4434317862](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317862) | validador do Job aceitava argumentos adicionais/alterados | confere todas flags e valores e reusa `_preflight`; contraprovas de vetor adulterado | AWAITING_FINAL_REREVIEW |
| [4434295530](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295530) | scratch Windows herdava ACL não privada | criação de scratch **somente teste** com SDDL protegida e owner explícito; consulta GetNamedSecurityInfo/GetAce/EqualSid, ACE desconhecida recusada; falhas Windows reais em iterações anteriores foram consertadas e reexecutadas | AWAITING_FINAL_REREVIEW |
| [4434295537](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295537) | `PYTHONOPTIMIZE=1` apagava asserts do pytest | pytest sempre sem otimização; `-O` apenas no worker, com flag comprovada na evidência | AWAITING_FINAL_REREVIEW |
| [4434295547](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434295547), [4434317883](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317883), [4434317890](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317890) | suite all-skipped ou falha JUnit/checkout incorreto podia gerar PASS | exigência de executados >0, `git rev-parse HEAD == ATLAS_CHECKOUT_SHA`, exit nonzero por falhas; contraprovas locais em CI | AWAITING_FINAL_REREVIEW |
| [4434317903](https://github.com/thalesvalente/Atlas/pull/20#discussion_r4434317903) | socketpair syscall 199 omitida no AArch64 | syscall 199 incluída no deny set e teste **estrutural** do BPF AArch64 no Ubuntu amd64; runtime arm64 não executado | AWAITING_FINAL_REREVIEW |

Demais observações do review (tempo wall estrito, fonte sintética, proteção de arquivo/descriptor, não ignorar symlink Windows) foram incorporadas aos testes nativos. Não foram executadas provas de crash adversarial completa nem as corridas de FDs/handles contra host com permissões reais.

## Distinções que impedem aprovação

1. O **Job Object** é supervisor de prazo/memória/descendentes, **não é** sandbox de rede/filesystem. A ACL privada protege somente o scratch de teste, não o namespace de leitura/gravação do worker Windows. Sem AppContainer/LPAC ou broker equivalente **enforced** → `WINDOWS_FS_NETWORK_OS_PROFILE_MISSING`.
2. Landlock+seccomp foram exercitados em runners Linux com fixtures inventadas. Isso **não** autoriza abrir fontes reais; C2-D/host L1 são outras frentes e dependem de autorizações explícitas.
3. O Copilot avaliou código e publicou findings reais, mas **nenhuma revisão distinta assinou aprovação do SHA terminal**. Não resolver automaticamente threads do revisor apenas porque o próprio autor implementou correções.
4. Workflows globais da PR #20 podem falhar sob checks de proveniência ou congelamento. Esses gates não foram contornados, alterados ou declarados verdes.

**Avaliação formal:** `INDEPENDENT_REVIEW_PERFORMED_WITH_FINDINGS_NO_FINAL_APPROVAL`. A implementação focada continua `C2_B_OS_BLOCKED_EXACT`, mesmo com CI focal `OBSERVED_PASS`. Sem G4/G5/G6/merge/release/deploy.
