# AB-CONTRACT-1.0

Contrato inicial da missão ATLAS021, 2026-10-24. Texto vinculante da direção e coordenação; não é autorização de promoção.


Este contrato aparece integralmente nos dois prompts. A é responsável pelo produto, protocolo e adaptadores; B é responsável pela preservação e aposentadoria física. As frentes podem executar em paralelo, mas não escrever no mesmo arquivo, mover a mesma fonte ou atribuir aprovação uma à outra.

### Decisão arquitetural vinculante — ADR-0001

O operador determinou a arquitetura abaixo. Registre-a em `docs/architecture/ADR-0001-atlas-protocol-producers-storage.md`, na constituição e nos requisitos. O estado deve distinguir **direção aprovada nesta instrução** de **implementação ainda não verificada**. Não fabrique assinatura, data de aprovação ou aprovação humana dos detalhes ainda não escolhidos.

```text
R4 e outros produtores independentes
                 |
                 | publicam registros no contrato versionado
                 v
Protocolo do Caderno Científico
  semântica + intercâmbio + persistência/endereçamento + conformidade
                 |
                 v
Armazenamento e acesso por implementações substituíveis
  arquivos/pacotes locais inicialmente; outros backends apenas se justificados
                 |
                 | leitura pelo contrato público
                 v
Atlas — interface genérica de consulta, comparação e visualização
```

**ARC-01 — Atlas é produto de interface.** Explora projetos, experimentos, execuções, métricas, evidências, linhagem e dossiês. Pode importar para índices derivados, manter preferências e exportar visualizações. Não é o executor de experimentos, o gerador RF/RNF/RES, o sistema de aprovação científica nem o mecanismo de limpeza de discos.

**ARC-02 — O Caderno Científico é contrato interoperável, não a interface.** Define dados, relações, identificadores, versões, estados e regras de persistência/intercâmbio. Especificação, schemas, validação e SDKs não podem depender do Atlas ou do R4. Distinguir este protocolo futuro do Caderno legado do R4 e de seus dados privados.

**ARC-03 — Armazenamento é uma responsabilidade separada.** Um backend de referência pode ser local e simples. Atlas não pode ser a única autoridade nem o único meio de recuperar o acervo. Índices e caches da interface devem ser descartáveis e reconstruíveis a partir das fontes autorizadas. Não exigir serviço SaaS, banco específico ou conta de provedor para o núcleo mínimo.

**ARC-04 — Produtores publicam; Atlas interpreta.** R4 implementa um adaptador para o contrato público, como qualquer outro produtor. RF/RNF/RES são conteúdos/extensões de domínio, não tipos obrigatórios do núcleo universal. Atlas não importa `r4.*`, não descobre worktrees privadas e não contém condicionais por nome de projeto para funcionar.

**ARC-05 — Independência demonstrada, não apenas separação de pastas.** O pacote do Atlas instala e executa sem R4 instalado, sem diretórios históricos e sem configuração herdada. Dois produtores realmente distintos devem ser consumidos pela mesma interface. Protocolo e validação funcionam sem instalar a interface.

**ARC-06 — Integridade não é autenticidade nem aceite científico.** Preservar a distinção entre validade sintática, conformidade semântica, digest, origem declarada, autenticação independente e decisão científica. Não promover `UNKNOWN`, `HOLD`, resultado sintético ou evidência derivada para ciência aprovada. A interface não reescreve silenciosamente os registros originais.

**ARC-07 — A interface não recebe poderes de migração ou retirada.** Ferramentas de manutenção, compatibilidade legada e operações do host ficam fora do runtime do Atlas. Não mover o leitor Windows suspenso para o novo repositório nem reconstruí-lo como atalho. Políticas reais da plataforma permanecem superiores a este contrato.

**ARC-08 — Canonização e conservação são decisões distintas.** `thalesvalente/Atlas` é o repositório destinado ao novo produto. O CA-01 existente no R4 permanece referência operacional provisória até paridade comprovada e promoção humana. Publicar a nova aplicação não autoriza apagar os históricos, a implementação antiga ou o Caderno legado. Arquivos científicos preservados não são “instâncias redundantes do produto”.

**ARC-09 — Sem mudança arquitetural unilateral.** Um agente não pode trocar esta arquitetura por “Atlas contém Caderno/R4 inteiro”, protocolo dependente da UI, armazenamento inseparável ou lógica RF no núcleo para acelerar a entrega. Qualquer desvio exige ADR sucessor com requisito motivador, evidências, alternativas, impacto, riscos, custo de migração/rollback e testes; parecer independente; **aprovação humana explícita vinculada à versão da proposta antes de implementar o desvio**. Silêncio, CI verde, comentário de bot e autorização de outra operação não são aprovação. Decisões técnicas compatíveis com ARC-01–08 continuam delegadas e documentadas.

### Coordenação, checkpoints e transferência de autoridade

- A registra a versão canônica deste contrato em `docs/coordination/AB-CONTRACT.md` no Atlas, preservando ARC-01–09. Antes dessa publicação, os dois prompts são o contrato inicial; B não precisa ficar ociosa.
- A cria ou identifica uma issue de coordenação no R4 **privado**, sem novos dados sensíveis, e fornece o link real a B. Cada frente publica seu próprio comentário append-only; não sobrescreve o status da outra. Não inventar número de issue ou PR.
- A escreve código/ADR/protocolo/CI do Atlas e, se necessário, somente o adaptador em uma branch própria e isolada do R4. B escreve seus planos, ferramentas de manutenção autorizadas e recibos em outra branch/namespace. Mudanças em arquivos compartilhados exigem handoff de ownership antes da edição.
- Cada handoff registra: `contract_version`, frente/emissor, data, commit/árvore, versão e digest do perfil, evidências, hipóteses, pendências, consumidores, escopo da declaração e validade perante drift. O registro privado pode conter mapas de fontes; o público, não.
- A fornece `A-DATA-REQUIREMENTS`, matriz de mapeamento legado→protocolo, testes de compatibilidade, limitações e `A-MIGRATION-DISPOSITION` por ID lógico: `NEEDED`, `NO_LONGER_NEEDED_BY_A`, `NOT_REQUIRED_BY_A` ou `UNKNOWN`. A declaração vale somente para o produto A; não encerra consumidores externos nem autoriza exclusão.
- B fornece `B-INVENTORY`, disposição/recuperação por ID lógico, versão do protocolo efetivamente usada, dependências reais e `B-RETIREMENT-READINESS`. Não exportar dados privados para GitHub ou para a sessão A sem aprovação de compartilhamento.
- O digest de um arquivo não deve ser usado como identidade pública de dados privados sem autorização. Recibos públicos usam IDs opacos, contagens e SHAs de código publicável. Caminhos absolutos, nomes de usuários do host, tokens e payloads ficam privados.
- A não espera a limpeza para desenvolver. B não espera o produto inteiro para classificar ou preservar por procedimentos permitidos. B não elimina fonte ainda necessária a A; tampouco confunde “A não precisa” com aprovação de retirada.
- Não executar merge, release, promoção canônica, cópia/restauração de dados privados, sincronização da principal ou exclusão com base apenas neste contrato. Cada operação mantém o gate humano específico definido na missão correspondente.

