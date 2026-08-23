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

Da eseguire **ogni volta che l'utente lo chiede** e **automaticamente tre volte al giorno alle 4:00, 12:00 e 18:00 (ora italiana)** tramite la Routine pianificata "Scansione KB Salute" (nota: con l'ora solare gli orari scivolano un'ora indietro, salvo aggiornamento del cron):

1. Elencare ricorsivamente il contenuto della cartella Drive `1MYOQz6jvyd59SkyRhJsugH65FJieO6PU` (query `parentId = '<id>'` su ogni sottocartella) con il connettore Google Drive.
2. Confrontare l'elenco con l'inventario in `memoria/MEMORIA.md` usando come chiave l'**ID Drive** e come discriminante la **data di modifica** (`modifiedTime`).
3. Per ogni file **nuovo o modificato**: leggerne il contenuto completo (`read_file_content`) e creare/aggiornare la relativa scheda in `MEMORIA.md`.
4. Per ogni file **rimosso** dalla cartella: non cancellare la scheda, ma marcarla `[RIMOSSO DAL DRIVE il <data>]`.
5. **Se la scansione non trova alcuna novità** (nessun file nuovo, modificato o rimosso): terminare in silenzio, **senza commit, senza push e senza messaggi all'utente**.
6. Se invece ci sono novità: aggiornare il campo **"Ultima scansione"**, aggiungere una riga al **Registro scansioni**, poi commit e push sul branch `claude/drive-knowledge-base-setup-d7vccx`:
   `git push -u origin claude/drive-knowledge-base-setup-d7vccx` (retry con backoff in caso di errori di rete).

### Rinomina automatica dei file nuovi (regola dell'utente, 23/08/2026)

Solo per i file **nuovi** trovati dalla scansione (mai retroattiva sui file già indicizzati): se il titolo è incoerente o poco descrittivo rispetto al contenuto, rinominare il file su Drive con `update_file` secondo la convenzione:

`AAAA.MM.GG - Tipo esame (struttura).estensione` — es. `2026.07.29 - RX mani (radiologia).pdf`

dove la data è quella **del documento** (visita/prelievo), non del caricamento. Regole:
- Rinominare solo se il contenuto è chiaro; se ambiguo, lasciare il nome e segnalarlo all'utente.
- Registrare sempre il **nome originale** nella scheda di MEMORIA.md ("Nome originale: ...").
- **Mai rinominare**: file marcati NON VALIDI (hanno la loro convenzione), report generati (`dd.mm.yyyy_*`), gli Sheet nella cartella `Dati Garmin`.

Note operative:
- I file `.numbers` (Apple Numbers) non sono leggibili dal connettore: censirli nell'inventario e segnalarli come non indicizzabili finché non vengono convertiti (es. in Google Sheets/xlsx).
- I duplicati (stesso titolo e stessa dimensione) vanno censiti una sola volta come scheda, annotando gli ID di tutte le copie.
- Il contenuto dei referti è **dato sanitario sensibile**: non copiarlo fuori da questo repository e non inviarlo a servizi esterni.
- **Dati marcati NON VALIDI:** se l'utente segnala che un dato o un referto non è attendibile (es. errore di misurazione), marcarlo chiaramente in MEMORIA.md, rinominare il file su Drive aggiungendo l'indicazione `[... NON VALIDO ...]` nel nome e non usare più quel dato per sintesi cliniche o report.
- **Verifica di plausibilità (regola del 23/08/2026):** prima di usare qualunque serie di misure in un commento clinico, controllare che i valori siano fisiologicamente plausibili. Sono campanelli d'allarme: valori identici ripetuti per giorni consecutivi, salti impossibili fra giorni adiacenti, valori presenti solo quando mancano tutte le altre misure della stessa notte. Se una serie è contaminata, escludere i valori sospetti, conservare il dato grezzo in una colonna a parte e **documentare in MEMORIA.md l'esclusione e le conclusioni precedenti che ne risultano invalidate**. Non presentare mai come reperto clinico un dato non verificato: allarma inutilmente la famiglia.

## Dati sportivi Garmin (pipeline attiva dal 23/08/2026)

**Vincolo dell'utente: nessuno strumento aziendale in questa knowledge base** — niente Make (account Wider View) e niente Strava. Il flusso è: dispositivi Garmin → Garmin Connect → **intervals.icu** (account personale di Massimo, collegato a Garmin) → API letta direttamente durante le scansioni → file CSV nel repository.

**Credenziali:** custodite SOLO nel file Drive `_chiave_intervals_icu.txt` (ID `1u5pg86vG7gROVyrv3Yv2ba3OaLtHpv6F`, dentro la cartella `Dati Garmin`). **Mai** scriverle nel repository, nei commit o nelle variabili d'ambiente. Athlete ID: `i685995`.

