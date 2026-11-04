/* Atlas native thematic view.
 * Visual layout/card behavior adapted from the historical R4 renderer:
 * R4-RNF-RES-FIX@789611d.../src/r4/presentation/atlas_assets/
 * graph-layout.js (Git blob 1b6d4afa) and graph-cards.js (edb8ea62).
 * Authorized code reuse: Atlas PR #18 comment 6552216866. No R4 runtime,
 * HTML/inline script, proprietary data, dependencies, or domain-specific labels.
 * Organization lines are NOT scientific provenance/causation.
 */
const NS = 'http://www.w3.org/2000/svg';
const COLORS = ['#5A91E6','#14A8A3','#9B81DE','#5F8BA2'];
const text = x => String(x ?? '');
function html(tag, cls='', value=null) {
  const node=document.createElement(tag);
  if(cls)node.className=cls;
  if(value!==null)node.textContent=text(value);
  return node;
}
function svgEl(tag, attrs={}, value=null) {
  const node=document.createElementNS(NS,tag);
  for(const [k,v] of Object.entries(attrs))node.setAttribute(k,text(v));
  if(value!==null)node.textContent=text(value);
  return node;
}
function wrapped(value,max=36,limit=2) {
  const tokens=text(value).split(/\s+/),lines=[];let line='';
  for(const word of tokens) {
    if((line+' '+word).trim().length>max) {
      if(line)lines.push(line);
      line=word;
    } else line=(line+' '+word).trim();
  }
  if(line)lines.push(line);
  const result=lines.slice(0,limit);
  if(lines.length>limit && result.length)result[result.length-1]=result[result.length-1].slice(0,max-1)+'…';
  return result.length?result.map(line=>line.length>max?line.slice(0,max-1)+'…':line):['Não declarado'];
}
function rawFamily(record) {
  const field=(record.fields||[]).find(x=>x.name==='native_family');
  return record.family || (field?.type==='string'?field.text:null) || 'Família não declarada';
}
function groupThemes(families,editorial,mode) {
  const neutral=(items,prefix,label)=>{
    if(!items.length)return [];
    const count=Math.min(3,items.length),columns=Array.from({length:count},()=>[]);
    items.forEach((name,i)=>columns[i%count].push(name));
    return columns.map((members,i)=>({id:prefix+':'+i,title:label+(count>1?' · '+(i+1):''),
      subtitle:'Índice balanceado; não é relação científica',families:members,neutral:true,
      color:'#788D9B'}));
  };
  if(mode==='native')return neutral(families,'native','Famílias de origem');
  if(!editorial || editorial.schema!=='r4-atlas-editorial-map/1'||!Array.isArray(editorial.themes))
    return neutral(families,'unmapped','Famílias sem tema associado');
  const known=new Set(families),claims=new Map();
  for(const t of editorial.themes)for(const f of Array.isArray(t?.families)?t.families:[])
    if(known.has(f))claims.set(f,(claims.get(f)||0)+1);
  const mapped=editorial.themes.filter(x=>typeof x?.id==='string'&&typeof x?.title==='string')
    .map((t,i)=>({id:'editorial:'+t.id,title:t.title,
      subtitle:typeof t.subtitle==='string'?t.subtitle:'Organização editorial declarada; não causal',
      families:(Array.isArray(t.families)?t.families:[]).filter(f=>known.has(f)&&claims.get(f)===1),
      neutral:false,color:COLORS[i%COLORS.length]}))
    .filter(t=>t.families.length);
  const included=new Set(mapped.flatMap(t=>t.families));
  return [...mapped,...neutral(families.filter(f=>!included.has(f)),'unmapped','Famílias sem tema associado')];
}
export function mountR4Map(host, records, onSelect, options={}) {
  // The presentation only consumes already verified Native View occurrences.
  // Never merge entries with the same native_id or infer a source relationship.
  const byUid=new Map(records.map(r=>[r.uid,r])),byFamily=new Map();
  for(const row of records) {
    const family=rawFamily(row);
    if(!byFamily.has(family))byFamily.set(family,[]);
    byFamily.get(family).push(row);
  }
  const familyNames=[...byFamily.keys()].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  let organization='thematic',expanded=new Set(),selected=null,disposed=false;
  let positions=new Map(),drawn=[],width=960,height=640,worldWidth=960,worldHeight=640;
  let zoom=1,tx=25,ty=25,drag=null,pending=null;
  const abort=new AbortController(),signal=abort.signal;
  const listen=(element,type,callback,opts={})=>element.addEventListener(type,callback,{signal,...opts});
  const wrapper=html('section','r4-map');
  const toolbar=html('div','r4-map-toolbar');
  const modeLabel=html('label','r4-map-mode','Organização');
  const mode=html('select');
  for(const [value,label] of [['thematic','Visão temática (R4)'],['native','Famílias de origem']]) {
    const option=html('option','',label);option.value=value;mode.append(option);
  }
  mode.setAttribute('aria-label','Organização do mapa');
  modeLabel.append(mode);toolbar.append(modeLabel);
  const overlayLabel=html('label','r4-map-overlay');
  const overlay=document.createElement('input');overlay.type='checkbox';
  overlayLabel.append(overlay,document.createTextNode('Mostrar relações declaradas'));
  toolbar.append(overlayLabel);
  const buttons=html('div','r4-map-buttons');toolbar.append(buttons);
  const scene=svgEl('svg',{'class':'r4-map-svg',viewBox:'0 0 960 640',
    role:'group','aria-label':'Mapa temático por famílias da revisão'});
  const world=svgEl('g'),edgeLayer=svgEl('g',{'aria-hidden':'true'}),cards=svgEl('g');
  world.append(edgeLayer,cards);scene.append(world);
  const bottom=html('div','r4-map-bottom'),mini=svgEl('svg',{'class':'r4-map-mini',viewBox:'0 0 200 108',
    role:'button',tabindex:'0','aria-label':'Minimapa do conjunto'});
  const caption=html('p','r4-map-caption');
  bottom.append(mini,caption);
  wrapper.append(toolbar,scene,bottom);host.replaceChildren(wrapper);
  function addButton(label,fn) {
    const button=html('button','r4-map-button',label);button.type='button';
    listen(button,'click',fn);buttons.append(button);return button;
  }
  addButton('Mostrar tudo',fit);
  addButton('Zoom confortável',comfortable);
  addButton('Focar seleção',()=>{if(selected)locate(selected);});
  addButton('Expandir famílias',()=>{expanded=new Set(familyNames);refresh(true);});
  addButton('Recolher',()=>{expanded.clear();refresh(true);});
  addButton('＋',()=>scale(1.25));
  addButton('−',()=>scale(.8));
  addButton('Tela inteira',()=>{if(document.fullscreenElement===wrapper)document.exitFullscreen();
    else if(wrapper.requestFullscreen)wrapper.requestFullscreen().catch(()=>{});});
  function themes(){
    return groupThemes(familyNames,options.editorial,organization)
      .map(t=>({...t,sets:t.families.map(f=>({family:f,rows:byFamily.get(f)||[]}))
        .filter(set=>set.rows.length)})).filter(t=>t.sets.length);
  }
  function layout() {
    const groups=themes(),count=groups.length;
    const isCompact=!familyNames.some(f=>expanded.has(f));
    const branchW=isCompact?370:566,branchGap=isCompact?28:40,left=30;
    const pageW=Math.max(800,left*2+count*branchW+Math.max(0,count-1)*branchGap);
    const output=[];
    output.push({id:'r4-root',type:'root',title:'Caderno científico',
      subtitle:records.length+' registros · '+familyNames.length+' famílias declaradas',
      x:(pageW-404)/2,y:22,w:404,h:90});
    let deepest=340;
    for(let i=0;i<groups.length;i++){
      const t=groups[i],bx=left+i*(branchW+branchGap);
      const count=t.sets.reduce((sum,set)=>sum+set.rows.length,0);
      output.push({id:'theme:'+t.id,type:'theme',title:t.title,subtitle:t.subtitle,
        theme:t.id,color:t.color,ordinal:i+1,count,x:bx+12,y:isCompact?170:185,w:branchW-24,h:92});
      let y=isCompact?290:318;
      for(const set of t.sets){
        const family={id:'family:'+set.family,type:'family',title:set.family,
          theme:t.id,color:t.color,count:set.rows.length,x:bx+22,y,w:branchW-44,h:90};
        output.push(family);
        if(expanded.has(set.family)){
          const rows=set.rows.slice().sort((a,b)=>text(a.title).localeCompare(text(b.title),'pt-BR'));
          const start=y+115,childW=234,childH=102,gap=118;
          rows.forEach((entry,j)=>output.push({id:'record:'+entry.uid,uid:entry.uid,
            type:'record',title:entry.title,subtitle:entry.status||'Estado não declarado',
            theme:t.id,color:t.color,parent:family.id,x:bx+43+(j%2)*260,
            y:start+Math.floor(j/2)*gap,w:childW,h:childH}));
          y=start+Math.ceil(rows.length/2)*gap+30;
        }else y+=115;
      }
      deepest=Math.max(deepest,y+40);
    }
    drawn=output;positions=new Map(output.map(n=>[n.id,n]));
    worldWidth=pageW;worldHeight=deepest;
  }
  function link(d,stroke,width=1.6,dash='',label='') {
    const path=svgEl('path',{d,fill:'none',stroke,'stroke-width':width,
      'stroke-dasharray':dash,'stroke-linecap':'round',
      'vector-effect':'non-scaling-stroke'});
    if(label)path.append(svgEl('title',{},label));
    edgeLayer.append(path);
  }
  function drawEdges() {
    const root=positions.get('r4-root'),groups=themes();
    for(const t of groups){
      const theme=positions.get('theme:'+t.id);if(!theme)continue;
      const a=root.x+root.w/2,b=theme.x+theme.w/2;
      link('M '+a+' '+(root.y+root.h)+' V 135 H '+b+' V '+theme.y,
        '#a9bfca',2,'','Agrupamento de apresentação: não declara causalidade');
      const fam=t.sets.map(set=>positions.get('family:'+set.family)).filter(Boolean);
      for(const f of fam){
        const x=theme.x+20;
        link('M '+x+' '+(theme.y+theme.h)+' H '+(x-12)+' V '+(f.y+38)+' H '+f.x,
          '#aec3ce',1.4,'','Família declarada na revisão; relação de organização');
        const members=drawn.filter(n=>n.parent===f.id);
        for(const c of members){
          link('M '+(f.x+20)+' '+(f.y+f.h)+' V '+(c.y-12)+' H '+(c.x+14)+' V '+c.y,
            '#bfd0d9',1.25,'','Pertencimento à família, não dependência científica');
        }
      }
    }
    if(!overlay.checked)return;
    // Overlay only relations with unambiguous declared record IDs.
    const claims=new Map();
    for(const row of records){
      const idField=(row.fields||[]).find(f=>f.name==='id'&&f.type==='string');
      const key=idField?.text||row.source_key;
      if(typeof key!=='string'||!key)continue;
      if(!claims.has(key))claims.set(key,[]);
      claims.get(key).push(row.uid);
    }
    let shown=0;
    for(const relationship of options.relations||[]){
      let data;
      try{data=JSON.parse(relationship.raw_json);}catch{continue;}
      if(typeof data?.from!=='string'||typeof data?.to!=='string')continue;
      const src=claims.get(data.from),dst=claims.get(data.to);
      if(src?.length!==1||dst?.length!==1)continue;
      const a=positions.get('record:'+src[0]),b=positions.get('record:'+dst[0]);
      if(!a||!b)continue;
      link('M '+(a.x+a.w/2)+' '+a.y+' C '+(a.x+a.w/2)+' '+(a.y-35)+
        ' '+(b.x+b.w/2)+' '+(b.y-35)+' '+(b.x+b.w/2)+' '+b.y,
        '#278f97',2,'6 4','Relação declarada: '+text(data.type||data.kind||'sem tipo'));
      shown++;
    }
    caption.dataset.relations=String(shown);
  }
  function card(node) {
    const root=node.type==='root',theme=node.type==='theme',family=node.type==='family';
    const chosen=node.uid&&node.uid===selected;
    const g=svgEl('g',{transform:'translate('+node.x+' '+node.y+')',
      'class':'r4-map-card r4-map-'+node.type+(chosen?' selected':''),
      role:'button',tabindex:'0','data-r4-id':node.id,
      'aria-label':node.title,'aria-expanded':family?String(expanded.has(node.title)):'',
      'data-uid':node.uid||''});
    g.append(svgEl('rect',{width:node.w,height:node.h,rx:root?18:theme?15:12,
      class:'r4-map-surface'}));
    if(!root)g.append(svgEl('rect',{x:0,y:12,width:5,height:node.h-24,rx:2,
      fill:node.color||'#788D9B'}));
    if(theme){
      g.append(svgEl('rect',{x:15,y:14,width:36,height:30,rx:9,fill:node.color}));
      g.append(svgEl('text',{x:33,y:35,'text-anchor':'middle',
        'class':'r4-map-number'},String(node.ordinal).padStart(2,'0')));
    }
    const x=theme?65:root?20:17,max=theme?35:family?40:root?36:node.w>=240?35:28;
    wrapped(node.title,max,2).forEach((line,i)=>
      g.append(svgEl('text',{x,y:theme?27+i*18:root?30+i*19:27+i*17,
        'class':'r4-map-title'},line)));
    const subtitle=root?node.subtitle:family?
      node.count+' registros · '+(expanded.has(node.title)?'Recolher −':'Expandir +'):
      node.subtitle||'';
    g.append(svgEl('text',{x:17,y:node.h-13,'class':'r4-map-subtitle'},
      [...text(subtitle)].slice(0,80).join('')));
    g.append(svgEl('title',{},node.title+' · '+subtitle));
    return g;
  }
  function invokeCard(event) {
    const element=event.target.closest?.('.r4-map-card');
    if(!element)return;
    const node=positions.get(element.getAttribute('data-r4-id'));
    if(!node)return;
    if(node.type==='root'){fit();return;}
    if(node.type==='theme'){focusTheme(node);return;}
    if(node.type==='family'){toggleFamily(node.title);return;}
    if(node.uid){selected=node.uid;render();onSelect(byUid.get(node.uid));}
  }
  listen(cards,'click',invokeCard);
  listen(cards,'keydown',event=>{
    if(event.key==='Enter'||event.key===' '){event.preventDefault();invokeCard(event);}
  });
  function render(){
    if(disposed)return;
    edgeLayer.replaceChildren();cards.replaceChildren();
    drawEdges();
    const inView=n=>(n.x+n.w)*zoom+tx>=0&&n.x*zoom+tx<=width&&
      (n.y+n.h)*zoom+ty>=0&&n.y*zoom+ty<=height;
    for(const n of drawn)if(inView(n))cards.append(card(n));
    drawMini();
    const shown=drawn.filter(n=>n.type==='record').length;
    caption.textContent=records.length+' registros disponíveis · '+familyNames.length+
      ' famílias literais · '+shown+' registros expandidos · '+drawn.length+
      ' cartões no mapa. Linhas cinza: organização, não causalidade.'+
      (overlay.checked?' Relações sobrepostas só quando declaradas e únicas.':'');
  }
  function camera(){world.setAttribute('transform','translate('+tx+' '+ty+') scale('+zoom+')');render();}
  function fit(){
    zoom=Math.max(.45,Math.min(1.15,(width-38)/worldWidth,(height-38)/worldHeight));
    tx=(width-worldWidth*zoom)/2;ty=20;camera();
  }
  function comfortable(){
    zoom=1;tx=width/2-(worldWidth/2)*zoom;ty=20;camera();
  }
  function scale(factor){
    const next=Math.max(.35,Math.min(3.5,zoom*factor)),ratio=next/zoom;
    tx=width/2-(width/2-tx)*ratio;ty=height/2-(height/2-ty)*ratio;
    zoom=next;camera();
  }
  function center(node){
    zoom=Math.max(.8,zoom);
    tx=width/2-(node.x+node.w/2)*zoom;
    ty=height/2-(node.y+node.h/2)*zoom;camera();
  }
  function focusTheme(node){center(node);}
  function refresh(preserve=false,anchor=null){
    const previous=anchor?positions.get(anchor):null;
    const x=previous?previous.x+previous.w/2:null,y=previous?previous.y+previous.h/2:null;
    layout();
    if(anchor&&positions.has(anchor)&&x!==null&&y!==null){
      const next=positions.get(anchor);
      tx+=(x-next.x-next.w/2)*zoom;
      ty+=(y-next.y-next.h/2)*zoom;
    }
    if(!preserve)fit();else camera();
  }
  function toggleFamily(name){
    expanded.has(name)?expanded.delete(name):expanded.add(name);
    refresh(true,'family:'+name);
  }
  function locate(uid){
    const row=byUid.get(uid);
    if(!row)return false;
    const family=rawFamily(row);
    expanded.add(family);layout();
    const node=positions.get('record:'+uid);
    if(!node)return false;
    selected=uid;center(node);onSelect(row);return true;
  }
  function drawMini(){
    mini.replaceChildren(svgEl('rect',{width:200,height:108,fill:'#eef5fb'}));
    const sx=200/worldWidth,sy=108/worldHeight;
    for(const n of drawn)mini.append(svgEl('rect',{x:n.x*sx,y:n.y*sy,
      width:Math.max(1,n.w*sx),height:Math.max(1,n.h*sy),rx:1,
      fill:n.type==='root'?'#1d526a':n.type==='theme'?'#4d9ba9':
        n.type==='family'?'#86b7c6':n.uid===selected?'#d39a44':'#bccdd8'}));
    mini.append(svgEl('rect',{'class':'r4-map-camera',x:Math.max(0,-tx/zoom*sx),
      y:Math.max(0,-ty/zoom*sy),width:Math.min(200,width/zoom*sx),
      height:Math.min(108,height/zoom*sy)}));
  }
  listen(mode,'change',()=>{organization=mode.value;refresh();});
  listen(overlay,'change',render);
  listen(scene,'pointerdown',e=>{
    if(e.button!==0||e.target.closest('.r4-map-card'))return;
    drag={x:e.clientX,y:e.clientY,tx,ty};scene.setPointerCapture(e.pointerId);
  });
  listen(scene,'pointermove',e=>{
    if(!drag)return;
    const rect=scene.getBoundingClientRect();
    tx=drag.tx+(e.clientX-drag.x)*width/rect.width;
    ty=drag.ty+(e.clientY-drag.y)*height/rect.height;camera();
  });
  listen(scene,'pointerup',()=>{drag=null;});
  listen(scene,'pointercancel',()=>{drag=null;});
  listen(scene,'wheel',e=>{e.preventDefault();scale(e.deltaY<0?1.12:1/1.12);},
    {passive:false});
  listen(scene,'keydown',e=>{
    const directions={ArrowLeft:[40,0],ArrowRight:[-40,0],ArrowUp:[0,40],ArrowDown:[0,-40]};
    if(directions[e.key]){e.preventDefault();tx+=directions[e.key][0];
      ty+=directions[e.key][1];camera();}
  });
  listen(mini,'click',e=>{
    const rect=mini.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width*worldWidth,
      y=(e.clientY-rect.top)/rect.height*worldHeight;
    tx=width/2-x*zoom;ty=height/2-y*zoom;camera();
  });
  listen(mini,'keydown',e=>{if(e.key==='Enter'){e.preventDefault();fit();}});
  const resize=new ResizeObserver(()=>{
    width=Math.max(300,scene.clientWidth);height=scene.clientHeight||640;
    scene.setAttribute('viewBox','0 0 '+width+' '+height);camera();
  });
  resize.observe(scene);layout();fit();
  return {
    locate,
    cancelPendingSelection(){if(pending!==null){clearTimeout(pending);pending=null;}},
    destroy(){
      disposed=true;resize.disconnect();abort.abort();
      if(pending!==null)clearTimeout(pending);
      wrapper.remove();host.replaceChildren();
    }
  };
}
