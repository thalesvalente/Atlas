# Clarificações — REUSE-01

1. O usuário determinou reaproveitar o pipeline do Atlas/Caderno legado, mantendo o Caderno interoperável. Essa direção é compatível com ARC-01–09; não ratifica ADR-0002.
2. Não basta reutilizar nomes de campos. O teste deve chamar as APIs originais do produtor e converter sua projeção, sem outro algoritmo de leitura do índice bruto.
3. Uma leitura existente pode inspecionar fontes registradas. O conversor não ganha, por isso, autorização para chamá-la sobre acervo real. A aquisição permanece responsabilidade do produtor em contexto permitido.
4. A conversão atua sobre dados já capturados. Seleção e mapeamento de vocabulário pertencem ao adaptador; reconstrução de evidências e estado do ledger, não.
5. Referência a evidência não significa entrada experimental. Sem direção declarada, mantê-la como menção/referência e documentar o limite de apresentação do viewer atual.
6. Reutilizar não significa publicar bibliotecas privadas no Atlas nem voltar a incorporar o R4 à interface.
7. Não criar outra frente ou outra numeração: atualizar feature 003, a candidata existente e sua rastreabilidade.

## LOCAL-REAL01 — esclarecimentos fornecidos pelo operador
Leitura local de código, configuração e metadados necessários e obtenção autenticada do adaptador estão autorizadas no escopo do piloto. Fonte histórica permanece somente leitura. Distribuição privada e evidências operacionais ficam na raiz ignorada escolhida pelo operador, sem importação de módulos no produto público. Nenhum novo Caderno, reader, ambiente consumidor ou worktree é necessário. Bloqueio de leitura real é específico ao mecanismo observado; não amplia nem cancela por inferência outras permissões. Zero perguntas adicionais: identidade ausente, limites de leitura, browser indisponível e revisão científica pendente já têm tratamento definido no pedido.
