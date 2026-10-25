# Feature 003 — Ponte interoperável com reaproveitamento do produtor

Revisão REUSE-01, 25/10/2026. Corrige a estratégia desta feature; não cria outra feature nem altera ADR-0001/ARC-01–09. Caderno 0.1.0a1 e ADR-0002 permanecem candidatos/PENDING_HUMAN.

## Objetivo
Como pesquisador, quero visualizar no Atlas um recorte da projeção científica que meu produtor já sabe construir, sem outro leitor de seu acervo e sem abandonar o contrato interoperável do Caderno.

## Requisitos
- FR-01: aquisição, interpretação de formatos nativos, normalização de estados e resolução de proveniência permanecem no pipeline existente do produtor. Não desenvolver um leitor paralelo no Atlas.
- FR-02: o adaptador é uma transformação explícita entre uma projeção existente, selecionada por identificadores exatos, e o Caderno 0.1.0a1. Não é um novo Caderno ou nova autoridade científica.
- FR-03: preservar registros, estados originais, parâmetros, métricas tipadas, referências e relações com origem declarada. Registrar dados não representados e relações cortadas pela seleção; não completar ausências por inferência.
- FR-04: a interface e o SDK continuam independentes do produtor. O adaptador específico fica no repositório privado do produtor; nenhum dado ou código privado é incorporado ao Atlas público.
- FR-05: metadados válidos não atestam autenticidade, disponibilidade de payloads, aceite científico ou recuperação histórica. A transformação não abre referências, não copia acervo e não executa modelos.
- FR-06: obter prova de interoperabilidade com o pipeline original sobre fixtures sintéticas e com o SDK/viewer instalados. Não usar um parser reimplementado em fixture como prova de reaproveitamento.
- FR-07: o recorte gera um pacote pequeno com metadados, fonte selecionada e manifesto de transformação. A fonte selecionada é evidência derivada, não cópia certificada do ledger. Não criar clones/worktrees no computador do operador.

## Histórias de usuário
US1: receber a projeção que o produtor já oferece e abrir o pacote convertido no Atlas.
US2: conferir a fidelidade campo a campo e ver limitações sem falsas aprovações.
US3: manter o mesmo contrato para outros produtores; formatos específicos não entram no núcleo.

## Aceite
Reaproveitamento demonstrado por testes com APIs existentes; nenhuma leitura nativa pelo conversor; SDK aceita a serialização; viewer funciona sem produtor; origem preservada no ensaio; revisão por SHA; zero alteração de constituição/perfil/schema. Leitura real do host e decisão de promoção são gates separados.

## Fora do escopo
BIM/IFC/IDS/SHACL, redesenho visual, pesquisa de um novo padrão, migração ou limpeza do acervo, chamadas a provedores, promoção canônica, merge, licença e release.

## Incremento operacional LOCAL-REAL01

### Requisitos adicionais
- FR-08: obter uma projeção operacional pelo pipeline existente, com origem, revisão de código, digest e alcance de leitura registrados. Ausência de configuração central não autoriza inicialização ou importação. Compatibilidade legada só quando já implementada e permitida.
- FR-09: disponibilizar o adaptador privado por distribuição verificável da revisão escolhida, incluindo sua cadeia de imports. Preservar o runtime existente do consumidor e a fonte histórica somente leitura; nenhum módulo privado entra no produto público.
- FR-10: selecionar a identidade solicitada sem fabricar presença. Uma substituição real, quando necessária, mantém o alvo original como pendência. Preservar os literais de estado e revisão e declarar as perdas do recorte.
- FR-11: validar o pacote no consumidor instalado e conferir a tela real em loopback, vinculando a identidade de origem à identidade exibida. Sem navegador disponível, registrar visualização não executada e entregar o comando; startup ou HTTP 200 não substituem a tela.
- FR-12: guardar dados operacionais e capturas em uma única raiz local ignorada, sem sobrescrever pacote existente, criar worktree ou ampliar os limites do adaptador. Publicação pública contém apenas resultado genérico sanitizado.
- FR-13: entregar comandos de repetição, reinício e encerramento, evidência delimitada de estabilidade das fontes observadas, PID/porta quando servidor iniciado e a menor ação restante para qualquer bloqueio. Verificar a porta antes de uso sem encerrar terceiros; manter somente a instância da demonstração, sem serviço permanente, e declarar se o processo não sobreviver ao término da sessão. Respeitar veto de plataforma ou leitor sem contorno.

### Cenários de aceite
- US1/P1: dada fonte operacional permitida e adaptador verificado, produzir um pacote da execução selecionada e abri-lo no consumidor independente; ou provar a chamada e a dependência exatas que impedem o percurso.
- US2/P2: comparar estados, parâmetros, métricas e lacunas disponíveis com a projeção capturada, mantendo revisão científica separada e referências sem direção como menções.
- US3/P2: repetir a inspeção do mesmo pacote sem produtor no processo consumidor e sem reinstalação.

