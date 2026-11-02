# Abrir o Caderno na interface nativa

Use um checkout atualizado desta PR23. O R4 e seu Caderno já existentes ficam onde estão; não trocar branches ou limpar workspaces de outras frentes.

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
