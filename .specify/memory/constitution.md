# Atlas Constitution

## Core Principles



**ARC-01 — Atlas é produto de interface.** Explora projetos, experimentos, execuções, métricas, evidências, linhagem e dossiês. Pode importar para índices derivados, manter preferências e exportar visualizações. Não é o executor de experimentos, o gerador RF/RNF/RES, o sistema de aprovação científica nem o mecanismo de limpeza de discos.

**ARC-02 — O Caderno Científico é contrato interoperável, não a interface.** Define dados, relações, identificadores, versões, estados e regras de persistência/intercâmbio. Especificação, schemas, validação e SDKs não podem depender do Atlas ou do R4. Distinguir este protocolo futuro do Caderno legado do R4 e de seus dados privados.

**ARC-03 — Armazenamento é uma responsabilidade separada.** Um backend de referência pode ser local e simples. Atlas não pode ser a única autoridade nem o único meio de recuperar o acervo. Índices e caches da interface devem ser descartáveis e reconstruíveis a partir das fontes autorizadas. Não exigir serviço SaaS, banco específico ou conta de provedor para o núcleo mínimo.

**ARC-04 — Produtores publicam; Atlas interpreta.** R4 implementa um adaptador para o contrato público, como qualquer outro produtor. RF/RNF/RES são conteúdos/extensões de domínio, não tipos obrigatórios do núcleo universal. Atlas não importa `r4.*`, não descobre worktrees privadas e não contém condicionais por nome de projeto para funcionar.

**ARC-05 — Independência demonstrada, não apenas separação de pastas.** O pacote do Atlas instala e executa sem R4 instalado, sem diretórios históricos e sem configuração herdada. Dois produtores realmente distintos devem ser consumidos pela mesma interface. Protocolo e validação funcionam sem instalar a interface.

**ARC-06 — Integridade não é autenticidade nem aceite científico.** Preservar a distinção entre validade sintática, conformidade semântica, digest, origem declarada, autenticação independente e decisão científica. Não promover `UNKNOWN`, `HOLD`, resultado sintético ou evidência derivada para ciência aprovada. A interface não reescreve silenciosamente os registros originais.

**ARC-07 — A interface não recebe poderes de migração ou retirada.** Ferramentas de manutenção, compatibilidade legada e operações do host ficam fora do runtime do Atlas. Não mover o leitor Windows suspenso para o novo repositório nem reconstruí-lo como atalho. Políticas reais da plataforma permanecem superiores a este contrato.

**ARC-08 — Canonização e conservação são decisões distintas.** `thalesvalente/Atlas` é o repositório destinado ao novo produto. O CA-01 existente no R4 permanece referência operacional provisória até paridade comprovada e promoção humana. Publicar a nova aplicação não autoriza apagar os históricos, a implementação antiga ou o Caderno legado. Arquivos científicos preservados não são “instâncias redundantes do produto”.

**ARC-09 — Sem mudança arquitetural unilateral.** Um agente não pode trocar esta arquitetura por “Atlas contém Caderno/R4 inteiro”, protocolo dependente da UI, armazenamento inseparável ou lógica RF no núcleo para acelerar a entrega. Qualquer desvio exige ADR sucessor com requisito motivador, evidências, alternativas, impacto, riscos, custo de migração/rollback e testes; parecer independente; **aprovação humana explícita vinculada à versão da proposta antes de implementar o desvio**. Silêncio, CI verde, comentário de bot e autorização de outra operação não são aprovação. Decisões técnicas compatíveis com ARC-01–08 continuam delegadas e documentadas.


## Privacidade e ownership

Conteúdo privado, inclusive código derivado, depende de liberação específica antes
 de publicação. A Frente A responde pelo produto/protocolo/adaptadores; B pela
preservação física. Comentários de coordenação são append-only por emissor.

## Development Workflow

constitution → specify → clarify → plan → checklist → tasks → analyze → implement
→ verify/test → converge → independent review. Evidências distinguem execução real,
sintética, CI, revisão, validade sintática, integridade e decisão científica.

## Governance

ARC-01–09 são direção aprovada na instrução do operador ATLAS021; sua implementação
não está automaticamente aprovada. ADR-0002 permanece candidata até aceite explícito.
Desvio arquitetural exige ADR sucessora, análise independente e aprovação humana
vinculada à versão antes de implementação. PUBLIC-SOURCE-TRANSFER, release, promoção,
migração e retirada preservam gates próprios. Não há ratificação de detalhes por bots.

**Version**: 1.0.0 | **Ratified**: direção na instrução de 2026-10-24 | **Last Amended**: 2026-10-24
