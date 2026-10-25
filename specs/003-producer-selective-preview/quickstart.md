# Guia de uso da feature 003
O viewer não importa código nem formatos privados de produtores. A saída do produtor deve ser um pacote Caderno 0.1.0a1 derivado, selecionado e validado em contexto privado.

Depois que o produtor gerar e validar um pacote pequeno, abra-o com a instalação existente:

```powershell
$viewer = 'G:\projetos\meu\atlas\.local\install-02\viewer-env\Scripts\python.exe'
$source = 'G:\projetos\meu\atlas\.local\campaigns-preview\rnf-pilot-01'
& $viewer -I -m atlas_viewer inspect $source
& $viewer -I -m atlas_viewer serve --source $source --port 8765
```

Origem, exportador, SHA e instruções específicas permanecem no guia **privado** R4. Nenhuma leitura direta do R4 é realizada pelo Atlas. Esta feature não cria nem apaga arquivos no host do operador.
