# Contrato LOCAL N02 — revisão offline, sem efeitos sobre fontes

## Fronteira e entradas

`tools/atlas_retention_audit.mjs` é ferramenta de manutenção separada do runtime
Atlas, executada com Node 24. Não é rota HTTP, importador científico, índice ou
mecanismo de retirada. Reutiliza o exportador e as identidades da Feature 005.

API pública:

```javascript
await auditRetention({
  planBytes, inventoryBytes, snapshotBytes,
  expectedInventorySha256, expectedSnapshotSha256,
  roots: { corpus: '/diretorio/autorizado' },
  files: { file01: { root_id: 'corpus', relative_path: 'dados/arquivo.bin' } },
});
```

Os três documentos são bytes UTF-8 (Buffer). Os dois digests são SHA-256 hexadecimal
minúsculo obtidos independentemente pelo operador: envelope N02 conferido após a
adaptação LOCAL e captura atual do DTO validado. O hash do novo envelope não é o hash
do inventário histórico nem do recibo: esses dois anchors ficam em delta_provenance.
Não são lidos de campos do próprio documento como substituto desses
argumentos. O inventário vincula também os bytes exatos do plano por `plan_sha256`.
Digest prova integridade dos bytes, não autenticidade, atualidade global ou ciência.
O operador LOCAL deve capturar o snapshot atual; fornecer novamente um hash antigo
não demonstra atualidade. A N02 não procura fontes, worktrees ou arquivos históricos.

`snapshotBytes` contém UM objeto source READY, no formato de
`/api/notebook` → `sources[i]`, capturado do leitor validado local. Conserva todos
os DTOs, campos presentes/ausentes, revision e metadata_sha256. Não usar a projeção
do produtor como substituto do DTO. O plano continua **atlas-retention-plan/1**,
version numérica 1, PROPOSAL_ONLY e DELETE_AUTHORIZED=NO, sem regravação.

Todos os UIDs do snapshot são únicos. O plano é confrontado com o resultado do
exportador F005 para os mesmos DTOs, intenções e anotações válidas da sessão:
source, revision, snapshot_key, selection_key, tipo, identidade lexical, raw_json,
linhas de tabelas, proteção e proveniência. A comparação não reconstrói lexemas
científicos por conversão numérica. A ordem de objetos JSON não tem significado;
a ordem de seleção e as strings lexicais têm. JSON com chaves duplicadas é recusado.

## Envelope do inventário, versão 1

O contrato sanitizado `ATLAS_N01_R_N02_SANITIZED/1` descreve a estrutura, e não
publica as linhas privadas. O LOCAL adapta o inventário existente para o envelope
abaixo, sem rescan integral e sem promover evidências históricas ou parciais.
Esta adaptação é explícita; não alegamos já ter importado os 684 arquivos privados.

```javascript
{
  schema: 'atlas-retention-inventory/1', version: 1,
  contract: 'ATLAS_N01_R_N02_SANITIZED/1',
  source: plan.source, snapshot_key: plan.snapshot_key,
  plan_sha256: '<sha256 dos bytes exatos do plano>',
  inventory_integrity: { status: 'VERIFIED', scope: 'OBSERVED_SUBSET_INTEGRITY' },
  validation_status: 'PARTIAL', evidence_scope: 'SCOPED_READ_ONLY',
  delta_provenance: {
    origin: 'N01_R_READ_ONLY',
    base_inventory_sha256: '<hash do inventário histórico>',
    receipt_sha256: '<hash do recibo N01-R>'
  },
  bindings: [{
    identity: plan.items[0].identity, type: plan.items[0].type,
    intent: plan.items[0].intent, file_ids: ['file01'],
    validation_status: 'PARTIAL',
    evidence_scope: 'SCOPED_RECORD_PHYSICAL_BINDING',
    dependency_status: 'UNRESOLVED', backup_status: 'NOT_VERIFIED'
  }],
  files: [{
    id: 'file01', sha256: '<hash seletivo conhecido ou null>', size_bytes: 123,
    category: 'SOURCE_ORIGINAL', consumers: [plan.items[0].identity.selection_key],
    shared: 'UNKNOWN', backup_status: 'NOT_VERIFIED'
  }]
}
```

Os campos do envelope e dos objetos mostrados são exatos, obrigatórios e sem
extensões silenciosas. `bindings` contém exatamente uma linha por item selecionado,
na ordem do plano. Identidade, tipo e intenção devem coincidir integralmente.
Um vínculo não resolvido usa `file_ids: []` e status parcial/não avaliado, mantendo
a lacuna. O inventário pode conter arquivos não selecionados; não serão abertos.

Enums:

- `validation_status` e `dependency_status`: VERIFIED, PARTIAL, UNRESOLVED,
  NOT_ASSESSED. São declarações de escopo, não comprovação de fechamento completo.
- `evidence_scope` do envelope: SCOPED_READ_ONLY ou HISTORICAL_SCOPED.
- `evidence_scope` de cada binding: DOCUMENTARY_WITNESS_ONLY,
  DOCUMENTARY_TABLE_AND_DOWNSTREAM_RELATION, SCOPED_RECORD_PHYSICAL_BINDING,
  RESOURCE_REFERENCE_CROSSWALK.
- `category`: SOURCE_ORIGINAL, UPSTREAM_INPUT, DERIVED_RESULT, SHARED_ARTIFACT,
  EXCLUSIVE_ARTIFACT, CHECKPOINT, CACHE, BACKUP, UNKNOWN_DEPENDENCY.
