# AP04-F4-C2-B-OS-SANDBOX-CHAT-01 — hard budgets e confinamento real do leitor externo

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub e GitHub Actions (runners Windows/Ubuntu, **somente arquivos inventados**). **Esforço: Extra High**, escolha manual do operador; nunca alegar nível efetivo não observável.
**Repositório único:** `thalesvalente/Atlas`. **Branch independente** `feat/atlas-parity04-f4-c2-os-isolation-20261101`, preparada a partir do SHA `e349a09d439d292011bca4c0994cf8ab3e3fbf9f` / tree `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df` da PR #18.
**Meta:** `C2_B_OS_ENFORCEMENT_VERIFIED_FOR_COMPOSITION` se os mecanismos forem realmente impostos e exercitados; `C2_B_OS_BLOCKED_EXACT` se o SO/runner negar alguma obrigação. Código seguro deve ser publicado mesmo no caso bloqueado.

## 1. Contratos e perímetro

Ler AP04-POR-v1.0-draft F4/G4, ARC-01–09, ADR-0003 v0.2 `APPROVED_SCOPED` no pacote `c3ea1e82938fd61cc5a22fee973352715a5bb527`, `SECURITY-AND-INTEROPERABILITY.md` F2, C0 contrato 003 `d498504cd2c4d230088f86e04e55624bbe32df79`, e C2 `SECURITY-AND-LIMITS.json` / `reader.py` no SHA `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`.

Objetivo é criar **isolamento imposto pelo SO**, não mais um timeout cooperativo com flags. Exigências não negociáveis: fonte exata/allowlist read-only, scratch temporário privado restrito à escrita própria, negação de rede/providers, **256 MiB de memória máxima** na métrica definida e verificada, **30 segundos de relógio** (wall time) por leitura/validação, cancelamento do grupo e ausência de descriptor parcial publicável. Job Object controla recursos, não isolamento de filesystem/rede; são mecanismos diferentes. Se algum requisito não for imposto ou verificado, negar uso real, sem `--synthetic-fixture` como atalho.

Fontes públicas oficiais para seleção de APIs: Microsoft Job Objects/`JOBOBJECT_EXTENDED_LIMIT_INFORMATION`/`TerminateJobObject`/AppContainer/LPAC; no Linux cgroup v2, namespaces, Landlock e seccomp quando disponíveis. A escolha deve ser justificada em recibos, sem alegar presença de permissão administrativa ou feature no Windows do operador.

## 2. Ownership exclusivo da branch B

Pode criar **somente arquivos novos**, por exemplo:
- `tools/atlas_legacy_presentation/os_supervisor.py`, `os_windows_job.py`, `os_windows_isolation.py`, `os_linux_isolation.py` e módulos prefixados `os_` próprios;
- `tests/qa/test_atlas_parity04_f4_c2_os_...`, `scripts/qa/atlas_parity04_f4_c2_os_...` e fixtures sintéticas com prefixo OS;
- workflow NOVO `.github/workflows/atlas-parity04-f4-c2-os-sandbox.yml` para CI isolada;
- recibos `docs/missions/atlas-parity-04/f4-c2-os-sandbox/`.

**Não editar:** `tools/atlas_legacy_presentation/reader.py`, `__main__.py`, `parser.py`, `legacy_v5.py`, `legacy_v5_descriptor.py`, testes/workflow C2-A, scripts globais, F3A/F3B, viewer/Catalog/SDK/Caderno, reader003, ADRs, manifestos antigos ou código R4. A conexão real de `reader.prepare` com o supervisor será de C2-D, **após** os SHAs de A e B estarem congelados. Uma branch independente não exige criar worktree; proibidos clones/worktrees persistentes, force/rebase e merge main.

Até três subagentes nativos reais quando disponíveis: A supervisor Job/limites, B negações OS e testes, C QA independente read-only, ownership disjunto e coordenador único writer. Se indisponíveis, fazer implementação segura e declarar ausência de revisão; nunca simular.

## 3. Implementar os limites rígidos Windows

