import {openNativePane,revealNativeControl} from './browser_native_triage_navigation.mjs';
import assert from 'node:assert/strict';

const panels = [
  [{width:1440,height:1200},{width:1101,height:900},{width:1100,height:900},
   {width:1024,height:900},{width:800,height:1000},{width:721,height:900},{width:720,height:900}],
  [{width:390,height:844},{width:320,height:740}],
];
const colors = {
  neutral:['#526978','#536c7b','#8597a4','#7d92a4'],
  failed:['#9e3447','#962f43','#b33e53','#b54353'],
  succeeded:['#116b4d','#12694d','#11866a','#147b59'],
  technical:['#285f8a','#295c82','#40779f','#326d9c'],
  mixed:['#87570d','#8a5b16','#b87724','#ae731e'],
  blocked:['#666324','#666324','#87924a','#858347'],
};
const rgb = hex => 'rgb('+hex.slice(1).match(/../g).map(v=>parseInt(v,16)).join(', ')+')';
const luminance = color => color.match(/\d+/g).map(Number).map(v=>v/255)
  .map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4)
  .reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
const contrast = (fg,bg) => {
  const values=[luminance(fg),luminance(bg)].sort((a,b)=>a-b);
  return (values[1]+.05)/(values[0]+.05);
};

async function openNotebook(page,url,report){
  page.on('pageerror',error=>report.errors.push(error.message));
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>!document.querySelector('#native-download')?.disabled);
}

async function chooseRecord(page,id){
  await page.locator('#native-search').fill(id);
  const index=page.locator('#native-record-index [data-uid]');
  await revealNativeControl(page,index);
  assert.equal(await index.count(),1);
  await index.click();
  return index;
}

async function sampleMinimap(page,touch){
  const mini=page.locator('.editorial-minimap');
  await mini.scrollIntoViewIfNeeded();
  const probe=await mini.evaluate(el=>{
    const {x,y,width,height}=el.getBoundingClientRect();
    const fractions=[.1,.3,.5,.7,.9];
    const points=fractions.flatMap(u=>fractions.map(v=>[x+u*width,y+v*height]));
    const hit=points.map(([px,py])=>el.contains(document.elementFromPoint(px,py)));
    const close=document.getElementById('native-close-detail');
    const rect=close.getBoundingClientRect();
    const closeReachable=!rect.width||close.contains(document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height/2));
    return {bounds:{x,y,width,height}, viewport:[innerWidth,innerHeight],closeReachable,
      hit:hit.filter(Boolean).length, inViewport:x>=0&&y>=0&&x+width<=innerWidth&&y+height<=innerHeight,
      detailsIntersect:points.filter(([px,py])=>{
        const overlay=document.elementFromPoint(px,py)?.closest('#native-detail');
        return overlay&&!overlay.contains(el);
      }).length};
  });
  // No DOM click or event dispatch. The browser chooses the actual hit target.
  if(probe.hit===25&&probe.inViewport){
    const svg=page.locator('.editorial-svg');
    const before=await svg.getAttribute('viewBox');
    for(const fraction of [.1,.7]){
      const x=probe.bounds.x+probe.bounds.width*fraction, y=probe.bounds.y+probe.bounds.height*fraction;
      if(touch) await page.touchscreen.tap(x,y);
      else await page.mouse.click(x,y);
      probe.cameraMoved=before!==await svg.getAttribute('viewBox');
      if(probe.cameraMoved) break;
    }
  }
  return probe;
}

