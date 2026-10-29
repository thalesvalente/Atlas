/* Explicit P03 embedding over the validated, disposable C1 read model. */
import {MetadataError, renderMetadata} from './parity02_p03_artifacts.js';
import {TableInputError, renderTable, validateTable} from './parity02_p03_table.js';

const categories = [['metrics', 'Métricas'], ['parameters', 'Parâmetros']];
const element = (doc, tag, text, className) => {
  const node = doc.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

export const propertyChoiceKey = (category, id) => JSON.stringify([category, id]);
export const p03ContextKey = (catalog, source, run) => JSON.stringify([
  catalog.snapshot_id, source.id, source.snapshot_id, run.id,
]);

function declaredRun(source, run) {
  const result = source?.read_model?.runs?.find(item => item.id === run?.id);
  if (!result || typeof source.id !== 'string' || typeof source.snapshot_id !== 'string') {
    throw new TableInputError('SOURCE_MISMATCH', '/run', 'Select a run from this validated source and snapshot.');
  }
  return result;
}

function choicesFor(run) {
  const choices = [], seen = new Set();
  for (const [category, label] of categories) {
    for (const property of run[category] || []) {
      const key = propertyChoiceKey(category, property.id);
      if (seen.has(key)) throw new TableInputError('DUPLICATE_ID', '/properties', 'Property identity repeats in this category.');
      seen.add(key);
      choices.push({category, label, property, key});
    }
  }
  return choices;
}

function transportedValue(property) {
  if (property.value === null || property.value === undefined) return null;
  // display_value is lexical text for numbers/strings, never a boolean parser.
  if (property.type === 'boolean') return property.value;
  if (typeof property.display_value === 'string') return property.display_value;
  if (typeof property.value === 'string') return property.value;
  throw new TableInputError('INVALID_VALUE', '/display_value', 'Exact presentation text is required before JSON transport.');
}

/** Build only explicitly selected PropertyValues; no persisted table is inferred. */
export function buildPropertyTables(source, selectedRun, selection) {
  const run = declaredRun(source, selectedRun);
  const choices = choicesFor(run), available = new Set(choices.map(choice => choice.key));
  for (const key of selection) {
    if (!available.has(key)) throw new TableInputError('UNKNOWN_PROPERTY', '/selection', 'Selection belongs to another run or snapshot.');
  }
  const groups = new Map();
  for (const choice of choices) {
    if (!selection.has(choice.key)) continue;
    const property = choice.property;
    const type = property.type === 'number' ? 'decimal' : property.type;
    const unit = property.unit ?? null;
    // Category, declared type and exact unit stay separate, with no conversion.
    const groupKey = JSON.stringify([choice.category, property.type, unit]);
    if (!groups.has(groupKey)) {
      const valueColumn = {id: 'value', label: 'Valor declarado', type};
      if (unit !== null && ['integer', 'decimal'].includes(type)) valueColumn.unit = unit;
      groups.set(groupKey, {
        version: 'p03-table/1', semantic_status: 'CANDIDATE_PRESENTATION',
        synthetic: run.synthetic === true,
        title: choice.label + ' por seleção · ' + property.type + ' · ' + (unit ?? 'unidade não declarada'),
        description: 'Seleção derivada sem conversão. Contexto: ' + JSON.stringify({
          source_id: source.id, snapshot_id: source.snapshot_id, entity_id: run.id,
        }),
        columns: [
          {id: 'name', label: 'Propriedade declarada', type: 'string'},
          {id: 'property_id', label: 'Identidade da propriedade', type: 'string'},
          valueColumn,
          {id: 'declared_type', label: 'Tipo declarado', type: 'string'},
          {id: 'unit', label: 'Unidade declarada', type: 'string'},
          {id: 'precision', label: 'Precisão declarada (texto exato)', type: 'string'},
        ],
        rows: [],
      });
    }
    const precision = property.precision == null ? null : property.display_precision;
    if (precision !== null && typeof precision !== 'string') {
      throw new TableInputError('INVALID_VALUE', '/display_precision', 'Exact declared precision text is required.');
    }
    const cells = {
      name: property.name, property_id: property.property_id ?? property.id,
      value: transportedValue(property), declared_type: property.type, unit, precision,
    };
    const missing_reasons = {};
    if (cells.value === null) missing_reasons.value = property.missing_reason || 'Valor não declarado.';
    if (unit === null) missing_reasons.unit = 'Unidade não declarada.';
    if (precision === null) missing_reasons.precision = 'Precisão não declarada.';
    groups.get(groupKey).rows.push({id: property.id, cells, missing_reasons});
  }
  const descriptors = [...groups.values()];
  descriptors.forEach(validateTable);
  return descriptors;
}

function presentationError(doc, error) {
  const node = element(doc, 'p', 'Falha de apresentação: ' + error.code + ' (' + error.path + '). Consulte os registros e a validação da fonte.', 'atlas-p03-presentation-error');
  node.dataset.testid = 'p03-presentation-error';
  node.setAttribute('role', 'status');
  return node;
}

/** Metadata stays independently fallible; no report or source is rewritten. */
export function renderP03Metadata(doc, source, run = null) {
  const wrapper = element(doc, 'section', undefined, 'atlas-p03-embedding');
  wrapper.dataset.testid = 'p03-metadata';
  wrapper.dataset.sourceId = source.id;
  wrapper.dataset.snapshotId = source.snapshot_id;
  wrapper.append(element(doc, 'p', 'Snapshot do pacote: ' + source.snapshot_id, 'atlas-p03-context'));
  for (const error of source.presentation?.errors || []) wrapper.append(presentationError(doc, error));
  const descriptor = source.presentation?.metadata;
  if (!descriptor) {
    if (!source.presentation?.errors?.length) wrapper.append(element(doc, 'p', 'Metadados indisponíveis: esta fonte não possui registros validados para apresentação.'));
    return wrapper;
  }
  try {
    if (descriptor.source.key !== JSON.stringify([source.id, source.snapshot_id])) throw new MetadataError('SOURCE_MISMATCH', 'source.key');
    let selected = descriptor;
    if (run) {
      const ids = new Set([run.id, ...(run.inputs || []), ...(run.outputs || []), ...(run.related_references || []).map(item => item.id)]);
      selected = {...descriptor, items: descriptor.items.filter(item => ids.has(item.identity.id))};
    }
    wrapper.append(renderMetadata(doc, selected));
  } catch (error) {
    if (!(error instanceof MetadataError)) throw error;
    wrapper.append(presentationError(doc, error));
  }
  return wrapper;
}

/** Detached subtree: listeners belong only to its own controls and disappear on removal. */
export function renderPropertySelection(doc, source, selectedRun, selection) {
  const section = element(doc, 'section', undefined, 'atlas-p03-picker atlas-p03-embedding');
  section.dataset.testid = 'p03-property-selection';
  section.dataset.sourceId = source.id;
  section.dataset.snapshotId = source.snapshot_id;
  section.dataset.entityId = selectedRun.id;
  section.append(element(doc, 'h3', 'Tabela derivada por seleção'), element(doc, 'p', 'Escolha métricas e parâmetros desta execução. Tipos e unidades distintos permanecem em tabelas separadas; precisão é texto declarado.'));
  const output = element(doc, 'div');
  output.dataset.testid = 'p03-derived-tables';
  output.setAttribute('aria-live', 'polite');
  const update = () => {
    output.replaceChildren();
    try {
      const descriptors = buildPropertyTables(source, selectedRun, selection);
      if (!descriptors.length) output.append(element(doc, 'p', 'Nenhuma propriedade selecionada.'));
      for (const descriptor of descriptors) {
        const table = renderTable(doc, descriptor);
        table.dataset.sourceId = source.id;
        table.dataset.snapshotId = source.snapshot_id;
        table.dataset.entityId = selectedRun.id;
        output.append(table);
      }
    } catch (error) {
      if (!(error instanceof TableInputError)) throw error;
      output.append(presentationError(doc, error));
    }
  };
  try {
    const choices = choicesFor(declaredRun(source, selectedRun));
    const fieldset = element(doc, 'fieldset');
    fieldset.append(element(doc, 'legend', 'Propriedades para a tabela derivada'));
    if (!choices.length) fieldset.append(element(doc, 'p', 'Nenhuma métrica ou parâmetro declarado.'));
    for (const choice of choices) {
      const label = element(doc, 'label', undefined, 'atlas-p03-picker__option');
      const control = element(doc, 'input');
      control.type = 'checkbox';
      control.checked = selection.has(choice.key);
      control.dataset.p03PropertyKey = choice.key;
      control.dataset.propertyKind = choice.category;
      control.dataset.propertyId = choice.property.id;
      control.addEventListener('change', () => {
        if (control.checked) selection.add(choice.key); else selection.delete(choice.key);
        update();
      });
      label.append(control, element(doc, 'span', choice.label + ' · ' + choice.property.name + ' · ' + choice.property.id));
      fieldset.append(label);
    }
    section.append(fieldset);
    update();
  } catch (error) {
    if (!(error instanceof TableInputError)) throw error;
    output.append(presentationError(doc, error));
  }
  section.append(output);
  return section;
}
