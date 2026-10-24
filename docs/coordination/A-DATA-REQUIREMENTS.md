# A-DATA-REQUIREMENTS — candidata 0.1.0a1

Contrato: **AB-CONTRACT-1.0**. Emissor: **Frente A / ORQ-A**. Data: **2026-10-24**.
Escopo: interface e protocolo candidatos; requisitos de consumidores externos
permanecem fora desta declaração. A versão concreta do protocolo é identificada por
[manifesto e digests](../protocol/profile-manifest.json).

## Entradas necessárias à interface

O produto requer uma fonte explicitamente declarada que satisfaça o perfil:
metadados, identificadores e relações; estados de execução/revisão; tipos e unidades;
origem declarada dos timestamps; disponibilidade de payloads; referências e digests
quando declarados. Não requer caminhos históricos, worktrees, banco de dados ou
instalação de qualquer produtor. Payload ausente permanece observável como ausente;
o registro não é transformado em evidência autenticada.

O índice em memória é reconstruível e descartável. A preferência do navegador e o
dossiê derivado não substituem a fonte. O produtor deve preservar o original e emitir
um novo snapshot em destino explicitamente selecionado; a interface não realiza
essa transformação. Mudanças de fonte são sinalizadas e exigem reconstrução explícita.

## Requisitos de compatibilidade e preservação

| Classe lógica | Disposição da Frente A | Justificativa e limite |
|---|---|---|
| Contrato/API de leitura usado pelo adaptador | NEEDED | Reproduzir o ensaio privado e identificar perdas; fixado na branch privada |
| Fixture sintética do produtor independente | NEEDED | Prova pública reproduzível de conformidade e interface |
| Fixture sintética do adaptador | NEEDED | Prova privada de compatibilidade, sem publicação do corpus |
| Fonte original de qualquer transformação futura | UNKNOWN | Nenhuma transformação de acervo real foi aprovada ou executada |
| Diretórios históricos para o runtime novo | NOT_REQUIRED_BY_A | Apenas o runtime sintético ensaiado; não encerra outros consumidores |
| Ferramenta operacional anterior | NEEDED | Mantém a referência provisória até paridade e promoção humana |
| Oito fontes históricas individuais mencionadas na missão | UNKNOWN | B-INVENTORY não recebido; não se inventam IDs, paths ou disposições |

Estas linhas são classes de requisitos, não uma disposição de oito fontes
identificadas. O registro de IDs individuais permanecerá vazio até existir um
inventário compartilhado com autorização compatível. O mapa concreto do adaptador,
as perdas e a ferramenta de conversão ficam na branch privada do produtor.

## Uso permitido da evidência por B

B pode continuar sua classificação e preservação pelos procedimentos já autorizados,
usar o contrato para planejar entradas/saídas e registrar dependências ainda abertas.
A aprovação de protocolo, conversão de dados reais, promoção e retirada mantêm seus
gates próprios. `NOT_REQUIRED_BY_A` não é autorização de exclusão ou substituição.

Mudanças no perfil, reader legado, adaptador ou lista de consumidores exigem
reavaliação proporcional. Um handoff append-only na coordenação privada vincula os
SHAs publicados, árvores, resultados de CI/review e pendências desta entrega.
