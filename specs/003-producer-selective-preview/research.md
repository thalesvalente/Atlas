# Pesquisa focal de reaproveitamento — REUSE-01

## Decisão
Usar a projeção normalizada existente do produtor como fronteira do adaptador e manter Caderno 0.1.0a1 como formato de interoperabilidade. A análise detalhada das APIs privadas e seus hashes fica no repositório privado.

## Fundamentação
A candidata anterior interpretava novamente um índice nativo. Isso duplicava regras e já exigiu correção de tipos que o legado conhecia. O pipeline existente distingue estado técnico, revisão, fontes, relações e lacunas; a ponte deve transformar seus resultados, não recalculá-los.

## Alternativas descartadas
- Reimplementar leitor nativo: duplica semântica e amplia o risco de regressão.
- Embutir o produtor no viewer: viola independência e privacidade.
- Abandonar o Caderno e abrir apenas HTML antigo: atende visualização legada, mas não interoperabilidade.
- Reexecutar automaticamente a aquisição histórica: excede o escopo de transformação e os limites operacionais conhecidos.

## Incertezas explícitas
A projeção disponível no host real e sua cobertura ainda não foram observadas nesta sessão. Uma prova sintética não demonstra recuperação histórica. Recursos não representáveis no perfil mínimo ficam preservados como evidência da transformação e limitações, sem mudança unilateral do padrão.

## Decisão focal CLOSE01 — 2026-10-25

A incerteza acima descreve REUSE-01; LOCAL-REAL01 foi concluído e é reconciliado em
`convergence.md`. Esta sessão não acessou o host nem o pacote real do operador.

Leitura do código público: `to_read_model()` conserva `entities`, mas só projeta
`object`/`result` nos artefatos da execução. `refs()` é o helper vigente; o validador
exige alvos declarados. `Catalog` constrói índices em memória por fonte e a UI já
usa chave composta e navegação interna segura. Decisão: adicionar descritores de
menções a cada run e uma seção textual, reaproveitando essas regras. Alternativas
descartadas: inventar inputs/outputs, procurar IDs globalmente ou reler carrier
privado; todas perderiam semântica/isolamento. Nenhuma pesquisa de novo padrão é necessária.
