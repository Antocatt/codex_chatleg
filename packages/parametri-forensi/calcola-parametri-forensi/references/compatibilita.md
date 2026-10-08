# Compatibilità e stato delle verifiche

Data: 8 ottobre 2026. Motore 1.1.0; Python 3.10+ standard library. Verifica locale effettuata su Linux, Python 3.12.14.

| Ambiente | Evidenza | Stato |
|---|---|---|
| Motore Python locale | Suite unittest, esempi civile e penale, esportazione JSON/CSV/HTML | Testato |
| Codex nel presente ambiente agente | Prova di uso con richiesta civile ed esecuzione dello script; richiesta penale incompleta restituisce domande | Testato mediante caricamento esplicito del percorso della skill |
| Loader del fork Antocatt/codex_chatleg | Lettura `codex-rs/core/src/skills/loader.rs` al commit `6a57d7980bca3121ca6d0e9b795304ec2d294208`; contratto YAML, nome ≤64 e descrizione ≤1024; percorso `$CODEX_HOME/skills` | Compatibilità strutturale verificata; loader Rust non compilato né eseguito |
| Codex attuale, scoperta locale | Documentazione ufficiale: `.agents/skills` e `~/.agents/skills`; installazione isolata testata | Scoperta automatica, CLI e app desktop non testate: eseguibili non disponibili |
| Claude Code | Documentazione ufficiale: `~/.claude/skills/<nome>/SKILL.md`, invocazione `/nome`; installazione isolata testata | Esecuzione CLI/app non testata: Claude Code non disponibile |
| macOS | Codice portabile e istruzioni `python3`; nessuna dipendenza nativa | Suite eseguita su runner macOS con Python 3.10/3.13; applicazioni desktop non testate |
| Windows | Codice portabile e istruzioni `py -3`; percorsi gestiti con pathlib; prova in home con spazi su Linux | Suite eseguita su runner Windows con Python 3.10/3.13; applicazioni desktop non testate |

Fonti di compatibilità:

- [Codex, skill](https://developers.openai.com/codex/skills/), documentazione consultata il giorno della verifica.
- [Claude Code, skill](https://code.claude.com/docs/en/skills).
- [Loader del fork](https://github.com/Antocatt/codex_chatleg/blob/6a57d7980bca3121ca6d0e9b795304ec2d294208/codex-rs/core/src/skills/loader.rs).

Nessun motore Rust modificato. La prova di un agente con percorso esplicito dimostra il workflow istruzioni → richiesta JSON → motore → prospetto; non dimostra la scoperta automatica di una versione desktop.

## Verifica pratica da eseguire sulle app

1. Installare la variante corretta e aprire un progetto locale a cui l’app ha accesso.
2. Verificare che la skill compaia nell’elenco; invocare il suo nome.
3. Chiedere il preventivo civile dell’esempio: il totale medio deve essere €7.407,95.
4. Chiedere «compenso penale in Cassazione» senza altri dati: devono essere chiesti finalità, fasi, date, regime, CPA, ritenuta, anticipazioni e casi speciali. Nessun totale definitivo.
5. Eseguire il caso penale completo incluso: totale medio forfettario €4.296,03.
6. Chiedere patrocinio Stato: deve segnalare fuori copertura.
7. Aprire l’HTML e salvarlo in PDF; controllare fasi, accessori e dati selezionati.

Registrare nome e versione dell’app, sistema operativo, versione Python, percorso installazione, modalità di invocazione e file risultanti. Solo dopo questa prova aggiornare uno stato in “testato”.

## Aggiornamento CI del primo rilascio

Dopo aver corretto la conservazione dei fine riga del checkout Git, i 30 test e la verifica dataset sono passati nei runner Windows con Python 3.10 e 3.13, Linux con Python 3.10 e 3.13 e macOS con Python 3.13. È stato avviato anche il job macOS/Python 3.10. Il pacchetto include `.gitattributes` per preservare i byte delle fonti e il dataset; input/output e test usano UTF-8 esplicito. È inoltre prevista una verifica contro i doppi fine riga nell’export CSV Windows.

[Esecuzione CI di verifica](https://github.com/Antocatt/codex_chatleg/actions/runs/37828478397).

I controlli generali preesistenti del fork hanno inoltre rilevato una release Rust 0.74.0 mancante e problemi di checksum/autenticazione delle dipendenze Bazel. Questi errori restano fuori dallo scopo della skill autonoma; nessun codice Rust è stato modificato. Le app desktop e la scoperta automatica non sono state testate.
