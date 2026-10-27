# Plano P01 — documentação e prova de contrato

**Branch:** `work/atlas-parity02-p01-contracts-20261027`. **Data:** 2026-10-27.
**Spec:** [spec.md](spec.md). **Estado:** candidata do workstream P01.

## Resumo

Fixar evidências públicas, classificar perdas, documentar apresentação/cobertura e
ensaiar exemplos sintéticos. Usar a API pública existente para verificar o que já é
representável. A implementação desta missão é a documentação e sua validação; não
inclui alterações de produto, protocolo, shell, workflows ou ADRs.

## Contexto técnico

Python 3 e biblioteca padrão; SDK público carregado dos bytes da baseline, sem
instalação no host nem import de produtor. Markdown, CSV UTF-8 e JSON são os artefatos.
Execução no sandbox Linux de engenharia do CHAT; não se atribui prova a Windows,
produtor operacional ou navegador. Fixtures próprias não contêm dados do acervo.
Sem dependência de rede para validar o pacote; repositório remoto usado para fontes e PR.

A validação documental usa códigos de erro determinísticos e um corpus explícito.
A prova do SDK usa os validadores públicos reais, não um parser substituto. Provas
históricas só podem ser reaproveitadas no SHA/árvore indicado, com sua atribuição.

## Constitution Check antes e depois do desenho

| Princípio | Aplicação nesta frente | Resultado do desenho |
|---|---|---|
| ARC-01 | documentação para interface; não execução experimental | compatível |
| ARC-02 | nenhum byte de protocolo alterado; worksheets fora do intercâmbio | compatível |
| ARC-03 | modelos derivados e cobertura opcionais/reconstruíveis | compatível |
| ARC-04 | fontes explícitas; nenhum parser de carrier privado | compatível |
| ARC-05 | prova usa SDK/viewer públicos sem produtor | compatível |
| ARC-06 | UNKNOWN, digest, autenticidade e ciência separados | compatível |
| ARC-07 | nenhuma operação no host/migração/retirada | compatível |
| ARC-08 | paridade documental não promove produto | compatível |
| ARC-09 | propostas futuras classificadas; direção ADR-0002 já aceita por recibo | compatível |

## Estrutura e ownership

- `docs/missions/atlas-parity-02/p01-contracts/`: evidência, matriz, decisões, resultados, handoff e manifesto.
- `docs/contracts/atlas-parity-02/p01/`: contratos candidatos, exemplos e validador documental.
- `specs/004-atlas-parity-c0/workstreams/p01-contracts/`: este ciclo Spec Kit.

Nenhum agregador da raiz 004 é escrito. P06 mantém ownership do ponteiro global.
No preflight a feature 004 não existia na baseline pública; P01 não aloca outro número.

## Execução e responsabilidades

1. Root fixa preflight e baseline. A inventaria anexos e fontes, sem copiar conteúdo privado.
2. Root especifica/clarifica e usa `setup_plan.py` no diretório próprio com
   `SPECIFY_FEATURE_DIRECTORY` e `SPECIFY_FEATURE_NO_PERSIST=1` oficiais.
3. A redige evidências/matriz; B redige apresentação/cobertura. Arquivos exclusivos.
4. Root prepara casos esperados antes do validador; valida semântica e consumo SDK.
5. Root confere rastreabilidade, ownership, hashes e regressões focais dos mesmos bytes.
6. C, sem autoria do delta, revisa os arquivos e executa verificações independentes.
7. Root resolve findings, registra convergência, cria commit e PR Draft no Atlas.

Agentes reais retornados pela ferramenta: `/root/archaeology`, `/root/semantics`,
`/root/independent_qa`. Identificadores são task IDs nativos, não nomes de agentes simulados.

## Gates de conclusão

`P01_CONTRACT_PACKET_READY` significa contratos suficientes para iniciar os itens
compatíveis. `P01_PARTIAL_INPUTS_EXPLICIT` registra a ausência dos estudos integrais,
sem bloquear o restante. Não há gate de promoção/ciência/merge habilitado pelo pacote.

Não executar helpers que inicializem outra feature ou alterem estado global. A CLI
`specify` não foi encontrada no PATH; helpers já versionados são usados diretamente.
Dispatch nativo de skills: NOT_RUN. Aplicação das instruções Spec Kit: manual com
execução real de helpers. Não reinstalar apenas para cumprir formalidade.
