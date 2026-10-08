# Manuale per avvocati e manutentori

## Indice

1. Installazione macOS e Windows
2. Uso con Codex e Claude Code
3. Richiesta e comandi
4. Esportazione
5. Test e aggiornamento
6. Uso durante il Master

## 1. Installazione

Occorre Python 3.10 o successivo, disponibile da [python.org](https://www.python.org/downloads/). Il pacchetto non richiede abbonamenti propri, API key, pip o collegamento Internet per i calcoli. Codex e Claude hanno requisiti e costi propri.

Estrarre il pacchetto in una cartella e aprire un terminale in quella cartella. Non occorre cambiare alcun file Rust o compilare Codex.

macOS:

```sh
python3 --version
python3 calcola-parametri-forensi/scripts/install.py --agent both
```

Windows PowerShell:

```powershell
py -3 --version
py -3 .\calcola-parametri-forensi\scripts\install.py --agent both
```

Il comando copia la skill in `~/.agents/skills/calcola-parametri-forensi` per Codex attuale e `~/.claude/skills/calcola-parametri-forensi` per Claude Code. `~` indica la cartella personale dell’utente, anche su Windows. In alternativa scegliere `--agent codex` o `--agent claude`.

Per il fork codex_chatleg o versioni storiche compatibili con il suo loader:

```sh
python3 calcola-parametri-forensi/scripts/install.py --agent codex-legacy
```

Su Windows sostituire `python3` con `py -3`. Questo usa `$CODEX_HOME/skills` se la variabile è definita, altrimenti `~/.codex/skills`. Non installare entrambe le varianti Codex senza necessità: alcune versioni potrebbero mostrare doppioni.

L’installatore rifiuta di sovrascrivere una copia già presente. Per aggiornare: salvare una copia della vecchia cartella, rimuovere solo la vecchia skill verificata e installare la nuova. Per disinstallare rimuovere solo `calcola-parametri-forensi` dalla destinazione scelta. Non modificare configurazioni o credenziali dell’agente.

Si può chiedere al proprio agente di eseguire questi comandi dal pacchetto estratto. L’app deve avere accesso alla cartella e alla shell locale. Se la skill non compare, controllare il percorso rispetto alla versione installata e riaprire/aggiornare l’elenco delle skill.

## 2. Uso naturale

Codex: «Usa $calcola-parametri-forensi per un preventivo civile davanti al Tribunale da 20.000 euro. Chiedimi cosa manca.»

Claude Code: «/calcola-parametri-forensi Prepariamo una nota spese penale per il Tribunale monocratico.»

L’agente sceglie la tabella, raccoglie dati, esegue Python e consegna i file. Non è un’interfaccia grafica autonoma e non è un MCP. Per usare la copia direttamente senza rilevamento automatico, indicare all’agente il percorso del suo `SKILL.md`.

La compatibilità desktop non è certificata: vedere [compatibilita.md](compatibilita.md).

## 3. Richiesta e comandi

I comandi vanno eseguiti con percorsi assoluti o dalla cartella skill. Tutti gli importi JSON devono essere stringhe con punto decimale: `"20000.00"`, non `"20.000,00"` né numeri floating point.

```sh
python3 scripts/compensi.py catalog
python3 scripts/compensi.py verify-data
python3 scripts/compensi.py calculate examples/input-civile.json --output /percorso/esistente/prospetto-civile
python3 scripts/compensi.py calculate examples/input-penale.json --output /percorso/esistente/prospetto-penale
python3 -m unittest discover -s tests -v
```

Su Windows usare `py -3`, ad esempio `--output "C:\Utenti\Nome\Documenti\prospetto"`. La directory deve già esistere; il prefisso non deve avere estensione. Il comando crea `.json`, `.html`, `.csv`, senza sovrascrivere output esistenti.

| Campo | Obbligo e valori |
|---|---|
| `purpose` | `preventivo`, `cliente`, `soccombente` |
| `table` | Identificatore restituito da `catalog`; penale con prefisso `penale-` |
| `phases` | Elenco non vuoto e senza doppioni, tra le fasi della tabella |
| `value`, `value_basis` | Solo civile: importo positivo o `indeterminabile` e criterio art. 5 motivato |
| `band`, `band_reason` | Solo indeterminabile: `52000`, `260000`, `520000` e motivazione |
| `completed_on` | ISO `YYYY-MM-DD`, richiesta per liquidazioni cliente/soccombente |
| `normative_date` | Data ISO; non dopo la verifica dataset |
| `tax_regime` | `ordinario` oppure `forfettario` |
| `cpa`, `withholding` | Booleani `true`/`false`, scelte da confermare |
| `vat_recoverable` | Obbligatorio per soccombente in ordinario: IVA non detraibile recuperabile? |
| `expenses_art15` | Importo delle anticipazioni art. 15; `"0.00"` se assenti |
| `expenses_art15_confirmed` | `true` obbligatorio se importo art. 15 positivo |
| `special_cases` | `[]` solo in assenza di casi fuori copertura; altrimenti elenco che ferma il calcolo |
| `non_contentious` | `true` richiesto per tabella volontaria |
| `title` | Facoltativo, testo generico di massimo 300 caratteri |
| `adjustments` | Facoltativo, tre modifiche qui sotto con `reason` obbligatoria |

Esempi di modifiche consentite:

```json
{"settlement": true, "reason": "Controversia definita con transazione"}
```

Sostituisce la fase decisionale civile scelta con compenso maggiorato del 25%. Non va aggiunta una seconda fase decisionale.

```json
{"complex_investigations": true, "reason": "Indagini difensive particolarmente urgenti"}
```

Solo per `penale-indagini-difensive`: +20%.

```json
{"subjects": 2, "plurality_percent": "30", "plurality_confirmed": true, "reason": "Stessa posizione processuale, questioni specifiche distinte; aumento richiesto"}
```

Il tetto è verificato, ma l’applicabilità e la misura rimangono scelte motivate dell’avvocato. Non usare per due coniugi, questioni identiche o più difensori: sono regole diverse, fuori copertura.

Codici uscita: `0` calcolo riuscito, `2` mancano dati (domande JSON in stdout), `1` errore o caso non supportato (diagnostica JSON in stderr). Nessun file esportato con dati mancanti.

## 4. Esportazione

- HTML autonomo, senza risorse remote, pronto per stampa A4: aprire nel browser e Stampa > Salva come PDF.
- JSON: richiesta completa, righe, basi di calcolo, aliquote, versioni e impronte SHA-256 per audit.
- CSV UTF-8 con BOM, separatore `;` e virgola decimale, apribile nei fogli di calcolo italiani.

Il motore non produce direttamente un PDF o DOCX. Il PDF dipende dalle impostazioni del browser. Il prospetto non è una fattura e non include bollo o acconti.

Esempio civile incluso: compenso medio €5.077,00; spese generali €761,55; CPA €233,54; IVA €1.335,86; totale €7.407,95. Esempio penale incluso, forfettario: compenso medio €3.592,00; spese €538,80; CPA €165,23; totale €4.296,03, IVA zero.

## 5. Test e aggiornamento

`data/tables.json` è separato dall’agente e dal motore. Non aggiornarlo con numeri ricordati dal modello. `references/sources.json` registra fonti e impronte dei testi ufficiali conservati.

Procedura di rilascio:

1. Verificare Normattiva, Gazzetta Ufficiale, Cassa Forense e fonti fiscali aggiornate.
2. Conservare la fonte ufficiale esatta e la sua impronta; documentare articoli applicabili, decorrenza e regime transitorio.
3. Aggiornare matrici e aliquote nel JSON; incrementare `dataset_version`. Non cambiare solo `verified_on`.
4. Se cambiano le regole, aggiornare il codice separatamente con nuove fixture normative e test.
5. Confrontare tutte le celle con l’originale e ricalcolare gli esempi indipendentemente; eseguire i test.
6. Aggiornare manuale e compatibilità; distribuire una versione nuova senza alterare vecchi prospetti.

Un dataset alternativo si carica con `python3 scripts/compensi.py --dataset /percorso/tables.json calculate richiesta.json`. La verifica strutturale non certifica la correttezza normativa dei dati: occorre revisione professionale. SHA-256 permette di identificare la versione usata, non è una firma digitale di autenticità.

## 6. Master

Distribuire una copia identica del pacchetto a ogni partecipante. Fare eseguire prima `verify-data`, poi l’esempio civile. Chiedere poi «calcolami una parcella penale» per mostrare la raccolta dei dati mancanti. Mostrare anche un caso di patrocinio Stato: il comportamento corretto nella v1 è fermarsi.

I calcoli funzionano offline. Le richieste in linguaggio naturale possono essere inviate al fornitore dell’agente: usare casi sintetici e titoli generici durante la formazione. Non occorre inviare fascicoli giudiziari per calcolare un compenso.
