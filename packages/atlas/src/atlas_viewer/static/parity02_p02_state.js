/* Pure presentation state. No DOM, storage, network or scientific decisions. */
(function (global) {
  'use strict';

  const VIEWS = Object.freeze(['explore', 'compare', 'timeline', 'lineage', 'sources', 'dossier']);
  const SORTS = Object.freeze(['title', 'id', 'source', 'status', 'review', 'time-asc', 'time-desc']);
  const PRESENCE = Object.freeze(['any', 'yes', 'no']);
  const STATUSES = Object.freeze(['', 'COMPLETED', 'PARTIAL', 'FAILED', 'RUNNING', 'UNKNOWN']);
  const REVIEWS = Object.freeze(['', 'UNKNOWN', 'HOLD', 'ACCEPTED', 'REJECTED', 'NOT_APPLICABLE']);
  const FIELDS = Object.freeze({query: 'q', project: 'project', experiment: 'experiment',
    source: 'source', status: 'status', review: 'review', metrics: 'metrics',
    references: 'references', sort: 'sort'});
  const PARAMETERS = new Set(['v', 'scope', 'view', 'run', 'selected', ...Object.values(FIELDS)]);
  const MAX_HASH_LENGTH = 65536;
  const MAX_TEXT_LENGTH = 8192;

  function defaults() {
    return {view: 'explore', detail: null, selected: [], filters: {query: '', project: '',
      experiment: '', source: '', status: '', review: '', metrics: 'any', references: 'any', sort: 'title'}};
  }

  function key(source, id) { return JSON.stringify([source, id]); }

  function text(value) { return value === null || value === undefined ? '' : String(value); }
  function folded(value) { return text(value).normalize('NFKC').toLowerCase(); }
  function compareText(a, b) { return a < b ? -1 : a > b ? 1 : 0; }

  function flatten(catalog) {
    const runs = [];
    for (const source of catalog?.sources || []) {
      for (const run of source.read_model?.runs || []) {
        runs.push({...run, _sourceId: source.id, _sourceName: source.name,
          _sourceSnapshot: source.snapshot_id, _key: key(source.id, run.id)});
      }
    }
    return runs;
  }

  function sortRuns(runs, sort = 'title') {
    const field = {title: 'name', id: 'id', source: '_sourceName', status: 'status', review: 'review_status'}[sort];
    return [...runs].sort((a, b) => {
      let compared = 0;
      if (sort === 'time-asc' || sort === 'time-desc') {
        // Missing or unparsable declared time remains last in either direction.
        // Sorting does not relabel an observed timestamp as an event timestamp.
        const at = a.started_at ? Date.parse(a.started_at) : NaN;
        const bt = b.started_at ? Date.parse(b.started_at) : NaN;
        if (Number.isFinite(at) !== Number.isFinite(bt)) return Number.isFinite(at) ? -1 : 1;
        if (Number.isFinite(at) && at !== bt) compared = (at - bt) * (sort === 'time-desc' ? -1 : 1);
      } else {
        const actualField = field || 'name';
        const av = a[actualField] || (actualField === 'name' ? a.id : '');
        const bv = b[actualField] || (actualField === 'name' ? b.id : '');
        compared = compareText(folded(av), folded(bv)) || compareText(text(av), text(bv));
      }
      // Explicit tie-breakers avoid dependence on graph/insertion order or locale.
      return compared || compareText(folded(a._sourceName), folded(b._sourceName)) ||
        compareText(text(a.id), text(b.id)) || compareText(text(a._key), text(b._key));
    });
  }

  function presenceMatches(values, presence) {
    const present = Array.isArray(values) && values.length > 0;
    return presence !== 'yes' && presence !== 'no' || (presence === 'yes' ? present : !present);
  }

  function filterRuns(runs, filters = {}) {
    const f = {...defaults().filters, ...filters};
    const query = folded(f.query).trim();
    const matches = runs.filter(run =>
      (!query || folded([run.name, run.id, run.description, run._sourceName, run._sourceId].map(text).join(' ')).includes(query)) &&
      (!f.source || run._sourceId === f.source) &&
      (!f.project || key(run._sourceId, run.project_id) === f.project) &&
      (!f.experiment || key(run._sourceId, run.experiment_id) === f.experiment) &&
      (!f.status || run.status === f.status) && (!f.review || run.review_status === f.review) &&
      presenceMatches(run.metrics, f.metrics) && presenceMatches(run.related_references, f.references));
    return sortRuns(matches, f.sort);
  }

  function invalid(message, reason = 'INVALID_ROUTE') {
    return {route: defaults(), warnings: [message], rejected: true, reason};
  }

  function canonicalKey(value) {
    if (typeof value !== 'string' || value.length > MAX_TEXT_LENGTH) throw new Error('Invalid identity');
    const pair = JSON.parse(value);
    if (!Array.isArray(pair) || pair.length !== 2 || pair.some(item => typeof item !== 'string' || !item)) {
      throw new Error('Invalid identity');
    }
    return key(pair[0], pair[1]);
  }

  function scalar(value) {
    if (typeof value !== 'string' || value.length > MAX_TEXT_LENGTH || /[\u0000-\u001f\u007f]/u.test(value)) {
      throw new Error('Invalid scalar');
    }
    return value;
  }

  function parse(hash, catalog) {
    if (hash === '' || hash === '#' || hash === null || hash === undefined) {
      return {route: defaults(), warnings: [], rejected: false, reason: null};
    }
    if (typeof hash !== 'string' || hash[0] !== '#' || hash.length > MAX_HASH_LENGTH) {
      return invalid('Endereço inválido ou acima do limite de leitura. Nenhuma execução foi aberta.');
    }
    const raw = hash.slice(1);
    let params;
    try {
      // URLSearchParams alone repairs malformed percent encodings silently.
      // Reject them before looking up any source or entity.
      decodeURIComponent(raw.replace(/\+/g, '%20'));
      params = new URLSearchParams(raw);
      const seen = new Set();
      for (const [name, value] of params) {
        if (!PARAMETERS.has(name) || seen.has(name)) throw new Error('Unknown or repeated parameter');
        seen.add(name);
        if (name !== 'selected') scalar(value);
      }
      if (params.has('v') && params.get('v') !== '1') throw new Error('Unsupported route version');
    } catch (_) {
      return invalid('Endereço malformado, com parâmetro repetido/desconhecido ou versão incompatível. Nenhuma execução foi aberta.');
    }
    const route = defaults();
    try {
      route.view = params.get('view') || route.view;
      if (!VIEWS.includes(route.view)) throw new Error('Invalid view');
      for (const [field, parameter] of Object.entries(FIELDS)) {
        if (params.has(parameter)) route.filters[field] = params.get(parameter);
      }
      if (!SORTS.includes(route.filters.sort) || !PRESENCE.includes(route.filters.metrics) ||
          !PRESENCE.includes(route.filters.references) || !STATUSES.includes(route.filters.status) ||
          !REVIEWS.includes(route.filters.review)) throw new Error('Invalid filter');
    } catch (_) {
      return invalid('O endereço contém uma vista, ordenação ou filtro inválido. Nenhuma execução foi aberta.');
    }

    const scope = params.get('scope');
    // Check binding before parsing or resolving every source-dependent identity.
    // Generic text/status filters may survive, but source/experiment/project,
    // selected runs and detail must never migrate to a different positional ID.
    const versioned = params.get('v') === '1';
    if (!versioned || !scope || !/^[a-f0-9]{64}$/.test(scope) || !catalog?.snapshot_id || scope !== catalog.snapshot_id) {
      route.filters.source = '';
      route.filters.project = '';
      route.filters.experiment = '';
      return {route, warnings: [versioned && scope ?
        'Este link pertence a outra sessão ou snapshot. Execução, seleção e filtros de fonte foram descartados; escolha novamente no conjunto atual.' :
        'Este link não identifica a sessão e o snapshot. Execução, seleção e filtros de fonte foram descartados para evitar abrir outra entidade.'],
      rejected: true, reason: versioned && scope ? 'SNAPSHOT_MISMATCH' : 'UNBOUND_ROUTE'};
    }

    try {
      if (params.has('run')) route.detail = canonicalKey(params.get('run'));
      if (params.has('selected')) {
        const selected = JSON.parse(params.get('selected'));
        if (!Array.isArray(selected) || selected.length > 4) throw new Error('Invalid selection');
        route.selected = [...new Set(selected.map(canonicalKey))];
      }
      for (const field of ['project', 'experiment']) {
        if (route.filters[field]) route.filters[field] = canonicalKey(route.filters[field]);
      }
    } catch (_) {
      return invalid('Identidade ou seleção inválida no endereço. Nenhuma execução foi aberta.');
    }

    const warnings = [];
    let reason = null;
    const sources = new Set((catalog.sources || []).map(source => source.id));
    const projects = new Set(), experiments = new Set();
    for (const source of catalog.sources || []) {
      for (const project of source.read_model?.projects || []) projects.add(key(source.id, project.id));
      for (const experiment of source.read_model?.experiments || []) experiments.add(key(source.id, experiment.id));
    }
    for (const [field, values] of [['source', sources], ['project', projects], ['experiment', experiments]]) {
      if (route.filters[field] && !values.has(route.filters[field])) {
        route.filters[field] = '';
        reason = 'UNKNOWN_FILTER';
        warnings.push('Um filtro de fonte, projeto ou experimento não existe neste snapshot e foi removido.');
      }
    }
    const runs = new Set(flatten(catalog).map(run => run._key));
    if (route.detail && !runs.has(route.detail)) {
      route.detail = null;
      reason = 'UNKNOWN_RUN';
      warnings.push('A execução indicada não existe neste snapshot. O contexto de consulta foi preservado.');
    }
    const selected = route.selected.filter(item => runs.has(item));
    if (selected.length !== route.selected.length) {
      reason = reason || 'UNKNOWN_SELECTION';
      warnings.push('Execuções inexistentes foram removidas da seleção; nenhuma foi substituída.');
    }
    route.selected = selected;
    return {route, warnings, rejected: warnings.length > 0, reason};
  }

  function stringify(route, catalog) {
    const current = {...defaults(), ...route, filters: {...defaults().filters, ...route?.filters}};
    if (!catalog || typeof catalog.snapshot_id !== 'string' || !/^[a-f0-9]{64}$/.test(catalog.snapshot_id)) {
      throw new Error('A loaded session/snapshot is required before making a link.');
    }
    const params = new URLSearchParams({v: '1', scope: catalog.snapshot_id, view: current.view});
    if (current.detail) params.set('run', current.detail);
    if (current.selected?.length) params.set('selected', JSON.stringify(current.selected));
    const empty = defaults().filters;
    for (const [field, parameter] of Object.entries(FIELDS)) {
      if (current.filters[field] !== empty[field]) params.set(parameter, current.filters[field]);
    }
    return '#' + params.toString();
  }

  const api = Object.freeze({VIEWS, SORTS, PRESENCE, STATUSES, REVIEWS,
    defaults, key, flatten, filterRuns, sortRuns, parse, stringify});
  global.AtlasParity02State = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
})(typeof globalThis === 'object' ? globalThis : window);
