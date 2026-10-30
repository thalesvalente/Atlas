# Plano técnico P02

## Contexto

Python >=3.11, SDK Caderno existente sem dependências de runtime; servidor loopback
da biblioteca padrão; JavaScript e CSS locais sem framework ou chamadas externas.
Reutilizar catálogo, projeção, filtros, comparação, timeline, linhagem e menções.
Nenhuma mudança persistida de schema/contexto/versão.

## Design

1. Catálogo acrescenta token de sessão/snapshot e cobertura derivada conservadora.
   `display_precision` conserva inteiros que JSON.parse não representa exatamente.
2. `parity02_p02_state.js` é módulo puro de filtros, ordenação e hash validado.
   Shell `app.js` renderiza o estado e sincroniza History API.
3. Preservar seletores de regressão atuais; adicionar controles acessíveis. Detalhe
   fecha sem perder filtros/view e restaura foco ao acionador quando disponível.
4. Fontes e escopo mostram limites/recortes; timeline mantém origens e sem data;
   linhagem lista também execuções isoladas. Comparação conserva seleção e metadados.
5. QA: 28 execuções sintéticas, negativas HTTP/URL/snapshot, testes de pure state,
   instalação wheel e harness browser explícito. Sem executar testes do host.

## Ownership entre agentes

- `/root/navigation_state`: catalog.py, server.py, novos módulos P02 backend e state.js.
- `/root/fixtures_browser`: novos testes, scripts QA e fixtures P02.
- `/root/independent_review`: revisão somente leitura, sem autoria do delta.
- `/root`: app.js/index.html/style.css, documentação, integração e publicação.

## Constitution check

ARC-01/03: índice/estado descartáveis e consulta. ARC-02/04/05: protocolo intacto,
sem imports privados, wheel isolado. ARC-06: desconhecido permanece desconhecido,
digest não autentica. ARC-07/08/09: sem operação do host, retirada ou novo desvio.
Não há alteração de feature registry nem extensão de autoridade.

## Convergência P06

Novo asset precisa permanecer em ASSETS e package-data. Glob atual `static/*.js`
já cobre. Auditoria global protege catalog/server/index.html, fora ownership P02:
P06 deverá revisar exceção estrita para esses paths. CI browser atual não chama
harness P02; não alegar que criação do arquivo o conecta automaticamente.
