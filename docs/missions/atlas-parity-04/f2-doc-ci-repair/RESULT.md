# AP04-F2-DOC-CI-REPAIR-01 — reparo em qualificação

Estado: REPAIR_CONTINUES_AFTER_WINDOWS_TIMEOUT. Não é AP04_F2_DOCUMENTATION_CI_QUALIFIED.

PLAN: prompt completo 8abf556c6c39fcc54855391f2eeef3d8a8615985, épocas C4/AP04/F1/F2 e dezenove documentos reconciliados. Dezenove paths exatos de reparo fixados antes da edição; A e B com arquivos exclusivos, C independente sem autoria, ORQ único publicador.

EXECUTE: o primeiro SHA técnico 9777d1a2dc58ab803b92b518d1e0a70ba0f8847e, tree 37fe3132c3e4b6a4161af4956a0659189136c1c1, preservou 526 blobs existentes e modificou somente seis controles de CI, acrescentando treze arquivos autorizados. A sucessão por épocas corrigiu a raiz que negava os cinco documentos F1 e catorze F2. Guard/testes/manifests históricos, produto e protocolo permaneceram intactos.

## Execução real e falha independente

Nesse SHA, cinco dos seis workflows terminaram success; ATLAS021 41151599012 terminou cancelled. Foram 33 jobs: 31 success e dois Windows cancelled. As quatro células AP04 passaram em 23 testes históricos mais 27 novos, inclusive as contraprovas C-001/C-002/C-003. Ubuntu instalado comprovou 218 IDs únicos (191 herdados + 27 novos), zero perdas/duplicações/skips/loader errors/falhas. Os quatro browsers C4 passaram nos 31 checks.

Windows fonte passou 12 testes de protocolo, 131 QA e 75 viewer. ATLAS021 jobs 124389144379 e 124389144600 foram cancelados na etapa de suíte instalada, aos 914 e 923 segundos, com limite configurado de 15 minutos. As execuções QA de fonte duraram 592.157s e 694.572s; a segunda execução instalada ficou incompleta. Não há prova instalada Windows completa nesse SHA, e nenhuma qualificação lhe é atribuída.

O reparo seguinte reduz processos Git por leituras em lote de objetos exatos. O framing confere OID, tipo, tamanho, separador, bytes e SHA-1; os snapshots, pais, modes e todas as revisões de controles continuam validados a cada chamada. Nenhum cache PASS, teste removido, subconjunto, aumento de timeout, alteração de pin ou bypass foi introduzido. Os dois hashes de revisão anterior correspondem exclusivamente aos bytes já publicados e revisados em 9777. Há 31 novos métodos definidos (27 preservados + quatro contraprovas de framing/pins); sua execução real ainda depende da CI deste candidato.

REVIEW: C revisou independentemente os blobs/deltas/37 hashes do primeiro SHA e confirmou C-001/C-002/C-003 em fonte e execução AP04. A revisão do candidato em lote identificou C-004, um pin histórico preenchido no lugar errado; foi corrigido antes de qualquer publicação e ganhou contraprova específica. C não encontrou finding bloqueante na fonte corrigida; o fechamento por execução permanece pendente.

CI-EVIDENCE.json conserva resultados, IDs, jobs, artefatos e limitações reais. Screenshots/JSON/JUnit foram conferidos por identidade e relação entre fontes congeladas, recibos/logs e uploads; ZIP/PNG/XML não foram abertos nem pixels inspecionados. O comparador externo RO-Crate offline conserva seus skips e exemplo negativo esperados; não é certificação Caderno/Process Run nem zero skip global externo.

O commit que contém estes recibos exige seis workflows completed/success e revisão independente no próprio SHA terminal. A conclusão externa será registrada na PR #15 sem ciclo de auto-hash.

AP04-POR, ADR-0003 v0.2/descriptor 0.2.0 propostos, G4 pendente, reader003, Caderno, runtime, R4 e fontes permanecem intactos. Sem F3–F6, File API, merge/release/deploy/promoção/migração/limpeza ou aceite científico.
