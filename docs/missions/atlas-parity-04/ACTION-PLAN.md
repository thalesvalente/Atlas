# Plano de ação — ATLAS-PARITY-04 (recuperação funcional sem migração)

**Baseline congelada:** C4 SHA 72d9b94e613a57c82a5afd309796f44b271e2185, PR Draft #13.  
**Objetivo:** Atlas novo MELHOR que o legado, sem perder a experiência e sem descartar os avanços de independência e interoperabilidade.  
**Não é uma campanha nova de migração:** usa leituras históricas autorizadas, contrato derivado de apresentação e UI própria.

## Diagnóstico

C4 possui filtros, comparação, timeline, referências, linhagem e metadados tipados, com testes de engenharia. Faltam a árvore SVG hierárquica clicável e as tabelas de requisitos reais. O pacote P04 que o usuário abriu é somente uma coorte pequena com duas execuções, sem métricas RF, e não representa todo o acervo. Portanto o problema tem dois lados inseparáveis: **dados históricos acessíveis** e **visualizações/ações úteis**.

## Frentes e dependências

| Fase | Natureza e owner | Entrega concreta | Dependência | Gate |
|---|---|---|---|---|
| F0 | Documentação, CHAT/GitHub | Este registro/ADR proposta/plano/matriz | C4 fixada | G0 |
| F1 | LOCAL, leitura externa e privacidade | Identificar projeção legada existente com árvore e pelo menos uma tabela RF literal; identidade/contagens/limites, sem mover dados | Permissões reais de fonte | G1 |
| F2 | CHAT, arquitetura | Definir contrato efêmero e revisar ARC-04/05/07/09; ADR versão final e eventual aceite humano antes de desvio | F0/F1 parcial | G4 |
| F3A | CHAT, branch UI gráfica exclusiva | Árvore visual genérica com nós clicáveis, expansão, zoom/pan/minimapa, teclado e legendas de relações | C4 + fixtures sintéticas | G2 |
| F3B | CHAT, branch UI tabular exclusiva | Requisitos RF/RNF/RES como visão opcional tipada, tabela original filtrável/exportável, sem domínio imposto ao core | C4 + fixtures sintéticas | G3 sintético |
| F4 | LOCAL para adaptador privado; CHAT integrador exclusivo da UI | Projeção efêmera externa lida pelo Atlas sem import R4; RF real e árvore em mesmo produto | F1, F2 aprovada conforme necessário, F3A/B | G4/G5 |
| F5 | QA independente + demonstração LOCAL privada | Confronto lado a lado; árvore e RF realmente navegáveis no Windows, sem alterar fontes, com regressão C4 por SHA | F4 | G5/G6/G7 |
| F6 | Futuro, repositório/produtor próprio | R4 passa gradualmente a publicar padrões diretamente, com teste de equivalência e retenção independente | Após utilidade/paridade | Fora de escopo agora |

F1 pode ocorrer em paralelo com F3A/F3B, porque os componentes de UI usam fixtures públicas. F2 é documental; uma entrada alternativa no runtime somente pode ser implementada depois da decisão arquitetural aplicável. Um integrador único escreve no shell compartilhado. Sem duas sessões simultâneas modificando a mesma worktree; usar branches Git sobre o repo existente, sem criar worktrees/clones novos.

## Critérios mínimos da primeira entrega útil

