# Resultado — ATLAS-PARITY-02-P03

**P03_COMPONENTS_VERIFIED_NOT_COMPOSED**
**VISIBLE_IN_MAIN_APP=false**

Entrega concreta publicada como [PR Draft #7](https://github.com/thalesvalente/Atlas/pull/7).
Código: `6c412c36e1dbe11711daa15c6d8727fbe94fa0ad`.
Árvore: `f9cac8cba86763c2ff98f883e33962648fc01004`.
Base: `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, tree
`5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`.

## O que foi entregue

Tabela semântica isolada com tipos, unidades, precisão declarada, ausências, ordenação e
filtro tipados. Strings numéricas/inteiros grandes preservados; números inteiros JS
inseguros recusados. Precisão não arredonda. Identidade acompanha a linha.

Projeção Python pura e renderer de metadados atuais: fonte+ID, File sem promoção semântica,
relações corroboradas e mentions separadas. Disponibilidade declarada/observada e digests
declarado/calculado são independentes. Nenhuma leitura de payload nos componentes.

Produto/documento rico só como candidato sintético declarado, com campos/seções de texto
inerte. HTML e URI não viram conteúdo ativo. Importar módulos não ativa UI. Harness próprio,
fixtures, testes e gate de navegador reproduzível estão nos paths P03 autorizados.

## Representabilidade

Contrato vigente fornece metadados, relações e PropertyValue tipado. Apresentação derivada
pode expor esses dados. Tabela genérica persistida, produto universal, documento rico e
coverage ledger exigem definição adicional; não foram introduzidos no Caderno.
Estudos A/B/C/D integrais e P01 pinado não foram recebidos. Hashes informados para C não são
tratados como prova de acesso ao estudo. Paridade com o legado não foi declarada.

## Evidência executada e reutilizada

| Verificação | Resultado e alcance |
|---|---|
| Focal Python | 35 métodos: 30 PASS,5 skips HTTP explícitos. |
| Node tabela | 42 casos PASS. |
| Node artefatos/documentos | 14 casos PASS. |
| Node renderers | 6 casos PASS com DOM recorder; não navegador. |
| Regressores selecionados | 117 métodos: 111 PASS,6 skips;4 HTTP baseline excluídos nominalmente. |
| Revisão independente | PASS_SCOPED;15 checks adicionais, oracle Decimal com 176 valores e 2 ausências. |
| Instalação offline | Wheels SDK/viewer,5 recursos P03 presentes, smoke -I -S sem R4 e fonte inalterada. |
| Preservação | 162 blobs baseline idênticos;28 arquivos oficiais Spec Kit conferidos. |

Os 3 wrappers Python reexecutam os casos Node. Focal, regressão e reruns se sobrepõem;
não são somados como testes únicos. SDK/QA e auditoria arquitetural da primeira rodada
foram reaproveitados nos mesmos bytes; viewer foi repetido após congelamento.

Revisor real `/root/p03_independent_review`, sem autoria do delta. Um finding P2 documental
foi corrigido: somente inteiros Number inseguros são detectáveis; perda decimal anterior
à entrada é irrecuperável e precisa ser evitada pelo transporte lexical.
Nenhum finding aberto. Os 25 hashes revisados foram ligados ao commit publicado em
`evidence/CODE-BINDING.json`.

## Limites materiais

- Sockets loopback recusados com EPERM: 5 HTTP P03 em skip e 4 HTTP baseline excluídos.
  Handler/parser foi exercitado sobre fluxo de bytes controlado, sem alegação de socket real.
- Chromium executável ausente: navegador, teclado real, layout e reflow NOT_RUN.
- Dependência jsonschema ausente: 1 teste SDK em skip.
- Build offline usou setuptools 84.1.0/wheel 0.48.0 disponíveis; equivalência com pin 80.9.0
  não verificada. Nenhum pin, rede ou sandbox alterado.
- Windows, host do usuário, composição, release, deploy, merge e ciência não atestados.
- CI por SHA: Spec Kit [40526464161](https://github.com/thalesvalente/Atlas/actions/runs/40526464161)
  SUCCESS no código6c412c36e1dbe11711daa15c6d8727fbe94fa0ad. Produto
  [40526464073](https://github.com/thalesvalente/Atlas/actions/runs/40526464073) em andamento
  na leitura após publicação: PENDING_EXTERNAL_RESULT. Nenhum desses resultados é
  atribuído ao commit documental posterior; fechamento registra checkpoint próprio.

Falhas intermediárias foram registradas: wrapper Node corrigido para TAP com contagem real;
negativo de relação ajustado; erros de setup HTTP mantidos como impedimentos do ambiente,
sem apresentar sucesso. Não houve contorno ou alteração de permissões.

## Método e ownership

Spec Kit 1.2.3: leitura de governança, especificação/clarificações/plano/checklist/tasks/análise,
implementação, verificação, convergência e revisão independente. Helpers reais existentes
foram executados com SPECIFY_FEATURE_NO_PERSIST=1; aplicação das skills foi manual, sem
alegar dispatch nativo ou CLI instalado. `.specify/feature.json` não foi escrito.

Três subagentes reais: `/root/p03_tables` (tabela), `/root/p03_artifacts` (metadados e testes
atribuídos), `/root/p03_independent_review` (revisão sem autoria). Coordenador: harness,
documentação, binding e publicação. Raciocínio solicitado Max/fallback xhigh;
**REASONING_EFFECTIVE=UNVERIFIED**, por ausência de telemetria do seletor.

Todo delta está no ownership P03. Protocolo, shell, catálogo, servidor, package-data,
workflows e histórico ADR permanecem byte a byte. Direção ADR-0002 aceita na PR #5 foi
reconhecida, sem pedir novamente o aceite e sem promover novos gates.

## Handoff

P06 recebe código por SHA e o commit documental separado, consulta INTEGRATION-CONTRACT,
compõe em sua candidata respeitando P02 e executa HTTP/browser reais. Componentes estão
prontos para essa composição; a aplicação principal continua sem ativá-los.
