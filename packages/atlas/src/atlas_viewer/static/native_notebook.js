import {renderTable} from './parity02_p03_table.js';
import {NativeTriageUI} from './native_triage_ui.js';
import {mountGraph} from './native_graph.js';
import {buildNativeNavigation} from './native_navigation.js';
import {mountLineage} from './native_lineage.js';
import {makePresentation,recordMatches,recordSort,norm,literalText,catalogTitle,catalogStatus,TABLE_FILTER_FIELDS,tableFilterOptions,tableMatchesFilters,typedTableCsv,groupRequirementRows} from './native_legacy_model.js';
import {mountEditorialTree} from './native_legacy_tree.js';
import {renderRecordIndex,renderRecordPresentation,renderPresentationDetail,renderReadingTable,renderDatasetNotice,renderRelationPresentation,renderCatalog,ASSET_COLLECTIONS} from './native_legacy_views.js';
const $=id=>document.getElementById(id),own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const state={sources:[],source:null,pane:'tree',treeMode:'editorial',page:0,table:null,columnPage:0,graph:null,lineage:null,request:0,navigation:null,detail:null,history:[],presentation:null,editorial:{},tableView:'reading',tableGrouping:'nucleus',columnOrder:'presentation',tableFilters:{},assetGroup:'product_items',relationMode:'records'};
const el=(tag,text=null,cls='')=>{const n=document.createElement(tag);if(text!==null)n.textContent=String(text);if(cls)n.className=cls;return n;};
const button=(text,fn)=>{const b=el('button',text);b.type='button';b.addEventListener('click',fn);return b;};
let detailTrigger=null,triage=null;
state.batchFiltered=[];
function declared(e,key){
  const aliases={native_id:e.kind==='record'?['native_id','id']:['native_id'],source_key:['key','id'],status:['execution_state','status','result_state','result_group'],date:['started_at','startTime','timestamp','date','scientific_at']};
  if(e[key]!==null&&e[key]!==undefined)return e[key]===''?'"" — texto vazio declarado':e[key];
  const field=(aliases[key]||[key]).map(name=>e.fields.find(f=>f.name===name)).find(Boolean);
  return field?(field.type==='null'?'NULL — valor declarado':field.text===''?'"" — texto vazio declarado':field.text):'Não declarado';
}
function markSelection(){
  $('native-content').querySelectorAll('tr[data-uid],tr[data-row-id],article[data-uid],li[data-uid],details[data-uid]').forEach(row=>{
    const selected=(row.dataset.uid||row.getAttribute('data-row-id'))===state.detail;
    row.dataset.selected=String(selected);if(row.tagName==='TR')row.setAttribute('aria-selected',String(selected));else if(selected)row.setAttribute('aria-current','true');else row.removeAttribute('aria-current');
  });
}
function closeDetail(restore=false){
  state.graph?.cancelPendingSelection?.();
  const selected=state.detail,content=$('native-content');
  let target;
  if(restore){
    const usable=node=>node?.isConnected&&!node.disabled&&node.getClientRects().length>0;
    const occurrence=[...content.querySelectorAll('[data-uid],[data-row-id],[data-native-node]')].find(node=>(node.dataset.uid||node.getAttribute('data-row-id')||node.getAttribute('data-native-node'))===selected);
    const occurrenceTrigger=occurrence?.querySelector('button:not(:disabled),summary')||(occurrence?.tabIndex>=0?occurrence:null);
    const recovered=occurrenceTrigger||(state.table===selected?$('native-table-detail'):null);
    target=[detailTrigger,recovered,...content.querySelectorAll('button,select,[tabindex="0"]')].find(usable);
  }
  $('native-detail').hidden=true;state.graph?.placeMinimap?.();state.detail=null;state.history=[];markSelection();
  if(restore){if(target){target.focus();target.scrollIntoView({block:'nearest',inline:'nearest'});}else{content.tabIndex=-1;content.focus();}}
  detailTrigger=null;
}
function rerenderFocus(label){render();const target=[...$('native-content').querySelectorAll('button,select')].find(n=>(n.id||n.textContent)===label&&!n.disabled);if(target)target.focus();else{$('native-content').tabIndex=-1;$('native-content').focus();}}
function population(host,rows,total,noun){
  const p=el('p',null,'application-population');p.append(el('strong',String(rows.length)),document.createTextNode(` ${noun} na seleção de ${total} nesta revisão.`));host.append(p);
  if(!rows.length){const empty=el('div',null,'empty');empty.append(el('h3',total?'Nenhum resultado para estes filtros':'Nenhuma ocorrência declarada'),el('p',total?'Ajuste a busca ou limpe os filtros para explorar esta seção.':'Esta seção está vazia na revisão selecionada. As outras visualizações continuam disponíveis.'));if(total)empty.append(button('Limpar filtros',clearFilters));host.append(empty);}
}
function clearFilters(){state.tableFilters={};triage.resetFilters();state.page=0;state.columnPage=0;closeDetail();render();}
const entries=()=>state.source?.status==='READY'?state.source.entries:[];
const presentation=()=>state.presentation??=makePresentation(entries());
const recordFilters=()=>triage?.filters()??{};
const visibleRecords=()=>presentation().records.filter(r=>triage?triage.matches(r.entry):true);
function matches(e,context=null){
  if(!triage)return true;
  if(!context)return triage.matches(e);
  const filters=triage.filters(),model=triage.model,annotations=triage.ledger.annotations;
  if(filters.query&&!model.matches(e,{query:filters.query},annotations)&&!model.matches(context,{query:filters.query},annotations))return false;
  for(const [key,value]of Object.entries(filters)){
    if(!value||key==='query'||key==='from'||key==='to')continue;
    if(key==='kind'){
      if(!model.matches(e,{kind:value},annotations)&&!model.matches(context,{kind:value},annotations))return false;
      continue;
    }
    const target=!model.facet(e,key,annotations).present?context:e;
    if(!model.matches(target,{[key]:value},annotations))return false;
  }
  const dated=model.facet(e,'date').present?e:context;
  return model.matches(dated,{from:filters.from,to:filters.to},annotations);
}
function message(text,error=false){$('native-notice').textContent=text;$('native-notice').classList.toggle('error',error);$('native-notice').setAttribute('role',error?'alert':'status');}
function options(id,values,all){
  const s=$(id);s.replaceChildren();const o=el('option',all);o.value='';s.append(o);
  for(const v of [...new Set(values.filter(Boolean))].sort()){
    const x=el('option',v);x.value=v;s.append(x);
  }
}
function contextualFilterOptions({preserve=true}={}){
  if(!triage)return;
  const technical=state.pane==='tree'&&state.treeMode==='structural'||state.pane==='relations'&&state.relationMode==='technical'||['tables','assets','coverage','overview','search','selected','retention','baselines'].includes(state.pane);
  triage.filterOptions(preserve,technical?entries():presentation().records.map(r=>r.entry));
}
function download(name,content,type='application/json'){const blob=content instanceof Blob?content:new Blob([content],{type}),u=URL.createObjectURL(blob),a=el('a');a.href=u;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1000);}

