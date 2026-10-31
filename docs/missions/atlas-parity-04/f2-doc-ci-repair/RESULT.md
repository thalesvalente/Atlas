# AP04-F2-DOC-CI-REPAIR-01 — resultado em qualificação

Estado: IMPLEMENTED_PENDING_REAL_ACTIONS_AND_REVIEW. Não é AP04_F2_DOCUMENTATION_CI_QUALIFIED.

PLAN: reconciliados C4/AP04/F1/F2, árvores/pais e os dezenove documentos exatos; prompt completo 8abf556c6c39fcc54855391f2eeef3d8a8615985 validado. Ownership de dezenove paths de reparo definido antes da edição. A e B têm arquivos exclusivos; C é independente e sem autoria; ORQ publica na branch existente.

EXECUTE: o sucessor separa épocas históricas da autoria posterior ao F2 terminal, congela o restante da árvore, preserva guard/testes/manifests históricos e exige controle independente do overlay. Dispatch por ancestralidade conserva fallback real anterior. Regressão instalada exige os 191 IDs herdados e registra novos IDs sem inventar contagem.

REVIEW: revisão preliminar C aceitou o plano como compatível com AP04-POR, apontando riscos de validação por época, cobertura positiva F1 e exclusão de linhas no preflight. A implementação e os gates reais ainda precisam da revisão no SHA publicado. Não se transfere aprovação por esse parecer de plano.

A causa original foi confirmada nos seis workflows/33 jobs terminais: o guard de reparo AP04 negava cinco documentos F1 e catorze F2; uploads/recibos ausentes eram consequências. CI-EVIDENCE.json distingue essa evidência das execuções novas.

As evidências de CI e revisão do commit que contém estes recibos serão fechadas externamente na PR Draft #15. Nenhum manifesto histórico, plano, documento técnico F2, ADR, DECISION-REQUEST, Caderno/protocolo/runtime/R4 ou fonte privada foi editado.

Sem desvio de AP04-POR; ADR-0003 v0.2 e descriptor 0.2.0 permanecem propostos, G4 pendente. Não há implementação de File API/F3–F6, merge/release/deploy/promoção/migração/limpeza ou aceite científico.
