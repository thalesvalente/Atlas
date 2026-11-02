# Modelo de apresentação

Source: source_id da CLI, metadata digest, revision do produtor, status READY/INVALID/UNAVAILABLE/UNSUPPORTED; sem persistência nova no Caderno.
Entry: uid de apresentação por ocorrência, kind e group, título textual, native_id distinto de source_key, parent_key opcional, status/data/família declarados, fields textuais e raw_json fiel ao valor original.
Table: entry kind=table com uid; Row: kind=row com table_uid, posição original, cells rotuladas por chave/tipo/texto/ausência; table metadata não funde rows. Missing é chave ausente; null é valor presente nulo.
Relation: entrada original inteira e endpoints declarados; aresta não resolvida não ganha destino arbitrário. Asset: referência textual, disponibilidade declarada separada de acesso; nenhum fetch de URI.
Collections desconhecidas: preservadas como entries collection, sem inferir semântica. Revisão/mudanças invalidam seleção, jamais mesclam fontes por IDs iguais.
