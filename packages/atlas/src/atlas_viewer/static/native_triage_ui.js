/** Feature 005: trusted DOM only. Session decisions never mutate source DTOs. */
import {createTriageModel, SelectionLedger, selectionKey, TRIAGE_DIMENSIONS} from './native_triage_model.js';
import {buildRetentionPlan, buildDossier, copyReferences, RETENTION_INTENTS} from './native_retention.js';
import {literalText} from './native_legacy_model.js';

const $ = id => document.getElementById(id);
const element = (tag, text, cls='') => {
  const node=document.createElement(tag);
  if(text!==undefined) node.textContent=String(text);
  if(cls) node.className=cls;
  return node;
};
const button = (text, run, id) => {
  const node=element('button',text);node.type='button';
  if(id)node.id=id;
  node.addEventListener('click',run);return node;
};
const FILTER_IDS=Object.freeze({family:'native-family',kind:'native-kind',execution:'native-execution',
  result_group:'native-status',publication:'native-publication',admission:'native-admission',
  review:'native-review',documentary:'native-documentary',baseline:'native-baseline',evidence:'native-evidence'});
const INTENT_LABELS=Object.freeze({KEEP_FULL:'Preservar integralmente',KEEP_ESSENTIALS:'Propor preservação essencial',
  REVIEW_FOR_REMOVAL:'Revisar possibilidade de descarte',UNDECIDED:'Ainda não decidido'});
const TYPE_EXPERIMENTS=new Set(['experiment','execution','run','attempt']);

