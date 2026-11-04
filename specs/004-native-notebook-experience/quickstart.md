# Abrir o Caderno na interface nativa

Use o checkout candidato da [PR Draft #25](https://github.com/thalesvalente/Atlas/pull/25), que converge PR23/24 e os handoffs qualificados. O checkout original, o R4 e o Caderno ficam preservados; não trocar branches ou limpar workspaces de outras frentes.

## Abrir PRIMEIRO o Atlas NOVO (sem R4)

Este é o produto reengenheirado. O launcher principal não exige `CodeRoot`
nem `NotebookRoot`: ele recebe apenas pacotes explicitamente selecionados do
**protocolo público Caderno**, que já existam no computador.

```powershell
python -m pip install ./packages/protocol ./packages/atlas
& .\scripts\ABRIR-ATLAS.ps1 -Source 'CAMINHO_DO_PACOTE_CADERNO_COMPATIVEL'
```

Abre `http://127.0.0.1:8765/notebook`. `-View Protocol` apresenta as
fontes compatíveis com o protocolo sem payload nativo, na rota `/`.
`-NoOpen` mantém o servidor acessível sem abrir uma janela. Sem `-Source`,
a aplicação inicia vazia, sem criar registros ou simular dados reais.
`Ctrl+C` encerra o servidor iniciado.

**Limite atual explícito:** a raiz `H:\R4-Caderno-Cientifico` não é um
pacote do protocolo novo por si só. O Atlas **não importa R4, não migra
o acervo, nem lê automaticamente o armazenamento legado**. A conversão
de uma fonte legada é responsabilidade de um produtor externo autorizado.

## Leitura operacional do Caderno legado, sem passo manual de exportação

Para abrir **o Atlas NOVO** diretamente com o Caderno histórico existente,
sem executar o renderer HTML do R4:

```powershell
& .\scripts\ABRIR-ATLAS.ps1 `
  -LegacyCodeRoot 'H:\Atlas009-CA01' `
  -LegacyNotebookRoot 'H:\R4-Caderno-Cientifico'
```

O lançador usa `scripts/atlas_launch.py` e cria um único processo
**externo** com o adaptador público `tools/export_native_notebook.py`
para consultar a API R4 `project()`. O processo exportador termina, o
`atlas_viewer` instalado recebe o pacote do protocolo em cache temporário
e abre `http://127.0.0.1:8765/notebook`. Ao encerrar a sessão, somente
o cache próprio daquela execução é removido. Se a fonte mudar durante a
sessão, reinicie para obter uma nova projeção; não é leitura contínua em
streaming nem edição do Caderno.

O R4 é dependência **da origem legada confiável**, não do programa Atlas
instalado. A raiz indicada em `-LegacyNotebookRoot` precisa ser um
**workspace R4 válido** para `r4.campaigns.atlas.project()`, com
`R4-WORKSPACE.json`; uma pasta com arquivos do Caderno pode não atender
a esse contrato. Verifique com `Test-Path
'H:\R4-Caderno-Cientifico\R4-WORKSPACE.json'`. Um erro
`ATLAS_LEGACY_R4_WORKSPACE_MARKER_MISSING` bloqueia a leitura sem criar
dados novos. Outros erros do adaptador agora mostram apenas códigos
estruturados, sem conteúdo privado. Para a causa completa no próprio host,
execute `tools/export_native_notebook.py` diretamente com saída nova em
`$env:TEMP`. Não está autorizado copiar o leitor privado para o repositório
público. A presença e permissões das raízes `H:\` devem ser verificadas
no computador real, não presumidas em GitHub Actions.

## Compatibilidade LEGADA opcional: produzir pacote a partir de R4

## Preparar os dois pacotes públicos

Python 3.11+ e navegador são necessários. No ambiente Python escolhido, a instalação explícita do produto é:

```powershell
python -m pip install ./packages/protocol ./packages/atlas
```

O launcher não instala dependências automaticamente. O código R4 escolhido deve ser a instalação confiável já funcional; suas dependências são as do produtor, não do wheel do Atlas.

## Comando operacional

```powershell
& .\scripts\ABRIR-ATLAS-NATIVO.ps1 `
  -CodeRoot 'H:\Atlas009-CA01' `
  -NotebookRoot 'H:\R4-Caderno-Cientifico' `
  -Output 'H:\Atlas-exports\consulta-nova'
```

Esses caminhos correspondem à instalação histórica documentada, não a presença conferida neste CHAT. Ajuste-os somente à instalação real. O pai de Output deve existir; `consulta-nova` precisa estar ausente. Saída deve ficar fora do código e do Caderno. O comando reutiliza `r4.campaigns.atlas.project`, exporta pacote novo, inicia o Atlas instalado e abre `http://127.0.0.1:8765/notebook`. Ctrl+C encerra somente esse servidor. `-NoOpen` evita abrir a janela, e `-Port` seleciona outra porta disponível.

Nenhum ledger é escrito, nenhuma experiência executada, nenhuma aprovação promovida. Referências externas são metadados, não downloads. O produtor original continua disponível para abrir seus documentos no host.

## Etapas separadas

```powershell
python -B tools/export_native_notebook.py --r4-code 'H:\Atlas009-CA01' --notebook-root 'H:\R4-Caderno-Cientifico' --output 'H:\Atlas-exports\consulta-nova'
python -m atlas_viewer serve --source 'H:\Atlas-exports\consulta-nova' --port 8765
```

Também é aceito JSON da projeção já exportada: `--projection ARQUIVO_JSON --output DIRETORIO_NOVO`, em vez de `--r4-code/--notebook-root`. Não é HTML, não há flag synthetic nem ingestão silenciosa de diretórios.

## Acervo extenso e diagnóstico do limite agregado

O Atlas antigo pode exibir normalmente o Caderno, enquanto a representação intermediária
do Atlas novo excede 32 MiB porque `raw_json` e os campos de exibição repetem
informações. Na versão atual, o exportador tenta V2 zlib quando a soma dos JSONs
excede 32 MiB. **Não é uma alteração do limite de 32 MiB dos pacotes armazenados**:
o leitor verifica todos os chunks e impõe limites próprios de descompressão
(8 MiB por File, 256 MiB de representação lógica). Valores científicos, hashes,
revisão, contagem e ordem são preservados; não se trunca o acervo.

Atualize a branch, sem merge:
```powershell
git pull --ff-only
python -m pip install .\packages\protocol .\packages\atlas
& .\scripts\ABRIR-ATLAS.ps1 -LegacyCodeRoot 'H:\Atlas009-CA01' -LegacyNotebookRoot 'H:\R4-Caderno-Cientifico'
```

O lançamento normal confirma prontidão pela **página estática**, não pela leitura
integral da API em timeout de 2 segundos. A própria UI lê e verifica os dados
uma vez, sem retry concorrente do launcher. Para uma prova explícita sem abrir
navegador, use `-NoOpen -ProbeOnly`: essa opção realiza uma única leitura
integral da API com limite de tempo maior e encerra seu próprio servidor.

Se aparecer `NATIVE_COMPRESSED_AGGREGATE_LIMIT_NO_TRUNCATION`,
`NATIVE_LOGICAL_LIMIT_NO_TRUNCATION` ou `NATIVE_SINGLE_ENTRY_TOO_LARGE`,
o fail-closed é intencional. Preserve esse código para engenharia; não reduza o
acervo ou aumente quotas manualmente. O teste no host ainda é necessário para
confirmar que a representação real cabe na nova versão.

## Navegação e atualização

O menu Caderno nativo oferece árvore com busca de qualquer nó/zoom/pan/minimapa, registros, tabelas P03 paginadas, relações, recursos/dossiês, linha do tempo e cobertura. Detalhe distingue native_id, source_key e UID de consulta; valor original permanece exportável como JSON. Tabelas têm CSV protegido de fórmulas e JSON sem arredondamento.

`Verificar alterações` somente consulta o snapshot e sinaliza CHANGED; não aceita bytes novos automaticamente. `Atualizar snapshot` solicita reconstrução explícita do índice nas fontes já escolhidas. Nenhuma opção muda o Caderno. Para refletir uma nova revisão do próprio Caderno, exporte outro pacote novo e inicie o viewer com essa fonte explícita.

## Conferência local

Compare revisão/contagens com a projeção original; navegue até o último nó e linha, confira null, valores grandes, colisões, metadados de documentos e exportação completa. Mantenha logs/pacotes no host privado. Esta conferência é T016 e não foi simulada pelo teste Chromium de engenharia. Use o Atlas antigo como referência operacional; não retire arquivos ou implemente migração para concluir esse aceite.

No fechamento, P05 executou essa conferência no Caderno real e inspecionou as
capturas. A referência original de mesmo snapshot foi composta em scratch
privado com os assets originais, sem chamar build/save_lineage nem escrever no
Caderno; não é novo build oficial legado. A navegação por referências declaradas
inclui nó, registro, tabela, linha/evidência e retorno. Duas tabelas declaradas
vazias continuam vazias. Os recibos do HEAD final, a matriz e o checklist humano
estão em [final-close.md](final-close.md) e na conversa da PR #25; não herdar
qualificação para futuras alterações do produto ou do acervo.
