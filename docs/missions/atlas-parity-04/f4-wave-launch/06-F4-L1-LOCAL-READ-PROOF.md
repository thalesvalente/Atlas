# AP04-F4-L1-LOCAL-READ-PROOF-01 — comprovação LOCAL do leitor externo O1

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** Codex LOCAL / Work Local, Windows, workspace real autorizado (não CHAT).  
**Esforço:** Extra High recomendado, selecionado MANUALMENTE pelo operador; nível efetivo não observável = UNVERIFIED.  
**Repositório canônico:** `thalesvalente/Atlas`; **não criar worktrees, clones ou branch de produto**, não alterar checkout compartilhado automaticamente.  
**Pré-requisito:** leitor C2 `F4_C2_EXTERNAL_READER_READY_FOR_LOCAL_QUALIFICATION` publicado por SHA, com código/hashes/testes. Resultado `F4_L1_LOCAL_READER_QUALIFIED_SCOPED` se fonte e segurança forem efetivamente verificadas; caso contrário `F4_L1_BLOCKED_EXACT`.

## Autorização do acervo — gate obrigatório

A autorização histórica da F1 era **exclusiva para F1/G1**, não transfere automaticamente permissão para esta fase. **Antes de ler qualquer arquivo legado**, solicitar/constatar autorização explícita NOVA do operador para F4-L1, com **arquivo(s) ou raiz exata**, operação read-only e limites. Não presumir que caminhos históricos do R4 ou 70+GB estejam autorizados. Se faltar autorização, entregar `F4_L1_SOURCE_NOT_AUTHORIZED`; não varrer drives em busca de substitutos.

A operação deve priorizar a projeção legada que F1 já qualificou, **somente quando expressamente reautorizada para esta missão**. Os recibos F1 privados no host são referência de identidade e comparação, não dados a publicar.

## Limites de ambiente e ownership

Usar checkout Atlas existente, somente leitura quanto a Git/produto, confirmar root/HEAD/status/worktrees; não fazer git switch, reset, clean, checkout extra ou instalação no Conda default. Materializar **apenas os arquivos públicos versionados do C2 por `git show`/GitHub SHA** na pasta scratch autorizada, sem clonar repositório nem criar outra worktree; não executar código remoto não verificado. Não copiar o leitor Windows suspenso, não importar R4 nem chamar pipeline produtor/HTML scripts.

**Raiz de saída exclusiva privada:** `<PROJECT_ROOT>/.local/atlas-parity04-f4-l1-reader/`, ignorada no Git. Um único probe de criação/leitura/remoção ali, somente se workspace realmente gravável. Se negado, `WORKSPACE_WRITE_BLOCKED`, sem alterar ACL/sandbox ou mudar root. Fonte(s) e recibos F1 são somente leitura. Coordinator único writer de recibos, agentes A integridade, B formato/literais, C revisão independente somente leitura, quando nativos reais disponíveis; sem agentes não simular.

## Provas reais mínimas do O1

1. Confirmar arquivo exato, allowlist, tamanho/mtime/hash antes da leitura, permissões e se há symlink/reparse/host path não permitido. Usar quotas do F2/C2; sem glob/recursão/novas fontes.
2. Executar **somente ferramenta externa C2** sobre projeção autorizada já existente, parser HTML/JSON inerte sem JS, sem rede/servidor, scratch temporário, fonte intacta. Produzir descriptor privado `atlas-legacy-presentation` 0.2.0, validado por JSON Schema Draft2020-12 e invariantes semânticas; se formato não suportado, `SOURCE_FORMAT_UNSUPPORTED` com menor campo/schema necessário, não reconstruir parser R4 no Atlas.
3. Conferir **contagens comparáveis ao snapshot F1**, não presumir que total do legado é igual a F1. F1 observou 159 records, cinco tabelas, 152 linhas, 2911 lineage nodes/1595 edges, 858 parent keys resolvidos, 28 RF não admitidas, quatro tabelas sem record_id, um Run isolado, null endpoints, unresolved e colisões. Se a fonte atual diferir, `SOURCE_DRIFT` com prova privada; não ajustar dados para passar. A linha RF literal deve conservar ID/descrição/critério quando existentes, categoria original MISSING e vínculos declarados, sem divulgar seu valor publicamente.
4. Verificar fonte/snapshot/ocorrência, todos os nós e tabelas importados sem truncamento, gaps preservados, `native_id=null` sem promoção, File ≠ produto, UNKNOWN_UPSTREAM e global_total desconhecido. Nada de criar caminho contínuo árvore→RF se não existe.
5. **Imutabilidade:** hash/tamanho/mtime antes e depois de cada fonte efetivamente lida, zero escrita em fonte/Caderno/R4; qualquer fonte alterada aborta.
6. **Segurança host:** controles allowlist, quotas 64MiB/192MiB/32MiB, TTL ≤60min, scratch externo, rejeição HTML/JS/URI/traversal/reparse/TOCTOU e prova de orçamento de abertura 256MiB/30s conforme ambiente. Se limite duro não for imposto/provado no Windows, `HARD_BUDGET_UNVERIFIED`; não declarar G4 PASS.
7. Encerrar ferramenta, descartar somente derivados próprios conforme política aprovada e **não apagar** originais ou experimentos. Evitar publicar descriptor privado, screenshot, caminho físico, ID nativo, hash da fonte ou RF literal no GitHub público.

## Recibos, privacidade e gate

Gerar apenas na pasta `.local` exclusiva:
`RESULT.private.md`, `INPUT-SCOPE.private.json`, `SOURCE-DRIFT.private.json`, `RF-LITERAL-CHECK.private.json`, `INTEGRITY.private.json`, `SECURITY-LIMITS.private.json`, `G4-RECEIPT.private.json`, `INDEPENDENT-REVIEW.private.md`, `MANIFEST.sha256` e `SANITIZED-HANDOFF.md/json` + `RESULT-REVIEW.sanitized.md`.

O resultado sanitizado pode informar apenas booleanos agregados, contagens não reidentificadoras e status por gate, sem caminhos/IDs/SHAs privados. Publicar esses arquivos sanitizados por Git-first em branch QA **separada**, criada somente depois do pin C2, com ownership exclusivo; se o LOCAL não tiver GitHub write, devolver conteúdo sanitizado a um CHAT publisher sem exigir download de ZIP do operador. Não editar a PR #15, F3A/F3B, integrador C3/C4 ou R4.

**PASS:** `F4_L1_LOCAL_READER_QUALIFIED_SCOPED` requer fonte explicitamente autorizada, descriptor real fiel, hard limits efetivamente conferidos, integridade e revisão; ainda não é browser G6/aceite científico. Se faltarem poderes do host, acesso à fonte, schema ou QA, registrar bloqueio exato e trabalho privado seguro feito. A etapa F5 só começa sob autorização específica após integração/CI e handoff F4.

**END-OF-F4-L1-PROMPT — COMPLETE**
