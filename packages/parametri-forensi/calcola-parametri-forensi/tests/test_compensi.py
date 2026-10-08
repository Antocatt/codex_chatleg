import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import compensi as c
import install


def civil(**changes):
    obj = json.loads((ROOT / 'examples/input-civile.json').read_text(encoding='utf-8'))
    obj.update(changes)
    return obj


def penal(**changes):
    obj = json.loads((ROOT / 'examples/input-penale.json').read_text(encoding='utf-8'))
    obj.update(changes)
    return obj


class CalculationTests(unittest.TestCase):
    def test_civil_golden_all_totals(self):
        r = c.calculate(civil())
        self.assertEqual(r['totals']['medio'], {'compenso':'5077.00', 'spese_generali':'761.55', 'base_cpa':'5838.55', 'cpa':'233.54', 'base_iva':'6072.09', 'iva':'1335.86', 'anticipazioni_art15':'0.00', 'totale_lordo':'7407.95', 'base_ritenuta':'5838.55', 'ritenuta':'0.00', 'netto_da_pagare':'7407.95'})
        self.assertEqual([r['totals'][x]['compenso'] for x in ['minimo','medio','massimo']], ['2538.50','5077.00','7615.50'])

    def test_penal_golden_forfettario(self):
        r = c.calculate(penal())
        self.assertEqual(r['totals']['medio'], {'compenso':'3592.00', 'spese_generali':'538.80', 'base_cpa':'4130.80', 'cpa':'165.23', 'base_iva':'4296.03', 'iva':'0.00', 'anticipazioni_art15':'0.00', 'totale_lordo':'4296.03', 'base_ritenuta':'4130.80', 'ritenuta':'0.00', 'netto_da_pagare':'4296.03'})

    def test_withholding_and_art15(self):
        r = c.calculate(civil(withholding=True, expenses_art15='100.00', expenses_art15_confirmed=True))
        t = r['totals']['medio']
        self.assertEqual([t[x] for x in ['iva','cpa','ritenuta','totale_lordo','netto_da_pagare']], ['1335.86','233.54','1167.71','7507.95','6340.24'])

    def test_no_cpa(self):
        t = c.calculate(civil(cpa=False))['totals']['medio']
        self.assertEqual([t['cpa'],t['iva'],t['totale_lordo']], ['0.00','1284.48','7123.03'])

    def test_all_boundaries(self):
        expected = [('0.01','1100'),('1100','1100'),('1100.01','5200'),('5200','5200'),('5200.01','26000'),('26000','26000'),('26000.01','52000'),('52000','52000'),('52000.01','260000'),('260000','260000'),('260000.01','520000'),('520000','520000')]
        for value, band in expected:
            with self.subTest(value=value):self.assertEqual(c.calculate(civil(value=value))['band_upper'],band)

    def test_every_table_every_band(self):
        data,_=c.load_dataset()
        for key,t in data['tables'].items():
            for bound in t['upper_bounds'] or [None]:
                with self.subTest(key=key,bound=bound):
                    req = civil(table=key, value=bound, phases=list(t['phases'])) if bound else penal(table=key,phases=list(t['phases']))
                    if key=='volontaria':req['non_contentious']=True
                    r=c.calculate(req)
                    self.assertEqual(r['status'],'ok')
                    self.assertLessEqual(c.Decimal(r['totals']['minimo']['totale_lordo']),c.Decimal(r['totals']['medio']['totale_lordo']))
                    self.assertLessEqual(c.Decimal(r['totals']['medio']['totale_lordo']),c.Decimal(r['totals']['massimo']['totale_lordo']))

    def test_missing_is_structured(self):
        r=c.calculate({'table':'tribunale'})
        self.assertEqual(r['status'],'needs_input')
        self.assertIn('value',{q['field'] for q in r['questions']})

    def test_special_case_stops_before_unnecessary_questions(self):
        with self.assertRaises(c.InputError):
            c.calculate({'table':'tribunale','special_cases':['patrocinio-stato']})

    def test_missing_completed(self):
        r=c.calculate(civil(purpose='cliente'))
        self.assertEqual(r['questions'],[{'field':'completed_on','question':c.QUESTIONS['completed_on']}])

    def test_indeterminate_explicit_band(self):
        r=c.calculate(civil(value='indeterminabile',band='52000',band_reason='Complessità ordinaria'))
        self.assertEqual(r['band_upper'],'52000')
        self.assertEqual(r['totals']['medio']['compenso'],'7616.00')

    def test_indeterminate_missing_reason(self):
        r=c.calculate(civil(value='indeterminabile',band='52000'))
        self.assertEqual(r['status'],'needs_input')

    def test_settlement_replaces_decision(self):
        r=c.calculate(civil(adjustments={'settlement':True,'reason':'Transazione giudiziale'}))
        self.assertEqual(r['totals']['medio']['compenso'],'5502.25')
        self.assertEqual(len(r['lines']),4)
        self.assertEqual(r['lines'][-1]['medio'],'2126.25')

    def test_complex_investigations(self):
        r=c.calculate(penal(table='penale-indagini-difensive',phases=['studio','istruttoria'],adjustments={'complex_investigations':True,'reason':'Particolarmente urgenti'}))
        self.assertEqual(r['totals']['medio']['compenso'],'2722.80')

    def test_plurality_caps(self):
        for n,p in [(2,'30'),(10,'270'),(11,'280'),(30,'470')]:
            with self.subTest(n=n):
                r=c.calculate(civil(adjustments={'subjects':n,'plurality_percent':p,'plurality_confirmed':True,'reason':'Stessa posizione e questioni distinte'}))
                self.assertEqual(r['status'],'ok')
        with self.assertRaises(c.InputError):c.calculate(civil(adjustments={'subjects':2,'plurality_percent':'31','plurality_confirmed':True,'reason':'Test'}))

    def test_soccombente_vat_must_be_confirmed(self):
        req=civil(purpose='soccombente',completed_on='2026-10-01')
        self.assertEqual(c.calculate(req)['status'],'needs_input')
        req['vat_recoverable']=False
        self.assertEqual(c.calculate(req)['totals']['medio']['iva'],'0.00')
        req['vat_recoverable']=True
        self.assertEqual(c.calculate(req)['totals']['medio']['iva'],'1335.86')

    def test_invalid_inputs(self):
        cases=[{'value':'-1'},{'value':'0'},{'value':'NaN'},{'value':'Infinity'},{'value':20000.0},{'value':True},{'value':'20.000,00'},{'value':'1100.001'},{'value':'520000.01'},{'table':'inventata'},{'phases':['studio','studio']},{'phases':[]},{'phases':['non-esiste']},{'normative_date':'2027-01-01'},{'normative_date':'2020-01-01'},{'normative_date':'sbagliata'},{'tax_regime':'estero'},{'tax_regime':'forfettario','withholding':True},{'cpa':'true'},{'special_cases':['patrocinio-stato']},{'special_cases':'nessuno'},{'unknown':'x'},{'adjustments':{'settlement':True,'reason':'x'},'phases':['studio']},{'adjustments':{'complex_investigations':True,'reason':'x'}},{'expenses_art15':'10','expenses_art15_confirmed':False},{'band':'52000'},{'adjustments':{'subjects':2,'reason':'x'}}]
        for changes in cases:
            with self.subTest(changes=changes),self.assertRaises(c.InputError):c.calculate(civil(**changes))

    def test_penal_nonexistent_cells_and_value(self):
        for req in [penal(table='penale-cassazione',phases=['istruttoria']),penal(table='penale-convalida-arresto',phases=['introduttiva']),penal(value='100')]:
            with self.assertRaises(c.InputError):c.calculate(req)

    def test_historical_performance_refused(self):
        with self.assertRaises(c.InputError):c.calculate(penal(completed_on='2022-10-22'))
        with self.assertRaises(c.InputError):c.calculate(penal(completed_on='2026-10-09'))

    def test_voluntary_contentious_refused(self):
        with self.assertRaises(c.InputError):c.calculate(civil(table='volontaria',phases=['compenso'],non_contentious=False))

    def test_html_escapes_user_content(self):
        page=c.render_html(c.calculate(civil(title='<script>alert(1)</script>')))
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('@page',page)

    def test_half_up(self):
        self.assertEqual(str(c.money(c.Decimal('1.005'))),'1.01')

    def test_repeatability(self):
        self.assertEqual(c.calculate(civil()),c.calculate(civil()))

    def test_bad_dataset_column_count(self):
        d,h=c.load_dataset();d=copy.deepcopy(d);d['tables']['tribunale']['phases']['studio'].pop()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data.json';p.write_text(json.dumps(d), encoding='utf-8')
            with self.assertRaises(c.InputError):c.load_dataset(p)


