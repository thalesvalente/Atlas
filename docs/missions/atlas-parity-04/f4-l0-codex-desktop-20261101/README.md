# Atlas AP04-F4 — handoff para Codex LOCAL Windows (L0)

Missão: **AP04-F4-L0-CODEX-DESKTOP-01**. Pacote documental preparado em 01/11/2026, para execução posterior e explícita pelo operador no **Codex LOCAL do desktop Windows**. Publicar o pacote no Git NÃO constitui execução local nem autorização de dados científicos.

## Abrir primeiro

1. **PROMPT-CODEX-LOCAL-L0.md** — instrução principal: execute, não gere um novo prompt.
2. **INPUT-PINS.json** — SHAs e decisões realmente fixadas.
3. **HANDOFF-SANITIZED.schema.json** / **HANDOFF-SANITIZED.template.json** — saída fechada, inicialmente NOT_EXECUTED.
4. **validate_sanitized.py** — validador local somente para o JSON sanitizado escolhido explicitamente; não lê corpus nem fontes.
5. **MANIFEST.sha256** — hashes dos seis arquivos acima, sem incluir a si próprio.

## Fronteira atual

- **C2-D**: PR Draft #18, SHA 86aec49d793d10c1d0b35db58fda747e0febdb23, tree 982da6af550229c45cef5b6bdbca5c1e4bcb4d12; estado C2_D_BLOCKED_EXACT. CI focal 41276067820/1 PASS 4/4, mas não é prova real de aquisição no host.
- **L0**: pode realizar preflight e consulta estrita dos recibos F1 locais. Somente reabrir exatamente três fontes científicas F1 depois de autorização humana explícita **na sessão local**, vinculada aos paths identificados nos recibos.
- **L1**: **NÃO EXECUTAR**. Requer novo C2-D READY_FOR_HOST_PROOF, worker de produção e confinamento filesystem/rede Windows, prova de host, revisão independente e autorizações próprias. K/ARC-09 para source-key/descriptor 0.2.1 também continua pendente.
- **Não é um instalador.** Não baixar ZIP desconhecido, não criar clone/worktree, não executar PowerShell alterando ExecutionPolicy, não varrer discos e não adicionar acervo privado ao Git.

## Recibos de saída

A execução local só pode criar dados de evidência em uma pasta PRIVADA já autorizada no host (fora do repositório e das fontes), sob nomes conforme L0 original. O JSON sanitizado é um **candidato a publicação**, nunca um upload automático. O validador confirma apenas forma e valores autorizados; exige-se revisão de privacidade e aprovação explícita para publicar qualquer recibo do host.

O resultado inicial correto quando não houver autorização de releitura é **F4_L0_SOURCE_NOT_AUTHORIZED** ou **F4_L0_PRECHECK_ONLY**, não G4 PASS. Se não existir Codex realmente local, o estado é LOCAL_WORKSPACE_UNAVAILABLE.

Referências:
- L0 original: docs/missions/atlas-parity-04/f4-direct-reuse-next-20261101/04-L0-LOCAL-REAL-SOURCE-WITNESS.md no SHA 315f7dbeffc80822e96068eed6b4af3193d1b6a7.
- L1 bloqueada: .../06-L1-LOCAL-REAL-READER-PROOF.md no mesmo SHA.
- Recibo final C2-D: https://github.com/thalesvalente/Atlas/pull/18#issuecomment-6553837707.