function exactOccurrenceJSON(e){
  if(e.kind!=='table')return e.raw_json;
  // Table entries carry a validated rows:[] transport skeleton. Reinsert
  // EVERY verified row's original raw JSON without JSON.parse/JS Number:
  // scientific integers and decimal lexemes must remain byte-exact.
  const rows=entries().filter(r=>r.kind==='row'&&r.table_uid===e.uid)
    .sort((a,b)=>a.ordinal-b.ordinal);
  if(rows.length!==e.row_count||rows.some((r,i)=>r.ordinal!==i))
    throw Error('NATIVE_TABLE_OCCURRENCE_INCOMPLETE');
  const head=e.raw_json;
  let depth=0,offset=-1;
  for(let i=0;i<head.length;i++){
    const ch=head[i];
    if(ch==='"'){
      let j=i+1,escaped=false;
      for(;j<head.length;j++){
        if(escaped){escaped=false;continue;}
        if(head[j]==='\\'){escaped=true;continue;}
        if(head[j]==='"')break;
      }
      if(j>=head.length)break;
      if(depth===1&&head.slice(i,j+1)==='"rows"'&&
         head.slice(j+1,j+4)===':[]'){
        if(offset!==-1)throw Error('NATIVE_TABLE_ROWS_AMBIGUOUS');
        offset=j+2;
      }
      i=j;
    } else if(ch==='{'||ch==='[')depth++;
    else if(ch==='}'||ch===']')depth--;
  }
  if(offset<0)throw Error('NATIVE_TABLE_ROWS_MISSING');
  return head.slice(0,offset+1)+rows.map(r=>r.raw_json).join(',')+
    head.slice(offset+1);
}
function navigation(){return state.navigation??=buildNativeNavigation(entries());}
function currentContext(){return{source:state.source.id,snapshot:state.source.metadata_sha256,pane:state.pane,treeMode:state.treeMode,page:state.page,table:state.table,columnPage:state.columnPage,tableView:state.tableView,tableGrouping:state.tableGrouping,columnOrder:state.columnOrder,tableFilters:{...state.tableFilters},assetGroup:state.assetGroup,relationMode:state.relationMode,detail:state.detail,triageFilters:triage.filters(),search:$('native-search').value,family:$('native-family').value,status:$('native-status').value,kind:$('native-kind').value};}
function pagedLinks(host,items,draw){
  let page=0;const content=el('div'),controls=el('div',null,'pager');host.append(content,controls);
  const show=()=>{content.replaceChildren();for(const item of items.slice(page*40,(page+1)*40))content.append(draw(item));controls.replaceChildren();if(items.length>40){const previous=button('← Vínculos',()=>{page--;show();}),next=button('Vínculos →',()=>{page++;show();});previous.disabled=page===0;next.disabled=(page+1)*40>=items.length;controls.append(previous,el('span',`${page*40+1}–${Math.min((page+1)*40,items.length)} de ${items.length}`),next);}};show();
}
function openOccurrence(uid){
  const target=navigation().byUid.get(uid);if(!target)return;
  if(state.detail)state.history.push(currentContext());state.detail=null;
  state.pane=({node:'tree',record:'records',table:'tables',row:'tables',asset:'assets',relation:'relations',collection:'coverage'})[target.kind]||'coverage';
  if(target.kind==='node')state.treeMode='structural';
  if(target.kind==='asset')state.assetGroup=target.group;
  if(target.kind==='relation')state.relationMode=target.group==='edges'?'records':'technical';
  state.page=0;state.columnPage=0;state.tableFilters={};
  if(target.kind==='table'||target.kind==='row')state.table=target.table_uid||target.uid;
  triage.resetFilters();
  if(target.kind==='row'){
    const original=entries().filter(e=>e.kind==='row'&&e.table_uid===target.table_uid),ordered=state.tableGrouping==='nucleus'?groupRequirementRows(original,{sourceId:state.source.id,snapshot:state.source.metadata_sha256}).flatMap(group=>group.rows):original;
    state.page=Math.floor(Math.max(0,ordered.findIndex(row=>row.uid===target.uid))/100);
  }
  else if(['record','relation','asset','collection'].includes(target.kind)){
    const population=target.kind==='record'?visibleRecords().sort(recordSort).map(r=>r.entry):entries().filter(e=>e.kind===target.kind&&(e.kind!=='collection'||e.group!=='$structure')&&(e.kind!=='asset'||e.group===state.assetGroup)&&(e.kind!=='relation'||state.relationMode==='technical'||e.group==='edges')&&matches(e));
    const index=population.findIndex(e=>e.uid===target.uid),pageSize=target.kind==='asset'?50:target.kind==='collection'?40:100;
    state.page=Math.floor(Math.max(0,index)/pageSize);
  }
  render();if(target.kind==='node'&&state.graph)state.graph.locate(uid);detail(target,false);
  $('native-detail').scrollIntoView({block:'nearest'});
}
function returnToSelection(){
  const saved=state.history.pop();if(!saved)return;
  if(saved.source!==state.source?.id||saved.snapshot!==state.source?.metadata_sha256){state.history=[];message('O snapshot mudou; selecione novamente a ocorrência.',true);return;}
  Object.assign(state,{pane:saved.pane,treeMode:saved.treeMode,page:saved.page,table:saved.table,columnPage:saved.columnPage,tableView:saved.tableView,tableGrouping:saved.tableGrouping??'nucleus',columnOrder:saved.columnOrder,tableFilters:{...saved.tableFilters},assetGroup:saved.assetGroup,relationMode:saved.relationMode,detail:null});
  contextualFilterOptions();
  triage.restoreFilters(saved.triageFilters||{query:saved.search,family:saved.family,result_group:saved.status,kind:saved.kind});
  render();const target=navigation().byUid.get(saved.detail);if(target){if(state.pane==='tree'&&state.graph)state.graph.locate(target.uid);detail(target,false);}
}
function relatedOccurrences(e){
  const model=navigation(),section=el('section',null,'native-links');section.dataset.testid='native-context-links';
  section.append(el('h3','Vínculos nesta fonte e revisão'),el('p','Referências declaradas e pertencimento estrutural permitem navegar; não comprovam derivação, autenticidade ou aceite.','muted'));
  const outgoing=model.outgoing.get(e.uid)||[],incoming=model.incoming.get(e.uid)||[];
  if(!outgoing.length&&!incoming.length)section.append(el('p','Nenhum vínculo entre ocorrências foi declarado. Os campos originais permanecem disponíveis abaixo.','muted'));
  pagedLinks(section,outgoing,ref=>{
    const item=el('div',null,'native-reference'),literal=ref.literal===null?'null':ref.literal;
    if(ref.resolution==='UNIQUE'){const target=model.byUid.get(ref.targets[0]);item.append(button(ref.label+' → '+target.title,()=>openOccurrence(target.uid)));}
    else if(ref.resolution==='COLLISION'){
      const candidates=el('details');candidates.append(el('summary',`${ref.label}: ${literal} — AMBIGUOUS · ${ref.targets.length} ocorrências`));
      pagedLinks(candidates,ref.targets,uid=>{const target=model.byUid.get(uid);return button(target.title+' · '+target.kind+' · '+target.uid,()=>openOccurrence(uid));});item.append(candidates);
    }else item.append(el('p',`${ref.label}: ${literal} — ${ref.resolution==='NOT_DECLARED'?'não declarado':ref.resolution==='NOT_INTERPRETED'?'não interpretado nesta revisão':'UNRESOLVED nesta revisão'}`,'muted'));
    return item;
  });
  if(incoming.length){const reverse=el('details');reverse.append(el('summary',`Referências recebidas · ${incoming.length}`));pagedLinks(reverse,incoming,ref=>{const target=model.byUid.get(ref.uid);return button(target.title+' · '+ref.label+(ref.resolution==='COLLISION'?' · alvo AMBIGUOUS':''),()=>openOccurrence(target.uid));});section.append(reverse);}
  for(const[name,raw]of model.evidence.get(e.uid)||[]){const evidence=el('details',null,'native-evidence');evidence.dataset.testid='native-evidence';evidence.append(el('summary','Evidência e origem declaradas · '+name),el('pre',raw));section.append(evidence);}
  return section;
}
function detail(e,remember=true,moveFocus=true){
  if(!entries().includes(e))return;
  const trigger=document.activeElement;if($('native-content').contains(trigger)||$('native-record-index').contains(trigger))detailTrigger=trigger;
  if(remember&&state.detail&&state.detail!==e.uid)state.history.push(currentContext());state.detail=e.uid;
  const full=exactOccurrenceJSON(e);$('native-detail').hidden=false;state.graph?.placeMinimap?.();const host=$('native-detail-body');host.replaceChildren();
  if(state.history.length){const back=button('← Voltar à seleção anterior',returnToSelection);back.dataset.testid='native-context-back';host.append(back);}
  renderPresentationDetail(host,e,presentation(),navigation(),openOccurrence);
  triage.addDetailControls(host,e);
  const inspection=el('details',null,'inspection');inspection.append(el('summary','Inspecionar identidade, vínculos, campos e JSON exato'),el('p',e.kind+' · '+e.group,'muted'));const d=el('dl');
  for(const[k,v]of [['ID original',declared(e,'native_id')],['Família',declared(e,'family')],['Estado declarado',declared(e,'status')],['Pointer',e.pointer],['Fonte',state.source.name||state.source.id],['Revisão',state.source.revision]])d.append(el('dt',k),el('dd',v??'Não declarado'));
  const technical=el('details',null,'application-identity'),identity=el('dl');technical.append(el('summary','Identidade, fonte e posição no snapshot'));
  for(const[k,v]of [['UID de consulta',e.uid],['Chave estrutural',declared(e,'source_key')],['Parente declarado',declared(e,'parent_key')],['Resolução',e.parent_resolution??'Não aplicável']])identity.append(el('dt',k),el('dd',v??'Não declarado'));
  technical.append(identity);const fields=el('dl',null,'application-fields');
  for(const f of e.fields)fields.append(el('dt',f.name+' ['+f.type+']'),el('dd',f.text));const pre=el('pre',full);pre.dataset.testid='native-raw';
  inspection.append(d,relatedOccurrences(e),technical,el('h3','Campos originais'),fields,el('h3','Valor original (JSON exato)'),pre,button('Exportar esta ocorrência',()=>download('atlas-occurrence.json',full)));host.append(inspection);
  markSelection();if(moveFocus&&state.pane!=='tree')$('native-detail-title').focus();
}
function pager(host,total,pageSize=100){const pages=Math.max(1,Math.ceil(total/pageSize));state.page=Math.min(state.page,pages-1);const p=el('div',null,'pager'),prev=button('← Anterior',()=>{state.page--;closeDetail();rerenderFocus(state.page===0?'Próxima →':'← Anterior');}),next=button('Próxima →',()=>{state.page++;closeDetail();rerenderFocus(state.page+1>=pages?'← Anterior':'Próxima →');});prev.disabled=state.page===0;next.disabled=state.page+1>=pages;p.append(prev,el('span',`Página ${state.page+1}/${pages} · ${total} ocorrências na seleção`),next);host.append(p);return state.page*pageSize;}
function grid(host,rows,columns){const wrap=el('div',null,'table-scroll'),table=el('table'),head=el('thead'),hr=el('tr');wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Tabela de ocorrências; role horizontalmente para consultar as colunas');columns.forEach(c=>{const th=el('th',c[0]);th.scope='col';hr.append(th);});head.append(hr);table.append(head);const body=el('tbody');for(const e of rows){const tr=el('tr');tr.dataset.uid=e.uid;columns.forEach((c,i)=>{const td=el('td');if(i===0)td.append(button(c[1](e),()=>detail(e)));else td.textContent=c[1](e);tr.append(td);});body.append(tr);}table.append(body);wrap.append(table);host.append(wrap);}
function showTree(host){
  const tools=el('div',null,'application-tree-organization'),label=el('label','Modo de navegação'),mode=el('select');mode.id='native-tree-mode';
  for(const[value,text]of [['editorial','Árvore editorial de registros'],['structural','Objetos técnicos — contexto integral']]){const o=el('option',text);o.value=value;mode.append(o);}mode.value=state.treeMode;label.append(mode);tools.append(label);host.append(tools);
  mode.addEventListener('change',()=>{state.treeMode=mode.value;state.page=0;closeDetail();render();$('native-tree-mode').focus();});
  if(state.treeMode==='editorial'){
    const rows=visibleRecords();state.batchFiltered=rows.map(r=>r.entry);if(!rows.length){population(host,rows,presentation().records.length,'registros');return;}
    state.graph=mountEditorialTree(host,presentation(),rows,e=>detail(e),state.editorial,{
      obstructions:()=>[$('native-detail'),$('native-batch-bar')].filter(n=>!n.hidden).map(n=>n.getBoundingClientRect()),
      minimapAnchor:()=>$('native-detail').hidden?null:$('native-close-detail'),
      isBatchSelected:e=>triage.ledger.has(e),onBatchToggle:e=>triage.toggle(e),onVisibilityChange:()=>triage.syncBatch(),
    });return;
  }
  const all=entries().filter(e=>e.kind==='node'),nodes=all.length?all:entries().filter(e=>e.kind==='record');
  host.append(el('h2','Estrutura técnica completa'),el('p','Contexto integral: os filtros abaixo selecionam resultados da busca; este grafo mantém todos os objetos técnicos. Use a árvore editorial para navegar apenas pelos registros do filtro.','notice'));
  if(!nodes.length){host.append(el('p','Nenhum nó estrutural declarado neste pacote.','empty'));return;}
  const gh=el('div');host.append(gh);state.graph=mountGraph(gh,nodes,node=>{const original=navigation().byUid.get(node.uid);if(original)detail(original);else closeDetail();});
  const selected=nodes.filter(e=>matches(e));state.batchFiltered=selected;host.append(el('p',`${selected.length} de ${nodes.length} nós encontrados. Contexto gráfico integral explicitamente separado dos resultados filtrados.`,'muted'));
  const offset=pager(host,selected.length,40),links=el('div',null,'graph-results');for(const n of selected.slice(offset,offset+40))links.append(button(n.title,()=>state.graph.locate(n.uid)));host.append(links);
}
function showRecords(host,kind='record'){
  const all=entries().filter(e=>e.kind===kind),rows=kind==='record'?visibleRecords().sort(recordSort):all.filter(e=>matches(e));host.append(el('h2',kind==='relation'?'Relações declaradas':'Registros e resultados das fontes integradas'),el('p','Execução, publicação, admissão e revisão são estados distintos. IDs repetidos permanecem como ocorrências separadas.','muted'));state.batchFiltered=rows.map(r=>r.entry||r);population(host,rows,all.length,'ocorrências');if(!rows.length)return;const offset=pager(host,rows.length);
  if(kind==='record')renderRecordPresentation(host,rows.slice(offset,offset+100),detail);else grid(host,rows.slice(offset,offset+100),[['Relação',e=>e.title],['Coleção',e=>e.group]]);
}
function tableFilterControls(host){
  const controls=el('fieldset',null,'table-tools table-domain-filters');
  controls.append(el('legend','Filtros declarados das tabelas'));
  for(const[field,title]of TABLE_FILTER_FIELDS){
    const values=tableFilterOptions(entries(),field);if(!values.length)continue;
    const label=el('label',title),select=el('select');select.id='native-table-filter-'+field;
    select.setAttribute('aria-label',title+' da tabela');
    const all=el('option','Todos');all.value='';select.append(all);
    for(const value of values){const option=el('option',value.label);option.value=value.key;select.append(option);}
    select.value=state.tableFilters[field]||'';label.append(select);controls.append(label);
    select.addEventListener('change',()=>{state.tableFilters[field]=select.value;state.page=0;state.columnPage=0;closeDetail();rerenderFocus(select.id);});
  }
  if(controls.children.length===1)return;
  const clear=button('Limpar filtros da tabela',()=>{state.tableFilters={};state.page=0;state.columnPage=0;closeDetail();rerenderFocus('native-table-clear');});
  clear.id='native-table-clear';clear.disabled=!Object.values(state.tableFilters).some(Boolean);controls.append(clear);host.append(controls);
}
function showTables(host){
  const allTables=entries().filter(e=>e.kind==='table'),byTable=new Map(allTables.map(t=>[t.uid,[]]));host.append(el('h2','Tabelas de resultados'));
  if(!allTables.length){host.append(el('p','Nenhuma tabela declarada.','empty'));return;}
  for(const row of entries())if(row.kind==='row'&&byTable.has(row.table_uid))byTable.get(row.table_uid).push(row);
  tableFilterControls(host);
  // A row can be found by any original field, in its declared table context.
  // Context only scopes the selection; no scientific field is rewritten.
  const rowMatches=(row,table)=>tableMatchesFilters(row,state.tableFilters)&&matches(row,table);
  const tables=allTables.filter(t=>tableMatchesFilters(t,state.tableFilters)&&
    ((!state.tableFilters.nucleus_id&&matches(t))||byTable.get(t.uid).some(r=>rowMatches(r,t))));
  host.append(el('p',`${tables.length} tabelas na seleção de ${allTables.length} carregadas.`,'muted'));
  if(!tables.length){host.append(el('p','Nenhuma tabela ou linha corresponde à busca e aos filtros.','empty'));return;}
  if(!tables.some(t=>t.uid===state.table))state.table=tables[0].uid;
  const label=el('label','Tabela'),sel=el('select');sel.id='native-table-select';
  for(const t of tables){const o=el('option',t.title);o.value=t.uid;sel.append(o);}sel.value=state.table;
  sel.addEventListener('change',()=>{state.table=sel.value;state.page=0;state.columnPage=0;closeDetail();rerenderFocus('native-table-select');});label.append(sel);host.append(label);
  const table=tables.find(t=>t.uid===state.table),allRows=byTable.get(state.table),rows=allRows.filter(e=>rowMatches(e,table));
  state.batchFiltered=[table];
  host.append(triage.checkControl(table,'Incluir tabela no lote'));
  renderDatasetNotice(host,table,presentation());
  const nucleusGroups=groupRequirementRows(rows,{sourceId:state.source.id,snapshot:state.source.metadata_sha256}),displayRows=state.tableGrouping==='nucleus'?nucleusGroups.flatMap(group=>group.rows):rows;
  const cols=[...new Set(allRows.flatMap(r=>Object.keys(r.cells)))],start=pager(host,rows.length),windowRows=displayRows.slice(start,start+100),columnPages=Math.max(1,Math.ceil(cols.length/32));
  state.columnPage=Math.min(state.columnPage,columnPages-1);const visibleColumns=cols.slice(state.columnPage*32,(state.columnPage+1)*32),tools=el('div',null,'toolbar');
  tools.append(button('Detalhes da tabela',()=>detail(table)),button('JSON das linhas selecionadas',()=>download('atlas-table-rows.json','['+rows.map(r=>r.raw_json).join(',')+']')),button('CSV protegido',()=>{
    const cell=v=>{let s=String(v??'');if(/^[\s\u0000-\u001f]*[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
    download('atlas-table.csv',[cols.map(cell).join(','),...rows.map(r=>cols.map(c=>cell(r.cells[c]?.text??'')).join(','))].join('\r\n'),'text/csv;charset=utf-8');
  }),button('CSV tipado das linhas',()=>download('atlas-table-typed.csv',typedTableCsv(table,rows,cols),'text/csv;charset=utf-8')));
  tools.firstElementChild.id='native-table-detail';
  host.append(tools,el('p',`${rows.length} linhas selecionadas de ${allRows.length} carregadas; ${cols.length} colunas. CSV protegido serve à leitura e pode confundir tipos ou valores ausentes. CSV tipado e JSON conservam presença, tipos e valores originais; o CSV tipado inclui a linha completa.`,'muted'));
  if(columnPages>1&&state.tableView==='p03'){const cp=el('div',null,'pager'),prev=button('← Colunas',()=>{state.columnPage--;closeDetail();rerenderFocus(state.columnPage===0?'Colunas →':'← Colunas');}),next=button('Colunas →',()=>{state.columnPage++;closeDetail();rerenderFocus(state.columnPage+1===columnPages?'← Colunas':'Colunas →');});prev.disabled=state.columnPage===0;next.disabled=state.columnPage+1===columnPages;cp.append(prev,el('span',`Janela de colunas ${state.columnPage+1}/${columnPages}`),next);host.append(cp);}
  if(!visibleColumns.length){host.append(el('p','A tabela não declara células; valores indisponíveis não são reconstruídos.','empty'));return;}
  const viewTools=el('div',null,'table-tools'),viewLabel=el('label','Apresentação'),view=el('select');view.id='native-table-view';
  for(const[value,text]of [['reading','Leitura organizada'],['p03','Inspeção P03 congelada']]){const o=el('option',text);o.value=value;view.append(o);}view.value=state.tableView;viewLabel.append(view);viewTools.append(viewLabel);
  const orderLabel=el('label','Ordem de colunas'),order=el('select');order.id='native-column-order';for(const[value,text]of [['presentation','Identificação → nome → descrição → critérios'],['original','Ordem original do snapshot']]){const o=el('option',text);o.value=value;order.append(o);}order.value=state.columnOrder;orderLabel.append(order);viewTools.append(orderLabel);
  const groupingLabel=el('label','Organização das linhas'),grouping=el('select');grouping.id='native-table-grouping';for(const[value,text]of [['nucleus','Agrupar por núcleo declarado'],['original','Ordem original das linhas']]){const o=el('option',text);o.value=value;grouping.append(o);}grouping.value=state.tableGrouping;groupingLabel.append(grouping);viewTools.append(groupingLabel);host.append(viewTools);
  grouping.addEventListener('change',()=>{state.tableGrouping=grouping.value;state.page=0;closeDetail();rerenderFocus('native-table-grouping');});
  view.addEventListener('change',()=>{state.tableView=view.value;closeDetail();rerenderFocus('native-table-view');});order.addEventListener('change',()=>{state.columnOrder=order.value;closeDetail();rerenderFocus('native-column-order');});
  host.append(el('p','Organização e ordem de leitura são apresentações reversíveis. O agrupamento usa somente o núcleo declarado; ausências ficam em Não declarado. JSON e CSV mantêm as linhas e colunas na ordem original da seleção, com seus valores exatos.','muted'));
  const drawRows=(target,visibleRows)=>{
    if(state.tableView==='reading'){renderReadingTable(target,visibleRows,cols,detail,{order:state.columnOrder});return;}
    const descriptor={version:'p03-table/1',semantic_status:'CANDIDATE_PRESENTATION',title:table.title,description:'Valores da projeção original; somente a janela visível é paginada.',columns:visibleColumns.map((c,i)=>({id:'c'+i,label:c,type:'string'})),rows:visibleRows.map(r=>{
      const cells=Object.create(null),missing_reasons=Object.create(null);visibleColumns.forEach((c,i)=>{const key='c'+i;if(!own(r.cells,c)){missing_reasons[key]='MISSING — chave ausente';}else if(r.cells[c].type==='null'){cells[key]=null;missing_reasons[key]='NULL — valor declarado';}else cells[key]=r.cells[c].text;});return{id:r.uid,cells,missing_reasons};
    })};
    try{target.append(renderTable(document,descriptor));}catch(error){target.append(el('p','Conteúdo excede o limite visual do P03; exibindo texto completo sem truncar valores.','notice'));grid(target,visibleRows,[['Ocorrência',r=>r.uid],...visibleColumns.map(c=>[c,r=>own(r.cells,c)?r.cells[c].text:'MISSING'])]);}
  };
  if(state.tableGrouping==='nucleus'){
    const visible=new Set(windowRows.map(row=>row.uid));
    for(const group of nucleusGroups){const groupRows=group.rows.filter(row=>visible.has(row.uid));if(!groupRows.length)continue;
      const section=el('section',null,'requirement-group');section.dataset.nucleusGroup=group.key;
      section.append(el('h3',`Núcleo: ${group.label} · ${groupRows.length} nesta página de ${group.rows.length} linhas do grupo na seleção`));drawRows(section,groupRows);host.append(section);
    }
  }else drawRows(host,windowRows);
  host.querySelectorAll('[data-row-id]').forEach(tr=>{tr.tabIndex=0;const row=windowRows.find(r=>r.uid===tr.getAttribute('data-row-id'));tr.setAttribute('aria-label','Detalhes da linha '+(row.ordinal+1));tr.addEventListener('click',()=>detail(row));tr.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();detail(row);}});});
}
function showAssets(host){
  host.append(el('h2','Produtos, apresentações e documentos'),el('p','Coleções declaradas separadas por papel; a disponibilidade documental não concede admissão experimental.','muted'));
  const all=entries().filter(e=>e.kind==='asset'),groups=ASSET_COLLECTIONS.filter(([key])=>all.some(e=>e.group===key));
  if(!groups.length){population(host,[],0,'recursos');return;}
  if(!groups.some(([key])=>key===state.assetGroup))state.assetGroup=groups[0][0];
  const label=el('label','Coleção de produtos / documentos'),select=el('select');select.id='native-asset-collection';
  for(const[key,title]of groups){const option=el('option',title+' · '+all.filter(e=>e.group===key).length);option.value=key;select.append(option);}select.value=state.assetGroup;label.append(select);host.append(label);
  select.addEventListener('change',()=>{state.assetGroup=select.value;state.page=0;closeDetail();rerenderFocus('native-asset-collection');});
  const collection=all.filter(e=>e.group===state.assetGroup),rows=collection.filter(e=>matches(e));state.batchFiltered=rows;population(host,rows,collection.length,'itens desta coleção');if(!rows.length)return;const offset=pager(host,rows.length,50);renderCatalog(host,rows.slice(offset,offset+50),presentation(),detail);
  host.append(el('p','Referências são inspecionadas localmente. Nenhum caminho, documento ou URI é aberto automaticamente.','muted'));
}
function showTimeline(host){host.append(el('h2','Linha do tempo declarada'));const populationRows=entries().filter(e=>e.kind==='record'),all=populationRows.filter(e=>matches(e));state.batchFiltered=all;population(host,all,populationRows.length,'registros');if(!all.length)return;const rows=[...all].sort((a,b)=>{const x=Date.parse(a.date),y=Date.parse(b.date);if(Number.isFinite(x)!==Number.isFinite(y))return Number.isFinite(x)?-1:1;return Number.isFinite(x)?x-y:0;});host.append(el('p','Datas são exibidas como declaradas; registros sem data válida aparecem ao final. A ordem não implica causalidade.','muted'));const start=pager(host,rows.length),list=el('ol',null,'timeline');for(const e of rows.slice(start,start+100)){const li=el('li');li.dataset.uid=e.uid;li.append(el('time',e.date??'Data não declarada'),button(e.title,()=>detail(e)),el('span',' '+declared(e,'status'),'badge'));list.append(li);}host.append(list);}
function showCoverage(host){
  host.append(el('h2','Cobertura e origens'));const counts=new Map(),structure=entries().find(e=>e.group==='$structure');
  for(const e of entries())if(e.group!=='$structure')counts.set(e.group,(counts.get(e.group)||0)+1);
  // Parse only container names/shapes. Scalar values below use verified lexical
  // fields, never a JSON.parse/Number round trip.
  const shape=structure?JSON.parse(structure.raw_json):{},empty=[];
  for(const[key,value]of Object.entries(shape))if(value!==null&&typeof value==='object'&&!counts.has(key)){counts.set(key,0);empty.push([key,Array.isArray(value)?'[]':'{}']);}
  const summary=el('div',null,'panel');summary.append(el('p','Esta área agrega ocorrências de contexto, cobertura e origens de coleções distintas. Seu contador de navegação não é a quantidade de limites históricos nem uma porcentagem de cobertura científica. As contagens referem-se exclusivamente à projeção selecionada.'));
  for(const[group,count]of counts)summary.append(el('p',group+': '+count));host.append(summary);
  if(structure?.fields.length){const globals=el('details',null,'panel'),values=el('dl');globals.dataset.uid=structure.uid;globals.append(el('summary','Valores globais da projeção'));for(const f of structure.fields)values.append(el('dt',f.name+' ['+f.type+']'),el('dd',f.text));globals.append(values);host.append(globals);}
  for(const[key,raw]of empty){const d=el('details',null,'panel');d.append(el('summary',key+' — coleção vazia'),el('pre',raw));host.append(d);}
  const all=entries().filter(e=>e.kind==='collection'&&e.group!=='$structure'),rows=all.filter(e=>matches(e));state.batchFiltered=rows;population(host,rows,all.length,'ocorrências adicionais');const start=pager(host,rows.length,40);
  for(const e of rows.slice(start,start+40)){const d=el('details',null,'panel');d.dataset.uid=e.uid;d.append(el('summary',e.group+' — '+e.title),el('pre',e.raw_json));host.append(d);}
}
function showRelations(host){
  host.append(el('h2','Relações com origem explícita'));
  const label=el('label','Coleção e contexto das relações'),select=el('select');select.id='native-relation-mode';
  for(const[value,text]of [['records','Relações dos registros visíveis'],['technical','Linhagem técnica — contexto integral']]){const option=el('option',text);option.value=value;select.append(option);}select.value=state.relationMode;label.append(select);host.append(label);
  select.addEventListener('change',()=>{state.relationMode=select.value;state.page=0;closeDetail();rerenderFocus('native-relation-mode');});
  if(state.relationMode==='technical'){host.append(el('p','Contexto integral de objetos e arestas técnicas. A busca global não recorta este diagrama; selecione relações dos registros para comparar o mesmo filtro.','notice'));const graph=el('div');host.append(graph);state.lineage=mountLineage(graph,entries(),e=>detail(e,true,false));showRecords(host,'relation');return;}
  const model=presentation(),visible=new Set(visibleRecords().map(r=>r.id)),filters=Object.values(recordFilters()).some(Boolean);
  const edges=model.edges.filter(e=>!filters||(e.from&&e.to&&visible.has(e.from)&&visible.has(e.to)));
  state.batchFiltered=edges.map(e=>e.entry);population(host,edges,model.edges.length,'relações entre registros do filtro');host.append(el('p','Origem e destino devem pertencer ao mesmo conjunto de registros visíveis. Contexto histórico e comparação não são causalidade.','muted'));if(!edges.length)return;const offset=pager(host,edges.length);renderRelationPresentation(host,edges.slice(offset,offset+100),model,openOccurrence);
}
function render(){
  if(state.graph){state.graph.destroy();state.graph=null;}if(state.lineage){state.lineage.destroy();state.lineage=null;}
  const host=$('native-content');host.replaceChildren();state.batchFiltered=[];contextualFilterOptions();
  document.querySelectorAll('[data-pane]').forEach(b=>{if(b.dataset.pane===state.pane)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  triage.renderFilterChips();
  const records=visibleRecords();$('native-index-count').textContent=`${records.length} / ${presentation().records.length} registros`;
  renderRecordIndex($('native-record-index'),records,presentation().records.length,state.detail,e=>{if(state.pane==='tree'&&state.treeMode==='editorial'&&state.graph)state.graph.locate(e.uid);else detail(e);});
  if(state.source?.status!=='READY'){host.append(el('p',state.source?'Esta fonte não está pronta para consulta. Verifique as alterações ou atualize o snapshot explicitamente.':'Nenhuma fonte disponível. Abra um pacote na entrada local do Atlas ou consulte a visão do protocolo.','empty'));triage.afterRender([]);return;}
  const triageRows=triage.renderPane(host,state.pane);
  if(triageRows!==null)state.batchFiltered=triageRows;
  else ({tree:showTree,records:showRecords,tables:showTables,relations:showRelations,assets:showAssets,timeline:showTimeline,coverage:showCoverage})[state.pane](host);markSelection();triage.afterRender(state.batchFiltered);
}
function selectSource(){
  state.source=state.sources.find(s=>s.id===$('native-source').value)||null;state.page=0;state.table=null;state.columnPage=0;state.navigation=null;state.presentation=null;state.editorial={};state.tableFilters={};
  closeDetail();$('native-detail-body').replaceChildren();$('native-search').value='';
  const list=entries();triage.bindSource(state.source);contextualFilterOptions({preserve:false});
  const count=kind=>list.filter(e=>e.kind===kind).length;
  const triageCounts=triage.navigationCounts();
  $('native-record-count').textContent=count('record');$('native-node-count').textContent=count('node');$('native-table-count').textContent=count('table')+' / '+count('row');$('native-asset-count').textContent=count('asset');
  for(const b of document.querySelectorAll('[data-pane]')){
    let badge=b.querySelector('.application-nav-count');if(!badge){badge=el('span',null,'application-nav-count');badge.setAttribute('aria-hidden','true');b.append(badge);}
    badge.hidden=b.dataset.pane==='overview';
    badge.textContent=triageCounts[b.dataset.pane]??(b.dataset.pane==='relations'?presentation().edges.length:count(({tree:'record',records:'record',tables:'table',relations:'relation',assets:'asset',timeline:'record',coverage:'collection'})[b.dataset.pane]));
    if(b.dataset.pane==='assets')b.title='Total agregado das coleções de produtos, recursos, documentos e dossiês; cada coleção pode ser consultada separadamente.';
    if(b.dataset.pane==='coverage')b.title='Total de ocorrências auxiliares de contexto, cobertura e origens; inclui várias coleções e não é a contagem de limites históricos nem um percentual científico.';
  }
  $('native-download').disabled=state.source?.status!=='READY';$('native-source').disabled=!state.sources.length;$('native-rebuild').disabled=!state.sources.length;
  $('native-revision').textContent=state.source?.revision?'Revisão: '+state.source.revision:'';
  message(state.source?.status==='READY'?'Payloads e recomposição verificados · use Atualizar para reler.':(state.source?.status??'Nenhuma fonte')+' — '+(state.source?.errors||[]).join(', '),state.source?.status!=='READY');render();triage.refreshSnapshotNotice();
}
async function load(){
  const request=++state.request;$('native-refresh').disabled=true;$('native-source').disabled=true;$('native-download').disabled=true;$('native-rebuild').disabled=true;$('native-content').setAttribute('aria-busy','true');message('Verificando os pacotes selecionados…');
  try{
    const response=await fetch('/api/notebook',{cache:'no-store'});if(!response.ok)throw Error('Falha de leitura HTTP '+response.status);
    const data=await response.json();if(request!==state.request)return;if(!Array.isArray(data.sources))throw Error('Resposta de fontes indisponível.');
    const old=state.source?.id;state.sources=data.sources;const select=$('native-source');select.replaceChildren();
    for(const s of state.sources){const o=el('option',(s.name||s.id)+' · '+s.status);o.value=s.id;select.append(o);}
    select.value=state.sources.find(s=>s.id===old)?.id||state.sources.find(s=>s.status==='READY')?.id||state.sources[0]?.id||'';selectSource();
  }catch(e){if(request===state.request){state.sources=[];state.source=null;$('native-source').replaceChildren();selectSource();message(e.message+' Use Verificar alterações para tentar novamente.',true);}}
  finally{if(request===state.request){$('native-refresh').disabled=false;$('native-content').setAttribute('aria-busy','false');}}
}
function navigatePane(pane){
  state.pane=pane;state.page=0;state.columnPage=0;triage.page=0;closeDetail();render();triage.afterNavigation();
}
function locateEntry(entry){
  let target=entry;
  if(entry.kind!=='record'&&entry.kind!=='node'){
    const refs=navigation().outgoing.get(entry.uid)||[],incoming=navigation().incoming.get(entry.uid)||[];
    const ids=new Set(refs.filter(ref=>ref.resolution==='UNIQUE').flatMap(ref=>ref.targets));
    for(const ref of incoming)if(ref.resolution==='UNIQUE')ids.add(ref.uid);
    const records=[...ids].map(uid=>navigation().byUid.get(uid)).filter(e=>e?.kind==='record');
    if(records.length!==1){detail(entry);message(records.length?'Mais de um vínculo declarado: escolha a ocorrência nos detalhes.':'Vínculo não comprovado: esta ocorrência não declara um experimento ou registro único para localizar.');return;}
    target=records[0];
  }
  const preserved=triage.filters();
  if(!triage.matches(target)){triage.resetFilters();message('Localizando o vínculo declarado na árvore; filtros foram removidos para revelar a ocorrência. A seleção em lote foi preservada.');}
  state.pane='tree';state.treeMode=target.kind==='node'?'structural':'editorial';state.page=0;closeDetail();render();
  state.graph?.locate(target.uid);
  const card=[...$('native-content').querySelectorAll('[data-graph-id],[data-native-node]')].find(n=>(n.getAttribute('data-graph-id')||n.getAttribute('data-native-node'))===target.uid);
  card?.focus({preventScroll:true});triage.syncBatch();
}
function filterChanged(){state.page=0;state.columnPage=0;triage.page=0;closeDetail();render();}
triage=new NativeTriageUI({presentation,navigation,pane:()=>state.pane,navigate:navigatePane,refresh:render,
  filterChanged,detail,openOccurrence,locate:locateEntry,download,message,
  tableFilters:()=>state.tableFilters,removeTableFilter:key=>{delete state.tableFilters[key];filterChanged();}});
$('native-source').addEventListener('change',selectSource);$('native-refresh').addEventListener('click',load);$('native-close-detail').addEventListener('click',()=>closeDetail(true));
document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;if(!$('native-detail').hidden){e.preventDefault();closeDetail(true);}else state.graph?.cancelPendingSelection?.();});
$('native-search').addEventListener('input',filterChanged);
$('native-clear').addEventListener('click',clearFilters);
document.querySelectorAll('[data-pane]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.pane==='selected')triage.mode='list';navigatePane(b.dataset.pane);}));
$('native-download').addEventListener('click',async()=>{
  const source=state.source;if(source?.status!=='READY')return;
  try{const response=await fetch('/api/notebook/export?'+new URLSearchParams({source:source.id,snapshot:source.metadata_sha256}));if(!response.ok)throw Error('Snapshot mudou ou ficou indisponível; atualize antes de exportar.');const bytes=await response.blob();if(state.source!==source)throw Error('A fonte mudou durante a exportação. Exporte novamente a revisão selecionada.');download('atlas-projection.json',bytes);}
  catch(e){message(e.message,true);}
});const mobileMedia=matchMedia('(max-width:720px)'),mobileFilters=document.querySelector('.mobile-filters');if(mobileMedia.matches)mobileFilters.open=false;mobileMedia.addEventListener('change',event=>{if(event.matches)mobileFilters.open=false;});load();
