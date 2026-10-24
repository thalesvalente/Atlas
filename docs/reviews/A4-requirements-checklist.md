# ATLAS021 — revisão independente de requisitos (A4)

Data: 24/10/2026. Escopo: missão ATLAS021 v1.0 e AB-CONTRACT-1.0; sem leitura de fontes privadas nesta fase. Autor da revisão: A4, distinto dos autores da UI e do SDK. Esta checklist avalia especificação e requisitos; não constitui aprovação humana, certificação científica nem autorização de publicação, migração ou retirada.

## Critérios de revisão antes da implementação

| ID | Critério observável | Evidência esperada | Estado inicial |
|---|---|---|---|
| Q01 | ARC-01–09 aparecem sem enfraquecimento na constituição, ADR-0001 e rastreabilidade | Referência de cada ARC a requisito mensurável e teste/revisão | PENDING_ARTIFACT |
| Q02 | ADR-0001 distingue direção humana já determinada de detalhes e implementação não verificados | Texto explícito, sem assinatura/aceite inventado | PENDING_ARTIFACT |
| Q03 | ADR-0002 escolhe uma proposta única com versões exatas compatíveis; marco A1 depende de aceite humano | Fontes primárias, prova comparativa executada, proposta versionada | PENDING_ARTIFACT |
| Q04 | Protocolo público, SDK, storage e UI têm dependências direcionais e instalações separadas | Grafo de módulos/dependências; instalação SDK sem viewer/R4 | PENDING_ARTIFACT |
| Q05 | Serialização JSON-LD suportada e limites semânticos são explicitados | Rejeição de contexto remoto/forma não suportada; índices e vínculos verificados | PENDING_ARTIFACT |
| Q06 | IDs, versões, namespaces, colisões, timestamps, valores ausentes, unidades e estados têm regras testáveis | Casos positivos e negativos e mensagens de erro acionáveis | PENDING_ARTIFACT |
| Q07 | Digest, sintaxe, semântica, origem declarada, autenticação e revisão científica são dimensões distintas | Modelo e UI não inferem autoria/aceite pelo hash ou status de execução | PENDING_ARTIFACT |
| Q08 | Fontes são somente leitura; índices e preferências ficam fora da base autorizada e são reconstruíveis | Snapshot de bytes antes/depois, rebuild e retomada | PENDING_ARTIFACT |
| Q09 | Leitura de referências e anexos tem política restritiva e limites definidos | Negativas traversal, symlink, URI externa, arquivo ausente, tamanho/quantidade | PENDING_ARTIFACT |
| Q10 | Texto/anexos não confiáveis não podem executar scripts nem gerar navegação/download implícitos | Payload XSS como texto; CSP; acesso externo observado zero | PENDING_ARTIFACT |
| Q11 | UI cobre lista, filtros, detalhe, comparação compatível, timeline, linhagem e dossiê | Teste navegador real de pacote instalado em desktop e mobile | PENDING_ARTIFACT |
| Q12 | UI cobre vazio, parcial, falha, fonte inacessível, referência ausente, digest alterado e versão incompatível | Cenários e mensagens, sem substituir falta por valor inventado | PENDING_ARTIFACT |
| Q13 | Dois produtores independentes exportam entradas pelo próprio código para o mesmo contrato | Comandos reais, mesmo SDK/viewer; fixture sintética explicitada | PENDING_ARTIFACT |
| Q14 | Mapping legado preserva estado, ID, data, digest e origem e relata perdas | Recibo privado de transformação e testes; sem promoção científica | PENDING_ARTIFACT |
| Q15 | Publicação contém somente material próprio/público licenciado/liberado | Inventário de arquivos, licenças, gate de transferência privada separado | PENDING_ARTIFACT |
| Q16 | Spec Kit instalado/pinado ou etapas manuais identificadas honestamente | Versão/ref, comandos e saídas, feature isolada, autoria da revisão | PENDING_ARTIFACT |
| Q17 | CI prova instalação limpa, normal/otimizado, Windows/Ubuntu, UI e negativa, no SHA exato | Jobs reais, status efetivo, sem reutilizar CI histórica como prova | PENDING_ARTIFACT |
| Q18 | Review independente e Codex são reais; ausência permanece pendente | SHA, autor, findings/resolução e link de revisão | PENDING_ARTIFACT |
| Q19 | A6 declara necessidades e disposição por ID lógico conhecido; não inventa inventário B | Handoff versionado/digest do perfil, escopo A e ressalva de drift | PENDING_ARTIFACT |
| Q20 | A7 e operações protegidas ficam explicitamente não autorizadas | Nenhum merge/release/deploy/migração/remoção; proposta exata futura | PENDING_ARTIFACT |

