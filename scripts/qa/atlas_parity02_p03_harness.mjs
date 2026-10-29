import data from './demo-data.js';
import {renderTable} from './parity02_p03_table.js';
import {renderMetadata, renderCandidate} from './parity02_p03_artifacts.js';

// This harness is the explicit caller. Production modules never auto-mount.
const example = document.getElementById('example');
const order = document.getElementById('order');
const missing = document.getElementById('missing');
const feedback = document.getElementById('feedback');
function largeTable() {
  return {version:'p03-table/1', semantic_status:'CANDIDATE_PRESENTATION', synthetic:true,
    title:'Limite sintético: 1000 linhas e 20000 células',
    columns:Array.from({length:20},(_,i)=>({id:i===0?'count':`c${i}`,label:`Coluna ${i+1}`,type:'integer',unit:'1'})),
    rows:Array.from({length:1000},(_,i)=>({id:`row-${i}`,cells:Object.fromEntries(Array.from({length:20},(_,j)=>[j===0?'count':`c${j}`,String(i*20+j)]))}))};
}
function updateTable() {
  const descriptor = example.value === 'large' ? largeTable() : data[example.value];
  const hasCount = descriptor.columns.some(column=>column.id==='count');
  order.disabled = missing.disabled = !hasCount;
  const options = {};
  if (hasCount && order.value !== 'declared') options.sort = {columnId:'count',direction:order.value};
  if (hasCount && missing.checked) options.filter = {columnId:'count',operator:'is_missing'};
  try {
    const rendered = renderTable(document, descriptor, options);
    document.getElementById('table-mount').replaceChildren(rendered);
    feedback.textContent = 'Apresentação atualizada; fonte preservada.';
  } catch(error) {
    feedback.textContent = `Entrada rejeitada: ${error.code || 'RENDER_ERROR'}`;
    document.getElementById('table-mount').replaceChildren();
  }
}
for (const control of [example,order,missing]) control.addEventListener('change',updateTable);
updateTable();
document.getElementById('metadata-mount').append(renderMetadata(document,data.metadata));
document.getElementById('product-mount').append(renderCandidate(document,data.product));
document.getElementById('document-mount').append(renderCandidate(document,data.document));
document.documentElement.dataset.p03Ready = 'true';