- `shared`: true, false ou a string UNKNOWN. `false` com mais de um consumidor ou
  categoria SHARED_ARTIFACT é contradição recusada. Compartilhamento declarado ou
  evidência insuficiente preservam a proteção correspondente.
- `backup_status`: NOT_VERIFIED ou DECLARED. Nenhum desses valores prova restauração.
- `sha256`: 64 dígitos hexadecimais minúsculos ou null, sem inventar hashes ausentes.
- `size_bytes`: inteiro seguro não negativo. IDs de arquivos/roots: 1–128 caracteres
  `[A-Za-z0-9_-]`, começando com alfanumérico. IDs duplicados são recusados.

Cada referência em `file_ids` deve existir em `files` e declarar o selection_key
como consumidor. Consumidores são identidades opacas não vazias e não são usados
para resolver nomes, caminhos ou conteúdo. A ausência de fechamento dos demais
consumidores permanece no parecer, mesmo se os arquivos selecionados tiverem hash.

## Resolução física autorizada

O inventário e o plano **não fornecem paths de filesystem**. `file_ids` são chaves
opacas; um campo `path`, `url`, `root` ou outro campo extra no inventário é rejeitado.
Referências que apareçam no JSON científico bruto permanecem texto inerte.

Somente `roots` e `files`, argumentos explícitos do chamador LOCAL/CLI, habilitam
leituras. Cada root deve ser diretório local absoluto e canônico, sem componente
symlink ou junction. Os paths dos três documentos CLI seguem a mesma fronteira.
No Windows, usar o nome físico completo, sem aliases curtos 8.3. A ferramenta recusa
divergência entre o path normalizado e realpath; não resolve links para autorizar
seus destinos. Conferir os paths do operador no preflight, sem converter referências
do inventário em autorização. Cada relative_path usa segmentos separados por `/`; `..`, `.`, segmentos
vazios, barras invertidas, caminhos absolutos/UNC, drives, ADS, URLs, nomes reservados
Windows, caracteres de controle, `%` e componentes com ponto/espaço final são recusados.
Não há fallback por nome, glob, inferência de UID ou busca recursiva.

Arquivos são abertos somente para leitura e devem ser regulares, sem symlink,
junction, hardlink ou alias físico entre IDs. A ferramenta verifica containment,
metadados antes/depois, identidade do descritor aberto, tamanho e SHA-256. Qualquer
mudança observada rejeita a execução. O snapshot não é uma trava do filesystem:
o operador deve executar sobre fontes estáveis; corridas hostis não observáveis
pelas primitivas portáveis não são uma propriedade certificada desta ferramenta.

Sem mapping ou sem hash histórico, a linha permanece NOT_VERIFIED; não se inventa
verificação física. Os mapas podem referenciar somente IDs existentes no inventário.
A ferramenta não grava, remove, move, cria diretórios, abre rede ou executa comandos.
Ela emite o parecer em stdout. Há limite de 64 MiB por documento JSON e profundidade
128; o hashing de arquivos autorizados é por blocos, não carrega o corpus na memória.

## CLI e resultado

```text
node tools/atlas_retention_audit.mjs \
  --plan /local/plan.json \
  --inventory /local/inventory-n02.json --inventory-sha256 HASH_N02_ENVELOPE \
  --snapshot /local/source-current.json --snapshot-sha256 HASH_CAPTURED_SOURCE \
  --root corpus=/local/corpus \
  --file file01=corpus:dados/arquivo.bin
```

`--root` e `--file` podem se repetir para IDs diferentes. Opções desconhecidas,
duplicadas para o mesmo ID ou sem valor são rejeitadas. Não há opção de execução,
exclusão, aplicação, limpeza, descarga de conteúdo ou escrita de relatório.

Sucesso de importação: exit 0, `schema=atlas-retention-review/1`,
`status=PROPOSAL_ONLY`, `runtime_import=VERIFIED_SCOPED`,
`DELETE_AUTHORIZED=NO`, `removal_authorized=false`,
`recoverable_space=RECOVERABLE_SPACE_UNKNOWN`. `validation_status=PARTIAL`
preserva os limites físicos, de dependências e backup. `file_verification[]` tem
status VERIFIED_CURRENT_READ ou NOT_VERIFIED; não contém paths ou bytes do corpus.
`items[]` conserva identidade, tipo, intenção e razões de proteção. Pareceres de
corpus privado permanecem LOCAL; somente fixtures e resultados sintéticos são públicos.

Recusa: exit 2, JSON `status=REJECTED`, `DELETE_AUTHORIZED=NO` e
`error.code` estável. API lança `RetentionError` com `.code`:
MALFORMED, STALE_SNAPSHOT_OR_REVISION, CONTRADICTORY_IDENTITY_OR_INTENT,
INVENTORY_INTEGRITY_UNVERIFIED, UNSAFE_PATH, EXTERNAL_LINK,
FILE_SUBSTITUTED, FILE_IDENTITY_AMBIGUOUS ou INPUT_UNREADABLE.
Erros não ecoam conteúdo nem caminhos privados. Uma recusa não grava recibo no corpus.

## Gates que permanecem LOCAL

Captura atual e âncoras independentes; adaptação das linhas privadas; vínculos ainda
não resolvidos; fechamento de consumidores compartilhados; revisão histórica
executada; cobertura e restauração de backup; medição física marginal; aceite humano.
KEEP_FULL continua obrigatório no lote N01-R já revisado. Nenhum resultado N02
autoriza retirada ou altera A01/T015 nos SHAs originais.
