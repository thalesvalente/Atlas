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
