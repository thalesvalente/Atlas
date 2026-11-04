# AP04 C4 — sucessor documental K por objetos Git exatos

Owner: C4/CI (P02). Escrita exclusiva nos seis paths deste pacote, sem edição dos
11 documentos K, dos 19 documentos F1/F2, dos 19 paths do reparo F2, dos pins
históricos ou de runtime. PR #14 permanece congelada. Não há merge/deploy/release.

## Contrato e DAG

O0: F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree
`1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`.
O1: P01 publica/revisa K; P02 desenvolve este harness independente da branch K.
O2: P02 vincula SOURCE-POLICY.json ao HEAD real da PR #21 e executa a matriz.
O3: revisão não autora e P03 compõem os controles, requalificando o SHA composto.
O4: aceite separado. Um run deste pacote não concede aceite de composição.

Fonte K inicialmente observada e fixada:
`508ccb257a44dc66da13d1edfec7f00ef5231d09`, tree
`854b57fe00ad9ba93177f9fd975dc2675c3751c6`, parent
`0a87fcd92002f49c9dea0d192f17aa45503be143`.
SOURCE-POLICY.json contém as quatro épocas, os 11 paths, modos 100644, OIDs e
SHA-256, o manifesto K de dez entradas e os 19 documentos históricos protegidos.
Nenhum wildcard de diretório concede autorização.

## Execução e limite de confiança

O guard original F2 continua intacto: PASS na sua época F2 e FAIL esperado em K
por paths não previstos. O novo guard não captura essa falha e a transforma em
PASS. Ele valida a época F2 com seu guard original, mantendo o SHA histórico no
recibo, e depois prova a sucessão estritamente aditiva por objetos Git K. Não
executa documentos, fixtures JSON ou proposta de schema 0.2.1.

O SHA do harness e o SHA K são separados. São rehashados os objetos commit/tree/
blob; a genealogia é linear, exata e explicitamente versionada, incluindo todos
os intermediários. São recusados paths extras, edição histórica mesmo revertida,
remoção/renomeação, symlink, executável, gitlink, aliases/travessia, manifestos
incompletos/adulterados, histórico shallow, replace refs e grafts.

O digest da política está no código, não no manifesto da autora. Os testes
validam o digest do guard antes de importar. O manifesto próprio cobre os outros
cinco arquivos, sem autoinclusão; o delta do harness também é limitado aos seis
paths declarados, com todos os paths históricos preservados.

```sh
python tests/qa/test_atlas_parity04_k_doc_ci.py --output /tmp/REGRESSIONS.json --junit /tmp/regressions.xml
python scripts/qa/atlas_parity04_k_doc_ci.py audit --source-sha 508ccb257a44dc66da13d1edfec7f00ef5231d09 --output /tmp/SOURCE.json --junit /tmp/source.xml
```

Use destinos externos graváveis apropriados ao SO. O primeiro comando reúne 44
IDs autorais; não é parecer independente. Os negativos reconstroem Git sintético
com identidades alteradas para exercitar a política sem depender apenas do pin.

## Actions e requalificação

Workflow `atlas-parity04-k-successor.yml`: Ubuntu/Windows × normal/-O, Python 3.12,
permissão contents:read e actions pinadas. Executa 44 regressões, o guard novo,
o guard F2 na época histórica, e a suíte C4 original instalada fora do checkout
K (223 IDs, zero perdas/skips). Faz readback da PR #21: drift do HEAD ou da base
é falha, não atualização automática de pin. JSON/JUnit distinguem os dois SHAs.
Nenhum continue-on-error, paths-ignore, skip ou relaxamento dos controles antigos.

A captura inicial de objetos Git, commit `c6f5da1213f2556b1d960fcc7cc314d13f46c9b2`,
run `41780668159`, foi somente transporte de fonte pública; não qualifica K.

Mudança posterior de P01 exige inspeção do novo delta/história, atualização
explícita da política C4, do seu digest e do pin de teste, novo manifesto, commit
e matriz completa. Não reutilizar o PASS de `508ccb2` para outro SHA.

## Gates ainda separados

O resultado deste workflow é `C4_K_SOURCE_CI_PASS_NOT_COMPOSITION_ACCEPTANCE`.
Os workflows antigos da consumidora continuam executando o guard F2 congelado;
seus FAILs não são escondidos nem contam como PASS. P03 precisa consumir este
harness por composição explícita e qualificar o SHA composto sem simplesmente
substituir os pins dos controles ou editar os documentos K. Esta PR não faz essa
integração nem declara que todos os checks legados ficaram verdes.

Sem CI terminal real, revisão independente comprovada, HEAD final P01 confirmado
e composição qualificada: `C4_K_SUCCESSOR_BLOCKED_EXACT`. Não confundir esta
limitação com falha da baseline ou autorização ARC-09. Descriptor 0.2.0 continua
o contrato aprovado; 0.2.1 é somente proposta. Nenhuma aprovação científica.

Subagentes nativos: NATIVE_SUBAGENTS_NOT_AVAILABLE. Validação autoral sequencial.
Spec Kit: assets existentes lidos; preflight com seleção efêmera de feature.
CLI specify indisponível no container: NOT_RUN, nenhuma instalação local feita.
