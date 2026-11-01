# AP04-F4-L1-LOCAL-REAL-READER-PROOF-02 — executar leitor protegido no acervo real autorizado

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente obrigatório: CODEX LOCAL no Windows com acesso ao host e arquivos privados. NÃO CHAT.**  
**Raciocínio recomendado: Extra High**, selecionado manualmente pelo operador.  
**Git:** usar checkout Atlas existente; não criar worktree/clone, não trocar branch compartilhada automaticamente, não resetar/limpar arquivos, não alterar R4 ou o corpus.  
**Resultado:** `F4_L1_LOCAL_REAL_READER_QUALIFIED_SCOPED` somente com fonte autorizada, processamento v5 REAL, controle OS medido, fidelidade F1 e revisão independente. Se faltar qualquer predicado: `F4_L1_BLOCKED_EXACT` com prova mínima, sem promover G4.

## 1. Gates de entrada que não podem ser inferidos

- F4 C2-D deve fornecer SHA final da PR Draft #18, handoff e **provas de parser real + supervisor/sandbox** com status `C2_D_REAL_V5_READER_READY_FOR_HOST_PROOF`, não apenas componente sintético v5. Conferir commit/tree/parent e que CLI/reader reais deixaram de aceitar bypass `--synthetic-fixture` com corpus.
- C2-K: se nova semântica source-key for necessária, obter **aprovação humana versionada ARC-09** e implementação compatível com as chaves do legado, sem inventar native IDs. Se ainda pendente, permitir inspeção/diagnóstico read-only, mas não declarar árvore real validada ou G4 completo.
- F4-L0: usar estrutura/recibos privados ou handoff sanitizado já verificados; se houve divergência de revisão, exigir ajustamento do parser e testes públicos antes da qualificação.
- Fonte: a aprovação de transferir CÓDIGO R4 privado ao Atlas público **não autoriza automaticamente leitura de qualquer arquivo do disco para F4**. A mensagem de início da L1 deve identificar ou reautorizar EXATAMENTE o conjunto de arquivos F1/recibos já pinados e o propósito read-only de prova. Sem permissão suficiente, `F4_L1_SOURCE_NOT_AUTHORIZED`, sem abrir arquivos. Não varrer H:/G:/outros drives, nem supor paths de outros chats.
- C0 adendo reader003 `d498504cd2c4d230088f86e04e55624bbe32df79`, F2 descriptor `c3ea1e82938fd61cc5a22fee973352715a5bb527`, F1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, AP04-POR-v1.0-draft, ARC-01–09 e ADR-0003 v0.2 APPROVED_SCOPED.

## 2. Ownership da bancada

Fonte R4, dados originais, builds antigos, F1 recibos, software legado e Caderno são SOMENTE LEITURA. Não executar `atlas.build`, pipeline R4, scripts HTML, JS do velho viewer, provider/inferência, instalação/rebuild amplo, varredura, limpeza ou migração. Não modificar ACL dos originais, políticas Windows, firewall ou permissões do host para contornar isolamento.

Executar ferramenta externa C2-D por **SHA fixado** em ambiente Python isolado existente/autorizado, sem instalar no Conda default ou modificar repos compartilhados. Não criar clone/worktree; usar Git existente e `git show`/pacote já qualificado se necessário. Abrir exclusivamente os handles allowlisted, previamente aprovados, sob política OS instalada e verificada.

**Scratch de descriptor** privado, efêmero e fora do checkout e da fonte; **recibos privados** na raiz `.local/atlas-parity04-f4-l1/` ignorada, somente se autorizada e gravável. Nunca usar pasta temporária genérica que permita sobrescrever fontes. Não enviar HTML, descriptor, hashes privados, IDs ou RF literal ao GitHub público.

Subagentes nativos reais quando disponíveis: A identidade/fonte, B segurança/limites, C revisão independente somente leitura, coordenador único writer de recibos. Se não disponíveis, continuar prova segura e marcar QA pendente, não afirmar revisão independente inexistente.

## 3. Prova da origem real e semântica

