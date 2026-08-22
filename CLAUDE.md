# Knowledge Base — Salute Massimo Sunzini

## Fonte unica dei dati (REGOLA VINCOLANTE)

L'**unica fonte autorizzata** per la lettura dei dati di questa knowledge base è la cartella Google Drive:

- **Nome cartella:** `Salute Massimo Sunzini`
- **ID cartella:** `1MYOQz6jvyd59SkyRhJsugH65FJieO6PU`
- **Link:** https://drive.google.com/open?id=1MYOQz6jvyd59SkyRhJsugH65FJieO6PU
- **Proprietario:** massimo.sunzini@forkey.it (condivisa con federico.sunzini@widerview.it)

Non usare altre cartelle Drive, e-mail o fonti esterne per popolare la memoria, salvo istruzione esplicita dell'utente in chat.

## File di memoria

La memoria statica della knowledge base è il file [`memoria/MEMORIA.md`](memoria/MEMORIA.md).
Contiene: inventario dei file della cartella (con ID Drive, data modifica, dimensione), sintesi completa del contenuto di ogni documento, quadro clinico riepilogativo e registro delle scansioni.

## Procedura di aggiornamento della memoria

Da eseguire **ogni volta che l'utente lo chiede** e **automaticamente ogni notte alle 4:00 (ora italiana)** tramite la Routine pianificata "Aggiornamento notturno KB Salute":

1. Elencare ricorsivamente il contenuto della cartella Drive `1MYOQz6jvyd59SkyRhJsugH65FJieO6PU` (query `parentId = '<id>'` su ogni sottocartella) con il connettore Google Drive.
2. Confrontare l'elenco con l'inventario in `memoria/MEMORIA.md` usando come chiave l'**ID Drive** e come discriminante la **data di modifica** (`modifiedTime`).
3. Per ogni file **nuovo o modificato**: leggerne il contenuto completo (`read_file_content`) e creare/aggiornare la relativa scheda in `MEMORIA.md`.
4. Per ogni file **rimosso** dalla cartella: non cancellare la scheda, ma marcarla `[RIMOSSO DAL DRIVE il <data>]`.
5. Aggiornare sempre il campo **"Ultima scansione"** e aggiungere una riga al **Registro scansioni** in fondo al file.
6. Commit e push sul branch `claude/drive-knowledge-base-setup-d7vccx`:
   `git push -u origin claude/drive-knowledge-base-setup-d7vccx` (retry con backoff in caso di errori di rete).

Note operative:
- I file `.numbers` (Apple Numbers) non sono leggibili dal connettore: censirli nell'inventario e segnalarli come non indicizzabili finché non vengono convertiti (es. in Google Sheets/xlsx).
- I duplicati (stesso titolo e stessa dimensione) vanno censiti una sola volta come scheda, annotando gli ID di tutte le copie.
- Il contenuto dei referti è **dato sanitario sensibile**: non copiarlo fuori da questo repository e non inviarlo a servizi esterni.
- **Dati marcati NON VALIDI:** se l'utente segnala che un dato o un referto non è attendibile (es. errore di misurazione), marcarlo chiaramente in MEMORIA.md, rinominare il file su Drive aggiungendo l'indicazione `[... NON VALIDO ...]` nel nome e non usare più quel dato per sintesi cliniche o report.

## Dati sportivi Garmin (pipeline approvata dall'utente il 22/08/2026)

I dati di allenamento e benessere misurati dai dispositivi Garmin di Massimo entrano nella KB attraverso la sottocartella Drive **`Dati Garmin`** (ID `1xUZ2RmuYnvjgzxBfih5rLT93dH6PgKm3`), che contiene due Google Sheet **fonte** (da indicizzare nella scansione come gli altri documenti):

- **`Attività sportive`** (ID `1mK0w3-HCaJUR6dvnw9R-3lsvFBPTqcui-ek0zc58ht0`): una riga per allenamento (data, sport, durata, distanza, FC media/max, passo, dislivello, calorie, sensazione 1-10).
- **`Benessere`** (ID `1lLLLOwxaPMKxerPNi-hQu0-kURr-SAGsQByaiO1SmZk`): una riga per giorno (FC a riposo, HRV, sonno, SpO2 notturna, peso, stress, body battery).

Architettura del flusso (soluzione B+C approvata): Garmin Connect → sincronizzazione nativa verso **Strava** (attività) e **intervals.icu** (benessere) → scenario **Make** (team 2720879, connessione Google `Wider View - Fede` id 13027459; connessione Strava da creare) e/o chiamate API intervals.icu → righe nei due Sheet. Backfill storico: export CSV una tantum da Garmin Connect caricato in `Dati Garmin`.

