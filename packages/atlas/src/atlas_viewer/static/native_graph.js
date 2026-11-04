/* Native structural graph. Presentation never changes the supplied identities.
 * Compact branch shelves, complete search, and viewport culling share one index.
 * No renderer, producer code, or scientific inference is used here.
 */
const NS = 'http://www.w3.org/2000/svg';
const CARD_W = 284, CARD_H = 108, GAP_X = 40, GAP_Y = 28, BRANCH_GAP = 64;
const MIN_ZOOM = .85, MAX_ZOOM = 2.5;
let graphSerial = 0;
function el(tag, attrs = {}, text = null, svg = false) {
  const node = svg ? document.createElementNS(NS, tag) : document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, String(value));
  if (text !== null) node.textContent = text;
  return node;
}

export function mountGraph(host, nodes, onSelect) {
  const serial = ++graphSerial, abort = new AbortController(), signal = abort.signal;
  const byId = new Map(nodes.map(node => [node.uid, node]));
  const declaredParents = new Map(), parents = new Map(), cycles = new Set();
  const children = new Map(nodes.map(node => [node.uid, []]));
  for (const node of nodes) {
    if (byId.has(node.parent_uid)) {
      declaredParents.set(node.uid, node.parent_uid);
      parents.set(node.uid, node.parent_uid);
    }
  }
  // Cut one edge per cycle ONLY for placement. Keep every declared edge for display.
  const done = new Set();
  for (const node of nodes) {
    const chain = [], local = new Map();
    let id = node.uid;
    while (byId.has(id) && !done.has(id)) {
      if (local.has(id)) {
        for (const member of chain.slice(local.get(id))) cycles.add(member);
        parents.delete(id);
        break;
      }
      local.set(id, chain.length); chain.push(id); id = parents.get(id);
    }
    chain.forEach(member => done.add(member));
  }
  for (const [id, parent] of parents) children.get(parent).push(id);
  const roots = nodes.filter(node => !parents.has(node.uid)).map(node => node.uid);
  const dense = nodes.length > 180, rootSet = new Set(roots), collapsed = new Set();
  let viewLimit = dense ? 24 : nodes.length;
  if (dense) for (const node of nodes) {
    if (!rootSet.has(node.uid) && children.get(node.uid).length) collapsed.add(node.uid);
  }
  let positions = new Map(), elements = new Map(), order = [], depths = new Map();
  let width = 900, height = 560, zoom = 1, px = 20, py = 20;
  let selected = null, active = roots[0] ?? null, worldWidth = CARD_W, worldHeight = CARD_H;
  let disposed = false, miniGeometry = { scale: 1, x: 0, y: 0 }, miniCamera, selectionTimer;
  let miniElements = new Map(), selectedMini;
  const box = el('section', { class: 'native-graph graph-shell' });
  const toolbar = el('div', { class: 'graph-toolbar', role: 'toolbar', 'aria-label': 'Navegação da árvore' });
  const path = el('nav', { class: 'graph-path', 'aria-label': 'Caminho ancestral' });
  const svg = el('svg', { class: 'graph-svg', role: 'tree', 'aria-label': 'Árvore estrutural do snapshot',
    tabindex: nodes.length ? -1 : 0, 'aria-describedby': `graph-help-${serial}`, viewBox: '0 0 900 560' }, null, true);
  const world = el('g', {}, null, true), edges = el('g', { 'aria-hidden': 'true' }, null, true);
  const nodeLayer = el('g', {}, null, true);
  const mini = el('svg', { class: 'graph-mini', viewBox: '0 0 200 104', role: 'button', tabindex: 0,
    'aria-label': 'Minimapa: clique ou use setas para navegar; Enter ajusta a vista' }, null, true);
  const footer = el('div', { class: 'graph-footer' });
  const meta = el('div', { class: 'graph-meta', role: 'status' });
  const help = el('p', { class: 'graph-help', id: `graph-help-${serial}` },
    'Setas percorrem a árvore · Enter seleciona · Espaço ou duplo clique expande · Shift + setas move a vista · + / − amplia · 0 ajusta. Linhas indicam parentesco estrutural, não causalidade.');
  const searchStatus = el('span', { class: 'graph-search-status', role: 'status', 'aria-live': 'polite' });
  world.append(edges, nodeLayer); svg.append(world); footer.append(mini, meta);
  box.append(toolbar, path, svg, footer, help); host.replaceChildren(box);
  const listen = (target, name, fn, opts = {}) => target.addEventListener(name, fn, { ...opts, signal });
  function button(label, action, container = toolbar) {
    const result = el('button', { type: 'button', class: 'graph-button' }, label);
    listen(result, 'click', action); container.append(result); return result;
  }
  button('Ampliar +', () => scale(1.2));
  button('Reduzir −', () => scale(1 / 1.2));
  button('Ajustar', fit).title = 'Enquadrar em escala de leitura; o minimapa mostra o conjunto';
  const focusSelection = button('Focar seleção', () => { if (selected !== null) locate(selected); });
  focusSelection.disabled = true;
  button('Expandir todos', () => preserveAnchor(() => { collapsed.clear(); viewLimit = nodes.length; }));
  button('Recolher', () => {
    let target = selected ?? active;
    while (parents.has(target)) target = parents.get(target);
    nodes.forEach(node => { if (children.get(node.uid).length) collapsed.add(node.uid); });
    layout();
    if (target !== null && positions.has(target)) { active = target; if (selected !== null) select(target); center(target); }
    draw();
  });
  const showMore = button('Mostrar mais nós +24', () => preserveAnchor(() => { viewLimit = Math.min(nodes.length, viewLimit + 24); }));
  showMore.hidden = !dense;
  const searchGroup = el('div', { class: 'graph-search' });
  const search = el('input', { type: 'search', class: 'graph-search-input', 'aria-label': 'Localizar nó na árvore', placeholder: 'Título, ID ou fonte…' });
  toolbar.append(searchGroup); searchGroup.append(search);
  button('Localizar / próximo', find, searchGroup); searchGroup.append(searchStatus);
  const searchIndex = nodes.map(node => [node.uid, [node.title, node.native_id, node.source_key, node.uid].join(' ').toLocaleLowerCase('pt-BR')]);
  let searchAt = -1, matches = [];
  listen(search, 'input', () => { searchAt = -1; matches = []; searchStatus.textContent = ''; });
  listen(search, 'keydown', event => { if (event.key === 'Enter') { event.preventDefault(); find(); } });
  function find() {
    const query = search.value.trim().toLocaleLowerCase('pt-BR');
    if (!query) { searchStatus.textContent = 'Digite um título, ID ou fonte.'; return; }
    if (searchAt < 0) matches = searchIndex.filter(([, text]) => text.includes(query)).map(([id]) => id);
    if (!matches.length) { searchStatus.textContent = 'Nenhum nó encontrado.'; return; }
    searchAt = (searchAt + 1) % matches.length;
    locate(matches[searchAt]);
    searchStatus.textContent = `${searchAt + 1} de ${matches.length} resultados`;
  }

  function pack(ids, sizes) {
    // Siblings occupy compact shelves; a deep expanded branch keeps its own space.
    const target = Math.max(CARD_W, Math.min(4 * CARD_W + 3 * GAP_X, width - 40));
    const items = []; let x = 0, y = 0, rowHeight = 0, usedWidth = 0;
    for (const id of ids) {
      const size = sizes.get(id);
      if (x > 0 && x + size.width > target) { y += rowHeight + GAP_Y; x = 0; rowHeight = 0; }
      items.push({ id, x, y }); usedWidth = Math.max(usedWidth, x + size.width);
      x += size.width + GAP_X; rowHeight = Math.max(rowHeight, size.height);
    }
    return { items, width: Math.max(CARD_W, usedWidth), height: ids.length ? y + rowHeight : 0 };
  }
  function layout() {
    const visibleRoots = roots.slice(0, viewLimit), visibleChildren = new Map();
    order = []; depths = new Map();
    const stack = visibleRoots.slice().reverse().map(id => [id, 1]);
    while (stack.length) {
      const [id, depth] = stack.pop(); order.push(id); depths.set(id, depth);
      const next = collapsed.has(id) ? [] : children.get(id).slice(0, viewLimit);
      visibleChildren.set(id, next);
      for (let i = next.length - 1; i >= 0; i--) stack.push([next[i], depth + 1]);
    }
    const sizes = new Map(), packs = new Map();
    for (let i = order.length - 1; i >= 0; i--) {
      const id = order[i], next = visibleChildren.get(id), packed = pack(next, sizes);
      packs.set(id, packed);
      sizes.set(id, { width: packed.width, height: CARD_H + (next.length ? BRANCH_GAP + packed.height : 0) });
    }
    const forest = pack(visibleRoots, sizes); positions = new Map();
    const placements = forest.items.slice().reverse();
    while (placements.length) {
      const { id, x, y } = placements.pop(), size = sizes.get(id);
      positions.set(id, { x: x + 16 + (size.width - CARD_W) / 2, y, left: x + 16 });
      for (const child of packs.get(id).items.slice().reverse()) {
        placements.push({ id: child.id, x: x + child.x, y: y + CARD_H + BRANCH_GAP + child.y });
      }
    }
    worldWidth = forest.width + 32; worldHeight = Math.max(CARD_H, forest.height);
    if (!positions.has(active)) active = positions.has(selected) ? selected : order[0] ?? null;
    updateMinimap();
  }
  function preserveAnchor(change) {
    const id = positions.has(selected) ? selected : active, before = positions.get(id);
    change(); layout(); const after = positions.get(id);
    if (before && after) { px += (before.x - after.x) * zoom; py += (before.y - after.y) * zoom; }
    draw();
  }
  function fit() {
    zoom = Math.max(MIN_ZOOM, Math.min(1, (width - 40) / worldWidth, (height - 40) / worldHeight));
    px = (width - worldWidth * zoom) / 2; py = worldHeight * zoom <= height - 40 ? (height - worldHeight * zoom) / 2 : 24;
    draw();
  }
  function scale(factor, cx = width / 2, cy = height / 2) {
    const next = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom * factor)), ratio = next / zoom;
    px = cx - (cx - px) * ratio; py = cy - (cy - py) * ratio; zoom = next; draw();
  }
  function center(id) {
    const position = positions.get(id); if (!position) return;
    px = width / 2 - (position.x + CARD_W / 2) * zoom;
    py = height / 2 - (position.y + CARD_H / 2) * zoom;
  }
  function ancestors(id) {
    const chain = [], visited = new Set();
    while (byId.has(id) && !visited.has(id)) { visited.add(id); chain.push(id); id = declaredParents.get(id); }
    return chain.reverse();
  }
  function updatePath() {
    path.replaceChildren(); focusSelection.disabled = selected === null;
    if (selected === null) { path.append(el('span', {}, 'Selecione um nó para ver seu caminho e detalhes.')); return; }
    const chain = ancestors(selected);
    let currentCrumb;
    chain.forEach((id, index) => {
      if (index) path.append(el('span', { 'aria-hidden': 'true' }, '›'));
      const crumb = button(String(byId.get(id).title ?? 'Sem título'), () => locate(id), path);
      crumb.title = String(byId.get(id).title ?? 'Sem título');
      if (id === selected) { crumb.setAttribute('aria-current', 'location'); currentCrumb = crumb; }
    });
    if (chain.some(id => cycles.has(id))) path.append(el('span', { class: 'graph-cycle-note' }, 'Ciclo declarado · caminho interrompido na repetição'));
    if (currentCrumb) {
      const crumbRect = currentCrumb.getBoundingClientRect(), pathRect = path.getBoundingClientRect();
      path.scrollLeft += Math.max(0, crumbRect.right - pathRect.right + 12);
    }
  }
  function select(id, notify = true) {
    if (!byId.has(id)) return;
    clearTimeout(selectionTimer);
    selected = id; active = id; updatePath(); draw(); if (notify) onSelect(byId.get(id));
  }
  function cancelPendingSelection() { clearTimeout(selectionTimer); }
  function toggle(id) {
    if (!children.get(id)?.length) return;
    const old = positions.get(id);
    collapsed.has(id) ? collapsed.delete(id) : collapsed.add(id);
    layout();
    if (selected !== null && !positions.has(selected)) { selected = id; updatePath(); onSelect(byId.get(id)); }
    active = id;
    const position = positions.get(id);
    if (old && position) { px += (old.x - position.x) * zoom; py += (old.y - position.y) * zoom; }
    draw(); elements.get(id)?.focus({ preventScroll: true });
  }
  function locate(id) {
    if (!byId.has(id)) return false;
    clearTimeout(selectionTimer);
    let changed = false;
    let child = id, parent = parents.get(child);
    while (parents.has(child)) {
      if (collapsed.has(parent)) changed = true;
      collapsed.delete(parent);
      const required = children.get(parent).indexOf(child) + 1;
      if (required > viewLimit) { viewLimit = required; changed = true; }
      child = parent; parent = parents.get(child);
    }
    const required = roots.indexOf(child) + 1;
    if (required > viewLimit) { viewLimit = required; changed = true; }
    if (changed) layout();
    if (!positions.has(id)) return false;
    active = id; selected = id; center(id); updatePath(); draw(); onSelect(byId.get(id)); return true;
  }
  const measure = document.createElement('canvas').getContext('2d');
  function visualPrefix(text) {
    // Bound presentation work before any canvas measurement or word wrapping.
    // Keep the complete original in search, accessible names and tooltips.
    const chars = [];
    for (const character of String(text)) {
      if (chars.length === 160) return { chars, clipped: true };
      chars.push(character);
    }
    return { chars, clipped: false };
  }
  function shortText(text, maxWidth, font) {
    const { chars, clipped } = visualPrefix(text); measure.font = font;
    const candidate = chars.join('') + (clipped ? '…' : '');
    if (measure.measureText(candidate).width <= maxWidth) return candidate;
    let low = 0, high = chars.length;
    while (low < high) {
      const mid = Math.ceil((low + high) / 2);
      if (measure.measureText(chars.slice(0, mid).join('') + '…').width <= maxWidth) low = mid;
      else high = mid - 1;
    }
    return chars.slice(0, low).join('') + '…';
  }
  function makeNode(id) {
    const node = byId.get(id), title = String(node.title ?? 'Sem título');
    const group = el('g', { class: 'graph-node', role: 'treeitem', tabindex: -1,
      'data-native-node': id, 'aria-label': title }, null, true);
    group.append(el('rect', { width: CARD_W, height: CARD_H, rx: 12 }, null, true), el('title', {}, title, true));
    // Two measured title lines stay inside the card, including wide Unicode IDs.
    const preview = visualPrefix(title);
    const words = (preview.chars.join('') + (preview.clipped ? '…' : '')).split(/\s+/), lines = ['']; measure.font = '650 17px system-ui';
    for (let i = 0; i < words.length; i++) {
      const test = lines[lines.length - 1] + (lines[lines.length - 1] ? ' ' : '') + words[i];
      if (measure.measureText(test).width > 234 && lines.length === 1 && lines[0]) lines.push(words[i]);
      else lines[lines.length - 1] = test;
    }
    lines.forEach((line, index) => {
      const label = el('text', { x: 16, y: 27 + index * 23, class: 'graph-node-title node-title' }, shortText(line, 234, '650 17px system-ui'), true);
      label.append(el('title', {}, title, true)); group.append(label);
    });
    const scientificId = node.native_id ?? node.source_key ?? 'Sem ID científico';
    const identity = el('text', { x: 16, y: 75, class: 'graph-node-meta meta' }, shortText(scientificId, 234, '13px system-ui'), true);
    identity.append(el('title', {}, String(scientificId), true)); group.append(identity);
    group.append(el('text', { x: 16, y: 96, class: 'graph-node-branch' }, '', true));
    return group;
  }
  function edgePath(parent, child) {
    // Route along shelf gutters rather than through cards in preceding rows.
    const sx = parent.x + CARD_W / 2, sy = parent.y + CARD_H;
    const busY = sy + 22, gutter = child.left - 16;
    return `M ${sx} ${sy} V ${busY} H ${gutter} V ${child.y - 12} H ${child.x + CARD_W / 2} V ${child.y}`;
  }
  function updateMinimap() {
    const scale = Math.min(188 / worldWidth, 92 / worldHeight);
    miniGeometry = { scale, x: (200 - worldWidth * scale) / 2, y: (104 - worldHeight * scale) / 2 };
    const { x, y } = miniGeometry;
    miniElements = new Map(); selectedMini = null;
    mini.replaceChildren(el('rect', { class: 'graph-mini-bounds', width: 200, height: 104 }, null, true));
    const overview = el('g', { transform: `translate(${x} ${y}) scale(${scale})` }, null, true);
    for (const [id, position] of positions) {
      const parent = positions.get(declaredParents.get(id));
      if (parent) overview.append(el('path', { class: 'graph-mini-edge', d: edgePath(parent, position) }, null, true));
      const miniNode = el('rect', { class: 'graph-mini-node', 'data-mini-node': id, x: position.x, y: position.y, width: CARD_W, height: CARD_H, rx: 8 }, null, true);
      overview.append(miniNode); miniElements.set(id, miniNode);
    }
    mini.append(overview);
    miniCamera = el('rect', { class: 'graph-mini-camera', 'aria-hidden': 'true' }, null, true); mini.append(miniCamera);
  }
  function draw() {
    if (disposed) return;
    world.setAttribute('transform', `translate(${px} ${py}) scale(${zoom})`);
    const visible = [];
    for (const [id, position] of positions) {
      if ((position.x + CARD_W) * zoom + px >= -20 && position.x * zoom + px <= width + 20 &&
          (position.y + CARD_H) * zoom + py >= -20 && position.y * zoom + py <= height + 20) visible.push([id, position]);
    }
    // Retain the roving focus target even when the camera moves it off screen.
    if (positions.has(active) && !visible.some(([id]) => id === active)) visible.push([active, positions.get(active)]);
    const keep = new Set(visible.map(([id]) => id)), selectedPath = new Set(selected === null ? [] : ancestors(selected));
    for (const [id, node] of elements) if (!keep.has(id)) { node.remove(); elements.delete(id); }
    edges.replaceChildren();
    for (const [id, position] of visible) {
      const parent = positions.get(declaredParents.get(id));
      if (parent) edges.append(el('path', { class: parents.has(id) ? 'graph-edge' : 'graph-edge graph-cycle-edge', d: edgePath(parent, position) }, null, true));
      let group = elements.get(id);
      if (!group) { group = makeNode(id); nodeLayer.append(group); elements.set(id, group); }
      group.setAttribute('transform', `translate(${position.x} ${position.y})`);
      group.setAttribute('aria-selected', String(selected === id));
      group.setAttribute('tabindex', active === id ? 0 : -1);
      group.setAttribute('aria-level', depths.get(id));
      const siblings = parents.has(id) ? children.get(parents.get(id)) : roots;
      group.setAttribute('aria-posinset', siblings.indexOf(id) + 1); group.setAttribute('aria-setsize', siblings.length);
      group.classList.toggle('graph-ancestor', selectedPath.has(id) && selected !== id);
      const count = children.get(id).length;
      if (count) group.setAttribute('aria-expanded', String(!collapsed.has(id)));
      const orphan = byId.get(id).parent_uid != null && !byId.has(byId.get(id).parent_uid);
      group.querySelector('.graph-node-branch').textContent = cycles.has(id) ? '↻ Ciclo declarado' : orphan ? 'Pai fora do snapshot' : count ? `${collapsed.has(id) ? '▸' : '▾'} ${count} filhos${!collapsed.has(id) && count > viewLimit ? ` · ${viewLimit} exibidos` : ''}` : 'Nó terminal';
    }
    const m = miniGeometry, cameraX = m.x - px / zoom * m.scale, cameraY = m.y - py / zoom * m.scale;
    const right = Math.min(200, cameraX + width / zoom * m.scale), bottom = Math.min(104, cameraY + height / zoom * m.scale);
    miniCamera.setAttribute('x', Math.max(0, cameraX)); miniCamera.setAttribute('y', Math.max(0, cameraY));
    miniCamera.setAttribute('width', Math.max(0, right - Math.max(0, cameraX)));
    miniCamera.setAttribute('height', Math.max(0, bottom - Math.max(0, cameraY)));
    selectedMini?.removeAttribute('aria-current'); selectedMini = miniElements.get(selected);
    selectedMini?.setAttribute('aria-current', 'true');
    showMore.disabled = viewLimit >= nodes.length;
    meta.textContent = `${nodes.length} nós carregados · ${positions.size} no foco atual · ${visible.length} na janela · zoom ${Math.round(zoom * 100)}% (mínimo legível 85%) · ${nodes.length - positions.size} recolhidos ou progressivos, todos disponíveis na busca · ${cycles.size} nós em ciclo.`;
  }
  function nodeId(event) { return event.target.closest?.('.graph-node')?.getAttribute('data-native-node'); }
  function focusNode(id) { if (!positions.has(id)) return; active = id; center(id); draw(); elements.get(id)?.focus({ preventScroll: true }); }
  listen(world, 'click', event => {
    const id = nodeId(event); if (id == null) return;
    event.stopPropagation(); select(id, false);
    // The host opens a detail panel on selection. Wait for the double-click
    // gesture before that reflow can move the target between its two clicks.
    selectionTimer = setTimeout(() => { if (!disposed && selected === id) onSelect(byId.get(id)); }, 600);
  });
  listen(world, 'dblclick', event => {
    const id = nodeId(event); if (id == null) return;
    event.stopPropagation(); clearTimeout(selectionTimer); toggle(id); onSelect(byId.get(id));
  });
  listen(world, 'focusin', event => {
    const id = nodeId(event); if (id == null) return;
    const rect = event.target.closest('.graph-node').getBoundingClientRect(), view = svg.getBoundingClientRect();
    const outside = rect.right <= view.left || rect.left >= view.right || rect.bottom <= view.top || rect.top >= view.bottom;
    if (active !== id || outside) { active = id; if (outside) center(id); draw(); }
  });
  listen(svg, 'keydown', event => {
    const id = nodeId(event) ?? active;
    if (event.shiftKey && event.key.startsWith('Arrow')) {
      const moves = { ArrowLeft: [80, 0], ArrowRight: [-80, 0], ArrowUp: [0, 80], ArrowDown: [0, -80] };
      event.preventDefault(); px += moves[event.key][0]; py += moves[event.key][1]; draw(); return;
    }
    let target;
    if (event.key === 'ArrowDown') target = order[Math.min(order.length - 1, order.indexOf(id) + 1)];
    else if (event.key === 'ArrowUp') target = order[Math.max(0, order.indexOf(id) - 1)];
    else if (event.key === 'Home') target = order[0];
    else if (event.key === 'End') target = order[order.length - 1];
    else if (event.key === 'ArrowRight') { if (collapsed.has(id)) toggle(id); else target = children.get(id)?.[0]; }
    else if (event.key === 'ArrowLeft') { if (children.get(id)?.length && !collapsed.has(id)) toggle(id); else target = parents.get(id); }
    else if (event.key === ' ') toggle(id);
    else if (event.key === 'Enter' && id != null) select(id);
    else if (event.key === '+' || event.key === '=') scale(1.2);
    else if (event.key === '-') scale(1 / 1.2);
    else if (event.key === '0') fit();
    else return;
    event.preventDefault(); event.stopPropagation(); if (target !== undefined) focusNode(target);
  });
  let drag = null;
  listen(svg, 'pointerdown', event => {
    if (nodeId(event) != null || event.button !== 0) return;
    drag = { x: event.clientX, y: event.clientY, px, py }; svg.setPointerCapture(event.pointerId);
  });
  listen(svg, 'pointermove', event => {
    if (!drag) return;
    const rect = svg.getBoundingClientRect();
    px = drag.px + (event.clientX - drag.x) * width / rect.width;
    py = drag.py + (event.clientY - drag.y) * height / rect.height; draw();
  });
  listen(svg, 'pointerup', () => { drag = null; }); listen(svg, 'pointercancel', () => { drag = null; });
  listen(svg, 'wheel', event => {
    event.preventDefault(); const rect = svg.getBoundingClientRect();
    scale(event.deltaY < 0 ? 1.1 : 1 / 1.1, (event.clientX - rect.left) * width / rect.width, (event.clientY - rect.top) * height / rect.height);
  }, { passive: false });
  function miniPan(event) {
    const rect = mini.getBoundingClientRect(), m = miniGeometry;
    px = width / 2 - ((event.clientX - rect.left) * 200 / rect.width - m.x) / m.scale * zoom;
    py = height / 2 - ((event.clientY - rect.top) * 104 / rect.height - m.y) / m.scale * zoom; draw();
  }
  listen(mini, 'click', miniPan);
  listen(mini, 'keydown', event => {
    const moves = { ArrowLeft: [width / 2, 0], ArrowRight: [-width / 2, 0], ArrowUp: [0, height / 2], ArrowDown: [0, -height / 2] };
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); fit(); }
    else if (moves[event.key]) { event.preventDefault(); px += moves[event.key][0]; py += moves[event.key][1]; draw(); }
  });
  width = Math.max(260, svg.clientWidth); height = svg.clientHeight || 560;
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  const resize = new ResizeObserver(() => {
    const nextWidth = Math.max(260, svg.clientWidth), nextHeight = svg.clientHeight || 560;
    if (nextWidth === width && nextHeight === height) return;
    width = nextWidth; height = nextHeight; svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    layout(); if (selected !== null && positions.has(selected)) center(selected); else fit(); draw();
  });
  resize.observe(svg); layout(); updatePath(); fit();
  return { locate, cancelPendingSelection, destroy() { disposed = true; clearTimeout(selectionTimer); resize.disconnect(); abort.abort(); elements.clear(); host.replaceChildren(); } };
}


