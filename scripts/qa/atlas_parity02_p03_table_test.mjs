/** Pure Node behavioral tests. These results do not claim a browser run. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import test from "node:test";
import {
  TABLE_LIMITS, TableInputError, validateTable, formatCell,
  sortRows, filterRows, renderTable,
} from "../../packages/atlas/src/atlas_viewer/static/parity02_p03_table.js";

const fixture = (name) => JSON.parse(readFileSync(new URL(`../../tests/fixtures/atlas_parity02/p03/${name}`, import.meta.url), "utf8"));
const positive = fixture("table-positive.json");
const column = (type, metadata = {}) => ({ id: "v", label: "Valor", type, ...metadata });
const table = (type, values, metadata = {}) => ({
  version: "p03-table/1", semantic_status: "CANDIDATE_PRESENTATION", synthetic: true,
  title: "Ensaio sintético", columns: [column(type, metadata)],
  rows: values.map((value, index) => ({ id: `row-${index}`, cells: value === undefined ? {} : { v: value } })),
});
const ids = (rows) => rows.map((row) => row.id);
const clone = (value) => structuredClone(value);
const rejects = (fn, code, path) => assert.throws(fn, (error) => {
  assert.ok(error instanceof TableInputError, `Unexpected error: ${error}`);
  assert.equal(error.code, code);
  if (path !== undefined) assert.equal(error.path, path);
  return true;
});
function freeze(value) {
  if (value && typeof value === "object") {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}

test("positive fixture retains lexical values, Unicode, missing values and metadata", () => {
  assert.strictEqual(validateTable(positive), positive);
  assert.equal(formatCell(positive.rows[0].cells.count, positive.columns[1]), "9007199254740993");
  assert.equal(formatCell(positive.rows[1].cells.count, positive.columns[1]), "09007199254740992");
  assert.equal(formatCell(positive.rows[0].cells.measure, positive.columns[2]), "0.123456789012345678901");
  assert.equal(formatCell(positive.rows[1].cells.measure, positive.columns[2]), "+001.2300e+2");
  assert.equal(formatCell(positive.rows[0].cells.code, positive.columns[4]), "00042");
  assert.equal(formatCell(positive.rows[0].cells.sample, positive.columns[0]), "São Luís / 水 / 🌱");
  assert.equal(positive.columns[2].precision, 2);
});

test("declared precision never rounds values or adds decimal places", () => {
  assert.equal(formatCell("1.234567890123456789", column("decimal", { precision: 2 })), "1.234567890123456789");
  assert.equal(formatCell("1", column("decimal", { precision: 8 })), "1");
  assert.equal(formatCell("0007", column("integer", { precision: 0 })), "0007");
});

test("missing values remain distinct from zero, empty string and false", () => {
  assert.equal(formatCell(null, column("integer")), "Não informado");
  assert.equal(formatCell(undefined, column("decimal"), "Não medido"), "Não informado — Não medido");
  assert.equal(formatCell(0, column("integer")), "0");
  assert.equal(formatCell(false, column("boolean")), "false");
  assert.equal(formatCell("", column("string")), "");
  assert.equal(formatCell(-0, column("decimal")), "-0");
  assert.equal(formatCell("-0.000", column("decimal")), "-0.000");
});

test("unsafe native integers fail before formatting and cannot be recovered by coercion", () => {
  for (const type of ["integer", "decimal"]) {
    rejects(() => validateTable(table(type, [9007199254740992])), "UNSAFE_NUMBER", "/rows/0/cells/v");
    rejects(() => formatCell(9007199254740992, column(type)), "UNSAFE_NUMBER", "/value");
    assert.equal(formatCell("9007199254740993", column(type)), "9007199254740993");
  }
});

test("nonfinite, boolean-as-number and incompatible scalar inputs fail explicitly", () => {
  for (const value of [NaN, Infinity, -Infinity]) rejects(() => validateTable(table("decimal", [value])), "INVALID_VALUE");
  for (const value of [true, {}, [], 2n, undefined]) {
    if (value === undefined) continue; // An omitted key is deliberately a missing value.
    rejects(() => validateTable(table("decimal", [value])), "INVALID_TYPE");
  }
  for (const value of ["true", 1, 0]) rejects(() => validateTable(table("boolean", [value])), "INVALID_TYPE");
  rejects(() => validateTable(table("integer", [1.2])), "INVALID_TYPE");
  rejects(() => validateTable(table("string", [1])), "INVALID_VALUE");
  const explicitUndefined = table("integer", []);
  explicitUndefined.rows = [{ id: "row", cells: { v: undefined } }];
  rejects(() => validateTable(explicitUndefined), "INVALID_TYPE");
});

test("numeric strings with whitespace, hex, infinity or comma separators are refused", () => {
  for (const value of [" 1", "1 ", "\n1", "1\n", "1\r", "1\u2028", "1\u2029", "0x10", "NaN", "Infinity", "1,2", "1_000", "", "١٢"]) {
    rejects(() => validateTable(table("decimal", [value])), "INVALID_TYPE");
  }
  rejects(() => validateTable(table("integer", ["1e2"])), "INVALID_TYPE");
  rejects(() => validateTable(table("integer", ["1.0"])), "INVALID_TYPE");
});

test("integer sorting is exact beyond Number precision and keeps lexical identity", () => {
  const data = table("integer", ["9007199254740993", "9007199254740992", "-9007199254740993", "09007199254740992"]);
  const sorted = sortRows(data, "v");
  assert.deepEqual(ids(sorted), ["row-2", "row-1", "row-3", "row-0"]);
  assert.strictEqual(sorted[2], data.rows[3]);
  assert.equal(sorted[2].cells.v, "09007199254740992");
});

test("decimal sorting is exact for near neighbors, exponents, leading zeros and negatives", () => {
  const data = table("decimal", ["0.123456789012345678902", "0.123456789012345678901", "1e-1000", "-1e1000", "+001.2300e+2", "123", "-0.000"]);
  assert.deepEqual(ids(sortRows(data, "v")), ["row-3", "row-6", "row-2", "row-1", "row-0", "row-4", "row-5"]);
  assert.deepEqual(ids(sortRows(data, "v", "desc")), ["row-4", "row-5", "row-0", "row-1", "row-2", "row-6", "row-3"]);
});

test("missing values sort last in both directions with stable ties and row identities", () => {
  const data = table("decimal", [null, "1.0", undefined, "01", "-1"]);
  assert.deepEqual(ids(sortRows(data, "v")), ["row-4", "row-1", "row-3", "row-0", "row-2"]);
  assert.deepEqual(ids(sortRows(data, "v", "desc")), ["row-1", "row-3", "row-4", "row-0", "row-2"]);
});

test("string numeric-looking codes are sorted as text and booleans are typed", () => {
  assert.deepEqual(ids(sortRows(table("string", ["2", "10", "001", "Á", "A"]), "v")), ["row-2", "row-1", "row-0", "row-4", "row-3"]);
  assert.deepEqual(ids(sortRows(table("boolean", [true, false, null, false]), "v")), ["row-1", "row-3", "row-0", "row-2"]);
});

test("numeric filters distinguish exact neighbors and do not turn absence into zero", () => {
  const data = table("decimal", ["0.123456789012345678901", "0.123456789012345678902", null, "0"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "gt", value: "0.123456789012345678901" })), ["row-1"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "eq", value: 0 })), ["row-3"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "lte", value: "0.123456789012345678901" })), ["row-0", "row-3"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "lt", value: "0" })), []);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "gte", value: "0.123456789012345678902" })), ["row-1"]);
});

test("text filters preserve Unicode and codes, and missing filters preserve row identity", () => {
  const data = table("string", ["0007", "7", "água 水", null, undefined]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", value: "7" })), ["row-1"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "contains", value: "水" })), ["row-2"]);
  assert.deepEqual(ids(filterRows(data, { columnId: "v", operator: "is_missing" })), ["row-3", "row-4"]);
  const present = filterRows(data, { columnId: "v", operator: "is_present" });
  assert.deepEqual(ids(present), ["row-0", "row-1", "row-2"]);
  assert.strictEqual(present[2], data.rows[2]);
});

test("filter operators and values cannot silently change types or units", () => {
  rejects(() => filterRows(table("integer", [1]), { columnId: "v", operator: "contains", value: "1" }), "INCOMPATIBLE_FILTER");
  rejects(() => filterRows(table("string", ["1"]), { columnId: "v", operator: "gt", value: "0" }), "INCOMPATIBLE_FILTER");
  rejects(() => filterRows(table("boolean", [true]), { columnId: "v", value: "true" }), "INVALID_TYPE");
  rejects(() => filterRows(table("integer", [1]), { columnId: "v", value: null }), "INVALID_OPTION");
  rejects(() => filterRows(table("integer", [1]), { columnId: "v", operator: "is_missing", value: 0 }), "INVALID_OPTION");
  rejects(() => filterRows(table("integer", [1]), { columnId: "v", operator: "regex", value: "1" }), "INVALID_OPTION");
  rejects(() => filterRows(table("decimal", [1], { unit: "mg/L" }), { columnId: "v", value: 1, unit: "g/L" }), "INVALID_DESCRIPTOR");
});

test("unknown columns and invalid sort directions fail predictably", () => {
  rejects(() => sortRows(positive, "missing"), "UNKNOWN_COLUMN", "/sort/columnId");
  rejects(() => sortRows(positive, "count", "random"), "INVALID_OPTION", "/sort/direction");
  rejects(() => filterRows(positive, { columnId: "missing", value: "x" }), "UNKNOWN_COLUMN", "/filter/columnId");
});

test("validation, formatting, sorting and filtering accept deep-frozen sources unchanged", () => {
  const data = freeze(clone(positive));
  const before = JSON.stringify(data);
  validateTable(data);
  sortRows(data, "count");
  filterRows(data, { columnId: "count", operator: "gte", value: 0 });
  formatCell(data.rows[0].cells.measure, data.columns[2]);
  assert.equal(JSON.stringify(data), before);
});

test("empty descriptor remains empty and supports nonmutating views", () => {
  const data = fixture("table-empty.json");
  assert.equal(validateTable(data).rows.length, 0);
  assert.deepEqual(sortRows(data, "count"), []);
  assert.deepEqual(filterRows(data, { columnId: "count", operator: "is_present" }), []);
});

test("malicious HTML and URI strings are preserved as inert scalar data", () => {
  const data = fixture("table-malicious.json");
  validateTable(data);
  for (const row of data.rows) for (const col of data.columns) assert.equal(formatCell(row.cells[col.id], col), row.cells[col.id]);
  assert.equal(globalThis.__p03_xss, undefined);
});

for (const item of fixture("table-invalid.json").cases) {
  test(`negative fixture: ${item.name}`, () => rejects(() => validateTable(item.descriptor), item.expected_code));
}

test("missing reasons cannot overwrite present values or name unknown columns", () => {
  const present = table("integer", [1]);
  present.rows[0].missing_reasons = { v: "Ausente" };
  rejects(() => validateTable(present), "INVALID_VALUE");
  const missing = table("integer", [null]);
  missing.rows[0].missing_reasons = { unknown: "Ausente" };
  rejects(() => validateTable(missing), "UNKNOWN_COLUMN");
  missing.rows[0].missing_reasons = { v: "" };
  rejects(() => validateTable(missing), "INVALID_VALUE");
});

test("duplicate columns, undeclared cells and unsupported metadata cannot be dropped", () => {
  const duplicate = table("string", ["text"]);
  duplicate.columns.push({ ...duplicate.columns[0] });
  rejects(() => validateTable(duplicate), "DUPLICATE_ID");
  const unknown = table("string", ["text"]);
  unknown.rows[0].cells.other = "unrepresented";
  rejects(() => validateTable(unknown), "UNKNOWN_COLUMN");
  rejects(() => validateTable(table("string", ["x"], { unit: "mg/L" })), "INVALID_TYPE");
  rejects(() => validateTable(table("boolean", [true], { precision: 2 })), "INVALID_VALUE");
});

test("accessors, array hooks and non-data objects are refused without invoking them", () => {
  let called = 0;
  const accessor = table("string", ["x"]);
  Object.defineProperty(accessor.rows[0].cells, "v", { enumerable: true, get() { called += 1; return "changed"; } });
  rejects(() => validateTable(accessor), "INVALID_DESCRIPTOR");
  const arrayHook = table("string", ["x"]);
  arrayHook.rows.forEach = () => { called += 1; };
  rejects(() => validateTable(arrayHook), "INVALID_DESCRIPTOR");
  const sparse = table("string", ["x"]);
  delete sparse.rows[0];
  rejects(() => validateTable(sparse), "INVALID_DESCRIPTOR");
  rejects(() => validateTable(new Date()), "INVALID_DESCRIPTOR");
  assert.equal(called, 0);
});

test("prototype-looking column identities remain ordinary data keys", () => {
  const data = table("string", []);
  data.columns[0].id = "__proto__";
  data.rows = [{ id: "constructor", cells: JSON.parse('{"__proto__":"safe value"}') }];
  validateTable(data);
  assert.deepEqual(ids(filterRows(data, { columnId: "__proto__", value: "safe value" })), ["constructor"]);
  assert.equal({}.polluted, undefined);
});

test("large table at the row and cell limits validates and keeps all identities", () => {
  const data = table("integer", []);
  data.columns = Array.from({ length: 20 }, (_, i) => ({ id: `c${i}`, label: `C${i}`, type: "integer", unit: "1" }));
  data.rows = Array.from({ length: 1000 }, (_, i) => ({ id: `r${i}`, cells: Object.fromEntries(data.columns.map((c) => [c.id, 1000 - i])) }));
  assert.equal(validateTable(data).rows.length, 1000);
  assert.equal(data.rows.length * data.columns.length, 20000);
  assert.equal(sortRows(data, "c0")[0].id, "r999");
  assert.equal(filterRows(data, { columnId: "c19", value: 500 })[0].id, "r500");
});

const limitCases = [
  ["rows", () => table("string", Array.from({ length: TABLE_LIMITS.rows + 1 }, () => "x"))],
  ["columns", () => ({ ...table("string", []), columns: Array.from({ length: TABLE_LIMITS.columns + 1 }, (_, i) => ({ id: String(i), label: "c", type: "string" })) })],
  ["cells", () => ({ ...table("string", Array.from({ length: TABLE_LIMITS.rows }, () => "x")), columns: Array.from({ length: 21 }, (_, i) => ({ id: String(i), label: "c", type: "string" })) })],
  ["text", () => table("string", ["x".repeat(TABLE_LIMITS.text + 1)])],
  ["totalText", () => table("string", Array.from({ length: 123 }, () => "x".repeat(TABLE_LIMITS.text)))],
  ["identifier", () => { const d = table("string", ["x"]); d.rows[0].id = "r".repeat(TABLE_LIMITS.identifier + 1); return d; }],
  ["label", () => ({ ...table("string", ["x"]), title: "t".repeat(TABLE_LIMITS.label + 1) })],
  ["unit", () => table("decimal", ["1"], { unit: "u".repeat(TABLE_LIMITS.unit + 1) })],
  ["numericText", () => table("integer", ["1".repeat(TABLE_LIMITS.numericText + 1)])],
  ["exponent", () => table("decimal", ["1e1001"])],
];
for (const [name, make] of limitCases) test(`limit: ${name}`, () => rejects(() => validateTable(make()), "LIMIT_EXCEEDED"));

test("declared precision has bounded integer values", () => {
  validateTable(table("decimal", ["1.234"], { precision: TABLE_LIMITS.precision }));
  for (const precision of [-1, 1.5, TABLE_LIMITS.precision + 1]) rejects(() => validateTable(table("decimal", ["1"], { precision })), "INVALID_VALUE");
});

test("individual textual and numeric boundaries are accepted without truncation", () => {
  const data = table("string", ["水".repeat(TABLE_LIMITS.text)]);
  data.title = "t".repeat(TABLE_LIMITS.label);
  data.rows[0].id = "r".repeat(TABLE_LIMITS.identifier);
  assert.strictEqual(validateTable(data), data);
  validateTable(table("decimal", ["1e1000", "1e-1000"], { unit: "u".repeat(TABLE_LIMITS.unit) }));
  assert.equal(formatCell("1".repeat(TABLE_LIMITS.numericText), column("integer")).length, TABLE_LIMITS.numericText);
});

test("renderer rejects bad inputs and options before creating any DOM element", () => {
  let created = 0;
  const documentSpy = { createElement() { created += 1; throw new Error("Unexpected DOM call"); } };
  rejects(() => renderTable(documentSpy, table("integer", [9007199254740992])), "UNSAFE_NUMBER");
  rejects(() => renderTable(documentSpy, positive, { sort: { columnId: "count", direction: "invalid" } }), "INVALID_OPTION");
  rejects(() => renderTable(documentSpy, positive, { filter: { columnId: "count", operator: "contains", value: "1" } }), "INCOMPATIBLE_FILTER");
  rejects(() => renderTable(null, positive), "INVALID_DOCUMENT");
  assert.equal(created, 0);
});

test("module import has no document, fetch or global activation requirement", () => {
  const moduleURL = new URL("../../packages/atlas/src/atlas_viewer/static/parity02_p03_table.js", import.meta.url).href;
  const result = spawnSync(process.execPath, ["--input-type=module", "-e", `
    Object.defineProperty(globalThis, 'document', { get() { throw new Error('DOM on import'); } });
    globalThis.fetch = () => { throw new Error('Network on import'); };
    await import(${JSON.stringify(moduleURL)});
  `], { encoding: "utf8", timeout: 10000 });
  assert.equal(result.status, 0, result.stderr);
});
