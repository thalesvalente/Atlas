# Handoff — convergência das 18 disposições

## Estado e localização

**18/18 decisões técnicas registradas.** Distribuição: 10
`SUPERSEDED_BY_DESIGN`, 4 `RETAIN_AND_IMPLEMENT`, 3 `REJECTED_WITH_REASON`,
1 `DEFERRED_HUMAN_DECISION`. Há estados diferentes nos subrequisitos; em especial,
uma PR tecnicamente sucedida não recebe aceite privado por consequência.

- Repositório: `thalesvalente/Atlas`.
- Base consolidada preservada: `8f8fe01c3041361aa2607194d66af6a640d834ad`.
- Branch própria: `fix/atlas-convergence18-20261108`, PR Draft, integrador P00.
- PR #40: Draft separada, `7ac3e76d12f6d2e59d235458dc122d85850cf499`, intacta.
- SHA qualificado, tree, PR e CI: **recibo terminal O4/O5 na conversa da PR**,
  com `ATLAS-CONVERGENCE-QA-SHA.json`. Este documento versiona o contrato de
  handoff; não declara antecipadamente o resultado de um job ainda não observado.

## Entrega funcional

A rota `/` passa a tratar seleção, detalhe e filtros de projeto/experimento como
contexto de um snapshot. Rebuild ou reinício invalida o contexto inteiro, ainda
que IDs declarados e bytes sobrevivam. Uma simples verificação GET conserva o
snapshot anterior e seus vínculos. Busca/status podem persistir; preferências
dependentes da fonte só voltam na mesma geração/instante/fontes do catálogo.

GET e POST são processados em fila. Um GET iniciado durante rebuild aguarda sua
conclusão; um rebuild solicitado durante GET não é descartado; falhas não deixam
a fila presa. A aplicação distingue indexação, consulta observada e publicação
declarada do pacote, sem inventar uma data científica para preencher ausências.

O adaptador externo verifica cadeia física, specs e módulos em cache antes da
execução; carrega o spec validado e restaura `sys.path`. Namespace legítimo é
preservado. Produtor confiável e dependências continuam confiáveis; a mudança
não oferece sandbox do host nem retoma o antigo leitor O1.

## Provas e limites

RED foi executado na baseline: sete falhas nos dez casos de estado/concorrência
e seis falhas nos oito casos iniciais de origem; os controles positivos passaram.
Os testes de origem foram corrigidos após revisão para propagar e medir `-O`
no subprocesso isolado, e o RED foi repetido nesse modo de forma real.

As matrizes O1 continuam congeladas com os findings da época. Os recibos O3
registram os novos bytes, testes GREEN e revisões não autoras. A CI final observa
build/install, Windows/Ubuntu normal/-O e Chromium; não substitui aceite humano
nem prova sobre um acervo privado. A diferença entre commit testado e HEAD
documental deve ser conferida no recibo terminal, inclusive após qualquer alteração.

O guard Spec Kit identificou `tasks.md` da Feature 001 como baseline protegida.
Os ledgers originais foram preservados; o novo [ledger desta missão](tasks.md)
faz o crosswalk com as specs aprovadas. CLI ausente ficou NOT_RUN, sem instalação,
repin, relaxamento de checks ou alteração dos normativos congelados.

## Decisões humanas que continuam abertas

| Objeto | Estado / consequência |
|---|---|
| ARC-09 / descriptor 0.2.1 no objeto congelado `d5bdc86` | Decisão versionada não recebida; sem ativação ou evolução normativa. |
| Ampliação do aceite OLD/NEW/zoom além do ato restrito #39 | Não foi produzida nesta missão; refinamentos já aceitos não são reabertos. |
| Aquisição O1 produtiva / eventual subsistema OS histórico | Não ativado; exige autorização e qualificação próprias. O FAIL histórico de sucessão #20 permanece. |
| Testemunho L0 e revisão de privacidade das fontes privadas exatas | Não executados aqui; validador histórico defeituoso rejeitado como gate do produto. |
| Merge das PRs de convergência e #40 | Requer autorização específica. Draft e CI verde não concedem merge. |
| Deploy, release, migração, exclusão de branches/worktrees/arquivos | Não autorizados nem executados nesta missão. |

O contrato externo 0.2.0 continua aprovado no seu escopo opcional; sua via
File API/RAM/TTL é distinta de Native View Files. Os 37 jobs históricos da #31,
os testes sintéticos e os controles de checksum não aprovam a proposta 0.2.1.

## Recuperação e continuidade

Consultar a [matriz nominal e justificativas](ATLAS-CONVERGENCE-DECISIONS-18.md),
o [CSV por requisito/item](ATLAS-CONVERGENCE-DECISIONS-18.csv), o
[DAG](ATLAS-CONVERGENCE-DAG.md) e a
[receita de clone](ATLAS-CONVERGENCE-PORTABILITY.md). O
[manifesto público](PUBLIC-EVIDENCE-MANIFEST.json) permite autenticar os recibos
e seus autores distintos.

A próxima intervenção deve partir do SHA terminal observado, preservar os
19 pareceres históricos e a recuperação #40, e verificar se houve alteração
posterior de HEAD/CI/reviews. Não reconstruir a matriz de 1.016 entradas, não
reabrir tarefas já qualificadas e não limpar dados privados como consequência
automática desta entrega. Os códigos de resultado do recibo distinguem
EXECUTADO, VERIFICADO, NOT_RUN, SKIP e gate humano; pendência humana não é PASS.
