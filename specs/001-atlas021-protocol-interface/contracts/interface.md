# Contrato interno da interface candidata

Importação Python: caderno_protocol.load_package(path) -> Package;
validate_document(dict) -> ValidationReport; to_read_model(Package) -> dict.
Package.document, metadata_sha256, report e payload_status. ValidationReport.valid,
errors e warnings. O modelo interno não é formato de intercâmbio.

CLI: `atlas serve --source PATH` repetível; `atlas inspect PATH` para JSON;
`atlas dossier --source PATH` para apresentação derivada em stdout. Sem path scan,
source discovery, escrita no acervo ou comandos científicos.

HTTP loopback: GET /, /app.js, /style.css; GET /api/catalog para snapshot derivado;
POST /api/reindex para reconstruir apenas fontes já declaradas, com Host/Origin
validados e sem aceitar novos paths no request. GET /api/dossier para JSON derivado.
Métodos de escrita no acervo são ausentes. CORS ausente; sem downloads remotos.

A projeção UI acrescenta `display_value` textual a métricas/parâmetros para preservar
inteiros além de 2^53 na apresentação JavaScript. O valor tipado original permanece
no servidor; dossiê é transportado como bytes, sem parse/reencode no navegador.
