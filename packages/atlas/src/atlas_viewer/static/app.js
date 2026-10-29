'use strict';

import {p03ContextKey, renderP03Metadata, renderPropertySelection} from './parity03_p03_composition.js';

// Records are untrusted text. Routes are validated before resolving source + ID.
const $ = id => document.getElementById(id);
const navigation = window.AtlasParity02State;
const initial = navigation.defaults();
const state = {catalog:null,runs:[],selected:new Set(),view:initial.view,detail:null,filters:initial.filters,returnFocus:null,p03Selections:new Map(),renderedDetail:null};
const key = navigation.key;
const filterControls = {query:'search',project:'project-filter',experiment:'experiment-filter',status:'status-filter',source:'source-filter',review:'review-filter',metrics:'metrics-filter',references:'references-filter',sort:'sort-order'};
const element = (tag,text,cls) => {const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(cls)node.className=cls;return node;};
const clear = id => $(id).replaceChildren();
const display = value => value===null||value===undefined?'Não informado':typeof value==='object'?JSON.stringify(value):String(value);
const badge = (text,kind) => element('span',text,'badge '+(kind||text||'unknown').toLowerCase().replace(/[^a-z_-]/g,''));
const runName = run => run.name||run.id;
const route = () => ({view:state.view,detail:state.detail,selected:[...state.selected],filters:{...state.filters}});
const filteredRuns = () => navigation.filterRuns(state.runs,state.filters);
const sourceFor = id => state.catalog.sources.find(source=>source.id===id);
function announce(text,error=false){$('notice').textContent=text;$('notice').className=error?'notice error':'notice';}
function addDefinition(dl,label,value){dl.append(element('dt',label),element('dd',display(value)));}
function tableRegion(label){const box=element('div','', 'table-wrap');box.tabIndex=0;box.setAttribute('role','region');box.setAttribute('aria-label',label);return box;}
function currentControl(){const node=document.activeElement;return node?.dataset.runKey?{key:node.dataset.runKey,kind:node.dataset.testid}:node?.id?{id:node.id}:null;}
function restoreControl(control){if(!control)return false;const node=control.id?$(control.id):[...document.querySelectorAll('button[data-run-key],input[data-run-key]')].find(x=>x.dataset.runKey===control.key&&x.dataset.testid===control.kind&&!x.closest('[hidden]'));if(!node||node.closest('[hidden]'))return false;node.focus({preventScroll:true});return document.activeElement===node;}
function commitRoute(next,{replace=false,focus=null}={}){
  if(!state.catalog){announce('Aguarde o carregamento das fontes antes de navegar.');return;}
  const hash=navigation.stringify(next,state.catalog);
  const parsed=navigation.parse(hash,state.catalog);
  applyRoute(parsed.route);
  const canonical=navigation.stringify(parsed.route,state.catalog);
  if(location.hash!==canonical)history[replace?'replaceState':'pushState'](null,'',canonical);
  renderRoute();
  if(parsed.warnings.length)announce(parsed.warnings.join(' '),true);
  if(focus==='detail'){$('detail').focus();$('detail').scrollIntoView({block:'start'});}
  else if(focus)restoreControl(focus);
}
function applyRoute(next){state.view=next.view;state.detail=next.detail;state.selected=new Set(next.selected);state.filters={...next.filters};for(const [field,id] of Object.entries(filterControls))if($(id).value!==state.filters[field])$(id).value=state.filters[field];}
function routeFromLocation(){if(!state.catalog)return;const parsed=navigation.parse(location.hash,state.catalog);applyRoute(parsed.route);renderRoute();if(parsed.warnings.length)announce(parsed.warnings.join(' '),true);}
function showView(view){commitRoute({...route(),view,detail:null});}
function showDetail(run){if(!document.activeElement?.closest('#detail'))state.returnFocus=currentControl();commitRoute({...route(),detail:run._key},{focus:'detail'});}
function closeDetail(){const control=state.returnFocus;commitRoute({...route(),detail:null});if(!restoreControl(control))$('main').focus({preventScroll:true});}
function runLink(run,label=runName(run)){const button=element('button',label,'inline-link');button.type='button';button.dataset.runKey=run._key;button.dataset.testid='run-link';button.addEventListener('click',()=>showDetail(run));return button;}
function sourceLink(sourceId){const button=element('button','Ver fonte e validação','source-anchor');button.type='button';button.addEventListener('click',()=>{showView('sources');const card=$('card-'+sourceId);if(card){card.focus();card.scrollIntoView({block:'nearest'});}});return button;}
function findEntity(sourceId,id){return (sourceFor(sourceId)?.read_model?.entities||[]).find(entity=>entity['@id']===id);}
function entityLink(sourceId,id,label){const run=state.runs.find(x=>x._sourceId===sourceId&&x.id===id);if(run)return runLink(run,label||runName(run));const entity=findEntity(sourceId,id),box=element('span');box.append(element('span',label||entity?.name||id),element('small',id));return box;}
function setOptions(id,items,title){const control=$(id);control.replaceChildren();const all=element('option',title);all.value='';control.append(all);for(const item of items){const option=element('option',item.name);option.value=item.key;control.append(option);}}
function updateCatalog(catalog){
  const focus=currentControl();state.catalog=catalog;state.runs=navigation.flatten(catalog);
  const contexts=new Set();for(const source of catalog.sources)for(const run of source.read_model?.runs||[])contexts.add(p03ContextKey(catalog,source,run));for(const context of state.p03Selections.keys())if(!contexts.has(context))state.p03Selections.delete(context);
  const projects=[],experiments=[];
  for(const source of catalog.sources){for(const item of source.read_model?.projects||[])projects.push({key:key(source.id,item.id),name:(item.name||item.id)+' · '+source.name});for(const item of source.read_model?.experiments||[])experiments.push({key:key(source.id,item.id),name:(item.name||item.id)+' · '+source.name});}
  const byName=(a,b)=>a.name<b.name?-1:a.name>b.name?1:a.key<b.key?-1:a.key>b.key?1:0;
  setOptions('project-filter',projects.sort(byName),'Todos os projetos');setOptions('experiment-filter',experiments.sort(byName),'Todos os experimentos');
  setOptions('source-filter',catalog.sources.map(s=>({key:s.id,name:s.name})).sort(byName),'Todas as fontes');
  setOptions('review-filter',navigation.REVIEWS.filter(Boolean).map(s=>({key:s,name:s})),'Todas as revisões');
  $('projects-count').textContent=projects.length;$('experiments-count').textContent=experiments.length;$('runs-count').textContent=state.runs.length;$('nav-count').textContent=state.runs.length;$('sources-count').textContent=catalog.sources.filter(s=>s.report.valid).length;
  $('snapshot-id').textContent=catalog.snapshot_id;
  $('indexed-at').textContent='Índice observado: '+catalog.indexed_at+' (não é data do evento)';
  const changed=catalog.sources.filter(s=>s.changed);$('change-notice').hidden=changed.length===0;$('change-notice').textContent=changed.length?`${changed.length} fonte(s) alterada(s). Registros do snapshot anterior preservados; reconstrua o índice para atualizar. A atualização expira os links e seleções antigos.`:'';
  const invalid=catalog.sources.filter(s=>!s.report.valid);
  if(!catalog.sources.length)announce('Nenhuma fonte declarada. Abra o Atlas com --source para consultar um pacote.');
  else if(invalid.length)announce(`${invalid.length} fonte(s) inválida(s) ou inacessível(is). Consulte Fontes e validade; esses registros não foram indexados.`,true);
  else announce(`${catalog.sources.length} fonte(s) aberta(s). Estados técnicos, revisão e registros sintéticos permanecem identificados.`);
  if(catalog.collisions.length)announce($('notice').textContent+' IDs repetidos entre fontes são mantidos separados.',Boolean(invalid.length));
  const parsed=navigation.parse(location.hash,catalog);applyRoute(parsed.route);
  // Canonicalize only known valid routes. Rejected URLs remain visible with an explanation.
  if(!parsed.rejected)history.replaceState(null,'',navigation.stringify(parsed.route,catalog));
  renderSources();renderDossier();renderRoute();restoreControl(focus);
  if(parsed.warnings.length)announce(parsed.warnings.join(' '),true);
}
function valueText(property){if(property.display_value===null)return 'Ausente';if(typeof property.display_value==='string')return property.display_value;return property.value==null?'Ausente':display(property.value);}
function precisionText(property){return typeof property.display_precision==='string'?property.display_precision:display(property.precision);}
function metricText(property){return valueText(property)+(property.unit?' '+property.unit:'')+(property.missing_reason?' — '+property.missing_reason:'');}
function activeFiltersText(){const labels={query:'Busca',project:'Projeto',experiment:'Experimento',source:'Fonte',status:'Estado',review:'Revisão',metrics:'Métricas',references:'Referências'};return Object.entries(labels).filter(([field])=>state.filters[field]&&state.filters[field]!=='any').map(([field,label])=>{const control=$(filterControls[field]);return label+': '+(control.tagName==='SELECT'?control.selectedOptions[0]?.textContent:state.filters[field]);}).join(' · ');}
function renderRuns(){
  clear('run-rows');const runs=filteredRuns();$('empty').hidden=Boolean(runs.length);$('result-count').textContent=`${runs.length} de ${state.runs.length} registros`;
  $('scope-summary').textContent=`${state.catalog.sources.length} pacote(s) declarado(s) · ${state.runs.length} execuções carregadas · ${runs.length} filtradas na tela. Total da fonte inteira: não informado.`;
  $('empty-reason').textContent=!state.catalog.sources.length?'Nenhuma fonte foi declarada. Abra um pacote pelo comando Atlas.':!state.runs.length?'Os pacotes abertos não contêm execuções indexáveis. Consulte Fontes e validade para distinguir ausência de dados de falha de leitura.':'Os filtros não encontraram execuções. '+(activeFiltersText()||'Nenhum filtro ativo.')+' Limpar os filtros preserva sua seleção para comparação.';
  for(const run of runs){
    const row=element('tr');row.dataset.runKey=run._key;
    const select=element('input');select.type='checkbox';select.checked=state.selected.has(run._key);select.dataset.testid='run-select';select.dataset.runKey=run._key;select.setAttribute('aria-label','Comparar '+runName(run)+' · '+run._sourceName);
    select.addEventListener('change',()=>{const selected=new Set(state.selected);if(select.checked){if(selected.size>=4){select.checked=false;announce('Selecione até quatro execuções para comparar. As demais continuam disponíveis.');return;}selected.add(run._key);}else selected.delete(run._key);commitRoute({...route(),selected:[...selected]},{focus:{key:run._key,kind:'run-select'}});});
    const selectCell=element('td');selectCell.append(select);row.append(selectCell);
    const title=element('td');const open=runLink(run);open.className='run-open';open.dataset.testid='run-open';title.append(open,element('small',run.id));
    const exp=findEntity(run._sourceId,run.experiment_id);title.append(element('small',exp?.name||run.experiment_id||'Experimento não declarado'));if(run.synthetic)title.append(badge('SINTÉTICO','synthetic'));row.append(title);
    const source=element('td',run._sourceName);source.append(element('small',run._sourceId));row.append(source);
    for(const value of [run.status,run.review_status]){const cell=element('td');cell.append(badge(value));row.append(cell);}
    const metric=element('td');for(const property of run.metrics.slice(0,2))metric.append(element('div',`${property.name}: ${metricText(property)}`));if(!run.metrics.length)metric.append(element('span','Sem métricas','muted'));if(run.metrics.length>2)metric.append(element('small',`+${run.metrics.length-2} no detalhe`));row.append(metric);$('run-rows').append(row);
  }
  const visible=new Set(runs.map(r=>r._key)),hidden=[...state.selected].filter(k=>!visible.has(k)).length;
  $('selected-count').textContent=state.selected.size?`${state.selected.size} execução(ões) selecionada(s)${hidden?' · '+hidden+' fora dos filtros':''}`:'Nenhuma execução selecionada';
  $('selection-summary').textContent='A seleção para comparação é mantida ao filtrar e navegar. São até quatro execuções; isso não limita o acervo.';
  $('clear-selection').disabled=state.selected.size===0;
}
function relatedReferenceSection(run) {
  const section=element('section','', 'related-references');
  section.dataset.testid='related-references';
  const title=element('h3','Referências relacionadas');
  title.id='related-references-heading';
  section.setAttribute('aria-labelledby',title.id);
  section.append(title,element('p','Menções declaradas nesta execução. Não indicam consumo, produção ou derivação e não constituem aprovação.','muted'));
  const references=run.related_references || [];
  if(!references.length){section.append(element('p','Nenhuma referência relacionada declarada.','muted'));return section;}
  const observations={
    AVAILABLE:'Conteúdo presente no pacote; SHA-256 calculado confere com o declarado.',
    AVAILABLE_UNVERIFIED:'Conteúdo presente e SHA-256 calculado; sem digest declarado para comparação.',
    MISSING:'Conteúdo não incluído neste pacote. A disponibilidade na origem não foi verificada.',
    EXTERNAL_UNRESOLVED:'Referência externa não acessada. Disponibilidade e integridade não verificadas.',
    UNVERIFIED:'Somente metadados declarados; conteúdo não verificado.',
    UNAVAILABLE:'Conteúdo não pôde ser lido neste pacote; integridade não verificada.',
    READ_BUDGET_EXCEEDED:'Limite de leitura atingido; conteúdo não verificado.',
    UNSAFE_REFERENCE:'Referência não aberta pelo resolvedor seguro; conteúdo não verificado.',
    INTEGRITY_MISMATCH:'Conteúdo diverge do digest ou tamanho declarado.'
  };
  for(const reference of references){
    const item=element('article','', 'panel related-reference');
    item.dataset.testid='related-reference';item.dataset.referenceId=reference.id;
    const heading=element('h4');heading.append(entityLink(run._sourceId,reference.id,reference.name || reference.id));item.append(heading);
    if(state.runs.some(r=>r._sourceId===run._sourceId && r.id===reference.id))item.append(element('code',reference.id));
    if(reference.types?.length)item.append(element('p','Tipo declarado: '+reference.types.join(', '),'muted'));
    if(reference.description)item.append(element('p',reference.description));
    const availability=reference.availability || {status:'UNVERIFIED'};
    const status=availability.status || 'UNVERIFIED';
    const details=element('dl');
    addDefinition(details,'Disponibilidade declarada',availability.declared ?? 'Não declarada');
    const observed=element('dd');observed.append(badge(status));
    details.append(element('dt','Observação do leitor'),observed);
    addDefinition(details,'SHA-256 declarado',reference.declared_digest ?? 'Não declarado');
    addDefinition(details,'SHA-256 calculado',availability.sha256 ?? 'Não calculado');
    item.append(details,element('p',observations[status] || 'Conteúdo não verificado.','muted'));
    section.append(item);
  }
  section.append(element('p','Disponibilidade e digest não autenticam origem nem aprovação científica.','muted'));
  return section;
}

