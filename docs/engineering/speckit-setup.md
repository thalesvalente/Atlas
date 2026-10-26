# Ambiente de engenharia do Atlas

Spec Kit **1.2.3**, integração **Codex / skills**, scripts **Python**.
O CLI é uma ferramenta de desenvolvimento isolada, sem dependência no SDK ou viewer.
O gerenciador usado nesta adoção é **uv 0.13.5**; o CLI foi instalado da distribuição
oficial `specify-cli==1.2.3` no PyPI, com Python **3.14.3** já disponível no host.
Dependências transitivas são resolvidas pelo uv; não se promete um ambiente binário
idêntico em todas as plataformas. A versão do CLI fixa seus assets oficiais incluídos.

## Organização canônica

| Caminho | Conteúdo e autoridade |
|---|---|
| `.specify/` | Infraestrutura oficial, templates, scripts, workflow e manifests gerenciados; constituição do Atlas preservada |
| `.agents/skills/speckit-*/SKILL.md` | Dez skills oficiais Codex, revisadas e versionadas |
| `specs/` | Artefatos das features; `001-*` e `002-*` preservados nesta manutenção |
| `docs/architecture/` | ADRs; ADR-0002 continua `PROPOSED / PENDING_HUMAN` |
| `docs/engineering/` | Procedimentos de ferramentas e desenvolvimento |
| `.local/` | Dados temporários, recibos locais e ambientes ignorados pelo Git |

O CLI persistente fica no diretório padrão de ferramentas do uv do usuário,
fora do clone. Não há instalação paralela em `.local/speckit-cli` nem scaffold
intermediário. `.local/install-02` é a instalação funcional existente do Atlas.
A regra de ignore de `.agents/` permite somente os `SKILL.md` oficiais revisados;
sessões, credenciais e demais arquivos de agentes não devem ser versionados.
`.specify/.gitignore` mantém o ponteiro de feature e configurações locais fora do Git.

## Configurar um clone novo

Requisitos: Git, Python 3.11+ (3.14.3 foi ensaiado), uv 0.13.5 e Codex disponível
no terminal. Abra o clone do Atlas no Codex. Verifique instalações existentes antes
de executar qualquer instalação: `Get-Command uv,specify,codex` no PowerShell,
ou `command -v uv specify codex` no shell POSIX; depois `uv tool list` e
`specify version --json` quando disponíveis. Se o CLI existente tiver outra versão,
atualize com o mesmo gerenciador, evitando deixar uma segunda cópia no PATH.