export class NativeTriageUI {
  constructor(hooks){
    this.hooks=hooks;this.source=null;this.model=createTriageModel({entries:[]});
    this.ledger=new SelectionLedger({entries:[]});this.mode='list';this.page=0;this.filtered=[];
    this.initSidebar();
    $('native-search-all').addEventListener('click',()=>hooks.navigate('search'));
    $('native-select-visible').addEventListener('click',()=>{this.ledger.selectMany(this.visibleEntries());this.selectionChanged();});
    $('native-select-filtered').addEventListener('click',()=>{this.ledger.selectMany(this.filtered);this.selectionChanged();});
    $('native-clear-batch').addEventListener('click',()=>{this.ledger.clear();this.selectionChanged();});
    for(const[id,mode]of [['native-compare','compare'],['native-batch-details','details'],['native-batch-links','links'],['native-dossier','dossier']]){
      $(id).addEventListener('click',()=>{this.mode=mode;this.page=0;hooks.navigate('selected');});
    }
    $('native-retention').addEventListener('click',()=>{this.page=0;hooks.navigate('retention');});
    $('native-copy-references').addEventListener('click',()=>this.copySelectedReferences());
    for(const id of Object.values(FILTER_IDS).concat(['native-from','native-to']))$(id).addEventListener('change',()=>hooks.filterChanged());
    this.scrollScheduled=false;
    window.addEventListener('scroll',()=>{
      if(this.scrollScheduled)return;this.scrollScheduled=true;
      requestAnimationFrame(()=>{this.scrollScheduled=false;this.syncBatch();});
    },{passive:true});
  }
  bindSource(source){
    const ready=source?.status==='READY';
    this.source=source?{...source,entries:ready?source.entries:[]}:{entries:[]};
    const hadSessionState=this.ledger.size>0||this.ledger.annotations.size>0||this.ledger.intents.size>0;
    const changed=this.ledger.bind(this.source);
    if(!ready){this.ledger.clear();this.ledger.annotations.clear();this.ledger.intents.clear();}
    this.model=createTriageModel(this.source,this.hooks.presentation());this.page=0;this.mode='list';
    this.resetFilters();this.filterOptions(false);
    this.invalidated=changed.invalidated&&hadSessionState;
    return this.invalidated;
  }
  filters(){
    const result={query:$('native-search').value,from:$('native-from').value,to:$('native-to').value};
    for(const[dimension,id]of Object.entries(FILTER_IDS))result[dimension]=$(id).value;
    return result;
  }
  matches(entry){return this.model.matches(entry,this.filters(),this.ledger.annotations);}
  hits(){return this.model.search(this.filters(),this.ledger.annotations);}
  filterOptions(preserve=true,contextEntries=null){
    for(const[dimension,id]of Object.entries(FILTER_IDS)){
      const select=$(id),old=preserve?select.value:'',oldLabel=select.selectedOptions[0]?.textContent;
      let values=this.model.options(dimension,this.ledger.annotations);
      if(dimension==='family'&&contextEntries){const keys=new Set(contextEntries.map(e=>this.model.facet(e,dimension).key));values=values.filter(f=>keys.has(f.key));}
      select.replaceChildren();const all=element('option','Todos');all.value='';select.append(all);
      for(const value of values){const option=element('option',value.label);option.value=value.key;
        if(value.raw!==undefined)option.dataset.raw=value.raw;
        if(value.type!==undefined)option.dataset.valueType=value.type;
        select.append(option);
      }
      if(old&&!values.some(value=>value.key===old)){const stale=element('option',(oldLabel||'Valor anterior')+' · fora do contexto');stale.value=old;select.append(stale);}
      select.value=old;
    }
  }
  restoreFilters(filters){
    $('native-search').value=filters.query||'';$('native-from').value=filters.from||'';$('native-to').value=filters.to||'';
    for(const [dimension,id]of Object.entries(FILTER_IDS)){
      const value=filters[dimension]||'',select=$(id);
      if(value&&![...select.options].some(o=>o.value===value)){const match=this.model.options(dimension,this.ledger.annotations).find(o=>o.key===value),option=element('option',match?.label||'Valor do contexto anterior');option.value=value;select.append(option);}
      select.value=value;
    }
  }
  resetFilters(){
    for(const id of Object.values(FILTER_IDS).concat(['native-search','native-from','native-to']))$(id).value='';
    this.page=0;
  }
  renderFilterChips(){
    const host=$('native-filter-chips');host.replaceChildren();
    const labels=new Map(TRIAGE_DIMENSIONS.map(d=>[d.id,d.label]));
    const active=[];
    const add=(label,value,remove)=>{active.push(label+': '+value);const chip=button(label+': '+value+' ×',remove);chip.className='triage-chip';chip.setAttribute('aria-label','Remover filtro '+label+': '+value);host.append(chip);};
    if($('native-search').value.trim())add('Busca',$('native-search').value.trim(),()=>{$('native-search').value='';this.hooks.filterChanged();$('native-search').focus();});
    for(const[dimension,id]of Object.entries(FILTER_IDS))if($(id).value)add(labels.get(dimension)||dimension,$(id).selectedOptions[0]?.textContent||'Valor selecionado',()=>{$(id).value='';this.hooks.filterChanged();$('native-clear').focus();});
    for(const[id,label]of [['native-from','Desde'],['native-to','Até']])if($(id).value)add(label,$(id).value,()=>{$(id).value='';this.hooks.filterChanged();$('native-clear').focus();});
    for(const[key,value]of Object.entries(this.hooks.tableFilters?.()||{}))if(value)add('Tabela · '+key,'ativo',()=>{this.hooks.removeTableFilter(key);$('native-clear').focus();});
    $('native-filter-count').textContent=active.length?'· '+active.length+' ativos':'';
    $('native-clear').disabled=!active.length;
    $('native-selection').textContent=active.length?active.join(' · '):'Todas as ocorrências da revisão selecionada';
    $('native-selection').hidden=!active.length;
    return active;
  }
  initSidebar(){
    const sidebar=$('native-sidebar'),toggle=$('native-menu-toggle'),close=$('native-nav-close'),backdrop=$('native-nav-backdrop');
    const mobile=matchMedia('(max-width:720px)'),wide=matchMedia('(min-width:1200px)');
    this.navState={wide:true,medium:false,mobile:false};
    this.navBand=()=>mobile.matches?'mobile':wide.matches?'wide':'medium';
    this.applySidebar=(returnFocus=false)=>{
      const temporary=mobile.matches,open=this.navState[this.navBand()];
      if(!open&&sidebar.contains(document.activeElement))returnFocus=true;
      sidebar.hidden=!open;backdrop.hidden=!(temporary&&open);
      document.body.classList.toggle('triage-nav-open',open);
      toggle.setAttribute('aria-expanded',String(open));
      toggle.textContent=temporary?'Menu':open?'Recolher navegação':'Expandir navegação';
      $('native-main').inert=temporary&&open;document.querySelector('.topbar').inert=temporary&&open;
      if(temporary&&open){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');sidebar.tabIndex=-1;}
      else{sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');sidebar.removeAttribute('tabindex');}
      if(returnFocus)toggle.focus();
    };
    this.closeSidebar=(returnFocus=true)=>{this.navState[this.navBand()]=false;this.applySidebar(returnFocus);};
    toggle.addEventListener('click',()=>{const band=this.navBand();this.navState[band]=!this.navState[band];this.applySidebar();if(mobile.matches&&this.navState[band])close.focus();});
    close.addEventListener('click',()=>this.closeSidebar());backdrop.addEventListener('click',()=>this.closeSidebar());
    sidebar.addEventListener('keydown',event=>{
      if(event.key==='Escape'){event.preventDefault();event.stopPropagation();this.closeSidebar();return;}
      if(event.key!=='Tab'||!mobile.matches)return;
      const nodes=[...sidebar.querySelectorAll('button,a,summary,[tabindex="0"]')].filter(n=>!n.disabled&&n.getClientRects().length);
      const first=nodes[0],last=nodes.at(-1);
      if(event.shiftKey&&(document.activeElement===first||document.activeElement===sidebar)){event.preventDefault();last?.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
    });
    mobile.addEventListener('change',()=>{this.navState.mobile=false;this.applySidebar(true);});
    wide.addEventListener('change',()=>this.applySidebar());
    this.applySidebar();
  }
  afterNavigation(){
    if(this.navBand()==='mobile')this.closeSidebar(false);
    const heading=$('native-content').querySelector('h2');
    if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
  }
  checkControl(entry,label='Selecionar'){
    const wrapper=element('label',undefined,'triage-check'),input=element('input');input.type='checkbox';input.dataset.batchUid=entry.uid;
    input.checked=this.ledger.has(entry);input.setAttribute('aria-label','Selecionar '+entry.title+' · '+this.model.type(entry).label);
    wrapper.append(input,element('span',label));
    input.addEventListener('click',event=>event.stopPropagation());
    input.addEventListener('keydown',event=>event.stopPropagation());
    input.addEventListener('change',()=>this.toggle(entry));return wrapper;
  }
  decorate(){
    for(const node of $('native-content').querySelectorAll('tr[data-uid],li[data-uid],article[data-uid],details[data-uid]')){
      const entry=this.model.byUid.get(node.dataset.uid);if(!entry||node.querySelector('[data-batch-uid]'))continue;
      const host=node.tagName==='TR'?node.firstElementChild:node;
      if(host)host.prepend(this.checkControl(entry));
    }
  }
  visibleEntries(){
    const result=new Map(),content=$('native-content');
    for(const node of content.querySelectorAll('[data-batch-uid]')){
      if(!node.getClientRects().length)continue;
      const entry=this.model.byUid.get(node.dataset.batchUid);if(!entry)continue;
      if(node.namespaceURI==='http://www.w3.org/2000/svg'){
        const rect=node.getBoundingClientRect(),map=node.closest('svg')?.getBoundingClientRect();
        if(!map||rect.right<=map.left||rect.left>=map.right||rect.bottom<=map.top||rect.top>=map.bottom)continue;
      }
      result.set(entry.uid,entry);
    }
    return [...result.values()];
  }
  afterRender(filteredEntries){
    this.filtered=filteredEntries;this.decorate();this.renderFilterChips();this.syncBatch();
  }
  navigationCounts(){
    const items=this.model.items;
    return {search:items.length,
      experiments:items.filter(e=>e.kind==='record'&&TYPE_EXPERIMENTS.has(this.model.type(e).key)).length,
      baselines:items.filter(e=>this.model.baseline(e,this.ledger.annotations).confirmed).length,
      selected:this.ledger.size,retention:this.ledger.size};
  }
  syncBatch(){
    const selected=this.ledger.entries();
    for(const node of document.querySelectorAll('[data-batch-uid]')){
      const entry=this.model.byUid.get(node.dataset.batchUid),checked=!!entry&&this.ledger.has(entry);
      if(node.tagName==='INPUT')node.checked=checked;
      else{node.setAttribute('aria-checked',String(checked));const mark=node.querySelector('text');if(mark)mark.textContent=checked?'✓':'';}
    }
    for(const node of $('native-content').querySelectorAll('[data-result-uid]'))node.dataset.batchSelected=String(this.ledger.has(this.model.byUid.get(node.dataset.resultUid)));
    const visible=this.visibleEntries(),filtered=this.hits().map(hit=>hit.entry);
    const visibleSet=new Set(visible.map(e=>e.uid)),filteredSet=new Set(filtered.map(e=>e.uid));
    const visibleCount=selected.filter(e=>visibleSet.has(e.uid)).length,hidden=selected.filter(e=>!filteredSet.has(e.uid)).length;
    const kinds=[...new Set(selected.map(e=>this.model.type(e).label))].join(', ');
    const summary=$('native-batch-summary');summary.dataset.selectedCount=String(selected.length);summary.dataset.visibleCount=String(visibleCount);summary.dataset.hiddenCount=String(hidden);
    summary.textContent=`${selected.length} selecionado(s) · ${visibleCount} visíveis · ${hidden} ocultos pelo filtro · ${kinds} · Revisão: ${this.source?.revision??'não declarada'}`;
    $('native-batch-bar').hidden=!selected.length;
    const visibleButton=$('native-select-visible'),allButton=$('native-select-filtered');
    visibleButton.textContent=`Selecionar visíveis (${visible.length})`;visibleButton.disabled=!visible.length;
    allButton.textContent=`Selecionar todos os resultados filtrados (${this.filtered.length})`;allButton.disabled=!this.filtered.length;
    for(const id of ['native-compare','native-retention','native-batch-details','native-copy-references','native-batch-links','native-dossier']){
      const node=$(id);node.dataset.batchCount=String(selected.length);node.setAttribute('aria-label',node.textContent+' · '+selected.length+' itens');
    }
    for(const [pane,count]of Object.entries(this.navigationCounts())){
      const nav=document.querySelector(`[data-pane="${pane}"]`);const badge=nav?.querySelector('.application-nav-count');if(badge)badge.textContent=String(count);
    }
  }
  refreshSnapshotNotice(){
    if(this.invalidated){this.hooks.message('A fonte ou revisão mudou. A seleção, as anotações e as intenções anteriores foram invalidadas; forme um novo lote.');this.invalidated=false;}
  }
  selectionChanged(){
    if(!['selected','retention'].includes(this.hooks.pane())){this.syncBatch();return;}
    const active=document.activeElement,uid=active?.dataset?.batchUid,id=active?.id;
    this.hooks.refresh();
    const same=id?$(id):[...$('native-content').querySelectorAll('[data-batch-uid]')].find(n=>n.dataset.batchUid===uid);
    if(same&&!same.disabled&&same.getClientRects().length){same.focus({preventScroll:true});return;}
    const fallback=$('native-content').querySelector('[data-batch-uid],h2');
    if(fallback){if(fallback.tagName==='H2')fallback.tabIndex=-1;fallback.focus({preventScroll:true});}
  }
  toggle(entry){this.ledger.toggle(entry);this.selectionChanged();}
  addDetailControls(host,entry){
    host.prepend(this.checkControl(entry,'Incluir no lote'));
    const designation=this.model.baseline(entry,this.ledger.annotations),section=element('section',undefined,'triage-annotation');
    section.append(element('h3','Designação de baseline'),element('p',designation.label));
    if(designation.reference)section.append(element('p','Referência a baseline declarada; não designa este item como baseline.'));
    const label=element('label','Motivo da anotação do operador (somente sessão)'),input=element('input');input.type='text';input.maxLength=1000;input.placeholder='Referência ou justificativa verificável';label.append(input);section.append(label);
    const remove=button('Remover anotação de sessão',()=>{
      this.ledger.removeAnnotation(entry);this.filterOptions();this.hooks.refresh();
      section.querySelector('p').textContent=this.model.baseline(entry,this.ledger.annotations).label;
      remove.hidden=true;input.focus();
      this.hooks.message('Anotação de sessão removida; os resultados e o lote disponível refletem a designação atual.');
    });
    remove.hidden=!this.ledger.annotations.has(selectionKey(this.source,entry));
    section.append(button('Anotar baseline nesta sessão',()=>{
      if(!input.value.trim()){input.setCustomValidity('Informe a justificativa da designação.');input.reportValidity();return;}
      input.setCustomValidity('');this.ledger.annotateBaseline(entry,input.value.trim());
      this.filterOptions();this.hooks.refresh();this.hooks.message('Baseline anotada pelo operador nesta fonte/revisão; a fonte original permanece intacta.');
      const status=section.querySelector('p');status.textContent=this.model.baseline(entry,this.ledger.annotations).label;
      remove.hidden=false;
      this.syncBatch();
    }));
    input.addEventListener('input',()=>input.setCustomValidity(''));
    section.append(remove);
    host.append(section);
  }
  pageRows(host,rows,draw,pageSize=40){
    const pages=Math.max(1,Math.ceil(rows.length/pageSize));this.page=Math.min(this.page,pages-1);
    const controls=element('div',undefined,'pager');
    const changePage=(delta)=>{
      this.page+=delta;this.hooks.refresh();
      const pager=$('native-content').querySelector('.pager');
      const target=pager?.querySelector(delta>0?'[data-page-next]':'[data-page-prev]');
      (target&&!target.disabled?target:pager?.querySelector('button:not(:disabled)'))?.focus();
    };
    const prev=button('← Anterior',()=>changePage(-1)),next=button('Próxima →',()=>changePage(1));
    prev.dataset.pagePrev='true';next.dataset.pageNext='true';
    prev.disabled=this.page===0;next.disabled=this.page+1>=pages;
    controls.append(prev,element('span',`Página ${this.page+1}/${pages} · ${rows.length} resultados`),next);host.append(controls);
    const list=element('div',undefined,'triage-result-list');for(const item of rows.slice(this.page*pageSize,(this.page+1)*pageSize))list.append(draw(item));host.append(list);
    return rows;
  }
  resultCard(entry,hit=null){
    const type=this.model.type(entry),card=element('article',undefined,'triage-result');card.dataset.resultUid=entry.uid;card.dataset.resultType=type.key;card.dataset.uid=entry.uid;
    card.append(element('p',type.label,'triage-type'));
    const head=element('div',undefined,'triage-result-head'),title=element('h3');title.append(button(entry.title,()=>this.hooks.detail(entry)));
    head.append(this.checkControl(entry,''),title);card.append(head);
    const execution=this.model.facet(entry,'execution');
    if(entry.kind==='record')card.append(element('p','Execução: '+execution.label,'muted'));
    else if(entry.kind==='table')card.append(element('p',`${entry.row_count} linhas declaradas · uma tabela não é uma execução.`, 'muted'));
    const baseline=this.model.baseline(entry,this.ledger.annotations);card.append(element('p','Baseline: '+baseline.label,'muted'));
    if(hit?.reasons?.length){const reason=element('p',hit.reasons.map(r=>(r.label||r.field)+': '+r.value).join(' · '),'triage-match');reason.dataset.matchReason='true';card.append(reason);}
    const identity=element('details');identity.append(element('summary','Identidade e origem'),element('p',`${type.label} · UID ${entry.uid} · Fonte ${this.source?.id??'não declarada'} · Revisão ${this.source?.revision??'não declarada'}`,'muted'));card.append(identity);
    const actions=element('div',undefined,'triage-result-actions');actions.append(button('Ver detalhes',()=>this.hooks.detail(entry)));
    const locate=button('Localizar na árvore',()=>this.hooks.locate(entry));locate.dataset.locateUid=entry.uid;actions.append(locate);card.append(actions);
    return card;
  }
  renderPane(host,pane){
    if(!['overview','search','experiments','baselines','selected','retention'].includes(pane))return null;
    if(pane==='overview'){
      host.append(element('h2','Visão geral desta revisão'),element('p','Escolha uma área ou pesquise uma identidade. A tabela, o experimento e a execução conservam sua natureza.','muted'));
      const metrics=element('div',undefined,'triage-metrics');
      for(const[label,count,destination]of [['Registros',this.model.items.filter(e=>e.kind==='record').length,'records'],['Tabelas',this.model.items.filter(e=>e.kind==='table').length,'tables'],['Baselines designadas',this.model.items.filter(e=>this.model.baseline(e,this.ledger.annotations).confirmed).length,'baselines'],['No lote',this.ledger.entries().length,'selected']]){
        const card=element('section',undefined,'triage-metric');card.append(element('strong',count),element('span',label),button('Explorar '+label.toLowerCase(),()=>this.hooks.navigate(destination)));metrics.append(card);
      }host.append(metrics);return [];
    }
    if(pane==='retention'){this.renderPlan(host);return this.ledger.entries();}
    if(pane==='selected'){this.renderSelected(host);return this.ledger.entries();}
    const labels={search:'Busca global — resultados tipados',experiments:'Experimentos e execuções declarados',baselines:'Baselines com designação explícita'};
    host.append(element('h2',labels[pane]));
    let hits=this.hits();
    if(pane==='experiments')hits=hits.filter(hit=>hit.entry.kind==='record'&&TYPE_EXPERIMENTS.has(hit.type));
    if(pane==='baselines')hits=hits.filter(hit=>hit.baseline.confirmed);
    host.append(element('p',`${hits.length} resultados de ${this.model.items.length} ocorrências nesta fonte/revisão.`, 'application-population'));
    if(pane==='baselines')host.append(element('p','Somente declaração explícita da fonte ou anotação do operador. “baseline” no título não comprova designação. Para encontrar a tabela M1.1, use Busca global.','notice'));
    if(pane==='experiments')host.append(element('p','Missões, marcos, tabelas e produtos continuam nas suas áreas. Não recebem classificação experimental por título ou publicação.','muted'));
    if(!hits.length){
      const diagnostic=this.model.diagnose(this.filters(),this.ledger.annotations);
      host.append(element('p','Nenhum resultado correspondente nesta revisão. Não encontrado no snapshot ou tipo de registro não correspondente aos filtros.','empty'));
      const details=element('details');details.append(element('summary','Diagnóstico da busca e campos ausentes'),element('pre',JSON.stringify(diagnostic,null,2)));host.append(details);
    }else this.pageRows(host,hits,hit=>this.resultCard(hit.entry,hit));
    return hits.map(hit=>hit.entry);
  }
  renderSelected(host){
    const selected=this.ledger.entries();host.append(element('h2',this.mode==='compare'?'Comparar selecionados':this.mode==='dossier'?'Dossiê dos selecionados':this.mode==='links'?'Vínculos declarados dos selecionados':'Selecionados'));
    host.append(element('p',`${selected.length} itens do lote explícito. Filtros não removem itens deste conjunto.`, 'muted'));
    if(!selected.length){host.append(element('p','Nenhum item selecionado. Marque registros na árvore, nas listas ou na busca.','empty'));return;}
    const modes=element('div',undefined,'toolbar');for(const[key,label]of [['list','Lista'],['compare','Comparar'],['details','Detalhes'],['links','Vínculos'],['dossier','Dossiê']]){const b=button(label,()=>{this.mode=key;this.page=0;this.hooks.refresh();});if(key===this.mode)b.setAttribute('aria-current','true');modes.append(b);}host.append(modes);
    if(this.mode==='dossier'){
      const dossier=buildDossier(this.source,selected,{annotations:this.ledger.annotations,intents:this.ledger.intents});
      host.append(element('p','Dossiê derivado da seleção, com lacunas explícitas. Um resumo não comprova preservação dos artefatos.','notice'),button('Exportar dossiê JSON',()=>{
        const current=buildDossier(this.source,this.ledger.entries(),{annotations:this.ledger.annotations,intents:this.ledger.intents});
        this.hooks.download('atlas-triage-dossier.json',JSON.stringify(current,null,2));
      },'native-export-dossier'));
      this.pageRows(host,dossier.items,item=>this.planCard(item,false));return;
    }
    if(this.mode==='compare'){
      const wrap=element('div',undefined,'triage-compare');wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Comparação; role horizontalmente para todos os campos');
      const table=element('table'),head=element('thead'),tr=element('tr');for(const name of ['Identidade / título','Tipo / família','Execução','Publicação / admissão / revisão','Baseline','Referências']){const th=element('th',name);th.scope='col';tr.append(th);}head.append(tr);table.append(head);
      const body=element('tbody');
      this.pageRows(host,selected,entry=>{const row=element('tr');row.dataset.uid=entry.uid;
        const title=element('td');title.append(this.checkControl(entry),button(entry.title,()=>this.hooks.detail(entry)),element('code',entry.uid));row.append(title);
        row.append(element('td',this.model.type(entry).label+'\n'+this.model.facet(entry,'family').label),element('td',this.model.facet(entry,'execution').label));
        row.append(element('td',['publication','admission','review'].map(key=>key+': '+this.model.facet(entry,key).label).join('\n')),element('td',this.model.baseline(entry,this.ledger.annotations).label));
        const refs=element('td');refs.append(button('Ver referências declaradas',()=>this.hooks.detail(entry)));row.append(refs);body.append(row);return element('span');});
      // The pager above controls the same 40-item comparison window.
      const placeholders=host.querySelector('.triage-result-list');placeholders?.remove();table.append(body);wrap.append(table);host.append(wrap);return;
    }
    this.pageRows(host,selected,entry=>{
      const card=this.resultCard(entry);
      if(this.mode==='details'){const values=element('details');values.append(element('summary','Campos originais (JSON exato)'),element('pre',entry.raw_json));card.append(values);}
      if(this.mode==='links'){
        const nav=this.hooks.navigation(),refs=nav.outgoing.get(entry.uid)||[];const section=element('section');section.append(element('h4','Referências nesta fonte/revisão'));
        if(!refs.length)section.append(element('p','Vínculo não comprovado: nenhuma referência declarada nesta revisão.','muted'));
        for(const ref of refs){const row=element('p',`${ref.label}: ${String(ref.literal)} · ${ref.resolution}`);if(ref.resolution==='UNIQUE'){const target=this.model.byUid.get(ref.targets[0]);if(target)row.append(button('Abrir '+target.title,()=>this.hooks.openOccurrence(target.uid)));}section.append(row);}card.append(section);
      }return card;
    });
  }
  planCard(item,editable=true){
    const entry=this.model.byUid.get(item.identity.uid),card=this.resultCard(entry);
    const protection=item.protection;card.append(element('p','Protegido · exclusão não autorizada. '+(protection.reasons||[]).join(' · '),'triage-protection'));
    const label=element('label','Intenção do operador — proposta, não comando','triage-plan-intent');
    if(editable){const select=element('select');select.dataset.intentUid=entry.uid;
      for(const key of RETENTION_INTENTS){const option=element('option',key+' — '+INTENT_LABELS[key]);option.value=key;select.append(option);}select.value=item.intent;
      select.addEventListener('change',()=>{this.ledger.setIntent(entry,select.value);this.hooks.message('Intenção atualizada somente na proposta. DELETE_AUTHORIZED=NO.');});label.append(select);
    }else label.append(element('p',item.intent));card.append(label);
    card.append(element('p','Espaço físico: A medir no ambiente LOCAL','muted'));
    const gaps=element('details');gaps.append(element('summary',`Lacunas de informação (${item.gaps.length})`),element('pre',JSON.stringify(item.gaps,null,2)));card.append(gaps);
    const declared=element('details');declared.append(element('summary','Configurações, código, resultados, métricas, limitações e artefatos declarados'),element('pre',JSON.stringify(item.declared,null,2)));card.append(declared);
    const original=element('details');original.append(element('summary','JSON original exato'),element('pre',item.raw_json));card.append(original);return card;
  }
  renderPlan(host){
    const entries=this.ledger.entries();host.append(element('h2','Plano de retenção — prévia da proposta'),element('p',`${entries.length} itens selecionados · PROPOSAL_ONLY · DELETE_AUTHORIZED=NO`, 'notice'));
    host.append(element('p','Nenhum arquivo será apagado, movido ou aberto. A execução futura depende de inventário LOCAL, dependências, dossiê preservado, backup/política, medição e autorização humana específica.','muted'));
    if(!entries.length){host.append(element('p','Selecione itens para preparar a proposta.','empty'));return;}
    const plan=()=>buildRetentionPlan(this.source,this.ledger.entries(),{annotations:this.ledger.annotations,intents:this.ledger.intents});
    host.append(button('Exportar plano JSON · '+entries.length+' itens',()=>this.hooks.download('atlas-retention-plan.json',JSON.stringify(plan(),null,2)),'native-export-plan'));
    this.pageRows(host,plan().items,item=>this.planCard(item));
  }
  async copySelectedReferences(){
    const value=copyReferences(this.source,this.ledger.entries());const text=typeof value==='string'?value:JSON.stringify(value,null,2);
    try{if(!navigator.clipboard?.writeText)throw Error('CLIPBOARD_UNAVAILABLE');await navigator.clipboard.writeText(text);this.hooks.message(`Referências de ${this.ledger.entries().length} itens copiadas.`);}
    catch{
      this.mode='list';this.hooks.navigate('selected');
      const label=element('label','Referências para copiar manualmente'),area=element('textarea');area.className='triage-reference-copy';area.readOnly=true;area.value=text;label.append(area);$('native-content').prepend(label);area.focus();area.select();this.hooks.message('Cópia automática indisponível; referências selecionadas para copiar.');
    }
  }
}
