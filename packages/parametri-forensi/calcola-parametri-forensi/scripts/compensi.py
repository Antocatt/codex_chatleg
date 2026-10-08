#!/usr/bin/env python3
"""Offline Italian forensic fee engine. Python >=3.10, standard library only."""
import argparse
import csv
import hashlib
import html
import io
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENT = Decimal('0.01')
VERSION = '1.0.0'


class InputError(ValueError):
    pass


def number(value, field):
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int)):
        raise InputError(f'{field}: usare stringa decimale con punto, senza separatore migliaia')
    try:
        n = Decimal(str(value))
    except InvalidOperation as exc:
        raise InputError(f'{field}: numero non valido') from exc
    if not n.is_finite() or n < 0 or n > Decimal('1000000000000'):
        raise InputError(f'{field}: numero non finito, negativo o eccessivo')
    return n


def money(n):
    return n.quantize(CENT, rounding=ROUND_HALF_UP)


def iso(value, field):
    if not isinstance(value, str):
        raise InputError(f'{field}: data ISO YYYY-MM-DD richiesta')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f'{field}: data ISO non valida') from exc


def load_dataset(path=None):
    raw = Path(path or ROOT / 'data/tables.json').read_bytes()
    data = json.loads(raw)
    if data.get('schema_version') != 1:
        raise InputError('Versione schema tabelle non supportata')
    iso(data['verified_on'], 'verified_on')
    iso(data['effective_from'], 'effective_from')
    if not data.get('source_url', '').startswith('https://') or not data.get('dataset_version'):
        raise InputError('Provenienza dataset mancante')
    for key, table in data['tables'].items():
        bounds = [number(x, key) for x in table['upper_bounds']]
        if bounds != sorted(set(bounds)) or not table['phases']:
            raise InputError('Struttura tabella non valida: ' + key)
        for phase, row in table['phases'].items():
            if len(row) != (len(bounds) or 1):
                raise InputError('Numero colonne non valido: ' + key + '/' + phase)
            for x in row:
                number(x, key)
    for x in data['ordinary_factors'].values():
        number(x, 'ordinary_factors')
    for field in ['general_expenses_rate', 'cpa_rate', 'vat_rate', 'withholding_rate']:
        number(data[field], field)
    return data, hashlib.sha256(raw).hexdigest()


QUESTIONS = {
    'purpose': 'Preventivo, liquidazione a carico del cliente o del soccombente?',
    'table': 'Quale procedimento e autorità? Consultare il comando catalog.',
    'phases': 'Quali fasi sono state svolte o sono incluse nel preventivo?',
    'tax_regime': 'Regime fiscale ordinario italiano o forfettario?',
    'cpa': 'Applicare il contributo integrativo Cassa Forense del 4%?',
    'withholding': 'Il cliente è sostituto d’imposta e si applica la ritenuta del 20%?',
    'expenses_art15': 'Importo delle anticipazioni documentate in nome e per conto del cliente ex art. 15? Indicare 0 se assenti.',
    'normative_date': 'Qual è la data di riferimento normativo del prospetto?',
    'special_cases': 'Ci sono patrocinio a spese dello Stato, equo compenso da valutare, accordi sul compenso o altre regole speciali? Indicare [] solo se assenti.',
    'value': 'Qual è il valore ai fini dell’art. 5 D.M. 55/2014? Per indeterminabile indicare "indeterminabile".',
    'completed_on': 'Quando è stata esaurita la prestazione professionale?',
    'value_basis': 'Su quale criterio dell’art. 5 si fonda il valore (domanda, attribuito, interesse effettivo, ecc.)?',
    'band': 'Per valore indeterminabile, scegliere lo scaglione motivato: 52000, 260000 oppure 520000 per particolare importanza.',
    'band_reason': 'Motivare la scelta dello scaglione per valore indeterminabile.',
    'non_contentious': 'Confermare che il procedimento di volontaria giurisdizione è non contenzioso.',
    'expenses_art15_confirmed': 'Confermare documentazione e anticipazione in nome e per conto del cliente ai sensi dell’art. 15.',
    'vat_recoverable': 'Nella liquidazione al soccombente, l’IVA è recuperabile (non detraibile per il cliente)? Confermare con l’avvocato.',
}
REQUIRED = ['purpose', 'table', 'phases', 'tax_regime', 'cpa', 'withholding',
            'expenses_art15', 'normative_date', 'special_cases']