async function focusedCard(page){
  await page.getByRole('button',{name:'Focar seleção',exact:true}).click();
  return page.locator('.editorial-svg .svg-record.selected').evaluate(node=>{
    const card=node.querySelector('.node-surface').getBoundingClientRect();
    const detail=document.getElementById('native-detail').getBoundingClientRect();
    const map=node.ownerSVGElement.getBoundingClientRect();
    const title=node.querySelector('text');
    const scale=title.getScreenCTM();
    const font=parseFloat(getComputedStyle(title).fontSize)*Math.hypot(scale.a,scale.b);
    const overlap=card.left<detail.right&&card.right>detail.left&&card.top<detail.bottom&&card.bottom>detail.top;
    const whole=card.left>=Math.max(0,map.left)-1&&card.right<=Math.min(innerWidth,map.right)+1&&
      card.top>=Math.max(0,map.top)-1&&card.bottom<=Math.min(innerHeight,map.bottom)+1;
    return {width:card.width,height:card.height,font,overlap,whole};
  });
}

export async function checkMinimap(browser,url,desktop,id,report){
  report.minimap=[];
  const mobile=await browser.newContext({isMobile:true,hasTouch:true,viewport:panels[1][0]});
  const origin=new URL(url).origin;
  await mobile.route('**/*',async route=>{
    const target=route.request().url();
    if(new URL(target).origin===origin) await route.continue();
    else{report.external_requests.push(target);await route.abort();}
  });
  const failures=[];
  try{
    for(const [sizes,context,touch] of [[panels[0],desktop,false],[panels[1],mobile,true]]){
      const page=await context.newPage();
      await page.setViewportSize(sizes[0]);
      await openNotebook(page,url,report);
      const panel=page.locator('#native-detail');
      await chooseRecord(page,id);
      for(const viewport of sizes){
        await page.setViewportSize(viewport);
        const cell={viewport,touch,stages:{}};
        report.minimap.push(cell);
        assert.ok(await panel.isVisible(),'resizing preserves open details');
        cell.stages.resize=await sampleMinimap(page,touch);
        cell.card=await focusedCard(page);
        cell.stages.open=await sampleMinimap(page,touch);
        cell.documentScroll=await page.evaluate(()=>{
          const before=scrollY;
          window.scrollBy(0,before>=180?-180:180);
          return scrollY-before;
        });
        cell.panelScroll=await panel.evaluate(el=>{el.scrollTop=el.scrollHeight;return el.scrollTop;});
        cell.stages.scroll=await sampleMinimap(page,touch);
        if(cell.stages.scroll.hit===25){
          const svg=page.locator('.editorial-svg');
          const before=await svg.getAttribute('viewBox');
          await page.locator('.editorial-minimap').press('ArrowRight');
          cell.keyboardMoved=before!==await svg.getAttribute('viewBox');
        }
        await page.keyboard.press('Escape');
        assert.ok(await panel.isHidden(),'Escape closes the details');
        cell.focusRestored=await page.evaluate(()=>document.activeElement.matches('#native-record-index [data-uid], .svg-record.selected'));
        cell.stages.closed=await sampleMinimap(page,touch);
        const index=await chooseRecord(page,id);
        assert.ok(await panel.isVisible(),'details reopen');
        const uid=await index.getAttribute('data-uid');
        assert.equal(await page.locator('.svg-record.selected').getAttribute('data-native-node'),uid);
        cell.stages.reopen=await sampleMinimap(page,touch);
        for(const [stage,probe] of Object.entries(cell.stages)){
          if(probe.hit!==25||!probe.inViewport||!probe.cameraMoved||!probe.closeReachable||probe.bounds.width<100||probe.bounds.height<70){
            failures.push(viewport.width+' '+stage+' '+probe.hit+'/25 viewport='+probe.inViewport+' camera='+probe.cameraMoved);
          }
        }
        if(!cell.card.whole||cell.card.overlap||cell.card.font<8) failures.push(viewport.width+' foco '+JSON.stringify(cell.card));
        if(!cell.panelScroll||!cell.documentScroll||!cell.keyboardMoved||!cell.focusRestored) failures.push(viewport.width+' rolagem/teclado/foco');
      }
      await page.close();
    }
  }finally{await mobile.close();}
  assert.deepEqual(failures,[]);
}

