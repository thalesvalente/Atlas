"""Gate F3B isolado: componente real em Chromium, Python normal e -O."""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import io
import json
import os
import re
import struct
import subprocess
import sys
import time
import unittest
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright
from f3b_fixture import ROOT, NOW, TABLE, fixture, validate_synthetic

JS = ROOT / 'packages/atlas/src/atlas_viewer/static/parity04_f3b_tables.js'
CSS = ROOT / 'packages/atlas/src/atlas_viewer/static/parity04_f3b_tables.css'
OUT = Path('.test-output/atlas-parity04-f3b')
SCREENSHOTS = []
BROWSER_VERSION = None
DECLARATIONS = {TABLE: {'6': {'type': 'integer', 'unit': '1'},
                            '7': {'type': 'decimal', 'unit': '1'},
                            '8': {'type': 'boolean', 'unit': None},
                            '9': {'type': 'string', 'unit': None}}}


class F3BTables(unittest.TestCase):
    maxDiff = 1000

    @classmethod
    def setUpClass(cls):
        global BROWSER_VERSION
        cls.descriptor, cls.schema, cls.cases = fixture()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        BROWSER_VERSION = cls.browser.version
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / 'synthetic-descriptor.json').write_text(json.dumps(cls.descriptor, ensure_ascii=False, indent=2), encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.errors = []
        self.requests = []
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('console', lambda msg: self.errors.append(msg.text) if msg.type == 'error' else None)
        def refuse(route):
            self.requests.append(route.request.url)
            route.abort()
        self.page.route('**/*', refuse)
        self.page.set_content('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>F3B synthetic harness</title></head><body><main id="mount"></main></body></html>')
        self.page.add_style_tag(content=CSS.read_text(encoding='utf-8'))
        self.page.add_script_tag(content=JS.read_text(encoding='utf-8'))
        self.mount()

    def tearDown(self):
        try:
            self.assertEqual(self.errors, [], 'Browser console/page errors')
            self.assertEqual(self.requests, [], 'Unexpected resource/network request')
        finally:
            self.page.close()

    def mount(self, descriptor=None, declarations=None):
        d = self.descriptor if descriptor is None else descriptor
        return self.page.evaluate('''({d,now,types}) => {
            if(window.component) window.component.dispose();
            window.clock=now; window.original=d; window.originalJSON=JSON.stringify(d); window.events=[];
            const old=document.getElementById('mount'); const root=old.cloneNode(false); old.replaceWith(root);
            root.addEventListener('atlas-f3b-select', e=>window.events.push(e.detail));
            window.component=AtlasF3BTables.mount(root,d,{now:()=>window.clock,pageSize:10,sortTypes:types});
            return window.component.getState();
        }''', {'d': d, 'now': NOW, 'types': DECLARATIONS if declarations is None else declarations})

    def state(self):
        return self.page.evaluate('component.getState()')

    def query(self, **kwargs):
        return self.page.evaluate('(q)=>component.query(q)', kwargs)

    def exported(self):
        return json.loads(self.page.evaluate('component.exportJSON()'))

    def token(self, table=TABLE, row='nav:a-row'):
        return self.page.evaluate('([t,r])=>component.token(t,r)', [table,row])

    def select(self, token):
        return self.page.evaluate('(t)=>component.select(t)', token)

    def test_01_fidelity_all_fields_types_lexemes_and_source_unchanged(self):
        self.assertEqual(self.state()['tableCount'], 5)
        self.assertEqual(self.state()['loaded'], 16)
        self.assertEqual(self.exported(), self.descriptor)
        self.assertTrue(self.page.evaluate('JSON.stringify(original)===originalJSON'))
        r = self.exported()['tables'][0]['rows'][0]
        self.assertEqual(r['cells'][6]['literal'], '9007199254740998')
        self.assertEqual(r['cells'][7]['literal'], '0.123456789012345678901')
        self.assertEqual(r['cells'][9]['type'], 'string')
        self.assertEqual(r['cells'][13]['type'], 'array')
        self.assertEqual(r['cells'][14]['type'], 'object')
        self.assertEqual(self.exported()['unmapped_fields'], self.descriptor['unmapped_fields'])
        validate_synthetic(self.exported())

    def test_02_integer_sort_exact_and_original_order_restore(self):
        self.assertTrue(self.query(sort={'column':6,'direction':'asc'}, pageSize=100))
        got = [r['cells'][6]['literal'] for r in self.state()['rows']]
        want = sorted([r['cells'][6]['literal'] for r in self.descriptor['tables'][0]['rows']], key=int)
        self.assertEqual(got, want)
        self.assertTrue(self.query(sort=None))
        self.assertEqual([r['ordinal'] for r in self.state()['rows']], list(range(16)))
        self.assertEqual(self.exported(), self.descriptor)

    def test_03_decimal_sort_exact_and_boolean_string_types(self):
        self.assertTrue(self.query(sort={'column':7,'direction':'asc'}, pageSize=100))
        got = [r['cells'][7]['literal'] for r in self.state()['rows']]
        self.assertEqual(got, sorted(self.cases['decimals'], key=Decimal))
        self.assertTrue(self.query(sort={'column':8,'direction':'asc'}))
        flags = [r['cells'][8]['literal'] for r in self.state()['rows']]
        self.assertEqual(flags, sorted(flags))
        self.assertTrue(self.query(sort={'column':9,'direction':'asc'}))
        self.assertTrue(all(r['cells'][9]['literal']=='0.100' for r in self.state()['rows']))
        self.assertEqual(self.exported(), self.descriptor)

    def test_04_sort_requires_explicit_declaration_and_matching_units(self):
        self.mount(declarations={})
        before = self.state()['rows']
        self.assertFalse(self.query(sort={'column':6,'direction':'asc'}))
        self.assertEqual(self.state()['rows'], before)
        self.assertTrue(self.page.locator('[data-f3b="error"]').inner_text())
        changed = copy.deepcopy(self.descriptor)
        changed['tables'][0]['rows'][0]['cells'][6]['unit'] = 'kg'
        self.mount(changed)
        self.assertFalse(self.query(sort={'column':6,'direction':'asc'}))
        self.assertEqual(self.exported(), changed)

    def test_05_filter_pagination_counts_without_mutation(self):
        self.assertTrue(self.query(search='RF-SYN-001', pageSize=10))
        s = self.state()
        self.assertEqual((s['loaded'],s['filtered'],s['visible']), (16,1,1))
        self.assertTrue(self.query(search='', sort=None, page=0, pageSize=10))
        ordinals = [r['ordinal'] for r in self.state()['rows']]
        self.assertTrue(self.query(page=1))
        s = self.state()
        ordinals += [r['ordinal'] for r in s['rows']]
        self.assertEqual((s['loaded'],s['filtered'],s['visible']), (16,16,6))
        self.assertEqual(ordinals, list(range(16)))
        self.assertIn('UNKNOWN', self.page.locator('[data-f3b="summary"]').inner_text())
        self.assertEqual(s['global_total'], None)
        self.assertEqual(self.exported(), self.descriptor)

    def test_06_twenty_eight_unadmitted_stay_queryable_without_native_id(self):
        self.assertTrue(self.query(table='nav:b-table', admission='UNADMITTED_NATIVE_RF', pageSize=100))
        s = self.state()
        self.assertEqual((s['loaded'],s['filtered'],s['visible']), (28,28,28))
        self.assertTrue(all(r['identity']['native_id'] is None and r['requirement']['native_id'] is None for r in s['rows']))
        self.assertTrue(self.select(self.token('nav:b-table','nav:b-row-27')))
        text = self.page.locator('[data-f3b="detail"]').inner_text()
        self.assertIn('UNADMITTED_NATIVE_RF', text)
        self.assertIn('binding_gap', text)

    def test_07_four_unbound_tables_remain_visible(self):
        expected = self.descriptor['tables'][1:]
        self.assertEqual(len(expected), 4)
        for t in expected:
            with self.subTest(table=t['identity']['navigation_id']):
                self.assertTrue(self.query(table=t['identity']['navigation_id']))
                self.assertEqual(self.state()['loaded'], len(t['rows']))
                self.assertIn('vinculad', self.page.locator('#mount').inner_text().lower())
        self.assertEqual(self.exported()['tables'], self.descriptor['tables'])

    def test_08_domains_optional_no_filename_mime_or_product_inference(self):
        self.assertTrue(self.query(table='nav:unknown-table'))
        self.assertEqual(self.state()['loaded'], 0)
        d = self.exported()
        self.assertEqual(d['tables'][4]['domain'], 'UNKNOWN')
        self.assertEqual(d['tables'][4]['domain_origin'], 'UNKNOWN')
        self.assertEqual(d['assets'][0]['kind'], 'File')
        self.assertIsNone(d['assets'][0]['declared_product_role'])
        self.assertEqual([t['domain'] for t in d['tables']], ['RF','RNF','RES','RF','UNKNOWN'])
        self.assertEqual(d['validation']['scientific_approval'], 'NOT_EVALUATED')
        self.assertEqual(d['validation']['authenticity'], 'NOT_VERIFIED')
        text = self.page.locator('#mount').inner_text()
        self.assertIn('LEGACY_DERIVED', text)
        self.assertIn('NOT_VERIFIED', text)
        self.assertIn('NOT_EVALUATED', text)

    def test_09_category_absence_null_empty_zero_unknown_remain_distinct(self):
        cells = []
        for i in range(5):
            nav = 'nav:a-row' if i==0 else f'nav:a-row-{i}'
            self.assertTrue(self.select(self.token(TABLE,nav)))
            detail = self.page.locator('[data-f3b="detail"]').inner_text()
            self.assertIn('category_status', detail)
            cells.append(self.exported()['tables'][0]['rows'][i]['cells'][5])
        self.assertEqual([c['type'] for c in cells], ['missing','null','string','integer','string'])
        self.assertEqual([c['literal'] for c in cells], [None,None,'','0','UNKNOWN'])
        self.assertEqual([c['absence'] for c in cells], ['MISSING','NULL',None,None,None])

    def test_10_hostile_html_js_uri_and_structured_values_inert(self):
        self.assertTrue(self.query(pageSize=100))
        self.assertEqual(self.page.locator('#mount img, #mount script, #mount iframe, #mount object, #mount a[href]').count(), 0)
        self.assertIsNone(self.page.evaluate('globalThis.__f3bPwned'))
        self.assertIsNone(self.page.evaluate('({}).polluted'))
        self.assertIn('<img', self.page.locator('#mount').inner_text())
        self.assertTrue(self.select(self.token(TABLE,'nav:a-row-12')))
        self.assertIn('</script><script>', self.page.locator('[data-f3b="detail"]').inner_text())
        self.assertEqual(self.exported(), self.descriptor)

    def test_11_csv_formula_controls_headers_quotes_unicode_and_full_scope(self):
        self.assertTrue(self.query(search='RF-SYN-001'))
        text = self.page.evaluate('(t)=>component.exportCSV(t)', TABLE)
        rows = list(csv.reader(io.StringIO(text, newline='')))
        source = self.descriptor['tables'][0]
        self.assertEqual(len(rows), len(source['rows'])+1)
        self.assertTrue(all(len(row)==len(source['columns']) for row in rows))
        literals = [[c['header_literal'] for c in source['columns']]] + [
            [('MISSING' if c['type']=='missing' else 'null' if c['type']=='null' else c['literal']) for c in r['cells']]
            for r in source['rows']]
        for i,(expected,actual) in enumerate(zip(literals,rows)):
            for j,(original,neutralized) in enumerate(zip(expected,actual)):
                with self.subTest(row=i,column=j):
                    self.assertFalse(any(ord(ch)<32 or 127<=ord(ch)<=159 or ch=='\ufeff' for ch in neutralized))
                    dangerous = re.match(r'^[\s\x00-\x1f\x7f-\x9f\ufeff]*[=+\-@]', original) is not None
                    controls = any(ord(ch)<32 or 127<=ord(ch)<=159 or ch=='\ufeff' for ch in original)
                    if dangerous:
                        self.assertTrue(neutralized.startswith("'"), 'Formula not neutralized')
                    elif not controls:
                        self.assertEqual(neutralized, original)
        self.assertTrue(rows[0][18].startswith("'="))
        self.assertEqual(self.exported(), self.descriptor)
        self.page.locator('[data-f3b="export-csv"]').click()
        self.assertEqual(self.page.locator('[data-f3b="export-output"]').input_value(),text.replace('\r\n','\n'))
        self.page.locator('[data-f3b="export-json"]').click()
        self.assertEqual(json.loads(self.page.locator('[data-f3b="export-output"]').input_value()),self.descriptor)

    def test_12_neutral_selection_event_context_occurrences_and_collisions(self):
        token = self.token(TABLE,'nav:a-row-14')
        self.page.evaluate('window.events=[]')
        self.assertTrue(self.select(token))
        self.assertEqual(self.page.evaluate('events.length'),1)
        event = self.page.evaluate('events[events.length-1]')
        self.assertEqual(event, token)
        self.assertEqual(event['source_id'], self.descriptor['source']['source_id'])
        self.assertEqual(event['snapshot_id'], self.descriptor['snapshot']['snapshot_id'])
        self.assertEqual(event['row_occurrence'], 0)
        other = self.token(TABLE,'nav:a-row-15')
        self.assertEqual(other['row_occurrence'], 1)
        self.assertTrue(self.select(other))
        self.assertEqual(self.state()['selection'], other)
        rows = self.exported()['tables'][0]['rows']
        self.assertEqual(rows[14]['identity']['native_id'], rows[15]['identity']['native_id'])
        self.assertNotEqual(rows[14]['identity']['navigation_id'], rows[15]['identity']['navigation_id'])
        forged = copy.deepcopy(token)
        forged['source_id'] = 'foreign-source'
        self.assertFalse(self.select(forged))
        forged = copy.deepcopy(token)
        forged['row_occurrence'] = 99
        self.assertFalse(self.select(forged))

    def test_13_reimport_same_snapshot_invalidates_old_token(self):
        token = self.token()
        self.assertTrue(self.select(token))
        self.assertTrue(self.page.evaluate('(d)=>component.setTables(d)', self.descriptor))
        self.assertIsNone(self.state()['selection'])
        self.assertNotEqual(self.state()['session_id'], token['session_id'])
        self.assertFalse(self.select(token))
        self.assertTrue(self.select(self.token()))

    def test_14_snapshot_source_switch_does_not_merge_or_resolve_stale_links(self):
        token = self.token()
        d = copy.deepcopy(self.descriptor)
        old_source = d['source']['source_id']
        old_snapshot = d['snapshot']['snapshot_id']
        def recontext(value):
            if isinstance(value, dict):
                for key, val in list(value.items()):
                    if key=='source_id' and val==old_source:
                        value[key] = 'synthetic-other-source'
                    elif key=='snapshot_id' and val==old_snapshot:
                        value[key] = 'fixture-overlap-snapshot'
                    else:
                        recontext(val)
            elif isinstance(value, list):
                for item in value:
                    recontext(item)
        recontext(d)
        self.assertTrue(self.page.evaluate('(d)=>component.setTables(d)', d))
        self.assertFalse(self.select(token))
        self.assertEqual(self.state()['loaded'], 16)
        self.assertEqual(self.state()['tableCount'], 5)
        self.assertEqual(self.exported(), d)
        self.assertTrue(self.select(self.token()))

    def test_15_expiration_invalidates_context_and_selection(self):
        token = self.token()
        self.assertTrue(self.select(token))
        self.page.evaluate('window.clock += 3600001')
        self.assertFalse(self.select(token))
        self.assertTrue(self.state()['expired'])
        self.assertIsNone(self.state()['selection'])
        self.assertTrue(self.page.locator('[data-f3b="error"]').inner_text())

    def test_16_invalid_schema_semantics_and_quotas_denied_atomically(self):
        token = self.token()
        self.assertTrue(self.select(token))
        def mutate(kind):
            d = copy.deepcopy(self.descriptor)
            t = d['tables'][0]
            r = t['rows'][0]
            if kind=='version': d['version']='999'
            elif kind=='extra_property': d['unexpected']='x'
            elif kind=='not_run': d['validation']['descriptor_schema']='NOT_RUN'
            elif kind=='failed_semantics': d['validation']['descriptor_semantics']='FAIL'
            elif kind=='numeric_trailing_newline': r['cells'][6].update(literal='123\n',lexeme='123\n')
            elif kind=='numeric_coercion': r['cells'][6]['literal']=9007199254740993
            elif kind=='row_width': r['cells'].pop()
            elif kind=='ordinal': r['ordinal']=99
            elif kind=='duplicate_navigation': t['rows'][1]['identity']['navigation_id']=r['identity']['navigation_id']
            elif kind=='navigation_promoted': r['identity']['native_id']=r['identity']['navigation_id']
            elif kind=='unadmitted_native': d['tables'][3]['rows'][0]['requirement']['native_id']='INVENTED'
            elif kind=='utf8_cell_quota': r['cells'][17].update(literal='é'*40000,lexeme=json.dumps('é'*40000,ensure_ascii=False))
            elif kind=='structured_depth': r['cells'][13].update(literal='['*25+'0'+']'*25,lexeme='['*25+'0'+']'*25)
            elif kind=='structured_lexeme_mismatch': r['cells'][13].update(literal='[1]',lexeme='[2]')
            elif kind=='invalid_array': r['cells'][13].update(literal='{}',lexeme='{}')
            elif kind=='lexical_mismatch': r['cells'][0]['lexeme']='"different"'
            elif kind=='requirement_index': r['requirement']['fields']['title']=255
            elif kind=='resolved_binding': t['record_binding']['declared_id']='MISMATCH'
            elif kind=='coverage_count': next(c for c in d['coverage']['counts'] if c['unit']=='rows')['loaded']=999
            elif kind=='invalid_calendar': d['snapshot']['scientific_at']='2026-02-31T00:00:00Z'
            elif kind=='resolved_collision': t['record_binding'].update(declared_id='ROW-SYN-COLLISION',target_navigation_id='nav:a-row-14')
            elif kind=='ttl': d['snapshot']['expires_at']='2026-10-30T15:01:00Z'
            elif kind=='expired': d['snapshot']['expires_at']='2026-10-30T12:01:01Z'
            elif kind=='table_quota':
                small=copy.deepcopy(d['tables'][4])
                small['columns']=[]
                d['tables']=[]
                for i in range(129):
                    item=copy.deepcopy(small)
                    item['identity'].update(navigation_id=f'nav:quota-table-{i}',locator=f'/tables/{i}')
                    d['tables'].append(item)
            return d
        kinds = ['version','extra_property','not_run','failed_semantics','numeric_trailing_newline','numeric_coercion','row_width',
                 'ordinal','duplicate_navigation','navigation_promoted','unadmitted_native','utf8_cell_quota',
                 'structured_depth','structured_lexeme_mismatch','invalid_array','lexical_mismatch','requirement_index','resolved_binding',
                 'coverage_count','invalid_calendar','resolved_collision','ttl','expired','table_quota']
        for kind in kinds:
            with self.subTest(mutation=kind):
                self.assertFalse(self.page.evaluate('(d)=>component.setTables(d)',mutate(kind)))
                self.assertTrue(self.page.locator('[data-f3b="error"]').inner_text())
                if kind=='table_quota':
                    self.assertIn('SCHEMA_MAX_ITEMS',self.state()['error'])
                self.assertEqual(self.state()['selection'],token)
                self.assertEqual(self.exported(), self.descriptor)

    def test_17_keyboard_semantics_and_headers(self):
        search = self.page.locator('[data-f3b="search"]')
        self.assertTrue(search.get_attribute('aria-label') or search.get_attribute('id'))
        search.focus()
        self.page.keyboard.type('RF-SYN-001')
        self.assertEqual(self.state()['filtered'],1)
        self.page.keyboard.press('Tab')
        self.assertFalse(self.page.evaluate('document.activeElement===document.body'))
        search.fill('')
        row = self.page.locator('button[data-row-nav="nav:a-row"]')
        row.focus()
        self.page.keyboard.press('Enter')
        self.assertIsNotNone(self.state()['selection'])
        self.assertIn('RF-SYN-001',self.page.locator('[data-f3b="detail"]').inner_text())
        table = self.page.locator('#mount table')
        self.assertEqual(table.locator('caption').count(),1)
        headers = table.locator('thead th').evaluate_all('(hs)=>hs.map(h=>({id:h.id,scope:h.scope,text:h.textContent}))')
        self.assertTrue(headers)
        self.assertTrue(all(h['id'] and h['scope']=='col' for h in headers))
        associations = table.locator('tbody td').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("headers"))')
        self.assertTrue(associations and all(associations))
        texts = [h['text'] for h in headers]
        expected = [c['header_literal'] for c in self.descriptor['tables'][0]['columns']]
        self.assertEqual([x for x in texts if x in expected],expected)

    def test_18_real_browser_reflow_screenshots_1440_390_320(self):
        for width in (1440,390,320):
            with self.subTest(viewport=width):
                self.page.set_viewport_size({'width':width,'height':900})
                self.assertTrue(self.query(search='',sort=None,page=0,pageSize=10))
                overflow = self.page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
                self.assertFalse(overflow,'Table overflow escaped viewport')
                name = f'chromium-{width}.png'
                file = OUT / name
                self.page.locator('.atlas-f3b .f3b-viewport').evaluate('(v)=>{v.scrollTop=0;v.scrollLeft=0;v.scrollIntoView({block:"start",inline:"nearest"});}')
                self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1'))
                self.page.screenshot(path=str(file),full_page=False)
                raw = file.read_bytes()
                if raw[:8] != b'\x89PNG\r\n\x1a\n':
                    raise ValueError('Screenshot is not PNG')
                dimensions = struct.unpack('>II',raw[16:24])
                self.assertEqual(dimensions,(width,900))
                SCREENSHOTS.append({'file':name,'sha256':hashlib.sha256(raw).hexdigest(),
                                    'width':width,'height':900,'browser':BROWSER_VERSION})
                self.assertIsNone(self.page.evaluate('globalThis.__f3bPwned'))

    def test_19_dispose_and_new_mount_invalidate_old_session(self):
        token = self.token()
        self.assertTrue(self.select(token))
        self.page.evaluate('component.dispose()')
        self.assertFalse(self.select(token))
        self.mount()
        self.assertFalse(self.select(token))
        self.assertTrue(self.select(self.token()))

    def test_20_view_clones_cannot_mutate_dataset_or_selection(self):
        self.assertTrue(self.select(self.token()))
        self.page.evaluate('''() => { const s=component.getState(); s.rows[0].cells[0].literal='MUTATED';
            if(s.selection) s.selection.source_id='MUTATED'; }''')
        self.assertEqual(self.exported(),self.descriptor)
        self.page.evaluate("if(events.length) events[events.length-1].source_id='MUTATED'")
        self.assertEqual(self.state()['selection']['source_id'],self.descriptor['source']['source_id'])
        self.assertTrue(self.page.evaluate('JSON.stringify(original)===originalJSON'))

    def test_21_empty_dataset_and_no_tables_message(self):
        d=copy.deepcopy(self.descriptor)
        for key in ('nodes','tables','relations','assets','unmapped_fields','gaps'):
            d[key]=[]
        for c in d['coverage']['counts']:
            c.update(selected=0,loaded=0,visible=None)
        state=self.mount(d)
        self.assertEqual(state['tableCount'],0)
        self.assertIsNone(state['selection'])
        text=self.page.locator('#mount').inner_text().lower()
        self.assertRegex(text,r'nenhuma|sem tabel|vazi')
        self.assertEqual(self.exported(),d)

    def test_22_new_module_session_cannot_resolve_old_deep_link(self):
        token=self.token()
        self.assertTrue(self.select(token))
        self.page.evaluate('component.dispose()')
        # Reinitialize module closure exactly as a fresh page/session does.
        self.page.add_script_tag(content=JS.read_text(encoding='utf-8'))
        self.mount()
        self.assertNotEqual(self.state()['session_id'],token['session_id'])
        self.assertFalse(self.select(token))
        self.assertTrue(self.select(self.token()))

    def test_23_native_collision_visible_per_occurrence_without_declared_gap(self):
        d=copy.deepcopy(self.descriptor)
        d['gaps']=[g for g in d['gaps'] if g['code']!='DECLARED_COLLISION']
        for i in (14,15):
            d['tables'][0]['rows'][i]['identity']['native_id']='ROW-SYN-DUPLICATE'
        self.mount(d)
        for i in (14,15):
            with self.subTest(occurrence=i):
                self.assertTrue(self.select(self.token(TABLE,f'nav:a-row-{i}')))
                row=self.page.locator(f'tr[data-row-nav="nav:a-row-{i}"]')
                self.assertEqual(row.get_attribute('data-native-collision'),'true')
                self.assertIn('COLLISION (DERIVED_FOR_PRESENTATION)',row.inner_text())
        self.assertEqual(self.exported(),d)

    def test_24_descriptor_byte_quota_rejects_before_clone_atomically(self):
        token=self.token()
        self.assertTrue(self.select(token))
        accepted=self.page.evaluate('''() => {
            const candidate=JSON.parse(component.exportJSON());
            candidate.tables[0].rows[0].cells[17].literal='Q'.repeat(33554433);
            return component.setTables(candidate);
        }''')
        self.assertFalse(accepted)
        self.assertIn('QUOTA_DESCRIPTOR_BYTES',self.state()['error'])
        self.assertTrue(self.page.locator('[data-f3b="error"]').inner_text())
        self.assertEqual(self.state()['selection'],token)
        self.assertEqual(self.exported(),self.descriptor)


class ReceiptResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.records=[]
        self.started={}
    def startTest(self,test):
        self.started[test.id()]=time.monotonic()
        super().startTest(test)
    def record(self,test,status,detail=None):
        self.records.append({'id':test.id(),'status':status,
            'seconds':time.monotonic()-self.started.get(test.id(),time.monotonic()),'detail':detail})
    def addSuccess(self,test):
        super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):
        super().addFailure(test,err);self.record(test,'FAIL',self._exc_info_to_string(err,test))
    def addError(self,test,err):
        super().addError(test,err);self.record(test,'ERROR',self._exc_info_to_string(err,test))
    def addSkip(self,test,reason):
        super().addSkip(test,reason);self.record(test,'SKIP',reason)
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        self.record(subtest,'PASS' if err is None else 'FAIL',None if err is None else self._exc_info_to_string(err,test))


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
    head=git('rev-parse','HEAD')
    expected=os.environ.get('F3B_SHA') or os.environ.get('GITHUB_SHA')
    if expected and head!=expected:
        raise RuntimeError(f'Checkout revision mismatch: {head} vs {expected}')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(F3BTables)
    result=unittest.TextTestRunner(verbosity=2,resultclass=ReceiptResult).run(suite)
    report={'schema':'atlas-f3b-browser-qa-1','sha':head,'tree':git('rev-parse','HEAD^{tree}'),
            'parent':git('rev-parse','HEAD^'),'platform':sys.platform,'python':sys.version,
            'optimize':sys.flags.optimize,'browser':BROWSER_VERSION,'tests':result.testsRun,
            'receipt_cases':len(result.records),
            'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),
            'success':result.wasSuccessful() and not result.skipped,'test_results':result.records,
            'screenshots':SCREENSHOTS,'external_requests_expected':0,
            'fixture_scope':'5 synthetic tables; 46 rows:16 RF,1 RNF,1 RES,28 unadmitted;4 unbound;no F1 replay'}
    report['files']=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                     for p in (JS,CSS,Path(__file__),ROOT/'tests/qa/f3b_fixture.py',ROOT/'tests/fixtures/atlas_parity04_f3b_cases.json')]
    (OUT/'BROWSER-RECEIPT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    xml=ET.Element('testsuite',name='F3B Chromium real',tests=str(len(result.records)),failures=str(len(result.failures)),errors=str(len(result.errors)),skipped=str(len(result.skipped)))
    properties=ET.SubElement(xml,'properties')
    ET.SubElement(properties,'property',name='top_level_tests',value=str(result.testsRun))
    for rec in result.records:
        case=ET.SubElement(xml,'testcase',name=rec['id'],time=str(rec['seconds']))
        if rec['status']!='PASS':
            ET.SubElement(case,{'FAIL':'failure','ERROR':'error','SKIP':'skipped'}[rec['status']]).text=rec['detail'] or rec['status']
    ET.ElementTree(xml).write(OUT/'junit.xml',encoding='utf-8',xml_declaration=True)
    print('F3B_RECEIPT_JSON='+json.dumps(report,ensure_ascii=False,sort_keys=True))
    return 0 if report['success'] else 1


if __name__=='__main__':
    sys.exit(main())
