# Atlas

**Interface local para explorar registros científicos, sem alterar o acervo.**

Base consolidada: [main em `8f8fe01`](https://github.com/thalesvalente/Atlas/commit/8f8fe01c3041361aa2607194d66af6a640d834ad).
O fechamento da [PR #25](https://github.com/thalesvalente/Atlas/pull/25) e sua
[matriz e checklist](specs/004-native-notebook-experience/final-close.md) são recibos
históricos de engenharia. A [PR #39 recebeu aceite restrito de apresentação](https://github.com/thalesvalente/Atlas/pull/39#issuecomment-6715128638);
isso não amplia os demais gates humanos de paridade OLD/NEW, promoção ou release.
As disposições das contribuições anteriores e os reparos posteriores estão no
[handoff de convergência](docs/missions/atlas-convergence-18-20261108/ATLAS-CONVERGENCE-HANDOFF.md).

O Atlas possui uma experiência **nativa do Caderno**, além da consulta pelo protocolo público. A projeção original do R4 é reutilizada por um adaptador externo; a interface usa DOM/SVG e o componente P03. O R4 e o Caderno existentes permanecem intactos. A integração técnica não concede release, promoção científica ou autorização de migração/limpeza.

## Iniciar o Atlas NOVO — independente do R4

A aplicação reengenheirada é `atlas-viewer`, no repositório **thalesvalente/Atlas**.
Instale os dois pacotes do checkout selecionado (Python 3.11+):

```powershell
python -m pip install ./packages/protocol ./packages/atlas
```

Abra o **produto novo**, sem executar/importar R4 ou exigir o código Atlas009:

```powershell
& .\scripts\ABRIR-ATLAS.ps1 -Source 'CAMINHO_DO_PACOTE_CADERNO_COMPATIVEL'
```

O navegador abre **http://127.0.0.1:8765/notebook**. `-View Protocol`
abre a visão genérica do protocolo em `/`; `-Source` pode listar até
16 pacotes explicitamente escolhidos. Sem `-Source` a interface abre **vazia**,
sem inventar um acervo. O servidor fica somente em 127.0.0.1 e encerra
com Ctrl+C. O comando `python -m atlas_viewer serve --source ...` é a
alternativa direta, sem PowerShell.

**Acesso imediato ao Caderno legado no Atlas novo (sem migração persistente):**

Quando os registros ainda estão no formato histórico privado, você pode abrir
**o novo produto com dados reais em uma só execução**, sem gerar manualmente
um pacote ou chamar o renderer antigo:

```powershell
& .\scripts\ABRIR-ATLAS.ps1 `
  -LegacyCodeRoot 'H:\R4-produtor-atualizado' `
  -LegacyNotebookRoot 'H:\R4-Caderno-Cientifico'
```

A compatibilidade funciona com um **adaptador externo em processo separado**
(`tools/export_native_notebook.py`, reutilizando a API produtora
`r4.campaigns.notebook_query_projection.project`). O checkout deve conter essa
API; uma revisão que ofereça somente o renderer histórico será recusada.
O Atlas instalado continua independente e consome apenas o pacote derivado,
em diretório temporário da sessão. O cache é removido somente após o servidor
encerrar, preservando os arquivos originais. Essas são raízes históricas
conferidas somente no host e revisão registrados no recibo; selecione um código R4 confiável já funcional.
Não há importação de `r4.*` no pacote `atlas_viewer`, nem
migração/inserção de ciência no Caderno. Para atualização após novas gravações,
encerre e reabra a sessão (nova projeção consistente).

A comparação funcional, visual e de integridade no Windows foi observada na
candidata de fechamento, com recibos privados e revisão de mesmo snapshot.
CI pública usa dados de engenharia; não recebe o acervo nem concede aceite humano.

**O que é uma fonte:** um pacote RO-Crate/Caderno no perfil público suportado,
não a pasta do Caderno legado do R4 nem `ATLAS-ATUAL.html`. A rota `/notebook`
exige o payload opcional `atlas-native-view/1`; para outros pacotes válidos,
use `-View Protocol`. Não há leitura automática de pastas, descoberta de
worktrees, migração ou conversão dentro do Atlas.

## Adaptador legado OPCIONAL para ver o Caderno antigo no Atlas NOVO

Para consultar registros ainda armazenados apenas no formato **legado do R4**,
o produtor antigo pode exportar um pacote pelo **adaptador separado**.
Isso não é o mecanismo de inicialização do novo produto, não instala R4
dentro do Atlas e não altera o Caderno. Requisitos adicionais desta etapa
opcional: código R4 confiável já funcional e a raiz do Caderno central.

```powershell
python -m pip install ./packages/protocol ./packages/atlas
```

Na raiz do checkout Atlas atualizado, execute:

```powershell
& .\scripts\ABRIR-ATLAS-NATIVO.ps1 `
  -CodeRoot 'H:\R4-produtor-atualizado' `
  -NotebookRoot 'H:\R4-Caderno-Cientifico' `
  -Output 'H:\Atlas-exports\consulta-nova'
```

Os caminhos dos exemplos devem ser substituídos pelas raízes confiáveis do host.
O pai de Output precisa existir; a pasta final deve ser **nova**, fora do código
e do Caderno. O launcher não instala software automaticamente. Ele usa
`r4.campaigns.notebook_query_projection.project`, inicia **o Atlas NOVO instalado**
e abre `http://127.0.0.1:8765/notebook`. `-NoOpen` apenas deixa de abrir o navegador;
Ctrl+C encerra o servidor criado pelo launcher. O fluxo entre aplicações também
aceita JSON previamente exportado pelo produtor via `--projection`; o viewer
consome somente o pacote e não precisa do renderer R4.

A interface oferece árvore estrutural com busca integral, pan/zoom/minimapa, registros e filtros, tabelas paginadas, recursos/dossiês, relações, linha do tempo, cobertura e exportação completa. `native_id` nulo permanece nulo; chaves estruturais e UIDs de consulta não viram identidade científica. Valores grandes, null e chave ausente são preservados. Coleções não interpretadas continuam acessíveis com seu JSON original.

O botão **Verificar alterações** não aceita uma fonte modificada como nova ciência. **Atualizar snapshot** reconstrói explicitamente o índice das fontes já selecionadas. Para atualizar a revisão do próprio Caderno, exporte outro pacote novo. Links documentais externos são apresentados como referências, sem download ou execução automática.

[Guia operacional e instalação](specs/004-native-notebook-experience/quickstart.md) · [Spec](specs/004-native-notebook-experience/spec.md) · [Plano](specs/004-native-notebook-experience/plan.md) · [Tasks](specs/004-native-notebook-experience/tasks.md) · [Análise e limitações](specs/004-native-notebook-experience/analysis.md).

## Referência original preservada

O Atlas R4 antigo continua referência operacional até equivalência conferida no acervo real e aceite humano. Para abrir a visualização já gerada na instalação existente:

```powershell
& .\scripts\ABRIR-ATLAS-ORIGINAL.ps1 -OpenExisting
```

`-CodeRoot` e `-NotebookRoot` permitem indicar explicitamente as raízes. A rota `/original` agora é apenas orientação inerte. A prévia anterior que executava HTML selecionado foi encerrada: não é necessária para a integração nativa e não é um leitor seguro genérico de HTML. Nenhum HTML histórico ou dado do operador foi excluído.

## Separação de responsabilidades

| Unidade | Responsabilidade |
|---|---|
| `packages/protocol` — caderno-protocol | Perfil, validação e leitura dos pacotes; independente da UI e de produtores |
| `packages/atlas` — atlas-viewer | Consulta, projeções derivadas e UI; sem imports R4 |
| `tools/export_native_notebook.py` | Adaptador externo, opt-in, da projeção da instalação R4 escolhida |
| Outros produtores | Exportação pelo mesmo contrato público |

O payload de apresentação `atlas-native-view/1` é conteúdo de Files verificados no perfil já existente; não redefine o protocolo científico ou inventa atividades para nós legados. Campos originais são reconstruídos e conferidos por digest. O wheel do Atlas não inclui o produtor privado. Fontes somente leitura, saídas derivadas em diretório novo, sem providers, bancos obrigatórios ou SaaS.

[ADR-0001](docs/architecture/ADR-0001-atlas-protocol-producers-storage.md) e [contrato A/B](docs/coordination/AB-CONTRACT.md) permanecem vinculantes. Digest é integridade observada, não autenticidade, aprovação científica ou confirmação de presença dos documentos externos.

A [ADR-0002 v1.0 foi aceita como direção de estabilização](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421), no escopo e versão daquele recibo. O [descriptor externo 0.2.0 foi aprovado em escopo opcional](https://github.com/thalesvalente/Atlas/pull/15#issuecomment-6539419419) e continua preservado: Native View Files é outra interface, sem implementação ou revogação implícita desse contrato. A proposta ARC-09/0.2.1 continua congelada e depende de decisão humana própria.

## Consulta pelo protocolo existente

```sh
atlas serve --source CAMINHO_DO_PACOTE
atlas inspect CAMINHO_DO_PACOTE
atlas dossier --source CAMINHO_DO_PACOTE
caderno-validate CAMINHO_DO_PACOTE
```

`--source` é repetível até 16 fontes. Servidor somente loopback; requisições não escolhem novos paths. A rota `/` conserva comparação, métricas tipadas, detalhes, linhagem e dossiê do read model público. `/notebook` consome os payloads nativos de apresentação quando presentes. Fonte sem payload nativo continua válida na visão do protocolo.

O exemplo `examples/environmental/sample` é explicitamente inventado para demonstração de engenharia, não seu Caderno real. [PoC reproduzível](docs/poc-reproducible.md).

## Intercâmbio e limites

RO-Crate 1.3 + Process Run Crate 0.6 + Caderno 0.1.0a1. [Perfil](docs/protocol/0.1.0a1.md), [pesquisa](research/protocol-options.md) e [conformidade](docs/protocol/conformance.md) registram os limites. Versões/contextos desconhecidos e payloads inválidos são recusados. A extensão `.eln` sozinha não comprova conformidade.

Metadados: 2 MiB; payload individual: 8 MiB; agregado: 32 MiB; ZIP: 64 MiB/4096 membros, razão máxima200. O exportador fragmenta Files sem truncar entradas; excesso de quota é erro explícito. A apresentação admite até100000 ocorrências e10000 nós dentro desses tetos. O navegador mostra janelas paginadas, sem descartar a população carregada. Não há certificação de segurança de host adversarial.

## Verificação de engenharia

O projeto contém Spec Kit1.2.3, scripts oficiais e10 skills em `.agents/skills`. A feature004 usa `SPECIFY_FEATURE_DIRECTORY` explícito e `SPECIFY_FEATURE_NO_PERSIST=1`; não altera o seletor global.

```sh
python scripts/run_checks.py
python -O scripts/run_checks.py
python -m unittest discover -s tests/viewer -p 'test_native_notebook*.py' -v
```

As Actions cobrem Windows/Ubuntu normal/-O, Spec Kit, instalação independente dos pacotes e Chromium real. O cenário nativo executa exporter/SDK/servidor/componentes e preserva screenshots/report. Dados de engenharia não substituem comparação no Caderno privado. O comando operacional no host e revisão independente no SHA final permanecem gates separados, registrados nas tasks e na PR.

Nenhuma licença de software foi concedida por esta candidata; referências públicas preservam seus avisos em [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Sem merge, release, deploy, promoção ou limpeza implícitos.
