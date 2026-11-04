/** Authorized, reviewed port of Atlas v6.1 presentation code at 2895d95.
 * Function-level provenance, source blobs and adaptations: REUSE-MANIFEST.json.
 * Only the verified Native View DTO supplies data; no imported HTML executes.
 */
import {KIND,COLORS,EDGE,literalText,familyIdentity} from './native_legacy_model.js';
const NS='http://www.w3.org/2000/svg';
const STATUS_INK=Object.freeze(Object.assign(Object.create(null),{published:'#116b4d',technical:'#285f8a',failed:'#9e3447',mixed:'#87570d',blocked:'#666324',unknown:'#526978'}));
export function mountEditorialTree(host,model,rows,onSelect,persistent={},options={}){
 const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
 const makeButton=(text,fn)=>{const b=el('button',text);b.type='button';b.addEventListener('click',fn);return b;};
 const controls=new Map(),$=id=>controls.get(id);
 const DATA={records:model.records,editorial_map:model.editorial_map,edges:model.edges.filter(e=>e.from&&e.to&&rows.some(r=>r.id===e.from)&&rows.some(r=>r.id===e.to))};
 const familyLabel=key=>model.familyLabel(key);
 const R=model.byUid,visible=new Set(rows.map(r=>r.id)),expanded=persistent.expanded??=new Set();
 const filtered=()=>rows,num=value=>value.toLocaleString('pt-BR');
 let selected=persistent.selected??null,graphNodes=[],graphEdges=[],full=[0,0,940,600],box=persistent.box??[0,0,940,600],zoomReferenceWidth=persistent.zoomReferenceWidth??null,moved=false;
 const frame=el('div',undefined,'editorial-tree');host.append(frame);
 const toolbar=el('div',undefined,'toolbar'),group=el('div',undefined,'button-group');toolbar.append(group);frame.append(toolbar);
 const add=(id,text,fn)=>{const b=makeButton(text,fn);controls.set(id,b);group.append(b);return b;};
 add('fit','Mostrar árvore inteira',()=>setBox([...full]));
 add('readable','Zoom confortável',()=>comfortable());
 add('focus','Focar seleção',()=>{if(selected)focusNode(selected);});
 add('expandAll','Expandir famílias',()=>changeTreeWithoutCameraJump(()=>rows.forEach(r=>expanded.add(nativeFamily(r)))));
 add('collapseAll','Recolher',()=>changeTreeWithoutCameraJump(()=>expanded.clear()));
 add('zoomIn','＋',()=>zoom(1.18)).setAttribute('aria-label','Aproximar');
 add('zoomOut','−',()=>zoom(1/1.18)).setAttribute('aria-label','Afastar');
 const zoomLabel=el('span','100%');controls.set('zoomLabel',zoomLabel);group.append(zoomLabel);
 const settings=el('div',undefined,'tree-controls'),label=el('label','Organização'),organization=el('select');organization.id='native-editorial-organization';
 for(const[value,title]of [['thematic','Visão temática'],['native','Famílias de origem']]){const o=el('option',title);o.value=value;organization.append(o);}organization.value=persistent.organization??'thematic';label.append(organization);settings.append(label);
 const relationsLabel=el('label'),relations=el('input');relations.type='checkbox';relations.checked=persistent.relations??false;relationsLabel.append(relations,document.createTextNode('Vínculos explícitos do filtro'));settings.append(relationsLabel);
 const counter=el('span',`${rows.length} / ${model.records.length} registros · índice e árvore no mesmo filtro`);settings.append(counter);
 const advanced=el('details',undefined,'editorial-options'),summary=el('summary',`Organização e vínculos · ${rows.length}/${model.records.length} registros`),media=globalThis.matchMedia?.('(max-width:720px)');
 advanced.open=media?.matches?(persistent.advancedOpen??false):true;advanced.append(summary,settings);frame.append(advanced);
 advanced.addEventListener('toggle',()=>{persistent.advancedOpen=advanced.open;});
 const responsiveOptions=event=>{advanced.open=!event.matches;};media?.addEventListener('change',responsiveOptions);

 function treeOrganizationMode(){return organization.value;}
 function treeRelationsVisible(){return relations.checked;}
 const map=el('div',undefined,'map');map.tabIndex=0;map.setAttribute('role','region');map.setAttribute('aria-label','Árvore editorial; arraste, use setas, +, − e Home');controls.set('map',map);
 const svg=document.createElementNS(NS,'svg');svg.classList.add('editorial-svg');svg.setAttribute('preserveAspectRatio','xMidYMin meet');svg.setAttribute('role','group');svg.setAttribute('aria-label','Mapa editorial de registros');map.append(svg);
 const minimap=el('div',undefined,'editorial-minimap'),mini=document.createElementNS(NS,'svg');mini.setAttribute('aria-hidden','true');minimap.append(mini);map.append(minimap);
 map.append(el('div','Arraste para explorar · roda ou +/− para aproximar · Home mostra tudo','map-hint'));frame.append(map);
 frame.append(el('p','Tema e família organizam a leitura. Não declaram parentesco, causalidade nem aprovação científica.','graph-explanation'));
 function comfortable(){
  const aspect=Math.max(.75,map.clientWidth/Math.max(350,map.clientHeight)),mobile=map.clientWidth<480,targetW=mobile?Math.min(450,full[2]):full[2];
  const legibleHeight=Math.min(full[3],Math.max(450,targetW/aspect*(mobile?1:.83))),themes=graphNodes.filter(n=>n.type==='theme'),middle=themes[Math.floor(themes.length/2)];
  const x=mobile&&middle?Math.max(0,middle.x+middle.w/2-targetW/2):full[0];setBox([x,full[1],targetW,legibleHeight]);
 }
 function renderGraph(preserve=false){
  const old=[...box],result=layoutFamilies();graphNodes=result.nodes;graphEdges=[];full=result.box;svg.replaceChildren();
  const defs=s('defs'),marker=s('marker',{id:'tree-arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});marker.append(s('path',{d:'M0 0 L10 5 L0 10 Z',fill:'#226e9c'}));defs.append(marker);svg.append(defs);
  renderTreeLinks();graphNodes.forEach(n=>drawNode(n));
  if(preserve)setBox(old);else comfortable();
 }
 function selectRecord(uid,focus=false){const hadFocus=document.activeElement?.getAttribute('data-graph-id')===uid;selected=uid;persistent.selected=uid;const r=R.get(uid);if(!r)return;expanded.add(nativeFamily(r));renderGraph(true);if(hadFocus)[...svg.querySelectorAll('[data-graph-id]')].find(n=>n.getAttribute('data-graph-id')===uid)?.focus();onSelect(r.entry);if(focus||selectedIsObscured(uid))focusNode(uid);}
function s(tag,attr={},text){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attr))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e;}
function wrapped(text,max=37,lines=2){
 const words=String(text).split(/\s+/).flatMap(word=>{const chars=Array.from(word),chunks=[];for(let i=0;i<chars.length;i+=max)chunks.push(chars.slice(i,i+max).join(''));return chunks;}),out=[];let l='';
 for(const w of words){if(Array.from((l+' '+w).trim()).length>max){if(l)out.push(l);l=w;}else l=(l+' '+w).trim();}if(l)out.push(l);
 const r=out.slice(0,lines);if(out.length>lines)r[lines-1]=Array.from(r[lines-1]).slice(0,max-1).join('')+'…';return r;
}
// R4 v5 — A navigation taxonomy with explicit (and separate) evidence edges.
// Root/theme/family arcs say ONLY that records are listed under an editorial
// family. They never assert scientific or chronological causality.
// Editorial membership is supplied by a hash-bound presentation map. Native
// families remain literal; neutral columns below are only a balanced index.
const TREE_THEME_PALETTE=['#5A91E6','#14A8A3','#9B81DE','#5F8BA2'];
function nativeFamily(record){return record.nativeFamilyKey;}

function neutralTreeThemes(families,prefix,title){
 if(!families.length)return [];
 const count=Math.min(3,families.length),columns=Array.from({length:count},()=>[]);
 families.forEach((family,index)=>columns[index%count].push(family));
 return columns.map((members,index)=>({id:prefix+'-'+index,title:title+(count>1?' · '+(index+1):''),
   subtitle:'Índice balanceado · sem inferência científica',families:members,neutral:true,color:'#788D9B'}));
}
function allTreeThemes(){
 const families=[...new Set(DATA.records.map(nativeFamily))].sort((a,b)=>familyLabel(a).localeCompare(familyLabel(b),'pt-BR'));
 if(treeOrganizationMode()==='native')return neutralTreeThemes(families,'native','Famílias de origem');
 const map=DATA.editorial_map;
 if(map?.schema!=='r4-atlas-editorial-map/1'||!Array.isArray(map.themes))
  return neutralTreeThemes(families,'unmapped','Famílias sem tema associado');
 const known=new Set(families),claims=new Map();
 for(const theme of map.themes.filter(t=>t&&typeof t==='object'))for(const member of (Array.isArray(theme.families)?theme.families:[])){
  const family=familyIdentity(member).key;if(known.has(family))claims.set(family,(claims.get(family)||0)+1);}
 const themes=map.themes.filter(t=>t&&typeof t.id==='string'&&typeof t.title==='string').map((t,index)=>({
  id:t.id,title:t.title,subtitle:t.subtitle===undefined?'Organização editorial · não causal':literalText(t.subtitle),
  color:TREE_THEME_PALETTE[index%TREE_THEME_PALETTE.length],
  families:(Array.isArray(t.families)?t.families:[]).map(f=>familyIdentity(f).key).filter(f=>known.has(f)&&claims.get(f)===1)
 })).filter(t=>t.families.length);
 const mapped=new Set(themes.flatMap(t=>t.families));
 return [...themes,...neutralTreeThemes(families.filter(f=>!mapped.has(f)),'unmapped','Famílias sem tema associado')];
}

const LINK_COLORS = Object.assign(Object.create(null),{PREDECESSOR:'#226e9c',INPUT_FROM:'#226e9c',DERIVED_FROM:'#226e9c',PRODUCES:'#26875e',PRESENTED_BY:'#26875e',HISTORICAL_CONTEXT:'#95a5b2',COMPARED_WITH:'#b78847'});
function svgPath(d,color,width=1.6,dash='',desc='',klass='tree-link',arrow=false) {
 const p=s('path',{d,fill:'none',stroke:color,'stroke-width':width,'stroke-dasharray':dash,
    'stroke-linecap':'round','stroke-linejoin':'round',class:klass});
 if(arrow) p.setAttribute('marker-end','url(#tree-arrow)');
 if(desc) p.appendChild(s('title',{},desc));
 svg.appendChild(p); return p;
}
function drawNode(node,parent=svg,miniature=false) {
 const isRoot=node.type==='root',isTheme=node.type==='theme',isFamily=node.type==='family';
 const r=R.get(node.id),selectedNow=r?.id===selected;
 const semanticRole=isRoot?'Mapa do Atlas':isTheme?`${node.title}: ${node.count} registros`:isFamily?`${node.title}: ${node.count} registros; expandir ou recolher`:r?.title??node.title;
 const g=s('g',{transform:`translate(${node.x} ${node.y})`,class:'svg-node svg-'+node.type+(selectedNow?' selected':''),
   'data-graph-id':node.id,'data-native-node':isRoot||isTheme||isFamily?'':node.id,tabindex:miniature?-1:0,role:'button','aria-label':semanticRole});
 const accent=isRoot?'#43D9D2':isTheme||isFamily?node.color||'#788D9B':COLORS[typeof r?.result_group==='string'?r.result_group:'']||'#7D92A4';
 const statusInk=STATUS_INK[typeof r?.result_group==='string'?r.result_group:'']||'#526978';
 const fill=isRoot?'#14354C':isTheme?'#EAF3FA':isFamily?'#FFFFFF':selectedNow?'#EFFAF8':'#FFFFFF';
 const outline=selectedNow?'#0E9189':isRoot?'#2C667B':isTheme?'#C9DFEE':isFamily?'#D8E5EF':'#DBE6EE';
 const corner=isRoot?18:isTheme?15:isFamily?13:11;
 const bg=s('rect',{width:node.w,height:node.h,rx:corner,fill,stroke:outline,'stroke-width':selectedNow?2.9:1.25,class:'node-surface'});g.appendChild(bg);
 if(!isRoot)g.appendChild(s('rect',{x:0,y:10,width:isTheme?5:4,height:node.h-20,rx:2,fill:accent}));
 if(isRoot){
  g.appendChild(s('circle',{cx:28,cy:28,r:13,fill:'#1F5A6C'}));
  g.appendChild(s('text',{x:28,y:32.5,'text-anchor':'middle','font-size':12,'font-weight':800,fill:'#E4FFFB'},'A'));
  g.appendChild(s('text',{x:49,y:29,'font-size':18.7,'font-weight':760,fill:'#F5FBFF','letter-spacing':'-.35'},'História experimental'));
  g.appendChild(s('text',{x:49,y:47,'font-size':10.7,fill:'#B3D7E5'},'Evidências · produtos · decisões'));
  g.appendChild(s('rect',{x:node.w-92,y:15,width:76,height:26,rx:13,fill:'#214F5B'}));
  g.appendChild(s('text',{x:node.w-54,y:32,'font-size':10.5,'text-anchor':'middle','font-weight':740,fill:'#6DF1DB'},'EXPLORAR'));
  g.appendChild(s('text',{x:18,y:node.h-12,'font-size':10.3,fill:'#C7E4ED'},node.subtitle||''));
 }else if(isTheme){
  const sign=String(node.ordinal??1).padStart(2,'0');
  g.appendChild(s('rect',{x:17,y:14,width:35,height:29,rx:9,fill:accent}));
  g.appendChild(s('text',{x:34.5,y:33.5,'font-size':13,'text-anchor':'middle','font-weight':800,fill:'#071F2E'},sign));
  for(const[i,line]of wrapped(node.title,36,2).entries())g.appendChild(s('text',{x:65,y:27+i*16,'font-size':15.5,'font-weight':750,fill:'#193B50'},line));
  g.appendChild(s('text',{x:19,y:node.h-12,'font-size':11,fill:'#496777'},node.subtitle||`${node.count} registros`));
 }else if(isFamily){
  const lines=wrapped(node.title,40,2);
  lines.forEach((line,i)=>g.appendChild(s('text',{x:17,y:25+i*17,'font-size':14.7,'font-weight':730,fill:'#17364C'},line)));
  g.appendChild(s('text',{x:17,y:node.h-13,'font-size':11.1,'font-weight':530,fill:'#496777'},`${num(node.count)} registros · ${expanded.has(node.familyKey)?'recolher −':'expandir +'}`));
  const x=node.w-28;
  g.appendChild(s('circle',{cx:x,cy:23,r:11.8,fill:'#EFF6FB',stroke:'#CDE0EE'}));
  g.appendChild(s('text',{x,y:27,'text-anchor':'middle','font-size':17,'font-weight':520,fill:'#386A87'},expanded.has(node.familyKey)?'−':'+'));
 }else{
  const lines=wrapped(node.title,node.w>=240?35:28,2);
  lines.forEach((line,i)=>g.appendChild(s('text',{x:15,y:25+i*16,'font-size':node.w>=240?12.8:12.1,'font-weight':730,fill:'#263D4C'},line)));
  const status=(r?.result===undefined?'':literalText(r.result)).replaceAll('_',' ').slice(0,node.w>=240?39:27);
  g.appendChild(s('text',{x:15,y:node.h-28,'font-size':10.5,'font-weight':650,fill:statusInk},status));
  g.appendChild(s('text',{x:15,y:node.h-12,'font-size':10,fill:'#496777'},(KIND[typeof r?.kind==='string'?r.kind:'']??'').slice(0,38)));
 }
 g.appendChild(s('title',{},isRoot?'Abrir árvore completa; linhas de organização não significam causalidade.':isTheme?`${node.title}\n${node.count} registros; organização, sem inferir causalidade.`:isFamily?`${node.title}\n${node.count} registros; clique para expandir.`:`${r?.title}\n${r?.result}\n${r?.id}`));
 if(!miniature){
  const invoke=(focus=false)=>{
   if(isRoot){setBox([...full]);return;}
   if(isTheme){focusTheme(node.id);return;}
   if(isFamily){toggleTreeFamily(node.familyKey);return;}
   selectRecord(node.id,focus);
  };
  g.addEventListener('click',()=>{if(!moved)invoke(false);});
  g.addEventListener('dblclick',e=>{e.stopPropagation();if(!moved)invoke(true);});
  g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();invoke(true);}});
 }
 parent.appendChild(g);
}

