# Solicitação objetiva de decisão humana — AP04-F2-v0.2

Estado: PENDING_HUMAN_DECISION. ADR-0003 v0.2: PROPOSED_NOT_APPROVED.
ARC09_APPROVAL_REQUIRED. Ainda sem aprovação de G4 ou autorização de implementação.

A pergunta será fixada no SHA técnico publicado e revisado, sem auto-hash do commit que registra o recibo.

**Pergunta única:** aprova a ADR-0003 v0.2 e o descriptor de apresentação 0.2.0 deste pacote AP04-F2-v0.2, identificados pelo SHA técnico e MANIFEST.sha256 no handoff, como exceção arquitetural delimitada para futura entrada opcional por File API na UI, com leitura legada externa, estado efêmero segregado, sem entrada no Catalog/SDK e sem alterar o protocolo Caderno?

A resposta deve ser explícita (APROVO ou REJEITO), citar versão e SHA exato. Pedido de ajustes mantém PENDING; silêncio, CI, comentário de agente, publicação ou consentimento funcional anterior não aprovam a proposta.

Escopo da decisão: exceção à exclusividade do contrato003 para apresentação neutra, riscos/limites/rollback descritos em ADR-0003-v0.2-CANDIDATE.md e ARCHITECTURE-OPTIONS.md. Se aprovada, a alteração futura do contrato003 deverá ser versionada e revisada antes da implementação. Nenhuma alteração ocorre nesta F2.

A aprovação desta pergunta não inicia F3A/F3B/F4/F5/F6, nem autoriza fonte privada nova, alteração de R4, migração, merge, release, deploy, promoção, aprovação científica ou limpeza. A integração futura segue dependências F1/F2/F3 e gates G4/G5; prova LOCAL privada e browser Windows seguem F5/G6. Plano AP04, PAR/G0–G9 e proteções ficam intactos.

Se rejeitada: conservar C4/Caderno e fontes, usar O4 somente como contingência a deliberar ou revisar documentalmente O2 com provas de conformidade/perdas. Sem implementação automática de alternativa.
