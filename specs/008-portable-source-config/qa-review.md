# QA independente — configuração portátil de fontes

**Resultado**: `PASS_INDEPENDENT_CODE_REVIEW_SCOPED`.  
**Revisor real**: agente `/root/p01_contracts_qa`, P01.  
**Data**: 2026-11-10. **Ambiente**: Linux, Python 3.12.14.  
**Branch**: `feat/atlas-portable-source-config-20261110`.  
**Base**: `43f7aaafedac7e8b124188baa51b888cee74c13c`.  
**Commit documental já publicado**: `1007eba65812387079e4350815b22b9d7a531fd1`.

P01 escreveu contrato/spec, não escreveu nem corrigiu código de runtime,
launchers, smoke ou testes auditados. P02 escreveu backend/CLI; P03 escreveu
launchers e documentação operacional; P00 escreveu o smoke. P01 executou sua
revisão e contraprovas, enviou findings e reavaliou as correções dos owners.

Este parecer qualifica o snapshot pelos hashes abaixo. O SHA terminal, CI e
publicação da PR serão registrados pelo integrador no recibo terminal; esse
recibo sucederá o estado pré-publicação T019/T020. Não atribuir a revisão a
outros bytes. Windows do operador permanece `LOCAL_TEST_NOT_RUN` (T021).

## Escopo e evidência executada pelo revisor

| Verificação | Resultado real |
|---|---|
| `python -m unittest discover -s tests/viewer -p 'test_source_config*.py' -v` com os dois `src` no PYTHONPATH | 44 descobertos, 43 PASS, 1 SKIP (case Windows), exit 0 |
| `python -m unittest discover -s tests/viewer -p 'test_native_notebook_source_config_launcher.py' -v` no mesmo ambiente | 21 descobertos, 15 PASS, 6 SKIP (runtimes PS 5.1/7 ausentes), exit 0 |
| 21 contraprovas adicionais por Python stdin, fixtures temporárias sintéticas | 21 PASS no backend final `81c9d091…`, exit 0 |
| Python isolado build03: `python -I -B scripts/qa/portable_source_config_smoke.py --receipt .local/portable-source-config/independent-smoke-final.json` | 23/23 PASS_SCOPED, exit 0 |
| Hashes de `source_config.py` e `__main__.py` realmente importados do build03 | Iguais ao checkout; ambos dentro de `sys.prefix`, `sys.flags.isolated=1` |
| `git diff --exit-code` contra base para protocolo, Catalog, static, `.specify` e `.agents` | Exit 0, sem alterações |
| Inspeção AST dos quatro módulos Python de runtime/launcher/smoke | Sem imports `r4`/`r4.*` |
| Leitura de diff, README, quickstart, contratos e código | Convergência conferida; achados resolvidos abaixo |

Os comandos focalizados usam apenas os paths relativos `packages/protocol/src`
e `packages/atlas/src` no `PYTHONPATH`. O smoke usa o Python da instalação
isolada criada por P00 e ignora `PYTHONPATH`. Nenhum pacote foi instalado por
P01. Nenhuma fonte privada ou serviço do operador foi acessado.

### Contraprovas adicionais

1. JSON com 1500 níveis é recusado sem traceback.
2. Chaves estranhas falham de forma explícita.
3. `clear` preserva arquivo alheio em vez de sobrescrevê-lo.
4. Falha de `os.replace` preserva os bytes anteriores.
5. Essa falha remove somente o temporário próprio.
6. Permissão real de leitura negada por `chmod(0)` produz código sem path.
7. Alias de diretório pai é detectado como duplicado.
8. Destino cujo pai é symlink para fonte é recusado.
9. Symlink de metadata como fonte é recusado.
10. CLI `--no-config` ignora configuração padrão malformada.
11. CLI com fonte explícita ignora padrão malformado e mantém saída redigida.
12. Erro de configuração malformada não expõe o caminho.
13. Seleção explícita ignora localização padrão inválida no ambiente.
14. Resumo só exibe caminhos com opção explícita.
15. Bytes científicos permanecem iguais após as operações.
16. Metadata não canônico protege a pasta do pacote (P00-F01).
17. Metadata anterior removido protege config em subdiretório (P01-F01).
18. Seleção vazia não cria configuração junto do marcador científico.
19. Reconfiguração de diretório movido continua permitida.
20. Configuração ao lado de arquivo ZIP continua permitida.
21. Bytes científicos permanecem iguais após todas as contraprovas do guard.

