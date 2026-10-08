# Parametri forensi italiani per agenti locali

Prima skill autonoma per avvocati: istruzioni linguistiche in `SKILL.md`, motore Python deterministico offline e tabelle verificabili del D.M. 147/2022. Non modifica il motore Rust di Codex.

**Copertura v1:** 20 tabelle civili (1–14, 16–20 e 20-bis) e 15 autorità/attività della tabella penale 15. Compensi minimi/medi/massimi della variazione ordinaria, spese generali 15%, CPA 4%, IVA 22% quando applicabile, anticipazioni art.15 e ritenuta opzionale. CSV, JSON di audit e HTML professionale stampabile in PDF. Richieste incomplete producono domande strutturate, senza totale definitivo.

**Limiti:** patrocinio Stato, regimi storici, valori oltre tabella, tabelle amministrative/tributarie/stragiudiziali, equo compenso e altre regole speciali non implementate fermano il calcolo. Non è una fattura. La verifica delle fonti è datata 8 ottobre 2026; la v1 blocca date normative successive finché non si revisiona il dataset.

## Installazione rapida

Python 3.10+; nessuna dipendenza pip, chiave API o servizio esterno per il motore.

Da questa cartella, macOS:

```sh
python3 calcola-parametri-forensi/scripts/install.py --agent both
```

Windows PowerShell:

```powershell
py -3 .\calcola-parametri-forensi\scripts\install.py --agent both
```

Scegliere `codex` per Codex attuale (`~/.agents/skills`), `claude` per Claude Code (`~/.claude/skills`), oppure `codex-legacy` per il fork codex_chatleg (`$CODEX_HOME/skills` / `~/.codex/skills`). `both` installa Codex attuale e Claude. Non sovrascrive skill esistenti.

- [Manuale completo](calcola-parametri-forensi/references/manuale.md)
- [Fonti, regole e limiti](calcola-parametri-forensi/references/riferimento.md)
- [Compatibilità e verifiche ancora da eseguire](calcola-parametri-forensi/references/compatibilita.md)
- [Esempio civile](calcola-parametri-forensi/examples/input-civile.json)
- [Esempio penale](calcola-parametri-forensi/examples/input-penale.json)

Codex: «Usa $calcola-parametri-forensi per un preventivo civile da 20.000 euro davanti al Tribunale; chiedimi i dati mancanti».

Claude Code: «/calcola-parametri-forensi Calcoliamo una nota compensi penale».

## Verifica e sviluppo

```sh
python3 -m unittest discover -s calcola-parametri-forensi/tests -v
python3 calcola-parametri-forensi/scripts/compensi.py verify-data
python3 calcola-parametri-forensi/scripts/compensi.py calculate calcola-parametri-forensi/examples/input-civile.json
```

Test locali su Linux/Python 3.12 e prova con un agente tramite percorso esplicito. Compatibilità strutturale con il loader del fork verificata sul suo codice. Test automatici eseguiti anche nei runner macOS e Windows; vedere compatibilita.md per matrice e stato. App desktop, scoperta automatica ed esecuzione Claude Code non sono ancora testate. I controlli generali del fork presentano errori di release/dipendenze fuori dallo scopo del pacchetto.

Il motore usa solo libreria standard. Tutte le 324 celle civili sono confrontate con un’estrazione indipendente dell’HTML ufficiale; 53 celle penali presenti (e celle vuote) sono verificate rispetto al PDF ufficiale, con controllo automatizzato delle prime sette colonne nell’HTML.

Versione motore `1.0.0`; dataset `dm147-2022-v1.0.0`. Prima di distribuire una versione aggiornata ai partecipanti, revisionare fonti, tabelle, decorrenze, esempi e test come indicato nel manuale. Il pacchetto non effettua aggiornamenti automatici.
