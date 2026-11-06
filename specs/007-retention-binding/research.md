# Decisões de implementação

- A seleção segue `snapshotKey`, `selectionKey` e os campos de identidade de `native_retention.js`. Os lexemas do DTO entram no digest sem parse e reserialização.
- A pinagem externa dos bytes delega a autenticação ao canal local usado pelo operador. O pin fornecido no próprio documento teria a mesma origem dos dados que ele deveria verificar.
- Aberturas ancoradas no kernel fazem a checagem de contenção durante a resolução. No Linux, `openat2` impede links e cruzamento de mounts abaixo da raiz autorizada. No Windows, cada componente é aberto relativamente ao handle anterior sem seguir reparse points. Os handles permanecem abertos durante a inspeção. [openat2](https://man7.org/linux/man-pages/man2/openat2.2.html), [NtCreateFile](https://learn.microsoft.com/windows/win32/api/winternl/nf-winternl-ntcreatefile), [GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew).
- A relação DTO–arquivo vem do inventário autenticado. Digests iguais de dois arquivos demonstram igualdade de conteúdo na leitura. Independência de backup e espaço liberável precisam de evidência adicional.
