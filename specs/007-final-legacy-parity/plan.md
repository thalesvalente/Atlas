# Plano incremental

Reusar leitor Native View, projeção preservada, testes e componentes aprovados.
O incremento anterior teve P00 como writer exclusivo. Nesta continuação,
P01 escreve somente interface/testes Atlas, P02 consumidores/testes R4 e P03
audita sem escrever nos arquivos auditados. P00 integra e mantém estes artefatos.

1. Autenticar fontes/SHAs e executar Spec Kit instalado sem instalar ferramentas,
   sem trocar feature.json e sem reconstruir inventários válidos.
2. Acrescentar CSV tipado em native_legacy_model.js, integrado à tabela existente.
   Cada célula é envelope JSON com tipo/presença e token original, sem Number.
   Linha original completa e identidade estrutural acompanham a exportação.
3. Acrescentar tools/verify_native_parity.py, oráculo offline com pins explícitos.
   Reusar read_source/restore_projection; resultados de dados nunca qualificam UI.
4. RED/GREEN, suíte existente, instalação local sem R4 e CI no SHA publicado.
5. QA não autora, matrizes privadas, patch R4 proposto separado e rollback.

Sem nova rota HTTP, dependência, worktree, mudança de schema, execução de produtor,
migração, exclusão científica, merge, release ou deploy.

## Continuação P01/P02 — escopo congelado

Reusar a candidata instalada #39, os relatórios e inventários delimitados.
P01 reconcilia revisão/pins/processos e produz matriz por capacidade. Chrome
bloqueado termina o controle de UI e encaminha roteiro manual; não se tenta outro
canal para contornar a política. Corrigir somente defeito material reproduzido.

P02 preserva a raiz canônica R4 com alterações preexistentes e reutiliza checkout
existente limpo, em branch independente derivada da main revalidada. Separa o
produtor científico do renderer com a menor extração compatível, mantém aliases,
atualiza launcher/CLI/migração/documentação e testa exportação para Atlas sem
executar a UI histórica. Não instala responsabilidades R4 no viewer.

P03 revisa matrizes, testes negativos, contratos, completude, rollback e invariantes
científicos. Nenhum arquivo tem dois writers. P00 confere integração com fixtures,
publica somente código/documentação liberados em PR Draft e acompanha CI/review
dos novos SHAs. Evidências científicas e caminhos privados ficam fora do Git.
Aceite humano, execução científica real e retirada conservam gates separados.

## Reteste: densidade, resumo e agrupamento

P01 reutiliza componentes do catálogo e cards de visão geral, corrigindo a
densidade da identificação com alinhamento que permita quebra controlada.
As métricas declaradas são recuperadas da apresentação autenticada; métricas de
consulta/sessão ficam nomeadas em contexto próprio, com denominadores explícitos.
Nenhuma contagem, título ou conteúdo das capturas privadas entra nas fixtures.

O agrupamento por núcleo é estado de apresentação: não altera a sequência raw
das linhas usada em exportações, nem cria identidade ou relação científica.
Acesso centralizado a campos declarados evita heurísticas por nome de projeto.
P03 revisa semântica dos contadores, ausência/zero, completos campos e população
agrupada. P00 mantém manifesto sucessor, instalação isolada e CI/review por novo
SHA; a sessão de reteste manual permanece separada da automação bloqueada.
