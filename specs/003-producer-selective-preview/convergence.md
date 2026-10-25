# Convergência técnica — REUSE-01

## Direção entregue
Pipeline existente do produtor → adaptador de projeção → Caderno 0.1.0a1 → Atlas independente. O leitor paralelo da candidata foi supersedido; não existe outro caminho ativo interpretando o índice bruto.

Especificação, clarificações, pesquisa de reaproveitamento, plano, checklist, tarefas e análise foram atualizados antes da implementação. O produtor manteve suas APIs originais e o exportador sintético; a ponte nova transforma apenas a projeção capturada.

## Evidência pública
No commit dca8b8645bc072230a29104a387e10b49fd4dbb8:
- CI Spec Kit: https://github.com/thalesvalente/Atlas/actions/runs/40226296214 — SUCCESS.
- CI de produto: https://github.com/thalesvalente/Atlas/actions/runs/40226296260 — SUCCESS.
- Codex: revisão concluída sem findings nesse SHA, registrada na PR #5.

Os testes privados da ponte passaram em Windows/Ubuntu, normal/-O, com APIs originais sobre fixture e consumo instalado sem produtor. Recibos, código, mapeamentos e SHAs privados permanecem no repositório privado. A entrega pública não publica dados de origem.

## Limites históricos — sessão REUSE-01 de 2026-10-25
A prova nova cobre SDK e inspeção pelo viewer instalado; não houve nova sessão de navegador dedicada a dados reais. A associação de evidência sem direção usa mentions; o viewer atual pode não mostrá-la por execução. Isso está declarado no contrato, não escondido por relações input/output inventadas.

`ADR_0001_CHANGED=false`; `ADR_0002_ACCEPTED=false`; `PUBLIC_SOURCE_TRANSFER=[]`; `HOST_REAL_READ=NOT_RUN`; `PHYSICAL_RETIREMENT=NOT_RUN`.

## Modo de execução histórico — sessão REUSE-01 de 2026-10-25
Sem delegador nativo nesta sessão. Revisão independente pelo Codex no GitHub. Autoria dos artefatos aplicou as skills oficiais; CLI Spec Kit1.2.3 e helpers reais foram executados em CI. Não se afirma dispatch nativo de skills ou instalação do CLI no host do usuário por esta sessão.

Este commit apenas reconcilia tarefas/convergência. O resultado de sua própria CI/review será acrescentado na PR por SHA, sem reatribuir provas anteriores. Merge, promoção, acervo real e interoperabilidade universal permanecem decisões/validações distintas.

## Incremento local LOCAL-REAL01 — 2026-10-25

O piloto operacional reutilizou o pipeline existente do produtor e seu adaptador de representação, preservando o pacote Caderno 0.1.0a1. O SDK/CLI instalados validaram o pacote; a execução selecionada foi conferida no navegador real do Atlas independente. Não foi necessário alterar código do consumidor, protocolo ou produtor.

A distribuição privada foi obtida por mecanismo autenticado na revisão escolhida, com manifesto e prova de imports; não foi incorporada ao produto público. Aquisição permaneceu delimitada aos controles permitidos antes da seleção. O modo de compatibilidade já existente foi explícito e não recebeu autoridade do Caderno central. A reconversão dos bytes capturados reproduziu o pacote byte a byte, sem sobrescrita nem releitura da fonte.

Revisores nativos reais de aquisição, QA e semântica/privacidade trabalharam somente leitura; o coordenador foi o único escritor. A revisão de requisitos encontrou dois problemas documentais, corrigidos antes da execução. QA e semântica finais: PASS_SCOPED, com limites declarados. As capturas, comandos e evidências completas ficam na raiz operacional ignorada; nenhum dado privado é publicado aqui.

Conservados os literais originais e as lacunas da projeção. Datas não foram promovidas a timestamps experimentais. Ausência de métricas na projeção não prova ausência em toda a experiência; referências neutras continuam mentions e podem não aparecer no detalhe. Avisos de payload ausente no pacote não atestam ausência da fonte. Autenticidade e aceite científico permanecem distintos da validação técnica.

