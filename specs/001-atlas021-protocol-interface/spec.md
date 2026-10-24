# Feature Specification: Atlas independente e Caderno interoperável

**Feature Branch**: `feat/atlas021-interface-protocol`

**Created**: 2026-10-24

**Status**: Draft — candidata autorizada; estabilização do protocolo e promoção dependem de decisão humana.

**Input**: Missão ATLAS021 Frente A e contrato AB-CONTRACT-1.0.

## User Scenarios & Testing

### User Story 1 — Explorar fontes declaradas (Priority: P1)

Uma pessoa pesquisadora abre uma fonte autorizada, identifica sua versão e validade,
consulta projetos, experimentos e execuções e inspeciona resultados sem alterar o acervo.

**Why this priority**: prova a independência e entrega consulta útil.

**Independent Test**: instalar somente o produto e seu protocolo em ambiente vazio;
abrir fonte sintética e verificar os registros exibidos e seus bytes originais.

**Acceptance Scenarios**:

1. Dada uma fonte válida explicitamente fornecida, abrir a interface mostra projetos,
experimentos, execuções, métricas, parâmetros, artefatos e versão do perfil.
2. Dada fonte vazia, inválida, inacessível ou versão desconhecida, exibir estado legível
sem inventar registros nem seguir referências externas automaticamente.
3. Dado rótulo contendo HTML/script, apresentar texto sem executar conteúdo.

### User Story 2 — Comparar e apresentar evidências (Priority: P1)

Uma pessoa revisora filtra execuções, compara apenas métricas compatíveis, navega por
linhagem/timeline e exporta dossiê derivado com referências e limitações.

**Why this priority**: torna observáveis evidências e incertezas.

**Independent Test**: selecionar duas execuções do mesmo conjunto, verificar valores,
unidades, parâmetros, origens e estado de revisão separados; exportar apresentação.

**Acceptance Scenarios**:

1. Busca, projeto, experimento e estado restringem os resultados e podem ser limpos.
2. Métricas de igual identidade/tipo/unidade podem ser comparadas; unidades diferentes
ou valores ausentes recebem aviso explícito sem conversão implícita.
3. Execução parcial/falha e revisão UNKNOWN/HOLD mantêm seus significados na tela,
na timeline, na linhagem e no dossiê. Dossiê é derivado e não certificação.
4. Fluxos principais funcionam por teclado, com nomes acessíveis e a 390 e 1440 pixels.

### User Story 3 — Interoperar e reconstruir (Priority: P1)

Um produtor independente publica registros pelo mesmo protocolo público. Outro
produtor adapta entradas legadas explicitamente selecionadas, preservando identificadores,
valores originais e limites da transformação.

**Independent Test**: executar ambos os exportadores sobre fixtures sintéticas,
validar fora da interface e consumir pela mesma instalação, sem flags de domínio.

**Acceptance Scenarios**:

1. O validador funciona sem instalar a interface nem qualquer produtor.
2. Reabrir/reconstruir índices recupera os mesmos registros a partir das fontes.
3. Um ID colidente entre fontes diferentes não sobrescreve silenciosamente um registro.
4. Uma alteração de fonte já aberta é sinalizada; reconstrução é explícita e preserva
os bytes da fonte e a distinção entre estado derivado e autoridade.

### Edge Cases

Metadados acima do limite, quantidade excessiva de entidades, referências ausentes,
IDs duplicados, contexto não catalogado, formatos desconhecidos, números não finitos,
path absoluto/traversal/symlink, digest divergente, ausência de payload, data sem origem,
timestamp inválido, ciclos e órfãos na linhagem, ação sem estado, rede indisponível,
cache descartado e mudanças após abertura. Pacotes ZIP podem ser lidos com limites
explícitos em memória, sem extração; entradas perigosas ou excessivas são recusadas.
Pacotes expandidos e metadados declarados são suportados. Uma extensão .eln não
implica conformidade com o perfil ELN, cuja versão é distinta. Não há download implícito de contexto ou evidência remota.

## Requirements

### Functional Requirements

