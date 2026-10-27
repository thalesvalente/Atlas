# ATLAS-PARITY-02-P02 — resultado C0

**Estado: `P02_IMPLEMENTED_VERIFICATION_PENDING`.** Incremento funcional implementado,
testado no ambiente isolado de engenharia e publicado na
[PR Draft #8](https://github.com/thalesvalente/Atlas/pull/8).
As provas locais passaram. A CI do código terminou com falhas concretas em dois
controles globais de ownership P06; não há declaração de integração global aprovada.

Tag: `seai.pipeline@llm-sec,agentic-pac/seai.qa:`.
Destino Git único: `thalesvalente/Atlas`.
Branch: `work/atlas-parity02-p02-c0-20261027`.

## Objetos entregues

| Objeto | Identidade |
| --- | --- |
| Base conferida | `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5` |
| Árvore da base | `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59` |
| Código testado e revisado | `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990` |
| Árvore do código | `3a6c4f1b486f47e78c1ab26643dc30ddb28d631a` |
| Commit documental | O commit que contém este documento; seu SHA é informado na PR e no fechamento externo. Não há autorreferência circular. |

O commit documental acrescenta evidências e atualiza somente a documentação P02.
Ele não recebe por atribuição a CI de outro SHA. A equivalência dos arquivos de
produto, fixtures e scripts com o CODE_SHA sustenta o reaproveitamento explícito
dos testes locais; resultados remotos continuam identificados pelo SHA executado.

## Incremento funcional

O explorador agora busca título, ID e fonte, oferece ordenação determinística e
filtros por fonte, revisão, presença de métricas e presença de referências, além
dos filtros herdados. Estados vazios distinguem ausência de dados e filtros sem
resultado. A seleção de comparação permanece explícita, inclusive quando filtros
ocultam um dos itens; o limite herdado de quatro itens é da comparação, não do corpus.

View, filtros, detalhe e seleção ficam em um hash validado. Voltar, avançar,
recarregar e fechar o detalhe preservam o contexto. Identidades `source-N` só são
resolvidas com o scope da sessão/snapshot conhecido. Reiniciar o servidor ou mudar
o snapshot expira o vínculo com aviso, evitando abrir silenciosamente outra entidade.
O token não contém caminhos, não é identidade permanente e não prova autenticidade.

A tela separa fonte/pacote, snapshot e quantidades carregadas/filtradas. Totais da
origem, elegíveis, selecionados pelo produtor e convertidos permanecem **não
informados** quando o contrato não os fornece. A cardinalidade da tela não é usada
como cobertura da população de origem.

Detalhe e comparação preservam estados técnicos e revisão, valor textual, tipo,
unidade e precisão declarada. Inteiros e precisão acima de 2^53 não são truncados
na apresentação. Entradas, saídas e derivação aparecem separadas; `mentions`
permanece referência neutra. Métricas incompatíveis não recebem conversão,
ranking ou causalidade inferida. O download de dossier preserva o corpo recebido,
sem parse/reencodificação JavaScript que altere inteiros.

Execuções sem datas ou sem relações continuam alcançáveis. A linha do tempo conserva
a origem declarada/observada, apresenta fim sem início quando esse é o dado disponível
e não transforma observação em evento. O shell tem foco visível, skip link, retorno
de foco e reflow de página; tabelas bidimensionais ficam em regiões próprias.

O novo asset `parity02_p02_state.js` está na allowlist fixa do servidor e no wheel.
O glob de package-data existente bastou; não houve mudança de versão ou de
`pyproject.toml`. DOM textual inerte, CSP, origem e fronteiras de leitura foram
preservados e exercitados por negativos reais.

## Provas executadas

| Prova | Resultado e atribuição |
| --- | --- |
| Suíte integrada, Python 3.12.14, Linux, wheels instalados, fora do checkout | **98 PASS**, zero falhas/erros/skips, CODE_SHA acima |
| Mesma suíte com `-O` | **98 PASS**, zero falhas/erros/skips, mesmo CODE_SHA |
| Composição das 98 provas únicas | 12 SDK + 50 QA + 36 viewer; os 12 casos focais P02 estão incluídos |
| Módulo de estado Node | 22 verificações internas, incluídas no caso unittest focal; não somadas novamente |
| Instalação limpa | SDK sem viewer/R4; viewer sem R4; CLI/import; reconstrução e fontes intactas |
| Browser real instalado | **23 PASS_SCOPED**, Chromium 153.0.8010.0, Playwright 1.62.1, duas fontes e 28 execuções sintéticas |
| Segurança observada no browser | Zero erros de página; zero tentativas de requisição externa; hashes das fontes inalterados |
| Layout | 1440, 390 e 320 CSS px; text spacing; teclado e foco; seis screenshots sintéticos |
| Contraste | Amostragem de texto visível sobre cores sólidas registrada no JSON; não é certificação WCAG |
| Fronteiras | Auditoria de arquitetura PASS_SCOPED; protocolo/governança/workflows/runner/auditorias globais intactos |
| Revisão independente | `/root/independent_review`, sem autoria do delta; ver [REVIEW.md](REVIEW.md) |

São **98 testes únicos executados em dois modos**, não 196 casos diferentes.
Não se somam novamente seleções focais, checks Node internos, reruns, OS ou modos.
Recibos completos estão em [receipts/](receipts/) e capturas em [screenshots/](screenshots/).
O [mapa de aceite](ACCEPTANCE-MAP.md) liga cada requisito às provas.

### Ambiente de navegador e limites visuais

O Chromium padrão do Playwright não estava instalado no runtime. As tentativas de
aquisição dos dois artefatos oficiais retornaram ZIPs truncados. Um Chromium real
foi disponibilizado por `@sparticuz/chromium@153.0.0` em diretório isolado e lançado
com os defaults do Playwright, sem os argumentos adicionais desse pacote.
A ressalva ENV-01 de fontes foi **resolvida no escopo ensaiado**: Noto Sans CJK JP e
Noto Color Emoji foram disponibilizadas somente no ambiente de evidência; as mesmas
23 verificações passaram novamente no mesmo CODE_SHA. A revisão independente
confirmou os glifos japoneses, gregos e emoji das fixtures nas novas capturas.
O recibo de ambiente preserva os hashes e a limitação das imagens anteriores.
Não houve alteração do host ou da configuração
de rede, firewall, ACL ou sandbox.

Zoom nativo: **NOT_RUN**. CSS zoom: **não usado**. Certificação WCAG: **não alegada**.
As capturas e medições sustentam somente os cenários e larguras efetivamente ensaiados.

## CI real do CODE_SHA

[Workflow de produto 40526560195](https://github.com/thalesvalente/Atlas/actions/runs/40526560195):
quatro jobs Ubuntu/Windows × otimização 0/1 e o job de referência pública passaram.
O job de navegador legado falhou após cinco checks: esperava que a célula da métrica
contivesse somente `temperature`, mas ela agora apresenta também a identidade
`urn:environmental:quantity:temperature`. As etapas posteriores desse job foram
skipped; não são provas executadas desta candidata.

[Workflow Spec Kit 40526560524](https://github.com/thalesvalente/Atlas/actions/runs/40526560524):
CLI oficial 1.2.3 e integração passaram nos dois OS. A auditoria histórica rejeitou
as mudanças autorizadas P02 em `catalog.py`, `server.py` e `static/index.html`.
O mesmo diagnóstico foi reproduzido localmente. Nenhuma allowlist global foi relaxada.
Os nomes de outros arquivos autorizados historicamente por essa auditoria referem-se
à sua base antiga; não significam alterações desta frente contra `c2d00fb…`.

O [recibo CI](receipts/ci-code.json) conserva SHA, runs, jobs, conclusões e diagnóstico.
A P06 deve atualizar estritamente auditoria e harness, conectar o novo wrapper e
reexecutar na candidata de convergência. Os passos estão em
[P06-INTEGRATION.md](P06-INTEGRATION.md). Até lá, permanece o estado de verificação pendente.

## Entradas, método, revisão e autoridade

AGENTS, constituição, ADR-0001/0002 e features 001–003 orientaram o trabalho.
As etapas de especificação/clarificação, plano, checklist, tasks, análise, implementação,
verificação, convergência de escopo e revisão foram aplicadas; helpers versionados
foram executados com `SPECIFY_FEATURE_NO_PERSIST=1`. Não houve dispatch nativo
de todos os comandos Spec Kit. O CLI local estava ausente; a CI executou a versão
oficial 1.2.3. O [recibo do método](receipts/method-architecture.json) distingue isso.

Raciocínio solicitado: **Max**, fallback **xhigh**. Configuração efetivamente observável:
**REASONING_EFFECTIVE=UNVERIFIED**. O texto do prompt não altera o seletor.

Três subagentes nativos reais trabalharam com responsabilidades exclusivas:
`/root/navigation_state` (catálogo/servidor/estado), `/root/fixtures_browser`
(fixtures/QA), `/root/independent_review` (revisão somente leitura).
O coordenador escreveu shell e documentação e publicou os objetos Git.

Estudos integrais A/B/C/D: **INPUT_MISSING**. Os dois hashes C fornecidos estão no
handoff como alegações de entrada, sem verificação de bytes ausentes. Não foram
inventados requisitos C-UX. Nenhum handoff P03 congelado foi recebido ou integrado.

A [PR #5](https://github.com/thalesvalente/Atlas/pull/5) e seu merge registram o aceite
da ADR-0002 v1.0 como direção de estabilização. Os bytes históricos PENDING_HUMAN
foram conservados. O campo antigo `human_protocol_acceptance=PENDING` do helper
`clean_install.py` foi preservado no recibo original, com esta atribuição explícita;
ele não revoga a decisão posterior e não exige pedir o mesmo aceite novamente.

Não houve operação do host do usuário, leitura de acervo privado, mudança do Caderno,
import de R4, merge, release, deploy, promoção canônica ou aceite científico.
O próximo ato mínimo autorizado nesta coordenação é o handoff de objetos congelados
à P06; os ajustes globais pertencem a ela e não foram incorporados por esta frente.

## Navegação da entrega

- [HANDOFF.json](HANDOFF.json): base, entradas, paths, provas, revisão e atos P06.
- [MANIFEST.sha256](MANIFEST.sha256): hashes dos artefatos e delta, excluindo o próprio manifesto.
- [ACCEPTANCE-MAP.md](ACCEPTANCE-MAP.md): requisitos e evidências.
- [REVIEW.md](REVIEW.md): parecer independente e findings.
- [REPRODUCE.md](REPRODUCE.md): comandos de execução e limites.
- [P06-INTEGRATION.md](P06-INTEGRATION.md): montagem, assets, estilos, wheel e CI.
