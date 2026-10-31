# AP04-F4-C0-READER003-CONTRACT-CHAT-01 — adendo versionado e revisão antes da integração

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions. **Esforço:** Extra High, selecionado manualmente pelo operador; nível efetivo não observado = UNVERIFIED.  
**Destino:** `thalesvalente/Atlas`; branch exclusiva convencional `docs/atlas-parity04-f4-reader003-20261031` (criada pelo coordenador); **sem worktrees/clones**.  
**Baseline:** PR #15 F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, árvore `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.  
**Meta:** `F4_C0_READER003_SCOPED_CONTRACT_REVIEWED`, restrita à documentação e sua revisão, não G4/G5.

## Baselines e aprovação já obtida

Verifique AP04-POR-v1.0-draft, F4/G4/G5, D-001–D-020, ARC-01–09, ADR-0001/0002, a ADR-0003 v0.2 e descriptor0.2.0 no pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527`; a aprovação humana **APPROVED_SCOPED** da PR #15 comentário `6539419419`. Consulte F1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, F2 `PARITY-TRACEABILITY.md` e o contrato atual `specs/003-producer-selective-preview/contracts/reader.md`.

A aprovação cobre leitura externa, descriptor efêmero e apresentação opcional segregada por File API. **Não** cobre importação no Catalog/SDK, endpoint HTTP adicional, reconstrução do leitor Windows, File API automática ou alteração do protocolo Caderno. O `reader.md` histórico continua Caderno-exclusivo. A F4 exige **versionar e revisar a exceção antes de integrar**. Se houver necessidade de ampliar o alcance/alterar o plano, documentar alternativas, riscos, diff e solicitar aprovação humana aplicável ANTES da implementação.

## Ownership sem sobreposição

Pode criar apenas:
- `specs/003-producer-selective-preview/contracts/reader.ap04-legacy-presentation-v0.2.md` — sucessor/adendo contratual específico;
- `docs/missions/atlas-parity-04/f4-c0-reader003/` — matriz de impacto, invariantes, contraprovas documentais, recibos e manifesto.

Não editar o `reader.md` histórico, constituição, ADRs antigas, F1/F2, GATES, protocolo/SDK, shell, servidor, Catalog, workflows/gates congelados ou branches F3A/F3B/C2. Revisão independente por subagente nativo C sem autoria; subagentes A (contrato) e B (segurança/verificação) apenas quando realmente disponíveis, coordenador único writer. Sem agentes: análise sequencial e estado de revisão pendente, não simular QA.

## Conteúdo obrigatório do adendo

- **Duas vias explicitamente separadas.** Caderno0.1.0a1→SDK→Catalog→API C4 permanece a via científica existente e **continua exclusiva no seu endpoint/reader**. Via nova: processo **externo LOCAL O1** lê somente projeção preexistente autorizada → descriptor JSON `atlas-legacy-presentation`0.2.0, LEGACY_DERIVED → importação **explícita** pela File API em painel segregado O3, **RAM-only** e sujeito a TTL.
- Definir precedência restrita à nova superfície opcional e como o leitor Caderno-exclusivo e a exceção ARC-09 convivem, sem tornar a segunda uma fonte de dados científicos. Não criar novo schema ou perfil obrigatório no Caderno, nem alterar versionamento RO-Crate/Process Run.
- Garantias de fonte/snapshot/sessão/ocorrência, tokens stale, null/unresolved/colisões, 28 RF não admitidas e Run externo sem caminho contínuo. Validação formal de shape e invariantes semânticas extras; integridade de bytes não implica autenticidade/ciência.
- Controle de segurança: sem upload ao servidor, novo endpoint, rede externa, execução de HTML/URI de fonte, storage persistente, leitura de caminhos por JS, descoberta de drives ou reconciliação automática entre vias. Assets JS/CSS futuros devem ser fixos, CSP/Origin inalterados. TTL ≤60 min, rejeição de documento não conforme/quotas e rollback sem tocar o Caderno.
- Preservar RO-Crate 1.3, Process Run 0.6 e Caderno 0.1.0a1; HL7/FHIR continua somente capacidade opcional por domínio sem perfil/versão/implementação.
- Listar invariantes e negativos que a F4-C3/F4-C4 deverão provar, sem atribuir sua execução a C0. Campo sem evidência = UNKNOWN, não aprovar automaticamente.

## Entrega e gate

Entregar adendo + `RESULT.md`, `INPUT-SHAS.json`, `CONTRACT-DELTA.md`, `SECURITY-AND-ROLLBACK.md`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`; cada arquivo com ownership, blob e SHA/tree/parent. Revisão independente real sobre a versão completa. Se o guard antigo rejeitar os novos documentos, registrar recusa como **sucessão CI a qualificar na C4**, não relaxar auditorias, reescrever manifestos históricos ou pins.

**Sucesso escopado:** `F4_C0_READER003_SCOPED_CONTRACT_REVIEWED` somente após adendo versionado, conflitos de precedência resolvidos e parecer real; sem implementação. Se o contrato histórico exigir edição para produzir precedência válida, publicar `F4_C0_ARCHITECTURAL_DECISION_REQUIRED` e solicitar autorização, não alterar bytes congelados por conveniência.

Não criar worktrees, clones, merge em main, release, deploy, promoção, migração, fonte privada ou R4.

**END-OF-F4-C0-PROMPT — COMPLETE**