function focusTheme(id){const theme=graphNodes.find(n=>n.id===id);if(!theme)return;
 const same=graphNodes.filter(n=>n.theme===theme.theme && n.type==='family');
 const h=Math.min(850,Math.max(420,(same.at(-1)?.y??theme.y+380)-theme.y+150));
 setBox([theme.x-40,theme.y-50,theme.w+80,h]);
}
// Expansion changes geometry, not the user's camera. Preserve zoom and keep the
// clicked family's centre at its previous screen location after re-layout.
// Zoom/fit/focus are explicit actions with separate handlers.
function changeTreeWithoutCameraJump(change,anchorId='tree:root'){
 const oldBox=[...box];
 const previous=graphNodes.find(n=>n.id===anchorId),hadFocus=document.activeElement?.getAttribute('data-graph-id')===anchorId;
 const oldCentre=previous?[previous.x+previous.w/2,previous.y+previous.h/2]:null;
 change();
 renderGraph(true);
 const current=graphNodes.find(n=>n.id===anchorId);
 if(oldCentre&&current){
  const newCentre=[current.x+current.w/2,current.y+current.h/2];
  setBox([oldBox[0]+newCentre[0]-oldCentre[0],
          oldBox[1]+newCentre[1]-oldCentre[1],oldBox[2],oldBox[3]]);
 }
 if(hadFocus)[...svg.querySelectorAll('[data-graph-id]')].find(n=>n.getAttribute('data-graph-id')===anchorId)?.focus();
}
function toggleTreeFamily(name){
 changeTreeWithoutCameraJump(()=>{
  if(expanded.has(name))expanded.delete(name);else expanded.add(name);
 },'family:'+name);
}
function orderFamilyRows(items){
 // The ordering is topological only for actual directed dependency edges. A
 // tie is sorted by label for browsing, not represented as a new relation.
 const ids=new Set(items.map(x=>x.id)); const incoming=new Map(items.map(x=>[x.id,0]));
 const targetEdges=DATA.edges.filter(e=>ids.has(e.from)&&ids.has(e.to)&&!['HISTORICAL_CONTEXT','COMPARED_WITH'].includes(e.type));
 const out=new Map(items.map(x=>[x.id,[]]));
 for(const e of targetEdges){out.get(e.from).push(e.to);incoming.set(e.to,incoming.get(e.to)+1);}
 const queue=[...items.filter(r=>incoming.get(r.id)===0)].sort((a,b)=>a.title.localeCompare(b.title,'pt-BR'));
 const result=[];
 while(queue.length){const n=queue.shift();if(result.some(r=>r.id===n.id))continue;result.push(n);for(const to of out.get(n.id)){
  incoming.set(to,incoming.get(to)-1);if(incoming.get(to)===0){queue.push(R.get(to));queue.sort((a,b)=>a.title.localeCompare(b.title,'pt-BR'));}}}
 if(result.length!==items.length) return [...items].sort((a,b)=>a.title.localeCompare(b.title,'pt-BR'));
 return result;
}


