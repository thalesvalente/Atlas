# Revisão de publicação — ATLAS021

O commit-semente permitido inicializou apenas README. Trabalho posterior ocorre em
branch própria. O produto é implementação nova a partir de requisitos e padrões
públicos. Houve inspeção separada de fontes privadas para o adaptador: não se alega
processo clean-room. Nenhum arquivo ou trecho derivado dessas fontes será publicado
no Atlas sem gate PUBLIC-SOURCE-TRANSFER. O adaptador, seus mapas, fixtures derivadas
 e testes ficam no repositório privado.

Nenhuma licença do produto foi escolhida. A ausência de licença não concede licença
open source aos consumidores. Dependências de teste e referências públicas mantêm
suas licenças; material redistribuído deve ter origem/pin/licença em THIRD_PARTY_NOTICES.
A entrega é uma PR Draft pré-release, sem publicação de pacote, release ou deploy.

Manifesto de transferência privada→pública na candidata inicial ATLAS021: conjunto
vazio. Esse registro histórico não descreve as sucessões explicitamente autorizadas.
Não há liberação implícita de transferência futura. Revisão independente deve
confirmar paths e conteúdo antes da publicação.

## Sucessão A01 — apresentação v6.1 autorizada

A autorização do proprietário registrada em
https://github.com/thalesvalente/Atlas/pull/18#issuecomment-6552216866 permite
reutilizar/adaptar e transferir os trechos necessários da apresentação antiga para
recuperar funcionalidades no Atlas independente. A continuação A01 solicita
explicitamente esse porte. O escopo e os blobs exatos estão em
`docs/missions/atlas-a01/REUSE-MANIFEST.json` e a reconciliação em
`docs/missions/atlas-a01/REUSE-AND-PARITY.md`.

Somente funções e estilos de apresentação revisados são incorporados. Não são
transferidos corpus, payloads embutidos, screenshots reais, fontes de experimentos,
credenciais, caminhos de host, executores ou leitores de arquivos do produtor.
O viewer continua sem dependência do runtime R4 e não executa scripts/HTML dos dados.
O manifesto histórico C2/v5 e os blobs P03 permanecem congelados; A01 é sucessor
delimitado, não autorização geral. Nenhuma licença de software foi escolhida ou
inventada por este porte. A autorização de transferência não concede direitos
sobre dependências de terceiros ou fontes não relacionadas no manifesto.

## Sucessão da evidência de bytes A01 na integração à main (2026-11-07)

O `docs/missions/atlas-a01/REUSE-MANIFEST.json` é o **testemunho histórico
congelado** da transferência autorizada. Suas posições e SHA-256 de destinos
representam o instante do porte; **não** são os hashes dos arquivos modificados
pelas melhorias posteriores da árvore, triagem e acessibilidade.

Para a candidata atual, o mapa de **oito destinos** com hashes de bytes Git,
identificações dos símbolos e posições de declarações atualizadas está em
`docs/missions/atlas-a01/REUSE-SUCCESSOR-20261107.json`. Os intervalos
completos de `drawNode` e `focusNode` são qualificados separadamente.
`scripts/qa/verify_a01_reuse_successor.py` verifica ambos os manifestos
contra a árvore atual no CI Windows/Ubuntu, recusando deriva de qualquer blob.

O sucessor **não** autoriza transferência nova de código privado, não muda
licença, não contém dados científicos e não revoga a proveniência original.
Sua validade é vinculada aos bytes atestados, não a commits futuros que os alterem.
Integrar o produto independente à `main` não demonstra paridade integral com
CA-01 nem permite retirar a interface antiga do R4 sem gate específico.
