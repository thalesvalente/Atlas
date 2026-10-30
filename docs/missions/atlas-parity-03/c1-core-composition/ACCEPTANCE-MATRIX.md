# Matriz de aceitação — C1

Provas de código abaixo pertencem a `af393e4c0cca19161f49bf9d847bd22617be15fb`, tree `e2a5731d0057f1676e4112d57061773a72e4fc6e`.
O SHA documental e seus gates próprios são confirmados pelo recibo terminal na
[PR #11](https://github.com/thalesvalente/Atlas/pull/11). Não há herança de resultado entre SHAs.

| Critério | Evidência concreta | Estado do código |
|---|---|---|
| Inputs, árvores, ancestry | INPUT-SHAS / MERGE-TOPOLOGY; merge com três pais | PASS |
| Manifests congelados | 55/55 e 22/22 na origem; nove desvios C1 explicitados | PASS |
| Auditoria deny-by-default | default RED esperado; opt-ins exatos; 15 casos de auditoria | PASS |
| Protocolo, governança e skills | hashes baseline; negativas por edição/adição/remoção | PASS |
| Windows e Ubuntu normal/-O | 122 IDs iguais por célula, zero falhas/erros/skips | PASS |
| SDK/viewer independentes | consumers externos ao checkout, sem R4 | PASS |
| Wheels e assets | quatro assets em wheel/instalado/HTTP iguais a Git | PASS |
| P06 invariância | 64 arquivos nas quatro células | PASS |
| Spec Kit 1.2.3 | CLI e helpers 003/004 reais; NO_PERSIST | SUCCESS |
| H06-01/02/03 | fonte+ID, métrica e cabeçalhos; três cenários legados | PASS |
| P02 C0 instalado | JSON, seis PNGs, glifos/fontes, reflow, teclado e foco | PASS |
| P06 troca de pacote | snapshot expira estado antigo; B íntegra e seleção nova | PASS |
| Rede e página | cinco jornadas sem requisições externas ou erros de página | PASS |
| Fontes sintéticas | hashes antes/depois; mutação P06 somente pelo driver esperado | PASS |
| Revisão independente de código | revisor nativo real sem autoria; zero bloqueantes | PASS_SCOPED |
| CI/revisão do commit documental | novos runs e parecer por SHA no recibo externo final | EXTERNAL_RECEIPT_REQUIRED |
| PR/refs de origem/main | reconciliar no fechamento; PR permanece Draft | EXTERNAL_FINAL_READ_REQUIRED |

Os 122 unittest são a coleção integrada observada, sem dupla contagem por OS,
modo, subprocesso ou seleção focal. Os checks browser têm seus próprios recibos.
O comparador histórico de referências públicas preserva o escopo offline anterior.
P02 não declara zoom nativo nem certificação WCAG e não usa CSS zoom.

O recibo externo só declara C1_CORE_CANDIDATE_READY após todos os gates no head
final. Qualquer falha deve gerar C1_BLOCKED_EXACT com job/step/arquivo/precondição.
