# Revisão independente de qualidade dos requisitos — A4

Data: 24/10/2026. Revisor: agente nativo A4, distinto do autor ORQ/A2 e do autor do SDK A1. Escopo: constituição, spec, plan, contrato interno, modelo e clarify da candidata ATLAS021. Nenhuma aprovação humana é conferida por este registro.

## Resultado pré-implementação UI

`PASS_SCOPED` para a qualidade dos requisitos da candidata. Q-REQ-01 foi conciliado antes da implementação UI; os limites de Q-REQ-02 foram fixados no contrato desta revisão. A direção ARC-01–09 está preservada. A1 (aceite de protocolo) e A7 (promoção) permanecem gates humanos próprios; não foram avaliados como PASS.

- [x] Histórias representam fluxos úteis e testáveis de consulta, comparação e interoperabilidade.
- [x] FR-001–FR-020 e SC-001–SC-006 têm comportamento e evidência verificáveis.
- [x] Fontes, dados sintéticos, desconhecimento, integridade e aceite científico são separados.
- [x] UI, SDK, produtores e armazenamento têm fronteiras e ownership claros.
- [x] Instalação isolada, fontes imutáveis, rebuild, colisões, negativas e UI desktop/mobile estão previstos.
- [x] Clareza suficiente para implementar candidata sem novas perguntas de detalhes reversíveis.
- [x] Gates privados/públicos, ADR-0002, release, promoção e retirada preservados.
- [x] Q-REQ-01 resolvido: spec/plan/research agora permitem leitura ZIP limitada em memória, sem extração. A spec explicita que a extensão `.eln` não prova conformidade ELN. A implementação deve ser testada contra esse comportamento.
- [x] Q-REQ-02 resolvido como contrato de desenho: metadados 2 MiB; payload individual 8 MiB; payload agregado 32 MiB; ZIP comprimido 64 MiB; 4096 membros de arquivo; 10000 entidades; profundidade 20; razão de compressão 200. SDK/perfil e testes devem usar esses mesmos limites ou registrar mudança explícita antes do aceite. Fixar o requisito não prova sua implementação.

## Evidência do snapshot revisado

Os digests abaixo se referem somente a documentos novos publicáveis desta missão, sem payloads privados.

| Documento | SHA-256 |
|---|---|
| `spec.md` | `6c02a86fdae96205e9005f5f55a2decd0e389bfbf4979609b97d4cbd58b9a049` |
| `plan.md` | `3a40e9976ee38dc301cd2e5ef6d032d64969a0740c9d0f646e9654dce69aa229` |
| `contracts/interface.md` | `21e21e9f092ad0ae996b3911714deb652695a2a6c0617a23aba558c860aedb0f` |
| `data-model.md` | `e53b403b6739e61670ba89d6811f1e36023679b4cc201f72704a4b8a85d4190f` |
| `clarifications.md` | `b4b2742a58fe20fa0c772fe21170601349c2177f77943413be03f7aea319106f` |

Mudanças posteriores devem atualizar a resolução dos itens afetados. Esta revisão antecede o código de UI; não é revisão da implementação nem substitui CI/revisão do SHA final.

A lista tasks.md foi revisada: owners, paths, dependências, paralelismo exclusivo e gates T024/T025 estão explícitos. Requisitos não foram removidos para obter o parecer.

## Addendum de precisão — revisão proporcional

O contrato interno acrescentou `display_value` derivado e transporte do dossiê como bytes, preservando o valor tipado original. A4 revisou esse delta e verificou no wheel final o inteiro9007199254740993 em detalhe/comparação/JSON bruto. O SDK recusa literal decimal não representável sem perda. Esta correção reforça FR-003/004/012 e não muda ARC nem autorização. Novo SHA-256 de `contracts/interface.md`: `9048be669ccb08af12a922d3bf8712c72e53ae1b825a908f75c7aab026027633`. Não foi necessário reabrir a checklist inteira.
