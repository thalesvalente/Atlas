# Feature Specification: configuração portátil de fontes

**Feature Branch**: `feat/atlas-portable-source-config-20261110`  
**Created**: 2026-11-10  
**Status**: contrato de implementação; validação Windows pendente.  
**Base observada**: `development`, commit `43f7aaafedac7e8b124188baa51b888cee74c13c`, tree `1645cc3edda61cc6372faef21af014f698583934`.

## User Scenarios & Testing

### User Story 1 — Configurar e reutilizar fontes (Priority: P1)

O operador escolhe manualmente um ou mais pacotes compatíveis, salva a seleção e
abre o Atlas novamente sem editar scripts nem repetir caminhos.

**Independent Test**: com configurações isoladas e pacotes sintéticos, salvar a
seleção, iniciar outra execução, conferir as fontes e comparar os bytes do pacote.

**Acceptance Scenarios**:

1. Sem configuração padrão nem fontes explícitas, abrir catálogo vazio legítimo,
   com orientação de configuração e sem procurar outros diretórios.
2. Configurar de uma a 16 fontes válidas persiste a seleção ordenada; uma nova
   execução utiliza exatamente essa lista, sem R4 instalado ou importado.
3. Exibir a configuração informa estado e contagem, sem caminhos por padrão;
   a divulgação de caminhos exige opção explícita para consulta local.
4. Limpar a seleção persiste lista vazia; a próxima execução permanece vazia.

### User Story 2 — Mudar de computador ou disco (Priority: P1)

O operador substitui os caminhos na configuração quando muda a instalação,
sem modificar o código ou copiar conteúdo científico para o repositório.

**Independent Test**: selecionar uma cópia sintética, removê-la, observar erro,
selecionar outra cópia explicitamente e reabrir a seleção corrigida.

**Acceptance Scenarios**:

1. Fonte salva inexistente/inacessível gera erro legível e reconfigurável; nenhuma
   outra fonte é escolhida automaticamente.
2. Caminhos com espaços/acentos e caminhos relativos têm resolução definida
   pelo contrato em `plan.md`, independente do diretório de execução posterior.
3. Arquivo indicado explicitamente e ausente, malformado ou incompatível falha;
   o Atlas nunca migra, ignora silenciosamente nem reescreve esse arquivo ao ler.
4. Falha durante gravação anterior à troca atômica preserva os bytes antigos;
   não sobra configuração parcial apresentada como válida.

### User Story 3 — Preservar seleções explícitas (Priority: P1)

Comandos existentes com `--source`/`-Source` continuam escolhendo apenas as
fontes fornecidas. O operador pode iniciar sem configuração persistida.

**Independent Test**: guardar configuração inválida e conferir que uma fonte
explícita válida ainda funciona; iniciar com configuração desabilitada e verificar
estado vazio. Exercitar os launchers sem servidor nos modos de gestão.

**Acceptance Scenarios**:

1. Fonte explícita substitui integralmente qualquer configuração, sem mescla
   nem leitura do arquivo que foi sobreposto.
2. Seleção explicitamente vazia no launcher não permite ao processo filho reler
   a configuração padrão e abrir dados diferentes.
3. Adaptador legado opt-in preserva o comportamento histórico: sem fonte nem
   configuração explícita, não acrescenta fontes persistidas automaticamente.
4. Python, Windows PowerShell 5.1 e PowerShell 7 oferecem a mesma escolha manual;
   o teste efetivo no host Windows é registrado separadamente.

### Edge Cases

Lista vazia, strings vazias, tipos incorretos, versão desconhecida, chaves JSON
ambíguas, duplicação da mesma fonte por caminhos equivalentes, diretório versus
seu `ro-crate-metadata.json`, 17 fontes, links rejeitados pelo leitor, fonte
substituída após salvar, destino de configuração dentro de pacote, falhas de
permissão/escrita/troca, execução sem terminal e erro de configuração contendo
caminhos privados. Não há fallback por busca, prompt automático ou API HTTP de escrita.