/* Atlas native thematic view.
 * Visual layout/card behavior adapted from the historical R4 renderer:
 * R4-RNF-RES-FIX@789611d.../src/r4/presentation/atlas_assets/
 * graph-layout.js (Git blob 1b6d4afa) and graph-cards.js (edb8ea62).
 * Authorized code reuse: Atlas PR #18 comment 6552216866. No R4 runtime,
 * HTML/inline script, proprietary data, dependencies, or domain-specific labels.
 * Organization lines are NOT scientific provenance/causation.
 */
const R4_MAP_NS = 'http://www.w3.org/2000/svg';
const COLORS = ['#5A91E6','#14A8A3','#9B81DE','#5F8BA2'];
const text = x => String(x ?? '');
function html(tag, cls='', value=null) {
  const node=document.createElement(tag);
  if(cls)node.className=cls;
  if(value!==null)node.textContent=text(value);
  return node;
}
function svgEl(tag, attrs={}, value=null) {
  const node=document.createElementNS(R4_MAP_NS,tag);
  for(const [k,v] of Object.entries(attrs))node.setAttribute(k,text(v));
  if(value!==null)node.textContent=text(value);
  return node;
}
function wrapped(value,max=36,limit=2) {
  const tokens=text(value).split(/\s+/),lines=[];let line='';
  for(const word of tokens) {
    if((line+' '+word).trim().length>max) {
      if(line)lines.push(line);
      line=word;
    } else line=(line+' '+word).trim();
  }
  if(line)lines.push(line);
  const result=lines.slice(0,limit);
  if(lines.length>limit && result.length)result[result.length-1]=result[result.length-1].slice(0,max-1)+'…';
  return result.length?result.map(line=>line.length>max?line.slice(0,max-1)+'…':line):['Não declarado'];
}
function rawFamily(record) {
  const field=(record.fields||[]).find(x=>x.name==='native_family');
  return record.family || (field?.type==='string'?field.text:null) || 'Família não declarada';
}
function groupThemes(families,editorial,mode) {
  const neutral=(items,prefix,label)=>{
    if(!items.length)return [];
    const count=Math.min(3,items.length),columns=Array.from({length:count},()=>[]);
    items.forEach((name,i)=>columns[i%count].push(name));
    return columns.map((members,i)=>({id:prefix+':'+i,title:label+(count>1?' · '+(i+1):''),
      subtitle:'Índice balanceado; não é relação científica',families:members,neutral:true,
      color:'#788D9B'}));
  };
  if(mode==='native')return neutral(families,'native','Famílias de origem');
  if(!editorial || editorial.schema!=='r4-atlas-editorial-map/1'||!Array.isArray(editorial.themes))
    return neutral(families,'unmapped','Famílias sem tema associado');
  const known=new Set(families),claims=new Map();
  for(const t of editorial.themes)for(const f of Array.isArray(t?.families)?t.families:[])
    if(known.has(f))claims.set(f,(claims.get(f)||0)+1);
  const mapped=editorial.themes.filter(x=>typeof x?.id==='string'&&typeof x?.title==='string')
    .map((t,i)=>({id:'editorial:'+t.id,title:t.title,
      subtitle:typeof t.subtitle==='string'?t.subtitle:'Organização editorial declarada; não causal',
      families:(Array.isArray(t.families)?t.families:[]).filter(f=>known.has(f)&&claims.get(f)===1),
      neutral:false,color:COLORS[i%COLORS.length]}))
    .filter(t=>t.families.length);
  const included=new Set(mapped.flatMap(t=>t.families));
  return [...mapped,...neutral(families.filter(f=>!included.has(f)),'unmapped','Famílias sem tema associado')];
}
export function mountR4Map(host, records, onSelect, options={}) {
  // The presentation only consumes already verified Native View occurrences.
  // Never merge entries with the same native_id or infer a source relationship.
  const byUid=new Map(records.map(r=>[r.uid,r])),byFamily=new Map();
  for(const row of records) {
    const family=rawFamily(row);
    if(!byFamily.has(family))byFamily.set(family,[]);
    byFamily.get(family).push(row);
  }
  const familyNames=[...byFamily.keys()].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  let organization='thematic',expanded=new Set(),selected=null,disposed=false;
  let positions=new Map(),drawn=[],width=960,height=640,worldWidth=960,worldHeight=640;
  let zoom=1,tx=25,ty=25,drag=null,pending=null;
  const abort=new AbortController(),signal=abort.signal;
  const listen=(element,type,callback,opts={})=>element.addEventListener(type,callback,{signal,...opts});
  const wrapper=html('section','r4-map');
  const toolbar=html('div','r4-map-toolbar');
  const modeLabel=html('label','r4-map-mode','Organização');
  const mode=html('select');
  for(const [value,label] of [['thematic','Visão temática (R4)'],['native','Famílias de origem']]) {
    const option=html('option','',label);option.value=value;mode.append(option);
  }
  mode.setAttribute('aria-label','Organização do mapa');
  modeLabel.append(mode);toolbar.append(modeLabel);
  const overlayLabel=html('label','r4-map-overlay');
  const overlay=document.createElement('input');overlay.type='checkbox';
  overlayLabel.append(overlay,document.createTextNode('Mostrar relações declaradas'));
  toolbar.append(overlayLabel);
  const buttons=html('div','r4-map-buttons');toolbar.append(buttons);
  const scene=svgEl('svg',{'class':'r4-map-svg',viewBox:'0 0 960 640',
    role:'group','aria-label':'Mapa temático por famílias da revisão'});
  const world=svgEl('g'),edgeLayer=svgEl('g',{'aria-hidden':'true'}),cards=svgEl('g');
  world.append(edgeLayer,cards);scene.append(world);
  const bottom=html('div','r4-map-bottom'),mini=svgEl('svg',{'class':'r4-map-mini',viewBox:'0 0 200 108',
    role:'button',tabindex:'0','aria-label':'Minimapa do conjunto'});
  const caption=html('p','r4-map-caption');
  bottom.append(mini,caption);
  wrapper.append(toolbar,scene,bottom);host.replaceChildren(wrapper);
  function addButton(label,fn) {
    const button=html('button','r4-map-button',label);button.type='button';
    listen(button,'click',fn);buttons.append(button);return button;
  }
  addButton('Mostrar tudo',fit);
  addButton('Zoom confortável',comfortable);
  addButton('Focar seleção',()=>{if(selected)locate(selected);});
  addButton('Expandir famílias',()=>{expanded=new Set(familyNames);refresh(true);});
  addButton('Recolher',()=>{expanded.clear();refresh(true);});
  addButton('＋',()=>scale(1.25));
  addButton('−',()=>scale(.8));
  addButton('Tela inteira',()=>{if(document.fullscreenElement===wrapper)document.exitFullscreen();
    else if(wrapper.requestFullscreen)wrapper.requestFullscreen().catch(()=>{});});
  function themes(){
    return groupThemes(familyNames,options.editorial,organization)
      .map(t=>({...t,sets:t.families.map(f=>({family:f,rows:byFamily.get(f)||[]}))
        .filter(set=>set.rows.length)})).filter(t=>t.sets.length);
  }
  function layout() {
    const groups=themes(),count=groups.length;
    const isCompact=!familyNames.some(f=>expanded.has(f));
    const branchW=isCompact?370:566,branchGap=isCompact?28:40,left=30;
    const pageW=Math.max(800,left*2+count*branchW+Math.max(0,count-1)*branchGap);
    const output=[];
    output.push({id:'r4-root',type:'root',title:'Caderno científico',
      subtitle:records.length+' registros · '+familyNames.length+' famílias declaradas',
      x:(pageW-404)/2,y:22,w:404,h:90});
    let deepest=340;
    for(let i=0;i<groups.length;i++){
      const t=groups[i],bx=left+i*(branchW+branchGap);
      const count=t.sets.reduce((sum,set)=>sum+set.rows.length,0);
      output.push({id:'theme:'+t.id,type:'theme',title:t.title,subtitle:t.subtitle,
        theme:t.id,color:t.color,ordinal:i+1,count,x:bx+12,y:isCompact?170:185,w:branchW-24,h:92});
      let y=isCompact?290:318;
      for(const set of t.sets){
        const family={id:'family:'+set.family,type:'family',title:set.family,
          theme:t.id,color:t.color,count:set.rows.length,x:bx+22,y,w:branchW-44,h:90};
        output.push(family);
        if(expanded.has(set.family)){
          const rows=set.rows.slice().sort((a,b)=>text(a.title).localeCompare(text(b.title),'pt-BR'));
          const start=y+115,childW=234,childH=102,gap=118;
          rows.forEach((entry,j)=>output.push({id:'record:'+entry.uid,uid:entry.uid,
            type:'record',title:entry.title,subtitle:entry.status||'Estado não declarado',
            theme:t.id,color:t.color,parent:family.id,x:bx+43+(j%2)*260,
            y:start+Math.floor(j/2)*gap,w:childW,h:childH}));
          y=start+Math.ceil(rows.length/2)*gap+30;
        }else y+=115;
      }
      deepest=Math.max(deepest,y+40);
    }
    drawn=output;positions=new Map(output.map(n=>[n.id,n]));
    worldWidth=pageW;worldHeight=deepest;
  }
  function link(d,stroke,width=1.6,dash='',label='') {
    const path=svgEl('path',{d,fill:'none',stroke,'stroke-width':width,
      'stroke-dasharray':dash,'stroke-linecap':'round',
      'vector-effect':'non-scaling-stroke'});
    if(label)path.append(svgEl('title',{},label));
    edgeLayer.append(path);
  }
  function drawEdges() {
    const root=positions.get('r4-root'),groups=themes();
    for(const t of groups){
      const theme=positions.get('theme:'+t.id);if(!theme)continue;
      const a=root.x+root.w/2,b=theme.x+theme.w/2;
      link('M '+a+' '+(root.y+root.h)+' V 135 H '+b+' V '+theme.y,
        '#a9bfca',2,'','Agrupamento de apresentação: não declara causalidade');
      const fam=t.sets.map(set=>positions.get('family:'+set.family)).filter(Boolean);
      for(const f of fam){
        const x=theme.x+20;
        link('M '+x+' '+(theme.y+theme.h)+' H '+(x-12)+' V '+(f.y+38)+' H '+f.x,
          '#aec3ce',1.4,'','Família declarada na revisão; relação de organização');
        const members=drawn.filter(n=>n.parent===f.id);
        for(const c of members){
          link('M '+(f.x+20)+' '+(f.y+f.h)+' V '+(c.y-12)+' H '+(c.x+14)+' V '+c.y,
            '#bfd0d9',1.25,'','Pertencimento à família, não dependência científica');
        }
      }
    }
    if(!overlay.checked)return;
    // Overlay only relations with unambiguous declared record IDs.
    const claims=new Map();
    for(const row of records){
      const idField=(row.fields||[]).find(f=>f.name==='id'&&f.type==='string');
      const key=idField?.text||row.source_key;
      if(typeof key!=='string'||!key)continue;
      if(!claims.has(key))claims.set(key,[]);
      claims.get(key).push(row.uid);
    }
    let shown=0;
    for(const relationship of options.relations||[]){
      let data;
      try{data=JSON.parse(relationship.raw_json);}catch{continue;}
      if(typeof data?.from!=='string'||typeof data?.to!=='string')continue;
      const src=claims.get(data.from),dst=claims.get(data.to);
      if(src?.length!==1||dst?.length!==1)continue;
      const a=positions.get('record:'+src[0]),b=positions.get('record:'+dst[0]);
      if(!a||!b)continue;
      link('M '+(a.x+a.w/2)+' '+a.y+' C '+(a.x+a.w/2)+' '+(a.y-35)+
        ' '+(b.x+b.w/2)+' '+(b.y-35)+' '+(b.x+b.w/2)+' '+b.y,
        '#278f97',2,'6 4','Relação declarada: '+text(data.type||data.kind||'sem tipo'));
      shown++;
    }
    caption.dataset.relations=String(shown);
  }
  function card(node) {
    const root=node.type==='root',theme=node.type==='theme',family=node.type==='family';
    const chosen=node.uid&&node.uid===selected;
    const g=svgEl('g',{transform:'translate('+node.x+' '+node.y+')',
      'class':'r4-map-card r4-map-'+node.type+(chosen?' selected':''),
      role:'button',tabindex:'0','data-r4-id':node.id,
      'aria-label':node.title,'aria-expanded':family?String(expanded.has(node.title)):'',
      'data-uid':node.uid||''});
    g.append(svgEl('rect',{width:node.w,height:node.h,rx:root?18:theme?15:12,
      class:'r4-map-surface'}));
    if(!root)g.append(svgEl('rect',{x:0,y:12,width:5,height:node.h-24,rx:2,
      fill:node.color||'#788D9B'}));
    if(theme){
      g.append(svgEl('rect',{x:15,y:14,width:36,height:30,rx:9,fill:node.color}));
      g.append(svgEl('text',{x:33,y:35,'text-anchor':'middle',
        'class':'r4-map-number'},String(node.ordinal).padStart(2,'0')));
    }
    const x=theme?65:root?20:17,max=theme?35:family?40:root?36:node.w>=240?35:28;
    wrapped(node.title,max,2).forEach((line,i)=>
      g.append(svgEl('text',{x,y:theme?27+i*18:root?30+i*19:27+i*17,
        'class':'r4-map-title'},line)));
    const subtitle=root?node.subtitle:family?
      node.count+' registros · '+(expanded.has(node.title)?'Recolher −':'Expandir +'):
      node.subtitle||'';
    g.append(svgEl('text',{x:17,y:node.h-13,'class':'r4-map-subtitle'},
      [...text(subtitle)].slice(0,80).join('')));
    g.append(svgEl('title',{},node.title+' · '+subtitle));
    return g;
  }
  function invokeCard(event) {
    const element=event.target.closest?.('.r4-map-card');
    if(!element)return;
    const node=positions.get(element.getAttribute('data-r4-id'));
    if(!node)return;
    if(node.type==='root'){fit();return;}
    if(node.type==='theme'){focusTheme(node);return;}
    if(node.type==='family'){toggleFamily(node.title);return;}
    if(node.uid){selected=node.uid;render();onSelect(byUid.get(node.uid));}
  }
  listen(cards,'click',invokeCard);
  listen(cards,'keydown',event=>{
    if(event.key==='Enter'||event.key===' '){event.preventDefault();invokeCard(event);}
  });
  function render(){
    if(disposed)return;
    edgeLayer.replaceChildren();cards.replaceChildren();
    drawEdges();
    const inView=n=>(n.x+n.w)*zoom+tx>=0&&n.x*zoom+tx<=width&&
      (n.y+n.h)*zoom+ty>=0&&n.y*zoom+ty<=height;
    for(const n of drawn)if(inView(n))cards.append(card(n));
    drawMini();
    const shown=drawn.filter(n=>n.type==='record').length;
    caption.textContent=records.length+' registros disponíveis · '+familyNames.length+
      ' famílias literais · '+shown+' registros expandidos · '+drawn.length+
      ' cartões no mapa. Linhas cinza: organização, não causalidade.'+
      (overlay.checked?' Relações sobrepostas só quando declaradas e únicas.':'');
  }
  function camera(){world.setAttribute('transform','translate('+tx+' '+ty+') scale('+zoom+')');render();}
  function fit(){
    zoom=Math.max(.45,Math.min(1.15,(width-38)/worldWidth,(height-38)/worldHeight));
    tx=(width-worldWidth*zoom)/2;ty=20;camera();
  }
  function comfortable(){
    zoom=1;tx=width/2-(worldWidth/2)*zoom;ty=20;camera();
  }
  function scale(factor){
    const next=Math.max(.35,Math.min(3.5,zoom*factor)),ratio=next/zoom;
    tx=width/2-(width/2-tx)*ratio;ty=height/2-(height/2-ty)*ratio;
    zoom=next;camera();
  }
  function center(node){
    zoom=Math.max(.8,zoom);
    tx=width/2-(node.x+node.w/2)*zoom;
    ty=height/2-(node.y+node.h/2)*zoom;camera();
  }
  function focusTheme(node){center(node);}
  function refresh(preserve=false,anchor=null){
    const previous=anchor?positions.get(anchor):null;
    const x=previous?previous.x+previous.w/2:null,y=previous?previous.y+previous.h/2:null;
    layout();
    if(anchor&&positions.has(anchor)&&x!==null&&y!==null){
      const next=positions.get(anchor);
      tx+=(x-next.x-next.w/2)*zoom;
      ty+=(y-next.y-next.h/2)*zoom;
    }
    if(!preserve)fit();else camera();
  }
  function toggleFamily(name){
    expanded.has(name)?expanded.delete(name):expanded.add(name);
    refresh(true,'family:'+name);
  }
  function locate(uid){
    const row=byUid.get(uid);
    if(!row)return false;
    const family=rawFamily(row);
    expanded.add(family);layout();
    const node=positions.get('record:'+uid);
    if(!node)return false;
    selected=uid;center(node);onSelect(row);return true;
  }
  function drawMini(){
    mini.replaceChildren(svgEl('rect',{width:200,height:108,fill:'#eef5fb'}));
    const sx=200/worldWidth,sy=108/worldHeight;
    for(const n of drawn)mini.append(svgEl('rect',{x:n.x*sx,y:n.y*sy,
      width:Math.max(1,n.w*sx),height:Math.max(1,n.h*sy),rx:1,
      fill:n.type==='root'?'#1d526a':n.type==='theme'?'#4d9ba9':
        n.type==='family'?'#86b7c6':n.uid===selected?'#d39a44':'#bccdd8'}));
    mini.append(svgEl('rect',{'class':'r4-map-camera',x:Math.max(0,-tx/zoom*sx),
      y:Math.max(0,-ty/zoom*sy),width:Math.min(200,width/zoom*sx),
      height:Math.min(108,height/zoom*sy)}));
  }
  listen(mode,'change',()=>{organization=mode.value;refresh();});
  listen(overlay,'change',render);
  listen(scene,'pointerdown',e=>{
    if(e.button!==0||e.target.closest('.r4-map-card'))return;
    drag={x:e.clientX,y:e.clientY,tx,ty};scene.setPointerCapture(e.pointerId);
  });
  listen(scene,'pointermove',e=>{
    if(!drag)return;
    const rect=scene.getBoundingClientRect();
    tx=drag.tx+(e.clientX-drag.x)*width/rect.width;
    ty=drag.ty+(e.clientY-drag.y)*height/rect.height;camera();
  });
  listen(scene,'pointerup',()=>{drag=null;});
  listen(scene,'pointercancel',()=>{drag=null;});
  listen(scene,'wheel',e=>{e.preventDefault();scale(e.deltaY<0?1.12:1/1.12);},
    {passive:false});
  listen(scene,'keydown',e=>{
    const directions={ArrowLeft:[40,0],ArrowRight:[-40,0],ArrowUp:[0,40],ArrowDown:[0,-40]};
    if(directions[e.key]){e.preventDefault();tx+=directions[e.key][0];
      ty+=directions[e.key][1];camera();}
  });
  listen(mini,'click',e=>{
    const rect=mini.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width*worldWidth,
      y=(e.clientY-rect.top)/rect.height*worldHeight;
    tx=width/2-x*zoom;ty=height/2-y*zoom;camera();
  });
  listen(mini,'keydown',e=>{if(e.key==='Enter'){e.preventDefault();fit();}});
  const resize=new ResizeObserver(()=>{
    width=Math.max(300,scene.clientWidth);height=scene.clientHeight||640;
    scene.setAttribute('viewBox','0 0 '+width+' '+height);camera();
  });
  resize.observe(scene);layout();fit();
  return {
    locate,
    cancelPendingSelection(){if(pending!==null){clearTimeout(pending);pending=null;}},
    destroy(){
      disposed=true;resize.disconnect();abort.abort();
      if(pending!==null)clearTimeout(pending);
      wrapper.remove();host.replaceChildren();
    }
  };
}
