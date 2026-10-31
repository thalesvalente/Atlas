# F3A / F3B — Contrato de paralelismo AP04

**Baseline fixa para as duas branches:** `54bb16d350f7bc34fafb95438bd64a2397d58bf3` (PR #15, qualificação documental). **Plano:** AP04-POR-v1.0-draft. **ADR-0003:** aprovada apenas como exceção arquitetural delimitada, não como autorização F4.

| Dimensão | F3A | F3B |
|---|---|---|
| Branch | `feat/atlas-parity04-f3a-graph-20261031` | `feat/atlas-parity04-f3b-tables-20261031` |
| Dono de código | `parity04_f3a_graph.js/.css` | `parity04_f3b_tables.js/.css` |
| Testes/harness | prefixo `f3a` | prefixo `f3b` |
| Documentos | `docs/missions/atlas-parity-04/f3a-graph/` | `docs/missions/atlas-parity-04/f3b-tables/` |
| Capability | PAR-001, parte de PAR-004/007 | PAR-002/003, parte de PAR-004 |
| Dados | Synthetic descriptor 0.2.0 | Synthetic descriptor 0.2.0 |
| Produto principal | Somente leitura; integração F4 | Somente leitura; integração F4 |

**Não modificar em paralelo:** `static/index.html`, `static/app.js`, shell CSS global, `Catalog`, `server.py`, reader003, SDK, protocolos, schemas, ADWs/ADRs, matrizes/gates da AP04 e scripts/workflows já congelados. Os artefatos F2 permanecem imutáveis. Só F4 terá ownership da integração, depois da qualificação de ambos e da mudança versionada/revisada do contrato 003 quando aplicável.

**Política Git:** duas branches distintas, cada uma baseada no mesmo F2 HEAD; sem worktrees/clones. Um único escritor por branch; colaboração de agentes apenas com ownership de paths distintos e revisor final não autor. Não criar uma terceira branch integradora agora. CI focal por SHA; resultado de CI global que rejeita deltas fora de guard congelado não vira motivo para relaxar auditorias. Corrigir ou solicitar qualificação sucessora com deltas exatos em etapa/ownership próprio.

**Fronteira de resultados:** F3A e F3B podem qualificar componentes sintéticos; não declaram recuperação real de RF/árvore, integração à interface, `G4/G5/G6 PASS`, ou paridade do acervo. A F4 comporá e F5 provará com fonte LOCAL autorizada. Migração histórica e alterações R4 continuam fora de escopo.
