# Handoff ao Codex LOCAL — Atlas N02 + N03

## Missão e ownership

Executar QA LOCAL somente leitura sobre a composição identificada no P00_HANDOFF
terminal da PR. Repositório thalesvalente/Atlas; branch de integração
integrate/atlas-n02-n03-20261106. Conferir o SHA/tree exatos do recibo antes de executar.
Não usar um HEAD mais recente presumindo o mesmo PASS. N02 original está em
ddf866ffb3eda09f5185a007a4c7a24a31eac57e; N03 preservada em
209b3f1fc9ab478c8d2adb84e0bb61f22106ad79.

O CHAT implementou/testou/publicou software público; o LOCAL mantém responsabilidade
pelos bindings privados. Não publicar nem enviar corpus, nomes privados ou relatórios
com identidades científicas. Retenção continua proposta; DELETE_AUTHORIZED=NO.

## READBACK e preparação delimitada

1. Resolver PROJECT_ROOT para um checkout/worktree autorizado; conferir permissões,
   git status/diff/worktrees, HEAD/tree/remotes e AGENTS.md. Preservar trabalho existente.
   Revalidar o recibo P00, A01 no 8e0e400d5220efceb6dd881772e5b07825442970 e T015 no
   46e18bd5c90b922b78cf6731f83ceedc4c09df85; não reaplicar seus aceites ao composto.
2. Reusar N01-R, inventário de 684 arquivos / 638 hashes seletivos e os 5 itens vinculados, juntamente com
   o plano KEEP_FULL. Conferir hashes e proveniência já existentes. Não repetir rescan,
   rehash integral, restauração, medição ou execução histórica quitada/fora de escopo.
3. Ler contracts/local.md. Capturar UM source DTO atual READY do leitor validado LOCAL,
   preservando todos os entries e os lexemas, e conferir que corresponde a source,
   revision e metadata_sha256 do plano. Um hash recém-calculado de uma captura antiga
   não demonstra atualidade. Não trocar uma projeção científica pelo DTO exigido.
4. Adaptar as linhas já verificadas ao envelope atlas-retention-inventory/1, conforme
   o contrato, conservando PARTIAL/UNRESOLVED/NOT_ASSESSED e campos de evidência.
   Não inventar hashes, locators, origem, revisão executada, consumidor exclusivo,
   backup integral ou restauração. inventory_integrity descreve somente o subconjunto.
5. Conferir a adaptação contra os recibos privados; ancorar o hash do envelope acabado
   separadamente. delta_provenance conserva os hashes do inventário histórico e do
   recibo. O plano é ancorado por seus bytes exatos; KEEP_FULL não pode mudar no lote.
6. Associar IDs opacos de arquivos a roots/paths locais autorizados via argumentos
   explícitos; nenhuma referência científica vira path automaticamente. Somente os
   arquivos selecionados e dotados de hash serão relidos pela ferramenta.

## EXECUTE

Node 24 já disponível é suficiente; não instalar ferramentas por presunção.
Executar a partir de PROJECT_ROOT, substituindo somente os argumentos privados
confirmados no preflight. Os paths abaixo são exemplos, não destinos a descobrir:

```powershell
node tools/atlas_retention_audit.mjs `
  --plan C:/qa-privado/plan.json `
  --inventory C:/qa-privado/inventory-n02.json --inventory-sha256 HASH_N02_ENVELOPE `
  --snapshot C:/qa-privado/source-current.json --snapshot-sha256 HASH_CAPTURED_SOURCE `
  --root corpus=C:/corpus-autorizado `
  --file file01=corpus:dados/arquivo.bin
```

A API Node documentada aceita os mesmos bytes/âncoras e mapas explícitos quando um
orquestrador LOCAL já existe; não precisa gerar shell a partir de dados. CLI emite
somente stdout. Se guardar parecer, escolher saída privada nova e autorizada fora
do corpus, conferindo que não substituirá arquivo existente.

## REVIEW e saída

Verificar exit 0 para importação ou exit 2/REJECTED para recusa. Mesmo exit 0 mantém
PROPOSAL_ONLY, validation_status=PARTIAL, DELETE_AUTHORIZED=NO, removal_authorized=false,
RECOVERABLE_SPACE_UNKNOWN. Cada file_verification é limitada ao arquivo lido naquela
execução; NOT_VERIFIED não equivale a ausência ou falha científica.

Conferir invariância das fontes selecionadas, preservar as evidências aprovadas e
mapear exatamente os gaps de N01-R que permanecem. Não executar exclusão, movimentação,
limpeza, merge, release/deploy, provider ou retentativas custosas sem nova justificativa.

Handoff sanitizado ao P00: SHA/tree executados, versões, comando sem paths privados,
exit code, hash do parecer privado, contagens verificadas/pendentes, categorias de
recusa ou gaps e próximo gate. Não anexar o inventário, snapshot ou corpus privado.
