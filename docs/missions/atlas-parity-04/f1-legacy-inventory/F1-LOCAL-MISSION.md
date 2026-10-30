# AP04-F1-LOCAL-LEGACY-SOURCE-INVENTORY-01 — inventário real, sem migração

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** Codex LOCAL/Work Local no Windows, com workspace autorizado.  
**Nível de esforço a selecionar manualmente:** **Extra High**, ou High se indisponível. Não afirmar seleção efetiva não observada.  
**Início:** autorizado pelo operador após `AP04_DOCUMENTATION_CI_QUALIFIED`.  
**Objetivo:** `F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED`, ou `F1_BLOCKED_EXACT`.  
**Natureza:** leitura e observação de dados legados. Sem implementação de interface, adaptador ou migração.

## 1. Referências, precedência e decisões imutáveis

Antes de iniciar, leia por SHA as fontes publicadas em `thalesvalente/Atlas`:

- Plano `AP04-POR-v1.0-draft` — PR Draft #14, commit `47c94d27aeb7717eebb30804f01cd2cd33507c8a`.
- `docs/missions/atlas-parity-04/ACTION-PLAN.md`, fase **F1** e gate **G1**.
- `DECISION-REGISTER.md` (D-001–D-020), `PARITY-MATRIX.csv` (PAR-001/002/003/004/011/012/013/015), `GATES.json` e `RESULT-REVIEW-TEMPLATE.md`.
- `docs/architecture/ADR-0003-legacy-compatibility-proposed.md` — estado **PROPOSED_NOT_APPROVED**, sem alterar a arquitetura.
- Constituição ARC-01–09, ADR-0001/0002, guardrails de interoperabilidade.
- Este prompt, pelo SHA do commit F1 indicado no link recebido.

O trabalho de paridade já estava em andamento; F1 não é reinício. O pedido atual prioriza recuperar uso do legado rapidamente, **sem** converter/reorganizar os experimentos históricos. As fases F2, F3A, F3B, F4, F5 e F6 continuam fora desta execução. Qualquer mudança do plano exige justificativa e aprovação aplicável ANTES da execução.

## 2. Workspace, raízes e proibições

- Abra como `PROJECT_ROOT` **o checkout Atlas existente**, realmente autorizado para trabalho; não confunda o workspace de outro chat com este.
- Inspecione apenas `git rev-parse HEAD`, `git status --porcelain`, `git worktree list`, `git rev-parse --show-toplevel` para proveniência. **Não faça switch de branch, reset, clean, checkout, fetch forçado ou alterações Git na F1**.
- Escrita privada exclusiva: `<PROJECT_ROOT>/.local/atlas-parity04-f1-legacy-inventory/`; confirme que `.local` é ignorado pelo Git. Faça uma única prova de criar/ler/remover um arquivo temporário dentro da raiz exclusiva. Se negar, `LOCAL_WORKSPACE_UNAVAILABLE`; não escolha outro drive nem modifique ACL/sandbox/firewall.
- Os dados de entrada pertencem a raízes **expressamente autorizadas**, reconhecidas em configuração/recibo local existente. Caminhos históricos em documentos são pistas, nunca autorização automática.
- **Nunca** percorrer G:, H:, Downloads, repositórios vizinhos ou worktrees em busca de dados. Não acessar fonte sem vínculo e autorização reais.
- Não criar worktree/clone/branch nova; não modificar repositórios R4 ou Atlas, fonte científica, pacote P04, Caderno legado ou novo, documentação original ou instalações.
- Não executar experimentos, `project`, `atlas`, `migrate`, `apply-import`, exportação, pipeline produtor, provider, LLM ou navegador. Não instalar pacotes nem disparar downloads.
- Se HTML tiver dados embutidos, parsear somente JSON **inerte**, sem executar scripts, links, HTML ativo, JS ou comandos contidos na fonte.
- O Atlas público não importa `r4.*`; nesta missão não implementar novo leitor dentro do runtime, não tocar schema/SDK/versão/protocolo.

## 3. Delegação nativa real, quando disponível

Até três subagentes nativos reais, sem inventar nomes/execuções:

- **A — seleção e integridade:** raízes realmente permitidas, fontes já identificadas, fingerprints, snapshots, cotas, preservação. Somente leitura.
- **B — semântica observada:** records, families, experiments, runs, edges, requirements, products/documents; identificar o que existe e está ausente. Somente leitura.
- **C — revisão adversarial independente:** conferir critérios G1, integridade e conclusões; não escrever nem ser autor dos recibos.

Coordenador único escreve os recibos na raiz privada. Se não há agentes reais, execute sequencialmente com `NATIVE_SUBAGENTS_NOT_AVAILABLE`; não denominar QA do autor como revisão independente.

## 4. Fonte legada: seleção rápida e delimitada

Comece com arquivos de configuração/recibos conhecidos e autorizados, não com descoberta geral. Escolha até **três projeções/índices preexistentes**, preferindo uma que já alimente o Atlas legado e contenha árvore mais tabelas de RF.

