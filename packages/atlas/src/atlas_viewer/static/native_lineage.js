/* A consultative graph of declared relation occurrences, never inferred science.
 * Endpoint values come from independently verified lexical fields, not a
 * JSON.parse/Number round trip. Ambiguous references stay ambiguous.
 */
import {declaredSourceAliases} from './native_navigation.js';
const NS='http://www.w3.org/2000/svg';
const PAGE_SIZE=6;
const fieldMap=entry=>new Map((entry.fields||[]).map(field=>[field.name,field]));
const token=field=>JSON.stringify([field.type,field.text]);
const scalarTypes=new Set(['string','integer','number','boolean']);
function relationFields(entry){
  const fields=fieldMap(entry),raw=entry.raw_json||'',endpointNames=new Map(['from','to','from_key','to_key'].map(name=>[JSON.stringify(name),name]));
  // Composite values are not scalar fields in native-view/1. Detect only
  // their top-level presence, without parsing or converting any JSON value,
  // so an array/object key cannot trigger a fallback to an unrelated ID.
  let depth=0;
  for(let i=0;i<raw.length;i++){
    const character=raw[i];
    if(character==='"'){
      let end=i+1,escaped=false;for(;end<raw.length;end++){if(escaped){escaped=false;continue;}if(raw[end]==='\\'){escaped=true;continue;}if(raw[end]==='"')break;}
      const name=depth===1&&raw[end+1]===':'?endpointNames.get(raw.slice(i,end+1)):null;
      if(name&&!fields.has(name)){const kind=raw[end+2]==='['?'array':raw[end+2]==='{'?'object':null;if(kind)fields.set(name,{name,type:kind,text:'Valor '+kind+' não interpretado; consultar JSON original'});}
      i=end;
    }else if(character==='{'||character==='[')depth++;else if(character==='}'||character===']')depth--;
  }
  return fields;
}

export function buildLineage(entries){
  const identities=new Map(),keys=new Map(),allKeys=new Map();
  function add(index,key,entry,basis){
    if(!index.has(key))index.set(key,new Map());
    const matches=index.get(key);
    if(!matches.has(entry.uid))matches.set(entry.uid,{entry,bases:[]});
    const match=matches.get(entry.uid);if(!match.bases.includes(basis))match.bases.push(basis);
  }
  for(const entry of entries){
    if(!['record','node','asset','table','row'].includes(entry.kind))continue;
    const fields=fieldMap(entry),native=fields.get('native_id')||(!fields.has('native_id')&&entry.kind==='record'?fields.get('id'):null);
    if(native&&scalarTypes.has(native.type))add(identities,token(native),entry,'native_id');
    for(const alias of declaredSourceAliases(entry))add(identities,token({type:'string',text:alias}),entry,'source_ids');
    if(typeof entry.source_key==='string'){
      const key=token({type:'string',text:entry.source_key});
      add(identities,key,entry,'source_key');add(allKeys,key,entry,'source_key');add(keys,JSON.stringify([entry.group,key]),entry,'source_key');
    }
  }
  function endpoint(relation,fields,side){
    const keyName=side+'_key',hasKey=fields.has(keyName),name=hasKey?keyName:side,field=fields.get(name);
    const result={side,field:name,value:field?.text??null,valueType:field?.type??null,candidates:[],status:'NOT_SCALAR_OR_ABSENT'};
    if(!field)return result;
    if(field.type==='null'){result.status='EXPLICIT_NULL';return result;}
    if(!scalarTypes.has(field.type)){result.status='NOT_INTERPRETED';return result;}
    if(hasKey&&field.type!=='string'){result.status='UNSUPPORTED_KEY_TYPE';return result;}
    const lookup=hasKey?(relation.group==='lineage_graph.edges'
      ?keys.get(JSON.stringify(['lineage_graph.nodes',token(field)])):allKeys.get(token(field)))
      :identities.get(token(field));
    result.candidates=lookup?[...lookup.values()]:[];
    result.status=result.candidates.length===1?'RESOLVED':result.candidates.length?'COLLISION':'UNRESOLVED';
    return result;
  }
  return entries.filter(entry=>entry.kind==='relation').map(relation=>{
    const fields=relationFields(relation),kind=['type','kind','predicate','relation'].map(name=>fields.get(name)).find(Boolean);
    return {relation,type:kind?.text??'Tipo não declarado',causalStatus:fields.get('causal_status')?.text??null,
      from:endpoint(relation,fields,'from'),to:endpoint(relation,fields,'to')};
  });
}