O primeiro probe exploratório exigia `JSON_INVALID` para nesting ainda parseável
neste runtime, que corretamente devolveu `SOURCE_INVALID`. A expectativa do
probe foi corrigida; não houve alteração do produto para satisfazê-la. O registro
acima é a reexecução final, após todas as correções dos findings.

## Regressão completa do integrador conferida

P00 executou `python scripts/run_checks.py` e `python -O scripts/run_checks.py`
no build03 instalado. P01 leu os dois recibos reais e confirmou o hash do backend.
Cada execução teve 204 testes descobertos: 194 PASS, 10 SKIP, zero falhas/erros,
exit 0. Distribuição: protocolo 12 (1 SKIP), QA 55 (0 SKIP), viewer 137 (9 SKIP).
O SKIP do protocolo é `jsonschema` opcional ausente; os nove do viewer dependem
de Windows/PowerShell/semântica de caminhos. Esses resultados pertencem a P00;
não são apresentados como execuções próprias do revisor. Os testes focais
anteriores integram essa população; não somar contagens de subconjuntos.

- `final-normal.json`: SHA-256 `9b129f269641863f0993209d333c3ba15cd70a9fc15b45376dfac636f706095a`.
- `final-optimized.json`: SHA-256 `e3ebe9088cf373d5d4c02f48310d44265b6af85d5a66fa5ec4f087620be40bfd`.

## Findings e disposição

| ID / origem | Impacto constatado | Correção e reteste | Estado |
|---|---|---|---|
| P00-F01 / integrador | Metadata válido com nome arbitrário permitia gravar preferências dentro da sua pasta científica | P02 passou a tratar o pai de todo metadata regular não ZIP/ELN como base; P01 reexecutou casos de seleção e clear, mantendo ZIP sibling permitido | RESOLVED |
| P01-F01 / revisor | Ao remover o metadata não canônico anterior, o guard perdia a proteção da pasta e permitia clear da config embutida | P02 verifica marcador fixo `ro-crate-metadata.json` em paths explicitamente ancorados; P01 reproduziu variante com config em subdiretório e confirmou rejeição, sem impedir troca de diretório movido | RESOLVED |
| P01-D01 / revisor, LOW | Exemplo relativo de config contradizia orientação de mantê-la fora do checkout | P03 usou pastas locais do usuário nos exemplos PowerShell/POSIX; P01 conferiu quickstart final `71f48051…` | RESOLVED |

Não restam findings materiais abertos neste escopo. Os testes RED dos reparos
foram produzidos/executados por P02; P01 verificou independentemente o efeito
final e não reivindica autoria desses testes.

## Rastreabilidade e limites

FR-001–015 estão implementados e cobertos pelos testes/probes observados;
FR-016 tem documentação e ensaio sintético preparado. FR-017 está evidenciado
no ambiente indicado, sem extrapolar para Windows. FR-018 depende também das
etapas remotas T019/T020 do integrador. A checklist separa contrato, código,
publicação e aceite local. Nenhuma revisão automatizada concede aceite científico.

A gravação protege fontes selecionadas/anteriores e reconhece o marcador fixo
no destino. Não faz glob/rglob nem procura pacotes alternativos. Leituras de
config e startup são limitadas; a validação do pacote permanece no SDK. Nenhuma
API HTTP de escrita ou dependência externa foi acrescentada.

