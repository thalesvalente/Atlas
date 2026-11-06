# Feature 005 — Navegação, triagem e proposta de retenção

**Branch:** `feat/atlas-experiment-triage-20261105`  
**Criada:** 2026-11-05 · **Status:** implementação em curso, aceite próprio pendente.  
**Entrada:** ATLAS-NAV-RETENTION-01, pedido explícito do operador. A01 aceita somente em `8e0e400d5220efceb6dd881772e5b07825442970` / tree `5e63684b266bebb983a02cf68c4f17d365d854a2`.

## User Scenarios & Testing

### US1 — Encontrar e compreender (P1)
O operador encontra ocorrências pela navegação lateral e busca tipada, identifica a natureza do resultado e consulta referências comprovadas.

**Aceite independente:** T01 busca `M1.1` encontra a tabela inventada com 39 linhas RF; não cria execução, sucesso, baseline ou equivalência com M1/M11. T02 execução SUCCEEDED/FAILED/blocked corresponde ao indicador, mesmo com publicação e resultado documental conflitantes. T03 localizar registro na árvore revela a família e o cartão sem alterar o lote; uma tabela só oferece ligação a registro se houver referência única declarada.

### US2 — Formar e comparar um lote (P1)
O operador marca cartões/registros, mantém foco e detalhes independentes e inspeciona o conjunto em vista própria.

**Aceite independente:** T04 seleção preservada entre vistas, filtros, agrupadores e páginas; visíveis e filtrados são ações diferentes com contagem explícita. T05 comparação apresenta tipos, estados, revisão e referências originais. Nova fonte/revisão invalida lote, anotações e intenções com aviso. Ao menos 1.200 registros sintéticos continuam consultáveis, sem corte silencioso.

### US3 — Propor conservação com segurança (P1)
O operador prepara dossiê e plano legível/exportável com suas intenções e lacunas.

**Aceite independente:** T06 exporta JSON versionado PROPOSAL_ONLY, com seleção explícita, fonte/revisão, valores exatos e DELETE_AUTHORIZED=NO. T07 baseline confirmada permanece protegida mesmo com REVIEW_FOR_REMOVAL. T08 ausência de backup, dependências ou retenção gera lacuna/proteção; falha experimental não libera descarte. T09 Atlas funciona instalado sem R4. T10 seleção/planejamento não fazem requisições externas nem mutações no pacote fonte.

### Edge Cases

M1, M11 e M1.1; famílias tipadas e colisões; títulos iguais; referência ausente/ambígua; campo ausente, NULL, vazio e UNKNOWN; inteiros maiores que 2^53 e decimais lexicais; conteúdo HTML/URL hostil; baseline apenas no título; seleção fora da página ou oculta; snapshot alterado; fonte vazia/inválida; menu/filtro/lote em 320 px.

## Requirements

