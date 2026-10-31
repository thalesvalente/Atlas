# AP04-F3B-CHAT-TABLES-01 — recuperar tabelas RF/RNF/RES como componente genérico

`seai.pipeline@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub e GitHub Actions, escrita efetiva. Sem host Windows e sem acervo privado.  
**Esforço:** **Extra High** ou maior disponível, selecionado MANUALMENTE pelo operador. `REASONING_EFFECTIVE=UNVERIFIED` se não observado.  
**Destino único:** `thalesvalente/Atlas`. **Branch pré-criada** `feat/atlas-parity04-f3b-tables-20261031`; não criar outras branches/worktrees/clones.  
**Base congelada:** SHA `54bb16d350f7bc34fafb95438bd64a2397d58bf3`, tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`, PR Draft #15 qualificada.  
**Resultado-alvo:** `F3B_TABLE_COMPONENT_READY_FOR_F4`, apenas com gates isolados e revisão real; caso contrário `F3B_BLOCKED_EXACT`. Não declarar RF real integrada ou G6.

## 1. Decisões e precedência

Ler `AP04-POR-v1.0-draft`, ACTION-PLAN F3B, D-001–D-020, PAR-002/PAR-003/PAR-004/PAR-005/PAR-006/PAR-012/PAR-015, G3/G5, ARC-01–09, ADR-0001/0002 e ADR-0003 v0.2 com aprovação **somente no escopo** do pacote técnico `c3ea1e82938fd61cc5a22fee973352715a5bb527` e comentário PR #15 `6539419419`. Reutilizar F1 G1 `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7` SOMENTE como evidência sanitizada; sem dados privados na CI.

Ler schema/exemplos sintéticos completos do `EPHEMERAL-PRESENTATION-CONTRACT.md`, `IDENTITY-AND-LOSS-POLICY.md` e N01–N24 em `PARITY-TRACEABILITY.md`. ADR aprovou uma **arquitetura candidata**, não implementou File API nem concedeu F4/F5. **Esta execução autoriza somente F3B**, não F3A/F4/F5/F6. Mudança necessária no plano ou gate: justificar e solicitar aprovação antes da implementação.

Preservar RO-Crate 1.3, Process Run 0.6, Caderno 0.1.0a1 e a possibilidade futura de HL7/FHIR por domínio, sem tipos clínicos universais ou alegação de conformidade.

## 2. Ownership exclusivo para trabalho em paralelo

F3B pode editar exclusivamente:
- `packages/atlas/src/atlas_viewer/static/parity04_f3b_tables.js`
- `packages/atlas/src/atlas_viewer/static/parity04_f3b_tables.css`
- `tests/qa/test_atlas_parity04_f3b_tables.py` e testes auxiliares **prefixados f3b**;
- `tests/fixtures/atlas_parity04_f3b_*` sintéticas;
- `scripts/qa/atlas_parity04_f3b_*` para harness isolado;
- `docs/missions/atlas-parity-04/f3b-tables/` (recibos e manifestos);
- `.github/workflows/atlas-parity04-f3b-tables.yml` se um gate próprio puder ser construído sem desativar gates históricos.

**Somente leitura:** shell/CSS principal, `static/index.html`, `static/app.js`, Catalog/servidor/SDK, protocolo e reader003, guards P06/P03/AP04/F2, manifestos históricos, F1/F2, branch F3A. Shared files = owner integrador da F4, que não pode ser antecipado. Coordenador único writer Git; subagentes A modelagem/fidelidade, B QA/browser, C revisão independente somente leitura, com arquivos exclusivos. Sem agentes reais: execução sequencial e `NATIVE_SUBAGENTS_NOT_AVAILABLE`, não simular QA.

Não trocar worktree local do operador. O trabalho pode ocorrer no GitHub por branch sem worktree adicional. Não criar clone persistente.

## 3. Engenharia funcional — tabelas reais na forma, sintéticas no conteúdo

Entregar componente neutro que consuma `tables` do descriptor **`atlas-legacy-presentation` 0.2.0** na memória, sem instalar adaptador, abrir arquivo privado ou integrar ao shell do Atlas.

