# Especificação C2 — qualificação focal P03

Missão ATLAS-PARITY-03-C2, 2026-10-27 (America/Fortaleza).
Branch `qa/atlas-parity03-c2-p03-gates-20261027`.
Entrada de código `6c412c36e1dbe11711daa15c6d8727fbe94fa0ad` e handoff
`ead1f753f52f22035326b7366dd2231c62775765`. O prompt do operador autoriza
qualificação isolada, sem composição. `VISIBLE_IN_MAIN_APP=false`.

## Cenários

1. Uma pessoa integradora confere 25 arquivos congelados, o manifesto original
   de 56 entradas e a preservação dos 219 arquivos herdados antes de compor.
2. Uma pessoa revisora instala SDK/viewer em ambientes novos fora do checkout,
   compara bytes dos wheels com Git e executa o teste JSON Schema anteriormente pulado.
3. Uma pessoa usuária navega pelo harness sintético em Chromium real, com teclado,
   390/320 CSS px, texto ampliado por espaçamento, dados tipados e conteúdo hostil inerte.

## Requisitos verificáveis

- FR-C2-001: fixar árvores/SHAs, conferir manifesto e todos os 25 arquivos P03;
  preservar originais, fontes, contrato, protocolo, shell e workflows globais.
- FR-C2-002: fornecer `jsonschema==4.25.1` test-only, Node 24 e coleção SDK/P03
  com teste de schema presente; falhar com qualquer skip, coleção vazia ou incompleta.
- FR-C2-003: construir com setuptools 80.9.0 e instalar SDK/viewer separadamente
  fora do checkout, sem produtor, índice de pacotes ou PYTHONPATH herdado.
- FR-C2-004: executar HTTP real em loopback no runner, allowlist exata de oito
  rotas, MIME/CSP, negativas de aliases/traversal/payload/métodos/origem e sem rede externa.
- FR-C2-005: executar Chromium real existente no Actions; tabela semântica,
  sort/filter tipados, precisão lexical, grandes inteiros, booleanos reais,
  null/ausência/motivo, File, mentions, teclado/foco, 390/320px, scroll 2D contido,
  text spacing, conteúdo hostil, zero erros/requisições externas do contexto.
- FR-C2-006: registrar zoom nativo a 200 como NOT_RUN se não comprovável. CSS zoom,
  deviceScaleFactor e CDP page scale não são substitutos.
- FR-C2-007: Linux/Windows para gates portáveis; Python normal e -O; JSON e PNG
  ligados ao SHA exato; CI terminal e parecer independente sem autoria do delta.
- FR-C2-008: demonstradores continuam `synthetic=true`; nenhuma qualificação
  deste harness é atribuída ao servidor ou ao browser global da aplicação.

## Critérios de sucesso e limites

`C2_P03_QUALIFIED_FOR_COMPOSITION` exige FR-C2-001–008 e revisão independente
do SHA final. Zoom nativo sem controlador comprovável recebe NOT_RUN, conforme
exceção explícita do operador. Qualquer gate obrigatório bloqueado resulta em
`C2_BLOCKED_EXACT`, com capacidade, job/step e menor ato.

ARC-01–09 preservados. O aceite já registrado da direção ADR-0002 é reconhecido;
não cria autorização de schema, composição, publicação canônica ou ciência.
R4 é produtor externo, sem imports, leitura privada ou execução.