- **FR-001**: abrir apenas fontes declaradas e exibir versão, validade e limites; ARC-01/02.
- **FR-002**: listar projetos/experimentos/runs e oferecer busca e filtros; ARC-01.
- **FR-003**: detalhe com parâmetros, métricas tipadas/unidades, evidências e referências; ARC-01/06.
- **FR-004**: comparação recusa incompatibilidade de tipo/unidade e explicita ausência; ARC-06.
- **FR-005**: timeline/linhagem mantêm IDs, origem das datas e relações declaradas; ARC-01/06.
- **FR-006**: dossiê derivado inclui navegação, fontes e limites sem alterar ciência; ARC-03/06.
- **FR-007**: fonte imutável; índice reconstruível e preferências em estado separado; ARC-03.
- **FR-008**: protocolo com versão exata, contexto restrito, IDs, relações e estados validados; ARC-02.
- **FR-009**: SDK/validador independentes, interface sem imports produtores/host; ARC-02/04/05/07.
- **FR-010**: dois exportadores distintos e mesmo leitor, com execução sintética explícita; ARC-04/05.
- **FR-011**: mapear legado sem apagar valores desconhecidos, datas, estados ou IDs; ARC-06/08.
- **FR-012**: distinguir sintaxe, semântica, digest, origem declarada, autenticação e aceite; ARC-06.
- **FR-013**: rejeitar conteúdo perigoso, traversal/symlink e versões/contextos desconhecidos; ARC-07.
- **FR-014**: não executar experiências, aprovar ciência, migrar acervo ou aposentar fontes; ARC-01/07/08.
- **FR-015**: teclado, rótulos acessíveis, foco visível e layout adaptado a desktop/mobile; ARC-01.
- **FR-016**: registrar A-DATA-REQUIREMENTS, mapeamento e disposição por ID conhecido; ARC-08/09.
- **FR-017**: manter ADR-0002 candidata até aceite humano vinculado à versão; ARC-09.
- **FR-018**: produzir CI Windows/Ubuntu normal/otimizado e revisão no SHA publicado; ARC-05/09.
- **FR-019**: fontes com IDs iguais são identificadas pelo par fonte/ID, com conflito visível; ARC-03/06.
- **FR-020**: detectar mudança de metadados/payload e mostrar digest separado da autenticação; ARC-06.

### Key Entities

Projeto contém experimentos; experimento agrupa execuções; execução é atividade de um
agente com parâmetros, entradas/saídas e tempos declarados. Artefato/evidência são
entidades referenciáveis cuja disponibilidade é separada da existência. Métrica possui
identidade, tipo, valor opcional e unidade. Relação expressa uso/geração/derivação.
Fonte identifica um snapshot e sua versão; índice e dossiê são derivados descartáveis.
Estado de execução, revisão científica e integridade são dimensões distintas.

## Success Criteria

### Measurable Outcomes

- **SC-001**: uma instalação vazia sem produtor legado apresenta todos os registros
sintéticos esperados do corpus declaradamente usado no teste, sem dados inventados.
- **SC-002**: os dois produtores passam a mesma validação independente e são exibidos
pela mesma instalação sem seleção de regras por projeto.
- **SC-003**: todas as negativas declaradas têm erro verificável; nenhuma resolução de
contexto ou evidência implica tráfego de rede durante a leitura.
- **SC-004**: comparação, detalhe, filtros, timeline e dossiê preservam valores/estados;
fluxos de teclado e layouts de 390/1440 pixels passam teste de navegador real.
- **SC-005**: bytes das fontes permanecem iguais antes/depois da leitura, comparação,
exportação e reconstrução; adulteração é sinalizada.
- **SC-006**: marcos A0–A7 recebem apenas estados sustentados por evidências e autorização;
nenhum gate humano pendente é marcado PASS por CI ou revisão automática.

## Assumptions

Uso local por uma pessoa, sem serviço SaaS, conta ou acesso remoto. Fontes de ensaio são
sintéticas; produção real não está autorizada. A proposta de protocolo pode ser
implementada/testada em pré-release antes de aceite, como permite a missão.
O runtime histórico segue referência provisória até paridade e promoção explícitas.
O inventário lógico B foi recebido pela coordenação privada; identidades individuais
e disposições ficam no registro privado. Receber IDs não confere acesso ao conteúdo,
dispensa de consumidores ou autorização física. Necessidades históricas permanecem UNKNOWN.

## Clarifications

### Session 2026-10-24

Escopo, separação A/B, visibilidade, gates e autorização de protótipo já estão resolvidos
pela missão. Nenhuma nova pergunta é necessária para desenvolver a candidata.
A única decisão material de protocolo será submetida após proposta concreta testada.
Licença/release/migração/retirada ficam fora da execução autorizada.
