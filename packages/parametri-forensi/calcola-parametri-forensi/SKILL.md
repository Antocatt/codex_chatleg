---
name: calcola-parametri-forensi
description: Calcolare compensi e parametri forensi italiani civili e penali, preventivi e note spese con minimi, medi, massimi, spese generali, CPA e IVA. Usare quando un avvocato chiede una parcella, un calcolo D.M. 55/2014 o D.M. 147/2022, anche in linguaggio naturale. Eseguire il motore locale e chiedere i dati mancanti; non inventare importi tabellari.
---

# Calcolare i parametri forensi

Usare esclusivamente `scripts/compensi.py` per importi, scaglioni, accessori e arrotondamenti. Risolvere i percorsi rispetto alla directory di questo SKILL.md, senza presumere la directory di lavoro. Utilizzare Python 3.10 o successivo, senza dipendenze esterne. Su macOS/Linux usare `python3`; su Windows `py -3`. Non modificare tabelle o codice per ottenere il risultato desiderato.

## Raccogliere i dati

Usare normalmente il percorso rapido. Chiedere soltanto:

1. autorità giudiziaria o tipo di procedimento;
2. valore della controversia, soltanto nel civile;
3. fasi da conteggiare;
4. inclusione di IVA e CPA;
5. eventuale aumento per complessità e numero di clienti, parti o imputazioni.

Le spese generali del 15% sono automatiche. Chiedere l’importo delle anticipazioni documentate ex art. 15 solo se l’avvocato segnala ulteriori spese. Non chiedere finalità, data, ritenuta, regime fiscale o un elenco di casi speciali quando l’utente vuole semplicemente il prospetto minimo/medio/massimo.

Eseguire `python3 "<skill>/scripts/compensi.py" catalog` per ricavare la chiave corretta dell’autorità e le fasi disponibili. Nel penale non chiedere il valore della causa. Nel civile chiedere sempre il valore o lo scaglione indeterminabile.

Per la complessità chiedere una percentuale da 0% a 50% e una breve motivazione. Il motore la applica al valore medio e produce una colonna `applicato`: non sommarla al massimo, che rappresenta già il limite del +50% dell’art. 4 o 12 comma 1.

Per più soggetti chiedere il numero e se applicare il massimo normativo o una percentuale inferiore. Prima di applicarlo confermare i presupposti dell’art. 4 o 12 comma 2. Il motore calcola il massimo con `plurality_percent: "max"`; non calcolarlo mentalmente.

## Calcolare e verificare

Preparare una richiesta JSON essenziale con stringhe decimali, punto decimale e nessun separatore di migliaia. Usare [input-rapido-penale.json](examples/input-rapido-penale.json) come schema. Non inserire nomi o dati giudiziari se non necessari; preferire un titolo generico.

Eseguire:

```sh
python3 "<skill>/scripts/compensi.py" quick "<richiesta.json>" --output "<cartella-output>/prospetto"
```

- Con `needs_input` (exit 2), porre le domande restituite e completare la richiesta, senza mostrare un totale definitivo.
- Con `error` (exit 1), correggere soltanto errori di input confermati; per un limite di copertura, spiegare il limite e non aggirarlo.
- Con `ok` (exit 0), riportare le fasi, minimo, medio e massimo, l’eventuale colonna applicata, compenso, spese generali, CPA, IVA, anticipazioni e totale. Verificare che le scelte corrispondano ai dati confermati dall’avvocato.
- Distinguere estremi della variazione ordinaria da minimi inderogabili, equo compenso, importi pattuiti e liquidazione effettiva. Il massimo riportato non include regole speciali non selezionate.
- Consegnare JSON di audit, CSV e HTML professionale. Per il PDF invitare ad aprire l’HTML e usare Stampa > Salva come PDF. Non dichiarare una generazione PDF diretta o un’esportazione Word.
- Riportare versione dataset, data verifica e collegamento alla Gazzetta Ufficiale. Se la data normativa supera la verifica, aggiornare le fonti con il manutentore: non cambiare solo la data di verifica.

Usare il comando `calculate` e il relativo schema completo soltanto quando l’avvocato chiede espressamente una liquidazione avanzata con date, ritenuta, rapporto cliente/soccombente o regole ulteriori. Il motore non usa rete. Non presentare come locale il trattamento della conversazione da parte di Codex/Claude. Non emettere né inviare fatture e non trasmettere prospetti a terzi senza richiesta.

Per installazione, test e aggiornamenti leggere [manuale.md](references/manuale.md). Per compatibilità verificata e limiti leggere [compatibilita.md](references/compatibilita.md).
