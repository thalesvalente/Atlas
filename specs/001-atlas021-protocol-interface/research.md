# Pesquisa e decisões de engenharia

Protocolo: trabalho A1 em `research/protocol-options.md` e ADR-0002. RO-Crate1.3 e
ProcessRun0.6 são candidatos compatíveis; .eln1.2 permanece alternativa de intercâmbio
com versão diferente. Pin e licença de fontes documentados pelo owner A1.

Stack: Python stdlib para SDK e servidor local, wheel separado por camada. Motivo:
instalação sem produtor legado e execução offline. SPA com assets embarcados reduz
build runtime/dependências. React/SaaS/banco foram descartados por não haver requisito
que justifique mais infraestrutura. UI não escreve no acervo; SDK pode ler ZIP com limites sem extrair para disco.

Spec Kit1.2.3 instalado via pacote oficial, init e scripts auxiliares executados.
Skills Codex `$speckit-*` lidas e aplicadas pelo agente; Codex CLI não está disponível,
logo não se alega invocação nativa dessas skills em outro agente/terminal.
