# Decisão de integração técnica

ENGINEERING_IN_PROGRESS. Nenhum merge em main está autorizado. A PR será Draft com ancestry C1/C2/C3 e sem atualização das branches fonte.

Se todos os gates runtime, P01/C3, CI/browser, integridade e revisão independente do SHA C4 passarem, o resultado permitido é C4_FULL_CANDIDATE_READY_HOST_GATE_DEFERRED. Esse estado permite somente handoff e revisão humana de código/evidências. LOCAL_C4_* continua NOT_RUN e HOST_OPERATIONAL_READINESS=false.

Falhas reais de composição/semântica/integridade/CI/revisão levam a C4_BLOCKED_EXACT com causa precisa e trabalho seguro restante concluído. O bloqueio WinError 10013 herdado do C1 sozinho não é uma falha funcional C4 nem causa para interromper a engenharia autorizada.

Protocolo/contexto/schema/versão/exportador/carrier, File/mentions, UNKNOWN/HOLD e ARC-01–09 permanecem. Sem publicação P04, import r4.*, aprovação científica, release, deploy, licença ou promoção.
