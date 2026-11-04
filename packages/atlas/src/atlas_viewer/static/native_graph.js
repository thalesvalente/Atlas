/* Native SVG camera over structural identities, never inferred scientific IDs.
 * Stable keyed nodes and delegated handlers preserve double-click/focus.
 * Large collections open at readable scale, not an invisible fit-to-all.
 */
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs={},text=null,svg=false){const n=svg?document.createElementNS(NS,tag):document.createElement(tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==null)n.textContent=text;return n;}
export function mountGraph(host,nodes,onSelect){
  const abort=new AbortController(),signal=abort.signal,byId=new Map(nodes.map(n=>[n.uid,n]));
  const children=new Map(nodes.map(n=>[n.uid,[]])),parents=new Map(),cycles=new Set();
  for(const n of nodes)if(n.parent_uid&&byId.has(n.parent_uid))parents.set(n.uid,n.parent_uid);
  const done=new Set();
  for(const n of nodes){if(done.has(n.uid))continue;const chain=[],local=new Map();let id=n.uid;while(id&&byId.has(id)&&!done.has(id)){if(local.has(id)){for(const c of chain.slice(local.get(id)))cycles.add(c);break;}local.set(id,chain.length);chain.push(id);id=parents.get(id);}chain.forEach(x=>done.add(x));}
  for(const id of cycles)parents.delete(id);
  for(const[id,p]of parents)children.get(p).push(id);
  const roots=nodes.filter(n=>!parents.has(n.uid)).map(n=>n.uid),collapsed=new Set();
  const dense=nodes.length>180,rootSet=new Set(roots);
  let viewLimit=dense?24:nodes.length;
  if(dense)for(const n of nodes)if(!rootSet.has(n.uid)&&children.get(n.uid).length)collapsed.add(n.uid);
  let positions=new Map(),elements=new Map(),width=900,height=480,zoom=1,px=20,py=20,selected=null,worldWidth=900,worldHeight=480,disposed=false;
  const box=el('section',{class:'native-graph'}),toolbar=el('div',{class:'graph-toolbar'}),svg=el('svg',{class:'graph-svg',role:'tree','aria-label':'Árvore estrutural do snapshot',tabindex:0,viewBox:'0 0 900 480'},null,true),world=el('g',{},null,true),edges=el('g',{'aria-hidden':'true'},null,true),nodeLayer=el('g',{},null,true),mini=el('svg',{class:'graph-mini',viewBox:'0 0 180 78',role:'button',tabindex:0,'aria-label':'Minimapa: clique para centralizar'},null,true),meta=el('div',{class:'graph-meta',role:'status'});
  world.append(edges,nodeLayer);svg.append(world);box.append(toolbar,svg,mini,meta);host.replaceChildren(box);
  const listen=(target,name,fn,opts={})=>target.addEventListener(name,fn,{...opts,signal});
  function button(label,action){const b=el('button',{type:'button'},label);listen(b,'click',action);toolbar.append(b);return b;}
  button('Ampliar +',()=>scale(1.3));button('Reduzir −',()=>scale(1/1.3));button('Ajustar',fit);
  button('Expandir todos',()=>{collapsed.clear();viewLimit=nodes.length;layout();draw();});
  button('Recolher',()=>{nodes.forEach(n=>{if(children.get(n.uid).length)collapsed.add(n.uid);});layout();draw();});
  const showMore=button('Mostrar mais nós +24',()=>{viewLimit=Math.min(nodes.length,viewLimit+24);layout();draw();});
  showMore.hidden=!dense;
  const search=el('input',{type:'search','aria-label':'Localizar nó na árvore',placeholder:'Localizar qualquer nó…'});toolbar.append(search);let searchAt=-1;
  function find(){const q=search.value.toLocaleLowerCase('pt-BR');const matches=nodes.filter(n=>[n.title,n.native_id,n.source_key].join(' ').toLocaleLowerCase('pt-BR').includes(q));if(matches.length){searchAt=(searchAt+1)%matches.length;locate(matches[searchAt].uid);}}
  button('Localizar / próximo',find);listen(search,'input',()=>{searchAt=-1;});listen(search,'keydown',e=>{if(e.key==='Enter'){e.preventDefault();find();}});
  function layout(){
    positions=new Map();const stack=roots.slice(0,viewLimit).reverse().map(id=>[id,0]),visited=new Set();let row=0,maxDepth=0;
    while(stack.length){
      const[id,depth]=stack.pop();if(visited.has(id))continue;visited.add(id);
      positions.set(id,{x:depth*300,y:row++*98});maxDepth=Math.max(depth,maxDepth);
      if(!collapsed.has(id)){const cs=(children.get(id)||[]).slice(0,viewLimit);for(let i=cs.length-1;i>=0;i--)stack.push([cs[i],depth+1]);}
    }
    worldWidth=Math.max(280,maxDepth*300+282);worldHeight=Math.max(100,row*98);
  }
  function fit(){
    // Fit small hierarchies; for large collections use a readable viewport.
    // Every node remains reachable by pan, minimap, search and the full list.
    zoom=dense?1:Math.max(.8,Math.min(1.2,(width-40)/worldWidth,(height-40)/worldHeight));
    px=20;py=20;draw();
  }
  function scale(factor){const next=Math.max(.00001,Math.min(4,zoom*factor)),ratio=next/zoom;px=width/2-(width/2-px)*ratio;py=height/2-(height/2-py)*ratio;zoom=next;draw();}
  function select(id){if(!byId.has(id))return;selected=id;for(const[key,node]of elements)node.setAttribute('aria-selected',String(key===id));onSelect(byId.get(id));}
  function toggle(id){if(!children.get(id)?.length)return;collapsed.has(id)?collapsed.delete(id):collapsed.add(id);layout();draw();elements.get(id)?.focus();}
  function locate(id){
    if(!byId.has(id))return;
    const visited=new Set();let child=id,p=parents.get(child);
    while(p&&!visited.has(p)){
      visited.add(p);collapsed.delete(p);
      const index=(children.get(p)||[]).indexOf(child);
      if(index>=viewLimit)viewLimit=index+1;
      child=p;p=parents.get(child);
    }
    const rootIndex=roots.indexOf(child);
    if(rootIndex>=viewLimit)viewLimit=rootIndex+1;
    layout();const pos=positions.get(id);if(!pos)return;
    zoom=Math.max(zoom,.8);px=width/2-(pos.x+130)*zoom;py=height/2-(pos.y+36)*zoom;
    selected=id;draw();onSelect(byId.get(id));
  }
  function draw(){
    if(disposed)return;world.setAttribute('transform',`translate(${px} ${py}) scale(${zoom})`);
    const candidates=[];for(const[id,p]of positions)if((p.x+265)*zoom+px>=0&&p.x*zoom+px<=width&&(p.y+74)*zoom+py>=0&&p.y*zoom+py<=height)candidates.push([id,p]);
    const visible=candidates.slice(0,1000),keep=new Set(visible.map(([id])=>id));
    edges.replaceChildren();
    for(const[id,node]of elements)if(!keep.has(id)){node.remove();elements.delete(id);}
    for(const[id,p]of visible){const pp=positions.get(parents.get(id));if(pp)edges.append(el('path',{class:'graph-edge',d:`M ${pp.x+260} ${pp.y+36} H ${p.x-12} V ${p.y+36} H ${p.x}`},null,true));}
    for(const[id,p]of visible){
      const n=byId.get(id);let g=elements.get(id);
      if(!g){g=el('g',{class:'graph-node',role:'treeitem',tabindex:0,'data-native-node':id,'aria-label':n.title},null,true);g.append(el('rect',{width:260,height:74,rx:10},null,true));const t=el('text',{x:13,y:28,class:'node-title'},[...n.title].slice(0,36).join('')+([...n.title].length>36?'…':''),true);t.append(el('title',{},n.title,true));g.append(t,el('text',{x:13,y:53,class:'meta'},cycles.has(id)?'Ciclo declarado · consultar detalhe':n.native_id??n.source_key??'Sem ID científico',true));nodeLayer.append(g);elements.set(id,g);}
      g.setAttribute('transform',`translate(${p.x} ${p.y})`);g.setAttribute('aria-selected',String(selected===id));if(children.get(id).length)g.setAttribute('aria-expanded',String(!collapsed.has(id)));
    }
    mini.replaceChildren(el('rect',{class:'bounds',width:180,height:78},null,true));const sx=180/worldWidth,sy=78/worldHeight;mini.append(el('rect',{class:'camera',x:Math.max(0,-px/zoom*sx),y:Math.max(0,-py/zoom*sy),width:Math.min(180,width/zoom*sx),height:Math.min(78,height/zoom*sy)},null,true));
    showMore.disabled=viewLimit>=nodes.length;
    meta.textContent=`${nodes.length} nós carregados · ${positions.size} no foco atual · ${visible.length} na janela${candidates.length>1000?' (aproxime para ver todos)':''} · zoom ${(zoom*100).toFixed(1)}% · ${nodes.length-positions.size} fora da vista inicial, disponíveis na busca · ${cycles.size} nós em ciclo. Duplo clique ou espaço expande/recolhe. Linhas representam parentesco estrutural, não causalidade.`;
  }
  function nodeId(event){return event.target.closest?.('.graph-node')?.getAttribute('data-native-node');}
  listen(world,'click',e=>{const id=nodeId(e);if(id){e.stopPropagation();select(id);}});
  listen(world,'dblclick',e=>{const id=nodeId(e);if(id){e.stopPropagation();toggle(id);}});
  listen(world,'keydown',e=>{const id=nodeId(e);if(!id)return;if(e.key==='Enter'){e.preventDefault();select(id);}else if(e.key===' '){e.preventDefault();toggle(id);}});
  let drag=null;
  listen(svg,'pointerdown',e=>{if(nodeId(e))return;drag={x:e.clientX,y:e.clientY,px,py};svg.setPointerCapture(e.pointerId);});
  listen(svg,'pointermove',e=>{if(!drag)return;const r=svg.getBoundingClientRect();px=drag.px+(e.clientX-drag.x)*width/r.width;py=drag.py+(e.clientY-drag.y)*height/r.height;draw();});
  listen(svg,'pointerup',()=>{drag=null;});listen(svg,'pointercancel',()=>{drag=null;});listen(svg,'wheel',e=>{e.preventDefault();scale(e.deltaY<0?1.1:1/1.1);},{passive:false});
  listen(svg,'keydown',e=>{const moves={ArrowLeft:[40,0],ArrowRight:[-40,0],ArrowUp:[0,40],ArrowDown:[0,-40]};if(moves[e.key]){e.preventDefault();px+=moves[e.key][0];py+=moves[e.key][1];draw();}});
  listen(mini,'click',e=>{const r=mini.getBoundingClientRect();px=width/2-(e.clientX-r.left)/r.width*worldWidth*zoom;py=height/2-(e.clientY-r.top)/r.height*worldHeight*zoom;draw();});listen(mini,'keydown',e=>{if(e.key==='Enter')fit();});
  const resize=new ResizeObserver(()=>{width=Math.max(280,svg.clientWidth);height=svg.clientHeight||480;svg.setAttribute('viewBox',`0 0 ${width} ${height}`);draw();});resize.observe(svg);layout();fit();
  return {locate,destroy(){disposed=true;resize.disconnect();abort.abort();elements.clear();host.replaceChildren();}};
}
