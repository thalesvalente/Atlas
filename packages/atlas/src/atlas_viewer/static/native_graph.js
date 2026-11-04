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
  function shortText(text, maxWidth, font) {
    text = String(text); measure.font = font;
    if (measure.measureText(text).width <= maxWidth) return text;
    const chars = Array.from(text);
    while (chars.length && measure.measureText(chars.join('') + '…').width > maxWidth) chars.pop();
    return chars.join('') + '…';
  }
  function makeNode(id) {
    const node = byId.get(id), title = String(node.title ?? 'Sem título');
    const group = el('g', { class: 'graph-node', role: 'treeitem', tabindex: -1,
      'data-native-node': id, 'aria-label': title }, null, true);
    group.append(el('rect', { width: CARD_W, height: CARD_H, rx: 12 }, null, true), el('title', {}, title, true));
    // Two measured title lines stay inside the card, including wide Unicode IDs.
    const words = title.split(/\s+/), lines = ['']; measure.font = '650 17px system-ui';
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
  return { locate, destroy() { disposed = true; clearTimeout(selectionTimer); resize.disconnect(); abort.abort(); elements.clear(); host.replaceChildren(); } };
}