function el(tag,attrs={},text=null,svg=false){const node=svg?document.createElementNS(NS,tag):document.createElement(tag);for(const[name,value]of Object.entries(attrs))node.setAttribute(name,String(value));if(text!==null)node.textContent=String(text);return node;}
const statusLabel={RESOLVED:'Referência resolvida',COLLISION:'Referência ambígua',UNRESOLVED:'Referência não encontrada',EXPLICIT_NULL:'Null declarado',NOT_SCALAR_OR_ABSENT:'Endpoint não declarado como escalar',NOT_INTERPRETED:'Valor não interpretado',UNSUPPORTED_KEY_TYPE:'Chave estrutural não textual'};

export function mountLineage(host,entries,onSelect){
  const model=buildLineage(entries),abort=new AbortController(),signal=abort.signal;
  const box=el('section',{class:'native-graph','data-component':'native-lineage'}),toolbar=el('div',{class:'graph-toolbar'}),svg=el('svg',{class:'graph-svg',role:'group','aria-label':'Grafo de relações declaradas; linhas neutras, sem causalidade inferida',tabindex:0,viewBox:'0 0 1000 560'},null,true),world=el('g',{},null,true),meta=el('p',{class:'graph-meta',role:'status'}),selection=el('div',{class:'panel','data-lineage-selection':''});
  const search=el('input',{type:'search','aria-label':'Buscar relação ou endpoint',placeholder:'Buscar tipo, referência ou nó…'}),type=el('select',{'aria-label':'Tipo de relação declarada'});
  type.append(el('option',{value:''},'Todos os tipos'));for(const value of [...new Set(model.map(item=>item.type))].sort())type.append(el('option',{value},value));
  toolbar.append(search,type);svg.append(world);box.append(el('h3',{},'Linhagem declarada'),el('p',{class:'muted'},'Cada linha liga endpoints explicitamente declarados. Tipos são literais da fonte; hierarquia, menção e causalidade são conceitos distintos. Referências ambíguas não são atribuídas a um candidato. Nenhuma causalidade é inferida.'),toolbar,svg,meta,selection);host.replaceChildren(box);
  let page=0,filtered=model,active=null,zoom=1,px=16,py=16,width=1000,height=560,worldWidth=1000,worldHeight=560,disposed=false,nodes=new Map(),edgeElements=new Map();
  const listen=(target,name,fn,options={})=>target.addEventListener(name,fn,{...options,signal});
  // Detached selection controls own their handlers; do not register each
  // transient button on the long-lived AbortSignal and retain old pages.
  function button(label,action,parent=toolbar){const node=el('button',{type:'button'},label);node.addEventListener('click',action);parent.append(node);return node;}
  const prev=button('← Relações anteriores',()=>{page--;render();}),next=button('Próximas relações →',()=>{page++;render();});
  button('Ampliar relações +',()=>scale(1.3));button('Reduzir relações −',()=>scale(1/1.3));button('Ajustar relações',()=>{zoom=Math.min(1,(width-32)/worldWidth,(height-32)/worldHeight);px=16;py=16;draw();});
  function label(node,value,maxWidth){
    const full=String(value),characters=[...full];let high=Math.min(characters.length,80),low=0;
    node.textContent=characters.slice(0,high).join('')+(high<characters.length?'…':'');
    if(node.getComputedTextLength()>maxWidth){while(low<high){const mid=Math.ceil((low+high)/2);node.textContent=characters.slice(0,mid).join('')+'…';if(node.getComputedTextLength()<=maxWidth)low=mid;else high=mid-1;}node.textContent=characters.slice(0,low).join('')+'…';}
    node.append(el('title',{},full,true));
  }
  function endpointKey(item,endpoint){return endpoint.status==='RESOLVED'?'entry:'+endpoint.candidates[0].entry.uid:'reference:'+item.relation.uid+':'+endpoint.side;}
  function centerNode(key){const node=nodes.get(key);if(!node)return;px=width/2-(node.x+130)*zoom;py=height/2-(node.y+37)*zoom;draw();}
  function describeEndpoint(item,endpoint){
    const card=el('div',{class:'panel'});card.append(el('h3',{},endpoint.side==='from'?'Origem declarada':'Destino declarado'),el('p',{},statusLabel[endpoint.status]),el('p',{class:'muted'},`${endpoint.field} · ${endpoint.valueType??'sem valor escalar'} · ${endpoint.value??'não declarado como escalar'}`));
    const actions=el('div',{class:'graph-results'});card.append(actions);
    button('Centralizar '+(endpoint.side==='from'?'origem':'destino'),()=>centerNode(endpointKey(item,endpoint)),actions);
    if(endpoint.status==='COLLISION')card.append(el('p',{class:'muted'},`${endpoint.candidates.length} ocorrências candidatas; nenhuma foi escolhida automaticamente.`));
    for(const match of endpoint.candidates)button(match.entry.title+' · '+match.entry.group+' · '+match.entry.uid,()=>onSelect(match.entry),actions);
    return card;
  }
  function choose(item,endpoint=null){
    active=item;selection.replaceChildren(el('h3',{class:'muted'},'Tipo declarado: '+item.type),el('p',{class:'muted'},'Estado causal declarado: '+(item.causalStatus??'não declarado')+' · sem validação causal pelo Atlas.'));
    button('Detalhes desta relação',()=>onSelect(item.relation),selection);
    selection.append(describeEndpoint(item,item.from),describeEndpoint(item,item.to));
    for(const[id,node]of edgeElements)node.setAttribute('aria-pressed',String(id===item.relation.uid));
    onSelect(endpoint?.status==='RESOLVED'?endpoint.candidates[0].entry:item.relation);
  }
  function draw(){if(!disposed)world.setAttribute('transform',`translate(${px} ${py}) scale(${zoom})`);}
  function scale(factor){const value=Math.max(.1,Math.min(4,zoom*factor)),ratio=value/zoom;px=width/2-(width/2-px)*ratio;py=height/2-(height/2-py)*ratio;zoom=value;draw();}
  function render(){
    if(disposed)return;
    page=Math.max(0,Math.min(page,Math.max(0,Math.ceil(filtered.length/PAGE_SIZE)-1)));const window=filtered.slice(page*PAGE_SIZE,(page+1)*PAGE_SIZE);
    world.replaceChildren();nodes=new Map();edgeElements=new Map();
    for(const item of window)for(const endpoint of [item.from,item.to]){
      const key=endpointKey(item,endpoint);if(!nodes.has(key))nodes.set(key,{key,item,endpoint,roles:new Set()});nodes.get(key).roles.add(endpoint.side);
    }
    const columns=[[],[]];for(const node of nodes.values())columns[node.roles.has('from')?0:1].push(node);
    columns.forEach((column,index)=>column.forEach((node,row)=>{node.x=index*680;node.y=row*112;}));worldWidth=960;worldHeight=Math.max(120,window.length*112,...columns.map(column=>column.length*112));
    const connections=el('g',{'data-lineage-edges':''},null,true),vertices=el('g',{'data-lineage-nodes':''},null,true);world.append(connections,vertices);
    window.forEach((item,index)=>{
      const from=nodes.get(endpointKey(item,item.from)),to=nodes.get(endpointKey(item,item.to));
      // Each occurrence has its own labelled lane, including parallel edges
      // and cycles. Shared endpoints remain one vertex, not guessed copies.
      const x1=from.x+260,y1=from.y+37,x2=to.x+(to.x===0?260:0),y2=to.y+37,lane=index*112+37;
      const d=`M ${x1} ${y1} C ${x1+65} ${y1} 400 ${lane} 470 ${lane} S ${x2-65} ${y2} ${x2} ${y2}`;
      const edge=el('g',{role:'button',tabindex:0,'aria-label':'Relação '+item.type+' · '+item.relation.uid,'aria-pressed':String(active===item),'data-lineage-relation':item.relation.uid},null,true);
      edge.append(el('path',{d,fill:'none',stroke:'#6b8375','stroke-width':2,'stroke-dasharray':'5 4'},null,true));
      const text=el('text',{x:470,y:lane-10,'text-anchor':'middle',fill:'#244e42','font-size':12},null,true);
      edge.append(text);connections.append(edge);label(text,item.type,230);edgeElements.set(item.relation.uid,edge);
    });
    for(const node of nodes.values()){
      const endpoint=node.endpoint,resolved=endpoint.status==='RESOLVED',entry=resolved?endpoint.candidates[0].entry:null;
      const title=entry?.title??(statusLabel[endpoint.status]+(endpoint.status==='COLLISION'?' ('+endpoint.candidates.length+')':'')),sub=entry?entry.group:((endpoint.valueType??'ausente')+': '+(endpoint.value??'sem literal escalar'));
      const vertex=el('g',{class:'graph-node',role:'button',tabindex:0,transform:`translate(${node.x} ${node.y})`,'aria-label':title,'data-lineage-endpoint':node.key,'data-resolution':endpoint.status},null,true);
      vertex.append(el('rect',{width:260,height:74,rx:10},null,true));const heading=el('text',{x:13,y:28,class:'node-title'},null,true),identity=el('text',{x:13,y:53,class:'meta'},null,true);vertex.append(heading,identity);vertices.append(vertex);label(heading,title,234);label(identity,sub,234);
    }
    prev.disabled=page===0;next.disabled=(page+1)*PAGE_SIZE>=filtered.length;
    meta.textContent=`${filtered.length} de ${model.length} relações declaradas na seleção · página ${page+1}/${Math.max(1,Math.ceil(filtered.length/PAGE_SIZE))} · ${window.length} relações e ${nodes.size} referências gráficas nesta página. Arraste ou use setas para mover; Enter/espaço seleciona.`;
    if(!window.length)selection.replaceChildren(el('p',{class:'empty'},model.length?'Nenhuma relação corresponde à busca.':'Nenhuma relação declarada nesta projeção.'));
    else if(active&&!window.includes(active)){active=null;selection.replaceChildren();}
    px=16;py=48;zoom=1;draw();
  }
  function activate(event){
    const endpoint=event.target.closest?.('[data-lineage-endpoint]'),relation=event.target.closest?.('[data-lineage-relation]');
    if(endpoint){const node=nodes.get(endpoint.getAttribute('data-lineage-endpoint'));if(node)choose(node.item,node.endpoint);}
    else if(relation){const item=model.find(item=>item.relation.uid===relation.getAttribute('data-lineage-relation'));if(item)choose(item);}
  }
  listen(world,'click',activate);listen(world,'keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate(event);}});
  function filter(){
    const query=search.value.trim().toLocaleLowerCase('pt-BR');
    filtered=model.filter(item=>(!type.value||item.type===type.value)&&(!query||[item.type,item.relation.uid,item.relation.title,...(item.relation.fields||[]).map(field=>field.text),...item.from.candidates.flatMap(match=>[match.entry.title,match.entry.uid]),...item.to.candidates.flatMap(match=>[match.entry.title,match.entry.uid])].some(value=>String(value).toLocaleLowerCase('pt-BR').includes(query))));
    page=0;render();
  }
  function locate(uid){
    if(disposed)return false;
    let item=model.find(item=>item.relation.uid===uid),endpoint=null;
    if(!item){item=model.find(item=>[item.from,item.to].some(value=>value.candidates.some(match=>match.entry.uid===uid)));if(item)endpoint=[item.from,item.to].find(value=>value.candidates.some(match=>match.entry.uid===uid));}
    if(!item)return false;
    search.value='';type.value='';filtered=model;page=Math.floor(model.indexOf(item)/PAGE_SIZE);render();choose(item,endpoint);
    if(endpoint)centerNode(endpointKey(item,endpoint));else{px=width/2-470*zoom;py=height/2-((model.indexOf(item)%PAGE_SIZE)*112+37)*zoom;draw();}
    return true;
  }
  listen(search,'input',filter);listen(type,'change',filter);listen(search,'keydown',event=>{if(event.key==='Enter'&&filtered.length){event.preventDefault();const item=filtered[0];choose(item);centerNode(endpointKey(item,item.from));}});
  let drag=null;listen(svg,'pointerdown',event=>{if(event.target.closest?.('[data-lineage-endpoint],[data-lineage-relation]'))return;drag={x:event.clientX,y:event.clientY,px,py};svg.setPointerCapture(event.pointerId);});
  listen(svg,'pointermove',event=>{if(!drag)return;const rect=svg.getBoundingClientRect();px=drag.px+(event.clientX-drag.x)*width/rect.width;py=drag.py+(event.clientY-drag.y)*height/rect.height;draw();});listen(svg,'pointerup',()=>{drag=null;});listen(svg,'pointercancel',()=>{drag=null;});
  listen(svg,'keydown',event=>{const moves={ArrowLeft:[40,0],ArrowRight:[-40,0],ArrowUp:[0,40],ArrowDown:[0,-40]};if(moves[event.key]){event.preventDefault();px+=moves[event.key][0];py+=moves[event.key][1];draw();}});
  const resize=new ResizeObserver(()=>{width=Math.max(280,svg.clientWidth);height=svg.clientHeight||560;svg.setAttribute('viewBox',`0 0 ${width} ${height}`);draw();});resize.observe(svg);render();
  return {locate,destroy(){disposed=true;resize.disconnect();abort.abort();nodes.clear();edgeElements.clear();host.replaceChildren();}};
}