### Critérios mensuráveis e exceções
- SC-01: uma execução operacional convertida e conferida em tela, com vínculo de identidade verificável e zero escrita nas fontes pela missão.
- SC-02: zero dado privado publicado no repositório público; zero nova worktree; runtime anterior preservado no escopo comparado.
- SC-03: em bloqueio, fechamento identifica etapa não executada, evidência concreta e ação mínima restante, sem marcar o piloto como concluído.
- Destino não vazio, alias ambíguo, caminho bloqueado, saída acima do limite ou leitura além do escopo interrompem a etapa dependente; não truncar, contornar nem criar pastas com sufixos.

### Clarificações de 2026-10-25
O pedido resolve as ambiguidades operacionais: leitura local delimitada autorizada, distribuição privada apenas no espaço operacional ignorado, fonte histórica sem escrita, visualização sem promoção científica e nenhum aceite automático de ADR-0002. Nenhuma pergunta adicional necessária.

## Incremento ATLAS003-CHAT-CLOSE01 — 2026-10-25

Retomar o piloto concluído pela frente LOCAL-REAL01 e tornar visíveis as referências
que o pacote já declara. A concordância do operador em avançar vale para esse escopo
demonstrado; não ratifica ADR-0002, ciência, merge ou release. Esta rodada usa apenas
fixtures públicas/sintéticas no ambiente de engenharia e na CI.

### Requisitos adicionais

- FR-14: apresentar as `mentions` da execução na seção **Referências relacionadas**,
  distinta de entradas, saídas e linhagem. Uma menção não afirma uso, produção,
  causalidade, integridade nem aprovação.
- FR-15: resolver identidade pelo par fonte/pacote e `@id`, nas formas admitidas
  pelo contrato existente. Repetições do mesmo alvo no mesmo pacote aparecem uma
  vez, na ordem da primeira menção; IDs iguais em fontes distintas ficam separados.
- FR-16: mostrar nome ou ID de fallback, tipo quando declarado, descrição disponível,
  digest declarado e observação de disponibilidade/integridade em campos distintos.
  Metadado declarado não é verificação; conteúdo ausente no pacote não prova ausência
  na origem. Alvo inexistente continua rejeitado pelo contrato (`MISSING_REFERENCE`).
- FR-17: execuções sem menções e projeções antigas sem o campo derivado novo mostram
  estado vazio claro. Preservar estados, revisão, métricas, parâmetros e relações
  existentes, sem converter menções em entradas/saídas nem inventar valores.
- FR-18: apresentar texto/HTML/URIs como dados inertes. Somente navegação interna
  existente pode abrir detalhes no mesmo pacote; nenhuma referência dispara
  download, leitura de caminho, execução ou navegação externa automática.
- FR-19: conservar foco visível, operação por teclado e hierarquia legível; títulos,
  descrições e IDs longos quebram linha. Verificar a seção em largura de 390 pixels
  e ampliação de 200%, sem redução de fontes ou rolagem horizontal na seção.
- FR-20: limitar a mudança ao modelo de leitura descartável e à apresentação genérica.
  Perfil/schema/contexto/ontologia, versão do protocolo e bytes de origem permanecem
  iguais. Reconstruir o índice e consumir pacotes antigos em instalação sem produtor.
- FR-21: fechar T020 com recibos existentes atribuídos a LOCAL-REAL01; atualizar o
  resumo atual da PR e publicar evidência da candidata por SHA, distinguindo HEAD,
  merge ref, prova sintética, piloto real, revisão independente e decisão humana.

### US4 — Conferir referências relacionadas (P1)

Uma pessoa revisora abre a execução e consulta as referências declaradas, sem
confundi-las com entradas/saídas nem com aceite científico.

1. Pacote com menções resolvidas, repetidas e formatos aceitos: mostrar cada alvo
   único com nome/ID e seus estados, na ordem declarada; preservar as outras relações.
2. Dois pacotes com o mesmo ID e nomes/estados diferentes: o detalhe e qualquer
   navegação interna permanecem na fonte selecionada.
3. Pacote sem menções ou modelo anterior: mostrar ausência de referências declaradas.
4. Alvo ausente: rejeitar o pacote, sem relaxar o contrato; payload ausente e digest
   apenas declarado: explicar o alcance sem atribuir ausência à origem.
5. Texto malicioso, URI externa e identificador longo: renderizar como texto, sem
   acesso externo; teclado, 200% e tela estreita continuam operáveis.

### Critérios do incremento

- SC-04: a omissão de menções reproduz RED na baseline instalada e GREEN após o
  incremento; todos os cenários US4 têm teste/evidência rastreável.
- SC-05: navegador real abre a seção e exercita teclado, navegação interna quando
  disponível, largura estreita e 200%; startup/HTTP 200 não contam como prova visual.
- SC-06: reconstrução do índice mantém a identidade fonte/ID e os bytes de todas as
  fontes sintéticas observadas; consumidor instalado não importa R4.
- SC-07: candidata publicada na PR existente, revisão independente por SHA e tabela
  objetiva da cadeia de integração; nenhum merge, release ou aceite humano simulado.

### Clarificações fornecidas na missão

Zero perguntas adicionais: protocolo persistido não muda; alvo ausente segue a
rejeição vigente; links internos já suportados são reutilizados e demais URIs ficam
inertes. Prova visual sintética da nova UI é separada do piloto real anterior. Sem
nova aquisição, adaptador, instalação no host do operador, piloto ou limpeza.
