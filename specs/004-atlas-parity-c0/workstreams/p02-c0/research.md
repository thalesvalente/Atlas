# Decisões e evidência de projeto

- Baseline já possui busca/filtros, contagem, comparação, timeline, relações e menções;
  ampliar o shell, sem duplicar componentes P03 ou importar branches em movimento.
- `source-N` é posicional (`catalog.py`); manter API existente requer scope obrigatório
  nas identidades navegáveis. Nonce da sessão + fingerprints ordenados rejeita
  reinícios e reordenação mesmo quando pacotes têm bytes idênticos. Alternativa de
  hash de caminho foi recusada para evitar derivar identidade pública de path privado.
- SDK já fornece inputs, outputs, timestamp_origin e precisão. Renderizar os campos
  existentes evita mudar o Caderno. Comparação agrupa identidade/tipo/unidade.
- Contrato não fornece contagens da população de origem/seleção/conversão. Renderizar
  “não informado” com contagens locais separadas é a única interpretação sustentada.
- Reutilizar glob package-data atual. Novo asset requer adição explícita a ASSETS.
- CLI `specify` e navegador não encontrados no preflight. Helpers Python versionados
  podem ser executados sem instalação nem mudança de `.specify/feature.json`.