function propertyTable(properties,label='Propriedades declaradas'){
  const box=tableRegion(label),table=element('table'),head=element('thead'),row=element('tr');
  for(const name of ['Propriedade','Valor','Tipo / unidade','Precisão declarada']){const th=element('th',name);th.scope='col';row.append(th);}head.append(row);table.append(head);const body=element('tbody');
  for(const property of properties){const tr=element('tr'),name=element('td',property.name);name.append(element('small',property.property_id||property.id));tr.append(name,element('td',valueText(property)+(property.missing_reason?' — '+property.missing_reason:'')),element('td',[property.type,property.unit].filter(Boolean).join(' / ')||'Não declarada'),element('td',precisionText(property)));body.append(tr);}table.append(body);box.append(table);return box;
}
function appendRelationList(host,title,ids,sourceId,empty){host.append(element('h3',title));if(!ids?.length){host.append(element('p',empty,'muted'));return;}const list=element('ul','', 'entity-list');for(const id of ids){const item=element('li');item.append(entityLink(sourceId,id));list.append(item);}host.append(list);}
function renderDetail(){
  const run=state.runs.find(r=>r._key===state.detail);$('detail').hidden=!run;if(!run){clear('detail-content');state.renderedDetail=null;return;}
  const source=sourceFor(run._sourceId),context=p03ContextKey(state.catalog,source,run);if(state.renderedDetail===context)return;
  clear('detail-content');state.renderedDetail=context;
  const target=$('detail-content');target.append(element('h3',runName(run)),element('code',run.id));
  const meta=element('div','', 'metadata');meta.append(badge(run.status),badge('Revisão: '+run.review_status,run.review_status));if(run.synthetic)meta.append(badge('SINTÉTICO','synthetic'));target.append(meta,element('p',run.description||'Sem descrição adicional.'));
  const dl=element('dl');for(const [label,value] of [['Fonte / pacote',run._sourceName],['Identidade da fonte',run._sourceId],['Snapshot do pacote',source?.snapshot_id],['Projeto',run.project_id],['Experimento',run.experiment_id],['Início declarado',run.started_at],['Fim declarado',run.ended_at],['Origem das datas',run.timestamp_origin],['Agente declarado',run.agent_id],['Software declarado',run.instrument_id]])addDefinition(dl,label,value);target.append(dl,element('p','Datas de observação não são promovidas a datas do evento. Origem temporal preservada conforme declarada.','muted'),sourceLink(run._sourceId));
  for(const [title,properties] of [['Métricas',run.metrics],['Parâmetros',run.parameters]]){target.append(element('h3',title));target.append(properties.length?propertyTable(properties,title+' da execução'):element('p','Nenhum valor declarado.','muted'));}
  if(!state.p03Selections.has(context))state.p03Selections.set(context,new Set());target.append(renderPropertySelection(document,source,run,state.p03Selections.get(context)));
  appendRelationList(target,'Entradas declaradas',run.inputs,run._sourceId,'Nenhuma entrada declarada.');
  appendRelationList(target,'Saídas declaradas',run.outputs,run._sourceId,'Nenhuma saída declarada.');
  target.append(element('h3','Artefatos e evidências'));if(!run.artifacts.length)target.append(element('p','Nenhum artefato vinculado.','muted'));
  for(const artifact of run.artifacts){const item=element('div','', 'panel'),availability=artifact.availability||{};item.append(element('strong',artifact.name),element('p',artifact.id),badge(availability.status||'UNVERIFIED'));const info=element('dl');for(const [label,value] of [['Formato',artifact.media_type],['Disponibilidade declarada',availability.declared],['SHA-256 declarado',artifact.declared_digest],['SHA-256 calculado',availability.sha256]])addDefinition(info,label,value);item.append(info,element('p','A observação descreve este pacote. Disponibilidade e digest não autenticam origem nem aprovação.','muted'));target.append(item);}
  target.append(relatedReferenceSection(run));
  target.append(renderP03Metadata(document,source,run));
  appendRelationList(target,'Derivação declarada — esta execução deriva de',run.derived_from,run._sourceId,'Nenhuma derivação de execução declarada.');
  target.append(element('p','Relações declaradas não demonstram causalidade.','muted'));
}
function renderComparison(){
  clear('compare-content');const host=$('compare-content'),runs=[...state.selected].map(k=>state.runs.find(r=>r._key===k)).filter(Boolean);
  if(runs.length<2){host.append(element('div','Selecione de duas a quatro execuções em Explorar para comparar.','empty'));return;}
  const groups=new Map(),identities=new Map();
  for(const run of runs)for(const metric of run.metrics){const id=metric.property_id||metric.name,group=JSON.stringify([id,metric.type,metric.unit]);if(!groups.has(group))groups.set(group,{name:metric.name,id,type:metric.type,unit:metric.unit,values:new Map()});const values=groups.get(group).values;if(!values.has(run._key))values.set(run._key,[]);values.get(run._key).push(metric);if(!identities.has(id))identities.set(id,new Set());identities.get(id).add(JSON.stringify([metric.type,metric.unit]));}
  const incompatible=[...identities.entries()].filter(([,values])=>values.size>1);
  if(incompatible.length)host.append(element('p','Unidades ou tipos incompatíveis: '+incompatible.map(([id])=>id).join(', ')+'. Os valores aparecem em linhas separadas; não há comparação numérica nem conversão implícita.','compare-note'));
  const box=tableRegion('Comparação bidimensional das execuções selecionadas');box.classList.add('comparison');const table=element('table'),head=element('thead'),header=element('tr');const metricHead=element('th','Métrica / tipo / unidade');metricHead.scope='col';header.append(metricHead);
  for(const run of runs){const th=element('th');th.scope='col';th.append(runLink(run),element('small',run._sourceName),element('small',run.id));header.append(th);}head.append(header);table.append(head);const body=element('tbody');
  const textRow=(title,read)=>{const row=element('tr'),label=element('th',title);label.scope='row';row.append(label);for(const run of runs)row.append(element('td',read(run)));body.append(row);};
  textRow('Estado da execução',r=>r.status);textRow('Revisão científica',r=>r.review_status);textRow('Snapshot do pacote',r=>sourceFor(r._sourceId)?.snapshot_id||'Não informado');
  for(const group of groups.values()){const tr=element('tr'),name=element('th',group.name);name.scope='row';name.append(element('small',[group.id,group.type,group.unit||'sem unidade'].join(' · ')));tr.append(name);for(const run of runs){const values=group.values.get(run._key),cell=element('td');if(!values)cell.textContent='Ausente / incompatível';else for(const metric of values){cell.append(element('div',metricText(metric)),element('small','Precisão declarada: '+precisionText(metric)));if(values.length>1)cell.append(element('small',metric.id));}tr.append(cell);}body.append(tr);}
  if(!groups.size)textRow('Métricas',()=> 'Nenhuma métrica declarada');
  textRow('Parâmetros',r=>r.parameters.length?r.parameters.map(p=>`${p.name}: ${metricText(p)} · ${p.type||'tipo não informado'} · precisão ${precisionText(p)}`).join('\n'):'Nenhum parâmetro declarado');
  textRow('Datas declaradas / origem',r=>`Início: ${display(r.started_at)}\nFim: ${display(r.ended_at)}\nOrigem: ${r.timestamp_origin}`);
  textRow('Entradas declaradas',r=>r.inputs?.length?r.inputs.join('\n'):'Nenhuma entrada declarada');textRow('Saídas declaradas',r=>r.outputs?.length?r.outputs.join('\n'):'Nenhuma saída declarada');
  textRow('Derivado de',r=>r.derived_from?.length?r.derived_from.join('\n'):'Nenhuma derivação declarada');
  textRow('Referências relacionadas (menções neutras)',r=>r.related_references?.length?r.related_references.map(x=>`${x.name||x.id} [${x.id}] · ${x.availability?.status||'UNVERIFIED'}`).join('\n'):'Nenhuma referência relacionada declarada');
  textRow('Artefatos / disponibilidade',r=>r.artifacts.length?r.artifacts.map(a=>`${a.name} [${a.id}] · ${a.availability?.status||'UNVERIFIED'}`).join('\n'):'Nenhum artefato vinculado');
  table.append(body);box.append(table);host.append(box,element('p','Seleção explícita no snapshot atual, inclusive registros fora dos filtros. Sem ranking, conversão, causalidade ou aprovação inferidos. Abra cada detalhe para metadados completos.','muted'));
}
function renderTimeline(){
  clear('timeline-content');const runs=navigation.sortRuns(filteredRuns(),'time-asc');
  for(const run of runs){const item=element('li'),label=run.timestamp_origin==='OBSERVED'?'Data observada declarada (não é data do evento): ':'Início declarado: ';item.append(element('time',run.started_at?label+run.started_at:run.ended_at?'Sem início declarado':'Sem data declarada'),runLink(run));if(run.ended_at)item.append(element('time',(run.timestamp_origin==='OBSERVED'?'Fim observado declarado (não é data do evento): ':'Fim declarado: ')+run.ended_at));const meta=element('div','', 'metadata');meta.append(badge(run.status),badge('Revisão: '+run.review_status,run.review_status),element('small','Origem temporal: '+run.timestamp_origin,'muted'));item.append(meta,element('small',run._sourceName,'muted'));$('timeline-content').append(item);}
  if(!runs.length)$('timeline-content').append(element('li','Nenhuma execução nesta seleção. Ajuste os filtros em Explorar.'));
}
function renderLineage(){
  clear('lineage-content');const host=$('lineage-content'),box=tableRegion('Relações declaradas, direção e fonte'),table=element('table'),head=element('thead'),header=element('tr');
  for(const text of ['Origem','Relação','Destino','Fonte']){const th=element('th',text);th.scope='col';header.append(th);}head.append(header);table.append(head);const body=element('tbody');let count=0;const connected=new Set();
  for(const source of state.catalog.sources)for(const relation of source.read_model?.relations||[]){const row=element('tr'),origin=element('td'),target=element('td');origin.append(entityLink(source.id,relation.source));target.append(entityLink(source.id,relation.target));const kind=element('td');kind.append(element('span',{input:'entrada de',output:'produziu',derived_from:'derivado de'}[relation.kind]||relation.kind,'relation'));const sourceCell=element('td',source.name);sourceCell.append(sourceLink(source.id));row.append(origin,kind,target,sourceCell);body.append(row);connected.add(key(source.id,relation.source));connected.add(key(source.id,relation.target));count++;}
  table.append(body);box.append(table);host.append(count?box:element('div','Nenhuma relação declarada nas fontes abertas.','empty'));
  const isolated=state.runs.filter(run=>!connected.has(run._key));host.append(element('h3','Execuções sem relações declaradas'));
  if(!isolated.length)host.append(element('p','Todas as execuções carregadas participam de alguma relação declarada.','muted'));else{const list=element('ul','', 'entity-list');for(const run of isolated){const item=element('li');item.append(runLink(run),element('small',run._sourceName));list.append(item);}host.append(list);}
}
function renderSources(){
  const expandedMetadata=new Set([...document.querySelectorAll('details[data-p03-metadata-context]')].filter(node=>node.open).map(node=>node.dataset.p03MetadataContext));
  clear('sources-content');for(const source of state.catalog.sources){const card=element('article','', 'panel source-card');card.id='card-'+source.id;card.tabIndex=-1;card.append(element('h3',source.name),badge(source.status));const dl=element('dl');
    for(const [label,value] of [['Fonte no conjunto aberto',source.id],['Snapshot do pacote',source.snapshot_id],['Perfil',source.version],['Sintaxe / semântica do perfil',source.report.valid?'Conforme ao candidato':'Não conforme'],['Autenticidade',source.authenticity],['Aprovação científica',source.scientific_approval],['Integridade de metadados',source.metadata_sha256],['Execuções carregadas',source.read_model?source.read_model.runs.length:'Não informado — fonte não indexada'],['População da fonte inteira',source.coverage?.source],['Total elegível na origem',source.coverage?.eligible],['Selecionados pelo produtor',source.coverage?.selected],['Convertidos pelo produtor',source.coverage?.converted]])addDefinition(dl,label,value);
    card.append(dl,element('p','O pacote aberto pode ser um recorte. Carregados descreve apenas o que esta interface leu; cobertura da fonte inteira e etapas do produtor não foram informadas pelo contrato.','muted'));
    if(source.changed)card.append(element('p',source.change_message,'compare-note'));const issues=[...(source.report.errors||[]),...(source.report.warnings||[])],details=element('details');details.append(element('summary',`${issues.length} erro(s) ou aviso(s)`));for(const issue of issues)details.append(element('p',`${issue.code}: ${issue.message} (${issue.path||issue.entity_id||''})`));card.append(details,element('p','Uma validação positiva não certifica resultados ou autenticidade.','muted'));
    const metadata=element('details'),metadataSummary=element('summary','Metadados declarados e observações do leitor');metadataSummary.id='p03-metadata-summary-'+source.id;metadata.dataset.p03MetadataContext=JSON.stringify([state.catalog.snapshot_id,source.id,source.snapshot_id]);metadata.open=Boolean(source.presentation?.errors?.length)||expandedMetadata.has(metadata.dataset.p03MetadataContext);metadata.append(metadataSummary,renderP03Metadata(document,source));card.append(metadata);$('sources-content').append(card);
  }if(!state.catalog.sources.length)$('sources-content').append(element('div','Nenhuma fonte declarada.','empty'));
}
function renderDossier(){$('dossier-summary').textContent=`${state.catalog.sources.length} fonte(s) · ${state.runs.length} execução(ões) carregadas · índice observado em ${state.catalog.indexed_at}. Exportação inclui todos os registros carregados, independentemente dos filtros da tela.`;clear('limitations');for(const text of state.catalog.limitations)$('limitations').append(element('li',text));}
function renderRoute(){
  for(const node of document.querySelectorAll('.view'))node.hidden=node.id!=='view-'+state.view;
  for(const button of document.querySelectorAll('.nav-button')){const active=button.dataset.view===state.view;button.classList.toggle('active',active);if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');}
  renderRuns();renderComparison();renderTimeline();renderLineage();renderDetail();
}
let loadPending=false;
async function load(reindex=false){if(loadPending)return;loadPending=true;$('refresh').disabled=true;try{const response=await fetch(reindex?'/api/reindex':'/api/catalog',reindex?{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}:{});if(!response.ok)throw new Error('Falha local HTTP '+response.status);updateCatalog(await response.json());}catch(error){announce('Não foi possível consultar o Atlas: '+error.message,true);}finally{loadPending=false;$('refresh').disabled=false;}}
for(const button of document.querySelectorAll('.nav-button'))button.addEventListener('click',()=>showView(button.dataset.view));
for(const [field,id] of Object.entries(filterControls))$(id).addEventListener(id==='search'?'input':'change',()=>{commitRoute({...route(),filters:{...state.filters,[field]:$(id).value}});});
$('filters').addEventListener('submit',event=>event.preventDefault());
$('clear-filters').addEventListener('click',()=>commitRoute({...route(),filters:navigation.defaults().filters}));
$('clear-selection').addEventListener('click',()=>commitRoute({...route(),selected:[]}));
$('compare-selected').addEventListener('click',()=>showView('compare'));
$('close-detail').addEventListener('click',closeDetail);
$('detail').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();closeDetail();}});
$('refresh').addEventListener('click',()=>load(true));
$('print-view').addEventListener('click',()=>window.print());
$('download-dossier').addEventListener('click',async()=>{try{const response=await fetch('/api/dossier');if(!response.ok)throw new Error('HTTP '+response.status);const blob=await response.blob(),url=URL.createObjectURL(blob),anchor=element('a');anchor.href=url;anchor.download='atlas-dossie-derivado.json';document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);announce('Dossiê derivado exportado com todos os registros carregados, fontes e limitações.');}catch(error){announce('Não foi possível exportar: '+error.message,true);}});
document.querySelector('.skip').addEventListener('click',event=>{event.preventDefault();$('main').focus();});
window.addEventListener('popstate',routeFromLocation);window.addEventListener('hashchange',routeFromLocation);
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&state.catalog)load(false);});
load();
