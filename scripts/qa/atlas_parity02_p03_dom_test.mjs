/** Execute actual renderers against a DOM recorder. This is not browser QA. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {test} from 'node:test';
import {renderTable} from '../../packages/atlas/src/atlas_viewer/static/parity02_p03_table.js';
import {renderMetadata,renderCandidate} from '../../packages/atlas/src/atlas_viewer/static/parity02_p03_artifacts.js';

const fixture=name=>JSON.parse(readFileSync(fileURLToPath(new URL(`../../tests/fixtures/atlas_parity02/p03/${name}`,import.meta.url)),'utf8'));
class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.attributes={};this.dataset={};this.className='';this.parentNode=null;this._text='';}
  append(...nodes){for(const node of nodes){assert.ok(node instanceof Element);assert.equal(node.parentNode,null);node.parentNode=this;this.children.push(node);}}
  setAttribute(name,value){assert.ok(!/^on/i.test(name));assert.ok(!['href','src','srcdoc'].includes(name));this.attributes[name]=String(value);}
  set textContent(value){this._text=String(value);this.children=[];}
  get textContent(){return this._text+this.children.map(node=>node.textContent).join('');}
  set innerHTML(_){throw new Error('ACTIVE_HTML_FORBIDDEN');}
}
const doc={createElement:tag=>new Element(tag)};
const walk=node=>[node,...node.children.flatMap(walk)];
const tagged=(node,tag)=>walk(node).filter(child=>child.tagName===tag);

test('table renderer creates detached semantic structure with typed metadata and exact text',()=>{
  const descriptor=fixture('table-positive.json');const before=JSON.stringify(descriptor);const root=renderTable(doc,descriptor);
  assert.equal(root.parentNode,null);assert.equal(tagged(root,'table').length,1);assert.equal(tagged(root,'caption')[0].textContent,descriptor.title);
  assert.equal(tagged(root,'th').filter(node=>node.attributes.scope==='col').length,6);
  assert.equal(tagged(root,'th').filter(node=>node.attributes.scope==='row').length,4);
  assert.ok(root.textContent.includes('0.123456789012345678901'));assert.ok(root.textContent.includes('9007199254740993'));assert.ok(root.textContent.includes('00042'));
  assert.ok(root.textContent.includes('Precisão declarada: 2'));assert.ok(root.textContent.includes('Não informado — Não medido'));
  const scroll=walk(root).find(node=>node.attributes.role==='region');assert.equal(scroll.attributes.tabindex,'0');assert.ok(scroll.attributes['aria-label'].includes(descriptor.title));
  assert.equal(JSON.stringify(descriptor),before);
});
test('rendered sorting/filtering preserves row identities and annotates header order',()=>{
  const descriptor=fixture('table-positive.json');const root=renderTable(doc,descriptor,{sort:{columnId:'count',direction:'asc'}});
  assert.deepEqual(tagged(root,'tr').filter(n=>n.attributes['data-row-id']).map(n=>n.attributes['data-row-id']),['amostra-C','amostra-B','amostra-A','amostra-Ausente']);
  assert.equal(tagged(root,'th').find(n=>n.attributes['aria-sort'])?.attributes['aria-sort'],'ascending');
  const filtered=renderTable(doc,descriptor,{filter:{columnId:'count',operator:'is_missing'}});assert.equal(tagged(filtered,'th').filter(n=>n.attributes.scope==='row')[0].textContent,'amostra-Ausente');
});
test('empty and all-filtered tables retain semantic headers and an explicit empty state',()=>{
  const empty=renderTable(doc,fixture('table-empty.json'));assert.ok(empty.textContent.includes('Nenhuma linha declarada'));assert.equal(tagged(empty,'tbody').length,1);
  const filtered=renderTable(doc,fixture('table-positive.json'),{filter:{columnId:'count',operator:'eq',value:'-999'}});assert.ok(filtered.textContent.includes('Nenhuma linha corresponde ao filtro'));assert.equal(tagged(filtered,'td')[0].attributes.colspan,'6');
});
test('hostile values remain text nodes across all actual renderers',()=>{
  const roots=[renderTable(doc,fixture('table-malicious.json')),renderMetadata(doc,fixture('artifact-descriptor.json')),renderCandidate(doc,fixture('document-candidate.json'))];
  for(const root of roots){assert.ok(root.textContent.includes('<'));assert.equal(walk(root).filter(n=>['script','img','iframe','a','object','embed'].includes(n.tagName)).length,0);}
  assert.equal(globalThis.P03_ATTACK,undefined);
});
test('current File and mentions stay neutral while synthetic rich semantics are explicit',()=>{
  const metadata=renderMetadata(doc,fixture('artifact-descriptor.json'));const file=walk(metadata).find(n=>n.dataset.entityId==='report.pdf');
  assert.ok(file.textContent.includes('Artefato declarado (File)'));assert.ok(file.textContent.includes('Menções neutras'));assert.equal(file.dataset.semanticKind,undefined);
  assert.ok(metadata.textContent.includes('SHA-256 declarado'));assert.ok(metadata.textContent.includes('SHA-256 calculado informado pelo leitor'));
  assert.ok(metadata.textContent.includes('Disponibilidade declarada'));assert.ok(metadata.textContent.includes('Disponibilidade observada pelo leitor'));
  const document=renderCandidate(doc,fixture('document-candidate.json'));const product=renderCandidate(doc,fixture('artifact-product-candidate.json'));
  assert.equal(document.dataset.semanticKind,'document');assert.equal(product.dataset.semanticKind,'product');assert.ok(document.textContent.includes('candidato · fixture sintética'));
});
test('maximum table renders all bounded cells without truncation',()=>{
  const descriptor={version:'p03-table/1',semantic_status:'CANDIDATE_PRESENTATION',synthetic:true,title:'Synthetic maximum',columns:Array.from({length:20},(_,i)=>({id:`c${i}`,label:`C${i}`,type:'string'})),rows:Array.from({length:1000},(_,i)=>({id:`r${i}`,cells:{c0:`value${i}`}}))};
  const root=renderTable(doc,descriptor);assert.equal(tagged(root,'td').length,20000);assert.equal(tagged(root,'th').filter(n=>n.attributes.scope==='row').length,1000);
});
