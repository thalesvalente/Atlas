# AP04 F4-C2-B — modelo de ameaças e fronteiras

**Ativo protegido:** projeções legadas privadas, diretórios adjacentes, credenciais, rede e integridade do ambiente do operador. **Insumos testados neste pacote:** somente `os-allowlisted.json`, `os-outside.json` e temporários inventados por pytest.

| Fronteira | Ameaça | Controle técnico | Evidência / estado |
|---|---|---|---|
| Trusted launcher → worker | Leitura antes do confinamento | Windows `CREATE_SUSPENDED` → `AssignProcessToJobObject` → `ResumeThread`; Linux inicializa isolamento antes de ler fixture; somente worker fixado | código + contraprovas sintéticas |
| Job Windows | OOM agregada ou descendentes | `JOB_OBJECT_LIMIT_JOB_MEMORY`, `KILL_ON_JOB_CLOSE`, quebra não autorizada | teste + consulta nativa do Job no runner |
| Worker Linux | Abrir arquivo fora da allowlist | Landlock 3+ com regra por inode de arquivo inventado | tentativa real `open` negada no runner |
| Worker Linux | Escrever na origem / outros diretórios | Landlock default-deny, scratch 0700 e umask 077 | tentativa real de escrita recusada |
| Worker Linux | Socket / provider / escape | seccomp BPF bloqueia `socket`, `fork`, `clone`, `execve` e congêneres, com arquitetura verificada | testes negativos de socket AF_INET/AF_INET6 + fork |
| Todos | 30 segundos wall ultrapassados | supervisor externo monotônico e encerramento do job/grupo | teste de sleep bloqueada 30 s |
| Falha de associação Windows | Worker executa antes de Job | processo suspenso terminável sem resume | injeção real de falha, ausência de relatório |
| Falha abrupta do supervisor | Filhos sobrevivem | Windows kill-on-close; Linux parent-death SIGKILL + seccomp denies fork | mecanismos configurados, crash test independente **pendente** |
| Escrita parcial/overwrite | Descriptor inválido publicado | Nenhuma integração/publicação de descriptor; scratch test não contém `atlas-c2-*.json` após OOM/timeout | provado apenas no harness isolado, produto bloqueado |
| Windows filesystem/rede | Acessar vizinhos, fonte em escrita, sockets loopback/external | **NENHUM** perfil efetivo implementado nesta versão; Job Object não os controla | `OS_PROFILE_NOT_ENFORCED`, bloqueio duro |
| TOCTOU | troca de caminho, hardlink, reparse point | preflight sintético com metadados/no-follow; não há broker/handle cross-boundary | prova adversarial do host **pendente** |
| Dados em disco/crash | core, pagefile, artefatos sobreviventes | Linux core desativado, scratch test privado | não prometer secure delete de pagefile/cache/backups |

**Riscos residuais**: Landlock tem limitações para descritores abertos antes da regra e alguns metadados `stat/chmod`; worker usa `close_fds=True` e não herda sockets, porém ataques mais sofisticados de FDs e corrida de arquivo não estão integralmente cobertos. `RLIMIT_AS` não mede RSS nem substitui accounting de cgroup; Linux proíbe criação de filhos neste perfil. O Job Windows mede **committed bytes do Job**, não working set. Teste CI não autentica arquivos científicos nem configuração do host.

**Fail closed**: caminhos que não sejam fixtures sintéticas são recusados pela API de ensaio; `require_production_acquisition` recusa qualquer argumento. Nenhuma alteração de ACL original, firewall, política global, admin, Conda, produção ou private drive.
