# ADR-0002 — RO-Crate 1.3 e Process Run 0.6 como candidato de protocolo

**Versão da proposta:** 1.0, 24/10/2026. **Estado:** PROPOSED / PENDING_HUMAN.
**Direção vinculante já aprovada:** ARC-01–09 de ADR-0001.
**Aceite desta escolha específica:** não recebido. Implementação candidata e
provas sintéticas não equivalem a aceite humano ou promoção canônica.

## Problema e decisão recomendada

Precisamos de um contrato que dois produtores diferentes possam publicar e que
uma interface genérica possa ler sem conhecer o código ou o armazenamento de
qualquer produtor. Resultados, revisão científica, integridade e disponibilidade
precisam continuar conceitos distintos. Um pacote deve permanecer recuperável
sem a interface e sem conta de serviço.

**Recomenda-se uma única combinação:** RO-Crate **1.3.0**, Process Run Crate
**0.6**, perfil mínimo **Caderno 0.1.0a1** com serialização JSON-LD restrita,
snapshots imutáveis em diretório/ZIP e extensões namespaced documentadas.
O perfil é descrito em [0.1.0a1](../protocol/0.1.0a1.md); sua versão e digest
constam em [profile-manifest.json](../protocol/profile-manifest.json).

Protocolo/SDK, backend de acesso e interface mantêm dependências direcionais.
O SDK roda sem viewer ou produtor. A UI lê dados e produz representações
derivadas. Exportadores e eventual conversor histórico são ferramentas separadas.

## Alternativas e evidência

A [pesquisa completa](../../research/protocol-options.md) confronta padrões,
versões, maturidade e licenças. RO-Crate fornece pacote/grafo; Process Run 0.6
declara compatibilidade com 1.3. ELN fixa RO-Crate 1.2; o protótipo comparativo
passou nos campos e checks ensaiados, mas requer outra combinação de versões.
OpenLineage atende eventos e linhagem de pipelines; ISA acrescenta conceitos de
estudo/amostra/ensaio que não são universais. PROV, JSON Schema e SHACL cumprem
funções complementares de semântica/validação.

As provas executadas recuperaram os mesmos **2 projetos, 3 experimentos, 4 runs
e 12 relações** nos finalistas RO-Crate/ELN. A base 1.3 e a alternativa base 1.2
passaram em **63 checks, zero falhas e três skips explícitos** no validador
externo 0.13.0. Seu catálogo Process Run ainda é 0.5: não há alegação de prova
externa integral de 0.6. O SDK/JSON Schema é complementado por QA independente.

## Extensões mínimas e restrições aceitas pela proposta

- Tipos `cp:Project`/`cp:Experiment` e ligação da execução ao experimento.
- Estados de execução/revisão separados, marcador sintético e origem temporal.
- Métricas/parâmetros tipados, unidade, precisão declarada e motivo de ausência.
- Disponibilidade declarada e SHA-256 de bytes, separados dos resultados observados.
- Contexto pinado localmente; relações declaradas, IDs com namespace, rejeição de
  duplicação/ciclos e limites explícitos de leitura/ZIP.

O enum schema.org não distingue PARTIAL/UNKNOWN diretamente. O perfil mantém
esses estados exatos em `cp:executionStatus`; a projeção da base utiliza Failed
para execução não integral e Potential para estado desconhecido, sem inferir
sucesso. Consumidores sem a extensão perdem essa nuance. Essa limitação integra
a proposta submetida à decisão humana.

## Custos, riscos e reversibilidade

O custo inicial é manter um schema, checagens semânticas restritas, um SDK Python
sem dependência de runtime e testes separados. Suportar RDF arbitrário, eventos,
assinaturas ou conversões gerais de unidades aumentaria esse custo sem evidência
de necessidade no primeiro incremento.

O catálogo externo não cobre Process Run 0.6 completamente; suas verificações
devem ser confrontadas com o texto normativo. A URI do candidato resolve na
branch e depende de sua conservação; promoção estável precisa de publicação
persistente. Digests não autenticam autoria/data. A defesa de paths não é
certificação de host adversarial. O viewer não recebe poderes de migração.

Rollback técnico: abandonar a candidata, conservar os snapshots/artefatos de
teste e manter a referência operacional anterior. Nenhum dado histórico é
reescrito. Uma versão futura incompatível deve definir migração explícita,
provas de perdas/identidade e novo gate; não reaproveitar silenciosamente esta URI.

## Decisão material solicitada ao operador

Aprovar ou rejeitar **esta combinação e o perfil 0.1.0a1 no digest do manifesto**
como direção para estabilização. Esse aceite específico não autoriza merge,
release, deploy, transferência de fonte privada, aplicação a acervo real ou
remoção física. Essas operações mantêm seus gates próprios e evidências exatas.