OPTIONAL = ['value', 'value_basis', 'band', 'band_reason', 'completed_on',
            'non_contentious', 'expenses_art15_confirmed', 'title', 'adjustments', 'vat_recoverable']


def calculate(request, dataset=None, dataset_hash=None):
    if dataset is None:
        dataset, dataset_hash = load_dataset()
    if not isinstance(request, dict):
        raise InputError('Richiesta JSON: oggetto richiesto')
    unknown = set(request) - set(REQUIRED + OPTIONAL)
    if unknown:
        raise InputError('Campi non riconosciuti: ' + ', '.join(sorted(unknown)))
    if 'special_cases' in request and (not isinstance(request['special_cases'], list) or request['special_cases']):
        raise InputError('Regole speciali da trattare separatamente: v1 non calcola patrocinio Stato, equo compenso, patti, trasferta, rimborsi diversi da art. 15 o maggiorazioni non documentate nel manuale')
    missing = [f for f in REQUIRED if f not in request]
    t = dataset['tables'].get(request.get('table')) if isinstance(request.get('table'), str) else None
    if t and t['kind'] == 'civile':
        missing += [f for f in ['value', 'value_basis'] if f not in request]
        if request.get('value') == 'indeterminabile':
            missing += [f for f in ['band', 'band_reason'] if f not in request]
    if request.get('purpose') in ['cliente', 'soccombente'] and 'completed_on' not in request:
        missing.append('completed_on')
    if request.get('purpose') == 'soccombente' and request.get('tax_regime') == 'ordinario' and 'vat_recoverable' not in request:
        missing.append('vat_recoverable')
    if request.get('table') == 'volontaria' and 'non_contentious' not in request:
        missing.append('non_contentious')
    if 'expenses_art15' in request and number(request['expenses_art15'], 'expenses_art15') > 0 and 'expenses_art15_confirmed' not in request:
        missing.append('expenses_art15_confirmed')
    if missing:
        return {'status': 'needs_input', 'questions': [{'field': f, 'question': QUESTIONS[f]} for f in missing]}
    if not t:
        raise InputError('Tabella non supportata: usare catalog; non inventare una tabella analoga')
    purpose = request['purpose']
    if purpose not in ['preventivo', 'cliente', 'soccombente']:
        raise InputError('purpose: scegliere preventivo, cliente o soccombente')
    normative = iso(request['normative_date'], 'normative_date')
    if normative > iso(dataset['verified_on'], 'verified_on'):
        raise InputError('Data normativa successiva alla verifica del dataset: aggiornare e revisionare le fonti')
    if normative < iso(dataset['effective_from'], 'effective_from'):
        raise InputError('Regime storico non implementato; non usare le tabelle 2022')
    if purpose != 'preventivo':
        completed = iso(request['completed_on'], 'completed_on')
        if completed < iso(dataset['effective_from'], 'effective_from') or completed > normative:
            raise InputError('Data prestazione incompatibile con regime 2022 o data normativa')
    regime = request['tax_regime']
    if regime not in ['ordinario', 'forfettario']:
        raise InputError('Regime fiscale non supportato: solo ordinario italiano o forfettario')
    for f in ['cpa', 'withholding']:
        if type(request[f]) is not bool:
            raise InputError(f'{f}: valore booleano richiesto')
    if regime == 'forfettario' and request['withholding']:
        raise InputError('Il regime forfettario non prevede la ritenuta sui compensi')
    if purpose == 'soccombente' and request['withholding']:
        raise InputError('La ritenuta dipende dal pagamento, non dalla liquidazione al soccombente: calcolarla separatamente')
    if 'vat_recoverable' in request and (purpose != 'soccombente' or type(request['vat_recoverable']) is not bool):
        raise InputError('vat_recoverable: booleano riservato alla liquidazione al soccombente')
    if 'title' in request and (not isinstance(request['title'], str) or len(request['title']) > 300):
        raise InputError('title: testo di massimo 300 caratteri')
    expenses = money(number(request['expenses_art15'], 'expenses_art15'))
    if expenses and request['expenses_art15_confirmed'] is not True:
        raise InputError('Spese art. 15 non confermate: non è possibile escluderle dagli imponibili')
    if request['table'] == 'volontaria' and request['non_contentious'] is not True:
        raise InputError('Tabella 7 riservata ai procedimenti non contenziosi')
    phases = request['phases']
    if not isinstance(phases, list) or not phases or any(not isinstance(p, str) for p in phases) or len(set(phases)) != len(phases):
        raise InputError('phases: elenco non vuoto di fasi uniche richiesto')
    if any(p not in t['phases'] for p in phases):
        raise InputError('Fase non tabellata; fasi consentite: ' + ', '.join(t['phases']))
    band_index = 0
    band = None
    if t['kind'] == 'penale':
        if any(f in request for f in ['value', 'value_basis', 'band', 'band_reason']):
            raise InputError('Il penale non utilizza valore o scaglione della causa')
    else:
        if not isinstance(request['value_basis'], str) or not request['value_basis'].strip():
            raise InputError('Motivazione del valore richiesta')
        if request['value'] == 'indeterminabile':
            band = str(request['band'])
            if band not in ['52000', '260000', '520000'] or band not in t['upper_bounds'] or not isinstance(request['band_reason'], str) or not request['band_reason'].strip():
                raise InputError('Scaglione indeterminabile non valido o non motivato')
            band_index = t['upper_bounds'].index(band)
        else:
            value = number(request['value'], 'value')
            if value != money(value) or value <= 0:
                raise InputError('value: importo positivo, al massimo due decimali')
            if 'band' in request or 'band_reason' in request:
                raise InputError('Scaglione manuale riservato al valore indeterminabile')
            for i, upper in enumerate(t['upper_bounds']):
                if value <= Decimal(upper):
                    band_index, band = i, upper
                    break
            else:
                raise InputError('Valore oltre la tabella: art. 6 e valori oltre 520.000 non implementati nella v1')
    adj = request.get('adjustments', {})
    if not isinstance(adj, dict) or set(adj) - {'settlement', 'complex_investigations', 'plurality_percent', 'subjects', 'plurality_confirmed', 'reason'}:
        raise InputError('adjustments: campi non validi')
    for f in ['settlement', 'complex_investigations', 'plurality_confirmed']:
        if f in adj and type(adj[f]) is not bool:
            raise InputError(f'adjustments.{f}: booleano richiesto')
    if adj and (not isinstance(adj.get('reason'), str) or not adj['reason'].strip()):
        raise InputError('Motivare le regole speciali selezionate in adjustments.reason')
    settlement = adj.get('settlement', False)
    investigation = adj.get('complex_investigations', False)
    if settlement and (t['kind'] != 'civile' or 'decisionale' not in phases or request['table'] in ['corti-superiori', 'corte-conti']):
        raise InputError('Conciliazione/transazione: richiede fase decisionale civile applicabile; non duplicare la fase')
    if investigation and request['table'] != 'penale-indagini-difensive':
        raise InputError('Aumento del 20% riservato alle indagini difensive complesse o urgenti')
    plurality = number(adj.get('plurality_percent', '0'), 'plurality_percent')
    if plurality:
        subjects = adj.get('subjects')
        if type(subjects) is not int or subjects < 2 or subjects > 30 or adj.get('plurality_confirmed') is not True:
            raise InputError('Pluralità: confermare presupposti art. 4/12 comma 2 e numero soggetti da 2 a 30')
        cap = Decimal(30 * (min(subjects, 10) - 1) + 10 * max(subjects - 10, 0))
        if plurality > cap:
            raise InputError('Maggiorazione pluralità superiore al limite normativo')
    elif any(f in adj for f in ['subjects', 'plurality_confirmed']):
        raise InputError('Soggetti indicati senza maggiorazione: esplicitare plurality_percent maggiore di zero o rimuoverli')
    lines = []
    for phase in phases:
        base = Decimal(t['phases'][phase][band_index])
        factor = (Decimal('1.25') if settlement and phase == 'decisionale' else Decimal(1)) * (Decimal('1.20') if investigation else Decimal(1))
        # Ordinary variation, then phase-specific rule, then plurality. Round each final phase once.
        amounts = {level: str(money(base * Decimal(mult) * factor * (1 + plurality / 100))) for level, mult in dataset['ordinary_factors'].items()}
        lines.append({'phase': phase, 'label': 'conciliazione/transazione (sostituisce decisionale)' if settlement and phase == 'decisionale' else phase,
                      'table_medium': str(base), 'special_factor': str(factor), 'plurality_percent': str(plurality), **amounts})
    totals = {}
    for level in dataset['ordinary_factors']:
        fee = sum((Decimal(row[level]) for row in lines), Decimal(0))
        general = money(fee * Decimal(dataset['general_expenses_rate']) / 100)
        cpa_base = fee + general
        cpa = money(cpa_base * Decimal(dataset['cpa_rate']) / 100) if request['cpa'] else Decimal('0.00')
        vat_base = cpa_base + cpa
        vat_due = regime == 'ordinario' and (purpose != 'soccombente' or request['vat_recoverable'])
        vat = money(vat_base * Decimal(dataset['vat_rate']) / 100) if vat_due else Decimal('0.00')
        withholding = money(cpa_base * Decimal(dataset['withholding_rate']) / 100) if request['withholding'] else Decimal('0.00')
        gross = fee + general + cpa + vat + expenses
        totals[level] = {k: str(money(v)) for k, v in {'compenso': fee, 'spese_generali': general, 'base_cpa': cpa_base,
                         'cpa': cpa, 'base_iva': vat_base, 'iva': vat, 'anticipazioni_art15': expenses,
                         'totale_lordo': gross, 'base_ritenuta': cpa_base, 'ritenuta': withholding, 'netto_da_pagare': gross - withholding}.items()}
    canonical = json.dumps(request, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    return {'status': 'ok', 'engine_version': VERSION, 'dataset_version': dataset['dataset_version'], 'dataset_sha256': dataset_hash,
            'request_sha256': hashlib.sha256(canonical).hexdigest(), 'verified_on': dataset['verified_on'], 'source_url': dataset['source_url'],
            'request': request, 'table_number': t['number'], 'table_label': t['label'], 'band_upper': band, 'lines': lines, 'totals': totals,
            'rates': {f: dataset[f] for f in ['general_expenses_rate', 'cpa_rate', 'vat_rate', 'withholding_rate']},
            'notes': ['Minimo e massimo indicano gli estremi della variazione ordinaria del 50%, con le sole regole selezionate: non una liquidazione automatica del giudice.',
                      'Spese generali sul compenso; CPA su compenso più spese generali; IVA sulla stessa base più CPA; base ritenuta senza CPA e IVA. Al soccombente, IVA solo se dichiarata recuperabile.',
                      'Anticipazioni art. 15 escluse dagli imponibili solo su conferma dell’avvocato. Altri rimborsi, bollo e acconti non inclusi.',
                      'Il calcolo è locale; la conversazione con l’agente segue il trattamento dati del fornitore utilizzato.',
                      'Preventivo delle attività indicate, da aggiornare se cambiano attività o normativa.' if purpose == 'preventivo' else 'Conteggiate esclusivamente le fasi dichiarate svolte.']}


def render_html(result):
    e = lambda x: html.escape(str(x), quote=True)
    levels = ['minimo', 'medio', 'massimo']
    def eur(x):
        return format(Decimal(x), ',.2f').replace(',', 'X').replace('.', ',').replace('X', '.') + ' €'
    rows = ''.join('<tr><td>' + e(row['label']) + '</td><td>' + eur(row['table_medium']) + '</td>' + ''.join('<td>' + eur(row[l]) + '</td>' for l in levels) + '</tr>' for row in result['lines'])
    summary = ''.join('<tr><th>' + e(field.replace('_', ' ')) + '</th>' + ''.join('<td>' + eur(result['totals'][l][field]) + '</td>' for l in levels) + '</tr>' for field in result['totals']['medio'])
    request = ''.join('<tr><th>' + e(k) + '</th><td>' + e(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) + '</td></tr>' for k, v in result['request'].items())
    notes = ''.join('<li>' + e(n) + '</li>' for n in result['notes'])
    audit = ''.join('<p><b>' + e(k) + ':</b> ' + e(result[k]) + '</p>' for k in ['engine_version', 'dataset_version', 'verified_on', 'dataset_sha256', 'request_sha256'])
    return f'''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Prospetto compensi</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;color:#17283b;max-width:1000px;margin:45px auto;padding:0 24px}}h1{{font-size:32px}}h2{{margin-top:32px;font-size:20px}}header{{border-bottom:3px solid #a78040;padding-bottom:20px}}small{{color:#576779}}table{{width:100%;border-collapse:collapse;margin:20px 0}}td,th{{padding:10px;border-bottom:1px solid #dbe1e7;text-align:right}}td:first-child,th:first-child{{text-align:left}}thead{{background:#17283b;color:white}}.audit{{font-size:11px;overflow-wrap:anywhere}}@page{{size:A4;margin:17mm}}@media print{{body{{margin:0;padding:0;font-size:10pt}}thead{{display:table-header-group}}tr{{break-inside:avoid}}h2{{break-after:avoid}}.audit{{font-size:8pt}}}}</style>
<header><small>PARAMETRI FORENSI ITALIANI · PROSPETTO DI CALCOLO</small><h1>{e(result['request'].get('title', 'Compenso professionale'))}</h1><p>Tabella {e(result['table_number'])} · {e(result['table_label'])}<br>Scaglione fino a {e(result['band_upper'] or 'non applicabile')} · Riferimento normativo {e(result['request']['normative_date'])}</p></header>
<h2>Compensi per fase</h2><table><thead><tr><th>Fase</th><th>Medio tabellare</th><th>Minimo</th><th>Medio</th><th>Massimo</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Accessori e importi finali</h2><p>Spese generali {e(result['rates']['general_expenses_rate'])}%; CPA {e(result['rates']['cpa_rate'])}% se selezionata; IVA {e(result['rates']['vat_rate'])}% in ordinario; ritenuta {e(result['rates']['withholding_rate'])}% se selezionata.</p><table><thead><tr><th>Voce</th><th>Minimo</th><th>Medio</th><th>Massimo</th></tr></thead><tbody>{summary}</tbody></table>
<h2>Dati e scelte dell’avvocato</h2><table>{request}</table><h2>Criteri e limiti</h2><ul>{notes}</ul><h2>Verificabilità</h2><p><a href="{e(result['source_url'])}">Gazzetta Ufficiale: D.M. 147/2022 e tabelle</a> · D.M. 55/2014 artt. 2, 4, 5, 12.</p><div class="audit">{audit}</div></html>'''


def render_csv(result):
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Voce', 'Minimo EUR', 'Medio EUR', 'Massimo EUR'])
    for row in result['lines']:
        writer.writerow([row['label']] + [row[l].replace('.', ',') for l in ['minimo', 'medio', 'massimo']])
    for field in result['totals']['medio']:
        writer.writerow([field] + [result['totals'][l][field].replace('.', ',') for l in ['minimo', 'medio', 'massimo']])
    writer.writerow(['dataset', result['dataset_version']])
    writer.writerow(['dataset_sha256', result['dataset_sha256']])
    writer.writerow(['request_sha256', result['request_sha256']])
    return output.getvalue()


def unique_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise InputError('Chiave JSON duplicata: ' + k)
        obj[k] = v
    return obj


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, help='Dataset versionato alternativo, revisionato')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('catalog', help='Elenco tabelle e fasi supportate')
    sub.add_parser('verify-data', help='Verifica struttura e impronta del dataset')
    calc = sub.add_parser('calculate')
    calc.add_argument('input', help='File JSON UTF-8; - per stdin')
    calc.add_argument('--output', type=Path, help='Prefisso file .json, .html e .csv; directory già esistente')
    args = parser.parse_args(argv)
    try:
        data, digest = load_dataset(args.dataset)
        if args.command == 'catalog':
            result = {'status': 'ok', 'tables': data['tables']}
        elif args.command == 'verify-data':
            result = {'status': 'ok', 'dataset_version': data['dataset_version'], 'sha256': digest, 'tables': len(data['tables'])}
        else:
            source = sys.stdin.buffer.read().decode('utf-8-sig') if args.input == '-' else Path(args.input).read_text(encoding='utf-8-sig')
            request = json.loads(source, object_pairs_hook=unique_object)
            result = calculate(request, data, digest)
            if args.output and result['status'] == 'ok':
                outputs = {'.json': json.dumps(result, ensure_ascii=False, indent=2) + '\n', '.html': render_html(result), '.csv': render_csv(result)}
                paths = [Path(str(args.output) + ext) for ext in outputs]
                if any(p.exists() for p in paths):
                    raise InputError('Output già esistente: scegliere un nuovo prefisso per preservare il prospetto')
                for ext, content in outputs.items():
                    Path(str(args.output) + ext).write_text(content, encoding='utf-8-sig' if ext == '.csv' else 'utf-8', newline='')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result['status'] == 'needs_input' else 0
    except (InputError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
