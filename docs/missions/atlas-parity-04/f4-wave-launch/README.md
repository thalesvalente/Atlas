# ATLAS-PARITY-04 — Onda F4: próximos prompts executáveis, sem mudar o plano

**Base conhecida:** F2 PR #15 `54bb16d350f7bc34fafb95438bd64a2397d58bf3` (tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`), F3A PR #16 `f0d39787e3fb93bfd70ad096824505ba298c6881`, F3B PR #17 `72118073cc72b4d3cdca21fcc64c18cf742ae384`. ADR-0003 v0.2 `APPROVED_SCOPED` na PR #15 comentário `6539419419`, pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527`.

**Escopo:** execução da F4 já prevista em `AP04-POR-v1.0-draft`. Os subpassos C0/C1/C2/C3/C4/L1 são apenas **decomposição operacional**. Não revisam F0–F6, G0–G9, PAR-001–015 ou a ADR. Se uma necessidade de desvio aparecer, registrar motivo e obter aprovação aplicável ANTES da mudança.

| Frente | Ambiente | Esforço recomendado | Quando iniciar | Branch/ownership | Resultado-alvo |
|---|---|---|---|---|---|
| [C0 — Contrato 003](01-F4-C0-READER003-CONTRACT-CHAT.md) | CHAT GitHub/Actions | Extra High | AGORA | `docs/atlas-parity04-f4-reader003-20261031` | `F4_C0_READER003_SCOPED_CONTRACT_REVIEWED` |
| [C1 — Escala do grafo](02-F4-C1-GRAPH-SCALE-CHAT.md) | CHAT GitHub/Actions | Extra High | AGORA, paralelo | `feat/atlas-parity04-f3a-graph-20261031` (existente) | `F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION` |
| [C2 — Leitor externo](03-F4-C2-EXTERNAL-READER-CHAT.md) | CHAT GitHub/Actions | Extra High | AGORA, paralelo | `feat/atlas-parity04-f4-external-reader-20261031` | `F4_C2_EXTERNAL_READER_READY_FOR_LOCAL_QUALIFICATION` |
| [C3 — Integração](04-F4-C3-INTEGRATION-CHAT.md) | CHAT GitHub/Actions | Extra High | Depois de C0+C1+C2+F3B | `integrate/atlas-parity04-f4-composition-20261031` | `F4_C3_INTEGRATED_CANDIDATE_GLOBAL_CI_PENDING` |
| [C4 — Gates globais](05-F4-C4-GLOBAL-CI-CHAT.md) | CHAT GitHub/Actions | Extra High | Depois de C3, sem writer concorrente | Mesma branch C3, controle exclusivo CI | `F4_G5_INTEGRATION_CI_QUALIFIED_HOST_GATE_DEFERRED` |
| [L1 — Prova da fonte](06-F4-L1-LOCAL-READ-PROOF.md) | Codex LOCAL Windows | Extra High | Depois de C2 e autorização explícita NOVA de leitura | Saída `.local` privada e branch QA sanitizada própria | `F4_L1_LOCAL_READER_QUALIFIED_SCOPED` |

**Paralelismo:** C0+C1+C2 independentes, em três CHATs; depois C3 e L1 podem trabalhar em ambientes distintos, com input já congelado e nenhum writer sobreposto. C4 só inicia após C3 congelar; L1 não escreve na branch do integrador. **F5 é posterior e requer autorização própria.**

## Regras fixas

- Não criar worktrees/clones persistentes. Preferir branches convencionais (as branches C0/C2/C3 são preparadas; C1 usa a existente; C4 reutiliza C3).
- Nunca modificar a F1, R4 ou corpus privado por conveniência. L1 exige autorização de fonte específica NOVA; a permissão exclusiva da F1 não se transfere.
- Caderno/RO-Crate/Process Run permanecem; HL7/FHIR só capacidade futura por domínio. Nenhum novo endpoint legado, import R4 ou conversão persistida.
- C3 só implementa File API opcional depois de C0 versionar/revisar o contrato 003; nenhuma integração antes dos quatro SHAs comprovados.
- Os gates históricos não devem ser desativados/afrouxados. C4 qualifica sucessão por path/blob exatos e exige CI do SHA final.
- G4 só pode ser sustentado por L1 real; G5 por C4 CI integrada. G6 browser com corpus privado pertence à F5, não antecipar seu resultado.
- Nenhum merge em main/PRs, release, deploy, promoção, migração, limpeza ou aprovação científica.
- Git-first para prompts, código e evidências públicas; recibos e descriptors privados continuam apenas em armazenamento LOCAL autorizado.

**Estado desta publicação:** `F4_PROMPTS_PUBLISHED_NOT_EXECUTED`. Não tratar a criação de branches/prompts como execução de produto, CI, aprovação de novos dados ou G4/G5.
