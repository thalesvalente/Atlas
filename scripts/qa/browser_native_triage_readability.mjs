/** Feature 005 visual QA: computed typography, actionable sizes and compact selected toolbar. */
import assert from 'node:assert/strict';
import {openNativePane} from './browser_native_triage_navigation.mjs';

const inspect = (page, selector) => page.locator(selector).first().evaluate(node => {
  const style = getComputedStyle(node);
  const box = node.getBoundingClientRect();
  return {font: Number.parseFloat(style.fontSize), height: box.height,
    gap: style.gap, justify: style.justifyContent, color: style.color,
    background: style.backgroundColor};
});

export async function runReadabilityChecks({browser, check, protectNetwork, report, url}) {
  const context = await browser.newContext({viewport: {width: 1440, height: 900}});
  await protectNetwork(context);
  const page = await context.newPage();
  try {
    await page.goto(url);
    await page.waitForFunction(() => !document.getElementById('native-download')?.disabled);
    await openNativePane(page, 'search');
    await page.locator('#native-search').fill('run-rf-proof');
    await check('UX_READABILITY_01_search_and_batch_are_legible', async () => {
      const field = await inspect(page, '#native-search');
      const card = await inspect(page, '.triage-result-head h3');
      const nav = await inspect(page, '#native-sidebar nav button[data-pane="tree"]');
      assert.ok(field.font >= 14 && card.font >= 16 && nav.font >= 14,
        'Search, card heading and navigation must use the new readable type scale');
      await page.locator('#native-content input[data-batch-uid]').first().check();
      const summary = await inspect(page, '#native-batch-summary');
      const primary = await inspect(page, '#native-retention');
      assert.ok(summary.font >= 14 && primary.font >= 13 && primary.height >= 44,
        'Selection summary and retention primary action must be readable and touch-sized');
      assert.equal(primary.color, 'rgb(255, 255, 255)');
      report.visual_readability.push({viewport: 1440, field, card, nav, summary, primary});
    });
    await check('UX_READABILITY_02_selected_modes_are_clustered_and_clear', async () => {
      await openNativePane(page, 'selected');
      const toolbar = await inspect(page, '#native-content > .toolbar');
      const actions = await page.locator('#native-content > .toolbar button').evaluateAll(nodes =>
        nodes.map(node => {const style = getComputedStyle(node), bounds = node.getBoundingClientRect();
          return {font: Number.parseFloat(style.fontSize), height: bounds.height, left: bounds.left};}));
      assert.equal(toolbar.justify, 'flex-start');
      assert.equal(actions.length, 5);
      assert.ok(actions.every(action => action.font >= 13 && action.height >= 44));
      assert.ok(actions.at(-1).left - actions[0].left < 750,
        'Selected-view actions should form a compact group, not span the entire viewport');
      assert.equal(await page.locator('#native-content > .toolbar button[aria-current="true"]').count(), 1);
      report.visual_readability.push({viewport: 1440, toolbar, actions});
    });
    await check('UX_READABILITY_03_comparison_headers_and_cells_are_readable', async () => {
      await page.locator('#native-content > .toolbar button').filter({hasText: /^Comparar$/}).click();
      const header = await inspect(page, '#native-content .triage-compare thead th');
      const cell = await inspect(page, '#native-content .triage-compare tbody td');
      assert.ok(header.font >= 13 && cell.font >= 14, 'Comparison table has readable headers and data');
      report.visual_readability.push({viewport: 1440, header, cell});
    });
  } finally {
    await context.close();
  }

  const mobile = await browser.newContext({viewport: {width: 390, height: 844}, isMobile: true, hasTouch: true});
  await protectNetwork(mobile);
  const phone = await mobile.newPage();
  try {
    await phone.goto(url);
    await phone.waitForFunction(() => !document.getElementById('native-download')?.disabled);
    await openNativePane(phone, 'search');
    await phone.locator('#native-search').fill('run-rf-proof');
    await phone.locator('#native-content input[data-batch-uid]').first().check();
    await check('UX_READABILITY_04_mobile_actions_remain_legible_without_global_overflow', async () => {
      const primary = await inspect(phone, '#native-retention');
      const summary = await inspect(phone, '#native-batch-summary');
      const overflow = await phone.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      assert.ok(primary.height >= 44 && primary.font >= 13 && summary.font >= 13);
      assert.ok(overflow <= 1, 'Mobile visual refinement must not introduce document-wide horizontal scrolling');
      report.visual_readability.push({viewport: 390, primary, summary, overflow});
    });
  } finally {
    await mobile.close();
  }
}