## Requirements

### Functional Requirements

- **FR-001**: salvar configuração local versionada, legível e editável; fora do Git e separada da identidade científica.
- **FR-002**: aplicar precedência exclusiva fonte CLI → arquivo explícito → arquivo padrão; nenhuma mescla ou leitura da opção sobreposta.
- **FR-003**: configuração padrão ausente e seleção vazia são estados legítimos; arquivo explícito ausente gera erro.
- **FR-004**: configurar, exibir e limpar fontes por CLI e launcher, sem iniciar servidor nos modos de gestão.
- **FR-005**: resolver caminhos relativos com base documentada; preservar espaços e Unicode entre processos.
- **FR-006**: validar estrutura, versão, tipos e valores do arquivo sem fallback silencioso.
- **FR-007**: recusar caminhos inexistentes, inacessíveis ou impróprios; validar compatibilidade antes de salvar pelo SDK existente.
- **FR-008**: manter o limite de 16 fontes, incluindo o adaptador quando usado; recusar duplicados sem descartar silenciosamente entradas.
- **FR-009**: substituir configuração atomicamente; erro anterior à substituição preserva o arquivo anterior e permite nova tentativa.
- **FR-010**: nenhuma leitura, inicialização ou exibição grava configuração nem modifica pacotes científicos.
- **FR-011**: não gravar configuração dentro de fonte escolhida nem sobrescrever pacote/metadata; preservar rejeições de links do SDK.
- **FR-012**: funcionamento independente do R4, sem dependências externas novas ou descoberta de fontes/worktrees/unidades.
- **FR-013**: preservar comandos explícitos existentes e o fluxo opt-in do adaptador externo; `inspect` continua independente de configuração.
- **FR-014**: desabilitar configuração persistida por opção explícita e congelar a seleção transmitida ao processo filho.
- **FR-015**: erros e resumos padrão não divulgam caminhos privados; detalhe local exige `show-paths` explícito.
- **FR-016**: fornecer documentação de instalação/reconfiguração em outro computador e handoff sintético para Windows 5.1/7.
- **FR-017**: implementar e executar testes disponíveis com fixtures sintéticas; registrar comando, ambiente, resultado e limites reais.
- **FR-018**: preservar ARC-01–09, ADR-0001, protocolo, fontes e branches protegidas pelo escopo; publicar somente branch própria e PR Draft.

### Key Entities

**Configuração local**: versão do formato e seleção ordenada de fontes; preferência
operacional, sem identidade científica ou garantia de autenticidade.
**Fonte selecionada**: caminho local explícito de um pacote já suportado pelo
protocolo. **Seleção efetiva**: lista derivada da precedência desta execução.

## Success Criteria

### Measurable Outcomes

- **SC-001**: primeira execução vazia, configuração manual e reutilização funcionam com 0, 1 e 16 fontes; 17 e duplicados falham claramente.
- **SC-002**: troca explícita do caminho permite reabrir a fonte sintética movida; fontes inexistentes nunca causam escolha de dados alternativos.
- **SC-003**: todas as negativas planejadas têm resultado verificável; arquivos científicos e configuração antiga permanecem íntegros nos casos especificados.
- **SC-004**: seleção explícita anterior continua utilizável mesmo com configuração padrão malformada, e não importa R4.
- **SC-005**: a PR contém implementação, testes, revisão independente e handoff; Windows permanece `LOCAL_TEST_NOT_RUN` até recibo efetivo.

## Assumptions

Uso local de uma pessoa, sem host adversarial controlando simultaneamente caminhos.
Não se acrescentam serviços, UI de seleção de arquivos, migração automática,
telemetria, provider ou controle de concorrência entre vários operadores.
Os caminhos desta documentação são placeholders, não caminhos do operador.
O integrador aprovou as decisões em `plan.md`; não há questão funcional pendente.
