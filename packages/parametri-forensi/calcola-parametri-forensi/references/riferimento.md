# Disciplina e copertura v1

Verifica delle fonti: 8 ottobre 2026. La versione consolidata del D.M. 55/2014 consultata su Normattiva riporta ultimo aggiornamento pubblicato l’8 ottobre 2022. La ricerca di aggiornamenti non ha individuato un successivo decreto sostitutivo delle tabelle. Non equivale a un monitoraggio automatico: ogni rilascio richiede una nuova verifica.

## Fonti ufficiali

- [D.M. 55/2014, testo vigente e multivigenza](https://www.normattiva.it/eli/id/2014/04/02/14G00067/CONSOLIDATED).
- [D.M. 147/2022, Gazzetta Ufficiale](https://www.gazzettaufficiale.it/eli/id/2022/10/08/22G00157/sg), entrata in vigore 23 ottobre 2022.
- [G.U. 236/2022 PDF ufficiale](https://www.gazzettaufficiale.it/eli/gu/2022/10/08/236/sg/pdf): testo, allegati e note con articoli consolidati. I valori civili sono stati estratti dal PDF; le 20 matrici sono confrontate nei test con la versione HTML ufficiale, estratta separatamente. La tabella penale ha due blocchi: il secondo è grafico nell’HTML e viene verificato sul PDF.
- [Allegato tabelle, versione HTML ufficiale](https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=22G00157&art.dataPubblicazioneGazzetta=2022-10-08&art.flagTipoArticolo=1&art.idArticolo=1&art.idGruppo=0&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=0&art.versione=1).
- [Cassa Forense, contributi in autoliquidazione](https://www.cassaforense.it/contributi-in-autoliquidazione), contributo integrativo 4%; [Regolamento unico](https://www.cassaforense.it/regolamento-unico-previdenza-forense). Non si calcolano qui contributo soggettivo o minimi annuali.
- [D.P.R. 633/1972 art. 16, MEF](https://def.finanze.it/DocTribFrontend/getAttoNormativoDetail.do?ACTION=getArticolo&codiceOrdinamento=0000000000000160000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000&id=%7B75A4827C-3766-4ECC-9C45-00C8D6CDC552%7D): IVA ordinaria 22%.
- [Agenzia Entrate, prassi sulle anticipazioni ex art. 15 n. 3 D.P.R. 633/1972, MEF](https://def.finanze.it/DocTribFrontend/getPrassiDetail.do?id=%7B5A3B645A-8D64-4817-9061-EB9AAD5FE9E1%7D): escluse se anticipate in nome e per conto, regolarmente documentate.
- [D.P.R. 600/1973 art. 25, testo vigente dal 1 gennaio 2026, MEF](https://def.finanze.it/DocTribFrontend/executePrintArticolo.do?articolo=Articolo+25&codiceOrdinamento=0000000000000250000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000&id=%7B178F0CBC-1969-49F3-974E-7C0E87B9A568%7D): ritenuta 20% sui compensi del professionista residente; esclusi dal pacchetto i regimi esteri e altri regimi speciali.
- [L. 190/2014 art. 1 comma 67, MEF](https://def.giustiziatributaria.gov.it/DocTribFrontend/executePrintArticolo.do?articolo=Articolo+1+com+67&codiceOrdinamento=0000000000000010000000000000000000000000000670000000000000000000000000000000000000000000000000000000000000000000000000000000000000&id=%7BA27C4916-5385-4241-8111-253A9BC8C965%7D), esclusione ritenuta; comma 58 per franchigia IVA. [Circolare Agenzia Entrate 9/E del 10 aprile 2019](https://def.finanze.it/DocTribFrontend/getPrassiDetail.do?id=%7BD4140375-DB3C-41E3-8FED-87B81B871C3D%7D).

## Regole implementate

| Regola | Fonte | Comportamento |
|---|---|---|
| Ambito parametri, distinzione dall’accordo sul compenso | D.M. 55 art. 1; L. 247/2012 art. 13 | Parametri indicativi nel preventivo; non sostituiscono un patto |
| Spese generali | D.M. 55 art. 2 comma 2 | 15% del compenso calcolato |
| Variazione ordinaria civile/penale | D.M. 55 artt. 4 comma 1, 12 comma 1 aggiornati | 50%, 100%, 150% del medio; arrotondamento per fase ai centesimi HALF_UP |
| Aumento per complessità | D.M. 55 artt. 4 comma 1, 12 comma 1 | Percentuale scelta e motivata da 0% a 50% sul medio; esposta come scenario applicato, senza sommarla al massimo |
| Fasi svolte | D.M. 55 artt. 4 comma 5, 12 comma 3 | Solo fasi scelte; celle penali vuote escluse, non trattate come compensi zero |
| Valore civile | D.M. 55 art. 5 | Valore determinato dall’avvocato secondo finalità: domanda/attribuito/interesse effettivo; non dal motore |
| Indeterminabile | Art. 5 comma 6 | Scaglione esplicito e motivato: fino a 52.000 o 260.000; 520.000 per particolare importanza |
| Volontaria giurisdizione | Art. 4 comma 4-bis | Richiede conferma non contenziosa |
| Conciliazione/transazione | Art. 4 comma 6 | Fase decisionale sostituita dal valore equivalente aumentato di 1/4; nessun doppio conteggio |
| Indagini difensive complesse/urgenti | Art. 12 comma 3-bis | +20% dei compensi delle indagini difensive confermate |
| Pluralità | Artt. 4 comma 2 / 12 comma 2 | Percentuale scelta e motivata, entro 30% per soggetto dal 2° al 10°, 10% dall’11° al 30°; richiede conferma dei presupposti |
| Minorenni penale | Art. 12 comma 3-ter | Selezione da parte dell’avvocato dell’autorità competente per adulto |
| CPA/IVA/ritenuta | Fonti previdenziali/fiscali sopra | CPA 4% su compenso + spese generali; IVA 22% sulla stessa base + CPA; ritenuta 20% sulla base senza CPA/IVA/art.15 |

Sequenza riproducibile: medio tabellare × variazione ordinaria, oppure medio × (1 + percentuale complessità) per lo scenario applicato; poi eventuale regola di fase × (1 + percentuale pluralità), arrotondamento singola fase; somma fasi; spese generali; CPA; IVA; anticipazioni; sottrazione ritenuta. Ogni voce è arrotondata a due decimali. Gli estremi restano quelli della variazione ordinaria con le sole modifiche confermate.

Il prospetto al soccombente richiede conferma sulla recuperabilità IVA: se detraibile per il cliente non viene aggiunta al rimborso. La ritenuta, legata al pagamento, è esclusa dal prospetto di liquidazione al soccombente; eventuale distrazione richiede valutazione separata.

## Copertura

Civile: tabelle 1–14 e 16–20, più 20-bis; giudice di pace, cognizione ordinaria/sommaria in Tribunale, lavoro, previdenza, convalida, precetto, volontaria, monitorio, istruzione preventiva, cautelare, Corte dei conti, appello, Cassazione, corti superiori, esecuzioni, tavolare, fallimento, passivo. Le denominazioni normative originali sono conservate: non significa che il vecchio rito sia ancora vigente.

Penale: tutte le 15 colonne della tabella 15, incluse preliminari, indagini difensive, GIP/GUP, convalida, cautelari, tribunali, assise, sorveglianza, appello e Cassazione. Non scegliere fasi solo perché esistono nella tabella: deve esserci attività relativa.

## Fuori copertura: fermare il calcolo

- Prestazioni esaurite prima del 23 ottobre 2022; date normative dopo l’ultima verifica.
- Civile oltre €520.000 e giudice di pace oltre la sua tabella (€26.000): gli incrementi discrezionali dell’art. 6 non sono automatizzati.
- Tabelle amministrative 21/22, tributarie 23/24, stragiudiziale 25, mediazione/negoziazione 25-bis e altre attività non comprese.
- Patrocinio Stato: artt. 82, 130, 106-bis D.P.R. 115/2002 da gestire con regole specifiche; non applicare una riduzione generica.
- Equo compenso L. 49/2023: non valutare validità dei patti o minimi inderogabili attraverso il solo prospetto ordinario.
- Patti già determinati, praticanti, art. 96 c.p.c., riduzioni per questioni identiche, due coniugi, ulteriori aumenti telematici, memorie in Cassazione, plurimi difensori da liquidare, class action, trasferta e altre maggiorazioni.
- Bollo, acconti, rimborso spese diverso dalle anticipazioni art.15, disciplina dei rimborsi analitici modificata dal D.Lgs. 192/2024, regimi IVA speciali, prestazioni estere.

Indicare il caso in `special_cases`; il motore rifiuta di produrre un importo apparentemente definitivo. Il pacchetto è una prima versione professionale circoscritta, non un calcolatore universale.
