# FOCO01 — recibo público da interface instalada

**Resultado:** `PASS_SCOPED`, em 24/10/2026. Este registro consolida as execuções
reais de A2 sobre o produtor ambiental sintético público existente e sua variante
adversarial. A consolidação não reexecutou os testes.

O [recibo estruturado](FOCO01-ui.json) preserva integralmente os resultados bem
sucedidos de instalação e browser, seus hashes, os hashes das fontes de build e
os limites da afirmação. Não contém fontes ou resultados de outro produtor.

## Identidade dos bytes verificados

| Entrada | Identidade |
|---|---|
| Baseline pública | `228fee0af13b15cfacd97b9b122a395b86be10fe` |
| Commit do incremento A2 | `164990a90c185e60dcba84719f353386d329b446` |
| SHA-256 de `scripts/qa/browser.mjs` | `e476087d9deed38863e93a5809f24763e265513dfebef08a7e6186bc1afb7131` |
| Perfil candidato | `0.1.0a1` |
| SHA-256 da descrição do perfil | `76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e` |

Os testes rodaram nos bytes da árvore de trabalho posteriormente incluídos no
commit A2. As fontes dos pacotes instalados permanecem iguais à baseline pública.
O recibo não atribui esses resultados a um SHA de integração posterior; CI e
revisão desse SHA exigem seus próprios registros.

## Resultados observados

| Ensaio | Resultado | Cobertura observada |
|---|---|---|
| Instalação limpa | PASS_SCOPED | SDK e viewer em ambientes novos, imports instalados, quatro runs, reconstrução equivalente e bytes das fontes intactos |
| Browser ambiental | 18 checks PASS | Quatro detalhes, duas ausências, sete vínculos com artefatos, doze relações e um par comparável em `source-1` |
| Browser adversarial | 22 checks PASS | Quatro detalhes, duas ausências, sete vínculos com artefatos, quatorze relações, precisão de inteiro grande e métricas/tipos/unidades incompatíveis |
| Erros JS / requisições externas da página | 0 / 0 nos dois browsers | Requisições externas são bloqueadas pelo harness e reprovam a execução |
| Desktop / mobile | PASS, capturas ambientais inspecionadas | Viewports de 1440 e 390 pixels; sem overflow da página observado |

O ensaio adversarial registra **zero pares compatíveis**. Essa fixture verifica
incompatibilidade e não é uma prova positiva de comparação. A contagem por fonte
impede que a comparação de uma fonte seja atribuída a outra.

Versões efetivas: Python **3.12.14**, Playwright **1.62.1**, Chromium
**151.0.7922.34**, build **1.3.0**, setuptools **80.9.0** e wheel **0.45.1**.
Os checks de browser não são uma contagem adicional de testes Python.

## Falhas ambientais resolvidas

A tentativa inicial de instalar ferramentas foi bloqueada pela rede do sandbox;
as ferramentas públicas fixadas foram instaladas em ambiente temporário separado
após execução autorizada. O teste do servidor também exigiu execução autorizada
para criar seu socket de loopback.

O browser não estava instalado. O CDN Playwright retornou HTML de indisponibilidade
em lugar do ZIP; o arquivo da **mesma versão** foi obtido da origem oficial Chrome
for Testing. A URL e o SHA-256 do arquivo estão no recibo estruturado. A tentativa
sem browser executou zero checks; somente as execuções completas posteriores são
as provas positivas da tabela.

## Limites e reprodução

Os [comandos de demonstração](../poc-reproducible.md) usam os entrypoints existentes
`scripts/qa/clean_install.py` e `scripts/ci/run_browser.py`. Escolha um destino novo
para cada instalação. Os comandos do JSON substituem somente caminhos locais por
placeholders lógicos.

A comparação de bytes antes/depois pertence ao estágio CLI, reconstrução e dossiê
do instalador; não se inventa uma auditoria adicional de bytes durante o browser.
Windows, Python otimizado, CI do SHA integrado e revisão Codex não foram executados
por este recibo A2. Capturas citadas nos recibos originais não são novos anexos deste
incremento documental.

**ADR-0002 permanece PENDING_HUMAN.** Estes resultados não representam aprovação
científica, certificação integral dos padrões, estabilização, merge, release,
promoção canônica, recuperação histórica ou autorização física.
