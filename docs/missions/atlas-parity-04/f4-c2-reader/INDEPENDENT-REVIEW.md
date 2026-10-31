# Revisão independente C — F4 C2

Revisor: subagente nativo `/root/review_c`, sem autoria ou escrita de código,testes,commits ou workflow. O coordenador apenas publica este parecer recebido do revisor.

Objeto: commit `9bbf6891433bbe1457a818afcd42ead44d95a07e`, tree `5994e923131148f0fb3ffa9217cbea5d5c7a5e0e`, parent `ddbab1b193054404a6bd5d5259a17f26397e9fd0`. PLAN conferido em `5ca6cdc7dbaa78e4bf0d29dc30bb1b9d17659260`.

A revisão estática cobriu aquisição/CLI,parser,validação semântica,schema aprovado,testes,harness de independência,workflow focal e contrato de leitura. Não há achados materiais abertos no escopo sintético declarado.

Foram corrigidos e rechecados: herança da DACL Windows; publicação sem sobrescrita; erros estruturados sem paths em traceback; formas inválidas de requirement/referências; parent contextual; conservação explícita de ciclos; limpeza do parcial por identidade; consistência dos metadados Windows por handle. As contraprovas finais distinguem substituição detectada de substituição impedida pelo SO e exigem preservação de arquivo alheio e ausência de descriptor final.

O revisor leu diretamente os quatro logs e C2_EVIDENCE_JSON da [CI focal41213116001](https://github.com/thalesvalente/Atlas/actions/runs/41213116001), concluída com sucesso no SHA revisado:

| Ambiente | Resultado |
|---|---|
| Windows normal |34PASS|
| Windows -O |34PASS|
| Ubuntu normal |33PASS,1SKIP específico ACL Windows|
| Ubuntu -O |33PASS,1SKIP específico ACL Windows|

Nas quatro combinações,independência SDK/viewer,exclusão da ferramenta dos wheels,execução fora do checkout sem ferramenta/R4 e ownership passaram. SHA/tree/parent e hashes dos inputs coincidem nos recibos. JSON/JUnit foram publicados como artifacts. O revisor não executou Python localmente; runtime local indisponível por erro MXC.

Conclusão: **F4_C2_BLOCKED_EXACT**. A qualificação sintética não resolve SOURCE_FORMAT_UNSUPPORTED (schema real não observado),HARD_BUDGET_UNVERIFIED (256MiB/30s sem mecanismo SO qualificado) e OS_ISOLATION_UNVERIFIED (confinamento arquivos/rede não qualificado).

--synthetic-fixture é facilidade de teste; não comprova origem inventada ou isolamento e não deve ser usado para acervo L1. Handoff exige amostra estrutural sanitizada e qualificação local própria. Este parecer não concede compatibilidade R4,prontidão operacional,aprovação científica,G4/G5/G6,merge,release ou deploy e não afirma CI global verde. Ajuste documental posterior de 'rename' para 'publicação atômica sem sobrescrita por hardlink exclusivo e unlink do parcial próprio' não muda o código revisado.
