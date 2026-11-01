# ATLAS AP04-F4 — execução direta do código real R4, sem perfil sintético de origem

**Status desta publicação:** `NEXT_EXECUTION_PROMPTS_PUBLISHED_NOT_RUN`.  
**Data de referência:** 2026-11-01. **Plano original preservado:** `AP04-POR-v1.0-draft`; decomposição operacional C2-A/B/K/D, L0/L1, C3/C4.  
**Forma aprovada de produto:** externo O1 → descriptor efêmero 0.2.0 (ou sucessor APROVADO) → File API explícita O3 no viewer segregado; Caderno/SDK/Catalog permanecem independentes.  
**Fonte histórica real:** R4 `r4-experiment-viewer-v5` já exportado, NÃO `atlas-legacy-synthetic-source/0.1.0`. Dados inventados continuam SOMENTE como valores de teste no formato real.

## Baselines imutáveis e privilégios

- F2 qualificada PR #15: `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.
- F4 C0 contrato 003 PR #19: `d498504cd2c4d230088f86e04e55624bbe32df79`, tree `4f0c6360d429507af1946a094c27b790c9894477`.
- F4 C1 gráfico escalável PR #16: `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, tree `1ba41dd01b118a008ca33061131e9181a2600548`.
- F3B tabelas PR #17: `72118073cc72b4d3cdca21fcc64c18cf742ae384`, tree `ac3dec6de49bf55dc25115bfb35dd364b1a2f690`.
- C2 real-v5 parcial PR #18: `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, tree `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df`, CI focal 4/4 e 51 métodos nas células Windows, 50 PASS + 1 SKIP ACL-Windows nas células Ubuntu. **Ainda BLOQUEADO operacionalmente**, sem review independente terminal nova.
- C2 histórica: `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`; 22 hashes de manifesto histórico não podem ser reescritos.
- F1 G1 sanitizada: `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`.
- Código-fonte antigo R4 **PRIVADO** de referência: `thalesvalente/R4-RNF-RES-FIX` SHA `5c145615c8a1bd601351badddccaf3acea474ed2`. O usuário aprovou nesta conversa transferência dos TRECHOS NECESSÁRIOS DE CÓDIGO ao Atlas público, não dos experimentos/credenciais/fonte bruta.
- ADR-0003 v0.2 `APPROVED_SCOPED`, pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527`, decisão humana PR #15 comentário `6539419419`. Isso NÃO aprova automaticamente descriptor 0.2.1, dados reais, G4/G5/G6, migração ou merge main.

## Execução recomendada — etapas e ambientes

| Ordem | Missão | Ambiente | Raciocínio recomendado | Branch / ownership | Início |
|---|---|---|---|---|---|
| A | [01 C2-A: mapear R4 v5 e relações](01-C2-A-REAL-V5-MAPPING-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | **PR #18 existente**, só parser/v5/QA e docs A | **AGORA** |
| B | [02 C2-B: Job Object/sandbox OS](02-C2-B-WINDOWS-OS-SANDBOX-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | **Branch B nova** `feat/atlas-parity04-f4-c2-os-isolation-20261101`, apenas módulos OS e tests próprios | **AGORA**, paralelo A |
| K | [03 C2-K: source_key↔native_id e proposta contratual](03-C2-K-KEY-IDENTITY-CONTRACT-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | **Branch documental nova** `docs/atlas-parity04-f4-key-identity-20261101` | **AGORA**, paralelo A/B; documento não é aprovação |
| L0 | [04 L0: conferir estrutura do HTML realmente existente](04-L0-LOCAL-REAL-SOURCE-WITNESS.md) | **LOCAL Windows** | **High** (Extra High quando necessário) | Somente recibos/fonte previamente identificados, saída privada; sem branch de produto | **AGORA só se autorização exata F4-L0 existir** |
| D | [05 C2-D: compor parser e proteções](05-C2-D-COMPOSE-REVIEW-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | Retorna à **PR #18**, único writer, após A/B congelados | **DEPOIS de A+B**, e K aprovada se mudança necessária |
| L1 | [06 L1: executar com arquivos reais e sandbox](06-L1-LOCAL-REAL-READER-PROOF.md) | **LOCAL Windows** | **Extra High** | Recibos privados/sanitizados, fonte read-only; sem checkout extra | **DEPOIS de D pronta + L0 + autorização exata** |
| C3 | [07 C3: integrar árvore/tabelas ao viewer](07-C3-INTEGRATE-REAL-ATLAS-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | Branch C3 `integrate/atlas-parity04-f4-composition-20261031`, shell/UI | **DEPOIS de C2-D, C0, C1, F3B**; L1 pode rodar paralelo |
| C4 | [08 C4: CI global de sucessão](08-C4-GLOBAL-CI-CHAT.md) | **CHAT** GitHub/Actions | **Extra High** | **Mesma branch C3**, mas só após C3 congelada/sem outro writer, guards/CI | **DEPOIS de C3** |

**Nível de raciocínio é recomendado; o operador precisa selecionar manualmente o esforço na interface.** No LOCAL, usar Codex com acesso ao Windows (não CHAT sem host). Todos os CHATs exigem GitHub e GitHub Actions conectados. Até três subagentes nativos reais por missão quando efetivamente disponíveis; não simular. Não presumir que a sessão tem esse recurso nem alegar revisão independente sem revisor distinto.

## DAG e fronteiras

```text
          ┌── C2-A (CHAT) ──────────────┐
          ├── C2-B (CHAT OS) ──────────┤
