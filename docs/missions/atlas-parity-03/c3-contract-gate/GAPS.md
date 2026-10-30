# ATLAS-PARITY-03-C3 — gate de contratos P01

## Lacunas verificáveis e próximo owner

- **CI final (C3):** verificar no run terminal os dois jobs Windows/Ubuntu e as duas execuções normal/`-O` em cada job. Os artefatos JUnit/JSON pertencem ao SHA efetivo, não ao head P01 histórico. Owner: C3.
- **Revisão independente (revisor nativo externo à autoria):** não disponível nesta sessão. A revisão local do autor não a substitui. Owner: revisor independente autorizado por sessão com delegação nativa ou revisão externa posterior.
- **P02/C1:** implementação P02 congelada no SHA `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`, mas ausente da árvore C3. Validar integração e fluxos endereçáveis no SHA composto. Owner: C1/P06.
- **P03/C2:** módulos P03 isolados no SHA `6c412c36e1dbe11711daa15c6d8727fbe94fa0ad`; componentes não ativados no aplicativo principal. Testar composição real separadamente. Owner: C2/P06.
- **P04/legado:** estudos completos A/B/C/D, upstream, perdas por camada e denominador de paridade não foram comprovados. O `UNKNOWN_UPSTREAM` de P01-J21 não é zero nem número de itens carregados. Owner: P04/detentor das entradas legítimas.
- **Evolução persistida:** P01-J18 (grade tabular), J19 (marco documental) e J28 (identidade persistente) precisam de decisão própria; exemplos sintéticos não alteram Caderno nem protocolo. Owner: P01 + decisão humana competente.
- **Semântica de cobertura:** sidecar opcional e derivado; nenhum percentual para denominador não estabelecido nem `0/0`. Owner: P06 na composição e responsável por evidência upstream.
- **Governança:** validade, integridade, autenticidade, proveniência e aprovação científica permanecem gates distintos; direção da ADR-0002 aceita previamente não implica release. Owner: mantenedor competente.

Não se inferem as doze jornadas do estudo C a partir das 28 jornadas P01. Menções não geram relações causais; `source-N` não é identidade durável.
