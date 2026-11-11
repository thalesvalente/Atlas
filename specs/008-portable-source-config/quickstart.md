# Configurar fontes locais do Atlas

Uma fonte é um pacote compatível já exportado, um arquivo de metadados ou um
arquivo ZIP/ELN aceito pelo protocolo. A configuração apenas lembra os caminhos
escolhidos: ela não copia o acervo, não converte fontes e não instala R4.

## Primeira configuração

Com os pacotes Atlas e protocolo instalados no Python selecionado, execute na
raiz do checkout:

```powershell
& .\scripts\ABRIR-ATLAS.ps1 -Configure -Source 'CAMINHO_DO_PACOTE_COMPATIVEL'
& .\scripts\ABRIR-ATLAS.ps1
```

O primeiro comando valida o pacote, salva a seleção e encerra. O segundo abre
o Atlas com essa seleção. Se o pacote não possuir apresentação nativa, use a
visão do protocolo: `& .\scripts\ABRIR-ATLAS.ps1 -View Protocol`.

Pelo Python, inclusive no Linux:

```sh
python -m atlas_viewer config set --source CAMINHO_DO_PACOTE_COMPATIVEL
python scripts/atlas_launch.py
```

`python -m atlas_viewer serve` é a entrada direta do servidor. Nenhum dos
launchers instala pacotes automaticamente ou pede seleção interativa durante
uma execução automatizada. Sem seleção salva, abrem um catálogo vazio legítimo.

## Selecionar várias fontes

```powershell
& .\scripts\ABRIR-ATLAS.ps1 -Configure -Source @('PACOTE_A', 'PACOTE_B')
```

```sh
atlas config set --source PACOTE_A --source PACOTE_B
```

São aceitas até 16 fontes distintas. Cada configuração substitui a lista inteira;
não há acréscimo ou mescla implícita. Caminhos duplicados, incluindo o diretório
de um pacote e seu próprio `ro-crate-metadata.json`, são recusados. Caminhos com
espaços e caracteres Unicode são aceitos; mantenha cada valor entre aspas quando
o shell exigir.

## Onde fica o arquivo

| Plataforma | Local padrão |
|---|---|
| Windows | `%LOCALAPPDATA%\Atlas\sources.json`; sem `LOCALAPPDATA`, `AppData\Local\Atlas\sources.json` sob o diretório do usuário |
| Linux | `$XDG_CONFIG_HOME/atlas/sources.json`; sem essa variável, `~/.config/atlas/sources.json` |

O arquivo é JSON UTF-8 com esquema restrito:

```json
{
  "version": 1,
  "sources": ["../pacotes/caderno A", "../pacotes/caderno B"]
}
```

Os comandos de configuração gravam caminhos absolutos. Ao editar o JSON
manualmente, um caminho relativo é resolvido a partir da pasta do próprio
arquivo, independentemente da pasta em que o Atlas foi iniciado. Caminhos
relativos recebidos por `--source` ou `-Source` são resolvidos a partir da pasta
atual do terminal. A ordem da lista é preservada.

Também é possível escolher um arquivo fora do repositório e fora dos pacotes:

```powershell
$AtlasConfig = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Atlas\fontes-alternativas.json'
& .\scripts\ABRIR-ATLAS.ps1 -Configure -Config $AtlasConfig -Source 'PACOTE_A'
& .\scripts\ABRIR-ATLAS.ps1 -Config $AtlasConfig
```

```sh
atlas_config="${XDG_CONFIG_HOME:-$HOME/.config}/atlas/fontes-alternativas.json"
atlas config set --config "$atlas_config" --source PACOTE_A
atlas serve --config "$atlas_config"
```

Esses exemplos usam a pasta local do usuário para o arquivo alternativo, mesmo
quando executados na raiz do checkout. No Linux, `XDG_CONFIG_HOME`, quando
definido, deve ser absoluto. Substitua `PACOTE_A` pela fonte deliberadamente
escolhida. Não grave a configuração privada no Git, dentro de um pacote
científico ou em lugar de outro documento.

## Precedência e uso temporário

| Invocação | Seleção utilizada |
|---|---|
| `--source` / `-Source` presente | Somente as fontes da chamada; não lê nem mescla configuração |
| Sem fonte explícita, com `--config` / `-Config` | Somente o arquivo indicado; arquivo ausente ou inválido é erro |
| Sem fonte explícita nem arquivo indicado | Configuração padrão; se não existir, catálogo vazio |
| `--no-config` / `-NoConfig` | Somente fontes explícitas da chamada; sem fontes, catálogo vazio |

`--config` e `--no-config` não podem ser usados juntos. Uma fonte explícita
continua permitindo consulta temporária quando um arquivo de configuração está
danificado. Por exemplo:

