# AP04-F4-C2-B-OS-SANDBOX-CHAT-01 — publicação executável e bloqueio preservado

## Resultado formal

`C2_B_OS_BLOCKED_EXACT` — supervisor, limites e **contraprovas nativas em dados inventados** implementados e executados, mas **não houve liberação para fontes reais** porque falta perfil Windows de confinamento filesystem/rede para o WORKER, integração C2-D e aceite final de revisão independente.

- Repositório: `thalesvalente/Atlas`; branch exclusiva `feat/atlas-parity04-f4-c2-os-isolation-20261101`; PR **Draft [#20](https://github.com/thalesvalente/Atlas/pull/20)**.
- Prompt fixado: `315f7dbeffc80822e96068eed6b4af3193d1b6a7` em `docs/missions/atlas-parity-04/f4-direct-reuse-next-20261101/02-C2-B-WINDOWS-OS-SANDBOX-CHAT.md`.
- Base inicial verificada antes da escrita: `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`.
- **Código e testes técnicos congelados:** SHA `29f0e144e7470794df721806ed1485d50000a05b` (commit técnico inclui também revisão/contratos de ameaça e política). Recibos posteriores são um **commit documental descendente**, não mudam estes blobs executáveis.
- **CI real focal no SHA técnico:** [GitHub Actions #41271638031](https://github.com/thalesvalente/Atlas/actions/runs/41271638031), `completed/success`, **4/4 jobs**:
  - Windows O0: 22 PASS, 2 SKIP, 0 FAIL, job `124745439571`.
  - Windows O1: 22 PASS, 2 SKIP, 0 FAIL, job `124745439423`.
  - Ubuntu O0: 18 PASS, 6 SKIP, 0 FAIL, job `124745439575`.
  - Ubuntu O1: 18 PASS, 6 SKIP, 0 FAIL, job `124745439576`.
  - Agregado **80 PASS / 16 SKIP não aplicáveis / 0 FAIL / 96 coletados**. O0/O1 otimizam apenas o WORKER; pytest mantém asserções ativas. Checker de recibo verificou SHA do checkout e JUnit com testes efetivamente executados.
- Quatro artefatos GitHub Actions persistem JUnit e `observed-ci.json`, IDs em `CI-EVIDENCE.json`.

## Produto implementado

`tools/atlas_legacy_presentation/os_supervisor.py`: API `run_synthetic_probe(mode)` cria seus próprios bytes inventados, não aceita caminhos externos; `require_production_acquisition()` lança `PRODUCTION_ACQUISITION_BLOCKED`. Worker repete verificação de ancestralidade/fixture/SID e recusa chamada direta inadequada.

Windows `os_windows_job.py`: `CREATE_SUSPENDED` → Job criado+consultado com limite **256 MiB committed bytes Job-wide** e `KILL_ON_JOB_CLOSE` → associação → retomada → deadline **30 segundos wall/monotonic**, sem breakaway; terminação de descendentes e contraprovas de falha de associação. `os_windows_acl.py`: scratch sintético descartável com DACL protegida, proprietário token atual, consulta binária de ACE/SID, sem alterar ACLs alheias.

Ubuntu `os_linux_isolation.py`: Landlock ABI >=3 fonte exata RO/scratch RW, seccomp-BPF nega socket/fork/clone/exec, `SECCOMP_RET_KILL_PROCESS` para arquitetura inesperada, `NO_NEW_PRIVS`, parent-death guard, `RLIMIT_AS=256 MiB` (**endereço virtual, não RSS**) e `RLIMIT_CORE=0`; deadline monitora wall clock e encerra grupo.

`os_worker.py` tem somente casos inventados de contraprova. `tests/qa/test_atlas_parity04_f4_c2_os_sandbox.py` implementa 24 casos, incluindo reparse/junction, argumentos adulterados, entrada direta recusada, origem inalterada e ausência de descriptor físico após falha. Workflow/SHA checker novos na área C2-B.

## Findings e bloqueios reais

Revisão distinta GitHub Copilot na PR #20 publicou três avaliações `Changes recommended` com findings reproduzíveis, primeira em [review 5726283233](https://github.com/thalesvalente/Atlas/pull/20#pullrequestreview-5726283233); reparos foram realizados e CI nativa reexecutada, porém não existe aprovação **independente** do código terminal. Subagentes nativos não estavam disponíveis nesta sessão.

A CI focal `success` **não implica CI global verde**: workflows legados de PR do Atlas, incluindo AP04 documentation successor e P03/C4/P06 frozen boundary/Spec Kit, registraram `failure` no SHA técnico por regras de proveniência/frozen fixtures próprias. Não foram modificados, desviados nem enfraquecidos. Esses eventos permanecem observáveis na PR #20.

**Crítico remanescente:** `Job Object` e DACL do scratch sintético não restringem o WORKER Windows a ler somente a fonte exata, gravar apenas scratch ou abrir sockets. Sem AppContainer/LPAC/broker efetivamente ensaiado, **WINDOWS_FS_NETWORK_OS_PROFILE_MISSING**. Do mesmo modo faltam prova completa de crash de supervisor e races de handle, integração de contrato `reader.prepare` por C2-D, e prova de host L1; nenhum desses bloqueios é eliminado pelos jobs focais verdes.

## Governança, ownership e menor ato seguinte

Diff contra base adiciona somente arquivos de `os_*`, harness/CI C2-B e recibos deste diretório; não edita mapeador C2-A, `reader.py`, reader003, F2, ADR-0003, manifestações históricas, código R4, dados ou políticas do host. Sem merge, release, deploy, migração, E1/E2, provider, replay ou leitura de arquivos privados.

Próxima frente C2-B: implementar e contraprovar filesystem/rede **Windows em perfil nativo real** em ambiente autorizado e submeter SHA a revisão independente final. C2-D: integrar somente blobs aprovados por SHA, sem presumir ancestralidade/merge da PR #20. L1: receber handoff separado e autorização explícita para qualquer prova do host. Decisões humanas G4/G5/G6 permanecem `BLOCKED/NOT_APPROVED`.

Ver `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `THREAT-MODEL.md`, `OS-POLICY-AND-CAPABILITIES.md`, `INDEPENDENT-REVIEW.md` e `HANDOFF.json`.