Regole di indicizzazione:
- Gli Sheet si aggiornano di continuo: la scheda in MEMORIA.md non deve elencare le righe, ma riportare **periodo coperto, numero di attività, medie/trend recenti** (ultime 4-8 settimane) e segnali rilevanti (es. calo di performance, FC a riposo in salita).
- La sezione 2 del report ("come sta e come rende") usa questi dati come base oggettiva delle performance sportive.
- Stato setup: finché i collegamenti Strava/intervals.icu non sono attivi, gli Sheet possono essere vuoti — indicarlo in MEMORIA.md senza considerarlo un errore.

## Report PDF

Su richiesta dell'utente si genera un report PDF di consultazione (es. `Report_Salute_Massimo_Sunzini_<data>.pdf`). Fonte esclusiva: `memoria/MEMORIA.md` e i file della cartella Drive sopra indicata. Struttura definita dall'utente (22/08/2026):

1. **Quadro dei documenti nella cartella** — tabella compatta (documento, data, tipo) per orientarsi tra i file.
2. **Sezione 1 — Commento sui dati oggettivi**: massimo ~5 righe su ciò che emerge oggettivamente dai documenti.
3. **Sezione 2 — Commento integrato con le sensazioni riferite**: stessa lunghezza, tiene conto anche delle sensazioni comunicate su stato di salute e performance sportive (oggi ricavate dai referti, es. Borg/anamnesi CPET; integrare eventuali note personali aggiunte in cartella).
4. **Sezione 3 — Suggerimenti e promemoria**: commento della stessa lunghezza con suggerimenti di terapie e stile di vita (attività sportive, cosa fare/cosa evitare, dieta), seguito da elenchi puntati ("Cosa fare", "Cosa evitare", "Da discutere con i medici") e tabella "Promemoria controlli e visite" (esame/visita, quando, perché).
5. Chiusura con disclaimer: report generato automaticamente, non è un documento medico e non sostituisce il parere dei curanti.

Generazione: script reportlab (A4); non usare caratteri fuori WinAnsi (niente frecce/simboli unicode speciali); per i bullet usare il carattere `•` in `bulletText`, non entità XML. **Impostare sempre `rl_config.useA85 = 0`** prima degli import di reportlab: la codifica ASCII85 di default non viene renderizzata dal visualizzatore PDF dell'app Google Drive mobile (pagina quasi vuota); con FlateDecode puro il PDF si vede ovunque.

**Linguaggio (regola dell'utente, 22/08/2026):** il report va scritto in italiano semplice, comprensibile a non medici. Evitare sigle e tecnicismi non spiegati: preferire perifrasi ("i bronchi lasciano passare circa il 40% dell'aria che dovrebbero" invece di "FEV1 40% del predetto"); quando un termine tecnico è necessario, spiegarlo tra parentesi. I dati marcati NON VALIDI in MEMORIA.md non vanno mai usati come base per commenti o suggerimenti: citarli solo per dire che l'esame va ripetuto.

### Consegna del report (regola dell'utente, 22/08/2026)

- Oltre all'invio in chat, **caricare sempre il PDF anche nella cartella Drive radice** `Salute Massimo Sunzini` (ID `1MYOQz6jvyd59SkyRhJsugH65FJieO6PU`), NON nella sottocartella "Documenti e referti".
- Nome file obbligatorio con la data di generazione nel formato `dd.mm.yyyy`: **`dd.mm.yyyy_Report Salute Massimo Sunzini.pdf`** (es. `22.08.2026_Report Salute Massimo Sunzini.pdf`).
- Ogni rigenerazione carica un nuovo file con la data corrente; le versioni precedenti restano in cartella come storico salvo diversa indicazione dell'utente. Se si rigenera lo stesso giorno, cestinare la versione precedente con la stessa data e caricare quella nuova.
- **Esclusione dall'indicizzazione:** i report generati (file il cui nome inizia con una data `dd.mm.yyyy_`) sono OUTPUT della knowledge base, non fonti. La scansione (notturna o su richiesta) NON deve indicizzarli come schede in MEMORIA.md; vanno solo elencati nella sezione "Report generati" della memoria.
- **Verifica di integrità dell'upload:** dopo `create_file` confrontare la dimensione restituita da Drive con quella del file locale; in caso di dubbio riscaricare con `download_file_content` e confrontare i contenuti.
