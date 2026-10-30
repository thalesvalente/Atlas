# Instrução para a conversa de origem — publicar arquivos sem exigir download manual

Na conversa que originalmente gerou `ATLAS-PARITY04-DOC-CI-REPAIR-01.patch` e o ZIP `blocked-exact`, execute:

> Localize os arquivos existentes no mesmo container/sessão que os gerou. Antes de qualquer operação, confira os três paths e recalcule SHA-256 com os bytes lidos de disco. O patch deve ser exatamente `d25540bce2a90dbf099ca38b82528b645ea49c92fd86d04438d5f1b7a58b83b8` e o ZIP exatamente `5788215d2267902988e141fa6db5a9434564b18204356a3a6d80a3dd2a883752`. Não reconstrua a partir do relatório. Confirme se contêm segredos, dados privados, paths de host ou materiais sem permissão de transferência. Não envie conteúdo privado ao GitHub público.
>
> Se os bytes originais existirem e puderem ser publicados, use a integração GitHub conectada para registrá-los **diretamente na branch de evidências deste registro**, sob `docs/missions/atlas-parity-04/ci-repair-recovery-20261030/originals/`, preservando nomes, extensão e bytes. Use blobs Git binários/base64 quando necessário. Registre sha256, Git blob SHA, commit e árvore. Não mexa na PR #14 nessa etapa e não crie worktree/clone.
>
> Se não houver acesso real a escrita GitHub, publique os bytes originais em uma origem verificável pelo usuário sem inventar localizador; caso contrário encerre `BLOCKED_ORIGINAL_ARTIFACTS_UNAVAILABLE` e reporte o impedimento exato. Nunca afirme upload concluído sem commit verificável.

**Este arquivo é uma instrução de recuperação, não uma autorização para expor conteúdo privado.** O ZIP poderá ser recuperado depois por GitHub, sem depender de download pelo operador.
