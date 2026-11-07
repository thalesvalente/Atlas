# Plano incremental

Reusar leitor Native View, projeção preservada, testes e componentes aprovados.
P00 é writer exclusivo de código. Agentes A/B/C produzem recibos privados.

1. Autenticar fontes/SHAs e executar Spec Kit instalado sem instalar ferramentas,
   sem trocar feature.json e sem reconstruir inventários válidos.
2. Acrescentar CSV tipado em native_legacy_model.js, integrado à tabela existente.
   Cada célula é envelope JSON com tipo/presença e token original, sem Number.
   Linha original completa e identidade estrutural acompanham a exportação.
3. Acrescentar tools/verify_native_parity.py, oráculo offline com pins explícitos.
   Reusar read_source/restore_projection; resultados de dados nunca qualificam UI.
4. RED/GREEN, suíte existente, instalação local sem R4 e CI no SHA publicado.
5. QA não autora, matrizes privadas, patch R4 proposto separado e rollback.

Sem nova rota HTTP, dependência, worktree, mudança de schema, execução de produtor,
migração, exclusão científica, merge, release ou deploy.