Persistência protege contra falhas anteriores à troca atômica; não promete
transação entre vários operadores ou proteção total contra corridas em host
adversarial. O runtime PowerShell foi revisado e tem testes executáveis, mas
seus seis casos foram SKIP neste host. A execução no computador Windows,
instalação local, fontes privadas e portas operacionais permanecem fora desta QA.

O guard histórico de apresentação conserva pins/manifestos e escopo. Este
parecer da feature 008 não o repina nem transforma sua baseline em recibo novo.
A CI final e revisão Codex, quando disponíveis, têm SHA/status próprios.

## Identidade dos arquivos auditados

| Arquivo | SHA-256 |
|---|---|
| `packages/atlas/src/atlas_viewer/source_config.py` | `81c9d0917780cc75bf1b4977c32ef10068a0dc0cd55085d67604a43e6f86c9bd` |
| `packages/atlas/src/atlas_viewer/__main__.py` | `92fcc89a4ce38804f6186fe0425fdb3476599f574c838f71567a401c94726817` |
| `scripts/atlas_launch.py` | `f66625343a3c448e708c5048a719a9ef4f1ce36f9c668b343df342e4aac7c5b4` |
| `scripts/ABRIR-ATLAS.ps1` | `8d2c469f293a2914a33a12fe0d3c602bbf6c843ec571e78d2d431c20b629f693` |
| `scripts/qa/portable_source_config_smoke.py` | `2da03cc55ae9e70ef9ad0db49c2264d93819556d55104a19ed44e0a5c8087c85` |
| `tests/viewer/test_source_config.py` | `5e9cac9837d67bb8da20420b140ef2e94aad251ede9aab0400db209a1dccf059` |
| `tests/viewer/test_source_config_cli.py` | `28c0fe0c75a6e52a7f25399f630cd28b17751b1d553240ef15a57c8eb7f5960c` |
| `tests/viewer/test_native_notebook_source_config_launcher.py` | `5e1c0c01d091a3fb5759a3a400506d48276cd04c4da81bb5550b171e39dc672c` |
| `specs/008-portable-source-config/quickstart.md` | `71f48051c65146b0bd87a7aac7b50c4fedb0a44bce03bd12f6f4f6d1994ea5dd` |
| `README.md` | `24ff20bc77078036688e132e7530e19800c43ba4b209cd82dc3a08e0b89859f2` |

Recibo independente de smoke (somente dados sintéticos): SHA-256 `b051434b533900688ffd7c337f6b39ddf98f22288dcfca5827ea5ce0428e5b84`.

## Adendo pós-CI — caminhos canônicos e timeout do navegador

Este adendo preserva os resultados e hashes históricos acima, referentes à
candidata `e7b0a56b17a3400c2b73b052c05fff84becd677a`. Não concede PASS global
enquanto o reteste remoto no próximo SHA estiver pendente.

### Expectativas de caminhos no Windows

P01 leu os logs `ci-130238953072.log` (10 falhas) e `ci-130238953175.log`
(11 falhas, incluindo o caso de 16 fontes). Todas essas falhas mostravam a
mesma divergência: a entrada temporária usava alias Windows 8.3, enquanto a
API devolvia o caminho absoluto canônico, conforme o contrato aprovado.
As falhas ocorreram em igualdade textual das expectativas dos testes.
P00 conferiu adicionalmente os jobs otimizados `130238953128` (11 falhas) e
`130238953690` (10), relatando os mesmos casos e nenhum outro ERROR; esses
dois logs não foram executados nem inspecionados por P01. Os quatro jobs
Windows afetados são requalificados pela próxima CI.

P02 e P03 corrigiram apenas as expectativas, usando `Path.resolve()`. P01
revisou os diffs: entradas continuam originais, igualdade continua exata,
ordem, cardinalidade e Unicode continuam verificados. Não houve mudança de
runtime, skips, workflows, protocolo ou fontes para obter resultado verde.

