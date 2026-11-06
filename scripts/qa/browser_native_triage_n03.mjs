/** Keyboard regressions reproduced on the accepted Feature 005 candidate. */
import assert from 'node:assert/strict';
import {openNativePane, revealNativeControl} from './browser_native_triage_navigation.mjs';

export async function runN03Checks({browser, check, expected, protectNetwork, report, url}) {
  const context = await browser.newContext({viewport: {width: 1440, height: 1200}});
  const uid = JSON.stringify(expected.uids['run-rf-proof']);
  const result = page => page.locator(`#native-content [data-result-uid=${uid}]`);
  const resultDetails = page => result(page).getByRole('button', {name: 'Ver detalhes', exact: true});
  const detail = page => page.locator('#native-detail');
  const detailCheckbox = page => detail(page).getByRole('checkbox', {name: /^Selecionar /});
  const hasFocus = locator => locator.evaluate(node => node === document.activeElement);
  const count = page => page.locator('#native-batch-summary').getAttribute('data-selected-count');
  await protectNetwork(context);

  const journey = (name, run) => check(name, async () => {
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(error.message));
    page.setDefaultTimeout(10000);
    try {
      await page.goto(url);
      await page.waitForFunction(() => !document.getElementById('native-download').disabled);
      await openNativePane(page, 'search');
      await page.locator('#native-search').fill('run-rf-proof');
      await run(page);
    } finally {
      await page.close();
    }
  });

  try {
    await journey('N03_escape_from_detail_checkbox_closes_details_and_restores_trigger', async page => {
      const trigger = resultDetails(page);
      await trigger.focus();
      await page.keyboard.press('Enter');
      assert.equal(await detail(page).isVisible(), true);
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      assert.equal(await hasFocus(detailCheckbox(page)), true);
      await page.keyboard.press('Space');
      assert.equal(await count(page), '1');
      await page.keyboard.press('Escape');
      assert.equal(await detail(page).isHidden(), true);
      assert.equal(await hasFocus(trigger), true);
      assert.equal(await count(page), '1');
    });

    await journey('N03_clearing_batch_from_search_moves_focus_out_of_hidden_bar', async page => {
      await result(page).getByRole('checkbox').focus();
      await page.keyboard.press('Space');
      const clear = await revealNativeControl(page, page.locator('#native-clear-batch'));
      await clear.focus();
      await page.keyboard.press('Space');
      assert.equal(await count(page), '0');
      assert.equal(await page.locator('#native-batch-bar').isHidden(), true);
      assert.equal(await hasFocus(page.locator('#native-select-visible')), true);
    });

    await journey('N03_plan_updates_immediately_without_stealing_focus_from_details', async page => {
      await result(page).getByRole('checkbox').check();
      await page.locator('#native-retention').click();
      await resultDetails(page).click();
      await detailCheckbox(page).focus();
      await page.keyboard.press('Space');
      assert.equal(await count(page), '0');
      assert.equal(await result(page).count(), 0);
      assert.equal(await page.locator('#native-export-plan').count(), 0);
      assert.equal(await hasFocus(detailCheckbox(page)), true);
      assert.equal(await detailCheckbox(page).isChecked(), false);
    });

    await journey('N03_breakpoint_preserves_content_focus_and_returns_open_drawer_focus', async page => {
      const search = page.locator('#native-search'), toggle = page.locator('#native-menu-toggle');
      await page.setViewportSize({width: 850, height: 1000});
      await page.waitForFunction(() => document.getElementById('native-menu-toggle').textContent === 'Expandir navegação');
      await search.focus();
      await page.setViewportSize({width: 390, height: 844});
      await page.waitForFunction(() => document.getElementById('native-menu-toggle').textContent === 'Menu');
      assert.equal(await hasFocus(search), true);
      await toggle.focus();
      await page.keyboard.press('Enter');
      assert.equal(await hasFocus(page.locator('#native-nav-close')), true);
      await page.setViewportSize({width: 1440, height: 1200});
      await page.waitForFunction(() => !document.getElementById('native-sidebar').hasAttribute('aria-modal'));
      assert.equal(await hasFocus(toggle), true);
    });
  } finally {
    await context.close();
  }
}
