# Contrato de consumo público
Entrada: snapshot Caderno 0.1.0a1 com `ro-crate-metadata.json`, contexto fixado, grafo e referência explícita.

Saída: modelos derivados de projetos, experimentos, runs, artefatos, métricas e relações para apresentação.

Falhas: fonte inacessível/inválida, versão desconhecida, inconsistência do grafo, conflito de IDs ou drift de conteúdo verificável não são convertidos automaticamente para `PASS`.

Fonte não confiável nunca é executada pelo Atlas; referências externas nunca são baixadas implicitamente. O produtor privado mantém seleção, proveniência de transformação e restrições do formato de origem.

**Não existe contrato público para ler diretamente a árvore ou os arquivos particulares de um produtor.**