**Prerequisito di rete:** l'ambiente cloud deve avere `intervals.icu` tra i domini consentiti (impostato il 23/08/2026 in Accesso alla rete → Personalizzato). Le chiamate vanno fatte con `curl` (urllib di Python non passa dal proxy e riceve 403).

**File dati nel repository** (aggiornati a ogni scansione, sono la fonte per i report):
- `dati/garmin/attivita.csv` — una riga per allenamento: data, ora, sport, nome, durata, distanza, FC media/max, dislivello, calorie, carico, sensazione, dispositivo.
- `dati/garmin/benessere.csv` — una riga per giorno con almeno una misura: FC a riposo (validata), FC a riposo (dato grezzo), HRV (rMSSD), sonno, punteggio sonno, SpO2, peso, massa grassa, VO2max, passi, forma (CTL), fatica (ATL).

**FC a riposo — filtro obbligatorio:** intervals.icu restituisce, nelle notti senza orologio, valori di `restingHR` fra 95 e 117 bpm che **non sono misure** (ripetuti identici per giorni, alternati a valori normali). Scrivere nella colonna `FC a riposo` solo i valori **< 95 bpm** e conservare tutto il resto in `FC a riposo (dato grezzo)`. Usare **solo la colonna validata** per medie, grafici e commenti.

**Copia su Drive:** dopo ogni rigenerazione dei CSV, replicarli come Google Sheet `Attività sportive` e `Benessere` nella sottocartella `Dati Garmin` (upload con `contentMimeType: text/csv`, che Drive converte in Sheet), cestinando la versione precedente. Sono **output**, non fonti: non indicizzarli come schede in MEMORIA.md e non rinominarli.

**Procedura di aggiornamento** (da eseguire in ogni scansione, dopo il controllo della cartella Drive):
1. Leggere le credenziali dal file Drive indicato sopra.
2. Scaricare con `curl` (autenticazione Basic, utente letterale `API_KEY`):
   `https://intervals.icu/api/v1/athlete/i685995/activities?oldest=AAAA-MM-GG&newest=AAAA-MM-GG` e lo stesso per `/wellness`.
