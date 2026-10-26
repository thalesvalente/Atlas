# Feature Specification: PoC reproduzível R4 → Caderno → Atlas

**Missão:** ATLAS021-A-POC-R4-FOCO01. **Data:** 2026-10-24.
**Estado:** candidata em verificação.
**Escopo:** [issue #2](https://github.com/thalesvalente/Atlas/issues/2).
Esta feature complementa a candidata PR #1 e a feature 001.

## User Scenarios & Testing

### US1 — Demonstrar o transporte e conservar o ensaio (P1)

Como demonstrador autorizado do produtor, quero criar uma amostra estritamente
sintética pelo caminho real do Caderno existente e conservar seu snapshot,
comparação semântica e recibos, para repetir a apresentação após o teste terminar.

**Teste independente:** exportação, validação e leitura recuperam os mesmos
registros e relações declarados; o resultado permanece em destino novo explícito.
Um destino existente é recusado sem alterar seus bytes.

**Aceite:** dado ambiente limpo e amostra sintética, quando a demonstração termina,
então há snapshot validado, mapa observável dos campos, recibo verificável e
instruções para abrir novamente a interface.

### US2 — Explorar e comparar sem o produtor instalado (P1)

Como leitor, quero abrir o snapshot em instalação independente e explorar catálogo,
filtros, todas as execuções, métricas, ausências, timeline, linhagem, evidências e
dossiê derivado, sem código ou arquivo histórico do produtor.

**Teste independente:** a mesma instalação abre a amostra R4 e o controle ambiental
existente. Cada fonte oferece comparação por identidade, tipo e unidade compatíveis;
comparação ambiental não é prova de comparação R4. Desktop e viewport móvel
conservam acesso à informação sem erro JavaScript ou pedido de rede externa.

### US3 — Revisar e entregar limites claros (P1)

Como revisor e Frente B, quero distinguir resultados técnicos, validade dos registros
e decisões humanas, com provas dos commits verificados e sem publicação de material privado.

**Teste independente:** casos inválidos são recusados/diagnosticados sem promover
estados; recibo final identifica escopo, perfil, commits, testes e limitações.
Disposição histórica fica desconhecida quando não há prova.

## Functional Requirements

- **FR-P01:** demonstração DEVE usar o caminho real de produção com fonte sintética;
  snapshot, recibos e roteiro DEVEM permanecer disponíveis após o processo.
- **FR-P02:** transporte DEVE preservar identidade, hierarquia, relações, estados,
  tempos declarados/desconhecidos, tipos, unidades, ausências e disponibilidade;
  perdas de representação DEVEM ser registradas e observáveis.
- **FR-P03:** leitor DEVE funcionar instalado sem produtor, acervo legado ou
  aquisição de contexto remoto; índices/dossiês DEVEM continuar reconstruíveis.
- **FR-P04:** prova de interface DEVE verificar todas as execuções de cada fonte,
  filtros, comparação compatível por fonte, timeline, linhagem e dossiê derivado.
- **FR-P05:** ausência NÃO DEVE virar zero; UNKNOWN/HOLD NÃO DEVEM virar sucesso
  ou aceite científico; tipo/unidade incompatíveis não são iguais.
- **FR-P06:** validação DEVE cobrir estrutura/tipo/ID inválido, relação pendente/cíclica,
  fonte ausente, hash divergente, ZIP corrompido/expansão excessiva controlada,
  perda numérica, mutação de fonte e referência externa sem download.
- **FR-P07:** demo pública DEVE ser reproduzível só com Atlas e produtor ambiental
  público existente. Código, corpus, mapas e recibos privados NÃO DEVEM ser copiados.
- **FR-P08:** evidências DEVEM distinguir execução local nova, prova histórica,
  CI e revisão; resultados DEVEM identificar bytes/commits pertinentes.
- **FR-P09:** handoff privado DEVE seguir AB-CONTRACT-1.0, separar independência
  funcional de disposição histórica e conservar decisões humanas pendentes.
- **FR-P10:** ADR-0001/ARC-01–09 e perfil candidato DEVEM permanecer preservados.
  BIM/IFC/IDS/SHACL, terceiro produtor, ciência real, merge, release, licença
  pública, promoção e operação física estão fora desta implementação.

## Non-functional Requirements

- **NFR-P01:** verificar Windows/Ubuntu, Python normal/otimizado; navegador real
  Linux desktop/móvel. Não atribuir Windows ao host local Linux.
- **NFR-P02:** fontes explícitas somente leitura; hashes antes/depois devem conservar
  pacotes e caderno sintético. Servidor de teste somente em loopback.
- **NFR-P03:** regressões proporcionais ao delta; reutilizar arquitetura, exportador,
  schema e provas de referência byte-identificadas que não mudaram.
- **NFR-P04:** falha de validação, instalação, comparação ou teste DEVE produzir
  saída de falha, nunca sucesso por mera conclusão da coleta.

## Edge Cases

Destino existente; tempo desconhecido; métrica ausente; número preciso; unidades/tipos
diferentes; fonte danificada ao lado de fonte saudável; ZIP pequeno com expansão
excessiva; dossiê válido sem revisão científica; browser com falha; commits divergentes.

## Success Criteria

- **SC-P01:** todos os registros/relações R4 sobrevivem conforme o mapa; nenhuma
  perda oculta nem fonte modificada.
- **SC-P02:** duas fontes existentes abertas pela mesma instalação independente;
  todas as execuções, ausências e relações verificadas, com comparação válida
  em cada fonte e zero erros de página/requisições externas.
- **SC-P03:** todos os cenários negativos têm evidência; uma fonte inválida não
  elimina a fonte saudável.
- **SC-P04:** sete gates técnicos completos no par final, recibo publicado e
  demonstração repetível pelas instruções.

POC_PASS_SCOPED e POC_TECHNICAL_READY=true exigem POC_R4_EXPORT, POC_ATLAS_IMPORT,
POC_UI_R4, POC_NEGATIVE_TESTS, POC_CI_REVIEW, POC_SCOPE_LOCK e POC_HANDOFF_B.
Prova parcial fica PARTIAL/HOLD com lacuna explícita. NOT_RUN cobre ciência real,
migração, retirada, experimentos/providers e ações humanas não decididas.

## Assumptions & Clarifications

Fonte é sintética; não se adquire acervo. Controle ambiental existente basta para
generalidade. Persistir demo significa conservar ensaio em diretório novo, sem
serviço permanente/backend novo. Corpus comparável pode ter valores sintéticos
declarados, conservando o corpus baseline por padrão.

### Session 2026-10-24

Missão, issue #2 e fontes primárias resolveram ambiguidades; zero perguntas.
ADR-0002 v1.0 / Caderno 0.1.0a1, digest
`76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e`,
continua PENDING_HUMAN, sem bloquear a PoC reversível autorizada.
