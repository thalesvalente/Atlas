# Verificação e exportação

No ambiente Atlas já instalado, sem produtor R4:

```powershell
python -I tools/verify_native_parity.py --projection D:/fonte/projection.json --package D:/pacote --expected-sha256 HASH_VERIFICADO_EXTERNAMENTE --expected-revision REVISAO_ESPERADA --summary-only --report D:/recibos/parity.json
```

O hash é dos bytes da projeção escolhida, não de JSON recanonizado. O operador
obtém os pins da custódia/recibo independente; usar o próprio pacote para escolher
o pin não prova autenticidade. A comparação usa conteúdo canônico completo e
tipos, com recusa de fonte/revisão divergentes. `--summary-only` omite os caminhos
individuais do recibo, mantendo comparação de todos e seu índice SHA-256.
O relatório deve ser novo e fora das fontes. Os arquivos permanecem somente leitura.

Em Tabelas, **CSV tipado das linhas** exporta todas as linhas selecionadas pelos
filtros, inclusive fora da página visível, em `atlas-table-csv/1` (UTF-8/RFC4180).
As cinco primeiras colunas são formato, UID contextual da tabela, UID da linha,
pointer da linha e JSON original completo da linha. UIDs/pointer são strings JSON.
Cada coluna `cell:<nome JSON>` contém `{"type":"missing"}` ou
`{"type":"<tipo>","value":<token JSON original>}`. NULL, vazio, texto, arrays,
objetos e números permanecem distintos. Tokens numéricos não passam por Number.
Os envelopes e strings JSON tornam fórmulas inertes sem alterar seu conteúdo.
Use parser JSON que conserve inteiros/decimais exatos ao consumir os tokens.
Metadados completos da tabela permanecem no JSON da ocorrência/projeção; este CSV
conserva as linhas, com identidade contextual da tabela.

**CSV protegido** mantém o formato de leitura anterior e neutraliza fórmulas,
podendo colapsar tipos/ausências. JSON integral permanece a exportação principal.
O parser atual rejeita decimais que perderiam valor; não promete preservar zeros
significativos/lexemas não canônicos de novas fontes arbitrárias.

CI/HTTP não substituem Chrome real, autenticação upstream ou aceite humano.
