# Parecer independente C2 — código qualificado

**Revisor:** /root/independent_review, agente nativo real, sem autoria de código,
testes, workflow ou documentação do delta. Parecer recebido por mensagem e
transcrito pelo coordenador.
**SHA:** `dc43653d4e06c1f5500437a42b2fb9e2df426dd6`.
**Árvore:** `0dd3331f1f873a634f286fdfdb703c1a76a87406`.
**Resultado:** `PASS_SCOPED_CODE_REVIEW`. **Bloqueantes abertos: 0.**

## Procedimentos independentes

Leitura do contrato/API e delta completo; confirmação remota da implementação
inicial e ancestralidade; conferência dos 25 arquivos nos dois inputs e dos
manifestos P03/C2; execução própria do gate inputs no SHA inicial e revisão
da correção CSS sem editar arquivos.

Exame dos oito artefatos do run 40546494721, hashes de todos os recibos referenciados
por JOB-SUMMARY e PNGs dos dois browsers; inspeção visual do desktop Linux,
320px com text spacing e RED anterior. Testes de produto/browser foram executados
por Actions, não no ambiente local do revisor.

## Constatações

| Área | Resultado examinado |
|---|---|
| Inputs/ownership | 25 frozen, 56 manifesto e 219 herdados intactos; somente paths C2 |
| Coleção | 47/47 por Linux/Windows × normal/-O; zero skips/erros/falhas |
| Schema antes pulado | test_sdk.ContractAndRoundTrip.test_profile_schema_matches_positive_fixture passou com jsonschema 4.25.1 test-only |
| Build/install | setuptools 80.9.0/build 1.3.0/wheel 0.45.1; 22 arquivos por blob; venvs externos,-I,sem R4 |
| HTTP | Socket real,oito rotas exatas,47 checks/configuração ; MIME/CSP/negativas/loopback |
| Browser Linux | Chrome 156.0.8078.47; 19/19,seis PNGs com hashes conferidos |
| Browser Windows | Chrome 156.0.8078.48; 19/19,seis PNGs com hashes conferidos |
| Spec Kit | CLI 1.2.3,integração/helpers nos dois sistemas,sem ponteiro global |
| CI | 40546494721:8/8 success;40546494687 success;40546494736 success |

Checks reais cobrem tabela/identidade, filtros/ordenação tipados, strings numéricas,
inteiros grandes, booleanos, null/ausência, unidades/precisão, File/mentions,
candidatos sintéticos, teclado/foco,1440/390/320px,scroll2D,text spacing e conteúdo
hostil. Zero page_errors,console_errors,requests externos e WebSockets no contexto.
Reruns da mesma coleção não são somados como testes únicos.

## Finding resolvido — C2-BROWSER-320

Run 40546112894 no SHA `97151e0e17c3d8afc70aad91a5c488cd831eb171` reproduziu
overflow dos controles do harness em 320px. O patch limitou track/grid e select
mantendo wrapping; não adicionou hidden/clip nem enfraqueceu oracle. Reexecução
integral no SHA dc43653d… comprovou document_scroll_width=320, nenhuma fuga externa
e scroll horizontal/vertical por teclado. O RED permanece no SHA anterior.

## Limitações e decisão

Zoom nativo a 200 permanece NOT_RUN, permitido condicionalmente no prompt.
Não houve substituição por CSS zoom/deviceScaleFactor/CDP scale. Rede do browser
é observação do contexto Playwright, não captura do processo inteiro. Contenção
vertical depende da CSS de embedding. Produto/documento continuam sintéticos;
VISIBLE_IN_MAIN_APP=false. ARC-01–09, independência do Caderno e eixos de
validade/integridade/autenticidade/ciência permanecem separados.

Nenhum finding bloqueante de código aberto. Parecer não aprova PR,merge,ciência
ou composição. O commit documental posterior requer CI e revisão próprios;
esse fechamento é identificado pelo SHA exato na PR #10 e na conversa. Nenhum
resultado acima é atribuído automaticamente ao commit documental.
