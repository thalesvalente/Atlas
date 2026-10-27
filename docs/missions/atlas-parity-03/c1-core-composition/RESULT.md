# ATLAS-PARITY-03-C1 — composição mínima C0 e reparo dos gates globais

`orq.phase@llm-sec,agentic-pac/seai.qa:`

## Resultado verificado e fechamento por SHA

Composição executável verificada em **`af393e4c0cca19161f49bf9d847bd22617be15fb`**, árvore **`e2a5731d0057f1676e4112d57061773a72e4fc6e`**,
na [PR Draft #11](https://github.com/thalesvalente/Atlas/pull/11), branch
`integrate/atlas-parity03-c1-core-20261027`. Os três workflows desse código
terminaram **success**, os cinco cenários browser passaram e a revisão nativa
independente não tem finding bloqueante.

Este arquivo integra um commit documental posterior ao código acima. Um commit
não pode incorporar seu próprio SHA nem os resultados de uma execução que ele
ainda vai provocar. Por isso, o **recibo terminal externo na PR #11** identifica
o SHA/tree que contém este documento, seus três runs novos, os artifacts e a
revisão final somente leitura. Somente após esse recibo completo o resultado da
missão é **C1_CORE_CANDIDATE_READY**. Na ausência de qualquer gate, o resultado
externo deve ser **C1_BLOCKED_EXACT**, com a condição concreta. Evidência do código
acima nunca é atribuída ao commit documental.

## Composição e entradas

A baseline é `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, árvore
`5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`, confirmada em main no preflight.
O merge `4bfe0040c273d35719fc6e3de5e81d1fe9e40b65`, árvore
`d02432046d4bb7945cfd39581f674d7252bc415b`, conserva três pais ordenados:
baseline, head documental P02 `db6e8b64c28e756d0a2ff4fd1cd90f404c6c0533`
e head documental P06 `9b0a500b6612d260a9f9bd8a4c8da1be4841cf48`.
Os códigos P02 `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990` e P06
`d21d8a490b89995ae5707a7a53b469685416a383` permanecem ancestrais.
Não houve conflito, squash, rebase ou alteração dos heads de origem pela missão.

INPUT-SHAS.json registra árvores, pais, paths e hashes dos manifests. Os
manifests de origem validam **55/55 P02 e 22/22 P06** nos respectivos heads e no
merge puro. No overlay C1, **53/55 e 15/22** permanecem idênticos: nove desvios
autorizados estão enumerados em MERGE-TOPOLOGY.json com justificativa e prova
nova. Os manifests históricos não foram reescritos para esconder esses deltas.
Os links CODE→DOC distinguem os hashes documentais que ainda não existiam nos
commits de código testados.

## Reparos e comportamento resultante

A auditoria mantém o default estrito e separa os opt-ins histórico e P02. A nova
autorização fixa exatamente catalog.py, server.py e static/index.html aos blobs
do código P02; não aceita exclusões arbitrárias ou prefixos de diretório. Todo
`packages/protocol/**` é comparado à baseline, inclusive adições e remoções.
As negativas de protocolo, constituição, ADRs, skills, remoções, siblings e bytes
não congelados são exercitadas nos dois modos Python.

H06-01/02/03 passaram a usar fonte+ID como identidade: `data-run-key` é comparado
a `JSON.stringify([sourceId, runId])`, com unicidade explícita. Nome e identificador
da métrica são conferidos em elementos distintos; valor, ausência, tipo, unidade
e precisão continuam obrigatórios. Comparações usam `th[scope="row"]` e mapeiam
os valores pelas identidades dos cabeçalhos. O oráculo não replica a ordenação do
produto. Os três cenários legados voltam a executar e a produzir recibos próprios.

A troca P06 respeita o binding global P02: snapshot novo expira todas as seleções
e o detalhe antigos; B conserva seus bytes e exige uma nova seleção explícita no
scope novo. O RED foi reproduzido no asset de estado real antes da correção do
harness; o runtime congelado permaneceu intacto. O browser real confirmou a nova
expectativa separadamente da contraprova Node.

Os consumidores Actions são criados em RUNNER_TEMP, fora do checkout. A prova
SDK sem viewer/R4 e viewer sem R4 antecede a instalação de jsonschema 4.25.1 como
ferramenta de teste. O runner instalado exige imports externos, checkout limpo,
IDs únicos, zero skips e propagação explícita de `-O` com `-I`. Os quatro assets
wheel/instalado/HTTP conferem com Git, assim como os 22 arquivos usados no build.

## CI do código composto

| Workflow | Run | Estado terminal |
|---|---|---|
| [ATLAS021 candidate verification](https://github.com/thalesvalente/Atlas/actions/runs/40549157553) | `40549157553` | `success` |
| [ATLAS003 Spec Kit contract checks](https://github.com/thalesvalente/Atlas/actions/runs/40549157542) | `40549157542` | `success` |
| [ATLAS-PARITY-02 P06 frozen-boundary QA](https://github.com/thalesvalente/Atlas/actions/runs/40549157548) | `40549157548` | `success` |

A coleção observada tem **122 casos únicos: 12 SDK + 74 QA + 36 viewer**.
Os mesmos casos passaram em Ubuntu/Windows × normal/`-O`, sem falhas, erros ou
skips. As quatro execuções, as seleções focais P06 e os checks browser não são
somados como novos unittest. A lista de IDs e seu hash estão nos recibos.
"Zero skips" qualifica essa coleção; não transforma o escopo offline histórico
do comparador externo RO-Crate em certificação integral de outro perfil.

Spec Kit **1.2.3** foi executado nos dois sistemas com integração Codex,
28 arquivos gerenciados intactos, dez skills e seis helpers protegidos. Features
003/004 são resolvidas com `SPECIFY_FEATURE_NO_PERSIST=1`; o ponteiro global não
foi gravado. A auditoria P06 confirma 64 arquivos protegidos nos quatro ambientes.

| Jornada browser | Checks executados | Requisições externas | Erros de página |
|---|---:|---:|---:|
| Troca válida P06 | 14 | 0 | 0 |
| Legado adversarial | 24 | 0 | 0 |
| Referências relacionadas | 23 | 0 | 0 |
| Legado normal | 20 | 0 | 0 |
| Explorador P02 C0 | 23 | 0 | 0 |

P02 foi executado por `atlas_parity02_p02_run_browser.py` no consumidor instalado,
com Chromium **151.0.7922.34** e Playwright **1.62.1**. O artifact
contém JSON, recibo de fontes e **seis PNGs** com hashes conferidos, além das
provas de reflow, teclado e foco. Fontconfig confirma a cobertura CJK/emoji das
fontes selecionadas; nomes, arquivos e SHA-256 reais estão em CI-EVIDENCE.json.
Fontes sintéticas permanecem byte-idênticas; na troca P06, apenas a mutação
deliberada do driver sintético é aceita, com bytes finais esperados conferidos.

## Tentativa anterior e reparo de provisionamento

R1 `df56eb6338626d1671d1882d0d745c02a1f48406` teve 14/15 jobs success.
O run de produto 40546244411 foi cancelled no job 122337532297, step
`Install pinned browser test tooling`: download adicional fonts-noto-cjk de
61,2 MB atingiu o limite de 15 minutos antes das jornadas browser.
R2 removeu somente duas linhas apt redundantes. As fontes CJK/emoji já haviam
sido disponibilizadas pelo provisionamento Playwright, e a prova obrigatória de
glifos/hashes permaneceu. O cancelamento e seus efeitos não foram reclassificados
como PASS; o histórico está em receipts/r1-terminal-and-r2-repair.json.

## Revisão, integridade e limites

Três subagentes nativos reais foram usados com responsabilidades separadas:
topologia/auditoria, CI/browser e revisão independente. O revisor
`/root/independent_review` não teve autoria no delta; seu parecer por SHA e a
inspeção de artifacts estão em INDEPENDENT-REVIEW.md. A revisão do futuro head
documental fica vinculada ao recibo externo final, sem transferência de veredito.

Runtime P02, protocolo, fixtures P02, exemplos e fronteiras protegidas conservam
os bytes congelados. P01/P03 não foram integrados e nenhum pacote privado P04 ou
acervo R4 foi usado. ARC-01–09 e a independência do Caderno permanecem preservados.
A direção ADR-0002 já aceita é reconhecida sem reescrever seu histórico.

Validade técnica, integridade por hashes, autenticidade e aprovação científica
continuam separadas. Não houve operação no host do usuário, merge em main,
release, deploy ou promoção canônica. A PR permanece Draft. Para P02:
`native_zoom=NOT_RUN`, `css_zoom_used=false`, `wcag_certification=false`.
O CSS200 do cenário legado de referências é registrado somente naquele cenário.
`REASONING_EFFECTIVE=UNVERIFIED`: o seletor Max solicitado não é observável.

## Manifesto e recibos publicados

MANIFEST.sha256 cobre os 283 arquivos da árvore candidata versionada,
excluindo somente ele próprio. Os digests dos artifacts Actions e os hashes das
capturas P02 estão nos recibos, vinculados ao SHA executado; os PNGs C1 foram
publicados nos artifacts dos runs correspondentes. Os oito documentos exigidos
e os recibos JSON brutos/consolidados estão neste diretório.