P01 reexecutou os testes modificados em Linux/Python 3.12.14:

| Execução | Config/CLI | Launcher | Exit |
|---|---|---|---|
| Normal | 44 descobertos, 43 PASS, 1 SKIP | 21 descobertos, 15 PASS, 6 SKIP | 0 |
| `-O` | 44 descobertos, 43 PASS, 1 SKIP | 21 descobertos, 15 PASS, 6 SKIP | 0 |

São 65 testes por modo, 58 PASS e 7 SKIP; os SKIPs são dependências de Windows
ou PowerShell. O reteste Windows pela CI do novo SHA permanece obrigatório.
As identidades atuais dos dois testes substituem suas entradas históricas na
tabela anterior; os demais oito arquivos auditados mantêm os mesmos bytes:

| Arquivo alterado pós-CI | SHA-256 revisado |
|---|---|
| `tests/viewer/test_source_config.py` | `b5696702f12ff8b77bd79fc336ab07082a64f1296fff128c9480c85ee87f2805` |
| `tests/viewer/test_native_notebook_source_config_launcher.py` | `1bea61c9c6ead65af4518f53743f608870f2b4d306d9691558f00c6507e71cc6` |

### Timeout do cenário original: INCONCLUSIVE / PENDING

No run `42933864055`, job `130238952728`, o cenário
`original-reference-inert-native-surface` completou a verificação da rota
inerte e a abertura normal de `/notebook`. O recibo mostrou zero erros de
página e zero requisições HTTP externas. A falha seguinte foi o timeout de
30 segundos em `scripts/qa/browser_original.mjs:51`, aguardando
`popup.waitForLoadState('domcontentloaded')` após Ctrl-click do link nativo.
O log de espera registrou `networkidle`, mas não registrou URL, readyState
ou eventos do documento do popup; isso não demonstra a causa raiz.

P01 confirmou que `browser_original.mjs`, `scripts/ci/run_browser.py`, servidor
e arquivos estáticos permanecem iguais à base `43f7aaaf…` e à candidata e7b0.
O runner original usa seleção vazia sem `--no-config`; isso merece isolamento
na investigação, mas não há evidência de configuração herdada no job. Os
comandos de instalação desse job não executam `config set`.

A reprodução diagnóstica de P00 no CHAT foi **BLOCKED antes de abrir página**:
`process_singleton_posix` falhou em `socket()` com `Operation not permitted`;
o log também registrou `ptrace` negado. Não é reprodução do timeout de CI,
não prova sua correção e não justifica chamá-lo de flake. Não houve contorno
das restrições do runtime.

Próximo passo: reteste natural do mesmo cenário, sem alterações, no SHA que
publicar as expectativas Windows corrigidas. Se o timeout reaparecer, colher
URL/readyState, eventos de navegação e lifecycle, responses/requestfailed e
trace do popup em diagnóstico separado; comparar aba ativa/background antes
de propor reparo. Preservar as asserções de rota inerte, ausência de execução
HTML, navegação e requisições externas. Não mudar produto, baseline, versões
de ferramentas ou skips às cegas. Windows do operador segue `LOCAL_TEST_NOT_RUN`.

### Identidade das evidências consultadas no adendo

- `ci-130238953072.log`: SHA-256 `d167cd1e3aa8001344bef6a08c38dae7748ff75c0c12eab5c781e369b93bb146`.
- `ci-130238953175.log`: SHA-256 `ce97bbef6cc89f024bc85d547c79ce3761bce9b1aba2d86f977b60b276a6d534`.
- `ci-130238952728.log`: SHA-256 `a543a423af259e320d4bf7f8bc803fe7791bc5c50ffecdfbffc0643e446cc8bc`.
- `browser-original-diagnostic.log`: SHA-256 `2214123937f71efb80a13dc0fabc47280f4185a04f3ff0a4f015a0a798ad2122`.
