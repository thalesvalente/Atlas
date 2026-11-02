# Abrir o Caderno na interface nativa

Use um checkout atualizado desta PR23. O R4 e seu Caderno já existentes ficam onde estão; não trocar branches ou limpar workspaces de outras frentes.

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
instalado. Não está autorizado copiar o leitor privado para o repositório
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

## Navegação e atualização

O menu Caderno nativo oferece árvore com busca de qualquer nó/zoom/pan/minimapa, registros, tabelas P03 paginadas, relações, recursos/dossiês, linha do tempo e cobertura. Detalhe distingue native_id, source_key e UID de consulta; valor original permanece exportável como JSON. Tabelas têm CSV protegido de fórmulas e JSON sem arredondamento.

`Verificar alterações` somente consulta o snapshot e sinaliza CHANGED; não aceita bytes novos automaticamente. `Atualizar snapshot` solicita reconstrução explícita do índice nas fontes já escolhidas. Nenhuma opção muda o Caderno. Para refletir uma nova revisão do próprio Caderno, exporte outro pacote novo e inicie o viewer com essa fonte explícita.

## Conferência local

Compare revisão/contagens com a projeção original; navegue até o último nó e linha, confira null, valores grandes, colisões, metadados de documentos e exportação completa. Mantenha logs/pacotes no host privado. Esta conferência é T016 e não foi simulada pelo teste Chromium de engenharia. Use o Atlas antigo como referência operacional; não retire arquivos ou implemente migração para concluir esse aceite.
