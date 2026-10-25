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
BIM/IFC/IDS/SHACL, mudanças visuais, pesquisa de um novo padrão, migração ou limpeza do acervo, chamadas a provedores, promoção canônica, merge, licença e release.
