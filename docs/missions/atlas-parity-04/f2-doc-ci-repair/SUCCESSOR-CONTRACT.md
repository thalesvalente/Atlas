# Contrato do sucessor documental F2 — AP04-F2-DOC-CI-REPAIR-01

AP04-POR-v1.0-draft preservado; prompt completo obrigatório 8abf556c6c39fcc54855391f2eeef3d8a8615985. O inventário exato de 19 paths, owners, finalidades, autorizações e verificações está em REPAIR-OWNERSHIP.json. A é único autor dos dois controles novos; B dos seis controles existentes; ORQ dos onze recibos. C é somente revisor. Não há autorização por prefixo de pasta. Entradas são blobs 100644, publicados na branch existente da PR Draft #15 por um pai e lease do HEAD.

## Épocas e história

C4 → AP04 original/reparo → F1 → F2 → reparo atual são épocas distintas. INPUT-SHAS.json fixa nove commits históricos com SHA/tree/parent e 19 documentos F1/F2 por path/blob/SHA256/mode. F1 não possui manifesto público próprio, então seus cinco blobs são congelados individualmente. Não há alegação de CI retroativa.

O guard AP04 histórico e seus 23 testes continuam byte-idênticos. A semântica de seus controles/deltas/manifests é aplicada aos objetos históricos até 47c94d27, sem estender retrospectivamente a antiga allowlist aos documentos F1/F2. Os manifests C1/C2/C3/C4/AP04/F2 continuam intactos.

O novo delta começa estritamente depois de 04373bb910db2e6215cc8bc4212093b649e48456. A árvore terminal fica congelada, exceto os seis controles B literais; o reparo acrescenta os outros 13 arquivos exatos. Cada commit posterior é inspecionado por pai/delta/status/mode e revisão dos controles. Merge, remoção, rename, symlink, gitlink, alteração fora do inventário e mudança ilícita depois revertida são rejeitados.

## Autoridade dos controles

OVERLAY.json exige JSON canônico e inventário/owners/purposes literais com os 19 documentos congelados. MANIFEST.sha256 é ordenado/completo: 19 documentos mais 18 arquivos do reparo, 37 entradas, excluindo a si próprio. Integridade não concede autorização semântica.

O entrypoint das contraprovas é o módulo de testes. Seu preflight independente verifica UTF8, AST e tabela exclusivamente literal antes de executar a fonte do guard naquele processo, sem statements ocultos nas linhas excluídas. Os demais bytes do guard e os controles aprovados são fixados independentemente; o guard fixa os bytes dos testes. Isso não afirma que outro processo de CI nunca tenha executado o guard antes do preflight.

A tabela atual APPROVED_PRIOR_CONTROL_REVISIONS admite **cinco** revisões exatas publicadas/revisadas: guard/testes 9777, guard/testes f642 e workflow ATLAS021 f642. INPUT-SHAS.json registra OID/SHA256/ref de cada uma. Candidatos não integrados são excluídos. A contraprova reconcilia commits/blobs/bytes antigos e atuais; recalcular manifest/overlay não autoriza versões novas. Mudanças futuras exigem novo diff, contraprovas e revisão sem herança automática.

Leituras Git usam cat-file --batch com OID exato e validação integral de header canônico, identidade, tipo, tamanho/limites, payload, LF, SHA1 do conteúdo, ordem e ausência de trailing bytes. Todas as árvores/modos/pais/revisões continuam conferidos por chamada, sem cache PASS.

## Dispatch e CI

A seleção real usa ancestralidade da âncora F2; Git com erro aborta. A linhagem anterior conserva chamada real ao guard histórico estrito. Nome de branch nunca autoriza conteúdo. C4 conserva INPUTS/COMPOSITION/COMPOSITION_TREE/P03_C4_ADAPTERS/ASSETS/manifests e oráculos.

A coleção exige os mesmos 191 IDs distintos herdados (168 C4+23 AP04) mais 32 novos, total 223, com nomes exatos, zero ausências/duplicatas/extras/loader errors/skips/falhas de casos. A checagem antiga 122 permanece junto da forte 191. SDK/viewer instalados fora do checkout com R4 ausente e browsers/HTTP/Chromium/managed assets/Spec Kit 1.2.3 permanecem gates reais.

ATLAS021 possui matriz literal OS×optimize×stage[source,installed]: quatro fontes completas e quatro instaladas completas, mesmo SHA/tree, timeout 15 por job, fail-fast=false, dez actions/pins na mesma ordem. Nenhuma suíte é reduzida/particionada. Steps inativos têm skips de roteamento; casos não podem ter skips. Upload installed-only tem nomes únicos OS/modo/SHA. Browser e comparador upstream continuam obrigatórios. A contraprova da matriz rejeita dez mutações.

## Evidência e fronteira

No SHA técnico bd2166651f159e70a8165e0f12c8ad2a3270a0d6 os seis workflows e 37 jobs passaram; quatro fontes/quatro instalações executaram 223 casos. A sequência 9777→f642→bd216 documenta dois ciclos não qualificados por timeout antes da matriz final. Os cancelamentos continuam nas referências imutáveis de CI-EVIDENCE.json; não foram convertidos em PASS.

O auditor P06 permanece inalterado com FAIL histórico exato para o path/blob ADR-0003 publicado; nenhuma liberação de docs/architecture ou diretório. Plano/GATES/constituição/ADRs/protocolo/schema/reader003/fixtures/fontes/AGENTS/skills permanecem congelados. ADR-0003 v0.2 e descriptor 0.2.0 seguem PROPOSED_NOT_APPROVED; G4 pendente, F3–F6 não iniciadas.

Qualificação exige seis workflows completed/success próprios no mesmo SHA FINAL e revisão C desse SHA/tree. O commit que contém recibos exige suas próprias execuções; o fechamento externo da PR #15 identifica esse SHA e os runs sem ciclo para embutir o próprio hash. Evidência de logs/recibos/upload não é inspeção manual de pixels, ciência, aprovação humana, host privado ou conformidade FHIR. Os limites e a exceção local somente de metadados estão em RESULT.md.
