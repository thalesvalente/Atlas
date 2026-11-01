# Revisão independente — STATUS PENDENTE

**Estado factual:** `INDEPENDENT_REVIEW_NOT_PERFORMED`. Nesta sessão não havia ferramenta de subagente nativo `spawn_agent/send_message/wait` ou equivalente habilitada, nem outro revisor efetivamente chamado. A análise adversarial abaixo é **autoavaliação do autor**, não parecer independente. Não simular segunda assinatura ou GATE PASS.

## Autoavaliação adversarial, limitada

- B refuta tentativa de usar `declared_id` como campo polimórfico: mesma string de key e records native escolheria entidade de outro namespace. É obrigatório um discriminante e índice estrutural isolado.
- C refuta indexação global por texto: precisa source/snapshot e invalidação de sessões.
- D refuta generalização de ID nativo: 50 grupos colidentes não se tornam 50 identidades certas, embora parent_keys únicos possam ser navegáveis por outra base.
- E/F refutam construção heurística de key e seleção do primeiro elemento.
- C2 e F3A hoje implementam a regra native-only separadamente; adendo proposto exige alinhamento de validadores e dispatch, não contorno de `validate_descriptor`.
- O1 deve impedir nova autoridade científica, causalidade falsa, Project/Experiment artificiais, alteração de schema/protocolo Caderno, acesso a URI e downgrade silencioso.
- As contagens F1 e os casos inventados não são prova de execução do reader nem paridade em fontes reais.
- A proteção CI histórica pode recusar novos paths; o revisor não pode pedir `continue-on-error` ou alteração de pins/allowlist para silenciar.

## Gate para revisor verdadeiramente distinto

Ler commit final e blobs de `INPUT-SHAS.json`; contestar O0 com A–F; verificar namespace/um snapshot/proof/colisões/ciclos/quotas/TTL/escopo ARC-09; validar `MANIFEST.sha256`, parent único, somente paths K; apontar findings reproduzíveis, nível de severidade, disposição e SHA exato. Publicar parecer assinado por executor diferente antes de marcar `C2_K_IDENTITY_DECISION_READY_FOR_HUMAN_REVIEW`. Aprovação humana ainda é ato distinto.

**Conclusão de QA atual:** lacuna material identificada e proposta pronta para revisão, mas `NATIVE_INDEPENDENT_QA=NOT_RUN`; `ARC09_APPROVAL=NOT_RECEIVED`.
