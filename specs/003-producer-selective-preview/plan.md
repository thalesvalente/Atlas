# Plano de implementação
1. Fixar o HEAD Atlas de manutenção Spec Kit da PR #4 e o contrato Caderno candidato. Executar preflight sem alterar a feature ativa local.
2. Revisar requisitos de consumo já cobertos por SDK e viewer; evitar nova camada de armazenamento ou leitor de diretórios privados.
3. Implementar o adaptador específico exclusivamente na candidata privada R4, com fonte seletiva pinada e somente leitura.
4. Validar o pacote derivado com o SDK público instalado em processo sem R4, incluindo tipos, estados, referências não resolvidas e índice derivado.
5. Reexecutar testes em Ubuntu/Windows normal e `-O`, confrontar resultados com os SHAs dos produtos e revisar os negativos.
6. Documentar comandos para o operador abrir o pacote em G: e selecionar o índice em H: apenas pelo produtor; ausência de acesso real em sessão remota é `NOT_RUN`.
7. Registrar revisão, limites, handoff e PR Draft empilhada. Não fazer merge ou promoção sem decisão humana.

A arquitetura e o formato persistente são invariantes desta feature. A execução de scripts gerados pelo Spec Kit no computador do usuário permanece responsabilidade da frente LOCAL; esta frente remota não simula execução de CLI que não possui.
