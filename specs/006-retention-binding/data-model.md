# Modelo de dados

- **Snapshot** tem ID de fonte, revisão e SHA-256 dos metadados. A chave de seleção acrescenta UID, tipo do DTO e lexema de `kind` para registros.
- **Vínculo** ancora UID, tipo do DTO, chave de origem quando presente, SHA-256 lexical do DTO e, para tabelas, SHA-256 das linhas ordenadas. As referências ligam esse DTO a arquivos inventariados. A cobertura pode avançar de parcial para completa.
- **Arquivo** tem ID opaco, alias de raiz, caminho relativo, bytes lógicos e SHA-256. O relatório deduplica por ID e recusa aliases físicos.
- **Cópia** liga um arquivo primário a outro arquivo de mesmo conteúdo sob outra raiz. Evidência da cópia e separação de volume são checadas na leitura.
- **Segmento** aponta para o digest do anterior e registra produtor e referência de evidência. O escopo de dependências só avança de desconhecido para completo.