1. Worker começa **sem ler bytes não confiáveis antes de ser confinado**. Configurar Job Object e associação ao processo/descendentes antes de retomar execução; quando viável, criação suspensa, associação, restrições, verificação e somente então resume. Falha de qualquer operação = `OS_PROFILE_NOT_ENFORCED`, sem processar dado.
2. Especificar medição exata de memória. Limite de 256 MiB imposto por Job sobre memória comprometida do processo ou conjunto conforme contrato; explicar que committed bytes, working set e RSS não são a mesma métrica. Provar tentativa de ultrapassar limite e encerrar/recusar. Não usar `psutil`/tracemalloc/limite apenas cooperativo como substituto de Job.
3. Supervisor controla 30 s **decorridos de relógio monotônico**; `JOB_OBJECT_LIMIT_JOB_TIME` é CPU em modo usuário, NÃO 30 segundos wall. Worker bloqueado no I/O e descendentes precisam ser terminados via Job no deadline; assegurar `KILL_ON_JOB_CLOSE`, fechamento de handles e impossibilidade de escape por breakaway sem nova autorização.
4. FS/rede: definir fronteira nativa AppContainer/LPAC/restricted-token ou mecanismo comparável **e demonstrar negação efetiva** para abertura de arquivo fora da allowlist, escrita na fonte inventada e conexão de rede inclusive loopback. Não assumir que passar uma string de allowlist ao Python equivale a negação de SO. Se usar broker de handles, ele é confiável apenas em API mínima que abre fonte exata read-only e scratch próprio; nenhuma função genérica read/write/socket.
5. Testar não concessão de privilégios no host: não alterar ACL de arquivos científicos, não alterar firewall, UAC, políticas globais, admins, aliases ou ambiente de Python/Conda do operador. Não utilizar bypass de sandbox ou escalation para satisfazer os testes.
6. Saída: escrita atômica somente em scratch já autorizado, sem publicar arquivo parcial no timeout/OOM/segurança, cleanup apenas de derivado próprio identificado. Não afirmar apagamento seguro ou limpeza de cache após crash; documentar o resíduo possível.

## 4. Linux, compatibilidade e ausência de capacidades

No Ubuntu implantar controle de memória/CPU/FS/rede adequado às permissões reais (cgroup v2/namespace/Landlock/seccomp conforme aplicável). `resource.setrlimit` é Unix, não resolve o Windows nem por si só a segurança FS/rede. Se o runner não permitir cgroups/ns/perfil nativo, falhar fechado e registrar `OS_ISOLATION_UNVERIFIED`; não substituir por teste que verifica apenas textos. Não exigir que o SO Linux faça exatamente o mesmo mecanismo que Windows, mas os invariantes contratados devem ser demonstrados para a célula anunciada.

Uma operação de test-only que não acessa dados privados pode gerar prova parcial de Job Windows e negação Linux sem liberar produção. O gate real L1 é exclusivo da máquina Windows autorizada, não herdará automaticamente permissões/configuração dos runners GitHub.

## 5. Contraprovas executáveis e gates

Windows: tentativa de alocar mais que 256 MiB, worker bloqueado além de 30 s, subprocesso/descendente, queda do supervisor, falha de associar Job, breakaway, leitura de fixture fora da allowlist, escrita em fonte inventada, socket loopback/external negado por SO, race de handle e publicação abortada. Quando um ataque exigir privilégios não disponíveis, registrar `NOT_RUN_UNSUPPORTED` e qualificação **bloqueada** para a proteção correspondente, não `PASS` nem skip disfarçado.

Linux: contraprovas equivalentes por controles reais. Python normal/`-O`, CI independente Windows/Ubuntu, IDs/artefatos JUnit/JSON por SHA, ações fixadas por SHA completo. Nenhum `continue-on-error`, `paths-ignore`, `|| true`, desativar workflow ou mexer em pins antigos para produzir verde.

Revisão independente de segurança no próprio SHA terminal, sem autoria. Se não houver ferramenta nativa, revisor humano/CHAT separado com evidência de autoria distinta; não alegar independência inexistente.

## 6. Entregáveis e montagem posterior

Persistir código/harness e `RESULT.md`, `THREAT-MODEL.md`, `OS-POLICY-AND-CAPABILITIES.md`, `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` na branch B. Recibo deve dizer se **cada** negação foi efetivamente imposta pelo SO, separando `OS_CONTROL_IMPLEMENTED`, `OS_CONTROL_TESTED_IN_RUNNER`, `HOST_UNVERIFIED`, `NOT_SUPPORTED` e `PRODUCTION_ACQUISITION_BLOCKED`.

C2-D, não B, integrará os blobs B por SHA à PR #18 depois que A terminar, mantendo commits de um único pai na PR18 e declarando **proveniência B por SHA/blob**, sem inventar que a branch B é ancestral. C2-D verificará a história B inteira, sem copiar arquivos não autorizados.

Se o controle/isolamento não estiver efetivo, `C2_B_OS_BLOCKED_EXACT` com menor ato de correção. **Não liberar G4/G5/G6, fonte real, F5, mudança R4, migração, merge main, release, deploy ou limpeza**.

**END-OF-AP04-F4-C2-B-PROMPT — COMPLETE**
