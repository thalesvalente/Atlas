import {renderTable} from './parity02_p03_table.js';
import {mountGraph} from './native_graph.js';
import {buildNativeNavigation} from './native_navigation.js';
import {mountLineage} from './native_lineage.js';
const $=id=>document.getElementById(id),own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const state={sources:[],source:null,pane:'tree',page:0,table:null,columnPage:0,graph:null,lineage:null,request:0,navigation:null,detail:null,history:[]};
const el=(tag,text=null,cls='')=>{const n=document.createElement(tag);if(text!==null)n.textContent=String(text);if(cls)n.className=cls;return n;};
const button=(text,fn)=>{const b=el('button',text);b.type='button';b.addEventListener('click',fn);return b;};
let detailTrigger=null;
function declared(e,key){
  const aliases={native_id:e.kind==='record'?['native_id','id']:['native_id'],source_key:['key','id'],status:['execution_state','status','result_state','result_group'],date:['started_at','startTime','timestamp','date','scientific_at']};
  if(e[key]!==null&&e[key]!==undefined)return e[key]===''?'"" — texto vazio declarado':e[key];
  const field=(aliases[key]||[key]).map(name=>e.fields.find(f=>f.name===name)).find(Boolean);
  return field?(field.type==='null'?'NULL — valor declarado':field.text===''?'"" — texto vazio declarado':field.text):'Não declarado';
}
function markSelection(){
  $('native-content').querySelectorAll('tr[data-uid],tr[data-row-id],article[data-uid],li[data-uid]').forEach(row=>{
    const selected=(row.dataset.uid||row.getAttribute('data-row-id'))===state.detail;
    row.dataset.selected=String(selected);if(row.tagName==='TR')row.setAttribute('aria-selected',String(selected));else if(selected)row.setAttribute('aria-current','true');else row.removeAttribute('aria-current');
  });
}
function closeDetail(restore=false){
  $('native-detail').hidden=true;state.detail=null;state.history=[];markSelection();
  if(restore){if(detailTrigger?.isConnected)detailTrigger.focus();else $('native-content').querySelector('button,select,[tabindex="0"]')?.focus();}
  detailTrigger=null;
}
function rerenderFocus(label){render();const target=[...$('native-content').querySelectorAll('button,select')].find(n=>(n.id||n.textContent)===label&&!n.disabled);if(target)target.focus();else{$('native-content').tabIndex=-1;$('native-content').focus();}}
function population(host,rows,total,noun){
  const p=el('p',null,'application-population');p.append(el('strong',String(rows.length)),document.createTextNode(` ${noun} na seleção de ${total} nesta revisão.`));host.append(p);
  if(!rows.length){const empty=el('div',null,'empty');empty.append(el('h3',total?'Nenhum resultado para estes filtros':'Nenhuma ocorrência declarada'),el('p',total?'Ajuste a busca ou limpe os filtros para explorar esta seção.':'Esta seção está vazia na revisão selecionada. As outras visualizações continuam disponíveis.'));if(total)empty.append(button('Limpar filtros',clearFilters));host.append(empty);}
}
function clearFilters(){for(const id of ['native-search','native-family','native-status'])$(id).value='';state.page=0;state.columnPage=0;closeDetail();render();}
const entries=()=>state.source?.status==='READY'?state.source.entries:[];
const textOf=e=>[e.title,e.native_id,e.source_key,e.family,e.status,e.raw_json,...e.fields.map(f=>f.text)].filter(x=>x!==null).join(' ');
function matches(e,context=null){const q=$('native-search').value.toLocaleLowerCase('pt-BR').trim();return(!q||textOf(e).toLocaleLowerCase('pt-BR').includes(q)||(context&&textOf(context).toLocaleLowerCase('pt-BR').includes(q)))&&(!$('native-family').value||(e.family??context?.family)===$('native-family').value)&&(!$('native-status').value||(e.status??context?.status)===$('native-status').value);}
function message(text,error=false){$('native-notice').textContent=text;$('native-notice').classList.toggle('error',error);$('native-notice').setAttribute('role',error?'alert':'status');}
function options(id,values,all){
  const s=$(id);s.replaceChildren();const o=el('option',all);o.value='';s.append(o);
  for(const v of [...new Set(values.filter(Boolean))].sort()){
    const x=el('option',v);x.value=v;s.append(x);
  }
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
function currentContext(){return{source:state.source.id,snapshot:state.source.metadata_sha256,pane:state.pane,page:state.page,table:state.table,columnPage:state.columnPage,detail:state.detail,search:$('native-search').value,family:$('native-family').value,status:$('native-status').value};}
function pagedLinks(host,items,draw){
  let page=0;const content=el('div'),controls=el('div',null,'pager');host.append(content,controls);
  const show=()=>{content.replaceChildren();for(const item of items.slice(page*40,(page+1)*40))content.append(draw(item));controls.replaceChildren();if(items.length>40){const previous=button('← Vínculos',()=>{page--;show();}),next=button('Vínculos →',()=>{page++;show();});previous.disabled=page===0;next.disabled=(page+1)*40>=items.length;controls.append(previous,el('span',`${page*40+1}–${Math.min((page+1)*40,items.length)} de ${items.length}`),next);}};show();
}
function openOccurrence(uid){
  const target=navigation().byUid.get(uid);if(!target)return;
  if(state.detail)state.history.push(currentContext());state.detail=null;
  state.pane=({node:'tree',record:'records',table:'tables',row:'tables',asset:'assets',relation:'relations',collection:'coverage'})[target.kind]||'coverage';
  state.page=target.kind==='row'?Math.floor(target.ordinal/100):0;state.columnPage=0;
  if(target.kind==='table'||target.kind==='row')state.table=target.table_uid||target.uid;
  for(const id of ['native-search','native-family','native-status'])$(id).value='';
  render();if(target.kind==='node'&&state.graph)state.graph.locate(uid);detail(target,false);
  $('native-detail').scrollIntoView({block:'nearest'});
}
function returnToSelection(){
  const saved=state.history.pop();if(!saved)return;
  if(saved.source!==state.source?.id||saved.snapshot!==state.source?.metadata_sha256){state.history=[];message('O snapshot mudou; selecione novamente a ocorrência.',true);return;}
  Object.assign(state,{pane:saved.pane,page:saved.page,table:saved.table,columnPage:saved.columnPage,detail:null});
  $('native-search').value=saved.search;$('native-family').value=saved.family;$('native-status').value=saved.status;
  render();const target=navigation().byUid.get(saved.detail);if(target){if(target.kind==='node'&&state.graph)state.graph.locate(target.uid);detail(target,false);}
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
  const trigger=document.activeElement;if($('native-content').contains(trigger))detailTrigger=trigger;
  if(remember&&state.detail&&state.detail!==e.uid)state.history.push(currentContext());state.detail=e.uid;
  const full=exactOccurrenceJSON(e);$('native-detail').hidden=false;const host=$('native-detail-body');host.replaceChildren();
  if(state.history.length){const back=button('← Voltar à seleção anterior',returnToSelection);back.dataset.testid='native-context-back';host.append(back);}
  host.append(el('h3',e.title),el('p',e.kind+' · '+e.group,'muted'));const d=el('dl');
  for(const[k,v]of [['Fonte',state.source.name||state.source.id],['Revisão',state.source.revision],['UID de consulta',e.uid],['ID original',declared(e,'native_id')],['Chave estrutural',declared(e,'source_key')],['Parente declarado',declared(e,'parent_key')],['Resolução',e.parent_resolution??'Não aplicável'],['Pointer',e.pointer]])d.append(el('dt',k),el('dd',v??'Não declarado'));
  for(const f of e.fields)d.append(el('dt',f.name+' ['+f.type+']'),el('dd',f.text));const pre=el('pre',full);pre.dataset.testid='native-raw';
  host.append(d,relatedOccurrences(e),el('h3','Valor original (JSON exato)'),pre,button('Exportar esta ocorrência',()=>download('atlas-occurrence.json',full)));
  markSelection();if(moveFocus&&state.pane!=='tree')$('native-detail-title').focus();
}
function pager(host,total,pageSize=100){const pages=Math.max(1,Math.ceil(total/pageSize));state.page=Math.min(state.page,pages-1);const p=el('div',null,'pager'),prev=button('← Anterior',()=>{state.page--;closeDetail();rerenderFocus(state.page===0?'Próxima →':'← Anterior');}),next=button('Próxima →',()=>{state.page++;closeDetail();rerenderFocus(state.page+1>=pages?'← Anterior':'Próxima →');});prev.disabled=state.page===0;next.disabled=state.page+1>=pages;p.append(prev,el('span',`Página ${state.page+1}/${pages} · ${total} ocorrências na seleção`),next);host.append(p);return state.page*pageSize;}
function grid(host,rows,columns){const wrap=el('div',null,'table-scroll'),table=el('table'),head=el('thead'),hr=el('tr');wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Tabela de ocorrências; role horizontalmente para consultar as colunas');columns.forEach(c=>{const th=el('th',c[0]);th.scope='col';hr.append(th);});head.append(hr);table.append(head);const body=el('tbody');for(const e of rows){const tr=el('tr');tr.dataset.uid=e.uid;columns.forEach((c,i)=>{const td=el('td');if(i===0)td.append(button(c[1](e),()=>detail(e)));else td.textContent=c[1](e);tr.append(td);});body.append(tr);}table.append(body);wrap.append(table);host.append(wrap);}
function showTree(host){const all=entries().filter(e=>e.kind==='node');const nodes=all.length?all:entries().filter(e=>e.kind==='record');host.append(el('h2','Árvore e linhagem'));if(!nodes.length){host.append(el('p','Nenhum nó estrutural declarado neste pacote.','empty'));return;}const gh=el('div');host.append(gh);state.graph=mountGraph(gh,nodes,detail);const selected=nodes.filter(e=>matches(e));host.append(el('p',`${selected.length} de ${nodes.length} nós encontrados. A busca alcança todas as ocorrências, inclusive fora da janela gráfica.`,'muted'));const offset=pager(host,selected.length,40),links=el('div',null,'graph-results');for(const n of selected.slice(offset,offset+40))links.append(button(n.title,()=>state.graph.locate(n.uid)));host.append(links);}
function showRecords(host,kind='record'){const all=entries().filter(e=>e.kind===kind),rows=all.filter(e=>matches(e));host.append(el('h2',kind==='relation'?'Relações declaradas':'Registros do Caderno'));host.append(el('p',kind==='relation'?'Cada ocorrência mantém seus endpoints, tipo e evidência no detalhe. Nenhuma seta é inferida de datas.':'Identificadores repetidos são preservados como ocorrências separadas.','muted'));population(host,rows,all.length,'ocorrências');if(!rows.length)return;const offset=pager(host,rows.length);grid(host,rows.slice(offset,offset+100),[['Título / ocorrência',e=>e.title],['ID original',e=>declared(e,'native_id')],['Família',e=>declared(e,'family')],['Estado',e=>declared(e,'status')],['Coleção',e=>e.group]]);}
function showTables(host){
  const allTables=entries().filter(e=>e.kind==='table'),byTable=new Map(allTables.map(t=>[t.uid,[]]));host.append(el('h2','Tabelas de resultados'));
  if(!allTables.length){host.append(el('p','Nenhuma tabela declarada.','empty'));return;}
  for(const row of entries())if(row.kind==='row'&&byTable.has(row.table_uid))byTable.get(row.table_uid).push(row);
  // A row can be found by any original field, in its declared table context.
  // Context only scopes the selection; no scientific field is rewritten.
  const tables=allTables.filter(t=>matches(t)||byTable.get(t.uid).some(r=>matches(r,t)));
  host.append(el('p',`${tables.length} tabelas na seleção de ${allTables.length} carregadas.`,'muted'));
  if(!tables.length){host.append(el('p','Nenhuma tabela ou linha corresponde à busca e aos filtros.','empty'));return;}
  if(!tables.some(t=>t.uid===state.table))state.table=tables[0].uid;
  const label=el('label','Tabela'),sel=el('select');sel.id='native-table-select';
  for(const t of tables){const o=el('option',t.title);o.value=t.uid;sel.append(o);}sel.value=state.table;
  sel.addEventListener('change',()=>{state.table=sel.value;state.page=0;state.columnPage=0;closeDetail();rerenderFocus('native-table-select');});label.append(sel);host.append(label);
  const table=tables.find(t=>t.uid===state.table),allRows=byTable.get(state.table),rows=allRows.filter(e=>matches(e,table));
  const cols=[...new Set(allRows.flatMap(r=>Object.keys(r.cells)))],start=pager(host,rows.length),windowRows=rows.slice(start,start+100),columnPages=Math.max(1,Math.ceil(cols.length/32));
  state.columnPage=Math.min(state.columnPage,columnPages-1);const visibleColumns=cols.slice(state.columnPage*32,(state.columnPage+1)*32),tools=el('div',null,'toolbar');
  tools.append(button('Detalhes da tabela',()=>detail(table)),button('JSON das linhas selecionadas',()=>download('atlas-table-rows.json','['+rows.map(r=>r.raw_json).join(',')+']')),button('CSV protegido',()=>{
    const cell=v=>{let s=String(v??'');if(/^[\s\u0000-\u001f]*[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
    download('atlas-table.csv',[cols.map(cell).join(','),...rows.map(r=>cols.map(c=>cell(r.cells[c]?.text??'')).join(','))].join('\r\n'),'text/csv;charset=utf-8');
  }));
  host.append(tools,el('p',`${rows.length} linhas selecionadas de ${allRows.length} carregadas; ${cols.length} colunas. Null e chave ausente permanecem distintos. CSV neutraliza fórmulas; JSON conserva os valores originais.`,'muted'));
  if(columnPages>1){const cp=el('div',null,'pager'),prev=button('← Colunas',()=>{state.columnPage--;closeDetail();rerenderFocus(state.columnPage===0?'Colunas →':'← Colunas');}),next=button('Colunas →',()=>{state.columnPage++;closeDetail();rerenderFocus(state.columnPage+1===columnPages?'← Colunas':'Colunas →');});prev.disabled=state.columnPage===0;next.disabled=state.columnPage+1===columnPages;cp.append(prev,el('span',`Janela de colunas ${state.columnPage+1}/${columnPages}`),next);host.append(cp);}
  if(!visibleColumns.length){host.append(el('p','A tabela não declara células; valores indisponíveis não são reconstruídos.','empty'));return;}
  const descriptor={version:'p03-table/1',semantic_status:'CANDIDATE_PRESENTATION',title:table.title,description:'Valores da projeção original; somente a janela visível é paginada.',columns:visibleColumns.map((c,i)=>({id:'c'+i,label:c,type:'string'})),rows:windowRows.map(r=>{
    const cells=Object.create(null),missing_reasons=Object.create(null);visibleColumns.forEach((c,i)=>{const key='c'+i;if(!own(r.cells,c)){missing_reasons[key]='MISSING — chave ausente';}else if(r.cells[c].type==='null'){cells[key]=null;missing_reasons[key]='NULL — valor declarado';}else cells[key]=r.cells[c].text;});return{id:r.uid,cells,missing_reasons};
  })};
  try{host.append(renderTable(document,descriptor));}catch(error){
    host.append(el('p','Conteúdo excede o limite visual do P03; exibindo texto completo sem truncar valores.','notice'));
    grid(host,windowRows,[['Ocorrência',r=>r.uid],...visibleColumns.map(c=>[c,r=>own(r.cells,c)?r.cells[c].text:'MISSING'])]);
  }
  host.querySelectorAll('[data-row-id]').forEach(tr=>{tr.tabIndex=0;const row=windowRows.find(r=>r.uid===tr.getAttribute('data-row-id'));tr.setAttribute('aria-label','Detalhes da linha '+(row.ordinal+1));tr.addEventListener('click',()=>detail(row));tr.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();detail(row);}});});
}
function showAssets(host){host.append(el('h2','Recursos, produtos e dossiês'));const all=entries().filter(e=>e.kind==='asset'),rows=all.filter(e=>matches(e));population(host,rows,all.length,'recursos');if(!rows.length)return;const offset=pager(host,rows.length,40),cards=el('div',null,'cards');for(const e of rows.slice(offset,offset+40)){const card=el('article',null,'panel');card.dataset.uid=e.uid;card.append(el('span',e.group,'badge'),el('h3',e.title),el('code',e.native_id??e.source_key??e.uid),el('p',declared(e,'status'),'muted'),button('Ver referência e detalhes',()=>detail(e)));cards.append(card);}host.append(cards,el('p','URIs são apresentadas como referências. O servidor não abre documentos externos nem recupera arquivos privados.','muted'));}
function showTimeline(host){host.append(el('h2','Linha do tempo declarada'));const populationRows=entries().filter(e=>e.kind==='record'),all=populationRows.filter(e=>matches(e));population(host,all,populationRows.length,'registros');if(!all.length)return;const rows=[...all].sort((a,b)=>{const x=Date.parse(a.date),y=Date.parse(b.date);if(Number.isFinite(x)!==Number.isFinite(y))return Number.isFinite(x)?-1:1;return Number.isFinite(x)?x-y:0;});host.append(el('p','Datas são exibidas como declaradas; registros sem data válida aparecem ao final. A ordem não implica causalidade.','muted'));const start=pager(host,rows.length),list=el('ol',null,'timeline');for(const e of rows.slice(start,start+100)){const li=el('li');li.dataset.uid=e.uid;li.append(el('time',e.date??'Data não declarada'),button(e.title,()=>detail(e)),el('span',' '+declared(e,'status'),'badge'));list.append(li);}host.append(list);}
function showCoverage(host){
  host.append(el('h2','Cobertura e origens'));const counts=new Map(),structure=entries().find(e=>e.group==='$structure');
  for(const e of entries())if(e.group!=='$structure')counts.set(e.group,(counts.get(e.group)||0)+1);
  // Parse only container names/shapes. Scalar values below use verified lexical
  // fields, never a JSON.parse/Number round trip.
  const shape=structure?JSON.parse(structure.raw_json):{},empty=[];
  for(const[key,value]of Object.entries(shape))if(value!==null&&typeof value==='object'&&!counts.has(key)){counts.set(key,0);empty.push([key,Array.isArray(value)?'[]':'{}']);}
  const summary=el('div',null,'panel');summary.append(el('p','Contagens referem-se exclusivamente à projeção selecionada. Não são porcentagem de toda a história nem aceite científico.'));
  for(const[group,count]of counts)summary.append(el('p',group+': '+count));host.append(summary);
  if(structure?.fields.length){const globals=el('details',null,'panel'),values=el('dl');globals.append(el('summary','Valores globais da projeção'));for(const f of structure.fields)values.append(el('dt',f.name+' ['+f.type+']'),el('dd',f.text));globals.append(values);host.append(globals);}
  for(const[key,raw]of empty){const d=el('details',null,'panel');d.append(el('summary',key+' — coleção vazia'),el('pre',raw));host.append(d);}
  const all=entries().filter(e=>e.kind==='collection'&&e.group!=='$structure'),rows=all.filter(e=>matches(e));population(host,rows,all.length,'ocorrências adicionais');const start=pager(host,rows.length,40);
  for(const e of rows.slice(start,start+40)){const d=el('details',null,'panel');d.append(el('summary',e.group+' — '+e.title),el('pre',e.raw_json));host.append(d);}
}
function showRelations(host){const graph=el('div');host.append(graph);state.lineage=mountLineage(graph,entries(),e=>detail(e,true,false));showRecords(host,'relation');}
function render(){
  if(state.graph){state.graph.destroy();state.graph=null;}if(state.lineage){state.lineage.destroy();state.lineage=null;}
  const host=$('native-content');host.replaceChildren();
  document.querySelectorAll('[data-pane]').forEach(b=>{if(b.dataset.pane===state.pane)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  const filters=[$('native-search').value.trim()&&'Busca: '+$('native-search').value.trim(),$('native-family').value&&'Família: '+$('native-family').value,$('native-status').value&&'Estado: '+$('native-status').value].filter(Boolean);
  $('native-selection').textContent=filters.length?filters.join(' · '):'Todas as ocorrências da revisão selecionada';$('native-clear').disabled=!filters.length;
  if(state.source?.status!=='READY'){host.append(el('p',state.source?'Esta fonte não está pronta para consulta. Verifique as alterações ou atualize o snapshot explicitamente.':'Nenhuma fonte disponível. Abra um pacote na entrada local do Atlas ou consulte a visão do protocolo.','empty'));return;}
  ({tree:showTree,records:showRecords,tables:showTables,relations:showRelations,assets:showAssets,timeline:showTimeline,coverage:showCoverage})[state.pane](host);markSelection();
}
function selectSource(){
  state.source=state.sources.find(s=>s.id===$('native-source').value)||null;state.page=0;state.table=null;state.columnPage=0;state.navigation=null;
  closeDetail();$('native-detail-body').replaceChildren();$('native-search').value='';
  const list=entries();options('native-family',list.map(e=>e.family),'Todas');options('native-status',list.map(e=>e.status),'Todos');
  const count=kind=>list.filter(e=>e.kind===kind).length;
  $('native-record-count').textContent=count('record');$('native-node-count').textContent=count('node');$('native-table-count').textContent=count('table')+' / '+count('row');$('native-asset-count').textContent=count('asset');
  for(const b of document.querySelectorAll('[data-pane]')){
    let badge=b.querySelector('.application-nav-count');if(!badge){badge=el('span',null,'application-nav-count');badge.setAttribute('aria-hidden','true');b.append(badge);}
    badge.textContent=count(({tree:'node',records:'record',tables:'table',relations:'relation',assets:'asset',timeline:'record',coverage:'collection'})[b.dataset.pane]);
  }
  $('native-download').disabled=state.source?.status!=='READY';$('native-source').disabled=!state.sources.length;$('native-rebuild').disabled=!state.sources.length;
  $('native-revision').textContent=state.source?.revision?'Revisão: '+state.source.revision:'';
  message(state.source?.status==='READY'?`${state.source.name} — payloads e recomposição verificados. Snapshot explícito; use Atualizar para reler.`:(state.source?.status??'Nenhuma fonte')+' — '+(state.source?.errors||[]).join(', '),state.source?.status!=='READY');render();
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
$('native-source').addEventListener('change',selectSource);$('native-refresh').addEventListener('click',load);$('native-close-detail').addEventListener('click',()=>closeDetail(true));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('native-detail').hidden){e.preventDefault();closeDetail(true);}});
for(const id of ['native-search','native-family','native-status'])$(id).addEventListener(id==='native-search'?'input':'change',()=>{state.page=0;state.columnPage=0;closeDetail();render();});
$('native-clear').addEventListener('click',clearFilters);
document.querySelectorAll('[data-pane]').forEach(b=>b.addEventListener('click',()=>{state.pane=b.dataset.pane;state.page=0;state.columnPage=0;closeDetail();render();}));
$('native-download').addEventListener('click',async()=>{
  const source=state.source;if(source?.status!=='READY')return;
  try{const response=await fetch('/api/notebook/export?'+new URLSearchParams({source:source.id,snapshot:source.metadata_sha256}));if(!response.ok)throw Error('Snapshot mudou ou ficou indisponível; atualize antes de exportar.');const bytes=await response.blob();if(state.source!==source)throw Error('A fonte mudou durante a exportação. Exporte novamente a revisão selecionada.');download('atlas-projection.json',bytes);}
  catch(e){message(e.message,true);}
});load();