- Registre **privadamente**: por que o candidato foi selecionado, caminho físico real, arquivo de configuração autorizado, tamanho, formato/schema declarado, chaves, limites, symlinks/reparse, SHA-256 quando possível e instante de observação (separado do tempo do experimento).
- Cota inicial: até 64 MiB por arquivo escolhido, sujeito ao limite documentado. Se exceder, reporte `READ_LIMIT_EXCEEDED` sem alterar fontes ou aumentar o limite silenciosamente.
- JSON/JSON-LD: use parser seguro, sem avaliar instruções. HTML: somente metadados e JSON embutido inerte, sem abrir navegador ou executar scripts.
- Se nenhum índice for acessível, registre `SOURCE_NOT_LOCATED`/`SOURCE_NOT_AUTHORIZED` e peça somente a **raiz autorizada ou caminho exato da projeção** que falta. Não faça varredura global.
- A coorte P04 de duas execuções sem linhas RF é evidência limitada; não qualifica G1.

## 5. Provar estrutura e ao menos UMA linha RF literal

Inspecione o formato real. No legado R4 podem existir coleções chamadas `records`, `edges`, `result_tables`, `products`, `product_groups`, `product_items`, `resources`, `resource_documents`, `dossiers` e `coverage`; esses nomes são **hipóteses a verificar**, não fatos obrigatórios.

**Hierarquia:** identificar fonte, famílias, projeto, experimento, execução/run/estágio, IDs originais, chaves de vinculação e relações tipadas. Diferenciar pertencimento organizacional, input/output, derivação, histórico contextual e menção neutra. Não criar pais/filhos por nome ou posição.

**Requisitos:** localizar ao menos uma **tabela RF existente e não sintética**. Verificar privadamente uma linha real com ID original, núcleo/categoria se presente, nome/título, descrição e critérios de aceite literais quando presentes; apontar a tabela e a localização interna exata no arquivo original; preservar vínculo explícito com projeto/experimento/execução/fonte. Registrar `MISSING`/`UNKNOWN` para campos que não existirem. Não duplicar o corpus nem inventar RF/RNF/RES.

**Outras funcionalidades:** caracterizar presença/ausência de produtos, documentos, dossiês, referências, revisões e cobertura, sem confundir `File` com produto, nem atribuir aprovação científica por integridade. RNF/RES apenas quando declarados, sem inferir disponibilidade.

**Contagens:** registrar quantos arquivos foram considerados, lidos, parseados e quantos objetos/linhas/relações existem **na seleção**, com escopo, unidade e denominador. O total global da história continua `UNKNOWN_UPSTREAM` sem prova própria.

## 6. Imutabilidade, segurança e negativos

- Para cada fonte lida e hashável, calcular SHA-256 antes/depois e exigir igualdade. Onde não for possível, registrar `NOT_HASHED` e motivo; não alegar integridade de todo o acervo.
- Comparar estado Git/arquivos de prova antes/depois no escopo observado; nenhuma fonte original, P04 ou instalação deve ser modificada.
- Conferir relações para destinos ausentes e duplicações apenas por leitura; qualquer caso negativo adicional deve usar fixtures locais descartáveis, jamais editar dados reais.
- Não seguir URIs privados, links `file://`, scripts, URLs externas, HTML ou payloads executáveis.
- Proibido publicar em GitHub público **qualquer** path físico, URI, ID de experimento, linha literal RF, cliente/pessoa, screenshot, digest de fonte privada, código privado ou dados que possam reidentificar o acervo.

## 7. Saídas locais e handoff público

**Somente no diretório `.local` exclusivo**, produza:

1. `RESULT.private.md` — conclusão e limitações por camada.
2. `SOURCE-SELECTION.private.json` — candidatos e seleção.
3. `SOURCE-STRUCTURE.private.json` — campos/tipos e contagens observadas.
4. `RF-VERIFICATION.private.json` — prova de linha RF literal, com ponteiro à origem, sem inventar valores.
5. `IMMUTABILITY.private.json` — hashes/estatísticas antes/depois no escopo.
6. `G1-RECEIPT.private.json` — estados de todos os predicados G1.
7. `INDEPENDENT-REVIEW.private.md` — parecer real ou indisponibilidade.
8. `SANITIZED-HANDOFF.md`, `SANITIZED-HANDOFF.json`, `RESULT-REVIEW.sanitized.md` — somente agregados, estados, falta de campos e próximos atos.
9. `MANIFEST.sha256` — arquivos privados gerados, sem auto-inclusão.

Não sobrescrever recibos antigos; versionar revisões locais se necessário.

G1 só é `F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED` quando uma fonte **real, preexistente, autorizada**, com hierarquia ligável e ao menos uma RF literal, foi confirmada na origem; limites e identidade estão honestos; originais não foram alterados no escopo medido. Revisão independente executada ou indisponível deve ser declarada sem simular. Estado contrário: `F1_BLOCKED_EXACT` + causa e menor próximo ato.

**Persistência:** publicar apenas os três arquivos `SANITIZED-*`/`RESULT-REVIEW.sanitized.md` na branch de documentação F1 deste prompt, depois de revisão de privacidade, **somente se houver GitHub com escrita efetiva**. Não tocar na PR #14 nem criar worktree/clone. Exigir SHA/tree/parent e verificação no Git. Se a sessão LOCAL não puder publicar, declarar `PUBLIC_HANDOFF_GIT_PERSISTENCE=PENDING` e transferir somente os documentos sanitizados a um CHAT com GitHub; não repetir a pesquisa privada por causa disso.

Não iniciar F2–F6, não implementar adaptador nem certificar HL7/FHIR. Terminar com confronto ao AP04-POR (PAR-001/002/003/004/011/012/013/015), evidências e impedimentos exatos. Sem merge, release, deploy, promoção, migração ou retirada.
