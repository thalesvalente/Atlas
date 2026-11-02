# Implementation Plan — experiência nativa do Caderno

## Technical Context
Python 3.12/stdlib e SDK Caderno existente; JavaScript ES modules/SVG/DOM; servidor local existente; testes unittest e Playwright já fixado pela CI. Sem novas dependências de runtime, serviços, banco ou contas. Sem clone/worktree adicional. Branch/PR #23, baseline observado 4e5eeb5aa9f9dc603a03d343615595c123381340.

## Constitution Check
ARC-01/03: visualização derivada, fontes somente leitura. ARC-02/04/05: produtor externo exporta Files no perfil existente; viewer não importa R4. ARC-06: sem aprovação inferida ou IDs científicos inventados. ARC-07/08: nenhum poder de migração/retirada; original preservado. ARC-09: nenhuma alteração do protocolo científico; payload opcional de apresentação separado. A execução usa apenas código público original do novo adaptador; código privado e dados permanecem no host.

## Research / decisão
Reutilizar `r4.campaigns.atlas.project(root)` (referência R4 789611d618a4aa3e404d11480b36413c7330a36b), que chama o read_model real e já preserva resolução/ausências. Não reconstruir leitor de ledgers, não inserir HTML em iframe e não impor o schema incompleto do antigo descriptor C2 aos source_keys. Intercâmbio: pacote RO-Crate normal contendo chunks JSON `atlas-native-view/1`, identificados pelo media type; nenhuma mudança em packages/protocol. Detalhes em research.md e contracts/native-view.md.

## Estrutura e ownership
- `tools/export_native_notebook.py`: adaptador externo de fonte original para apresentação genérica e pacote.
- `packages/atlas/src/atlas_viewer/native_notebook.py`: leitor de payloads declarados/verificados e snapshot da API.
- `packages/atlas/src/atlas_viewer/server.py`: rota fixa /notebook e /api/notebook.
- `packages/atlas/src/atlas_viewer/static/native_notebook.*`: UI nativa; componente `parity02_p03_table.js/css` reaproveitado por blob.
- `scripts/ABRIR-ATLAS.ps1`: **entrada principal do Atlas NOVO** independente do R4, sem aquisição ou descoberta implícita, usando apenas pacotes fixados do protocolo; modo vazio explícito.
- `scripts/ABRIR-ATLAS-NATIVO.ps1`: somente compatibilidade externa com o produtor legado; preflight, export e abertura; sem instalação automática.
- `tests/viewer/test_native_notebook.py`, `scripts/qa/browser_native_notebook.mjs`: contrato, integração e browser.

## PLAN/DAG
O0 spec/contrato → O1 adaptador e DTO → O2 leitor + componentes + launcher → O3 testes/CI SHA final + revisão externa → O4 aceite host. Um writer nesta sessão. Sem subagentes nativos disponíveis: NATIVE_SUBAGENTS_NOT_AVAILABLE, execução sequencial; não simular QA independente.

## Spec Kit realmente utilizado
Skills `speckit-plan`, `speckit-tasks`, `speckit-implement` lidas em .agents/skills; constituição preservada; sem extensions.yml nesta árvore. Scripts setup_plan.py, setup_tasks.py e check_prerequisites.py serão executados nos runners com `SPECIFY_FEATURE_DIRECTORY=specs/004-native-notebook-experience` e `SPECIFY_FEATURE_NO_PERSIST=1`. CLI não instalada no container do CHAT: não instalar nem alegar comando local executado. As Actions já instalam a versão fixada 1.2.3.

## Testes e gates
Pacote válido pelo SDK; precisão/ausência/colisão; fraude de hash, versão desconhecida, arquivo ausente, ZIP/diretório e quotas; fonte intacta; regressões do viewer; UI nativa busca, árvore, tabelas, recursos, timeline, coverage e exports em Chromium. Windows/Ubuntu normal/-O por CI. Revisão @codex separada e host real ficam pendentes até evidência.

## Integração / rollback
Commits incrementais na PR #23 com lease do HEAD. P03 importado por blob do próprio repo, fontes/manifests históricos intactos. Rollback é retornar à aplicação anterior e continuar usando o Atlas R4; não tocar no Caderno. Mudanças de source files pinados exigem atualização explícita da auditoria scoped com negativos, nunca desativar checks.
