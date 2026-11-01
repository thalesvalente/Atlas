# AP04-F4-C2-B — Política OS, limites e capacidades

**Contexto imutável**: ADR-0003-v0.2 `APPROVED_SCOPED`, F2, reader003 e precedência da via Caderno. Este componente é **somente um ensaio nativo de SO** para futura composição C2-D; não é aquisição privada nem valida paridade. Todos os dados do workflow são inventados internamente.

## Windows

- Worker confiável fixado em `os_worker.py`; lançado **suspenso**; Job criado com limite agregado `JOB_OBJECT_LIMIT_JOB_MEMORY=268435456` de **committed bytes**. Limites consultados por `QueryInformationJobObject`; `KILL_ON_JOB_CLOSE` e `BREAKAWAY_OK=0`; somente depois `AssignProcessToJobObject`/retomada. Terminador monitorado pelo supervisor usa **wall clock monotônico 30 s**; não substituído por `JOB_OBJECT_LIMIT_JOB_TIME`.
- Contraprovas: 300MiB, sleep 90s, filho bloqueado, tentativa de breakaway, falha forçada de associação sem retomada, encerramento de descendentes e ausência de descriptor publicável.
- Caminhos do worker de teste são gerados internamente a partir de literais inventados. Scratch 0700 equivalente: criação Windows com descritor de segurança explícito **protegido** e dono SID do token atual, ACEs de owner+SYSTEM; rechecagem com `GetNamedSecurityInfoW`, `GetAce` e `EqualSid`, negando trustees não permitidos. Não alterar ACLs de outras pastas, fontes ou host.
- **Diferenciação obrigatória**: privacidade do scratch de teste não confina leitura/escrita do WORKER em outros caminhos. Job Object **não bloqueia rede**. Sem AppContainer/LPAC ou broker, esse requisito F2 está **NÃO IMPLEMENTADO** para Windows; `C2_B_OS_BLOCKED_EXACT`.

## Ubuntu Linux

- `prctl(NO_NEW_PRIVS)`, `PR_SET_PDEATHSIG=SIGKILL`; Landlock v3+ file-level RO na fixture fonte exata, RW somente no scratch próprio; `seccomp-BPF` veda criação de sockets e novos processos/exec, com `SECCOMP_RET_KILL_PROCESS` para arquitetura não esperada; sem herança de descritores via `close_fds=True`.
- `RLIMIT_AS` igual a **256MiB de espaço de endereçamento virtual** e `RLIMIT_CORE=0`; essas métricas diferem de committed Job e RSS/cgroup v2. Nenhuma afirmação falsa de equivalência de medidas.
- Prazo de 30s supervisor externo monotônico, `killpg`, espera terminal; testes recusam escrita fora do scratch, abertura de arquivo fora da allowlist, sockets loopback/IPv6, fork, OOM virtual, timeout, forma de reporter 0600 e ausência física de descriptor.
- Se Landlock ABI <3, seccomp indisponível, plataforma desconhecida, scratch inseguro ou limite falho: **bloqueio**, nunca substituição por deadline cooperativo.

## Política de CI e gates

- `windows-latest` e `ubuntu-latest` com worker normal (`optimize=0`) e worker otimizado (`optimize=1`). **Pytest sempre com asserts ativos**, independentemente do worker. O recibo audita `git rev-parse HEAD == ATLAS_CHECKOUT_SHA`, JUnit com pelo menos um teste executado, zero falhas e erros, e falha com exit code não-zero no caso contrário.
- Artefatos do GitHub Actions são JUnit e `observed-ci.json` sob `.test-output/`, retidos no serviço, não dados científicos. A rotina preserva bloqueio `PRODUCTION_ACQUISITION_BLOCKED` mesmo se todos testes passam.
- Contribuição C2-B não altera `reader.py` de C2-A, schema do descriptor, arquivo histórico/manifesto antigo, workflow congelado, `AGENTS.md`, `feature.json`, R4 ou planos.
- Não executar replays R4, inferências/providers, importação de fontes reais ou chamadas externas de rede. G4 continua `BLOCKED`, G5/G6 `NOT_APPROVED`.

Fontes técnicas: [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects); [Microsoft AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer); [Linux Landlock](https://docs.kernel.org/userspace-api/landlock.html).
