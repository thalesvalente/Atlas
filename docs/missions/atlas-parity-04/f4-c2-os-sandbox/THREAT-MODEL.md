# AP04-F4-C2-B — Threat model e fronteiras verificadas

Missão: `AP04-F4-C2-B-OS-SANDBOX-CHAT-01`. Contrato: ADR-0003-v0.2 `APPROVED_SCOPED` e F2. Evidência física limitada a GitHub Actions com **fixtures inventadas internamente**. A aquisição real permanece bloqueada.

| Fronteira | Ataque/contraprova | Controle implementado | Limite residual |
|---|---|---|---|
| API pública do supervisor | Passar caminhos privados ou fixture externa | `run_synthetic_probe(mode)` **não aceita caminhos**; cria arquivos exatos inteiramente inventados em `TemporaryDirectory`; `require_production_acquisition` sempre lança `PRODUCTION_ACQUISITION_BLOCKED` | É API de teste, não interface geral para dados científicos; não equivale a autorização do host |
| Entrada do worker | Iniciar antes de recursos | Windows `CreateProcessW(CREATE_SUSPENDED)` + `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` com AppContainer próprio, token/SID verificados antes de retomar, Job configurado/consultado; Linux ativa Landlock/seccomp antes de abrir fixture | Perfil Windows testado com fixture inventada, não broker geral de fonte real; invariantes de handles/host adversarial exigem QA independente |
| Windows memória/processos | 300MiB, árvore descendente, quebra Job | Job com `JOB_OBJECT_LIMIT_JOB_MEMORY=256MiB` (committed bytes agregados), `KILL_ON_JOB_CLOSE`, sem breakaway; `TerminateJobObject`, consulta `ActiveProcesses=0`; testes no AppContainer para OOM, filho negado/encerrado, breakaway e prazo | Job por si não confina filesystem/rede; AppContainer permanece restrito aos fixtures testados e não autoriza aquisição |
| Windows scratch inventado | DACL permissiva, owner diferente, path reparse | Diretório sintético novo com SDDL privado SYSTEM+owner; verifica owner/ACEs/herança e rejeita ancestrais reparse; AppContainer tem somente handle de escrita do relatório previamente aberto no scratch | AppContainer não é LPAC e possui acessos padrão a recursos de sistema/ao próprio perfil; não demonstrado isolamento genérico de todos os paths fora da fixture |
| Linux memória | Alocação >256MiB | `RLIMIT_AS=268435456` para endereçamento virtual e `RLIMIT_CORE=0`; fork/clone vedados em seccomp | Não equivale a `memory.max` cgroup v2 ou RSS |
| Linux filesystem | Abrir fixture fora da allowlist / alterar original | Landlock ABI>=3 regra por arquivo fonte somente read, scratch privadamente 0700, umask077, sem execução de arquivos | Dir/FD races e TOCTOU completos exigem auditoria adicional |
| Linux rede | Socket loopback/externo | seccomp BPF bloqueia socket e criação de processos; sem inherited FDs no `Popen` `close_fds=True`; auditoria de arquitetura inesperada usa `SECCOMP_RET_KILL_PROCESS` com opcode `BPF_RET` | Não executar experimento real de rede externa nem ler dados privados |
| Prazo independente do worker | 90s de sleep, deadlocks, tarefa descendente | Supervisor mede monotonic elapsed 30s (não CPU), encerra Job/grupo; Windows termina descendentes; Linux mata grupo | Exigir prova de crash host/worker com falha de supervisor em qualificação posterior |
| Publicação atômica | Timeout/OOM deixam descriptor aparentemente completo | Harness inspeciona scratch próprio e confirma **zero** `atlas-c2-*.json` e origem inventada inalterada; worker JSON receipt usa `open('x')` | Não existe integração ao `reader.prepare` da frente C2-A/C2-D nesta branch |
| Validade da CI | `-O` apaga asserts, resultado all-skipped vira verde | pytest sempre `PYTHONOPTIMIZE=0`, worker alterna `-O` via env; checker requer JUnit com testes executados+zero erros/falhas e SHA de checkout exato | CI focal ≠ gates globais congelados nem revisão final humana |

## Decisões conservadoras

- A matriz Linux prova negativas nativas nos runners Linux. A matriz Windows atual executa **AppContainer nativo sem capabilities de rede**, verifica SID do token suspenso, exceções de loopback, controle positivo/negativo e Job Object; o supervisor valida e mantém o handle read-only **não herdável** da fonte sintética e só transfere o handle write-only do relatório. O worker Windows **não lê a fonte**: recebe apenas metadados verificados pelo supervisor. Isso demonstra a negação das operações ensaiadas no ambiente sintético, **não** um broker geral de leitura de dados científicos nem confinamento absoluto de todos os objetos do host. `PRODUCTION_ACQUISITION_BLOCKED` e `C2_B_OS_BLOCKED_EXACT` permanecem até composição, contraprovas completas e revisão independente.
- Não foi concedido acesso à bancada privada; fixtures, diretórios temporários e recibos são sintéticos. Nunca afirmar ausência de caminhos secretos no host a partir de uma string `synthetic`.
- Diretórios temporários criados são descartáveis e confinados aos próprios testes. Nenhuma ACL original, firewall, Conda, R4, arquivo científico ou permissão global foi tocada.
- Em falha de capacidade do SO, o perfil retorna `OS_ISOLATION_UNVERIFIED`/equivalente. Falha fechada significa manter aquisição bloqueada, **não** converter CI verde em aprovação.
- `reader003`, SDK, Caderno, Catalog, esquema do descriptor, aprovação ARC-09 e decisões humanas permanecem preservados.

## Evidência/revisão

A PR Draft [#20](https://github.com/thalesvalente/Atlas/pull/20) recebeu revisão distinta real do Copilot [review 5726283233](https://github.com/thalesvalente/Atlas/pull/20#pullrequestreview-5726283233), com findings de segurança; há correções de autoria posterior, mas nenhum aceite independente final dessas correções. Recibo por SHA em `CI-EVIDENCE.json`; contraprovas individuais em `NEGATIVE-TESTS.json`. G4/G5/G6: não promovidos.
