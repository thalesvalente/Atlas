/** Atlas F005 follow-up: zoom-equivalent reflow and SVG text legibility.
 * A 720x450 CSS viewport with DPR=2 approximates the layout viewport of
 * Chrome at 200% zoom in a 1440x900 physical window; this does not
 * replace an actual Chrome zoom/user test on the Windows host.
 * No corpus access, source mutations, or CSP weakening.
 */
import assert from 'node:assert/strict';
import {openNativePane, revealNativeControl} from './browser_native_triage_navigation.mjs';

const readLabel = (page, selector) => page.locator(selector).first().evaluate(node => {
  const style = getComputedStyle(node), rect = node.getBoundingClientRect();
  return {font_px: parseFloat(style.fontSize), line_height: style.lineHeight,
    visible: rect.width > 0 && rect.height > 0,
    clipped: node.scrollHeight > node.clientHeight + 2,
    text: node.textContent?.trim().slice(0,90)};
});

const readSvg = (page, physicalScale) => page.locator('.editorial-svg').evaluate((svg, dpr) => {
  const nodes = [...svg.querySelectorAll('.svg-record')];
  const samples = nodes.slice(0,30).map(node => {
    const title = node.querySelector('text'), matrix = title?.getScreenCTM();
    const nominal = title ? parseFloat(getComputedStyle(title).fontSize) : null;
    const css_px = matrix && Number.isFinite(nominal)
      ? nominal * Math.hypot(matrix.a,matrix.b) : null;
    const rect = node.getBoundingClientRect();
    return {id:node.getAttribute('data-graph-id'),title:title?.textContent,
      css_px, physical_px: css_px === null ? null : css_px*dpr,
      has_semantic_name: Boolean(node.getAttribute('aria-label') || node.querySelector('title')),
      visible_in_css_viewport: rect.right > 0 && rect.left < innerWidth &&
        rect.bottom > 0 && rect.top < innerHeight};
  });
  return {zoom_label: document.querySelector('.editorial-tree .toolbar .button-group span')?.textContent,
    total_visible_records:nodes.length, samples,
    smallest_css_px:Math.min(...samples.map(s=>s.css_px).filter(Number.isFinite)),
    small_overview_count:samples.filter(s=>s.css_px !== null && s.css_px < 12).length};
},physicalScale);

