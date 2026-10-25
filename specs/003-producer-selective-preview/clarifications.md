# Clarificações — REUSE-01

1. O usuário determinou reaproveitar o pipeline do Atlas/Caderno legado, mantendo o Caderno interoperável. Essa direção é compatível com ARC-01–09; não ratifica ADR-0002.
2. Não basta reutilizar nomes de campos. O teste deve chamar as APIs originais do produtor e converter sua projeção, sem outro algoritmo de leitura do índice bruto.
3. Uma leitura existente pode inspecionar fontes registradas. O conversor não ganha, por isso, autorização para chamá-la sobre acervo real. A aquisição permanece responsabilidade do produtor em contexto permitido.
4. A conversão atua sobre dados já capturados. Seleção e mapeamento de vocabulário pertencem ao adaptador; reconstrução de evidências e estado do ledger, não.
5. Referência a evidência não significa entrada experimental. Sem direção declarada, mantê-la como menção/referência e documentar o limite de apresentação do viewer atual.
6. Reutilizar não significa publicar bibliotecas privadas no Atlas nem voltar a incorporar o R4 à interface.
7. Não criar outra frente ou outra numeração: atualizar feature 003, a candidata existente e sua rastreabilidade.