AGORA ────┤                             ├── C2-D (CHAT, PR18) ──┬── L1 (LOCAL, fonte autorizada)
          ├── C2-K (CHAT, decisão)* ───┤                        │
          └── L0 (LOCAL, se autorizado) ┘                        └── C3 (CHAT, após C0+C1+F3B)
                                                                                 │
                                                                             C4 (CHAT)
                                                                                 │
                                                       G4 LOCAL + G5 CI + nova autorização → F5
```

`*` Se K provar que não é preciso mudar descriptor, basta o parecer; se exigir mudança 0.2.1, deve haver aprovação humana ARC-09 **antes do código** e antes de C3. L0 não exige C2-D pronto e não executa o leitor bloqueado: serve apenas como testemunho de formato. Se nenhuma nova leitura local for autorizada, A/B/K podem progredir com código real R4 e valores inventados; D/C3 não alegam prova de corpus.

## Ownership paralelo e salvaguardas

- A edita `parser.py`, `legacy_v5.py`, `legacy_v5_descriptor.py`, testes/QA v5 e workflow focal já existente da PR18.
- B cria arquivos novos prefixados `os_`, testes/harness OS próprios e workflow isolado em branch separada; não edita os arquivos de A. D revisa B por SHA e introduz blobs específicos na PR18 por commit de um pai, registrando B como fonte **não ancestral Git**, sem falsificar proveniência.
- K só escreve docs de proposta de descriptor; não altera contrato/ADR/schema 0.2.0. O operador deve aprovar eventual adendo antes da implementação.
- L0/L1 usam apenas paths exatos do recibo F1 com autorização F4 explícita; não publicam RF real nem descriptor, caminhos/hashes/IDs privados.
- D edita ponto de entrada/worker e QA de composição depois de A/B; C3 edita shell e integração só depois de D; C4 edita guards/CI somente depois de C3. Nenhum writer concorrente na mesma branch.
- Original C2, Caderno 0.1.0a1, RO-Crate 1.3, Process Run 0.6, ADRs/manifestos históricos e AP04-POR permanecem; HL7/FHIR capacidade FUTURA, sem conformidade implícita.
- Nenhuma desativação de CI, `paths-ignore`, `continue-on-error`, mudança de pins, exceção ampla `docs`/`scripts`/`tests`, ou falso PASS no SHA final. Gates G4 (leitura LOCAL + isolamento OS), G5 (viewer integrado + CI C4), G6 (demonstração LOCAL com RF real na F5) **não** são intercambiáveis.
- Nada de merge main, release, deploy, promoção, migração, limpeza, alteração R4, provider, varredura de drives, clone/worktree persistente ou transferência de acervo. Ações que exigirem revisão ARC-09 ficam bloqueadas até decisão versionada.

## Resultados e handoff

Os oito arquivos Markdown são **prompts de execução**, não relatórios de código executado. Os resultados e patches devem ficar nas próprias branches de ownership por SHA, em Git, com revisão independente real. `DEPENDENCIES.json` nesta pasta fixa o DAG e os estados. A F5 não começa com estes prompts e exigirá autorização separada após provas efetivas G4/G5.

**END-OF-AP04-F4-NEXT-WAVE-README — COMPLETE**
