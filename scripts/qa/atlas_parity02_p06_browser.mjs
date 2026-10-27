/** Valid-package replacement, stale selection/detail and scoped keyboard links. */
import {chromium} from 'playwright';
import {readFile, writeFile} from 'node:fs/promises';

const args = Object.fromEntries(process.argv.slice(2).reduce((items, value, i, all) => {
  if (i % 2 === 0) items.push([value.slice(2), all[i + 1]]);
  return items;
}, []));
for (const key of ['url', 'metadata', 'replacement', 'report']) {
  if (!args[key]) throw new Error('Missing argument: ' + key);
}
const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const receipt = {status:'FAIL',scope:'synthetic valid-package replacement on installed viewer',
  checks:[], external_requests:[],page_errors:[],browser_version:browser.version()};
const check = (name, condition) => {
  receipt.checks.push({name,status:condition?'PASS':'FAIL'});
  if (!condition) throw new Error(name);
};
page.on('request', request => {
  if (new URL(request.url()).origin !== new URL(args.url).origin)
    receipt.external_requests.push(request.url());
});
page.on('pageerror', error => receipt.page_errors.push(error.message));
try {
  await page.goto(args.url, {waitUntil:'networkidle'});
  await page.locator('[data-testid="run-open"]').first().waitFor();
  const initial = await page.evaluate(async()=>await (await fetch('/api/catalog')).json());
  const [sourceA,sourceB] = initial.sources;
  const [runA] = sourceA.read_model.runs, [runB,targetB] = sourceB.read_model.runs;
  check('fixture_has_repeated_ids_and_distinct_source_labels',
    runA.id===runB.id && runA.name!==runB.name && sourceA.id!==sourceB.id);
  const open = run => page.getByRole('button',{name:run.name,exact:true});
  const select = run => page.getByRole('checkbox',{name:'Comparar '+run.name,exact:true});
  await select(runA).check();
  await select(runB).check();
  await open(runA).click();
  const detail = page.locator('#detail');
  check('old_detail_opened_from_source_A',
    await detail.isVisible() && (await page.locator('#detail-content > code').textContent())===runA.id);

  // This is the sole deliberate source mutation, performed by the fixture driver.
  await writeFile(args.metadata, await readFile(args.replacement));
  const stale = await page.evaluate(async()=>await (await fetch('/api/catalog')).json());
  check('valid_replacement_is_marked_changed_without_silent_cache_substitution',
    stale.sources[0].status==='CHANGED' &&
    stale.sources[0].read_model.runs[0].id===runA.id &&
    stale.sources[1].status==='READY');
  await Promise.all([
    page.waitForResponse(response=>new URL(response.url()).pathname==='/api/reindex' &&
      response.request().method()==='POST' && response.status()===200),
    page.locator('#refresh').click(),
  ]);
  await page.getByRole('button',{name:runA.name.replace('[P06-A]','[P06-A-NEW]'),exact:true}).waitFor();
  check('obsolete_detail_is_closed_instead_of_resolving_same_id_in_source_B',
    !(await detail.isVisible()) && await open(runA).count()===0);
  check('only_unaffected_source_selection_survives_reindex',
    await select(runB).isChecked() &&
    (await page.locator('#selected-count').textContent()).startsWith('1 '));
  const refreshed = await page.evaluate(async()=>await (await fetch('/api/catalog')).json());
  check('replacement_has_new_ids_and_other_source_keeps_original_ids',
    refreshed.sources[0].status==='READY' &&
    refreshed.sources[0].read_model.runs.every(run=>run.id!==runA.id) &&
    refreshed.sources[1].read_model.runs[0].id===runB.id);
  await open(runB).click();
  const related = page.locator('[data-testid="related-references"]')
    .getByRole('button',{name:targetB.name,exact:true});
  await related.focus();
  check('source_B_related_link_receives_keyboard_focus', await related.evaluate(e=>e===document.activeElement));
  await page.keyboard.press('Enter');
  await page.locator('#detail-content > h3').first().filter({hasText:targetB.name}).waitFor();
  check('keyboard_reference_remains_scoped_after_other_package_is_replaced',
    (await page.locator('#detail-content > code').textContent())===targetB.id &&
    (await page.locator('#detail-content').textContent()).includes('[P06-B]') &&
    !(await page.locator('#detail-content').textContent()).includes('[P06-A-NEW]'));
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:args.report.replace(/\.json$/,'.png'),fullPage:true});
  check('replacement_navigation_reflows_at_390_pixels',
    await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  check('no_page_error_or_external_request',
    receipt.page_errors.length===0 && receipt.external_requests.length===0);
  receipt.status='PASS_SCOPED';
} catch (error) {
  receipt.error=String(error.message);
} finally {
  await writeFile(args.report,JSON.stringify(receipt,null,2)+'\n');
  await browser.close();
}
process.exitCode=receipt.status==='PASS_SCOPED'?0:1;