export async function checkExecutionStates(context,url,cases,report){
  const page=await context.newPage();
  await openNotebook(page,url,report);
  report.execution_states=[];
  const failures=[];
  try{
    for(const scenario of cases){
      await openNativePane(page,'tree');
      const index=await chooseRecord(page,scenario.id);
      const node=page.locator('.svg-record.selected');
      const label=node.locator('text').nth(-2);
      const treeInk=await label.evaluate(el=>getComputedStyle(el).fill);
      const treeAccent=await node.locator('rect').nth(1).evaluate(el=>getComputedStyle(el).fill);
      const tooltip=(await node.locator('title').textContent()).split('\n').slice(1,-1).join('\n');
      const treeText=await label.textContent();
      const labelLimit=Number(await node.locator('.node-surface').getAttribute('width'))>=240?39:27;
      const detail=page.locator('#native-detail .tags .badge');
      const detailText=await detail.allTextContents();
      const detailStyle=await detail.evaluateAll(list=>list.map(el=>[getComputedStyle(el).color,getComputedStyle(el).backgroundColor]));
      const dot=await index.locator('.dot').evaluate(el=>getComputedStyle(el).backgroundColor);
      const raw=JSON.parse(await page.locator('[data-testid="native-raw"]').textContent());
      for(const [key,value] of Object.entries(scenario.fields)) assert.deepEqual(raw[key],value);
      await openNativePane(page,'records');
      const badge=page.locator('.record-reading tbody tr td:nth-child(3) .badge');
      const tableText=await badge.textContent();
      const tableStyle=await badge.evaluate(el=>[getComputedStyle(el).color,getComputedStyle(el).backgroundColor]);
      const [expectedTree,expectedBadge,expectedDot,expectedAccent]=colors[scenario.tone].map(rgb);
      const observed={id:scenario.id,tone:scenario.tone,treeInk,treeAccent,tableStyle,detailStyle,dot,
        treeText,tooltip,tableText,detailText};
      report.execution_states.push(observed);
      assert.equal(tooltip,scenario.text??'');
      assert.equal(treeText,(scenario.text??'').replaceAll('_',' ').slice(0,labelLimit));
      assert.equal(tableText,scenario.text??'Não declarado');
      assert.deepEqual(detailText,scenario.text===null?[]:[scenario.text]);
      if(treeInk!==expectedTree||treeAccent!==expectedAccent||tableStyle[0]!==expectedBadge||dot!==expectedDot||
        (detailStyle.length&&detailStyle[0][0]!==expectedBadge)){
        failures.push(scenario.id+' '+JSON.stringify({expectedTree,expectedBadge,expectedDot,expectedAccent,treeInk,treeAccent,tableStyle,detailStyle,dot}));
      }
      assert.ok(contrast(treeInk,rgb('#effaf8'))>=4.5);
      assert.ok(contrast(...tableStyle)>=4.5);
      if(detailStyle.length) assert.ok(contrast(...detailStyle[0])>=4.5);
    }
    assert.equal(await page.locator('#native-content img, #native-detail img').count(),0);
    await page.locator('#native-clear').click();
    report.record_layout=[];
    for(const width of [1440,390,320]){
      await page.setViewportSize({width,height:1000});
      const layout=await page.locator('.record-reading').evaluate(wrap=>{
        const rows=[...wrap.querySelectorAll('tbody tr')];
        return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,
          rowHeights:rows.map(row=>row.getBoundingClientRect().height),
          focusable:wrap.tabIndex===0&&wrap.getAttribute('role')==='region',
          actionHeight:rows[0].querySelector('button').getBoundingClientRect().height,
          horizontalScroll:wrap.scrollWidth-wrap.clientWidth};
      });
      assert.equal(layout.rowHeights.length,cases.length);
      assert.equal(layout.documentWidth,width);
      assert.ok(layout.focusable&&layout.actionHeight>=24);
      if(width===1440) assert.equal(layout.horizontalScroll,0);
      report.record_layout.push(layout);
    }
    assert.deepEqual(failures,[]);
  }finally{await page.close();}
}
