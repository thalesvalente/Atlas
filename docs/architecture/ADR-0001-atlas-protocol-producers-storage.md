# ADR-0001 — Atlas, protocolo, produtores e armazenamento

Estado: **DIREÇÃO APROVADA NA INSTRUÇÃO ATLAS021**; implementação **EM VERIFICAÇÃO**. Registro: 2026-10-24. Não há assinatura humana fabricada nem aceite de detalhes do protocolo.


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


## Consequências e verificação

A especificação e SDK formam distribuição independente. A interface usa apenas essa API. O adaptador produtor privado permanece fora do produto. A ADR-0002 exige aceite humano para estabilização e dados reais. Testes de fronteiras, instalação limpa, imutabilidade, produtores e revisão independente serão ligados em `specs/001-atlas021-protocol-interface/traceability.md`. Nenhum teste verde autoriza migração ou retirada.