## Matriz de arquitetura e execução planejada

| ARC | Fronteira testada | Teste independente proposto | Limite da prova |
|---|---|---|---|
| ARC-01 | Viewer não executa experimentos nem aprova ciência | Inspeção CLI/rotas/API + teste negativas de métodos mutantes | Teste de ausência não é prova completa de segurança |
| ARC-02 | SDK/protocolo não importa UI/R4 | AST imports diretos/transitivos; metadata wheels; import em venv SDK-only | Imports dinâmicos exigem revisão complementar |
| ARC-03 | Índice descartável, fonte recuperável sem UI | Carregar com SDK; rebuild e remoção apenas do cache de teste; igualdade de read-model | Não certifica preservação de acervo histórico |
| ARC-04 | Core desconhece domínios específicos | AST e busca de condicionais/tipos RF/RNF/RES; dois produtores reais | Nomes podem aparecer só em docs/evidência sintética, não em despacho do core |
| ARC-05 | Instalação independente funcional | Build wheels; instalar em venv novo; executar fora da árvore e limpar PYTHONPATH | CI Windows permanece necessária se local Linux |
| ARC-06 | Ciência não promovida por integridade | Round-trip UNKNOWN/HOLD/PARTIAL/FAILED, datas declaradas, digest mismatch | Origem declarada não autentica produtor |
| ARC-07 | Runtime não contém manutenção/retirada | Revisão wheel e comandos; fonte imutável; API restrita | Não introduzir leitor suspenso como solução de host |
| ARC-08 | Nova candidata não é promoção | Revisão README/ADRs/marcos; gate A7 ausente conserva baseline provisória | Passar testes não aprova mudança canônica |
| ARC-09 | Desvio abre HOLD | Fixtures de arquitetura adulteradas devem falhar nos detectores; relatório de desvios | Detectores cobrem riscos concretos, não aprovação humana |

## Conjunto adversarial mínimo

1. Metadados truncados, JSON duplicado/ambíguo, top-level incorreto, nós repetidos e IDs colidentes.
2. Versão do perfil ausente/desconhecida; contexto remoto ou contexto redefinindo termos; campos obrigatórios e relações ausentes.
3. Evidência local ausente, hash divergente, extensão desconhecida, payload HTML/JS e nome com script.
4. Referências `../`, absolutas, URI `file:`, URL externa, caminhos percent-encoded, barras invertidas, symlink saindo da base, pacote acima dos limites e quantidade excessiva.
5. Estado de execução parcial/falho com revisão desconhecida ou HOLD; dados sintéticos nunca apresentados como observações reais.
6. Valores nulos, boolean como número, NaN/Infinity, unidade faltante/incompatível; comparação só entre definições e unidades compatíveis.
7. Duas fontes com mesmo ID e bytes distintos; mesma fonte reaberta; fonte alterada depois de indexada; reconstrução sem escrita no original.
8. Navegação por teclado, foco visível, labels e contraste básico, viewport mobile sem conteúdo/ação essencial inacessível.

## Estados dos marcos na revisão inicial

A0–A6: NOT_EVALUATED (artefatos e execução ainda não examinados). A1 exige, adicionalmente, aceitação humana da proposta exata. A7: NOT_AUTHORIZED nesta missão. Nenhuma marcação desta checklist altera esses gates.
