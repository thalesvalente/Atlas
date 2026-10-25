# Plano — REUSE-01

## Contexto técnico
Atlas e SDK públicos preservados. Perfil candidato 0.1.0a1 preservado. Produtor privado responsável pela leitura/normalização existentes e pelo adaptador. Python e bibliotecas já usadas pelo produto; sem dependência nova de domínio.

## Constitution Check
ARC-01 interface; ARC-02 protocolo independente; ARC-03 índices derivados; ARC-04 produtores específicos fora do núcleo; ARC-05 prova com instalação isolada; ARC-06 validade não equivale a ciência; ARC-07 nenhuma manutenção física; ARC-08 promoção separada; ARC-09 sem desvio arquitetural. Resultado da análise: compatível.

## Fases
1. Comparar a candidata anterior com APIs/projeções existentes; registrar o que é reutilizado, substituído e mantido.
2. Atualizar spec, clarificações, contratos, checklist e tarefas antes da implementação.
3. Escrever testes que exercitem o pipeline original e exijam a ponte de projeção; registrar RED real.
4. Substituir o leitor paralelo da candidata por um adaptador de projeção. Manter a API sintética anteriormente validada sem relaxar seu gate.
5. Testar conversão, seleção, perdas, estados, precisão, referências e isolamento. Validar o pacote no SDK/viewer público sem introduzir dependência privada.
6. Rodar helpers oficiais do Spec Kit e CI Windows/Ubuntu. Revisão independente pelo Codex; não simular subagentes ausentes.
7. Convergir requisitos/tarefas/evidências e publicar correção nas PRs já abertas, sem merge.

## Limites operacionais
Não há acesso ao H:/G: do operador nesta execução. O código novo não executa leitores suspensos, não descobre raízes e não substitui métodos de preservação. PoC real depende de aquisição permitida pelo produtor e fonte explicitamente selecionada.
