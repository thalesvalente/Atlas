# ADR-0003 — Proposta de compatibilidade legada por leitura externa

**Versão:** 0.1-proposta — 2026-10-30  
**Estado:** OBJETIVO FUNCIONAL DEFINIDO PELO OPERADOR; DESENHO ARQUITETURAL NÃO RATIFICADO.  
**Motivação:** o usuário deseja recuperar rapidamente árvore clicável e tabelas reais de requisitos do Atlas legado sem converter o acervo histórico agora.

## Contexto verificável

C4 possui exploração C0 e apresentação de propriedades; a amostra privada consultada contém apenas duas execuções, sem tabelas RF literais. O legado possuía árvore gráfica, tabelas de RF, produtos, documentos, histórico e cobertura. Recuperar só CSS ou ampliar fixtures sintéticas não demonstra paridade. Migrar o acervo exigiria trabalho e risco que não são prioridade agora.

## Alternativas examinadas

| Opção | Vantagem | Risco/custo | Disposição |
|---|---|---|---|
| A — converter todo o legado para Caderno antes de usá-lo | Um formato final | Alto custo, reorganização, semântica perdida | REJEITADA NO CURTO PRAZO |
| B — copiar os leitores/artefatos privados para o runtime Atlas | Rapidez aparente | Acoplamento, ARC-04/07, direitos, privacidade | NÃO AUTORIZADA |
| C — leitor externo somente leitura + projeção neutra efêmera e descartável | Usa registros já existentes, sem alterar fonte | Requer contrato de confiança/identidade/limites e integração controlada | PREFERIDA COMO PROPOSTA |
| D — abrir o viewer antigo separado | Contingência quase imediata | Não entrega interface unificada | CONTINGÊNCIA, NÃO PARIDADE |
| E — atualizar primeiro R4 para produzir o Caderno | Solução futura durável | Bloqueia a necessidade urgente | POSTERGADA EM CAMPANHA R4 |

## Desenho candidato para C

- Ferramenta externa ao runtime, com entrada explícita de projeção legada conhecida/autorizada. Nunca descobrir automaticamente worktrees, diretórios privados, arquivos irmãos ou discos.
- Leitura de índices/projeções preexistentes, sem novo parser genérico capaz de executar payloads, sem revalidar fontes massivamente e sem reexecutar experimentos.
- Projeção de APRESENTAÇÃO somente, transitória (memória ou cache ignorado), com ID de fonte+entidade, estrutura declarada, relações tipadas, produtos, linhas RF, ausências, hashes observados, cobertura e perdas.
- Fonte original mantém autoridade. Projeção não altera estado, não autentica ciência, não vira pacote Caderno, não assina resultados e não concede aprovação.
- Atlas consome somente contrato neutro explicitamente validado, nunca importa r4.* ou condiciona a apresentação ao nome do produtor. A C4/Caderno continuam executáveis sem o modo legado.
- HTML/URI/payload privado permanece inerte e não é servido por wildcard. Relatórios públicos usam dados exclusivamente sintéticos/sanitizados e licença conferida.
- Rollback por desativar a compatibilidade e descartar índices derivados; fontes e C4 permanecem intactas.

## Compatibilidade com decisões anteriores

A direção funcional não revoga ARC-01–09. **Alterar a fronteira de entrada de uma UI antes limitada ao Caderno pode ser um desvio arquitetural.** O integrador deve demonstrar que a solução C permanece fora do runtime e é compatível com os contratos vigentes; se houver desvio, exige versão sucessora da ADR e aprovação humana explícita vinculada ao documento antes de implementar esse desvio (ARC-09). A presente publicação Draft não é esse aceite.

## Provas exigidas antes de alegar sucesso

1. Uma fonte legada autorizada com linhas RF literais, identificadores e proveniência.
2. Árvore realmente navegável, com expansão, seleção, zoom/pan, minimapa e teclado; hierarquia visual não promovida a causalidade.
3. Tabela RF real (ID, núcleo quando houver, nome, descrição, critérios de aceite, filtros, detalhe, exportação) fiel à fonte.
4. Código público de UI independente de código privado; SDK Caderno e C4 continuam passando tests/CI.
5. Zero escrita no acervo; limites e perdas declarados; nenhuma cópia privada publicada.
6. Gates de Windows/browser e revisão independente por SHA, separando prova sintética de caso real.

## Operações não autorizadas

Nenhuma migração persistida, reorganização de diretórios, nova worktree, alteração de R4, cópia de leitores suspensos, acesso a fontes não permitidas, limpeza, merge, release, deploy, promoção ou uso clínico/comprovação HL7. Estas ações têm contratos próprios.

**Decisão pendente:** escolher/formalizar tecnicamente C, verificar ARC-07/09 e obter aprovação versionada quando necessária. Trabalho preliminar de inventário em leitura e construção de UI independente em fixture pública não devem ficar bloqueados por estudos não essenciais.
