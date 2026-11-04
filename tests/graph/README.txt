Atlas native graph: synthetic browser acceptance

Run from the repository root with Node 24, Playwright 1.62.1 and Chromium:
  node scripts/qa/browser_native_graph.mjs --report-dir <new-report-directory>

Optional --playwright-path accepts an absolute installed package directory.
Optional --baseline-ref 7c72d9c863871f3541eadb6aac85cab864ad559f captures PR24
with the same fixtures and benchmark operations, without applying the new gates.

Fixtures are invented: a 1202-node star; a 2911-node branched collection;
null/colliding scientific IDs, separate source keys, absent parents and cycles.
All occurrences are exhaustively located; the original input and callback
identity must remain intact. Mouse, keyboard, mobile, culling, progressive
disclosure, minimap, readable zoom, ancestral path and delayed detail reflow
are exercised. Slow double click uses a measured 450 ms between click events.

Engineering gates: mount <1000 ms and synchronous pan p95 <100 ms on this host.
These exclude browser launch, network, asynchronous paint and are not an SLA.
The callback opening the host detail waits 600 ms after a single click so a
double click can complete before the host resizes; visual selection is immediate.
Keyboard and locate callbacks remain immediate.

evidence/ contains only invented-data PNGs and reports. The after report names
the product-code commit and exact JS/CSS hashes. Later test-only commits do not
change those product bytes. Host/private corpus evidence must never be copied
here. The standalone graph harness is an explicit local command; existing CI
continues running the inherited notebook and lineage browser suites.

Integration: mountGraph(host,nodes,onSelect) -> {locate(uid),destroy()} is stable.
The graph receives the complete, validated structural occurrences. Global
filters and occurrence details remain owned by the notebook shell. Only
.graph-* CSS rules and native_graph.js change product behavior.
