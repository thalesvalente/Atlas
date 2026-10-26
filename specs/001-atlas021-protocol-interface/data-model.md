# Modelo de dados

Contrato externo: grafo RO-Crate com entidades e propriedades do perfil candidato
(documentado por A1). Fonte permanece autoridade. Read model apenas derivado:
projects, experiments, runs; run id/name/project_id/experiment_id/status/review_status/
synthetic/parameters/metrics/artifacts/inputs/outputs/started_at/ended_at. Identidade
na UI é fonte opaca + ID declarado, sem deduplicação silenciosa entre fontes.

Cada fonte tem versão, status de validação, digest de metadados e disponibilidade de
payload. Digest prova igualdade de bytes na ocasião, não origem nem data autênticas.
Campos desconhecidos não são promovidos a sucesso. Preferências não contêm payloads.