- [ ] **Árvore**: estrutura de projeto/família/experimento/execução em SVG real, expansão/recolhimento, seleção contextual, zoom/pan e minimapa; suporte teclado/foco e diferentes larguras.
- [ ] **Requisitos**: pelo menos uma tabela RF literal de fonte legada autorizada, com ID original, núcleo quando declarado, nome, descrição e critério de aceite; filtros/ordenação/detalhe/exportação.
- [ ] **Conexão**: clicar nó→execução→tabela→linha→evidência preserva fonte/snapshot/ID; relação de pertencimento não finge derivação.
- [ ] **Compatibilidade**: Caderno funciona sozinho, Atlas C4 sem R4, adaptador externo read-only, sem alterações de schema/versão do protocolo.
- [ ] **Fidelidade**: origem, ausências, estados, ligações, formatos, hash, perdas e contagens visíveis e não inventadas.
- [ ] **Segurança**: nenhum payload/HTML arbitrário executado, nenhuma fonte privada enviada ao GitHub, zero alteração dos bytes originais.
- [ ] **Provas**: CI Windows/Ubuntu normal/-O, browser real no SHA sucessor, prova LOCAL privada e parecer independente.
- [ ] **Padrões**: RO-Crate/Process Run preservados; HL7/FHIR não perde ponto de extensão nem recebe rótulo falso de conformidade.

## Próximas funcionalidades após o corte mínimo, sem abandoná-las

- PAR-005 produtos, grupos, versões, execução vinculada.
- PAR-006 documentos, dossiês e referências verificadas.
- PAR-007 grafo de linhagem tipada.
- PAR-008 timeline/histórico com escopo.
- PAR-009 cobertura com denominadores reais ou UNKNOWN.
- PAR-010 inventário consultivo de armazenamento, sem exclusão.

O corte mínimo é **MINIMUM_LEGACY_PARITY_DEMONSTRATED**, não paridade completa. PAR-005 a PAR-010 permanecem abertas até recuperação/verificação ou decisão explícita de substituição. Não apagá-las da matriz.

## Gates e negativas

| Gate | Prova exigida | Não confundir com |
|---|---|---|
| G0 | Documentação versionada e ADR proposta sem autorização implícita | Aceite de nova arquitetura |
| G1 | Projeção legada real autorizada com RF literal e identidade verificada | Total do acervo |
| G2 | Árvore clicável, zoom/pan/minimapa, teclado e fluxo de navegação em navegador | SVG estático |
| G3 | RF real e fiel, incluindo linhas/critério originais | Tabela genérica de propriedades |
| G4 | Leitor externo + derivação efêmera; zero escrita na fonte; decisão ARC-09 quando aplicável | Migração ou padrão conforme |
| G5 | Sem regressão C4; testes no SHA integrado e isolamento R4 | Reuso automático de CI antiga |
| G6 | Browser Windows com amostra privada real + recibos no SHA testado | Screenshot parcial não atribuído |
| G7 | Matriz sem item P0 omitido e pendências P1 explícitas | Paridade integral sem evidência |
| G8 | Eventual merge/release/promoção com autorização humana separada | CI verde |
| G9 | Retenção/limpeza com autorização específica posterior | Qualquer atividade desta fase |

## Riscos de desvio e contraprovas

1. UI sem dados reais → G1/G3 exigem literal RF.
2. Dados sem UI navegável → G2 exige árvore clicável e navegação contextual.
3. Cópia de código privado → auditoria de origem dos arquivos públicos e proibição de import R4.
4. Migração disfarçada → hash antes/depois e escopo de escrita somente em cache derivado.
5. Nova autoridade científica → rotular LEGACY_DERIVED e preservar fonte.
6. Padrões esquecidos → matriz de padrões e não regressão Caderno/HL7 como capacidade futura.
7. Ciclos de QA sem funcionalidade → cada handoff comprova ao menos IDs PAR-xxx com jornada.
8. Suposta limpeza segura → proibição de exclusão até missão distinta de retenção.

## Decisão de fim de fase

Possíveis estados: MINIMUM_LEGACY_PARITY_DEMONSTRATED; PARTIAL_PARITY_WITH_GAPS; CONTRACT_DECISION_PENDING; BLOCKED_EXACT. **Nenhum é automaticamente PARITY_COMPLETE, RELEASE ou CLEANUP_AUTHORIZED.** Não mudar os nomes dos itens para torná-los artificialmente concluídos.
