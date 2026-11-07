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
      assert.ok(field.font >= 14 && card.font >= 16,
        'Search field and result heading must use the new readable type scale');
      await page.locator('#native-content input[data-batch-uid]').first().check();
      report.visual_readability.push({viewport: 1440, field, card});
    });
    await check('UX_READABILITY_02_selected_modes_are_clustered_and_clear', async () => {
      await openNativePane(page, 'selected');
      const nav = await inspect(page, '#native-sidebar nav button[data-pane="tree"]');
      const summary = await inspect(page, '#native-batch-summary');
      const primary = await inspect(page, '#native-retention');
      assert.ok(nav.font >= 14 && summary.font >= 14 && primary.font >= 14 && primary.height >= 36 && primary.height <= 42,
        'Selected modes must provide legible navigation, summary and primary action');
      assert.equal(primary.color, 'rgb(255, 255, 255)');
      const toolbar = await inspect(page, '#native-content > .toolbar');
      const actions = await page.locator('#native-content > .toolbar button').evaluateAll(nodes =>
        nodes.map(node => {const style = getComputedStyle(node), bounds = node.getBoundingClientRect();
          return {font: Number.parseFloat(style.fontSize), height: bounds.height, left: bounds.left};}));
      assert.equal(toolbar.justify, 'flex-start');
      assert.equal(actions.length, 5);
      assert.ok(actions.every(action => action.font >= 14 && action.height >= 36 && action.height <= 42));
      assert.ok(actions.at(-1).left - actions[0].left < 750,
        'Selected-view actions should form a compact group, not span the entire viewport');
      assert.equal(await page.locator('#native-content > .toolbar button[aria-current="true"]').count(), 1);
      report.visual_readability.push({viewport: 1440, nav, summary, primary, toolbar, actions});
    });
    await check('UX_READABILITY_03_comparison_headers_and_cells_are_readable', async () => {
      await page.locator('#native-content > .toolbar button').filter({hasText: /^Comparar$/}).click();
      const header = await inspect(page, '#native-content .triage-compare thead th');
      const cell = await inspect(page, '#native-content .triage-compare tbody td');
      assert.ok(header.font >= 14 && cell.font >= 15, 'Comparison table has readable headers and data');
      const identity = await page.locator('.triage-compare-identity').first().evaluate(node => {
        const check = node.querySelector('.triage-check');
        const input = check.querySelector('input');
        const label = check.querySelector('span');
        const title = node.querySelector('.triage-compare-title');
        const cb = check.getBoundingClientRect(), tb = title.getBoundingClientRect();
        return {checkTextVisible: getComputedStyle(label).display !== 'none',
          accessibleName: input.getAttribute('aria-label'), checked: input.checked,
          checkboxWidth: cb.width, checkboxHeight: cb.height,
          titleFont: Number.parseFloat(getComputedStyle(title).fontSize),
          titleButtonHeight: tb.height, gap: tb.left - cb.right,
          sameRow: Math.abs((cb.top+cb.height/2) - (tb.top+tb.height/2)) <= 24};
      });
      assert.equal(identity.checkTextVisible, false, 'Redundant selection label should not crowd the title');
      assert.match(identity.accessibleName, /^Selecionar /, 'Input must retain accessible name');
      assert.equal(identity.checked, true, 'Selection must survive switching to compare mode');
      assert.ok(identity.titleFont >= 15 && identity.checkboxHeight >= 36 && identity.sameRow && identity.gap >= 4 && identity.gap <= 24,
        'Checkbox and interactive title must align compactly');
      report.visual_readability.push({viewport: 1440, header, cell, identity});
    });
    await check('UX_READABILITY_05_tablet_compact_controls_and_header', async () => {
      await page.setViewportSize({width: 780, height: 845});
      const toggle = await inspect(page, '#native-menu-toggle');
      const primary = await inspect(page, '#native-retention');
      const mode = await inspect(page, '#native-content > .toolbar button');
      const geometry = await page.locator('.triage-compare-identity').first().evaluate(node => {
        const check = node.querySelector('.triage-check').getBoundingClientRect();
        const title = node.querySelector('.triage-compare-title').getBoundingClientRect();
        return {gap: title.left-check.right, aligned: Math.abs((check.top+check.height/2)-(title.top+title.height/2)) <= 24,
          documentOverflow: document.documentElement.scrollWidth-innerWidth};
      });
      assert.equal(toggle.color, 'rgb(247, 251, 255)', 'Navigation toggle must match dark header theme');
      assert.ok(toggle.height >= 36 && toggle.height <= 44 && toggle.font >= 14);
      assert.ok(primary.height >= 36 && primary.height <= 42 && mode.height >= 36 && mode.height <= 42);
      assert.ok(geometry.aligned && geometry.gap >= 4 && geometry.gap <= 24);
      assert.ok(geometry.documentOverflow <= 1, 'Tablet comparison should keep horizontal scrolling inside its region');
      report.visual_readability.push({viewport: 780, toggle, primary, mode, geometry});
    });
    await check('UX_TYPE_HIERARCHY_06_region_labels_and_tree_controls', async () => {
      await openNativePane(page, 'tree');
      const samples = {
        section: await inspect(page, '#native-sidebar nav details > summary'),
        sidebarTitle: await inspect(page, '#native-nav-title'),
        provenance: await inspect(page, '.application-provenance > summary'),
        queryLabel: await inspect(page, '.triage-query label'),
        treeOrganization: await inspect(page, '.application-tree-organization label'),
        graphControls: await inspect(page, '.editorial-tree .tree-controls label'),
        graphButton: await inspect(page, '.editorial-tree .toolbar button')
      };
      assert.ok(samples.section.font >= 16 && samples.sidebarTitle.font >= 16,
        'Region titles must be visibly stronger than ordinary sidebar options');
      assert.ok(samples.provenance.font >= 14 && samples.queryLabel.font >= 14 &&
        samples.treeOrganization.font >= 14 &&
        samples.graphControls.font >= 14 && samples.graphButton.font >= 13,
        'Controls and contextual region labels must use a consistent readable type scale');
      report.visual_readability.push({viewport: 1440, hierarchy: samples});
    });
    await check('UX_TYPE_HIERARCHY_07_custom_text_spacing_preserves_navigation', async () => {
      // Simulate user overrides as a same-origin stylesheet response. Do not
      // disable or bypass the Atlas CSP (style-src 'self').
      const styled = await browser.newContext({viewport: {width: 1440, height: 900}});
      await protectNetwork(styled);
      await styled.route('**/native_legacy_integration.css', async route => {
        const response = await route.fetch();
        assert.equal(response.status(), 200);
        const original = await response.text();
        const override = '\n/* Synthetic WCAG 1.4.12 text spacing sample */\n' +
          '.triage .sidebar nav details > summary, .triage .application-tree-organization label, ' +
          '.triage .editorial-tree .tree-controls label {' +
          'line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}';
        await route.fulfill({response, body: original + override});
      });
      const styledPage = await styled.newPage();
      try {
        await styledPage.goto(url);
        await styledPage.waitForFunction(() => !document.getElementById('native-download')?.disabled);
        await openNativePane(styledPage, 'tree');
        const samples = await styledPage.evaluate(() => {
          const get = selector => {
            const n = document.querySelector(selector), r = n.getBoundingClientRect();
            const style = getComputedStyle(n);
            return {visible: r.width > 0 && r.height > 0, scrollHeight: n.scrollHeight,
              clientHeight: n.clientHeight, letterSpacing: style.letterSpacing,
              lineHeight: style.lineHeight};
          };
          return {section: get('#native-sidebar nav details > summary'),
            navigationMode: get('.application-tree-organization label'),
            treeControls: get('.editorial-tree .tree-controls label')};
        });
        for (const sample of Object.values(samples)) {
          assert.ok(sample.visible && sample.scrollHeight <= sample.clientHeight + 2 &&
            Number.parseFloat(sample.letterSpacing) > 0,
            'The sampled region heading must reflow without clipping under user text spacing');
        }
        assert.equal(await styledPage.locator('#native-tree-mode').count(), 1,
          'Text spacing must not hide the tree mode control');
        report.visual_readability.push({viewport: 1440, text_spacing: samples});
      } finally {await styled.close();}
    });
    for (const width of [1440, 780, 390]) {
      await page.setViewportSize({width, height: 900});
      if (await page.locator('#native-clear').isEnabled()) await page.locator('#native-clear').click();
      await openNativePane(page, 'assets');
      await check(`UX_SELECTION_08_catalog_spacing_and_discoverable_deselect_all_${width}`, async () => {
        const clear = page.locator('.triage-select-actions #native-clear-batch');
        assert.equal(await clear.count(), 1, 'Deselect-all is beside select-visible/filter, outside More actions');
        assert.equal(await clear.locator('xpath=ancestor::details').count(), 0);
        const geometry = await page.locator('.catalog-reading tbody td').first().evaluate(cell => {
          const label = cell.querySelector('.triage-check'), title = cell.querySelector('.rowlink');
          const checkBounds = label.getBoundingClientRect(), titleBounds = title.getBoundingClientRect();
          return {text: cell.textContent, accessibleName: label.querySelector('input').getAttribute('aria-label'),
            gap: titleBounds.left - checkBounds.right, below: titleBounds.top - checkBounds.bottom,
            label: {x: checkBounds.x, y: checkBounds.y, width: checkBounds.width, height: checkBounds.height,
              display: getComputedStyle(label).display, marginBottom: getComputedStyle(label).marginBottom},
            title: {x: titleBounds.x, y: titleBounds.y, width: titleBounds.width, height: titleBounds.height},
            rowHeight: cell.parentElement.getBoundingClientRect().height,
            documentOverflow: document.documentElement.scrollWidth - innerWidth};
        });
        report.visual_readability.push({viewport: width, catalog_selection: geometry});
        assert.match(geometry.text, /^Selecionar\s+\S/, 'Selection text does not join the document title');
        assert.match(geometry.accessibleName, /^Selecionar /);
        assert.ok(geometry.gap >= 8 || geometry.below >= 4,
          `Selection and title have a visible gap or separate lines at ${width}px: ${JSON.stringify(geometry)}`);
        assert.ok(geometry.documentOverflow <= 1, 'Catalog spacing must keep horizontal scrolling inside the table region');
        if (width === 1440) {
          const centers = Math.abs(geometry.label.y + geometry.label.height / 2 - geometry.title.y - geometry.title.height / 2);
          assert.ok(geometry.gap >= 8 && centers <= 16 && geometry.rowHeight <= 76,
            `Wide catalog identity stays on a compact row without reducing the accessible checkbox: ${JSON.stringify(geometry)}`);
        }
        if (await clear.isEnabled()) await clear.click();
        for (const select of ['native-select-visible', 'native-select-filtered']) {
          await page.locator('#' + select).click();
          const count = Number(await page.locator('#native-batch-summary').getAttribute('data-selected-count'));
          assert.ok(count > 0);
          assert.equal(await clear.innerText(), `Desmarcar todos (${count})`);
          await clear.click();
          assert.equal(await clear.innerText(), 'Desmarcar todos (0)');
          assert.equal(await clear.isDisabled(), true);
          assert.equal(await page.locator('#native-batch-summary').getAttribute('data-selected-count'), '0');
          assert.equal(await page.locator('#native-content input[data-batch-uid]:checked').count(), 0);
          assert.equal(await page.locator('#native-select-visible').evaluate(node => node === document.activeElement), true);
        }
        for (const pane of ['selected', 'retention']) {
          await openNativePane(page, 'assets');
          await page.locator('#native-select-visible').click();
          await openNativePane(page, pane);
          await clear.click();
          assert.equal(await clear.isDisabled(), true);
          const focus = await page.evaluate(() => ({tag: document.activeElement.tagName,
            connected: document.activeElement.isConnected, disabled: !!document.activeElement.disabled}));
          assert.deepEqual(focus, {tag: 'H2', connected: true, disabled: false},
            'Clearing a selected/retention view restores focus to a connected heading');
        }
      });
    }
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
    await openNativePane(phone, 'selected');
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
