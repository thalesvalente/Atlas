# AP04 F4-C2-B — política de isolamento e capacidades observáveis

## Windows (runners GitHub)

- **Implementado e ensaiado**: `CreateJobObjectW`, `SetInformationJobObject`, `QueryInformationJobObject`, `JOB_OBJECT_LIMIT_JOB_MEMORY=268435456`, `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, `CreateProcessW(CREATE_SUSPENDED)`, associação antes de `ResumeThread`, `TerminateJobObject` e consulta de `ActiveProcesses` após timeout.
- **Escopo de memória**: committed bytes agregado do Job. Não confundir com RSS, working set ou tempo CPU.
- **Escopo de deadline**: relógio monotônico do processo supervisor, 30 s, incluindo worker bloqueado/descendente, sem usar `JOB_OBJECT_LIMIT_JOB_TIME` como wall clock.
- **Não implementado**: AppContainer/LPAC ou broker de handles/ACL. Job não restringe filesystem e rede, sequer o loopback; nunca afirmar que a execução Windows foi confinada nessas dimensões.
- **Perfil proposto ao próximo owner**: AppContainer/LPAC sem capabilities de rede, com fonte inventada exata read-only e scratch próprio, process creation suspenso e Job; testes de `CreateFileW`, write e conexão loopback/external. Não criar perfis, ACLs ou políticas do computador pessoal sem autorização. API experimental `CreateProcessInSandbox` depende do SO e de especificação compilada; a presença documental não é evidência do runner.
- **Status**: `OS_CONTROL_IMPLEMENTED` para Job; `OS_CONTROL_TESTED_IN_RUNNER` para Job no SHA com CI verde; `NOT_SUPPORTED` para FS/rede até implementação e contraprovas; `HOST_UNVERIFIED`.

## Linux (runners GitHub)

- **Implementado**: Landlock ABI >=3 (`landlock_create_ruleset`, `landlock_add_rule`, `landlock_restrict_self`) sobre um arquivo exato read-only e scratch privado RW, seccomp BPF bloqueando socket/fork/clone/exec, `NO_NEW_PRIVS`, `PDEATHSIG`, `RLIMIT_AS=256 MiB`, `RLIMIT_CORE=0`, umask 077.
- **Escopo de memória**: `RLIMIT_AS` é teto de virtual address space do worker, não um contador cgroup v2 de memória residente. `fork/clone` é negado para evitar soma de processos; kernel/host memory fuera do address space não é contabilizado da mesma forma.
- **Escopo de rede**: chamada de criação de socket AF_INET/AF_INET6 negada pelo SO; sem socket herdado no processo criado com `close_fds=True`.
- **Fallback**: Landlock ABI <3, seccomp não disponível, OS não reconhecido, scratch impróprio, perfil incompleto → `OS_ISOLATION_UNVERIFIED` e recusa; **sem bypass cooperativo**. Não criar cgroups sem delegação.
- **Status**: `OS_CONTROL_IMPLEMENTED`; `OS_CONTROL_TESTED_IN_RUNNER` apenas para as contraprovas observadas e o SHA correspondente. Testes Linux não qualificam host Windows do operador.

## Direitos e fontes

Norma F2: no máximo 3 entradas allowlisted, fonte somente leitura, scratch temporário privado fora do checkout/acervo; sem recursão, ZIP, provider, código R4 ou rede. Limites 64 MiB por arquivo, 192 MiB combinado e descriptor 32 MiB permanecem de responsabilidade de reader/C2-D, não são alterados aqui. Não há produção nesta branch.

Referências públicas oficiais: [Microsoft — Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer); [Microsoft — JobObject extended limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information); [Linux kernel — Landlock](https://docs.kernel.org/userspace-api/landlock.html).

**Restrição mandatória**: operação real fica em `PRODUCTION_ACQUISITION_BLOCKED` até Windows FS/rede e demais invariantes testados e validados por revisão independente. Nenhuma aprovação de G4/G5/G6.
