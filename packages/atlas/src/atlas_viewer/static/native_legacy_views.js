/** Safe DOM adaptation of v6.1 renderList/renderDetails/renderRecordTable,
 * renderRFTable/renderRelations and hcMount/hcRender. See REUSE-MANIFEST.json.
 * Native entries and literal values are inputs; no HTML, URL or script imports.
 */
import {KIND,EDGE,literalText,readingColumns,catalogTitle,catalogStatus,recordSort,objectData,recordExecutionPresentation} from './native_legacy_model.js';
export const element=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;};
export const action=(text,fn,cls='')=>{const b=element('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const originalIdentity=r=>{const field=r.entry.fields.find(f=>f.name==='native_id')||r.entry.fields.find(f=>f.name==='id');return field?field.type==='null'?'NULL — valor declarado':field.text===''?'"" — texto vazio declarado':field.text:literalText(r.original_id);};
function stateLines(host,data,fields){const dl=element('dl',undefined,'declared-states');for(const[key,label]of fields)if(own(data,key))dl.append(element('dt',label),element('dd',literalText(data[key])));if(dl.childElementCount)host.append(dl);}
function badge(host,value,group){if(value!==undefined)host.append(element('span',literalText(value),'badge '+(typeof group==='string'&&/^[a-z]+$/.test(group)?group:'')));}
const heading=(host,title,description)=>{const h=element('div',undefined,'section-head'),left=element('div');left.append(element('h2',title));if(description)left.append(element('p',description,'sub'));h.append(left);host.append(h);return h;};
function executionBadge(host,record,omitMissing=false){
  const {state,tone}=recordExecutionPresentation(record);
  if(state===undefined&&omitMissing)return;
  const text=literalText(state),indicator=element('span',text,'badge '+tone);
  indicator.dataset.executionTone=tone;indicator.title='Execução · '+text;host.append(indicator);
}
function tableFrame(host,headers,cls=''){const wrap=element('div',undefined,'table-wrap '+cls);wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Tabela; role horizontalmente para consultar todas as colunas');const table=element('table'),thead=element('thead'),tr=element('tr');for(const label of headers){const th=element('th',label);th.scope='col';tr.append(th);}thead.append(tr);const tbody=element('tbody');table.append(thead,tbody);wrap.append(table);host.append(wrap);return tbody;}
export function renderRecordIndex(host,rows,total,selected,select){
  host.replaceChildren();for(const r of [...rows].sort(recordSort)){const b=action('',()=>select(r.entry),'node-card'+(selected===r.id?' selected':''));b.dataset.uid=r.id;b.setAttribute('aria-current',selected===r.id?'true':'false');const title=element('span',r.title,'title'),meta=element('span',undefined,'meta'),execution=recordExecutionPresentation(r),dot=element('i',undefined,'dot '+execution.tone);dot.dataset.executionTone=execution.tone;dot.setAttribute('role','img');dot.setAttribute('aria-label','Execução · '+literalText(execution.state));dot.title=dot.getAttribute('aria-label');meta.append(dot,document.createTextNode(KIND[typeof r.kind==='string'?r.kind:'']??literalText(r.kind)));b.append(title,meta);host.append(b);}if(!rows.length)host.append(element('p','Nenhum registro neste filtro. Use Limpar.','sub'));
}
export function renderRecordPresentation(host,rows,select){
  const body=tableFrame(host,['Registro / identificador original','Tipo / família','Resultado da execução','Publicação / revisão','Artefatos'],'record-reading');
  for(const r of rows){const tr=element('tr');tr.dataset.uid=r.id;const name=element('td');name.append(action(r.title,()=>select(r.entry),'rowlink'),element('code',originalIdentity(r),'record-id'));const kind=element('td');kind.append(element('b',KIND[typeof r.kind==='string'?r.kind:'']??literalText(r.kind)),element('p',r.family,'sub'));const result=element('td');executionBadge(result,r);const states=element('td');stateLines(states,r,[['publication','Publicação'],['admission','Admissão'],['human_review','Revisão humana']]);if(!states.childElementCount)states.append(element('span','Publicação / revisão não declaradas','sub'));const artifacts=element('td',Array.isArray(r.resources)?`${r.resources.length} referências declaradas`:'Referências não declaradas');tr.append(name,kind,result,states,artifacts);body.append(tr);}
}
export function renderPresentationDetail(host,entry,model,navigation,open){
  const value=model.read(entry),data=objectData(value),r=model.byUid.get(entry.uid);host.append(element('div',r?(KIND[typeof r.kind==='string'?r.kind:'']??literalText(r.kind)):entry.group,'kicker'),element('h2',r?.title??literalText(catalogTitle(data)===undefined?entry.title:catalogTitle(data))));
  if(value!==data)host.append(element('p','Valor literal: '+literalText(value)));
  if(r)host.append(element('p',r.family,'sub'),element('code',originalIdentity(r),'record-id'));else if(entry.native_id!==null)host.append(element('code',entry.native_id,'record-id'));
  const tags=element('div',undefined,'tags');if(r)executionBadge(tags,r,true);else badge(tags,data.result,data.result_group);badge(tags,data.retention);host.append(tags);
  if(entry.kind==='row'){host.append(element('h3','Campos literais da linha'));const fields=element('dl',undefined,'declared-states');for(const[name,cell]of Object.entries(entry.cells))fields.append(element('dt',name),element('dd',cell.type==='null'?'NULL — valor declarado':cell.text));host.append(fields);}
  const links=[...(navigation.outgoing.get(entry.uid)||[]),...(navigation.incoming.get(entry.uid)||[]).map(ref=>({...ref,targets:[ref.uid]}))];
  const targets=[...new Set(links.filter(ref=>ref.resolution==='UNIQUE').flatMap(ref=>ref.targets))].map(uid=>navigation.byUid.get(uid)).filter(Boolean);
  const journey=targets.filter(e=>e.kind==='table'||e.kind==='asset'&&['product_items','dossier_packages','dossier_assessments'].includes(e.group));
  if(journey.length){const section=element('section',undefined,'record-journey');section.append(element('h3','Produtos, tabelas e dossiês'));for(const e of journey)section.append(action(e.title+(e.kind==='table'?` · ${e.row_count} linhas`:''),()=>open(e.uid)));host.append(section);}
  if(data.summary!==undefined)host.append(element('p',literalText(data.summary)));
  stateLines(host,data,[['execution_state','Execução · execution_state'],['status','Estado · status'],['result_state','Resultado · result_state'],['result_group','Grupo · result_group'],['result','Execução · result'],['publication','Publicação'],['admission','Admissão'],['human_review','Revisão humana'],['experimental_binding','Vínculo experimental'],['content_status','Conteúdo'],['model','Modelo'],['reasoning','Raciocínio'],['controller_reasoning','Raciocínio do controlador']]);
  if(data.current_notebook_observation!==undefined){const observation=element('details');observation.append(element('summary','Observação atual do Caderno'),element('pre',literalText(data.current_notebook_observation)));host.append(observation);}
  if(data.metrics!==undefined){const metrics=element('details');metrics.append(element('summary','Métricas declaradas'),element('pre',literalText(data.metrics)));host.append(metrics);}
  const resources=targets.filter(e=>e.kind==='asset'&&['resources','resource_documents'].includes(e.group));
  if(resources.length){const section=element('section');section.append(element('h3','Documentação e evidências'));const roles=['presentation-index','presentation','requirements','report','data','traceability','receipt','evidence'];resources.sort((a,b)=>{const rank=e=>{const i=roles.indexOf(objectData(model.read(e)).role);return i<0?roles.length:i;};return rank(a)-rank(b);});resources.forEach((e,index)=>{const item=element('article',undefined,'resource-card'),value=objectData(model.read(e));item.append(action(literalText(value.name??value.label??e.title),()=>open(e.uid)),element('p',literalText(value.role),'sub'));stateLines(item,value,[['availability','Disponibilidade'],['status','Estado']]);if(index<5)section.append(item);else{let more=section.querySelector('details');if(!more){more=element('details');more.append(element('summary',`Mais ${resources.length-5} referências`));section.append(more);}more.append(item);}});host.append(section);}
  if(r){const relations=model.edges.filter(e=>e.from===r.id||e.to===r.id);if(relations.length){const section=element('section');section.append(element('h3','Relações declaradas'));for(const edge of relations){const other=model.byUid.get(edge.from===r.id?edge.to:edge.from),card=element('div',undefined,'resource-card');card.append(element('b',EDGE[edge.type]??literalText(edge.type)));if(other)card.append(action(other.title,()=>open(other.id)));if(edge.reason!==undefined)card.append(element('p',literalText(edge.reason),'sub'));section.append(card);}host.append(section);}}
  for(const[key,title]of [['notes','Notas e proveniência'],['paths','Referências de armazenamento'],['sources','Fontes declaradas'],['source_warning','Limites da fonte'],['blockers','Bloqueios declarados']])if(data[key]!==undefined){const section=element('details');section.append(element('summary',title),element('pre',literalText(data[key])));host.append(section);}
}
export function renderReadingTable(host,rows,originalColumns,select,{order='presentation'}={}){
  const columns=order==='original'?originalColumns:readingColumns(originalColumns),focused=columns.length<originalColumns.length;
  if(focused)host.append(element('p',`Leitura essencial: ${columns.length} de ${originalColumns.length} colunas. A ordem original mostra todas; exportações conservam todas as colunas.`,'sub'));
  const body=tableFrame(host,columns,'literal-reading'+(focused?' reading-focus':''));
  for(const row of rows){const tr=element('tr');tr.dataset.rowId=row.uid;columns.forEach((name,index)=>{const cell=row.cells[name],td=element('td');td.dataset.column=name;const text=cell===undefined?'MISSING — chave ausente':cell.type==='null'?'NULL — valor declarado':cell.text;if(index===0)td.append(action(text,()=>select(row),'rowlink'));else td.textContent=text;tr.append(td);});body.append(tr);}return columns;
}
export function renderDatasetNotice(host,entry,model){
  const data=objectData(model.read(entry)),notice=element('section',undefined,'notice dataset-notice');notice.append(element('strong',entry.title));
  stateLines(notice,data,[['status','Estado'],['admission','Admissão'],['publication','Publicação'],['human_review','Revisão humana'],['availability','Disponibilidade']]);
  const warning=typeof data.source_warning==='string'&&data.source_warning?data.source_warning:typeof data.reason==='string'&&data.reason?data.reason:null;
  if(warning!==null)notice.append(element('p',warning));
  if(typeof data.binding_gap==='string'&&data.binding_gap)notice.append(element('p','Vínculo com o Caderno: '+data.binding_gap));
  host.append(notice);
}
export function renderRelationPresentation(host,edges,model,open){
  const body=tableFrame(host,['Origem','Relação declarada','Destino','Justificativa e fonte'],'relation-reading');
  for(const edge of edges){const tr=element('tr');tr.dataset.uid=edge.entry.uid;const endpoint=(candidates,literal,resolution)=>{const td=element('td');if(candidates.length===1)td.append(action(candidates[0].title,()=>open(candidates[0].uid),'rowlink'));else if(candidates.length>1){const details=element('details');details.append(element('summary',`${literalText(literal)} · AMBIGUOUS (${candidates.length})`));for(const e of candidates)details.append(action(e.title+' · '+e.uid,()=>open(e.uid)));td.append(details);}else td.append(element('span',literalText(literal)),element('small',(resolution??'NOT_DECLARED')+' nesta revisão'));return td;};const type=element('td');type.append(action(EDGE[edge.type]??literalText(edge.type),()=>open(edge.entry.uid),'rowlink'));const source=element('td',edge.reason===undefined?'Justificativa não declarada':literalText(edge.reason));if(edge.proofs!==undefined){const d=element('details');d.append(element('summary','Fonte / prova declarada'),element('pre',literalText(edge.proofs)));source.append(d);}tr.append(endpoint(edge.fromCandidates,edge.originalFrom,edge.fromResolution),type,endpoint(edge.toCandidates,edge.originalTo,edge.toResolution),source);body.append(tr);}
}
export const ASSET_COLLECTIONS=[['products','Produtos e apresentações'],['product_items','Produtos / itens'],['product_groups','Grupos de produtos'],['resource_documents','Documentos e dossiês'],['resources','Recursos de apresentação e evidência'],['dossier_packages','Pacotes de dossiê'],['dossier_assessments','Avaliações documentais']];
// Adapted hcRun: choose only meaningful declared context, retaining its field
// label. NULL run_id is not promoted to another ID or an admission state.
function catalogContext(host,data){
  const fields=[['native_run_id','Run original'],['run_id','Run'],['execution_id','Execução'],['stage_id','Estágio'],['scope_id','Escopo'],['entity_type','Tipo'],['dossier','Dossiê'],['root_id','Raiz'],['kind','Tipo']];
  const meaningful=([key])=>own(data,key)&&data[key]!==null&&data[key]!=='';
  const run=fields.slice(0,3).find(meaningful),stage=fields.slice(3).find(meaningful);
  if(run||stage){const selected=[run,stage].filter(Boolean);stateLines(host,data,selected);return;}
  const declared=fields.filter(([key])=>own(data,key));if(declared.length)stateLines(host,data,declared);else host.append(element('span','Contexto não declarado','sub'));
}
export function renderCatalog(host,entries,model,select){
  const body=tableFrame(host,['Produto / documento / referência','Execução / estágio / escopo','Estado documental declarado','Acesso'],'catalog-reading');
  for(const entry of entries){
    const value=model.read(entry),data=objectData(value),tr=element('tr');tr.dataset.uid=entry.uid;
    const name=element('td'),title=catalogTitle(data);name.append(action(literalText(title===undefined?entry.title:title),()=>select(entry),'rowlink'));
    if(value!==data)name.append(element('p','Valor literal: '+literalText(value)));if(data.role!==undefined)name.append(element('p',literalText(data.role),'sub'));
    const context=element('td');catalogContext(context,data);
    const identities=element('details',undefined,'catalog-identities');identities.append(element('summary','Identidades originais'));const values=element('dl',undefined,'declared-states');
    for(const key of ['id','native_id','atlas_record_id','product_id','group_id','native_run_id','run_id','execution_id','stage_id'])if(own(data,key))values.append(element('dt',key),element('dd',literalText(data[key])));
    if(values.childElementCount){identities.append(values);context.append(identities);}
    const status=element('td');badge(status,catalogStatus(data));
    if(['publication','human_review','availability','experimental_binding'].some(key=>own(data,key))){const more=element('details');more.append(element('summary','Publicação, revisão e disponibilidade'));stateLines(more,data,[['publication','Publicação'],['human_review','Revisão humana'],['availability','Disponibilidade'],['experimental_binding','Vínculo experimental']]);status.append(more);}
    const access=element('td');access.append(action('Referência e detalhes',()=>select(entry)));tr.append(name,context,status,access);body.append(tr);
  }
}