function layoutFamilies(){
 const themes=allTreeThemes().map(t=>({...t, sets:t.families.map(f=>({family:f,rows:filtered().filter(r=>nativeFamily(r)===f)})).filter(e=>e.rows.length)})).filter(t=>t.sets.length);
 const n=themes.length,compact=!themes.some(t=>t.sets.some(set=>expanded.has(set.family))),branchWidth=compact?370:566,branchGap=compact?28:40,left=35;
 const pageW=Math.max(940,left*2+n*branchWidth+(n-1)*branchGap);
 const out=[];const rootW=compact?404:452,rootH=compact?88:94;
 out.push({id:'tree:root',title:'Atlas · História experimental',subtitle:`${num(visible.size)} registros · ${themes.reduce((a,t)=>a+t.sets.length,0)} famílias nativas · ${themes.filter(t=>!t.neutral).length} temas editoriais`,type:'root',x:(pageW-rootW)/2,y:24,w:rootW,h:rootH});
 let deepest=360;
 themes.forEach((t,i)=>{
  const bx=left+i*(branchWidth+branchGap);
  const count=t.sets.reduce((a,g)=>a+g.rows.length,0);
  out.push({id:'theme:'+t.id,title:t.title,subtitle:`${count} registros · ${t.subtitle}`,type:'theme',theme:t.id,color:t.color,ordinal:i+1,x:bx+12,y:compact?160:185,w:branchWidth-24,h:compact?92:92,count});
  let y=compact?293:328;
  for(const set of t.sets){
   const fam={id:'family:'+set.family,title:familyLabel(set.family),familyKey:set.family,type:'family',theme:t.id,color:t.color,x:bx+22,y,w:branchWidth-44,h:compact?82:90,count:set.rows.length};
   out.push(fam);
   if(expanded.has(set.family)){
    const rs=orderFamilyRows(set.rows),startY=y+125,childH=102,gapY=120,childW=234;
    rs.forEach((r,j)=>out.push({id:r.id,title:r.title,type:'record',theme:t.id,parent:fam.id,
      x:bx+42+(j%2)*260,y:startY+Math.floor(j/2)*gapY,w:childW,h:childH}));
    y=startY+Math.ceil(rs.length/2)*gapY+38;
   }else y+=compact?114:132;
  }
  deepest=Math.max(deepest,y+48);
 });
 return {nodes:out,edges:[],box:[0,0,pageW,deepest],kind:'tree',themeCount:themes.length};
}
function renderTreeLinks(){
 const pos=new Map(graphNodes.map(n=>[n.id,n]));
 const rootNode=pos.get('tree:root');
 for(const t of allTreeThemes()){const theme=pos.get('theme:'+t.id);if(!theme)continue;
  const x0=rootNode.x+rootNode.w/2,x1=theme.x+theme.w/2,y0=rootNode.y+rootNode.h,y1=theme.y;
  svgPath(`M${x0},${y0} V${y0+23} H${x1} V${y1}`, '#a6bcc8',2.2,'','Organização do caderno por temas, não derivação causal.','tree-contains');
  const families=t.families.map(f=>pos.get('family:'+f)).filter(Boolean);
  if(!families.length)continue;
  const spine=theme.x+13,start=theme.y+theme.h;
  svgPath(`M${theme.x+24},${start} H${spine} V${families.at(-1).y+38}`, '#a9bcc8',1.5,'','','tree-contains');
  for(const f of families){svgPath(`M${spine},${f.y+38} H${f.x}`, '#a9bcc8',1.55,'',`Contém ${f.count} registros. Não representa predecessor.`,'tree-contains');
   const children=graphNodes.filter(n=>n.parent===f.id);
   if(!children.length)continue;
   const childSpine=f.x+10,first=f.y+f.h,last=children.at(-1).y-10;
   svgPath(`M${f.x+20},${first} H${childSpine} V${last}`, '#bdcbd5',1.3,'',`Pertencimento documental à família ${f.title}.`,'tree-contains');
   for(const child of children){const x=child.x+18,midY=child.y-10;
    svgPath(`M${childSpine},${midY} H${x} V${child.y}`, '#bdcbd5',1.25,'',`O registro pertence à família ${f.title}; esta linha NÃO declara dependência.`,'tree-contains');}
  }
 }
 const visibleEdges=treeRelationsVisible()?DATA.edges.filter(e=>pos.has(e.from)&&pos.has(e.to)):[];
 let proofLinks=0;
 for(const e of visibleEdges){const a=pos.get(e.from),b=pos.get(e.to);if(!a||!b)continue;
  const pa=pos.get(a.parent),pb=pos.get(b.parent),offset=proofLinks%4*4;
  // Paths run in row gaps and branch gutters, outside record card surfaces.
  const xa=a.x+a.w/2,xb=b.x+b.w/2,ya=a.y-10,yb=b.y-10;
  const ga=(pa?pa.x+pa.w: a.x+a.w)+14+offset;
  const gb=(pb?pb.x+pb.w: b.x+b.w)+14+offset;
  const top=Math.min(...graphNodes.filter(n=>n.type==='theme').map(n=>n.y))-14-offset;
  const route=a.theme===b.theme?`H${ga} V${yb} H${xb}`:`H${ga} V${top} H${gb} V${yb} H${xb}`;
  svgPath(`M${xa},${a.y} V${ya} ${route} V${b.y}`,LINK_COLORS[e.type]||'#226e9c',e.type==='HISTORICAL_CONTEXT'?1.35:2.2,
   ['HISTORICAL_CONTEXT','COMPARED_WITH'].includes(e.type)?'6 5':'',
   `${EDGE[e.type]||e.type}: ${e.reason===undefined?'':literalText(e.reason)}\n${e.proofs===undefined?'':literalText(e.proofs)}`,'tree-provenance',e.type!=='HISTORICAL_CONTEXT');
  proofLinks++;
 }
 // A collapsed family still makes the verified inter-family relationships
 // discoverable. The arrow summarizes existing edges; it does not invent one.
 const summary=new Map();
 for(const e of (treeRelationsVisible()?DATA.edges:[])){const a=R.get(e.from),b=R.get(e.to);if(!a||!b||nativeFamily(a)===nativeFamily(b))continue;
  const fa=pos.get('family:'+nativeFamily(a)),fb=pos.get('family:'+nativeFamily(b));if(!fa||!fb)continue;
  const key=JSON.stringify([nativeFamily(a),nativeFamily(b)]);if(!summary.has(key))summary.set(key,[]);summary.get(key).push(e);
 }
 let lanes=0;
 for(const [key,es] of summary){const [src,dst]=JSON.parse(key);const a=pos.get('family:'+src),b=pos.get('family:'+dst);
  const color=es.some(e=>e.type==='INPUT_FROM'||e.type==='DERIVED_FROM')?'#2b7799':'#9cacb9';
  const x1=a.x+a.w,y1=a.y+20,x2=b.x+b.w,y2=b.y+20,offset=(lanes%4)*4;
  const ga=x1+14+offset,gb=x2+14+offset,top=Math.min(...graphNodes.filter(n=>n.type==='theme').map(n=>n.y))-14-offset;
  svgPath(`M${x1},${y1} H${ga} V${top} H${gb} V${y2} H${x2}`,color,2.1,'7 5',
    `${es.length} relação(ões) entre ${familyLabel(src)} e ${familyLabel(dst)}, documentadas individualmente na aba Relações.`,'tree-family-evidence',true);
  lanes++;
 }
 return {proofLinks,aggregateRelations:summary.size,visibleHierarchies:graphNodes.filter(n=>n.type==='family').length};
}