export async function runZoomReflowChecks({browser, check, protectNetwork, report, url, reportPath}) {
  report.zoom_audit ??= [];
  for(const sample of [{percent:100,width:1440,height:900,dpr:1},
                      {percent:200,width:720,height:450,dpr:2}]) {
    const context=await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:false});
    await protectNetwork(context);
    const page=await context.newPage();
    page.setDefaultTimeout(12000);
    try {
      if(sample.percent===200){
        const cdp=await context.newCDPSession(page);
        await cdp.send('Emulation.setDeviceMetricsOverride',{
          width:sample.width,height:sample.height,deviceScaleFactor:2,mobile:false});
      }
      await page.goto(url);
      await page.waitForFunction(()=>!document.querySelector('#native-download')?.disabled);
      await check('UX_ZOOM_'+sample.percent+'_navigation_heading_reflow', async()=>{
        const header=page.locator('#native-menu-toggle');
        if(await header.getAttribute('aria-expanded')==='false') await header.click();
        const section=await readLabel(page,'#native-tabs details > summary');
        const sidebar=await readLabel(page,'#native-nav-title');
        assert.ok(section.font_px>=16 && sidebar.font_px>=16);
        assert.ok(section.visible && sidebar.visible && !section.clipped && !sidebar.clipped);
        await openNativePane(page,'tree');
        const controls={
          mode:await readLabel(page,'.application-tree-organization label'),
          organization:await readLabel(page,'.editorial-tree .tree-controls label'),
          toolbar:await readLabel(page,'.editorial-tree .toolbar button')
        };
        assert.ok(controls.mode.font_px>=14 && controls.organization.font_px>=14 &&
          controls.toolbar.font_px>=13);
        const layout=await page.evaluate(()=>({css_width:innerWidth,css_height:innerHeight,
          device_pixel_ratio:devicePixelRatio,
          document_overflow:document.documentElement.scrollWidth-innerWidth,
          tree_present:!!document.querySelector('.editorial-svg'),
          minimap_present:!!document.querySelector('.editorial-minimap')}));
        assert.equal(layout.css_width,sample.width);
        assert.ok(layout.document_overflow<=1,'Atlas must reflow without global horizontal overflow');
        assert.ok(layout.tree_present && layout.minimap_present);
        report.zoom_audit.push({case:'navigation',percent:sample.percent,mode:'zoom-equivalent CSS viewport',
          layout,section,sidebar,controls});
      });
      await check('UX_ZOOM_'+sample.percent+'_svg_overview_and_focus_legibility',async()=>{
        await page.locator('#native-search').fill('run-rf-proof');
        const expand=page.getByRole('button',{name:'Expandir famílias',exact:true});
        await expand.click();
        await page.locator('.editorial-svg .svg-record').first().waitFor({state:'attached'});
        const overview=await readSvg(page,sample.dpr);
        assert.ok(overview.total_visible_records>=1);
        assert.ok(overview.samples.every(s=>s.has_semantic_name),
          'Graphic nodes require accessible names even when overview text is small');
        // A real toolbar action tests the reduced overview, close to the
        // operator's 88% tree view, without modifying the graph's DOM or camera.
        await page.getByRole('button',{name:'Afastar',exact:true}).click();
        const reduced=await readSvg(page,sample.dpr);
        assert.equal(reduced.total_visible_records,overview.total_visible_records);
        assert.ok(reduced.smallest_css_px < overview.smallest_css_px,
          'Zoom-out must actually reduce apparent SVG label size');
        await page.locator('.editorial-svg').scrollIntoViewIfNeeded();
        const reducedScreenshot=reportPath.replace('.json','-reduced-overview-'+sample.percent+'.png');
        await page.screenshot({path:reducedScreenshot,fullPage:false});
        report.screenshots.push(reducedScreenshot.split('/').at(-1));
        const index=page.locator('#native-record-index [data-uid]').first();
        await revealNativeControl(page,index);
        await index.click();
        await page.getByRole('button',{name:'Focar seleção',exact:true}).click();
        // Bring the graphic surface into the visible viewport before sampling
        // actual record exposure; do not confuse an off-screen SVG DOM node
        // with a readable record.
        await page.locator('.editorial-svg').scrollIntoViewIfNeeded();
        const focused=await page.locator('.editorial-svg .svg-record.selected').evaluate((node,dpr)=>{
          const title=node.querySelector('text'),matrix=title?.getScreenCTM();
          const css_px=matrix ? parseFloat(getComputedStyle(title).fontSize) *
            Math.hypot(matrix.a,matrix.b) : null;
          const rect=node.getBoundingClientRect();
          const detail=document.querySelector('#native-detail');
          const detailRect=detail.getBoundingClientRect();
          const overlapsDetail=!detail.hidden && rect.left<detailRect.right &&
            rect.right>detailRect.left && rect.top<detailRect.bottom &&
            rect.bottom>detailRect.top;
          const visibleInViewport=rect.right>0 && rect.left<innerWidth &&
            rect.bottom>0 && rect.top<innerHeight;
          const pointX=Math.min(innerWidth-1,Math.max(1,rect.left+rect.width/2));
          const pointY=Math.min(innerHeight-1,Math.max(1,rect.top+rect.height/2));
          const hit=document.elementFromPoint(pointX,pointY);
          return {css_px,physical_px:css_px===null?null:css_px*dpr,
            has_detail_panel:!detail.hidden,
            has_accessible_name:Boolean(node.getAttribute('aria-label') || node.querySelector('title')),
            visible_in_viewport:visibleInViewport,overlaps_detail:overlapsDetail,
            center_hittable:node.contains(hit),
            rect:{x:rect.left,y:rect.top,w:rect.width,h:rect.height},
            css_viewport:{width:innerWidth,height:innerHeight}};
        },sample.dpr);
        assert.ok(focused.css_px>0 && focused.has_accessible_name &&
          focused.has_detail_panel,
          'Focusing an SVG record must preserve an accessible route to full details');
        const warning=[
          ...(overview.small_overview_count || reduced.small_overview_count ? ['Reduced overview labels under 12 CSS px: focus or details needed'] : []),
          ...(!focused.visible_in_viewport || focused.overlaps_detail || !focused.center_hittable
            ? ['Focused SVG card not fully exposed in this viewport; human Chrome check required'] : [])
        ];
        const screenshot=reportPath.replace('.json','-zoom-'+sample.percent+'.png');
        await page.screenshot({path:screenshot,fullPage:false});
        report.screenshots.push(screenshot.split('/').at(-1));
        report.zoom_audit.push({case:'svg',percent:sample.percent,
          overview,reduced,focused,warning,screenshot:screenshot.split('/').at(-1),reducedScreenshot:reducedScreenshot.split('/').at(-1)});
      });
    } finally {await context.close();}
  }
}
