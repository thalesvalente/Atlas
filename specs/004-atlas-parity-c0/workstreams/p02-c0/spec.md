# P02 — Explorador C0 endereçável

Missão: ATLAS-PARITY-02-P02. Tag: `seai.pipeline@llm-sec,agentic-pac/seai.qa:`.
Base: `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, árvore
`5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`. Feature 004 não existe na base.
Somente este workstream é escrito; seleção de feature e agregadores são da P06.

## Constitution e entradas

ARC-01–09, ADR-0001 e bytes de `packages/protocol/**` vinculantes e preservados.
ADR-0002 v1.0 aceita como direção pela PR #5 e seu merge; não significa release,
aprovação científica ou promoção. Preservar textos históricos anteriores.
Estudos A/B/C/D integrais ausentes: `INPUT_MISSING`. Hashes C fornecidos não foram
verificados sem bytes. Requisitos abaixo vêm do prompt P02 e das features 001–003.

## Jornadas e critérios de aceite

- P02-R01: explorar todos os registros carregados com ordenação determinística,
  busca título/ID/fonte e filtros por projeto, experimento, estado, fonte, revisão,
  presença de métricas e menções. Seleção de até quatro permanece ao filtrar.
- P02-R02: hash contém view, filtros, detalhe e seleção; recarregar e histórico
  restauram contexto. Rejeitar entradas inválidas, IDs inexistentes e scope expirado.
  Um `source-1` jamais muda de entidade silenciosamente após reinício/reordenação.
- P02-R03: mostrar fonte/pacote, snapshot, carregados/filtrados. Totais de origem,
  elegíveis, selecionados pelo produtor e convertidos são não informados sem
  evidência contratual; não confundir recorte da tela com cobertura da origem.
- P02-R04: detalhe/comparação preservam estado, revisão, valor textual exato, tipo,
  unidade, precisão, parâmetros, disponibilidade, entradas/saídas e derivação.
  Menções são neutras; incompatibilidade não recebe conversão/ranking.
- P02-R05: ausência de datas/relações não exclui execuções; origem temporal e direção
  declaradas aparecem, sem promover observação a evento ou vínculo a causalidade.
- P02-R06: layout legível em desktop, 390 e 320 CSS px, teclado/foco e text spacing.
  Tabelas bidimensionais têm regiões próprias; CSS zoom não prova zoom nativo/WCAG.
- P02-R07: dados entram como texto; CSP/origem/allowlist fixos, sem resolução externa.
- P02-R08: wheels instalados fora do checkout, sem R4; asset novo deve ser servido
  por allowlist explícita e empacotado. Fixtures >=24 execuções em duas fontes.

## Clarificações decididas dentro do escopo

Scope de navegação vale pela sessão de servidor + snapshot indexado. Reiniciar o
servidor expira links explicitamente; reload do navegador na sessão os preserva.
Um token aleatório de sessão evita publicar caminhos em identificadores derivados.
Filtros são aplicados à exploração/timeline; comparação usa seleção explícita,
inclusive itens ocultos pelos filtros. Relações mantêm endpoints declarados.
Números de cobertura não existentes no contrato não são inferidos de `datePublished`,
nome da fonte ou cardinalidade local. P03 não é dependência desta implementação.

## Gates

Implementação autorizada, branch/commit/PR Draft sanitizados autorizados. Sem merge,
release, host, acervo privado, provider ou alteração de protocolo. Navegador e CI
pendentes não são PASS. Qualquer ajuste fora ownership recebe handoff para P06.