```powershell
& .\scripts\ABRIR-ATLAS.ps1 -Source 'PACOTE_TEMPORARIO'
& .\scripts\ABRIR-ATLAS.ps1 -NoConfig
```

Esses comandos não alteram a configuração salva. O processo filho recebe a
seleção já resolvida, inclusive quando vazia; não recarrega outro arquivo.

## Consultar, substituir ou limpar a seleção

```powershell
& .\scripts\ABRIR-ATLAS.ps1 -ShowConfig
& .\scripts\ABRIR-ATLAS.ps1 -ShowConfig -ShowPaths
& .\scripts\ABRIR-ATLAS.ps1 -Configure -Source 'NOVO_CAMINHO_DO_PACOTE'
& .\scripts\ABRIR-ATLAS.ps1 -ClearSources
```

```sh
atlas config show
atlas config show --show-paths
atlas config set --source NOVO_CAMINHO_DO_PACOTE
atlas config clear
```

Adicione `-Config` ou `--config` em cada chamada para operar um arquivo
específico. A consulta padrão esconde os caminhos. A opção `ShowPaths` é uma
solicitação local de exibição; sua saída não deve ser publicada. A consulta
continua disponível quando uma fonte foi movida, porque lê somente a
configuração. Limpar a seleção grava `"sources": []`; nenhum pacote é excluído.

## Trocar de computador ou de disco

1. Prepare o checkout da candidata escolhida e um ambiente Python 3.11+ próprio
   para o Atlas. Instale `packages/protocol` e `packages/atlas` nesse ambiente,
   seguindo o procedimento de instalação aprovado para a máquina. Ative o
   ambiente antes de usar o launcher PowerShell, que procura `python` no `PATH`.
2. Disponibilize o pacote compatível no local escolhido. Esta etapa de transporte
   é externa ao Atlas e não é executada pelos comandos de configuração.
3. Execute `-Configure -Source 'NOVO_CAMINHO'` ou
   `atlas config set --source NOVO_CAMINHO`. Não é necessário editar scripts.
4. Abra novamente o launcher. Para um conjunto portátil com caminhos relativos
   editados no JSON, preserve a relação entre as pastas e indique o arquivo com
   `--config` / `-Config`.

O arquivo de configuração não contém o pacote nem confere identidade ou aceite
científico. O Atlas não procura o disco antigo nem tenta adivinhar o novo local.

## Erros e recuperação

| Situação | Ação |
|---|---|
| Fonte movida ou removida | Salve novamente a seleção inteira com o caminho correto |
| Arquivo explicitamente indicado ausente | Crie a seleção nesse caminho com `config set` / `-Configure` |
| JSON malformado, versão desconhecida ou arquivo alheio | Preserve o arquivo e corrija-o manualmente ou escolha um novo `--config`; a gravação recusa sobrescrevê-lo |
| Pacote inválido ou incompatível | Selecione um pacote válido; a configuração não reescreve o conteúdo científico |
| Mais de 16 fontes ou duplicação | Corrija a lista explicitamente escolhida |
| Falha de acesso ou de gravação | Escolha um local permitido para a configuração; falhas anteriores à troca atômica preservam os bytes anteriores |
| Launcher novo com pacote instalado antigo | Atualize os dois pacotes no ambiente escolhido, conforme o procedimento de instalação da máquina |

Os erros de operação informam códigos sem divulgar caminhos locais. Não há
fallback para outras fontes. Fontes são abertas somente para leitura; a gravação
de preferências usa arquivo temporário exclusivo e troca atômica no mesmo
diretório. Configuração não é um mecanismo de backup dos dados.

## Adaptador legado opcional

Os parâmetros existentes `-LegacyCodeRoot` e `-LegacyNotebookRoot` continuam
explícitos e o adaptador permanece fora do processo Atlas. Uma chamada somente
com essas raízes não herda a seleção padrão. Fontes adicionais podem ser
indicadas por `-Source` ou por `-Config`, respeitando o teto de 16 que inclui o
pacote temporário do adaptador.

Os modos de configuração não aceitam raízes legadas: a projeção temporária
nunca é salva como preferência. O produto com um pacote compatível existente
continua funcionando sem R4 instalado.

## Validação desta candidata

Os testes usam somente pacotes sintéticos e diretórios temporários. O módulo
`test_native_notebook_source_config_launcher.py` cobre gravação/reutilização,
mudança de local, precedência, catálogo vazio, relativos, Unicode, erros,
integração legada delimitada e execução real dos launchers quando os runtimes
PowerShell 5.1/7 estão disponíveis. Um `SKIP` por runtime ausente não equivale a
teste aprovado. O recibo no computador Windows do operador permanece
`LOCAL_TEST_NOT_RUN` até a execução do handoff.