1. Antes da leitura, confirmar paths exatos F1 (captura, pointer e HTML já qualificado) e dados de hash/size/mtime/identidade existentes nos recibos privados. Se a fonte mudou desde F1, abortar `SOURCE_DRIFT`, jamais editar/regerar para coincidir.
2. Validar de forma INERTE o bloco `script#data[type=application/json]` e `r4-experiment-viewer-v5` do arquivo já exportado. Não seguir pointers/URIs a menos que o ALVO também esteja autorizado; não executar scripts para descobrir JSON.
3. Executar **a CLI de produção protegida C2-D**, jamais `--synthetic-fixture` com dados reais, com limites nativos comprovados. Se o ambiente não suportar Job/FS/network confinement, registrar `HARD_BUDGET_UNVERIFIED`/`OS_ISOLATION_UNVERIFIED` e NÃO processar dados reais.
4. Conferir inércia: zero execução R4/JS, zero requests de rede, nenhum acesso fora dos handles autorizados, nenhuma alteração da origem, scratch fora do checkout, TTL≤3600 e publicação atômica. Negativos de worker bloqueado, OOM, negação FS e socket devem ser demonstrados com fixtures inventadas; não fazer ataques de indisponibilidade sobre arquivos de produção.
5. Descriptor deve validar JSON Schema Draft 2020-12 0.2.0 ou sucessor aprovado e invariantes semânticas. Campos `key/ui_id/native_id`, parent_key/arestas tipadas, originais x derivados e 858 ligações explícitas da F1 devem ser confrontados em recibo privado. Se houver gaps por contrato, não falsificar `RESOLVED`; separar `SOURCE_STRUCTURAL_KEY_GAP` de ausência real de referência.
6. Reconciliação selecionada F1 (NÃO população global): records=159, lineage_nodes=2911, lineage_edges=1595, tabelas=5 com linhas `[39,85,28,0,0]` (152), 28 RF não admitidas, 4 tabelas sem record_id resolúvel, Run externo isolado, 22 endpoints null, 75 relações unresolved, 50 colisões, grupos repetidos. **Não somar records+lineage nodes como se fossem a mesma entidade**; descriptor pode conter ambas as coleções como nós distintos, contagem resultante deve ser explicitada.
7. Comparar **em privado** a linha RF original G1 (ID, núcleo/módulo, Nome, Descrição, Critérios, categoria ausente) por tipo/valor/posição e vínculo documentado; diferença dispara `RF_LITERAL_DRIFT`, não normalizar texto ou arredondar. Preservar `MISSING` ≠ null ≠ vazio ≠ zero; metadata e URI não implicam admissão/aprovação científica.
8. Hash/size/mtime/identidade antes/depois de cada fonte realmente aberta; nenhum arquivo original escrito. Comparar com F1 e registrar apenas contagens públicas após revisão de privacidade.

## 4. Oráculos de host e limites

**Memória:** prova nativa de limite de 256 MiB com métrica definida e controle OS consultado, ataques em worker inventado; não afirmar teto do browser nem substituir por memory_profiler. **Prazo:** 30 s elapsed com supervisor externo e encerramento do Job/descendentes em timeout, falha atômica. **Filesystem:** fonte RO e scratch RW somente; teste de escrita na fonte inventada negada pelo SO; leitura fora da allowlist e socket negados pelo OS, não só pelo próprio Python. **TOCTOU:** handle e path/ancestrais rechecados antes/depois; no unreconciled drift. Qualquer falha=HOLD, não ignorar.

Receipts públicos jamais contêm paths Windows, SHA de dados, RF literal, nomes/dados de cliente, screenshots privados ou stdout de parser. Recibos privados incluem `SOURCE-IDENTITY.private.json`, `FORMAT-AND-LINEAGE.private.json`, `RF-LITERAL-CHECK.private.json`, `OS-SECURITY.private.json`, `NEGATIVE-TESTS.private.json`, `G4-RECEIPT.private.json`, `INDEPENDENT-REVIEW.private.md`, `HANDOFF.private.json`, `MANIFEST.sha256`. Saída sanitizada liberada: `RESULT.sanitized.md`, `HANDOFF.sanitized.json` e `RESULT-REVIEW.sanitized.md`.

## 5. Encerramento seguro e publicação

A revisão independente C precisa comprovar a origem e o descriptor REAL, hard limits, integridade, campos RF, lacunas e privacidade sem autoria da ferramenta. Se L0/source real exigir código novo, devolver somente CONTRAEXEMPLO INVENTADO e diagnóstico sanitizado ao owner C2; não editar o parser diretamente no host sem nova qualificação Git/CI.

Publicar o handoff sanitizado somente se aprovado para publicação; branch QA pública exclusiva criada por publisher separado depois de validar conteúdo. Guardar privados apenas no host, nunca em comentário da PR #18.

**Sucesso:** `F4_L1_LOCAL_REAL_READER_QUALIFIED_SCOPED` = amostra real autorizada, fidelidade original, segurança SO efetiva, originais iguais e revisão independente; ainda NÃO é G6 browser/paridade do acervo global e não altera ADR/planos.
**Bloqueio:** `F4_L1_BLOCKED_EXACT`, com código, evidência privada e próximo ato mínimo, preservando os originais.

Sem F5, merge main, release, deploy, promoção, migração, limpeza, alteração R4 ou ampliação de permissão por inferência.

**END-OF-AP04-F4-L1-PROMPT — COMPLETE**