function screenToWorld(x,y,target=svg){const p=target.createSVGPoint();p.x=x;p.y=y;return p.matrixTransform(target.getScreenCTM().inverse());}
function setBox(b){
 if(!b.every(Number.isFinite)||b[2]<=0||b[3]<=0)return;
 box=b;
 // One stable 100% reference; expanded and collapsed trees have different full
 // widths, but the same viewBox size must mean the same visual magnification.
 if(zoomReferenceWidth===null)zoomReferenceWidth=full[2];
 svg.setAttribute('viewBox',b.join(' '));
 $('zoomLabel').textContent=Math.round(zoomReferenceWidth/b[2]*100)+'%';
 updateMini();
}
// The Native drawer is an overlay, unlike the original reserved detail column.
// Fit the selection in the visible, unobstructed region without shrinking the map.
function focusArea(){
 const rect=svg.getBoundingClientRect(),width=globalThis.innerWidth??rect.left+rect.width,height=globalThis.innerHeight??rect.top+rect.height;
 let regions=[{left:Math.max(rect.left,0)+12,top:Math.max(rect.top,0)+12,right:Math.min(rect.left+rect.width,width)-12,bottom:Math.min(rect.top+rect.height,height)-12}];
 for(const obstacle of options.obstructions?.()??[]){
  const left=obstacle.left-12,top=obstacle.top-12,right=obstacle.right+12,bottom=obstacle.bottom+12;
  regions=regions.flatMap(r=>right<=r.left||left>=r.right||bottom<=r.top||top>=r.bottom?[r]:[
   {...r,right:Math.min(r.right,left)},{...r,left:Math.max(r.left,right)},
   {...r,bottom:Math.min(r.bottom,top)},{...r,top:Math.max(r.top,bottom)}
  ]).filter(r=>r.right>r.left&&r.bottom>r.top);
 }
 regions.sort((a,b)=>(b.right-b.left)*(b.bottom-b.top)-(a.right-a.left)*(a.bottom-a.top));
 return {rect,area:regions[0]};
}
function selectedIsObscured(id){
 if(!(options.obstructions?.()??[]).length)return false;
 const node=[...svg.querySelectorAll('[data-graph-id]')].find(n=>n.getAttribute('data-graph-id')===id),r=node?.getBoundingClientRect();if(!r)return false;
 return r.left<0||r.top<0||r.right>(globalThis.innerWidth??Infinity)||r.bottom>(globalThis.innerHeight??Infinity)||(options.obstructions?.()??[]).some(o=>r.left<o.right&&r.right>o.left&&r.top<o.bottom&&r.bottom>o.top);
}
function focusNode(id){
 const n=graphNodes.find(x=>x.id===id);if(!n)return;
 let {rect,area}=focusArea();
 // On a narrow screen the map may start below the bottom sheet. Bring the
 // work surface into view before choosing the available camera rectangle.
 if(!area||area.right-area.left<180||area.bottom-area.top<180){svg.scrollIntoView?.({block:'center',inline:'nearest',behavior:'instant'});({rect,area}=focusArea());}
 if(!area||!rect.width||!rect.height){setBox([n.x-65,n.y-80,n.w+130,n.h+160]);return;}
 const scale=Math.min((area.right-area.left)/(n.w+130),(area.bottom-area.top)/(n.h+160));
 const cx=(area.left+area.right)/2-rect.left,cy=(area.top+area.bottom)/2-rect.top;
 setBox([n.x+n.w/2-cx/scale,n.y+n.h/2-cy/scale,rect.width/scale,rect.height/scale]);
}
function zoom(f,cx,cy){const rect=svg.getBoundingClientRect();if(!rect.width)return;const p=screenToWorld(cx??rect.left+rect.width/2,cy??rect.top+rect.height/2);const w=box[2]/f;if(w<150||w>Math.max(30000,full[2]*4))return;setBox([p.x-(p.x-box[0])/f,p.y-(p.y-box[1])/f,w,box[3]/f]);}
function updateMini(){if(!mini||!full)return;mini.replaceChildren();mini.setAttribute('viewBox',full.join(' '));for(const n of graphNodes)mini.appendChild(s('rect',{x:n.x,y:n.y,width:n.w,height:n.h,rx:8,fill:n.type==='root'?'#264e6c':n.type==='theme'?'#549caa':n.type==='family'?'#77b8c5':n.id===selected?'#d49841':'#b9cbd8'}));mini.appendChild(s('rect',{x:box[0],y:box[1],width:box[2],height:box[3],fill:'#25789b0d',stroke:'#26759b','stroke-width':Math.max(2,full[2]/200)}));}
 organization.addEventListener('change',()=>{persistent.organization=organization.value;renderGraph();});
 relations.addEventListener('change',()=>{persistent.relations=relations.checked;renderGraph(true);});
 let drag=null;
 map.addEventListener('pointerdown',event=>{if(event.button!==0)return;moved=false;drag={x:event.clientX,y:event.clientY,box:[...box],id:event.pointerId};});
 map.addEventListener('pointermove',event=>{if(!drag)return;const dx=event.clientX-drag.x,dy=event.clientY-drag.y;if(!moved&&Math.hypot(dx,dy)<4)return;moved=true;if(!map.hasPointerCapture(drag.id))map.setPointerCapture(drag.id);const rect=svg.getBoundingClientRect(),scale=Math.max(box[2]/rect.width,box[3]/rect.height);setBox([drag.box[0]-dx*scale,drag.box[1]-dy*scale,drag.box[2],drag.box[3]]);});
 const stop=()=>{if(drag&&map.hasPointerCapture(drag.id))map.releasePointerCapture(drag.id);drag=null;};map.addEventListener('pointerup',stop);map.addEventListener('pointercancel',stop);
 map.addEventListener('wheel',event=>{event.preventDefault();zoom(event.deltaY<0?1.14:.877,event.clientX,event.clientY);},{passive:false});
 map.addEventListener('keydown',event=>{if(event.target!==map)return;let handled=true;if(event.key==='+'||event.key==='=')zoom(1.18);else if(event.key==='-')zoom(1/1.18);else if(event.key==='Home'||event.key==='0')setBox([...full]);else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)){const dx=event.key==='ArrowLeft'?-.08:event.key==='ArrowRight'?.08:0,dy=event.key==='ArrowUp'?-.08:event.key==='ArrowDown'?.08:0;setBox([box[0]+dx*box[2],box[1]+dy*box[3],box[2],box[3]]);}else handled=false;if(handled)event.preventDefault();});
 minimap.addEventListener('click',event=>{const p=screenToWorld(event.clientX,event.clientY,mini);setBox([p.x-box[2]/2,p.y-box[3]/2,box[2],box[3]]);});
 renderGraph(Boolean(persistent.box));
 return {locate(uid){const r=R.get(uid);if(!r||!visible.has(uid))return false;selectRecord(uid,true);return true;},destroy(){media?.removeEventListener('change',responsiveOptions);persistent.box=[...box];persistent.zoomReferenceWidth=zoomReferenceWidth;stop();},cancelPendingSelection(){stop();},camera(){return [...box];}};
}
