# ATLAS-SPECKIT-SETUP01 — registro de execução

Data: **25/10/2026**. Baseline: `a6e57c9c6748b4a0d50b554613c93e2b8a785554`.
Branch: `codex/atlas-speckit-setup01`. Base da PR: `feat/atlas021-poc-r4-foco01-20261024`,
no mesmo SHA. As PRs anteriores não foram modificadas.

## PLAN

Preflight somente leitura confirmou checkout limpo, HEAD destacado no SHA solicitado,
uma única worktree e ausência de instalação detectável do uv/Spec Kit nos comandos,
pacotes e diretórios persistentes consultados. O README relatava instalação anterior;
isso não foi usado como prova do estado atual. Codex CLI 0.149.0 e Python 3.14.3
estavam disponíveis. O perfil interativo PowerShell apresentou erros de hook Conda;
os comandos seguintes usaram shell sem perfil, sem editar o perfil do usuário.

Antes das escritas de adoção, foram registrados os hashes SHA-256 dos 109 arquivos
versionados, o inventário Git e os 1.845 arquivos da instalação funcional. Um ZIP
dos bytes originais ficou junto ao baseline em `.local/speckit-setup01/`, ignorado.
Criou-se uma branch exclusiva no checkout existente. Não houve stash, checkout de
outra base, nova worktree ou alteração das branches das PRs anteriores.

A documentação oficial da tag 1.2.3 foi consultada para adoção em projeto existente,
instalação PyPI/uv, integração Codex e seleção não persistente de feature. A
documentação oficial OpenAI confirmou o diretório de descoberta das skills.
O procedimento reproduzível está em [ambiente de engenharia](../engineering/speckit-setup.md).

## EXECUTE

1. Instalador oficial fixado do uv **0.13.5**, no diretório persistente do usuário;
   seu SHA-256 observado foi `84b66aa3018e9d800886543380d967bb3fb9652cfb251cfa5f3c73f4e62f59f2`.
2. `uv tool install specify-cli==1.2.3 --python <Python existente>`: uma única
   ferramenta persistente, em ambiente isolado gerenciado pelo uv. Não se criou
   ambiente de CLI nem scaffold intermediário em `.local/`.
3. Inicialização oficial no Atlas, sem cópia manual de scaffolds:

   ```sh
   specify init --here --force --non-interactive --integration codex --integration-options="--skills" --script py
   ```

4. Inspeção dos arquivos gerados, configuração do Git para compartilhar a infraestrutura
   e somente as skills revisadas; atribuição MIT upstream preservada. A licença do
   Atlas não foi alterada.
5. Segunda execução do mesmo inicializador no mesmo checkout, após registrar hashes
   dos 28 conteúdos gerenciados, workflow e constituição: **30/30 sem alteração de
   conteúdo**. Os timestamps dos registros nativos foram renovados normalmente.
6. Auditoria reutilizável somente leitura em `scripts/qa/speckit_audit.py`, procedimento
   de clone novo e atualização do README para separar o estado atual do registro antigo.

## REVIEW e validação executada

| Verificação | Resultado observado |
|---|---|
| `specify version` / `--json` | CLI 1.2.3, Python 3.14.3, Windows AMD64 |
| `uv tool list` | Uma ferramenta: `specify-cli v1.2.3`, executável `specify` |
| `specify check` | Exit 0; Codex CLI disponível. Outros agentes não instalados não são requisito do Atlas |
| `specify integration status --json` | `ok`, default Codex, 0 ausentes/modificados/inválidos, 0 manifests não verificados |
| Skills | 10 nomes/frontmatters válidos; conteúdo coerente com os hashes oficiais gerados |
| Scripts | 6 Python válidos; fallback PowerShell instalado pelo mecanismo oficial |
| Pré-requisitos 001 e 002 | Exit 0; spec/plan/tasks presentes; documentos auxiliares e template resolvidos |
| Sem seleção de feature | Exit 1 esperado, sem criação de `feature.json` |
| Auditoria de preservação | 105 arquivos originais protegidos, todos idênticos por bytes ao commit de referência |
| Instalação funcional | 1.845 arquivos, zero alterados/ausentes/adicionados; nenhuma reinstalação |
| Smoke CLI instalado | Viewer `inspect` e validador do protocolo: exit 0 com a fixture ambiental sintética |
| Suíte existente `scripts/run_checks.py` | 71 testes: protocolo 12, QA 46, viewer/HTTP 13; zero falhas, erros ou skips |
| Inventário de worktrees | Uma antes e depois, mesma raiz; apenas branch/HEAD mudam conforme o commit |
| Diff Git preparado | `git diff --cached --check`: exit 0; 42 arquivos, apenas quatro originais modificados |

As suítes usaram o Python do ambiente de ferramenta já instalado, com as fontes
públicas no `PYTHONPATH`, sem instalar dependências na aplicação. A tentativa inicial
no sandbox encontrou restrições de diretório temporário; os temporários passaram
a ficar no workspace. Protocolo e QA então passaram, mas quatro testes HTTP ficaram
impedidos por sockets. A execução com acesso aprovado ao loopback passou integralmente.
Não se alterou código para contornar falhas do ambiente.

O agente real `/root/independent_review` revisou em modo somente leitura infraestrutura,
procedimento, auditoria, ignores e preservação: **PASS, nenhum bloqueador**. Confirmou
independentemente os 1.845 arquivos da instalação e ausência de `feature.json`.
Seu `uv tool list` não acessou o lock fora do sandbox; a checagem foi concluída pelo
executor com a permissão de instalação já concedida. Não se simulou agente ou ferramenta.
A segunda revisão independente cobriu também este relatório e o recibo JSON,
comparou os logs de testes e confirmou os 30 conteúdos da reinicialização: **PASS**.

Os quatro arquivos originais alterados deliberadamente são `.gitignore`,
`.specify/toolchain.json`, `README.md` e `THIRD_PARTY_NOTICES.md`. Constituição,
ARC-01–09, ADR-0001/0002, `AGENTS.md`, todas as specs, fontes, fixtures e testes
originais permaneceram intactos. O [recibo estruturado](SPECKIT-SETUP01.json) registra
resultados e escopo; logs locais brutos e inventários do host não são publicados.

## Limites da evidência

- A integração está instalada, registrada e íntegra. Não se executou um novo modelo,
  nem workflows de skills que editam features ou constituição. Uma sessão Codex já
  aberta pode precisar ser reaberta para atualizar a lista de skills.
- As skills oficiais mencionam `python3`; o alias Store deste Windows é inoperante.
  Os auxiliares foram executados com o `python` real, conforme o procedimento.
- A repetição ensaiada é no checkout existente; não se criou outro clone ou ambiente
  Atlas para afirmar reprodução independente. Os comandos para clone novo usam as
  ferramentas oficiais fixadas. Dependências transitivas não têm lock binário global.
- Não se executou novo browser ou reinstalação limpa do runtime nesta manutenção.
  O smoke instalado e os 71 testes têm o escopo descrito acima.
- Digests dos manifests demonstram consistência dos arquivos gerados; não são
  autenticação criptográfica independente do publicador da distribuição.
- Não houve acesso ao R4 em H:, chamada paga, conteúdo privado, integração real
  de campanha, mudança do Caderno 0.1.0a1, aceite de ADR-0002, merge, release ou deploy.
  `PENDING_HUMAN` permanece. Configuração de engenharia não é prova operacional R4.
