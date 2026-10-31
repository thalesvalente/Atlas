# Componente F3A — contrato de consumo isolado

AP04-F3A-CHAT-GRAPH-01, AP04-POR-v1.0-draft. Entrada única: descriptor atlas-legacy-presentation 0.2.0 já materializado em memória. Não é Caderno/RO-Crate/Process Run conforme. Autoridade LEGACY_DERIVED, autenticidade NOT_VERIFIED, ciência NOT_EVALUATED, freshness OBSERVED_SNAPSHOT_ONLY.

A API é um ES module independente em parity04_f3a_graph.js; CSS exclusivamente namespaced em parity04_f3a_graph.css. Nenhum import para runtime principal, F3B, Catalog, SDK, protocolo ou R4. Integração de assets, seleção File API, abertura/parse externo e roteamento são ownership F4.

## API

```js
import {mount} from "./parity04_f3a_graph.js";
const graph = mount(container, descriptor); // elemento DOM dedicado
container.addEventListener("graph-selection", event => {
  // detalhe neutro; o consumidor não ganha resolução de entidade privada
  const context = event.detail;
});
graph.getState();          // estado descartável de inspeção
graph.select(context);     // seleção exige contexto completo e sessão vigente
graph.select(null);        // limpar seleção
graph.setData(descriptor); // nova importação: invalida seleção e links anteriores
graph.dispose();           // remove listeners/temporizadores/DOM/estado
```

Contexto usa source_id, snapshot_id, occurrence, nav_id e session_id. nav_id é DERIVED_FOR_PRESENTATION, nunca native_id. A chave operacional inclui a sessão do componente; ID textual igual em outro snapshot/fonte não é destino alternativo. Seleção não resolve native_id colidente. Atualização e expiração invalidam contexto; não há remapeamento por título/ordinal. A opção now injeta relógio nos testes, sem persistência.

## Modelo e semântica

Cada descriptor tem uma fonte/snapshot, sem soma global. Hierarquia segue somente parent_key_literal e parent RESOLVED contextual com alvo original único. Kind enum preservado: Project, Family, Experiment, Run, Other, Unknown; Stage declarado é Other com original_type Stage, nunca nível inferido. Órfãos, ciclos e Run externo isolado permanecem distinguíveis; grupo visual não é entidade científica. Stub DECLARED_EXTERNAL_REFERENCE não satisfaz RESOLVED da entidade fonte.

Pertencimento hierárquico e ORGANIZATIONAL_MEMBERSHIP, DECLARED_LINEAGE, DECLARED_BINDING e NEUTRAL_MENTION têm estilos/legendas distintos. Direção FROM_TO é declarada; UNDIRECTED/UNKNOWN não recebem causalidade. Null/unresolved/collision/repeat_group/repeat_occurrence/binding_gap são preservados por ocorrência. Contagens podem se sobrepor, não são uma partição aditiva.

Todos labels/IDs/locators/URIs são texto inerte, construído via APIs DOM/textContent. Não existe avaliação de JS/HTML, abertura de URI, fetch/telemetria, leitura de pasta ou storage no componente. Quotas invalidam entrada inteira; não há subconjunto silenciosamente qualificado. Dados de tabela/asset fora da visualização não recebem renderer nem resolução inventada.

## Interação e acessibilidade

SVG real com expansão/recolhimento, seleção, controles/gestos pan/zoom, ajustar/reset e minimapa navegável. Tab entra nos controles e árvore; setas/Home/End percorrem nós, Enter seleciona e Escape limpa. Foco visível e nomes acessíveis; seleção/zoom/foco sobrevivem a mudanças de layout quando possível, com retorno ao ancestral quando filho fica oculto. Estado é temporário e segregado por mount/sessão.

Alvos de QA: 1440, 390 e 320 CSS px; labels extensos e hostis, foco após colapso, zoom por controles/roda/gestos e pan/minimapa. Não se afirma zoom nativo 200%, leitor de tela completo ou certificação WCAG. Contraste e inspeções geométricas focais não substituem auditoria integral.

## Orçamento e responsabilidades de abertura

O componente recebe objeto já alocado pelo chamador. Não lê nem parseia arquivo. Limites documentais de envelope: 32MiB de representação JSON, profundidade20, 10.000 nós e 100.000 relações. O orçamento próprio de render é 1.000 nós / 4.000 relações, com recusa atômica visível e prazo de 30s por operação. Não há truncamento. O payload real F1 sanitizado informa 2.911 nós; ele excederia esta capacidade e não foi executado. F4 deverá resolver o orçamento de visualização antes de qualquer demonstração com esse payload; F3A não afirma prontidão desse acervo. As medições sintéticas ficam nos recibos do SHA testado.

F2 exige orçamento de 256MiB/30s por abertura externa. F3A não certifica heap total do browser nem fluxo de importação. F4 deverá impor os limites de aquisição/parse/heap antes de entregar dados ao componente; essa obrigação permanece aberta. F3A limita trabalho próprio de modelo/DOM e mede execuções sintéticas, sem reivindicar G4. A interpretação foi revisada por C como compatível com o escopo in-memory, sem alteração contratual.

## Fronteira de qualificação

Gate focal executa componente isolado com fixture original sintética, Chromium real Windows/Ubuntu e Python normal/-O. Capturas/JSON/JUnit são atribuídos a SHA/tree. A revisão usa execução e oráculos explícitos, não snapshots cegos. Testes F4 relativos a host paths/TOCTOU, tabelas/exportação, SDK instalado e acervo privado são fora do escopo desta prova; N01–N24 são confrontados no RESULT sem inventar execução.

O gate histórico pode recusar paths novos por autoria congelada. Essa recusa não é removida nem convertida em G5 PASS. Prontidão F3A permite handoff futuro F4, sem iniciar integração, sem recuperar árvore legada real e sem aceitar ciência.
