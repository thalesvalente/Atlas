# ATLAS-PARITY-04 — Registro de decisões e plano de recuperação

**Identidade:** AP04-POR-v1.0-draft — 2026-10-30  
**Repositório único:** thalesvalente/Atlas  
**Baseline do produto:** C4 — SHA 72d9b94e613a57c82a5afd309796f44b271e2185; tree 0a622663ca40232d6143659f82cfe9ce43702e90; PR Draft #13.  
**Natureza:** apenas documentação e governança pré-implementação. Nenhum código, protocolo ou dado privado é alterado ou transferido.

## Por que este registro existe

As campanhas ATLAS-PARITY-01, 02 e 03 **já eram campanhas de recuperação de paridade**. A C4 consolidou arquitetura, contratos, interface C0, metadados e CI, mas não recuperou as jornadas mais ricas do Atlas legado: árvore gráfica hierárquica clicável, tabelas RF literais, produtos, documentos, histórico e cobertura. O pacote P04 aberto recentemente continha somente duas execuções e não continha linhas de RF suficientes para demonstrar as tabelas antigas.

A decisão atual NÃO é reiniciar paridade. É corrigir a prioridade: recuperar rapidamente a funcionalidade legada por leitura compatível, sem migração persistida em massa, e preservar integralmente C4, Caderno interoperável e padrões futuros, inclusive HL7/FHIR.

## Documentos para toda missão subsequente

- [Registro histórico e decisões atuais](DECISION-REGISTER.md).
- [ADR-0003 — proposta técnica de compatibilidade externa](../../architecture/ADR-0003-legacy-compatibility-proposed.md).
- [Plano de ação por fases, owners e gates](ACTION-PLAN.md).
- [Matriz verificável de paridade](PARITY-MATRIX.csv).
- [Padrões e interoperabilidade](INTEROPERABILITY-GUARDRAILS.md).
- [Modelo obrigatório de confronto de resultados](RESULT-REVIEW-TEMPLATE.md).
- [Fontes, precedência e lacunas](EVIDENCE-REGISTER.md).
- [Baseline e gates legíveis por máquina](GATES.json).

## Distinções obrigatórias

- DIREÇÃO APROVADA: princípio funcional e limites explicitamente definidos pelo operador.
- ACEITE DELIMITADO: ADR-0002 aceita como direção de estabilização, sem release nem promoção.
- PROPOSTA TÉCNICA: desenho específico da compatibilidade, ainda sujeito a ARC-09.
- OBSERVADO: prova em SHA/ambiente; não transfere sucesso para outro SHA.
- NÃO EXECUTADO: diferente de PASS e FAIL.
- BLOQUEADO: indicar causa exata e menor ação; não mudar o objetivo para encerrar.

## Como evitar deriva

Cada novo handoff deve citar esta baseline documental por commit e os IDs PAR-xxx afetados. Comparar ANTES e DEPOIS, mostrar testes e capturas, registrar regressões, desconhecidos e decisões pendentes. Não fechar paridade funcional completa enquanto jornadas do legado permanecerem sem prova de recuperação.

Sem novas worktrees/clones, mudança no R4, limpeza, migração em massa, publicação de fontes privadas, merge, release, deploy ou promoção. Publicar este registro em Draft não aprova a implementação da ADR-0003.