- **FR-001 / G2:** lateral recolhível, hierarquia de até dois níveis, expandida por padrão em desktop amplo e compacta nas larguras intermediárias; mobile com Menu, fechar/Escape e retorno de foco. Espaço liberado pertence à área principal; estado dura a sessão.
- **FR-002 / G3:** busca de título, ID original, UID, família, missão/run/experimento e demais campos disponíveis; resultados tipados com motivo, contagem e paginação integral. Identidade e referência não derivam de similaridade textual. Diferenciar não encontrado, tipo divergente, campo ausente e vínculo não comprovado.
- **FR-003 / G4:** filtros combináveis e removíveis individualmente para execução, resultado documental, publicação, admissão, revisão, família, tipo, baseline, período declarado e evidência. Estado de execução usa a precedência já exibida na A01; filtros documentais permanecem separados. Não confundir ausência/NULL/vazio/desconhecido.
- **FR-004 / G5:** vista de baselines baseada em designação explícita da fonte ou anotação de sessão do operador, com origem/revisão identificadas. Uma referência a baseline não torna o registro referenciador uma baseline. DTO original permanece intacto.
- **FR-005 / G6:** seleção identificada por fonte, revisão/digest, UID e tipo; sem cascata por agrupador editorial. Informar total, visíveis, ocultos pelo filtro, tipos e revisão. Troca de snapshot invalida seleção anterior.
- **FR-006 / G7:** lote com comparar, detalhes, copiar referências, vínculos, dossiê, plano e limpar; todas ações identificam quantidade e são acessíveis no mobile.
- **FR-007 / G8:** plano contém identidade, proveniência, título/família, estados e, quando declarados, configurações, revisões de código, resultados/métricas, limitações, dependências e artefatos. Lacunas explícitas, intenção por item, campos de verificação pendentes, versão e PROPOSAL_ONLY. Intenções: KEEP_FULL, KEEP_ESSENTIALS, REVIEW_FOR_REMOVAL, UNDECIDED.
- **FR-008 / G9:** proteção fail-closed para baselines, unicidade, fontes, configurações, backups não verificados, dependências compartilhadas e retenção desconhecida. Tamanho desconhecido: “A medir no ambiente LOCAL”. Não há comandos, exclusão, caminhos arbitrários, abertura automática nem efeitos sobre o corpus.
- **FR-009 / G11:** navegação/seleção/exportação por teclado e toque, foco visível, sem oclusão de controles/minimapa; HTML semântico e rótulos. Verificar 1440×1200, 1024×900, 800×1000, 390×844 e 320×740.
- **FR-010 / G13:** preservar protocolo, descriptor 0.2.0, DTO validado, JSON/CSV e lexemas, CSP, P03, leitor/launcher, independência do produtor e fontes privadas. Sem instalação de scheduler/banco/daemon.
- **FR-011 / G14–15:** testes RED/GREEN reais, regressões, Actions Windows/Ubuntu normal/-O no SHA publicado, Codex Review terminal, revisão de agente não autor e handoff na própria PR Draft empilhada na #32. Sem merge/release/deploy; aceite da nova feature separado.

### Key Entities

Ocorrência é um DTO de consulta. Registro é a classe de ocorrência, cujo tipo declarado pode ser experimento, execução, tentativa, missão, marco, baseline, produto ou outro; não são sinônimos. Tabela, linha, recurso/documento/artefato, nó e relação conservam seus tipos. Foco, detalhe e inclusão no lote são estados distintos. Anotação é do operador, vinculada à identidade/revisão. Plano é proposta inerte, nunca autorização.

## Success Criteria

- **SC-001:** T01–T10 passam com fixtures públicas inventadas; zero classificação científica inventada nos casos adversariais.
- **SC-002:** todos os registros filtrados permanecem alcançáveis; selecionar visíveis não incorpora itens de outras páginas/ramos recolhidos.
- **SC-003:** seleção/filtragem de 1.200+ registros responde em até 2 s no ambiente de teste informado, sem perda de identidade; medir, não presumir.
- **SC-004:** cinco viewports sem overflow horizontal do shell; tabelas/grafos podem rolar na própria região. Teclado/Escape/Enter/Espaço e toque conferidos.
- **SC-005:** hashes das fontes antes/depois iguais, nenhuma requisição externa e todo plano mantém DELETE_AUTHORIZED=NO.
- **SC-006:** A01 permanece qualificada por regressões no sucessor; CI/review novos não herdam PASS do SHA aceito.

## Assumptions / Clarifications

Somente snapshots já validados, somente dados sintéticos públicos nesta missão. Designações booleanas `baseline`/`is_baseline` e tipo `baseline` são lidas literalmente quando presentes, sem inventar campos no protocolo; referências são resolvidas pelo índice existente. Anotações vivem apenas na sessão e na exportação explícita. Retenção física, inventário e espaço real dependem de LOCAL futuro autorizado. Não há dúvida contratual que bloqueie a implementação compatível.