3. Rigenerare i due CSV con l'intera finestra storica disponibile (semplice e idempotente); nel foglio benessere scartare i giorni privi di qualsiasi misura.
4. Se i CSV cambiano, aggiornare la scheda "Dati sportivi Garmin" in MEMORIA.md con **periodo coperto, numero di attività, medie e trend recenti** (mai l'elenco delle righe) e committare insieme al resto.

**Uso nei report:** la sezione 2 ("come sta e come rende") usa questi numeri come base oggettiva delle performance, affiancandoli alle sensazioni riferite.

**Note operative:**
- Il file `_chiave_intervals_icu.txt` e i due Google Sheet in `Dati Garmin` NON vanno indicizzati come schede in MEMORIA.md né rinominati.
- HRV e SpO2 sono misurati solo nelle notti in cui l'orologio è indossato con il monitoraggio attivo: la copertura parziale è normale, non è un errore.

## Strumenti

Gli script della knowledge base stanno in [`strumenti/`](strumenti/README.md): `costruisci_csv.py` (JSON intervals.icu -> CSV, con il filtro sulla FC a riposo), `chart.py` (grafici vettoriali) e `genera_report.py` (PDF del report). Modificare quelli, non riscriverli da zero a ogni richiesta.

## Report PDF

Su richiesta dell'utente si genera un report PDF di consultazione (es. `Report_Salute_Massimo_Sunzini_<data>.pdf`). Fonte esclusiva: `memoria/MEMORIA.md`, i file della cartella Drive sopra indicata e i CSV in `dati/garmin/`. **Struttura aggiornata dall'utente il 23/08/2026** (l'elenco dei documenti va in fondo, non in testa):

1. **Sezione 1 — Cosa dicono i dati oggettivi**: massimo ~5 righe su ciò che emerge oggettivamente dai documenti.
2. **Sezione 2 — Come sta e come rende**: stessa lunghezza; tiene conto delle sensazioni riferite (Borg/anamnesi CPET, note personali in cartella) **e degli allenamenti e dei dati Garmin**, che vanno citati esplicitamente come base oggettiva delle performance.
3. **Sezione 3 — Consigli e promemoria**: commento della stessa lunghezza con suggerimenti di terapie e stile di vita (attività sportive, cosa fare/cosa evitare, dieta), seguito da elenchi puntati ("Cosa fare", "Cosa evitare", "Da discutere con i medici") e tabella "Promemoria controlli e visite" (esame/visita, quando, perché).
4. **Sezione 4 — Tabella dei dati Garmin mese per mese**: una riga per mese con FC a riposo, HRV, SpO2, sonno, peso, massa grassa, VO2max, numero di sedute, ore di attività, FC media in attività. Mai l'elenco delle singole giornate.
5. **Sezione 5 — Grafici**, subito sotto la tabella: 4 grafici rilevanti per la salute di Massimo (battito a riposo, ossigeno notturno con linea di riferimento al 95%, peso, attività fisica svolta), seguiti da un breve testo che spiega come leggerli.
6. **Sezione 6 — Documenti usati per questo report**: tabella compatta (documento, data, cosa contiene). **In fondo alla pagina: sono le fonti, non l'apertura.**
7. Chiusura con disclaimer: report generato automaticamente, non è un documento medico e non sostituisce il parere dei curanti; elencare i dati esclusi perché non validi.

Generazione: script reportlab (A4); non usare caratteri fuori WinAnsi (niente frecce/simboli unicode speciali); per i bullet usare il carattere `•` in `bulletText`, non entità XML. **Impostare sempre `rl_config.useA85 = 0`** prima degli import di reportlab: la codifica ASCII85 di default non viene renderizzata dal visualizzatore PDF dell'app Google Drive mobile (pagina quasi vuota); con FlateDecode puro il PDF si vede ovunque.

**Grafici:** disegnarli come vettoriali nativi con `reportlab.graphics.shapes` (Drawing/PolyLine/Circle/Rect/String). Non usare matplotlib né immagini PNG/SVG importate: il PDF passerebbe da ~16 KB a oltre 170 KB e il caricamento su Drive diventa impraticabile. Etichettare solo primo, ultimo e valore estremo di ogni serie, non tutti i punti. Palette: serie `#2a78d6`, riferimento `#e34948`, testo `#0b0b0b`/`#52514e`, griglia `#dcdcd8`.

**Prima di considerarlo finito:** renderizzare il PDF in immagini (`pypdfium2`) e guardarle, per intercettare titoli orfani, tabelle spezzate e pagine quasi vuote. Usare `PageBreak` prima della tabella mensile e `KeepTogether` per tenere insieme intestazione + tabella + disclaimer.

**Caricamento su Drive:** `create_file` richiede il contenuto in base64 nel parametro. Trascrivere il base64 **in un blocco unico** (`cat` del file `.b64` e riporto integrale): spezzarlo in più letture e ricucirlo introduce errori sulle giunzioni. Dopo l'upload confrontare `fileSize` restituito da Drive con la dimensione del file locale: devono coincidere esattamente.

**Linguaggio (regola dell'utente, 22/08/2026):** il report va scritto in italiano semplice, comprensibile a non medici. Evitare sigle e tecnicismi non spiegati: preferire perifrasi ("i bronchi lasciano passare circa il 40% dell'aria che dovrebbero" invece di "FEV1 40% del predetto"); quando un termine tecnico è necessario, spiegarlo tra parentesi. I dati marcati NON VALIDI in MEMORIA.md non vanno mai usati come base per commenti o suggerimenti: citarli solo per dire che l'esame va ripetuto.

### Consegna del report (regola dell'utente, 22/08/2026)

- Oltre all'invio in chat, **caricare sempre il PDF anche nella cartella Drive radice** `Salute Massimo Sunzini` (ID `1MYOQz6jvyd59SkyRhJsugH65FJieO6PU`), NON nella sottocartella "Documenti e referti".
- Nome file obbligatorio con la data di generazione nel formato `dd.mm.yyyy`: **`dd.mm.yyyy_Report Salute Massimo Sunzini.pdf`** (es. `22.08.2026_Report Salute Massimo Sunzini.pdf`).
- Ogni rigenerazione carica un nuovo file con la data corrente; le versioni precedenti restano in cartella come storico salvo diversa indicazione dell'utente. Se si rigenera lo stesso giorno, cestinare la versione precedente con la stessa data e caricare quella nuova.
- **Esclusione dall'indicizzazione:** i report generati (file il cui nome inizia con una data `dd.mm.yyyy_`) sono OUTPUT della knowledge base, non fonti. La scansione (notturna o su richiesta) NON deve indicizzarli come schede in MEMORIA.md; vanno solo elencati nella sezione "Report generati" della memoria.
- **Verifica di integrità dell'upload:** dopo `create_file` confrontare la dimensione restituita da Drive con quella del file locale; in caso di dubbio riscaricare con `download_file_content` e confrontare i contenuti.
