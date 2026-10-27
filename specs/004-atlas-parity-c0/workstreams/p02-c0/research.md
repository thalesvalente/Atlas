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

## Atualização após execução, sem apagar o preflight

Chromium 153.0.8010.0 real foi disponibilizado no runtime isolado com
`@sparticuz/chromium@153.0.0`, após os arquivos de download padrão do Playwright
chegarem truncados. A jornada instalada passou 23 checks. A revisão identificou
glifos CJK/emoji ausentes; fontes compatíveis foram fornecidas somente no ambiente
de evidência e a mesma jornada foi repetida no mesmo CODE_SHA. Recibos e hashes em
`docs/missions/atlas-parity-02/p02-c0/receipts/`. Não houve alteração de produto por isso.

Helpers setup_plan, setup_tasks e check_prerequisites executados com NO_PERSIST.
O CLI oficial Spec Kit 1.2.3 e sua integração passaram nos jobs CI do CODE_SHA;
a auditoria histórica falhou para três arquivos de shell/catalog/server P02.
O harness browser global falhou em expectativa antiga de texto da célula de métrica.
Ambos os ajustes globais são P06, com diagnóstico e próximos atos exatos no handoff.
