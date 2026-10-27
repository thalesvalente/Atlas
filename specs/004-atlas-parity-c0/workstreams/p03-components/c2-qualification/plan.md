# Plano C2 — PLAN → EXECUTE → REVIEW

## Arquitetura e decisões

Preservar integralmente os 25 arquivos P03 e os 219 arquivos do handoff. Acrescentar
harness/gates com prefixo atlas_parity03_p03, workflow próprio e este subworkstream.
Nenhuma dependência de teste entra no produto. Reusar pins build 1.3.0,
setuptools 80.9.0, wheel 0.45.1, jsonschema 4.25.1 e Playwright 1.62.1 já usados no repo.

O harness reutiliza os oito recursos P03, substituindo apenas sua CSS de embedding
para limitar a altura da região tabular; o CSS congelado do componente não ganha
essa garantia automaticamente. CSP permite o esquema data: para o favicon constante; nenhuma imagem HTTP(S) é permitida.
Host/Origin e o request-target bruto são validados; nenhuma rota de payload existe.

Browser usa Chrome/Chromium existente do runner, sem download. Requests/WebSockets
do contexto são observados e impedidos fora da origem loopback. Isso não é captura
de tráfego background de todo Chromium. Zoom nativo a 200 sem prova recebe NOT_RUN.

## Ownership exclusivo real

| Agente | Escrita |
|---|---|
| /root/packaging_http | Novos gates Python build/HTTP/harness |
| /root/browser_semantics | Novo browser MJS e CSS focal |
| /root | Workflow, runner/coleção, docs, workstream, commits e Draft |
| /root/independent_review | Nenhuma autoria do delta; parecer por mensagem |

## Sequência e dependências

1. Fixar entrada e confirmar manifestos; fazer análise de requisitos/ownership.
2. Implementar build/HTTP e browser em paralelo, com revisão adversarial separada.
3. Publicar candidata exata; executar matriz portable Linux/Windows × O0/O1,
   browser Linux/Windows e Spec Kit Linux/Windows.
4. Resolver falhas reais de gate sem alterar ownership alheio; novo delta implica
   novo SHA e nova execução. Sem polling contínuo: consultas por eventos próprios.
5. Congelar documentação com recibos do código explicitamente identificado;
   executar CI novamente no commit documental final e revisar esse SHA.

## Spec Kit 1.2.3

Método e skills oficiais do repo orientam specify/clarify/plan/checklist/tasks/
analyze/implement/verify/converge/review. Helpers reais usam
SPECIFY_FEATURE_NO_PERSIST=1 e SPECIFY_FEATURE_DIRECTORY deste subworkstream.
CLI 1.2.3 em venv/job isolado, sem reinitialização e sem escrever ponteiro global.
Redação/análise humana-assistida são diferenciadas de execução CLI.
REASONING_EFFECTIVE=UNVERIFIED: o seletor solicitado não é observável.
