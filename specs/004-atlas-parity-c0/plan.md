# Plano agregador 004 — ATLAS-PARITY-03-C1

## Arquitetura e ownership

ARC-01–09 e ADR-0002 regem a composição. Runtime Python/JS existente permanece
congelado em P02; SDK independente, HTTP loopback, fontes sintéticas públicas.
Sem nova dependência de runtime, schema, versão persistida ou adaptador.

| Responsável | Paths/atividade exclusivos |
|---|---|
| /root | composição, publicação, agregadores 004 e docs da missão C1 |
| /root/topology_speckit | scripts/qa/speckit_audit.py e negativas correspondentes |
| /root/ci_browser | três workflows autorizados, browser.mjs, harness P02/P06 e prova instalada |
| /root/independent_review | leitura do SHA final; nenhuma autoria no delta |

P01/P03 excluídos. Workstreams recebidos e branches fonte são preservados.
O ponteiro global não será escrito. Helpers usam
SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0 e SPECIFY_FEATURE_NO_PERSIST=1.

## PLAN → EXECUTE → REVIEW

1. Conferir main, cinco entradas fixadas, árvores, parentage e manifests.
2. Compor árvore sem conflitos e merge com os três pais baseline/P02/P06;
   nenhum squash, rebase ou commit de origem reescrito.
3. Reparar auditoria com opt-ins fixos, negativos e pin dos três blobs P02;
   comparar todo packages/protocol com c2d00fb, incluindo adições e remoções.
4. Corrigir H06-01/02/03 usando identidades do produto, sem duplicar seu sort;
   adaptar P06 ao binding global após contraprova executada e atribuída.
5. Criar ambientes em RUNNER_TEMP: clean_install comprova SDK/viewer isolados;
   somente depois instalar jsonschema de teste e executar coleção com zero skips.
6. Executar browsers normal/adversarial/referências/P06/P02 em Actions;
   registrar pacotes/fontes, versões, hashes, seis capturas P02 e fontes intactas.
7. Publicar PR Draft própria e obter CI do SHA exato; revisor sem autoria lê esse
   objeto. Correções materiais recebem novo commit, novo teste e nova revisão.
8. Consolidar documentos e manifesto, executar gates também no commit documental;
   vincular recibo externo final ao SHA que não pode ser autoembutido no commit.

## Controles e limites

Auditoria histórica preserva default estrito. Flags explícitas:
--allow-presentation-delta --allow-p02-c0-delta. O primeiro opt-in conserva apenas
as seis exceções históricas; o segundo exige três blobs P02 exatos e protocolo
c2 íntegro, sem autorizar delta adicional do read_model pela exceção histórica.

Suites completas e instaladas podem repetir casos: a coleção ordenada de IDs é
o denominador, com OS/modos/reruns separados. Checks internos Node não viram
unittest adicionais. Browser P02 não simula zoom nativo. Cenário legado de CSS
zoom mantém seu recibo próprio sem contaminar css_zoom_used=false do P02.

RUNNER_TEMP é obrigatório para consumidores CI. Fontes CJK/emoji são tooling do
runner, sem incorporar fonte nova ao produto. Recibos legados human_protocol_acceptance
PENDING são históricos; aceite da direção ADR-0002 na PR #5 permanece vigente.

## Convergência

Os gaps recebidos são auditoria (FR-006), seletores/oráculos (FR-002/003/009),
isolamento/browser P02 (FR-004/010) e ligação agregada da feature (FR-011).
As tarefas novas são append-only depois de T011. Nenhuma tarefa exige P03, P01,
coorte privada, teste de host ou aceitação científica.
