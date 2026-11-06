# Interface LOCAL da N02

## Invocação

```text
python -B -m tools.atlas_retention_binding --plan <plano.json> --plan-sha256 <sha256> --inventory <base.json> --inventory-sha256 <sha256> --root "corpus=<diretório-absoluto>"
```

A CLI recebe o JSON original da Feature 005. Para complementos, repita
`--inventory` e `--inventory-sha256` na mesma ordem, do segmento-base ao
atual. O SHA-256 de cada documento é calculado sobre os bytes exatos,
incluindo whitespace e terminador de linha. A confiança depende de o
operador obter os pins do plano e da cadeia atual por canal autenticado.
Um digest recebido de origem desconhecida só demonstra integridade
relativa. Produtor e evidência identificam a proveniência nesse canal.

## Envelope do inventário

```json
{
  "schema": "atlas-retention-inventory/1",
  "source": {
    "id": "invented-source",
    "revision": "SYNTHETIC_R1",
    "metadata_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "parent_sha256": null,
  "provenance": {
    "producer": "synthetic-operator",
    "evidence": "local-attestation-001"
  },
  "dependency_scope": "UNKNOWN",
  "files": [
    {
      "id": "f1",
      "root": "corpus",
      "path": "dados/file.bin",
      "bytes": 0,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ],
  "bindings": [
    {
      "uid": "view:4",
      "dto_kind": "record",
      "source_key": "sample-key",
      "raw_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "validation_status": "VERIFIED",
      "evidence_scope": "PHYSICAL_BINDING",
      "coverage": "PARTIAL",
      "files": ["f1"]
    }
  ],
  "backups": []
}
```

- `source` replica ID, revisão e digest da fonte do plano. Use os UIDs
  e tipos do snapshot Native View validado. Omita `source_key` quando
  ausente no exportador.
- `raw_sha256` é o SHA-256 dos bytes UTF-8 da string `raw_json` do DTO
  original. Preserve os lexemas. Em tabelas inclua `table_rows_sha256`
  sobre a matriz ordenada `[[uid, ordinal, raw_json], …]` das linhas
  originais, como JSON compacto UTF-8 sem escapes ASCII extras. Uma
  tabela vazia usa `[]`.
- Em cada vínculo, `files` lista IDs de arquivos primários comprovadamente
  associados ao DTO. Um ID pode ser referenciado por vários DTOs. Use um
  ID por arquivo físico, mesmo se houver vários consumidores. IDs e aliases
  de raiz são tokens ASCII minúsculos com até 64 caracteres, começando por
  letra e contendo letras, dígitos, hífen e sublinhado.
- Cada vínculo atesta `validation_status: VERIFIED` apenas para os arquivos
  listados. Use `evidence_scope: PHYSICAL_BINDING` para vínculo físico de
  execução ou artefato e `DOCUMENTARY_WITNESS` para bytes documentais.
  Um testemunho documental exige cobertura parcial e mantém bloqueio.
- `coverage` é `PARTIAL` ou `COMPLETE` por vínculo. `dependency_scope`
  é `UNKNOWN` ou `COMPLETE`. Declare escopo completo com evidência de
  todos os dependentes dos primários, inclusive DTOs fora do lote, e
  vínculos completos. Um vínculo completo tem pelo menos um arquivo.
  A CLI verifica a coerência e a presença dos arquivos selecionados.
- Cada backup tem `primary` e `copy`. A cópia consta em `files` sob
  outra raiz, com tamanho e digest idênticos e sem uso como primário.
  Acrescente `independence_evidence` e `restore_evidence` quando houver
  referências autenticadas a evidências de independência e restauração.
  Para revisão, a CLI exige bytes verificados, ambas as referências e
  volumes distintos. Independência de domínio de falha e restauração
  são atestadas pelo operador.
- Um complemento aponta em `parent_sha256` para os bytes exatos do segmento
  anterior. Acrescente arquivos, backups e UIDs novos. Um UID anterior pode
  reaparecer para estender um vínculo parcial com a mesma identidade e um
  superconjunto de arquivos, para elevar seu escopo documental com prova
  física ou para selar a cobertura. O escopo completo sela os vínculos
  primários. Complementos de independência ou restauração de uma cópia
  são aceitos mantendo as referências anteriores.
- Caminhos usam componentes relativos separados por `/`, com grafia NFC.
  Nomes de dispositivo, ADS, componentes vazios, `.`, `..`, barras
  invertidas, caracteres de controle e ponto ou espaço final são recusados.
  Raízes explícitas são disjuntas e apontam para diretórios reais. As
  referências do plano, inclusive artefatos e dependências, ficam como texto.
- SHA-256 usa 64 dígitos hexadecimais minúsculos. JSON exige chaves únicas.
  Cada documento tem até 128 MiB. A cadeia tem até 32 segmentos e 256 MiB
  somados. Uma revisão nova exige novo inventário-base e novo plano.

## Mapeamento da N01-R

O recibo `ATLAS_N01_R_N02_SANITIZED/1` descreve estrutura e lacunas.
A entrega LOCAL projeta locators exatos confirmados pela N01-R em referências
por raiz e liga cada um ao DTO da mesma revisão. `inventory_integrity`
corresponde aos pins externos. `delta_provenance` corresponde à cadeia
`parent_sha256` e às referências de evidência. Um testemunho documental
vincula seu próprio arquivo com cobertura parcial. Uma relação downstream
ou locator alternativo exige evidência antes de entrar como vínculo físico.
Enquanto houver lacunas no fechamento de consumidores ou vínculos, use
`dependency_scope: UNKNOWN`. Cópias verificadas em escopo seletivo exigem
prova adicional para preencher `restore_evidence`.

## Saída

`BOUND_READ_ONLY` com código 0 indica vínculo do lote às provas aceitas.
`REJECTED` com código 2 traz o código de erro e descarta resultados parciais.
O resultado usa índices da seleção, IDs opacos de arquivo e os pins do
plano e da ponta do inventário. `BLOCKED` identifica impedimentos por item.
`REVIEW_ONLY` indica que um item com intenção explícita e evidências
suficientes pode ser encaminhado a revisão humana. Ambos mantêm
`DELETE_AUTHORIZED=NO` e `removal_authorized=false`.

Os bytes lógicos somam primários distintos efetivamente verificados.
Bytes protegidos são o subconjunto coberto pelas proteções e lacunas.
`logical_complete` indica cobertura dos vínculos selecionados. A estimativa
é `RECOVERABLE_SPACE_UNKNOWN` quando falta prova de espaço liberável. Um
lote completo cujos arquivos estão todos protegidos por KEEP_FULL ou baseline
tem zero bytes potencialmente recuperáveis dentro da proposta.

## Limites de resolução

Linux x86-64 e arm64 requerem kernel com `openat2` e `/proc/self/fd`.
O adaptador admite ext2/3/4, Btrfs, XFS, tmpfs e OverlayFS locais. Windows
requer volumes locais com suporte a identidade de arquivo e informação
por handle. Symlinks e reparse points são recusados em qualquer componente.
Use a grafia real de cada componente. A leitura é direcionada por vínculos,
com reconferência de metadados ao concluir o lote. Use conta com acesso
de leitura, volumes estáveis e política de timestamps do host adequada ao
acervo. O resultado é pontual.