class SourceTests(unittest.TestCase):
    def test_all_civil_cells_match_official_html_independently(self):
        # Independent HTML table extraction vs dataset extracted from official PDF layout.
        s=(ROOT/'references/allegato-gu.txt').read_text(encoding='utf-8')
        headers=list(re.finditer(r'^\s*(\d+(?:-BIS)?)\.\s+[A-Z][A-Z ,/ÀÈÙ]+\s*$',s,re.M))
        data,_=c.load_dataset()
        for table in data['tables'].values():
            if table['kind']=='penale':continue
            n=table['number'].upper()
            indexes=[i for i,h in enumerate(headers) if h[1]==n]
            self.assertEqual(len(indexes),1,n)
            i=indexes[0]; block=s[headers[i].end():headers[i+1].start() if i+1<len(headers) else len(s)]
            rows=[]
            for line in block.splitlines():
                cells=line.split('|')[2:-1]
                if cells and all(re.fullmatch(r'\s*\d[\d.]*,\d{2}\s*',x) for x in cells):
                    parsed=[x.strip().replace('.','').replace(',','.') for x in cells]
                    if parsed != [x+'.00' for x in table['upper_bounds']]:
                        rows.append(parsed)
            self.assertEqual(rows,list(table['phases'].values()),n)

    def test_first_seven_penal_columns_against_official_html(self):
        source=(ROOT/'references/allegato-gu.txt').read_text(encoding='utf-8')
        block=source[source.index('15. GIUDIZI PENALI'):source.index('16. PROCEDURE')]
        rows=[]
        for line in block.splitlines():
            cells=line.split('|')[2:-1]
            if cells and any(re.fullmatch(r'\s*\d[\d.]*,\d{2}\s*',x) for x in cells):
                rows.append([x.strip().replace('.','').replace(',','.') if x.strip() else None for x in cells])
        self.assertEqual(len(rows),4)
        names=['giudice-pace','indagini-preliminari','indagini-difensive','convalida-arresto','cautelari-personali','cautelari-reali','gip-gup']
        data,_=c.load_dataset()
        for i,name in enumerate(names):
            expected={phase:[rows[j][i]] for j,phase in enumerate(['studio','introduttiva','istruttoria','decisionale']) if rows[j][i] is not None}
            self.assertEqual(data['tables']['penale-'+name]['phases'],expected)

    def test_source_integrity_manifest(self):
        import hashlib
        manifest=json.loads((ROOT/'references/sources.json').read_text(encoding='utf-8'))
        for name,digest in manifest['snapshots_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)


class IntegrationTests(unittest.TestCase):
    def run_cli(self,*args,input=None):
        return subprocess.run([sys.executable,str(ROOT/'scripts/compensi.py'),*args],input=input,text=True,encoding="utf-8",capture_output=True)

    def test_cli_exports_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix=Path(tmp)/'prospetto'
            r=self.run_cli('calculate',str(ROOT/'examples/input-civile.json'),'--output',str(prefix))
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual({p.suffix for p in Path(tmp).iterdir()},{'.json','.html','.csv'})
            self.assertEqual(json.loads(prefix.with_suffix('.json').read_text(encoding='utf-8'))['totals']['medio']['totale_lordo'],'7407.95')
            again=self.run_cli('calculate',str(ROOT/'examples/input-civile.json'),'--output',str(prefix))
            self.assertEqual(again.returncode,1)

    def test_cli_exit_codes_and_duplicate_keys(self):
        self.assertEqual(self.run_cli('calculate','-',input='{}').returncode,2)
        self.assertEqual(self.run_cli('calculate','-',input='{bad').returncode,1)
        self.assertEqual(self.run_cli('calculate','-',input='{"table":"a","table":"b"}').returncode,1)
        self.assertEqual(self.run_cli('verify-data').returncode,0)

    def test_install_all_paths_and_run_outside_skill(self):
        with tempfile.TemporaryDirectory(prefix='skill home ') as tmp:
            home=Path(tmp)
            for agent in ['codex','codex-legacy','claude']:
                target=install.install(agent,home)
                self.assertTrue((target/'SKILL.md').exists())
                run=subprocess.run([sys.executable,str(target/'scripts/compensi.py'),'calculate',str(target/'examples/input-penale.json')],cwd=home,text=True,encoding="utf-8",capture_output=True)
                self.assertEqual(run.returncode,0,run.stderr)
                with self.assertRaises(FileExistsError):install.install(agent,home)

    def test_frontmatter_loader_contract(self):
        # Static contract, not a claim of executing Codex's Rust loader.
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        front=text.split('---',2)[1]
        name=re.search(r'^name: (.+)$',front,re.M)[1]
        desc=re.search(r'^description: (.+)$',front,re.M)[1]
        self.assertEqual(name,install.NAME)
        self.assertLessEqual(len(name),64)
        self.assertLessEqual(len(desc),1024)


if __name__=='__main__':unittest.main()
