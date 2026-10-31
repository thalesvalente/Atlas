# AP04-F2-DOC-CI-REPAIR-01 — resultado técnico e fechamento

Resultado comprovado no SHA técnico **bd2166651f159e70a8165e0f12c8ad2a3270a0d6**, tree **fd5d73e327e3c780efa4f6aa2437b20eb6eca6e5**: **AP04_F2_DOCUMENTATION_CI_QUALIFIED**. Os seis workflows próprios terminaram completed/success, tentativa 1, com 37/37 jobs success. Quatro suítes completas de fonte e quatro instaladas executaram os mesmos 223 IDs distintos: 191 herdados (168 C4 +23 AP04) e 32 novos, sem falhas, erros, loader errors, duplicatas, ausências ou skips de casos. C revisou esse SHA e seus 37 logs; nenhum finding bloqueante aberto.

Este recibo tem escopo explícito no SHA técnico acima. O commit que o contém exige seus próprios seis workflows e revisão independente, sem herdar o verde anterior. O fechamento externo na PR Draft #15 registra o SHA/tree final e os respectivos runs/parecer; não se cria outro commit para embutir o próprio hash.

## PLAN → EXECUTE → REVIEW

O prompt integral obrigatório 8abf556c6c39fcc54855391f2eeef3d8a8615985 foi lido e conferido: oito seções e marcador END-OF-MISSION-PROMPT COMPLETE. A versão truncada anterior foi substituída por instrução expressa do operador. AP04-POR-v1.0-draft foi preservado, sem desvio necessário ou implementado.

O guard histórico comparava C4..HEAD com seu antigo delta, rejeitando cinco documentos F1 e 14 F2 legítimos. O sucessor verifica os controles e manifests históricos nos objetos originais, congela individualmente os 19 documentos F1/F2 e só admite o novo delta exato de 19 paths depois do F2 terminal 04373bb9. Cada pai/árvore/modo/revisão intermediária é conferido, inclusive alteração proibida depois revertida. Guard antigo, seus 23 testes e manifests históricos permanecem byte-idênticos.

A escreveu exclusivamente o novo guard e suas contraprovas; B escreveu cinco workflows e o controle C4; ORQ publicou onze recibos; C foi revisor nativo real independente, somente leitura e sem autoria. REPAIR-OWNERSHIP.json identifica autorização, finalidade e verificação por path. Publicação por Git Data API, um pai, fast-forward com lease, somente na branch existente da PR #15.

O primeiro reparo 9777 e a otimização f642 passaram nos guards, mas a suíte instalada Windows excedeu o orçamento preservado de 15 minutos. Ambos permanecem como ciclos não qualificados e cancelados nas referências imutáveis de CI-EVIDENCE.json. A leitura Git em lote agora valida integralmente cada frame e conteúdo. O ATLAS021 distribui as suítes completas pelos stages source/installed, mantendo 15 minutos por job, os dez actions/pins em ordem, todos os gates, isolamento e recibos. Nenhum teste foi removido, fracionado ou flexibilizado.

A execução remota confirmou SDK/viewer instalados fora do checkout com R4 ausente; browsers/HTTP/Chromium reais, checks/screenshots C4, managed assets e Spec Kit 1.2.3. CI-EVIDENCE.json contém runs/jobs, IDs, recibos, uploads e hashes. O manifesto suplementar tem 37 entradas exatas, sem auto-inclusão; os históricos continuam intactos.

C-001–C-004 foram corrigidos e fechados em fonte/execução: isolamento dos cenários negativos, preflight independente, autorização de toda revisão intermediária e pins antigos/atuais corretamente separados. A revisão não é aprovação humana, científica ou arquitetural.

## Limites e autoridade

Os ZIP/PNG/XML binários não foram abertos e não houve inspeção manual de pixels. Foram conferidos logs/recibos por SHA, serializers/contagens, nomes/tamanhos/hashes de screenshots, uploads e digests/API de 28 publicações de artefatos. O comparador upstream offline mantém três availability skips em cada um dos três relatórios e cinco falhas no terceiro caso esperado inválido, todos expectation_met=true; isso não é skip/falha dos 223 casos unittest. Etapas de stage inativo têm skips de roteamento explícitos.

Exceção procedural declarada: antes de obter o prompt, o coordenador executou comandos locais somente de metadados Git e inventário de nomes de arquivos de instruções no checkout já aberto. Não houve escrita Git local, código/testes/instalação locais ou acesso a corpus privado/fontes/R4. Essas observações foram excluídas das provas de qualificação, obtidas de GitHub/GitHub Actions. C não auditou independentemente esse trace local.

ADR-0003 v0.2 e descriptor 0.2.0 seguem PROPOSED_NOT_APPROVED; G4 ARCHITECTURAL_DECISION_PENDING. D-001–020/PAR-001–015/G0–G9 preservados em DECISION-COMPLIANCE.md. A missão não promove paridade, ciência, host privado ou conformidade HL7/FHIR e não autoriza F3–F6, File API/UI, merge/release/deploy/promoção/migração/limpeza ou alterações R4/fontes privadas. PR #15 permanece Draft.