- Tabelas por ID/ocorrência/fonte/snapshot com cabeçalhos e colunas em ordem **original**; tipos, unidades, precisão, representação lexical e ausência preservados. Literais de RF são strings inertes, nunca HTML executável. Sem coerção inadvertida de números grandes/decimais/bools.
- Implementar busca/filtro, ordenação tipada apenas quando declarada, paginação/virtualização sem ocultar totais, detalhe fiel de linha e exportação. Filtro/ordenação NÃO podem modificar o dataset; indicar linhas carregadas/filtradas/visíveis e desconhecido global.
- IDs nativos, núcleo/módulo, nome, descrição, critérios de aceite e categoria `MISSING` apresentados quando realmente declarados. Distinguir `MISSING`, JSON null, string vazia, zero e informação `UNKNOWN`. Nunca preencher categoria por heurística.
- RF, RNF e RES são domínios **opcionais**; só exibir categorias efetivamente declaradas, sem inferir a partir de nome, MIME ou filename. `UNADMITTED_NATIVE_RF` com `native_id=null` deve ser consultável como **não admitida**, jamais ganhar identidade científica/aceite.
- Quatro tabelas sem `record_id` resolúvel devem continuar consultáveis como **não vinculadas**, não sumir nem receber record inventado. `binding_gap` e Run externo isolado ficam explícitos; não afirmar caminho contínuo árvore→RF. Seleção por fonte/snapshot/tabela/linha/occurrence com evento neutro de navegação para F4; **não importar código F3A**.
- Exportação: JSON fiel com literal/tipo/unidade/precisão/ausência, CSV seguro contra formula injection (`=`, `+`, `-`, `@`, CR/LF/control chars), aspas, delimitador e Unicode. Declarar diferença entre export literal JSON e CSV neutralizado; não alterar fonte. Não exportar dados inadvertidamente à rede.
- Textos hostis HTML/JS/URI, células extensas, arrays e objetos são dados inertes. Nada de `innerHTML` não sanitizado, URLs executáveis, downloads automáticos de recursos, telemetria ou acesso host. Evitar XSS/CSV formula execution.
- Componente independente com API explícita `mount`, `setTables`, `select`, `dispose` (ou equivalente), sem storage persistente. Troca de snapshot e expiração invalidam IDs/seleção; mensagens de ausência e erro visíveis.
- UI semântica `<table>` com `<th>`, caption e headers associados, suporte teclado/foco, filtros rotulados, reflow e overflow contido a 1440/390/320 CSS px. Não assumir que uma tabela horizontal longa cabe sem scroll; não ocultar conteúdos/colunas silenciosamente.

## 4. QA adversarial, browser e critérios G3 sintéticos

Fixtures devem ser 100% sintéticas, incluindo uma tabela fictícia RF completa, RNF/RES declaradas, tabela desvinculada, linha RF sem ID nativo, ausência de categoria e valores adversariais.

Testar:
- todos os campos e colunas, preservação de tipo/lexema/literal, números maiores que 2^53 e decimais exatos;
- filtros/ordenação/paginação sem perda/alteração de linhas; sem agregação de snapshots sobrepostos;
- quatro tabelas desvinculadas, 28 RF não admitidas em fixtures representativas (não alegar replay F1), seleção e binding_gap;
- classificação e estado sem inferência de RF/RNF/RES, File ≠ produto, `MISSING` ≠ null/vazio/zero;
- HTML/JS hostil em títulos/células, links maliciosos e CSV formula injection, com export JSON fiel e CSV seguro;
- teclado e foco; screenshots de browser real Windows/Ubuntu (Chromium) em larguras 1440, 390, 320, sem erros de console, page errors ou requisições externas;
- invalidar seleção/deep links por troca de snapshot/reimportação; quotas/erros visíveis e negados atomicamente.

Testar Python normal e `-O` nos harnesses Python, sem skips e sem `assert` removível em checkers de segurança. Os gates focais devem executar componentes de verdade, não apenas presença de string/AST. Emitir JSON/JUnit com SHA, IDs de teste e screenshots.

A CI global histórica pode rejeitar legitimamente novos paths de produto. Não afrouxar P06/AP04/F2/C4, não alterar pins para silenciar e não usar `continue-on-error` ou `paths-ignore` para fingir verde. Qualifique a F3B no gate isolado; se houver conflito de sucessão global, registre a causa e contrato para integrador/owner correspondente. Não declarar G5 global nem paridade real nessa condição.

## 5. Entrega Git e revisão

Entregar módulos JS/CSS, harness público isolado, testes/fixtures sintéticas e sob `docs/missions/atlas-parity-04/f3b-tables/`:
- `RESULT.md`, `INPUT-SHAS.json`, `TABLE-CONTRACT.md`, `BROWSER-RECEIPT.json`, `EXPORT-SECURITY.json`, `NEGATIVE-TESTS.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256`.
- Rastreabilidade antes/depois PAR-002/003/004/012/015, limitações, evidências por SHA/tree/parent e escopo da coleção testada.
- Revisor independente real, sem autoria, verifica o HEAD terminal, CI focada, semântica, segurança de export e integridade. Um commit documental posterior exige CI/revisão do novo SHA para fechamento.
- Publicar diretamente no Git branch F3B, fast-forward sem rebase/force; nenhuma branch ou worktree adicional. PR Draft própria apenas se necessária para CI/QA, base explícita na branch F2, mantendo PR #15 Draft. Não realizar merge.
- Git como handoff durável, nada de download manual de ZIP; nenhuma fonte privada, ID ou requisito real no repositório público.

**`F3B_TABLE_COMPONENT_READY_FOR_F4`** atesta somente tabela genérica sobre fixture, não RF real na C4 nem G6. Se faltarem browser, QA independente ou gate, `F3B_BLOCKED_EXACT` com menor ato e artefatos preservados. Sem migração, alteração R4, F4/F5/F6, release, deploy, promoção, aprovação científica ou limpeza.

**END-OF-F3B-PROMPT — COMPLETE**
