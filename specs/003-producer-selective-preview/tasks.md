# Tarefas — correção REUSE-01

## Especificação e desenho
- [x] R001 Conferir direção do usuário e ARC-01–09; manter ADR-0002 pendente.
- [x] R002 Comparar APIs legadas e identificar duplicação no adaptador anterior.
- [x] R003 Atualizar spec, clarificações, pesquisa, plano, dados, contrato e checklist.
- [x] R004 Analisar consistência entre fronteiras, retenção e interoperabilidade.

## Execução e convergência técnica
- [x] R005 Registrar teste RED da ponte exigida sobre a baseline, com recibos privados.
- [x] R006 Implementar adaptador privado sobre projeção existente e superseder o leitor paralelo sem I/O.
- [x] R007 Provar SDK/viewer independentes, origem preservada no ensaio e limites semânticos.
- [x] R008 Executar helpers oficiais e CI focal, com SHAs/ambientes explícitos.
- [x] R009 Obter revisão independente da implementação e da especificação; registrar escopo por SHA.
- [x] R010 Publicar convergência e guia revisado, sem atribuir os resultados a dados reais.

O fechamento documental não altera SDK/viewer/perfil. CI/review posteriores deste commit documental são registrados de forma append-only na PR; não se atribui antecipadamente a eles o PASS da implementação anterior.

## Gates separados e ainda abertos
- [ ] R011 Aquisição/piloto no host real: NOT_RUN nesta sessão remota.
- [ ] R012 ADR-0002, merge e promoção: decisões humanas separadas.
