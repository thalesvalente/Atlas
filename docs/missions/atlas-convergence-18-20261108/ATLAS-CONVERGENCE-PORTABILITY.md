# Portabilidade verificável e limites

## Material recuperável

Código, testes, matriz de 18 disposições, 84 requisitos, 240 itens de crosswalk,
provas sintéticas e revisões independentes estão nesta branch pública. Os
artefatos de O1 mantêm seus hashes; paths temporários do runtime nos logs são
proveniência de execução, não diretórios privados a reproduzir.

O recibo terminal da PR registra o SHA final, tree, jobs, hashes de review,
comandos de clone e readback. O arquivo `ATLAS-CONVERGENCE-QA-SHA.json` completo é
entregue com esse recibo e no pacote de evidências da conversa. Ele é emitido
depois da CI; um commit não tenta embutir o próprio hash nem se aprova por referência
circular. Os IDs/URLs dos Actions permanecem recuperáveis mesmo quando os
artefatos temporários de browser expiram.

## Novo clone

Em um diretório escolhido pelo operador que ainda não contenha um checkout Atlas:

```sh
git clone https://github.com/thalesvalente/Atlas.git atlas
cd atlas
git fetch origin fix/atlas-convergence18-20261108
git switch --detach FETCH_HEAD
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git fsck --connectivity-only --no-dangling
```

Compare HEAD/tree aos valores **exatos** do recibo terminal. Se a branch avançou,
faça `git switch --detach SHA_EXATO_DO_RECIBO` antes de reproduzir os testes.
Não use um checkout com alterações próprias para simular clone limpo.

O clone por rede deve ser completo, sem `--reference`, alternates, grafts ou
`replace`. No host pessoal já existente, reusar a raiz autorizada e seu inventário;
esta receita não concede permissão para criar clones irmãos, apagar worktrees
ou substituir dados locais.

## Reprodução de testes

Com Node já disponível:

```sh
node --test scripts/qa/test_protocol_snapshot.mjs
python -B tests/viewer/test_native_notebook_producer_origin.py -v
python -O -B tests/viewer/test_native_notebook_producer_origin.py -v
python -B scripts/qa/speckit_audit.py --allow-presentation-delta
python -B scripts/qa/verify_a01_reuse_successor.py
```

Os testes de origem usam somente fixtures sintéticas e dependências públicas de
código-fonte do checkout. O subprocesso mede o modo otimizado: `-I` não depende da
variável `PYTHONOPTIMIZE`. Symlink indisponível no runner gera SKIP explícito;
o caso de sombreamento por pacote ambiente permanece executável sem symlink.

Instalação de wheels, Chromium e Windows/PowerShell são qualificados pelos
workflows existentes da PR. Para executá-los em outro ambiente, seguir os pins e
comandos desses workflows somente em ambiente autorizado a instalar dependências.
A presente missão não instalou ferramentas no runtime do Chat nem solicitou
Codex Local por conveniência.

## PR #40 e histórico

A #40 permanece Draft separada. Seus cinco arquivos podem ser inspecionados sem
integrá-los, usando o SHA `7ac3e76d12f6d2e59d235458dc122d85850cf499` com `git show`.
As 24 disposições já resolvidas não foram refeitas. O readback de portabilidade
conferiu a presença das 24 refs de recuperação, a ancestralidade e os cinco
arquivos adicionados; nenhuma exclusão no host foi executada novamente.

As refs das PRs históricas #6–#22/#30/#31 permanecem disponíveis. A baseline
normativa ARC-09 `d5bdc86ef68cad2f5d503945ca788c3a74df4839` e a guarda terminal K
não foram reescritas. Fonte pública recuperável não significa aceite normativo.

## Dados privados e LOCAL_NOT_REQUIRED

**LOCAL_NOT_REQUIRED para os reparos e para a QA desta convergência.** Fixtures,
GitHub Actions, Windows padrão e Chromium remoto bastam para os comportamentos
retidos. Não foi necessário acessar unidades G:/H:, GUI pessoal, dispositivo ou
corpus real. O bloqueio de Chromium no runtime do Chat foi suprido pelo workflow
de browser, sem contorno de permissões.

GitHub não é backup de `.local`, fontes científicas, recibos privados, worktrees
não publicados ou arquivos ignorados. Nenhum desses dados foi acessado, copiado,
certificado como recuperável ou removido. O testemunho L0 e os atos de privacidade
históricos continuam separados. Não se emite `LOCAL_REQUIRED` sem provar uma
dependência real e preparar o checkpoint específico.
