# Decisão humana solicitada — AP04-F2-v0.2

Estado: PENDING_HUMAN_DECISION.
ADR-0003 v0.2: PROPOSED_NOT_APPROVED. Gate: ARC09_APPROVAL_REQUIRED.
Não há G4 PASS ou autorização de implementação.

Objeto da decisão: ADR-0003 v0.2 e descriptor atlas-legacy-presentation 0.2.0 no pacote técnico AP04-F2-v0.2, [SHA c3ea1e82938fd61cc5a22fee973352715a5bb527](https://github.com/thalesvalente/Atlas/commit/c3ea1e82938fd61cc5a22fee973352715a5bb527), tree 986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c.
[MANIFEST.sha256 técnico](https://github.com/thalesvalente/Atlas/blob/c3ea1e82938fd61cc5a22fee973352715a5bb527/docs/missions/atlas-parity-04/f2-legacy-contract/MANIFEST.sha256): SHA-256 dfe50699a7bb9df042264220a356d1f3e4b959df02bac76870e54cd152953b5f.
Esse pacote foi revisado independentemente por /root/review_c, sem findings documentais abertos após correção C-001. O commit que contém esta solicitação acrescenta o recibo e o vínculo explícito, sem modificar o desenho técnico.

**Pergunta única: aprova a ADR-0003 v0.2 e o descriptor 0.2.0 do pacote AP04-F2-v0.2 no SHA c3ea1e82938fd61cc5a22fee973352715a5bb527 como exceção arquitetural delimitada para futura entrada opcional por File API na UI, com leitura legada externa e estado efêmero segregado, sem entrada no Catalog/SDK e sem alterar o protocolo Caderno?**

Uma resposta válida deve ser explícita: APROVO ou REJEITO, citando ADR-0003 v0.2, descriptor 0.2.0 e o SHA acima. Pedido de ajustes mantém PENDING. Silêncio, CI, comentário de agente, publicação ou consentimento funcional anterior não aprovam.

A decisão trata da exceção à exclusividade do reader003. Se aprovada, a alteração futura desse contrato deverá ser versionada e revisada antes da implementação. Nenhuma alteração ocorre em F2. Requisito, evidência, O1–O5, impactos, custo relativo, riscos, oracles e rollback estão na ADR candidata e nos demais documentos técnicos fixados pelo SHA.

A aprovação desta pergunta não inicia F3A/F3B/F4/F5/F6, não concede acesso privado novo, alteração de R4, migração, merge, release, deploy, promoção, aprovação científica ou limpeza. Integração futura segue F1/F2/F3 e G4/G5; demonstração LOCAL privada e browser Windows seguem F5/G6. AP04-POR, PAR/G0–G9 e proteções permanecem intactos.

Se rejeitada, conservar C4/Caderno e fontes; O4 permanece contingência a deliberar, e O2 exige nova avaliação de conformidade/perdas. Nenhuma alternativa será implementada automaticamente.

Identidade deste recibo: o commit/tree que contém este arquivo. A revisão externa do SHA terminal e o handoff Git ficam no corpo da PR Draft de revisão documental. Não se tenta embutir o hash do próprio commit.
