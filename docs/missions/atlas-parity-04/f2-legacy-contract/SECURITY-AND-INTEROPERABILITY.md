# Segurança e interoperabilidade — proposta AP04-F2-v0.2

Estado: obrigações de desenho, nenhuma implementação ou qualificação de host.
Entrada: processo externo LOCAL → JSON privado temporário → seleção File API no browser → parser neutro → estado da aba. Nada é enviado a servidor remoto.

## Aquisição e isolamento futuros (G4)

Operador identifica previamente roots autorizadas e a allowlist EXATA de arquivos, com visibilidade e permissão para leitura. A autorização não deriva de nomes, links encontrados ou conteúdo. Sem glob, busca recursiva, descoberta de worktree, leitura de vizinhos, rebuild do produtor, execução de JS/HTML ou chamada de provider. Licença de fonte pública deve ser verificada antes de incorporá-la; conteúdo privado permanece privado e requer liberação específica para qualquer publicação.

Processo externo com permissão de leitura somente no acervo e escrita somente no próprio diretório temporário privado, sem rede/provedores. Se o ambiente não provar essa separação, bloquear aquisição; não afirmar isolamento de OS por mero uso de outra pasta. Nenhuma ACL/configuração é alterada em F2.

Resolver cada alvo e ancestrais contra root real, rejeitar caminhos absolutos recebidos no payload, traversal/percent-decoding, aliases Unicode/casefold, UNC/device/ADS, symlinks/reparse points, hardlinks/arquivos especiais quando não puder ser provada identidade. Abrir por handle com proteção no-follow quando suportada, verificar identidade antes/depois no mesmo handle, tamanho/mtime/digest dos bytes, e recusar troca de alvo ou alteração durante leitura (TOCTOU). Falta de garantia deve gerar UNSAFE/UNVERIFIED e impedir snapshot utilizável, sem certificar host adversarial.

Limites candidatos explícitos, negociáveis somente por versão revisada: até 3 arquivos allowlisted, 64 MiB cada/192 MiB total de entrada, sem recursão/ZIP/extração; descriptor UTF-8 até 32 MiB; profundidade 20; 10.000 nós; 100.000 ocorrências de relações; 128 tabelas; 100.000 linhas no total; 256 colunas por tabela; 64 KiB por literal de célula, lexeme de 128 KiB para escapes e total dentro do limite do descriptor. Até 30 segundos por leitura/validação, cancelamento e limite de memória do processo de 256 MiB imposto pelo host. Se a plataforma não conseguir impor esses limites, recusar a execução. Excesso, JSON com chaves duplicadas, codificação inválida, NaN/Infinity ou truncamento interrompe a importação com erro explícito; nunca exibe subconjunto como completo. São limites propostos, não medições de benchmark. Alterações posteriores têm versão/testes próprios.

## Cache e snapshot

Cache temporário só contém o descriptor necessário, permissões privadas, fora de fontes/checkout, ignorado para publicação. TTL máximo proposto 60 minutos desde emissão, com instante observado separado, sem renovação por acesso. Sem LocalStorage/IndexedDB/service worker, sem logs de payload/path/ID privados. Memória da aba é descartada ao fechar, importar outro snapshot, expirar ou detectar erro. Arquivo é removido somente pelo processo dono, validando path exato e identidade do cache; sem limpeza recursiva de acervo. Backups/temporários do OS e memória não são promessa de apagamento seguro.

Snapshot identifica os bytes efetivamente lidos, escopo e sessão, nunca autoria ou atualidade contínua. Releitura externa compara bytes/tamanho/mtime/identidade com o snapshot anterior e gera nova identidade se mudaram; reimportação/reindexação e nova sessão invalidam todos os links anteriores, mesmo com native_id igual. Browser não conhece alterações posteriores da fonte: exibe «snapshot observado; fonte não reobservada», e expiração impede exportação/navegação. Nenhum hash privado sai da bancada nesta F2.

## Browser e exportação futura (G5)

File API lê somente arquivo selecionado, não uma pasta. Parser/validador neutro rejeita formato/versão desconhecido e URI de schema remoto, preserva lexical numérico e quotas. Não usa eval, innerHTML, iframe, DOM de HTML fonte, imports dinâmicos do descriptor, handlers ou fetch de URI de dados. Textos via textContent; SVG produzido por componentes próprios, IDs de DOM separados de IDs recebidos. URI é string inerte; não abrir file:, javascript:, data:, UNC, links de rede ou anexos. Sem upload/telemetria.

Rotas/APIs existentes continuam Caderno. Nenhum endpoint HTTP sidecar/ingestão proposto. Se um desenho futuro introduzir HTTP, exigirá revisão adicional de origem/CSP, loopback, Host/Origin exatos, CSRF, no-store e quotas antes de operar; esta proposta não o autoriza. Server C4 usa connect-src self, frame-ancestors none, no-store e same-origin; manter essas restrições ao servir assets fixos. Nenhuma porta/servidor foi iniciado por F2.

Filtro/ordenação mantém ocorrência e contexto. Exportação canônica futura é JSON literal tipado com perdas/proveniência. CSV destinado a planilhas neutraliza prefixos =,+,-,@ e whitespace/control chars, faz quoting de aspas/separadores/newlines e registra a transformação; arquivo seguro e valor literal original permanecem distinguíveis. Não anunciar CSV sanitizado como bytes literais originais. Exportação é derivada e privada por padrão, limitada ao snapshot/seleção com contagens e ausências.

## Padrões preservados

| Padrão/contrato | Estado | Regra |
|---|---|---|
| RO-Crate 1.3 | Direção aceita delimitada da ADR-0002 | Não alterar contexto/schema/pins; descriptor não é crate |
| Process Run 0.6 | Direção aceita, sem release implícita | Relação declarada não é execução reproduzida |
| Caderno 0.1.0a1 | Perfil pré-release independente | SDK e reader existentes intactos |
| JSON-LD/PROV | Forma restrita e proveniência declarada no protocolo | Nada de resolução remota ou causalidade inferida |
| HL7/FHIR | FUTURE_CAPABILITY_ONLY_NOT_IMPLEMENTED | Não introduzir recurso clínico no núcleo universal |
| BIM/IFC/IDS/SHACL | Roadmap | Sem implementação ou conformidade nova |

O aceite posterior da ADR-0002 como direção consta em D-007 e não reescreve seu cabeçalho histórico. Não fixa versão/IG/perfil FHIR. Uma futura extensão de saúde requer caso de uso, recursos/perfis, versão, terminologias, identificadores, consentimento/privacidade, proveniência, autorização e testes próprios, fora de F2.

Fontes primárias consultadas apenas para confirmar o escopo: [FHIR, intercâmbio de saúde](https://hl7.org/fhir/) e [Process Run 0.6, extensão de RO-Crate 1.3](https://www.researchobject.org/workflow-run-crate/profiles/0.6/process_run_crate/). Nenhum exemplo dessas fontes foi copiado. Os exemplos deste pacote são originais sintéticos, sem incorporação de fixture de terceiros, sem alteração de licença do repositório.
