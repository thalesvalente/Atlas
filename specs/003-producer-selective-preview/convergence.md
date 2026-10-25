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

## Limites
A prova nova cobre SDK e inspeção pelo viewer instalado; não houve nova sessão de navegador dedicada a dados reais. A associação de evidência sem direção usa mentions; o viewer atual pode não mostrá-la por execução. Isso está declarado no contrato, não escondido por relações input/output inventadas.

`ADR_0001_CHANGED=false`; `ADR_0002_ACCEPTED=false`; `PUBLIC_SOURCE_TRANSFER=[]`; `HOST_REAL_READ=NOT_RUN`; `PHYSICAL_RETIREMENT=NOT_RUN`.

## Modo real de execução
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
