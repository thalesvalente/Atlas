# AP04 F4-L0 — revisão independente de recibo privado (sem nova leitura científica)

**Missão:** `AP04-F4-L0-QA-INDEPENDENT-RECEIPTS-01`
**Estado de entrada informado pelo operador (não revalidado neste CHAT):** `SOURCE_BYTES_MATCH_F1` para **ARQUIVO 3**, mtime `AMBIGUOUS`, `MTIME_SERIALIZATION_UNVERIFIED`, G4 `BLOCKED`, revisão independente `PENDING`.
**Objetivo:** revisar, no host local Windows, apenas os recibos privados F1/L0, a evidência de comparação SHA-256 do arquivo 3 e a preservação documental, por executor realmente distinto do autor dos recibos. Nenhuma nova leitura do HTML científico, nenhum cálculo de hash do arquivo de origem.

- [PROMPT-CODEX-LOCAL-INDEPENDENT-QA.md](PROMPT-CODEX-LOCAL-INDEPENDENT-QA.md): instrução para **novo Codex LOCAL, em sessão separada da que produziu os recibos**, se independência puder ser comprovada.
- [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md): critérios objetivos, achados e estados.
- [HANDOFF-REVIEW.template.json](HANDOFF-REVIEW.template.json): modelo inicial NÃO EXECUTADO de síntese sanitizada; nunca contém hashes, paths ou IDs privados.
- [MANIFEST.sha256](MANIFEST.sha256): SHA-256 desses quatro arquivos, não incluindo a si próprio.

**Distinção:** igualdade de hashes atual × F1 para o mesmo arquivo/snapshot sustenta **igualdade de bytes no escopo observado**. Não prova mtime, identidade global, parser real, sandbox Windows, L1 ou G4. A regra temporal F1 continua não recuperada; mtime ambíguo NÃO vira MATCH por parecer.

**Entradas Git fixadas:**
- PR #22: `docs/ap04-f4-l0-codex-desktop-handoff-20261101`; parent deste pacote `f487c0982a7ead8b458b9f193a917a2fd3bb0359`.
- [L0 inicial e governança](https://github.com/thalesvalente/Atlas/blob/f487c0982a7ead8b458b9f193a917a2fd3bb0359/docs/missions/atlas-parity-04/f4-l0-codex-desktop-20261101/PROMPT-CODEX-LOCAL-L0.md).
- [F1 sanitizada](https://github.com/thalesvalente/Atlas/blob/a237f446e54927eeeda8ed5e8e9daa83ee09dcb7/docs/missions/atlas-parity-04/f1-legacy-inventory/SANITIZED-HANDOFF.json).
- [C2-D final e bloqueada](https://github.com/thalesvalente/Atlas/blob/86aec49d793d10c1d0b35db58fda747e0febdb23/docs/missions/atlas-parity-04/f4-c2-composition/RESULT.md).

**Privacidade:** o revisor não deve enviar para qualquer chat/PR: paths de fontes, hashes privados, relatórios integrais, payloads, IDs científicos, RF literal, screenshots, segredos. Não há autorização implícita para reabrir fontes; ler recibos somente se isso estiver autorizado na nova sessão local. O relatório detalhado permanece na pasta privada previamente autorizada; não sobrescrever recibos. Sem merge, release, deploy, R4, L1, G4 ou C3.

**Status deste pacote:** `QA_PROMPT_PUBLISHED_NOT_EXECUTED`.
