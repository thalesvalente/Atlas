# Feature 003 — Prévia seletiva de execução científica produzida externamente

**Status:** escopo de PoC, sem aceite científico ou alteração do protocolo.

## Visão
Como pesquisador, quero abrir no Atlas um pacote científico derivado de um subconjunto explicitamente selecionado por um produtor, para avaliar sua execução, revisão, métricas, artefatos e relações sem importar todo o acervo ou instalar o produtor.

### Histórias e critérios de aceite
**US1: receber pacote de produtor externo.** Dada uma fonte explicitamente fornecida, o SDK e o viewer já instalados devem ler metadados Caderno 0.1.0a1 sem importar bibliotecas do produtor. Fontes externas ou ausentes não acionam rede nem são consideradas verificadas.

**US2: exploração conservadora.** Projeto, experimento e execução mantêm IDs; estado técnico e revisão humana permanecem distintos, e `UNKNOWN` não vira `ACCEPTED`. O usuário identifica relações não exportadas como lacuna, em vez de vê-las como uma linhagem completa.

**US3: não desviar a arquitetura.** A conversão do formato privado permanece no produtor privado; o Atlas apenas interpreta o contrato público. O núcleo não ganha tipos ou condicionais exclusivos de um produtor.

**US4: operação reprodutível.** O operador consegue abrir um pacote pequeno em instalação Atlas existente, dentro de diretório local ignorado, sem copiar repositórios inteiros ou criar worktrees.

## Fora do escopo
BIM, IFC, IDS, SHACL, integração remota, alteração de formato do Caderno, importação de RAW protegido, execução real de modelos, migração ou aposentadoria do acervo, autenticação de autoria, release ou promoção canônica.

## Dependências
ADR-0001 e ARC-01–09 vinculantes. ADR-0002 e Caderno 0.1.0a1 ainda `PENDING_HUMAN`. PoC sintética anterior nas PRs #1/#3 e preparação de engenharia na #4 não são reimplementadas.

## Gate final
`ATLAS_SELECTED_PACKAGE_READABLE` no SDK e viewer independentes, `SOURCE_READ_ONLY` comprovado no escopo do produtor, `PUBLIC_SOURCE_TRANSFER=[]`; os resultados específicos sobre conteúdo real dependem de validação local privada, não são declarados por CI sintética.
