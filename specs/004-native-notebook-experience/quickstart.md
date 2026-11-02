# Executar a experiência nativa

Pré-requisitos: versão desta PR instalada com packages/protocol e packages/atlas; Python no PATH; checkout confiável do R4 já funcional; Caderno central existente. Não instalar dependências privadas no viewer.

Comando Windows (a implementar nesta feature):

```powershell
& .\scripts\ABRIR-ATLAS-NATIVO.ps1 -CodeRoot 'H:\Atlas009-CA01' -NotebookRoot 'H:\R4-Caderno-Cientifico' -Output 'H:\Atlas-exports\consulta-nova'
```

O diretório Output deve ser novo e seu pai existente, fora do código e do Caderno. O launcher exporta a projeção original e abre a rota /notebook do novo Atlas. Não atualiza ledgers nem o HTML antigo. Para execução explícita:

```powershell
python -B tools/export_native_notebook.py --r4-code 'H:\Atlas009-CA01' --notebook-root 'H:\R4-Caderno-Cientifico' --output 'H:\Atlas-exports\consulta-nova'
python -m atlas_viewer serve --source 'H:\Atlas-exports\consulta-nova' --port 8765
```

Abra http://127.0.0.1:8765/notebook. Conferir revisão e contagens com o Atlas antigo; testar nó final da árvore, busca, tabela completa/valores nulos, recursos/dossiês e exportação. Conteúdo indisponível deve continuar indisponível. Registrar recibo local, sem publicar dados no GitHub. Não iniciar migração/limpeza.

Verificações de engenharia: scripts/run_checks.py, workflow native-notebook, Spec Kit setup_plan/setup_tasks/check_prerequisites com FEATURE_DIRECTORY desta feature e NO_PERSIST=1. Independent review e host real devem manter estado NOT_RUN/PENDING enquanto ausentes.