Comparação final limitada aos controles efetivamente observados e aos arquivos instalados declarados no manifesto de instalação: sem divergência nesse escopo. Não há atestação universal do host, do acervo, do índice ou HEAD histórico. O servidor usa loopback e processo supervisionado, sem serviço permanente; há comandos de repetição/reinício/encerramento e a sobrevivência ao término da sessão não é garantida.

Skills oficiais aplicadas pelo agente sobre a feature existente, com artefatos redigidos pelo coordenador. Helpers efetivamente executados: resolve_template (constituição/spec), check_prerequisites (paths/checklist/analyze/implement/converge), setup_plan e setup_tasks; CLI1.2.3/integration status e auditoria de preservação conferidos. Não houve reinicialização, nova feature ou persistência de ponteiro compartilhado. Revisão constitucional sem alteração de governança.

Convergência operacional: nenhuma lacuna de código que impeça o objetivo no escopo autorizado. T020 aguarda a conciliação da publicação/revisão externa do novo HEAD documental; recibos pós-commit informam SHA e estado reais. CI/review desse delta não são antecipados. R012/ADR-0002 e merge/release/promoção permanecem gates humanos separados.

## Conciliação CLOSE01 do piloto — 2026-10-25

T020 está encerrada por evidências existentes, atribuídas à frente LOCAL-REAL01:

