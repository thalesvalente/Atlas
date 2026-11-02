# Native View 1 — conteúdo de apresentação, não protocolo científico

Um pacote RO-Crate 1.3 / Caderno 0.1.0a1 existente contém Files de `encodingFormat=application/vnd.atlas.native-view+json`, com cp:sha256 e contentSize obrigatórios. Não há novo @context nem alteração do SDK. O viewer lê somente esses Files explicitamente incluídos no pacote fixado na CLI.

Cada chunk: `{format:"atlas-native-view",version:"1",revision:string,ordinal:integer,entries:[...]}`. Ordinais contíguos, revisão única. Entradas têm uid único derivado de coleção/posição, kind (record/node/relation/table/row/asset/collection), group, title, native_id/source_key/parent_key opcionais, fields como pares nome/texto/tipo e raw_json com JSON original. Linhas têm table_uid e cells textuais com tipo/ausência explícitos. Nenhum uid é identidade científica. Conteúdo desconhecido continua em collection/raw_json. O consumidor não reinterpreta IDs nulos nem status desconhecidos.

Manifesto do root declara revision e entryCount por namespace de apresentação. Limites: metadata2MiB, File8MiB, bytes32MiB, 100000 entradas, 10000 nós. Falhas de quota, formato, digest, ordinal, duplicidade ou revisão invalidam a fonte inteira, nunca truncam dados. UTF-8 e JSON finito sem chaves duplicadas. Conteúdo original preservado em strings JSON para evitar arredondamento em JavaScript.

GET /api/notebook não aceita path ou URL do cliente. Retorna fontes por source_id, metadata_sha256, revisão, estado e entries. GET /notebook entrega apenas assets do produto. Sem upload, HTML importado, scripts remotos, iframe, acesso automático a links ou autoridade de ciência. Fontes não nativas continuam válidas no viewer de protocolo existente.

A exportação é local e exige escolha explícita do produtor/Caderno. O pacote deriva dos valores retornados pela API original e não certifica autenticidade da ciência ou segurança de host adversarial. Navegação de parentes usa chaves estruturais únicas no grupo; repetições/ciclos permanecem observáveis e não autorizam fusão de entidades.
