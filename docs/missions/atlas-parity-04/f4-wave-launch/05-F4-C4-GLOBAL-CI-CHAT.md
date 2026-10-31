# AP04-F4-C4-GLOBAL-CI-CHAT-01 — qualificar sucessão F3/F4 sem enfraquecer gates

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub + GitHub Actions. **Esforço:** Extra High, seleção MANUAL.  
**Repositório:** `thalesvalente/Atlas`. **Branch de escrita:** a MESMA branch existente do integrador F4, `integrate/atlas-parity04-f4-composition-20261031`, **somente depois** de C3 encerrar e congelar seu SHA. Não criar branch de CI, nova worktree, clone ou PR desnecessária.  
**Resultado-alvo:** `F4_G5_INTEGRATION_CI_QUALIFIED_HOST_GATE_DEFERRED`, restrito à CI global e revisão independente; G4 LOCAL e G6 ainda separados.

## Precondições e ancestralidade

- F2 PR #15 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.
- F3B PR #17 `72118073cc72b4d3cdca21fcc64c18cf742ae384`, sua tree, manifestos e revisão.
- F3A PR #16 e **sucessor C1 escalável** (usar SHA FINAL comprovado, não antigo 1.000 nós).
- Contrato C0 versionado e leitor C2 público, por SHA/tree/parent congelados nos handoffs.
- C3 composição final com SHA/tree/parents/CI focal/parecer, e sem writer C3 ativo.

A branch C3 deve conservar ancestry dos quatro inputs. Confirmar todos os SHAs e objetos pelos seus manifestos. Se faltar uma dependência, `F4_C4_INPUT_BLOCKED_EXACT` e não mexer em guard. Confrontar AP04-POR F4/G4/G5, ARC-01–09, ADR-0003 v0.2 `APPROVED_SCOPED`, F1 G1, F2, PAR-001–015, `reader003` adendo revisado e o `GLOBAL-GATE-REPAIR-CONTRACT.md` da F3A (mais causas F3B).

## Ownership exclusivo: apenas QUALIFICAÇÃO

C4 pode escrever exclusivamente scripts/guards/dispatchers de CI identificados, workflows de CI estritamente necessários, seus testes adversariais com prefixo `atlas_parity04_f4_c4_*` e `docs/missions/atlas-parity-04/f4-c4-ci/`; **não modificar** renderer F3A/B, leitor C2, shell C3, protocolo, schemas ou contrato C0. Qualquer file extra exige justificativa e ownership explícitos ANTES da alteração.

Subagentes: A proveniência/epochs/guard; B workflows/tooling/testes; C QA independente somente leitura, sem autoria. Coordenador único writer e publisher, não compartilhar worktree. Se agentes não disponíveis, executar trabalho técnico seguro e reportar ausência de review, nunca simular PASS.

## Reparar a causa real, não o resultado da CI

O F3A/F3B foi focalmente qualificado, mas gates globais antigos rejeitam:
1. História F2 congelada que não autorizava novos `PLAN.md`, componentes e docs F3A/F3B;
2. Inventário de fixtures C4 que não admite fixture sintética F3A como se fosse histórica;
3. Collection/tooling antigo de ATLAS021 que descobre novo teste browser sem Playwright, gerando `ERR_MODULE_NOT_FOUND`.

**Confronte os logs NOVOS do SHA C3**, pois a causa pode ter mudado. Não assumir que todos os workflows falham pelo mesmo motivo. Produzir um sucessor explícito por epochs C4→AP04→F1→F2→F3A/C1→F3B→C0/C2→C3→C4, com SHA/tree/parent/mode/blobs e paths exatos. Validar todos os commits de cada ramo, inclusive edição transitória não autorizada depois revertida. Nenhum `docs/**`, `.github/**`, `scripts/**`, `tests/**`, `specs/**` como allowlist genérica.

Implementar proteção de conteúdo **independente do manifesto editável** (por bytes/AST/controle revisto) e overlay suplementar canônico que cubra TODOS os paths autorizados. Manifestos históricos C1/C2/C3/C4/AP04/F1/F2/F3A/F3B devem permanecer byte-idênticos. Não liberar mudanças de protocolo, ADR, reader003 fora do adendo C0, SDK ou imports R4. Auditor P06 histórico continua fail-closed com exceção exata da ADR proposta previamente autorizada, não exceção para pasta inteira.

**Tooling:** instalar somente versões fixadas necessárias à coleção completa nos jobs corretos, sem substituir testes por skip, xfail, roteamento apenas por nome de branch, `continue-on-error`, `paths-ignore`, `|| true`, `if:false`, actions não fixadas ou alterar pins históricos para verde.

## Contraprovas e CI terminal

Em repositórios sintéticos, positivos para a composição exata; RED para path extra, symlink, rename, mode errado, alteração de docs F1/F2/F3, adendo C0 adulterado, manifestos rehashados, guard relaxado, branch lookalike, input sem ancestry, C4 ASSETS/fixtures/reader003 históricos adulterados, alteração transitória revertida, perda de teste herdado, token stale validado indevidamente, dados privados incluídos ou ADR/G4 artificialmente promovidos.

Verificar Windows/Ubuntu × normal/`-O` com zero skips/erros/falhas, F2 **223 IDs anteriores** preservados, F3A seus 22 métodos + 17 jornadas Chromium anteriores e novos casos de escala, F3B seus 24 métodos e **380 IDs de recibos por célula** (não somar essas contagens como se fossem todos métodos unitários), C2/C3 novos. Recontar identidades por suite realmente coletada.

Exigir seis workflows globais anteriores (ATLAS021, P06, P03, C4, ATLAS003, AP04 successor), workflows F3A/F3B/C2/C3 aplicáveis e guard F4 novo, todos executados/atribuídos ao **MESMO SHA FINAL** após todo commit documental. Se alguns não acionarem, diagnosticar trigger sem desativá-los e registrar `CI_NOT_TRIGGERED`. Browser real (Chromium) e Spec Kit 1.2.3 no SHA, SDK/viewer sem R4 e Caderno sem sidecar. Não transferir PASS de SHA anterior.

A revisão independente deve conferir HEAD terminal, todos os jobs/logs/artifacts, história, negativos e isolamento. Registrar limites de inspeção de ZIP/PNG/XML e não afirmar pixels inspecionados sem olhar. Um commit de fechamento posterior exige CI/review do novo SHA.

## Artefatos e estado

Persistir código de guard/QA e sob `docs/missions/atlas-parity-04/f4-c4-ci/`: `RESULT.md`, `INPUT-SHAS.json`, `SUCCESSION-CONTRACT.md`, `REPAIR-OWNERSHIP.json`, `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`. SHA/tree/parent e links Git, sem depender de ZIP baixado pelo usuário.

**`F4_G5_INTEGRATION_CI_QUALIFIED_HOST_GATE_DEFERRED`** exige CI global e focal no SHA final + review verdadeira, mas não demonstra RF real, G4 LOCAL, G6, paridade total ou prontidão do host. Se a CI exigir relaxar proteção, pedir decisão formal antes; não mascarar com workflow verde. PR F4 e PRs #15–17 permanecem Draft, sem merge em main, release, deploy, migração, alteração R4, promoção, limpeza ou fonte privada pública.

**END-OF-F4-C4-PROMPT — COMPLETE**