- [Recibo sanitizado LOCAL-REAL01](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6404206290): SDK/CLI instalados e navegador real; QA/semântica PASS_SCOPED.
- [Codex](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6404222103): concluído sem findings para `856ce3b4b3e2a25b8bc6d05c68a2cfeefc025cb6`.
- [CI de produto 40239890514](https://github.com/thalesvalente/Atlas/actions/runs/40239890514): 6/6 jobs SUCCESS, checkout do HEAD exato `856ce3b4b3e2a25b8bc6d05c68a2cfeefc025cb6`.
- [CI Spec Kit 40239890476](https://github.com/thalesvalente/Atlas/actions/runs/40239890476): 2/2 jobs SUCCESS na merge ref `8a18f5170a1795b5be671db538f6606e2e29083f`, formada pelo HEAD acima e base `a26b976fad70a8918ccaa5f4ba64aa4b453abed6`.

O estado pendente no último parágrafo de LOCAL-REAL01 é histórico e fica conciliado
por estes recibos posteriores. Esta sessão não leu arquivos/capturas do host nem
reexecutou aquisição/adaptador/piloto. A concordância do operador em avançar é
registrada no escopo demonstrado; ADR-0002, ciência e integração não são ratificadas.

## Execução CLOSE01 — candidata de engenharia

Delegação nativa real: A semântica/read model, B testes/navegador e C revisão
independente. O coordenador mantém UI/docs/Git. Sem autores concorrentes nos mesmos
arquivos. Skills oficiais 1.2.3 lidas e aplicadas pelo coordenador; dispatch nativo
dessas skills NOT_RUN. CLI local indisponível; helpers oficiais executados na sessão
com seleção explícita da feature e `SPECIFY_FEATURE_NO_PERSIST=1`. Não existe arquivo
de hooks `.specify/extensions.yml`; nenhum hook foi inventado. A constituição/ADRs
permanecem byte-idênticos. Resultados da candidata serão conciliados por SHA.

### Implementação e prova pré-publicação

O read model acrescenta `related_references` e a UI apresenta **Referências
relacionadas**. São preservados fonte + ID, semântica neutra, estados/revisão,
inputs/outputs/linhagem e os recursos persistidos. O índice continua somente em
memória. Não se reimplementou aquisição, adaptador, leitor legado ou protocolo.

- RED real: teste `test_declared_mention_is_visible_without_input_or_output_invention`
  contra a instalação da baseline `856ce3b...`: 1 FAIL pela ausência do novo campo.
- GREEN instalado: 11 testes focais em normal e `-O`; suíte integrada instalada
  com 12 SDK + 50 QA + 24 viewer = **86 PASS por modo, zero SKIP**. SDK sem viewer/R4
  e consumidor sem R4; byte-identidade/reconstrução PASS no escopo sintético.
- Os testes integrados locais antecedem o último ajuste de fallback textual do
  renderer, identificado na revisão. O SDK não mudou; caso `name=42` passou focalmente
  na instalação existente. A UI final e a matriz final são gates da CI por HEAD.
- Auditoria do Spec Kit: 28 assets oficiais, 10 skills, 6 helpers e 99 arquivos da
  baseline preservados; seis arquivos de apresentação/harness com exceção explícita.
  Quatro testes provam que o opt-in não libera schema/governança/skills ou exclusão.
- Revisão independente nativa C encontrou zero P1/P2 no delta; a inconsistência
  histórica do quickstart e o fallback não textual foram corrigidos. O parecer final
  será vinculado ao SHA no recibo pós-commit, sem o autor se declarar revisor independente.

O primeiro ensaio de HTTP na sandbox teve quatro erros de criação de socket; os
mesmos testes passaram com a permissão de loopback do ambiente de engenharia. Os
logs originais foram conservados. Isso não altera controles do host do operador.

### Prova visual e gates pós-commit

Navegador local desta sessão: NOT_RUN. Chromium ausente; a revisão automática de
permissão rejeitou seu download temporário por interpretar instalação como fora
do escopo. Nenhum contorno ou repetição desse download ocorreu. A missão permite a
capacidade Chromium já existente na CI: o job do consumidor instalado executa
`--related-references` e publica somente JSON/PNGs de fixtures sintéticas, HEAD,
hashes dos wheels e verificação dos bytes das fontes.

Esse cenário verifica os IDs contra o grafo persistido, incluindo dois pacotes com
IDs iguais, campos maliciosos, duplicações, estado vazio, teclado/foco e navegação
interna. Confere 390 pixels e ampliação CSS de 200%, explicitamente sem alegar zoom
nativo de todos os navegadores ou conformidade WCAG integral.

T027 (prova visual), a parte de CI de T028 e a revisão/publicação final de T029
ficam aguardando o primeiro recibo pós-commit. Esse comentário append-only na #5,
identificado por `ATLAS003-CHAT-CLOSE01` e SHA integral, é a fonte de fechamento
dessas tarefas; não haverá commit apenas para converter seus checkboxes em PASS.
Falha real exige correção material e novo SHA; pendência não é sucesso.

### Integração pública — topologia conferida em 2026-10-25

| PR | Base → HEAD conferidos | CI/revisão já existentes | Dependência e decisão seguinte |
|---|---|---|---|
| [#1](https://github.com/thalesvalente/Atlas/pull/1) | `main@0e1bbbd6` → `228fee0a` | [40117984475](https://github.com/thalesvalente/Atlas/actions/runs/40117984475) SUCCESS; Codex sem findings no HEAD | Raiz da cadeia; autorização humana de integração |
| [#3](https://github.com/thalesvalente/Atlas/pull/3) | `feat/atlas021-interface-protocol@228fee0a` → `a6e57c9c` | [40139350780](https://github.com/thalesvalente/Atlas/actions/runs/40139350780) SUCCESS; Codex sem findings no HEAD | Depende de #1; retarget para main e conferir delta após integração da base |
| [#4](https://github.com/thalesvalente/Atlas/pull/4) | `feat/atlas021-poc-r4-foco01-20261024@a6e57c9c` → `a26b976f` | [40214513596](https://github.com/thalesvalente/Atlas/actions/runs/40214513596) SUCCESS; revisão nativa versionada em docs/verification/SPECKIT-SETUP01.md; sem revisão GitHub publicada | Depende de #3; mesmo tratamento, sem reabrir bytes inalterados |
| [#5](https://github.com/thalesvalente/Atlas/pull/5) | `codex/atlas-speckit-setup01@a26b976f` → candidata CLOSE01, SHA no recibo | Piloto conciliado acima; nova CI/revisão aguardam o HEAD publicado | Depende de #4; integrar o incremento se os gates do recibo passarem e houver autorização |

Todas estavam abertas/Draft, sem merge. A ordem decorre das bases reais, não da
numeração. Recomenda-se preservar ancestralidade com merge commits quando a
integração for autorizada: #1, retarget/conferência de #3, #3, retarget/conferência
de #4, #4, retarget/conferência de #5, #5. Não há retarget ou merge nesta missão.
Squash/rebase das bases exige reconciliação da pilha antes de continuar.

O adaptador privado mantém sua própria candidata e provas; não existe import ou
dependência de instalação dele no viewer genérico. A integração desta UI pública
não depende de limpar históricos, aceitar ciência ou integrar o produtor privado.

### Decisão humana específica recomendada

Submeter a **ADR-0002 v1.0 de 24/10/2026**: RO-Crate 1.3.0 + Process Run Crate
0.6.0 + perfil Caderno 0.1.0a1, digest do perfil
`76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e`, como direção
para estabilização. A recomendação se apoia nas provas já publicadas de dois
produtores, instalação independente, matriz Windows/Ubuntu normal/-O e piloto
LOCAL-REAL01; a nova apresentação preserva a mesma combinação.

Limites da proposta: JSON-LD restrito; validador externo 0.13.0 não cobre Process
Run 0.6 integralmente; estados extensivos podem perder nuance em outros consumidores;
URI em branch exige publicação persistente antes da estabilização; digest não
autentica origem/ciência. Aceitar essa direção não autoriza merge, release, promoção,
dados privados ou manutenção física. A candidata de interface pode ser avaliada
como protótipo autorizado enquanto essa escolha específica segue PENDING_HUMAN.

### Estados conservados

`LOCAL_REAL01_CLOSEOUT_RECONCILED=true`; `T020_CLOSED_WITH_EXISTING_EVIDENCE=true`;
`LEGACY_READER_OR_ADAPTER_REIMPLEMENTED=false`; `INTEROPERABLE_CADERNO_PRESERVED=true`;
`PERSISTED_PROFILE_SCHEMA_CHANGED=false`; `PRIVATE_DATA_PUBLISHED=false`;
`USER_HOST_WRITES=0`; `USER_WORKTREES_CREATED=0`;
`REAL_PILOT_RERUN_BY_THIS_SESSION=NOT_RUN`; `ADR_0002_ACCEPTANCE=PENDING_HUMAN`;
`MERGE_RELEASE_CLEANUP=NOT_RUN`. Demais estados dependem do recibo final por SHA.

### Convergência focal após a primeira CI CLOSE01

No HEAD `b0b3e5f474beae98fc7c901c67cd08a176175714`,
[Spec Kit](https://github.com/thalesvalente/Atlas/actions/runs/40246194666) passou
2/2 jobs. Na [CI de produto](https://github.com/thalesvalente/Atlas/actions/runs/40246194796),
os quatro jobs Windows/Ubuntu normal/-O e a referência pública passaram; navegador
falhou somente em `References remain within viewport at CSS zoom 200%`.

O recibo real da CI registra 20 checks anteriores aprovados, 8 execuções/22
referências de duas fontes, duas navegações internas, quatro estados vazios,
390 pixels, zero erros de página/tráfego externo e bytes das fontes iguais.
Isso é prova parcial, não PASS visual integral. A captura de 200% ainda não existia,
pois a assertiva antecedia sua emissão. T030 acrescenta diagnóstico de geometria
e captura antes dessa assertiva, preservando o requisito e o gate; a correção do
layout será limitada à causa demonstrada. Não há nova aquisição ou piloto.
