/** Real navigation through the responsive sidebar, shared by browser regressions.
 * Opening the drawer is part of the user journey; no DOM click, forced action,
 * skipped assertion or hidden control manipulation is used.
 */
export async function openNativePane(page, name) {
  const destination = page.locator('[data-pane="' + name + '"]');
  const toggle = page.locator('#native-menu-toggle');
  if (await toggle.count()) {
    // A viewport change updates CSS before the media-query event updates the
    // labelled drawer state. Wait for that observable state before deciding
    // whether a real click is needed; never click a stale desktop rail.
    await page.waitForFunction(() => {
      const mobile = matchMedia('(max-width:720px)').matches;
      return mobile === (document.getElementById('native-menu-toggle').textContent === 'Menu');
    });
    if (await toggle.getAttribute('aria-expanded') === 'false') await toggle.click();
  }
  await revealNativeControl(page, destination);
  await destination.click();
}

/** Open disclosure ancestors by their real summary controls before interaction. */
export async function revealNativeControl(page, control) {
  const ancestors = await control.locator('xpath=ancestor::details').all();
  for (const disclosure of ancestors) {
    if (await disclosure.getAttribute('open') === null) {
      await disclosure.locator(':scope > summary').first().click();
    }
  }
  return control;
}

/** Legacy test literals now choose typed facets by their unchanged human label. */
export async function selectNativeOption(page, id, option) {
  const control = await revealNativeControl(page, page.locator('#' + id));
  if (typeof option !== 'string' || option === '') return control.selectOption(option);
  const exactValue = await control.locator('option').evaluateAll((options, value) => options.some(item => item.value === value), option);
  return control.selectOption(exactValue ? option : {label: option});
}
