# Validação da ponte reaproveitada

1. No contexto privado do produtor, obtenha uma projeção pelo pipeline existente, somente onde essa aquisição já estiver permitida.
2. Entregue a projeção capturada ao adaptador, com seleção explícita e digest. Ele não deve reabrir fontes.
3. Valide o pacote com o SDK Caderno e abra-o com a instalação Atlas já existente, usando `atlas_viewer inspect` e `serve --source`.
4. Confira IDs, estados originais, revisão independente do resultado, métricas, referências e perdas do recorte.

Não executar novamente os comandos antigos de interpretação direta de índice. O guia privado acompanha a revisão da ponte e define as pré-condições; este documento não autoriza leitura de acervo, publicação, migração ou exclusão.

No piloto REUSE-01/LOCAL-REAL01, runtime, perfil e schema públicos ficaram
inalterados. CLOSE01 acrescenta a apresentação genérica abaixo; perfil/schema
continuam intactos. Nenhum requisito de BIM ou SHACL é adicionado.

## Conferir CLOSE01 sem repetir o piloto

Use um checkout de engenharia desta candidata e as dependências já fixadas no
workflow. O diretório de trabalho abaixo precisa ser novo; o helper não sobrescreve
uma instalação existente e não acessa fontes do operador.

```sh
python scripts/qa/clean_install.py --repo . --work .ci-related-check
python scripts/ci/run_browser.py --work .ci-related-check --related-references
```

O segundo comando requer o Chromium/Playwright já previsto na CI. Ele gera dois
pacotes sintéticos, abre o produto instalado sem R4 e encerra somente o processo
filho que iniciou. A CI executa esse cenário após os cenários existentes, usando
`.ci-clean`, e preserva JSON/PNGs sintéticos em artefato associado ao HEAD.

No detalhe de uma execução, confira **Referências relacionadas**: nome/ID, tipo,
descrição e digest/disponibilidade separados. Menções não acrescentam entradas,
saídas ou linhagem. O link de uma execução referenciada abre o alvo na mesma fonte;
URIs externas e caminhos são texto. Uma execução sem menções tem estado vazio.
O ensaio inclui teclado/foco, 390 pixels e ampliação de renderização CSS em 200%;
não constitui certificação WCAG ou teste de todos os mecanismos de zoom do navegador.

Para os auxiliares oficiais, use seleção explícita da mesma feature:

```sh
SPECIFY_FEATURE_NO_PERSIST=1 SPECIFY_FEATURE_DIRECTORY=specs/003-producer-selective-preview python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
python scripts/qa/speckit_audit.py --allow-presentation-delta
```

O gate histórico de setup, sem a opção explícita, continua rejeitando alterações
de runtime. A opção libera somente os seis caminhos de apresentação/harness já
delimitados; governança e recursos persistidos permanecem protegidos.

O pacote privado real não precisa ser transferido nem convertido de novo. Sua
conferência adicional com a UI nova, se desejada posteriormente, pertence ao
operador e não é condição para a prova sintética deste incremento.
