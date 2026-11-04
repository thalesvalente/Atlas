/**
 * Isolated candidate presentation component. This is not a persisted Caderno
 * schema, a carrier reader or an automatically activated Atlas feature.
 * Importing the module performs no DOM mutation, IO or event registration.
 */

export const TABLE_LIMITS = Object.freeze({
  rows: 1000, columns: 32, cells: 20000, text: 8192, totalText: 1000000,
  identifier: 256, label: 1024, unit: 128, numericText: 256,
  exponent: 1000, precision: 100,
});

const TYPES = new Set(["string", "integer", "decimal", "boolean"]);
const INTEGER = /^[+-]?\d+$/;
const DECIMAL = /^([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:[eE]([+-]?\d+))?$/;
const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
const pointer = (key) => String(key).replace(/~/g, "~0").replace(/\//g, "~1");
const isMissing = (row, key) => !own(row.cells, key) || row.cells[key] === null;

export class TableInputError extends Error {
  constructor(code, path, message) {
    super(`${code} at ${path}: ${message}`);
    this.name = "TableInputError";
    this.code = code;
    this.path = path;
  }
}

function fail(code, path, message) {
  throw new TableInputError(code, path, message);
}

// JSON-shaped data only. Accessors are refused before any property is read.
function record(value, path, keys) {
  if (value === null || typeof value !== "object" || Array.isArray(value)
      || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) {
    fail("INVALID_DESCRIPTOR", path, "Expected a plain data object.");
  }
  for (const key of Reflect.ownKeys(value)) {
    const property = Object.getOwnPropertyDescriptor(value, key);
    if (typeof key !== "string" || !own(property, "value") || !property.enumerable) {
      fail("INVALID_DESCRIPTOR", path, "Only enumerable data properties are supported.");
    }
    if (keys && !keys.includes(key)) fail("INVALID_DESCRIPTOR", `${path}/${pointer(key)}`, "Unknown field.");
  }
}

function array(value, path, limit) {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) fail("INVALID_DESCRIPTOR", path, "Expected a plain array.");
  if (value.length > limit) fail("LIMIT_EXCEEDED", path, `Maximum ${limit} items.`);
  if (Reflect.ownKeys(value).length !== value.length + 1) fail("INVALID_DESCRIPTOR", path, "Only array items and length are supported.");
  for (let index = 0; index < value.length; index += 1) {
    const property = Object.getOwnPropertyDescriptor(value, String(index));
    if (!property || !own(property, "value") || !property.enumerable) fail("INVALID_DESCRIPTOR", `${path}/${index}`, "Expected a data item.");
  }
}

function text(value, path, limit, empty = false) {
  if (typeof value !== "string" || (!empty && !value.trim())) fail("INVALID_VALUE", path, "Expected a string with a declared value.");
  if (value.length > limit) fail("LIMIT_EXCEEDED", path, `Maximum ${limit} UTF-16 code units.`);
  return value.length;
}

function validateColumn(column, path) {
  record(column, path, ["id", "label", "type", "unit", "precision"]);
  let length = text(column.id, `${path}/id`, TABLE_LIMITS.identifier);
  length += text(column.label, `${path}/label`, TABLE_LIMITS.label);
  if (!TYPES.has(column.type)) fail("INVALID_TYPE", `${path}/type`, "Unsupported column type.");
  const numeric = column.type === "integer" || column.type === "decimal";
  if (own(column, "unit")) {
    if (!numeric) fail("INVALID_TYPE", `${path}/unit`, "Units are supported only for numeric columns.");
    length += text(column.unit, `${path}/unit`, TABLE_LIMITS.unit);
  }
  if (own(column, "precision")) {
    if (!numeric || !Number.isInteger(column.precision) || column.precision < 0 || column.precision > TABLE_LIMITS.precision) {
      fail("INVALID_VALUE", `${path}/precision`, `Expected declared precision from 0 to ${TABLE_LIMITS.precision} on a numeric column.`);
    }
  }
  return length;
}

function numericText(value, type, path) {
  if (typeof value === "number") {
    if (!Number.isFinite(value)) fail("INVALID_VALUE", path, "Numeric values must be finite.");
    if (Number.isInteger(value) && !Number.isSafeInteger(value)) fail("UNSAFE_NUMBER", path, "Transport large integers as strings before JSON/JavaScript conversion.");
    if (type === "integer" && !Number.isInteger(value)) fail("INVALID_TYPE", path, "Expected an integer.");
    return Object.is(value, -0) ? "-0" : String(value);
  }
  if (typeof value !== "string") fail("INVALID_TYPE", path, "Expected a numeric string or a finite number.");
  if (value.length > TABLE_LIMITS.numericText) fail("LIMIT_EXCEEDED", path, `Maximum ${TABLE_LIMITS.numericText} characters in a numeric literal.`);
  if (value !== value.trim()) fail("INVALID_TYPE", path, "Numeric literals cannot contain surrounding whitespace.");
  if (type === "integer") {
    if (!INTEGER.test(value)) fail("INVALID_TYPE", path, "Expected an integer literal without whitespace.");
  } else {
    const match = DECIMAL.exec(value);
    if (!match) fail("INVALID_TYPE", path, "Expected a decimal literal without whitespace.");
    const exponent = Number(match[5] || "0");
    if (!Number.isSafeInteger(exponent) || Math.abs(exponent) > TABLE_LIMITS.exponent) fail("LIMIT_EXCEEDED", path, `Exponent magnitude cannot exceed ${TABLE_LIMITS.exponent}.`);
  }
  return value;
}

function validateValue(value, column, path) {
  if (value === null) return 0;
  if (column.type === "string") return text(value, path, TABLE_LIMITS.text, true);
  if (column.type === "boolean") {
    if (typeof value !== "boolean") fail("INVALID_TYPE", path, "Expected a boolean, not a string or number.");
    return String(value).length;
  }
  return numericText(value, column.type, path).length;
}

/** Validate without copying, coercing, freezing or modifying the caller's data. */
export function validateTable(descriptor) {
  record(descriptor, "", ["version", "semantic_status", "synthetic", "title", "description", "columns", "rows"]);
  if (descriptor.version !== "p03-table/1") fail("UNSUPPORTED_VERSION", "/version", "Expected p03-table/1.");
  if (descriptor.semantic_status !== "CANDIDATE_PRESENTATION") fail("UNSUPPORTED_SEMANTICS", "/semantic_status", "This descriptor defines candidate presentation only.");
  if (own(descriptor, "synthetic") && typeof descriptor.synthetic !== "boolean") fail("INVALID_TYPE", "/synthetic", "Expected a declared boolean.");
  let length = text(descriptor.title, "/title", TABLE_LIMITS.label);
  if (own(descriptor, "description")) length += text(descriptor.description, "/description", TABLE_LIMITS.text, true);
  array(descriptor.columns, "/columns", TABLE_LIMITS.columns);
  array(descriptor.rows, "/rows", TABLE_LIMITS.rows);
  if (!descriptor.columns.length) fail("INVALID_DESCRIPTOR", "/columns", "Declare at least one column, even for an empty table.");
  if (descriptor.columns.length * descriptor.rows.length > TABLE_LIMITS.cells) fail("LIMIT_EXCEEDED", "/rows", `Maximum ${TABLE_LIMITS.cells} declared data cells.`);
  const columns = new Map();
  descriptor.columns.forEach((column, index) => {
    length += validateColumn(column, `/columns/${index}`);
    if (columns.has(column.id)) fail("DUPLICATE_ID", `/columns/${index}/id`, "Column identity must be unique within the descriptor.");
    columns.set(column.id, column);
  });
  const rows = new Set();
  descriptor.rows.forEach((row, index) => {
    const path = `/rows/${index}`;
    record(row, path, ["id", "cells", "missing_reasons"]);
    length += text(row.id, `${path}/id`, TABLE_LIMITS.identifier);
    if (rows.has(row.id)) fail("DUPLICATE_ID", `${path}/id`, "Row identity must be unique within the descriptor.");
    rows.add(row.id);
    record(row.cells, `${path}/cells`);
    for (const key of Object.keys(row.cells)) {
      if (!columns.has(key)) fail("UNKNOWN_COLUMN", `${path}/cells/${pointer(key)}`, "Cell has no declared column.");
      length += validateValue(row.cells[key], columns.get(key), `${path}/cells/${pointer(key)}`);
    }
    if (own(row, "missing_reasons")) {
      record(row.missing_reasons, `${path}/missing_reasons`);
      for (const key of Object.keys(row.missing_reasons)) {
        if (!columns.has(key)) fail("UNKNOWN_COLUMN", `${path}/missing_reasons/${pointer(key)}`, "Missing reason has no declared column.");
        if (!isMissing(row, key)) fail("INVALID_VALUE", `${path}/missing_reasons/${pointer(key)}`, "A present value cannot have a missing reason.");
        length += text(row.missing_reasons[key], `${path}/missing_reasons/${pointer(key)}`, TABLE_LIMITS.label);
      }
    }
    if (length > TABLE_LIMITS.totalText) fail("LIMIT_EXCEEDED", path, `Maximum ${TABLE_LIMITS.totalText} total UTF-16 code units.`);
  });
  if (length > TABLE_LIMITS.totalText) fail("LIMIT_EXCEEDED", "", `Maximum ${TABLE_LIMITS.totalText} total UTF-16 code units.`);
  return descriptor;
}

/** Precision remains metadata. Numeric strings are returned verbatim. */
export function formatCell(value, column, missingReason) {
  validateColumn(column, "/column");
  if (missingReason !== undefined) text(missingReason, "/missingReason", TABLE_LIMITS.label);
  if (value === undefined || value === null) return missingReason === undefined ? "Não informado" : `Não informado — ${missingReason}`;
  if (missingReason !== undefined) fail("INVALID_VALUE", "/missingReason", "A present value cannot have a missing reason.");
  validateValue(value, column, "/value");
  return typeof value === "number" && Object.is(value, -0) ? "-0" : String(value);
}

// Values never pass through Number for comparison. Number is used only for the
// bounded exponent, after validating the lexical form and exponent limit.
function numericKey(value) {
  const lexical = typeof value === "number" && Object.is(value, -0) ? "-0" : String(value);
  const match = DECIMAL.exec(lexical);
  const fraction = match[3] ?? match[4] ?? "";
  const digits = `${match[2] || "0"}${fraction}`;
  const coefficient = BigInt(`${match[1] === "-" ? "-" : ""}${digits}`);
  return { coefficient, exponent: coefficient === 0n ? 0 : Number(match[5] || "0") - fraction.length };
}

function keyFor(value, column) {
  return column.type === "integer" || column.type === "decimal" ? numericKey(value) : value;
}

function compare(a, b, column) {
  if (column.type === "integer" || column.type === "decimal") {
    const exponent = Math.min(a.exponent, b.exponent);
    const left = a.coefficient * 10n ** BigInt(a.exponent - exponent);
    const right = b.coefficient * 10n ** BigInt(b.exponent - exponent);
    return left < right ? -1 : left > right ? 1 : 0;
  }
  // Deterministic UTF-16 lexical string order; boolean false precedes true.
  return a < b ? -1 : a > b ? 1 : 0;
}

function findColumn(descriptor, columnId, path) {
  if (typeof columnId !== "string") fail("INVALID_OPTION", path, "Expected a column identity.");
  const column = descriptor.columns.find((item) => item.id === columnId);
  if (!column) fail("UNKNOWN_COLUMN", path, "Column is not declared in this descriptor.");
  return column;
}

function orderedRows(rows, column, direction) {
  if (direction !== "asc" && direction !== "desc") fail("INVALID_OPTION", "/sort/direction", "Expected asc or desc.");
  return rows.map((row, index) => ({ row, index, missing: isMissing(row, column.id),
    key: isMissing(row, column.id) ? null : keyFor(row.cells[column.id], column) }))
    .sort((a, b) => {
      if (a.missing !== b.missing) return a.missing ? 1 : -1;
      const order = a.missing ? 0 : compare(a.key, b.key, column);
      return (direction === "asc" ? order : -order) || a.index - b.index;
    }).map((item) => item.row);
}

/** Stable typed order, always putting missing values last. Row objects persist. */
export function sortRows(descriptor, columnId, direction = "asc") {
  validateTable(descriptor);
  return orderedRows(descriptor.rows, findColumn(descriptor, columnId, "/sort/columnId"), direction);
}

function filterPredicate(descriptor, filter) {
  record(filter, "/filter", ["columnId", "operator", "value"]);
  const column = findColumn(descriptor, filter.columnId, "/filter/columnId");
  const operator = filter.operator ?? "eq";
  if (operator === "is_missing" || operator === "is_present") {
    if (own(filter, "value")) fail("INVALID_OPTION", "/filter/value", "Missing-state filters do not accept a value.");
    return (row) => isMissing(row, column.id) === (operator === "is_missing");
  }
  if (!["eq", "contains", "lt", "lte", "gt", "gte"].includes(operator)) fail("INVALID_OPTION", "/filter/operator", "Unsupported filter operator.");
  if ((operator === "contains" && column.type !== "string")
      || (["lt", "lte", "gt", "gte"].includes(operator) && !["integer", "decimal"].includes(column.type))) {
    fail("INCOMPATIBLE_FILTER", "/filter/operator", "Operator is incompatible with the declared type.");
  }
  if (!own(filter, "value") || filter.value === null) fail("INVALID_OPTION", "/filter/value", "Declare a typed value; use is_missing for absence.");
  validateValue(filter.value, column, "/filter/value");
  const target = keyFor(filter.value, column);
  return (row) => {
    if (isMissing(row, column.id)) return false;
    const value = row.cells[column.id];
    if (operator === "contains") return value.includes(filter.value);
    const order = compare(keyFor(value, column), target, column);
    return ({ eq: order === 0, lt: order < 0, lte: order <= 0, gt: order > 0, gte: order >= 0 })[operator];
  };
}

/** Type-aware filter returning original row objects, without changing sources. */
export function filterRows(descriptor, filter) {
  validateTable(descriptor);
  return descriptor.rows.filter(filterPredicate(descriptor, filter));
}

function cellText(row, column) {
  if (isMissing(row, column.id)) return row.missing_reasons && own(row.missing_reasons, column.id)
    ? `Não informado — ${row.missing_reasons[column.id]}` : "Não informado";
  const value = row.cells[column.id];
  return typeof value === "number" && Object.is(value, -0) ? "-0" : String(value);
}

/** Return a detached semantic table region; the caller controls attachment. */
export function renderTable(document, descriptor, options = {}) {
  validateTable(descriptor);
  record(options, "/options", ["filter", "sort"]);
  let rows = descriptor.rows;
  if (own(options, "filter")) rows = rows.filter(filterPredicate(descriptor, options.filter));
  if (own(options, "sort")) {
    record(options.sort, "/sort", ["columnId", "direction"]);
    rows = orderedRows(rows, findColumn(descriptor, options.sort.columnId, "/sort/columnId"), options.sort.direction ?? "asc");
  }
  if (!document || typeof document.createElement !== "function") fail("INVALID_DOCUMENT", "/document", "Supply a DOM Document explicitly.");
  const element = (name, className, value) => {
    const node = document.createElement(name);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  };
  const component = element("section", "atlas-p03-table");
  component.setAttribute("data-component", "parity02-p03-table");
  component.append(element("p", "atlas-p03-table__status", `Apresentação candidata${descriptor.synthetic === true ? " · Dados sintéticos" : ""}`));
  if (descriptor.description) component.append(element("p", "atlas-p03-table__description", descriptor.description));
  component.append(element("p", "atlas-p03-table__summary", `${rows.length} linhas apresentadas de ${descriptor.rows.length} declaradas. Precisão é metadado; valores não são arredondados.`));
  const scroll = element("div", "atlas-p03-table__scroll");
  scroll.setAttribute("role", "region");
  scroll.setAttribute("aria-label", `Tabela: ${descriptor.title}. Área com rolagem horizontal quando necessária.`);
  scroll.setAttribute("tabindex", "0");
  const table = element("table", "atlas-p03-table__grid");
  table.append(element("caption", "atlas-p03-table__caption", descriptor.title));
  const thead = element("thead");
  const headRow = element("tr");
  const identity = element("th", "atlas-p03-table__identity", "Identidade da linha");
  identity.setAttribute("scope", "col");
  headRow.append(identity);
  for (const column of descriptor.columns) {
    const header = element("th");
    header.setAttribute("scope", "col");
    if (options.sort?.columnId === column.id) header.setAttribute("aria-sort", options.sort.direction === "desc" ? "descending" : "ascending");
    header.append(element("span", "atlas-p03-table__heading", column.label));
    const metadata = [`Tipo: ${column.type}`];
    if (column.type === "integer" || column.type === "decimal") metadata.push(`Unidade: ${column.unit ?? "não declarada"}`);
    if (own(column, "precision")) metadata.push(`Precisão declarada: ${column.precision} casas decimais`);
    header.append(element("span", "atlas-p03-table__metadata", metadata.join(" · ")));
    headRow.append(header);
  }
  thead.append(headRow);
  table.append(thead);
  const tbody = element("tbody");
  for (const row of rows) {
    const tr = element("tr");
    tr.setAttribute("data-row-id", row.id);
    const rowHeader = element("th", "atlas-p03-table__identity", row.id);
    rowHeader.setAttribute("scope", "row");
    tr.append(rowHeader);
    for (const column of descriptor.columns) tr.append(element("td", isMissing(row, column.id) ? "atlas-p03-table__missing" : "", cellText(row, column)));
    tbody.append(tr);
  }
  if (!rows.length) {
    const tr = element("tr");
    const empty = element("td", "atlas-p03-table__empty", descriptor.rows.length ? "Nenhuma linha corresponde ao filtro." : "Nenhuma linha declarada.");
    empty.setAttribute("colspan", String(descriptor.columns.length + 1));
    tr.append(empty);
    tbody.append(tr);
  }
  table.append(tbody);
  scroll.append(table);
  component.append(scroll);
  return component;
}
