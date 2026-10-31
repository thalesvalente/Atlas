// Deterministic original synthetic scale fixtures. No source corpus or I/O.
export function scaleFixture(base, nodeCount = 2911, relationCount = 1595) {
  if (nodeCount < base.nodes.length || relationCount < base.relations.length) throw new Error('Scale fixture cannot discard seed occurrences');
  const d = structuredClone(base), seed = d.nodes[0], edge = d.relations[0];
  const ref = n => ({ source_id: d.source.source_id, snapshot_id: d.snapshot.snapshot_id, declared_id: n.identity.native_id, target_navigation_id: n.identity.navigation_id, resolution: 'RESOLVED', evidence_locator: n.identity.locator });
  for (let i = d.nodes.length; i < nodeCount; i++) {
    const parent = i === 109 ? d.nodes[1] : d.nodes[109 + Math.floor((i - 110) / 8)];
    const n = structuredClone(seed);
    n.identity = { native_id: 'SYN-SCALE-' + i, navigation_id: 'nav:scale-' + i, navigation_id_kind: 'DERIVED_FOR_PRESENTATION', occurrence: 0, locator: '/synthetic/scale/nodes/' + i };
    n.kind = 'Other'; n.original_type = 'SyntheticScale'; n.label_literal = 'Nó sintético ' + i;
    n.parent_key_literal = parent.identity.native_id; n.parent = ref(parent); n.tree_state = 'PARENT_RESOLVED';
    d.nodes.push(n);
  }
  for (let i = d.relations.length; i < relationCount; i++) {
    const r = structuredClone(edge), a = d.nodes[109 + ((i - 210) % (nodeCount - 109))], b = d.nodes[109 + ((i - 209) % (nodeCount - 109))];
    r.identity = { native_id: null, navigation_id: 'nav:scale-rel-' + i, navigation_id_kind: 'DERIVED_FOR_PRESENTATION', occurrence: 0, locator: '/synthetic/scale/relations/' + i };
    r.from = ref(a); r.to = ref(b); r.evidence_locator = r.identity.locator;
    r.kind_literal = 'NEUTRAL_MENTION'; r.semantics = 'NEUTRAL_MENTION'; r.direction = 'UNDIRECTED';
    r.issues = []; r.repeat_group = null; r.repeat_occurrence = 1; r.binding_gap = false;
    d.relations.push(r);
  }
  const totals = { presentation_node_occurrences: nodeCount, source_nodes: nodeCount - 1, external_reference_stubs: 1, relations: relationCount, tables: 0, rows: 0, assets: 0 };
  for (const c of d.coverage.counts) { c.selected = totals[c.unit]; c.loaded = totals[c.unit]; c.visible = null; }
  return d;
}

// Stress shape is explicitly synthetic, with no hierarchy or inferred relation meaning.
export function stressFixture(base, nodeCount, relationCount) {
  const d = structuredClone(base), seed = d.nodes[0], edge = d.relations[0];
  d.nodes = Array.from({ length: nodeCount }, (_, i) => {
    const n = structuredClone(seed);
    n.identity = { native_id: 'SYN-STRESS-' + i, navigation_id: 'nav:stress-' + i, navigation_id_kind: 'DERIVED_FOR_PRESENTATION', occurrence: 0, locator: '/n/' + i };
    n.label_literal = 'Sintético ' + i; return n;
  });
  const ref = i => ({ source_id: d.source.source_id, snapshot_id: d.snapshot.snapshot_id, declared_id: 'SYN-STRESS-' + i, target_navigation_id: 'nav:stress-' + i, resolution: 'RESOLVED', evidence_locator: '/n/' + i });
  d.relations = Array.from({ length: relationCount }, (_, i) => {
    const r = structuredClone(edge);
    r.identity = { native_id: null, navigation_id: 'nav:stress-rel-' + i, navigation_id_kind: 'DERIVED_FOR_PRESENTATION', occurrence: 0, locator: '/r/' + i };
    r.from = ref(i % nodeCount); r.to = ref((i + 1) % nodeCount); r.evidence_locator = '/r/' + i;
    r.issues = []; r.repeat_group = null; r.repeat_occurrence = 1; r.binding_gap = false; return r;
  });
  d.gaps = []; d.unmapped_fields = [];
  const totals = { presentation_node_occurrences: nodeCount, source_nodes: nodeCount, external_reference_stubs: 0, relations: relationCount, tables: 0, rows: 0, assets: 0 };
  for (const c of d.coverage.counts) { c.selected = totals[c.unit]; c.loaded = totals[c.unit]; c.visible = null; }
  return d;
}
