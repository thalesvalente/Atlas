# AP04-F4-C2-B-OS-SANDBOX-CHAT-01 — C2_B_OS_BLOCKED_EXACT

## Estado e proveniência

- Repositório: `thalesvalente/Atlas`; branch exclusiva: `feat/atlas-parity04-f4-c2-os-isolation-20261101`.
- Prompt imutável: `315f7dbeffc80822e96068eed6b4af3193d1b6a7`, `02-C2-B-WINDOWS-OS-SANDBOX-CHAT.md`.
- Base original da branch: commit `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, tree `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df`.
- SHA técnico final dos novos módulos e testes (sem recibos): `5fe99d28fa2543478a0436ea94d80eabe07a9fad`.
- CI sintética comprovada no primeiro SHA `3ad2b700c570db6ec0ce4604c9fbc02b479d9287`: run [41270139863](https://github.com/thalesvalente/Atlas/actions/runs/41270139863), 4/4 jobs success; Windows 12 PASS ×2, Linux 9 PASS+3 not-applicable ×2. Isso não valida automaticamente o SHA sucessor.
- O `CI-EVIDENCE.json` fixa o resultado do SHA técnico após suas execuções. Cada recibo deriva do SHA técnico; o SHA de publicação documental e sua CI devem ser verificados separadamente.
- PR independente Draft: [#20](https://github.com/thalesvalente/Atlas/pull/20), sem merge; PR #18 de C2-A não editada.

## Engenharia executável

**Windows**: worker nasce suspenso via `CreateProcessW`, Job configurado e consultado antes da associação e da retomada, teto de 268435456 bytes de **memória comprometida agregada do Job**, `KILL_ON_JOB_CLOSE`, sem `BREAKAWAY_OK`. Supervisor mede tempo decorrido monotônico (não tempo de CPU) e chama `TerminateJobObject` no limite de 30 s. Contraprovas sintéticas: alocação maior que teto, 30 s bloqueado, processo descendente, tentativa breakaway, falha forçada de associação. Launcher recusa qualquer worker que não seja o `os_worker.py` revisado.

**Ubuntu Linux**: worker com `RLIMIT_AS=268435456` (limite de espaço de endereçamento virtual, não RSS), `RLIMIT_CORE=0`, umask 077, `PR_SET_NO_NEW_PRIVS` e `PR_SET_PDEATHSIG`, Landlock ABI >=3 para fonte inventada exata somente leitura e scratch 0700, seccomp-BPF para negar sockets, fork/clone e exec. Cronômetro monotônico externo termina grupo de processo. CI comprovou as negações em runners Ubuntu do primeiro SHA; última CI discriminada em recibo próprio.

**Ambos**: testes trabalham exclusivamente com dados inventados e deixam `require_production_acquisition` em `PRODUCTION_ACQUISITION_BLOCKED`, sem usar `--synthetic-fixture` como privilégio. Nenhum código existente de `reader.py`, C2-A ou Caderno foi editado; acoplamento ao leitor pertence exclusivamente a C2-D.

## Bloqueios obrigatórios

1. **WINDOWS_FS_NETWORK_OS_PROFILE_MISSING**: Job Object não controla read-only exata, escrita apenas em scratch nem sockets. Não foi criado perfil AppContainer/LPAC, broker nem ACL de fontes. Uma tentativa de execução real fica bloqueada.
2. **INDEPENDENT_SECURITY_REVIEW_PENDING**: sessão não dispõe de `spawn_agent`/delegação nativa real. Uma revisão de autoria distinta e ancorada ao SHA terminal não pode ser autodeclarada.
3. **RACE_CRASH_PROOFS_INCOMPLETE**: queda abrupta do supervisor e disputa de handles não têm cobertura negativa integral; `KILL_ON_JOB_CLOSE`/PDEATHSIG são configurados e exercitados parcialmente, não equivalem a revisão de crash adversarial.
4. **HOST_UNVERIFIED**: GitHub Actions não mede permissões do Windows privado, nem libera a aquisição de dados reais.
5. **PRODUCT_PUBLICATION_NOT_COMPOSED**: teste de ausência física de descriptor no scratch exercita o supervisor isolado, não o `reader.prepare`; C2-D ainda não fez a composição.

Não liberar G4, G5, G6, F5, merge, release, deploy, migração, R4 ou limpeza de acervo. Menor ato seguinte: owner C2-B criar versão posterior de isolamento AppContainer/LPAC comprovado e reexecutar contraprovas nativas em fixtures; revisor independente distinto; C2-D compor os **blobs por SHA**, e L1 comprovar o host somente sob autorização própria. Preserve aprovações humanas da ADR-0003 e precedência de reader003.
