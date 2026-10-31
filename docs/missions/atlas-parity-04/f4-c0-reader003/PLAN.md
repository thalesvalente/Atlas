# PLAN — AP04-F4-C0-READER003-CONTRACT-CHAT-01

Owner/writer: coordenador /root; A contrato e B segurança apenas análise; C revisão independente sem autoria. Data: 2026-10-31 (America/Fortaleza). Esforço efetivo: UNVERIFIED.
Estado inicial: PLAN_RECORDED; alvo documental F4_C0_READER003_SCOPED_CONTRACT_REVIEWED.

## Entradas e autoridade

Branch exclusiva preexistente docs/atlas-parity04-f4-reader003-20261031 observada em 54bb16d350f7bc34fafb95438bd64a2397d58bf3, tree 1372dd532b2323fc1ebaa5c2f00b6d537c636dc9. Prompt lido em c4f1204d75222c1a72678d22f1a4b23f1a33ab8f, blob 1446b71cd71f6f231d0b3888969901294bd7dd8c. O prompt está em outra história; é entrada por SHA, não será copiado nem integrado à branch C0.

Aplicam-se AP04-POR-v1.0-draft, D-001–D-020, ARC-01–09, ADR-0001/0002 e aprovação humana APPROVED_SCOPED da ADR-0003 v0.2/descriptor0.2.0 do pacote c3ea1e82938fd61cc5a22fee973352715a5bb527, tree 986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c, comentário https://github.com/thalesvalente/Atlas/pull/15#issuecomment-6539419419. F1 a237f446e54927eeeda8ed5e8e9daa83ee09dcb7 é evidência sanitizada anterior, não autorização de fonte atual.

## Sequência autorizada

1. PLAN: ler fontes e specs/001-atlas021-protocol-interface; fixar entradas, ownership e invariantes; registrar este plano em Git antes da autoria técnica.
2. EXECUTE: criar somente specs/003-producer-selective-preview/contracts/reader.ap04-legacy-presentation-v0.2.md e documentos nesta pasta. Explicitar sucessão local das duas frases globais do reader003; via Caderno exclusiva e inalterada. Herdar descriptor/schema F2 por blob, sem novo formato. Documentar impacto, segurança, rollback e oracles C3/C4, todos runtime NOT_RUN.
3. REVIEW: publicar pacote completo com RESULT.md, INPUT-SHAS.json, CONTRACT-DELTA.md, SECURITY-AND-ROLLBACK.md, INDEPENDENT-REVIEW.md, HANDOFF.json e MANIFEST.sha256; C nativo revisa por SHA/tree/parent sem autoria. Corrigir achados somente no escopo; persistir parecer e handoff, então C confere HEAD terminal e recibo externo na PR Draft.
4. Verificar delta exato e imutabilidade dos blobs fora do ownership, proveniência dos objetos, manifestos e resultados de CI automática se disparada. Rejeição histórica dos novos documentos será CI_SUCCESSION_TO_QUALIFY_C4, sem relaxar auditorias ou pins. Não exigir nem alegar G4/G5 pela documentação C0.

## Custódia sem autorreferência

UTF-8 e LF, mode 100644. MANIFEST.sha256 cobre todos os outros arquivos C0, com paths de raiz; exclui a si próprio para evitar digest circular. Inventário suplementar OUTPUT-OBJECTS.json registra blobs do payload e seu commit/tree/parents por SHA. Recibos posteriores apontam para objetos já existentes; o SHA/tree/parents do próprio recibo são resolvidos pelo envelope Git e publicados na PR. Não inventar SHA próprio, não usar placeholder como digest. O fechamento pode acrescentar somente documentos de custódia nesta pasta; revisão terminal externa preserva o HEAD sem loop de commits. C3 deve fixar o SHA terminal e todos os blobs, inclusive recibos e manifesto.

## Limites e contingências

Sem implementação, integração, runtime, SDK/protocolo, reader.md histórico, constituição/ADRs, F1/F2/GATES/workflows, feature.json, fontes privadas, licença ou chamadas pagas. Sem worktree/clone, merge, release, deploy, promoção, migração ou limpeza. Coordenador é único publisher. Uso do conector GitHub é o ambiente CHAT previsto; shell e node locais falharam no launcher MXC ao enumerar D: antes de execução, logo status/HEAD local e testes locais são UNVERIFIED/NOT_RUN. Checkout local não será alterado.

Nenhuma mudança de AP04-POR é proposta. Se a precedência não puder ser legitimada pela exceção aprovada, registrar F4_C0_ARCHITECTURAL_DECISION_REQUIRED antes de qualquer ampliação; solicitar decisão humana com alternativas/risco/diff, sem editar congelados.
