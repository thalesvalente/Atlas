# Revisão de arquitetura e segurança — A4

Data: 24/10/2026. Estado: `DESIGN_REVIEWED_IMPLEMENTATION_PENDING`. Revisor independente dos autores da UI e SDK. Constituição ARC-01–09 lida e preservada no desenho. Esta lista documenta provas necessárias, não uma declaração de cumprimento ainda não executado.

| ID | Requisito para implementação/aceite | Teste/revisão |
|---|---|---|
| QA-ARC-01 | SDK instala sem UI e produtor; viewer sem imports R4/execução de experimentos | Guard AST, metadata wheels, venv limpo, revisão de imports dinâmicos |
| QA-ARC-02 | Versão/contexto/forma JSON-LD restritos; relações e IDs validados | Negativas diretas validate_document e SDK CLI sem rede |
| QA-ARC-03 | Leitura só em fonte declarada; ZIP, se aceito, sem extração | Traversal, symlink, path absoluto, URLs, duplicação de nomes e limites |
| QA-ARC-04 | Orçamento total de payload além do limite por arquivo | Conjunto expandido que ultrapassa limite agregado |
| QA-ARC-05 | Nenhum input inválido aborta silenciosamente ou retorna sucesso | URI malformada, JSON duplicado/NaN, tipos, status, versões |
| QA-ARC-06 | Fonte imutável e índice reconstruível; detecção de alteração | Digests de teste antes/depois, rebuild, reabertura e troca deliberada de bytes |
| QA-ARC-07 | Ausência de autoridade científica implícita | UNKNOWN/HOLD preservados; sintético não promovido; relatório expõe NOT_VERIFIED/NOT_EVALUATED |
| QA-ARC-08 | HTTP serve somente loopback e fontes fixas | Host/Origin inválidos, path injection, métodos/rotas ausentes, sem CORS |
| QA-ARC-09 | Texto não confiável não executa; referências externas não baixam | XSS como texto, tráfego externo zero, CSP, ausência de HTML de anexos |
| QA-ARC-10 | Comparação preserva identidade/tipo/unidade e ausentes | Incompatibilidade com mensagem; nenhuma conversão/zero inventado |
| QA-ARC-11 | Teclado, labels, foco e mobile/desktop funcionam no instalado | Chromium real nos fluxos principais, 390/1440px |
| QA-ARC-12 | Nenhuma fonte privada/copied derivation no público | Inventário e provenance de arquivos, adaptador no privado; sem licença inventada |
| QA-ARC-13 | CI e Codex aplicáveis ao SHA publicado | Links/jobs reais; pendência continua PENDING |

Riscos conhecidos do desenho: leitura de arquivos não certifica host adversarial nem elimina todas as corridas entre checagem e abertura; referência HTTP(S) é registro não resolvido, não download autorizado; integridade por bytes não autentica origem/data; testes Linux locais não substituem Windows na CI. Nenhuma dessas limitações é ocultada por um PASS de sintaxe.
