---
name: calcola-parametri-forensi
description: Calcolare compensi e parametri forensi italiani civili e penali, preventivi e note spese con minimi, medi, massimi, spese generali, CPA e IVA. Usare quando un avvocato chiede una parcella, un calcolo D.M. 55/2014 o D.M. 147/2022, anche in linguaggio naturale. Eseguire il motore locale e chiedere i dati mancanti; non inventare importi tabellari.
---

# Calcolare i parametri forensi

Usare esclusivamente `scripts/compensi.py` per importi, scaglioni, accessori e arrotondamenti. Risolvere i percorsi rispetto alla directory di questo SKILL.md, senza presumere la directory di lavoro. Utilizzare Python 3.10 o successivo, senza dipendenze esterne. Su macOS/Linux usare `python3`; su Windows `py -3`. Non modificare tabelle o codice per ottenere il risultato desiderato.

## Raccogliere i dati

1. Leggere [riferimento.md](references/riferimento.md) per ambito, regole e limiti. Eseguire `python3 "<skill>/scripts/compensi.py" catalog` per scegliere il procedimento e le fasi reali. Distinguere penale e civile: non usare il valore della causa nel penale; non applicare le tabelle civili alla parte civile senza valutare le attività effettive e la disciplina pertinente.
2. Chiedere in piccoli gruppi soltanto i dati mancanti: finalità (preventivo/cliente/soccombente), procedimento/autorità/grado, fasi, criterio e valore civile, data di esaurimento se liquidazione, data normativa, regime fiscale, applicazione CPA, ritenuta, anticipazioni ex art. 15 e casi speciali. Non presumere il regime personale dell’utente per altri avvocati.
3. Per valore indeterminabile chiedere scaglione e motivazione ex art. 5 comma 6; per minori in penale chiedere quale autorità sarebbe competente se maggiorenni. Non confondere fasi tabellate e fasi effettivamente svolte. Nei preventivi indicare le attività previste.
4. Accertare casi speciali: patrocinio Stato, patti, equo compenso, più soggetti, questioni identiche, atti telematici agevolmente consultabili, trasferta, rimborsi non art. 15, art. 96 c.p.c., Cassazione con memoria, controversie oltre tabella. Consultare i limiti del manuale; se non coperti, fermarsi e spiegare il dato/regola ancora da gestire. Non ricondurli artificiosamente al caso ordinario. Usare `special_cases: []` solo dopo aver accertato che non ci sono regole non implementate.
5. Applicare le tre regole opzionali documentate (`adjustments`) soltanto su istruzioni dell’avvocato e con motivazione. Non selezionare automaticamente la maggiorazione massima per pluralità. Per due coniugi e questioni identiche, fermarsi: la v1 non implementa i regimi specifici.

## Calcolare e verificare

Preparare una richiesta JSON con stringhe decimali, punto decimale e nessun separatore di migliaia. Usare [input-civile.json](examples/input-civile.json), [input-penale.json](examples/input-penale.json) e [manuale.md](references/manuale.md) come esempi/schema. Non inserire nomi o dati giudiziari se non necessari; preferire un titolo generico.

Eseguire:

```sh
python3 "<skill>/scripts/compensi.py" calculate "<richiesta.json>" --output "<cartella-output>/prospetto"
```

- Con `needs_input` (exit 2), porre le domande restituite e completare la richiesta, senza mostrare un totale definitivo.
- Con `error` (exit 1), correggere soltanto errori di input confermati; per un limite di copertura, spiegare il limite e non aggirarlo.
- Con `ok` (exit 0), riportare le fasi, i tre livelli, compenso, spese generali, basi imponibili, CPA, IVA, anticipazioni, totale lordo, eventuale ritenuta e netto. Verificare che le scelte corrispondano ai dati confermati dall’avvocato.
- Distinguere estremi della variazione ordinaria da minimi inderogabili, equo compenso, importi pattuiti e liquidazione effettiva. Il massimo riportato non include regole speciali non selezionate.
- Consegnare JSON di audit, CSV e HTML professionale. Per il PDF invitare ad aprire l’HTML e usare Stampa > Salva come PDF. Non dichiarare una generazione PDF diretta o un’esportazione Word.
- Riportare versione dataset, data verifica e collegamento alla Gazzetta Ufficiale. Se la data normativa supera la verifica, aggiornare le fonti con il manutentore: non cambiare solo la data di verifica.

Il motore non usa rete. Non presentare come locale il trattamento della conversazione da parte di Codex/Claude. Non emettere né inviare fatture e non trasmettere prospetti a terzi senza richiesta.

Per installazione, test e aggiornamenti leggere [manuale.md](references/manuale.md). Per compatibilità verificata e limiti leggere [compatibilita.md](references/compatibilita.md).
