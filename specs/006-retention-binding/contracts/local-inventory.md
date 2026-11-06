# Interface LOCAL da N02

## Invocação

```text
python -B -m tools.atlas_retention_binding --plan <plano.json> --plan-sha256 <sha256> --inventory <base.json> --inventory-sha256 <sha256> --root "corpus=<diretório-absoluto>"
```

A CLI recebe o JSON original da Feature 005. Para complementos, repita `--inventory` e `--inventory-sha256` na mesma ordem, do segmento-base ao atual. O SHA-256 de cada documento é calculado sobre os bytes exatos, inclusive whitespace e terminador de linha. A confiança vem de o operador obter esses pins por um canal autenticado, separado dos documentos apresentados ao verificador. Use os pins do plano exportado e da cadeia atual autorizada. Um digest fornecido junto com bytes de origem desconhecida só prova integridade relativa. Produtor e evidência são identificadores opacos da proveniência registrada nesse canal.

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
      "coverage": "PARTIAL",
      "files": ["f1"]
    }
  ],
  "backups": []
}
```

- `source` replica exatamente ID, revisão e digest da fonte do plano. Use os UIDs e tipos do snapshot Native View validado. A chave `source_key` é omitida quando ausente no exportador.
- `raw_sha256` é o SHA-256 dos bytes UTF-8 da string `raw_json` do DTO original. Preserve os lexemas. Em tabelas inclua `table_rows_sha256` sobre a matriz ordenada `[[uid, ordinal, raw_json], …]` das linhas originais, codificada como JSON compacto UTF-8 sem escapes ASCII extras. Uma tabela vazia usa a matriz `[]`.
- `files` em cada vínculo é a lista de IDs de arquivos primários comprovadamente associados ao DTO. Um ID pode ser referenciado por vários DTOs. Um arquivo físico aparece uma única vez, mesmo se houver vários consumidores. IDs de arquivo e aliases de raiz são tokens ASCII minúsculos com até 64 caracteres, começando por letra e contendo letras, dígitos, hífen e sublinhado.
- `coverage` é `PARTIAL` ou `COMPLETE` por vínculo. `dependency_scope` é `UNKNOWN` ou `COMPLETE`. Declare escopo completo somente com evidência de todos os dependentes dos primários, inclusive DTOs fora do lote, e todos os vínculos completos. Um vínculo completo tem pelo menos um arquivo. A CLI verifica a coerência da declaração e a presença dos arquivos selecionados. A cobertura do universo depende da evidência autenticada da N01-R.
- Cada backup opcional tem a forma `{"primary":"f1","copy":"f2","independence_evidence":"local-backup-proof"}`. A cópia consta em `files` sob outra raiz, com tamanho e digest idênticos e sem uso como primário. A CLI verifica os bytes e exige volumes distintos para considerar a evidência de independência. Volumes distintos, por si, não provam domínios de falha independentes. A referência de evidência é responsabilidade do operador.
- Um segmento complementar aponta em `parent_sha256`NaN`.`, `..`, barras invertidas, caracteres de controle ou ponto/espaço final. Raízes explícitas são disjuntas e apontam para diretórios reais. As referências do plano, inclusive artefatos e dependências declarados no DTO, ficam como texto.
- SHA-256 usa 64 dígitos hexadecimais minúsculos. JSON exige chaves únicas. Cada documento pode ter até 128 MiB e uma cadeia pode ter até 32 segmentos e 256 MiB somados. Uma revisão nova exige novo inventário-base e novo plano.

## Saída

`BOUND_READ_ONLY` com código 0 indica que o lote fornecido foi vinculado às provas aceitas. `REJECTED` com código 2 traz apenas um código de erro e descarta resultados parciais. O resultado usa índices da seleção e IDs opacos de arquivo, sem os caminhos físicos ou JSON original. `BLOCKED` identifica impedimentos por item. `REVIEW_ONLY` indica que um item com intenção explícita e evidências suficientes pode ser encaminhado a revisão humana. Ambos mantêm `DELETE_AUTHORIZED=NO` e `removal_authorized=false`.

Os bytes lógicos são a soma dos primários distintos efetivamente verificados. Bytes protegidos são o subconjunto coberto pelas proteções e lacunas do relatório. `logical_complete` indica cobertura dos vínculos selecionados. A estimativa de espaço é `RECOVERABLE_SPACE_UNKNOWN` quando não há prova de espaço liberável. Um lote completo cujos arquivos estão todos protegidos por KEEP_FULL ou baseline tem zero bytes potencialmente recuperáveis dentro da proposta.

## Limites de resolução

Linux x86-64 e arm64 requerem kernel com `openat2` e `/proc/self/fd`. Use um filesystem local com identidade e metadados estáveis. Windows requer volumes locais com suporte a identidade de arquivo e informação por handle. Symlinks e reparse points são recusados em qualquer componente. A leitura é pontual, direcionada por vínculos, sem varredura. Use conta com acesso de leitura, volumes estáveis e política de timestamps do host adequada ao acervo. O relatório não é um lock persistente, uma prova de backup restaurável ou uma autorização operacional.
