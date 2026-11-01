# Revisão independente — parecer no SHA final NÃO COMPROVADO

**Estado factual:** `INDEPENDENT_REVIEW_NOT_PROVEN` para a candidata corrigida. Houve revisão Copilot **não autora** registrada na PR #21 no SHA inicial `ab22a78eb22af4ef9651cdd8f652c3cb2755e947`, com **cinco findings reais**; ela não examinou o SHA corrigido. Nesta execução não há ferramenta nativa de subagente `spawn_agent/send_message/wait` habilitada: `NATIVE_SUBAGENTS_NOT_AVAILABLE`. A verificação dos reparos pelo próprio executor é **autoavaliação autoral** e não qualifica a candidata como aprovada.

## Autoavaliação adversarial, limitada

- B refuta tentativa de usar `declared_id` como campo polimórfico: mesma string de key e records native escolheria entidade de outro namespace. É obrigatório um discriminante e índice estrutural isolado.
- C refuta indexação global por texto: precisa source/snapshot e invalidação de sessões.
- D refuta generalização de ID nativo: 50 grupos colidentes não se tornam 50 identidades certas, embora parent_keys únicos possam ser navegáveis por outra base.
- E/F refutam construção heurística de key e seleção do primeiro elemento.
- C2 e F3A hoje implementam a regra native-only separadamente; adendo proposto exige alinhamento de validadores e dispatch, não contorno de `validate_descriptor`.
- O1 deve impedir nova autoridade científica, causalidade falsa, Project/Experiment artificiais, alteração de schema/protocolo Caderno, acesso a URI e downgrade silencioso.
- As contagens F1 e os casos inventados não são prova de execução do reader nem paridade em fontes reais.
- A proteção CI histórica pode recusar novos paths; o revisor não pode pedir `continue-on-error` ou alteração de pins/allowlist para silenciar.

## Findings do Copilot — disposição autoral, a confirmar por revisor distinto

- `r4434300170`: contagens F1 agora descritas como baseline sanitizada e escopada em COMPATIBILITY.
- `r4434300181`: spans Markdown corrigidos no descriptor e nas contraprovas.
- `r4434300187`: obrigação estrutural de `node.parent`/`parent_key_literal` documentada conforme 0.2.0 e nova igualdade com `declared_key_literal` no 0.2.1.
- `r4434300194`: grafia “órfãos” corrigida.
- `r4434300198`: token de conclusão alinhado entre HANDOFF e RESULT, com manifesto regenerado.

**Gate ainda não satisfeito:** nenhum desses itens foi reavaliado por executor comprovadamente independente **no novo commit**. Não resolver threads em nome do revisor nem declarar `PASS` de revisão. A CI poderá permanecer vermelha pelo guard histórico de paths K: achado `C4_AP04_F2_GUARD_SUCCESSION_REQUIRED_FOR_NEW_K_DOC_PATHS`, atribuído somente ao owner C4.

## Gate para revisor verdadeiramente distinto

Ler commit final e blobs de `INPUT-SHAS.json`; contestar O0 com A–F; verificar namespace/um snapshot/proof/colisões/ciclos/quotas/TTL/escopo ARC-09; validar `MANIFEST.sha256`, parent único, somente paths K; apontar findings reproduzíveis, nível de severidade, disposição e SHA exato. Publicar parecer assinado por executor diferente antes de marcar `C2_K_IDENTITY_DECISION_READY_FOR_HUMAN_REVIEW`. Aprovação humana ainda é ato distinto.

**Conclusão de QA atual:** `C2_K_REVIEW_BLOCKED_EXACT`, `NATIVE_INDEPENDENT_QA=NOT_RUN`, `INDEPENDENT_REVIEW_NOT_PROVEN`, `ARC09_APPROVAL=NOT_RECEIVED`. Revisão Copilot anterior é entrada de QA, não aprovação das correções.
