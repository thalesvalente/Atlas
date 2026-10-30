# ATLAS-PARITY04-DOC-CI-PUBLISH-REVIEW-03 — aplicar o reparo ORIGINAL e qualificar a PR #14

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** Codex LOCAL com acesso de escrita ao checkout Atlas existente, GitHub/GitHub Actions; alternativa CHAT apenas com capacidades reais de escrita Git e revisão independente.  
**Esforço:** operador seleciona Max (Extra High como alternativa); não declarar observação do seletor se não houver.  
**Destino único de correção:** `thalesvalente/Atlas`, PR Draft #14, branch `docs/atlas-parity04-plan-of-record-20261030`.  
**Origem dos originais:** `evidence/atlas-ap04-ci-repair-recovery-20261030`, diretório `docs/missions/atlas-parity-04/ci-repair-recovery-20261030/originals/`.  
**Resultado-alvo:** `AP04_DOCUMENTATION_CI_QUALIFIED` somente se todas as provas reais fecharem.

## Entradas congeladas

- C4: SHA `72d9b94e613a57c82a5afd309796f44b271e2185`, tree `0a622663ca40232d6143659f82cfe9ce43702e90`.
- PR #14 original: SHA `c25d37998dac7174067a2819391f3af1625f96dc`, tree `e6eacdd02a329f88bc0dd656523b84a8fec9217e`.
- Original patch: SHA-256 `d25540bce2a90dbf099ca38b82528b645ea49c92fd86d04438d5f1b7a58b83b8`; Git blob `d6ab785bc75634f8248e525580d01cf25b809d18`.
- Original ZIP: SHA-256 `5788215d2267902988e141fa6db5a9434564b18204356a3a6d80a3dd2a883752`; Git blob `2dd4fc9f1f3ca425f00b3fb16de1ae1c4d5cb158`.
- Contrato AP04-POR-v1.0-draft; ADR-0003 permanece apenas PROPOSTA; ARC-01–09 vinculantes.
- `originals/APPLY-INSTRUCTIONS.md` contém o roteiro original; siga-o junto aos gates abaixo.

## Fase 0 — Preflight por identidade

1. Leia `AGENTS.md`, Spec Kit e os contratos AP04 aplicáveis.
2. Confira que `git remote get-url origin` corresponde a `thalesvalente/Atlas`; faça somente fetch das duas branches existentes e não crie worktrees/clones.
3. Confirme checkout limpo, branch atual e HEAD; se a PR #14 avançou, reconcilie por ancestry/diff e **não aplique cegamente**.
4. Recupere o patch do blob Git por bytes, sem redirecionar `git show` usando um PowerShell que possa transcodificá-lo. Em Python: `Path(dest).write_bytes(subprocess.check_output(["git","show", ref+":"+path]))`, onde `ref` é a ref remota exata da branch de evidências e `path` o caminho do patch acima. Grave no diretório ignorado `.local` do próprio checkout, após verificar permissão.
5. Confira SHA-256 e blob SHA-1. Compare o patch com o ZIP quando necessário; `ORIGINALS-VERIFIED.json` já documenta a igualdade, mas a execução deve conferir o objeto baixado.

## Fase 1 — Aplicação e testes focais

1. Trabalhe **somente** na branch existente da PR #14. Exija HEAD original `c25d379...` e checkout limpo, ou registre e trate desvio por procedimento de aprovação de plano.
2. Execute `git apply --check --index <patch-verificado>`, depois `git apply --index <patch-verificado>`; `git diff --cached --check`; compare exatamente 19 paths, 5 modified e 14 added, sem tocar nos nove documentos AP04 originais.
3. Revise o guard inteiro e roteamento P03/C4; auditoria P06 congelada continua estrita. Sem exceções genéricas em `docs/**`, `scripts/**`, workflows, ADR, fixtures ou manifests.
4. Compile os três módulos Python previstos no pacote, rode as contraprovas (17 normal e 17 `-O` se o patch permanecer intacto), valide YAML/JSON e testes negativos de symlink, modo, pin, branch parecida, alteração transitória/revertida, ADR/protocolo/fixture/runtime.
5. Qualquer alteração em relação ao patch original deve ser justificada e receber novos hashes e testes próprios. Não atribuir resultados de testes antigos a bytes modificados.

## Fase 2 — Publicação e CI do SHA novo

1. Faça commit normal e push fast-forward na **mesma** branch/PR Draft #14. Não rebase, squash, force-push, merge para main nem nova PR.
2. Exija novas execuções no SHA publicado: AP04 dedicado; P06; P03; C4; ATLAS021; Spec Kit; Windows/Ubuntu, normal e `-O`, zero skips e browsers reais requeridos.
3. Confira os 168 IDs herdados C4 e os artefatos ligados ao SHA; não use os runs históricos como prova do novo HEAD.
4. Use até três subagentes nativos reais quando disponíveis, ownership exclusivo; o revisor independente não pode ter autoria do delta. Sem subagente, faça testes possíveis, mas não alegue revisão independente.
5. Publique recibos por SHA após o resultado. **Qualquer commit de recibos cria outro SHA que exige sua própria CI e revisão**; não feche circularmente a própria identidade.

## Fase 3 — Conclusão e confronto obrigatório

- Confronte o resultado com `AP04-POR-v1.0-draft` e o registro de decisões D-001–D-020.
- Declare `AP04_DOCUMENTATION_CI_QUALIFIED` somente se Git/CI/revisão exatos estiverem comprovados no SHA final.
- Caso contrário, `AP04_DOC_CI_BLOCKED_EXACT` com código já publicado, falha específica e menor próximo ato.
- Não iniciar AP04 F1–F6; sem alteração do R4, fontes privadas, HL7/FHIR, Caderno, worktrees, migração, limpeza, merge, release, deploy, promoção ou ciência.

## Persistência obrigatória

Artefatos públicos, prompts, patches, testes e recibos devem estar **no Git**, vinculados a branch, commit e SHA. Não dependa de download manual de outros chats. Privados permanecem em armazenamento privado autorizado, com referência sanitizada e hashes. Esta branch de evidências não é a PR #14; NÃO aplique o patch nela.