Se uv estiver ausente, use seu instalador oficial fixado, sem bootstrap próprio:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/0.13.5/install.ps1 | iex"
```

```sh
curl -LsSf https://astral.sh/uv/0.13.5/install.sh | sh
```

Reabra o terminal para carregar o PATH. O instalador do Windows usa o diretório
de executáveis do usuário, normalmente `%USERPROFILE%\.local\bin`.

```sh
uv --version
uv tool list
uv tool install specify-cli==1.2.3
specify version --json
specify check
specify integration status --json
python scripts/qa/speckit_audit.py
```

`uv tool install` é persistente e isolado. Não use `uvx` como substituto de uma
instalação persistente. Se já instalado por uv em versão diferente, a atualização
deliberada é `uv tool install --force specify-cli==1.2.3`, seguida de nova validação.
Uma instalação anterior por outro gerenciador deve ser reconciliada por ele antes
de escolher o comando canônico. O status deve indicar Codex como default e nenhum
arquivo gerenciado ausente, modificado ou inválido.

O clone já contém a infraestrutura oficial gerada e as skills; não é necessário
reinicializá-lo para começar a trabalhar. Para uma adoção inicial ou regeneração
deliberada, o mecanismo oficial usado nesta missão é:

```sh
specify init --here --force --non-interactive --integration codex --integration-options="--skills" --script py
```

Antes de `--force`, registre `git rev-parse HEAD`, `git status --short` e
`git worktree list --porcelain`, crie uma branch própria e tenha commit ou backup
reversível de todo trabalho local, inclusive arquivos gerenciados ignorados.
Depois examine `git diff`, `git status --short`, `specify integration status --json`
e execute a auditoria de preservação. O comando mescla arquivos gerenciados e pode
substituí-los; não execute com trabalho local sem preservar. O inicializador 1.2.3
preserva uma constituição existente; a auditoria confirma essa condição no Atlas.
Em CI sem agente instalado, `--ignore-agent-tools` é uma opção oficial; ela não
comprova disponibilidade nem execução do Codex.

`--script py` instala seis scripts Python e também o fallback do shell da plataforma
(PowerShell no Windows; Bash em sistemas POSIX). Isso é comportamento nativo.
Manifests e registros podem receber novos timestamps ao reinicializar; compare
os hashes dos conteúdos gerenciados, não apenas os timestamps.

## Uso pelo Codex e seleção de feature

As skills são descobertas pelo Codex em `.agents/skills/`. Em uma sessão aberta
depois da instalação, invoque por exemplo `$speckit-analyze` ou `$speckit-plan`.
São instruções para o agente; não são subcomandos do terminal `specify`.
`$speckit-constitution` pode editar a constituição: sua presença não autoriza
reescrever as decisões do Atlas. A skill `speckit-taskstoissues` é upstream
obsoleta; sua presença tampouco autoriza criar issues ou ativar extensões.

A feature ativa é independente da branch. Durante esta missão, **somente ORQ**
escreve `.specify/feature.json`. O baseline não tinha esse arquivo, e a manutenção
não o cria. Para validar features existentes sem persistir seleção:

```powershell
$env:SPECIFY_FEATURE_NO_PERSIST = '1'
try {
    $env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-atlas021-protocol-interface'
    python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
    $env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-atlas021-poc-r4'
    python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
} finally {
    Remove-Item Env:SPECIFY_FEATURE_DIRECTORY -ErrorAction SilentlyContinue
    Remove-Item Env:SPECIFY_FEATURE_NO_PERSIST -ErrorAction SilentlyContinue
}
```

Os exemplos gerados das skills usam `python3`. Neste host Windows esse nome
resolve para um alias inoperante da Microsoft Store; use o executável real `python`
para os mesmos auxiliares. Não há shim artesanal nem alteração nas skills oficiais.
No POSIX, use `python3` caso `python` não exista. Para leitura sem persistência:

```sh
SPECIFY_FEATURE_NO_PERSIST=1 SPECIFY_FEATURE_DIRECTORY=specs/002-atlas021-poc-r4 \
  python3 .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
```

## Verificação e reversibilidade

`python scripts/qa/speckit_audit.py` valida os manifests oficiais, frontmatter das
skills, sintaxe dos scripts e integridade por bytes dos documentos, fontes e testes
preexistentes contra o commit de referência. Exige que esse commit esteja no clone;
em um clone raso, obtenha o histórico necessário antes de executar a auditoria.
Ele não inicializa projetos, não instala ferramentas e não muda a feature ativa.
`specify check` verifica ferramentas disponíveis; não executa experimentos ou modelos.

No checkout desta missão, o backup dos 109 arquivos originais e os hashes dos
1.845 arquivos de `.local/install-02` ficam em `.local/speckit-setup01/`, ignorado.
Conserve esse recibo enquanto precisar de rollback local. Uma reversão compartilhada
deve ser feita por commit que reverta exclusivamente este incremento, com revisão;
o CLI persistente é independente do Git. Não apague `.local/install-02` para reverter
ferramentas de engenharia. Nenhuma worktree adicional é necessária.

Esta configuração prepara o desenvolvimento de integrações seletivas. A prova
real R4 → Caderno → Atlas, aceite científico, liberação de fontes privadas e promoção
do protocolo continuam operações com evidências e autorizações próprias.

## Fontes oficiais

- [Instalação do Spec Kit 1.2.3](https://github.com/github/spec-kit/blob/v1.2.3/docs/installation.md).
- [Adoção em projetos existentes](https://github.com/github/spec-kit/blob/v1.2.3/docs/guides/existing-projects.md).
- [Integração Codex](https://github.com/github/spec-kit/blob/v1.2.3/docs/integrations/codex.md).
- [CLI e seleção de feature](https://github.com/github/spec-kit/blob/v1.2.3/docs/reference/core.md).
- [Manutenção da integração](https://github.com/github/spec-kit/blob/v1.2.3/docs/integrations/cli.md).
- [Skills do Codex](https://developers.openai.com/codex/skills).
- [Instalação oficial do uv](https://docs.astral.sh/uv/getting-started/installation/).
