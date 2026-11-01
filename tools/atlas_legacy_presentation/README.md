# Ferramenta externa de qualificação sintética F4 C2

Estado: F4_C2_BLOCKED_EXACT para legado real. Este código original público não integra Atlas/Caderno e não importa produtores. A única entrada implementada é o formato de ensaio atlas-legacy-synthetic-source 0.1.0, com synthetic=true. Não é um schema observado do R4. Outros formatos são SOURCE_FORMAT_UNSUPPORTED.

A CLI padrão recusa HARD_BUDGET_UNVERIFIED antes de inspecionar paths. --synthetic-fixture habilita SOMENTE testes com bytes inventados pelo operador; a flag não prova origem pública, permissão nem isolamento. Nunca usar essa flag para acervo L1. Não há confinamento OS de rede/filesystem/memória qualificado. O prazo cooperativo de 30s não é limite duro. G4 fica bloqueado.

Python >=3.11, dependência externa jsonschema==4.25.1 instalada em ambiente de engenharia separado. Executar da raiz pública: python -m tools.atlas_legacy_presentation --source ARQUIVO_ABSOLUTO_INVENTADO --allow MESMO_ARQUIVO_EXATO --scratch PAI_TEMPORARIO_PRIVADO_FORA_DOS_REPOS --synthetic-fixture. A operação cria um diretório próprio privado e um descriptor 0.2.0. Fonte nunca é escrita. Não há glob, busca, recursão, links ativos, providers ou pipeline.

Descriptor possui TTL de até60min. validate_descriptor(...,now=...) recusa expiração; consumidor futuro precisa sempre fornecer relógio real. CLI encerra após emissão; expiração não promete apagar bytes no disco. cleanup_owned remove somente identidade emitida pelo mesmo processo, sem scan e sem recuperação de ownership após crash. ACL/DACL do diretório recém-criado restringe a escrita sintética, mas não prova confinamento do processo ou host adversarial.

SHA-256/tamanho/mtime/ctime/identidade são comparados antes/depois pelo mesmo handle e o path é rechecado. Hash é integridade observada, não autenticidade. TOCTOU adversarial, ACL trocada por outro processo e limpeza após crash não estão qualificados. Nenhum snapshot real utilizável é permitido por esta versão.

Contrato e bloqueios detalhados: docs/missions/atlas-parity-04/f4-c2-reader/READER-CONTRACT.md. Os testes inventam 28 linhas não admitidas, quatro tabelas sem vínculo, colisões e Run isolado; esses números não são leitura ou validação do acervo histórico.
