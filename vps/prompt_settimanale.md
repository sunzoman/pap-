[Scansione KB Salute — SETTIMANALE, domenica mattina, eseguita in automatico sulla VPS «miles» come utente federico, senza nessuno in chat.]

Aggiorna la knowledge base "Salute Massimo Sunzini" seguendo CLAUDE.md e memoria/MEMORIA.md (branch claude/drive-knowledge-base-setup-d7vccx, già aggiornato dallo script di avvio). Tre parti: A) documenti su Drive, B) dati sportivi Garmin, C) report + avviso via mail. Chiusura con riepilogo per mail a Federico.

STRUMENTI SU QUESTA MACCHINA (leggi la sezione "Esecuzione sulla VPS" di CLAUDE.md)
- Qui NON ci sono i connettori di claude.ai. Per Drive usa `python3 strumenti/google_api.py` (ls, info, scarica, carica, rinomina, cestina); per la posta `python3 strumenti/gmail_send.py`.
- Le credenziali sono già nelle variabili d'ambiente (INTERVALS_API_KEY, token Google su file, GITHUB_TOKEN per git). Non leggere, stampare o copiare MAI file di credenziali o variabili segrete.
- File temporanei SOLO in `tmp/` (ignorata da git); cancellala a fine lavoro con `python3 -c "import shutil; shutil.rmtree('tmp', ignore_errors=True)"`.
- Con lo scope drive.file lo script può modificare solo i file che ha creato lui: se una rinomina o un cestinamento di un file creato altrove dà 403, non è un errore bloccante — annotalo nel riepilogo come "da fare a mano".

PARTE A — DOCUMENTI DRIVE
1. `python3 strumenti/google_api.py ls 1MYOQz6jvyd59SkyRhJsugH65FJieO6PU --ricorsivo > tmp/drive.jsonl` (crea prima tmp/).
2. Confronta con l'inventario in MEMORIA.md (chiave: ID Drive; discriminante: modifiedTime).
3. File NUOVI: scaricali in tmp/ con `scarica`, leggili integralmente (lo strumento Read legge i PDF) e crea la scheda. Rinomina secondo la convenzione di CLAUDE.md se il contenuto è chiaro; se la rinomina dà 403, annota nella scheda il nome proposto e mettilo nel riepilogo. MAI toccare: file NON VALIDI, i report (`⌛️ `/`🆕`), i due Sheet e `_chiave_intervals_icu.txt` nella cartella Dati Garmin. Sono attesi: documentazione dell'operazione ai polmoni, TAC del torace di controllo, referti di visite recenti — l'anamnesi in MEMORIA.md dà il contesto.
4. File MODIFICATI: aggiorna la scheda. RIMOSSI: marca [RIMOSSO DAL DRIVE il <data>]. I .numbers restano non indicizzabili; i report restano esclusi (solo elenco in "Report generati").

PARTE B — DATI GARMIN (intervals.icu)
5. Scarica con curl (utente letterale API_KEY, password $INTERVALS_API_KEY):
   https://intervals.icu/api/v1/athlete/i685995/activities?oldest=2015-01-01&newest=<oggi>  -> tmp/garmin/acts_raw.json
   https://intervals.icu/api/v1/athlete/i685995/wellness?oldest=2015-01-01&newest=<oggi>    -> tmp/garmin/well_raw.json
   I nomi sono obbligatori (controllo in costruisci_csv.py).
6. `JSON_DIR=tmp/garmin python3 strumenti/costruisci_csv.py`.
7. Se i CSV cambiano: aggiorna la scheda "Dati sportivi Garmin" in MEMORIA.md (periodo, numero attività, ultime 8 settimane, medie e trend, segnali — mai le singole righe). Regola di plausibilità: valori fuori scala vanno aggiunti a ESCLUSI e documentati. Il sync può portare allenamenti retroattivi.
8. Replica i CSV su Drive come Sheet nella cartella Dati Garmin (ID 1xUZ2RmuYnvjgzxBfih5rLT93dH6PgKm3): `carica dati/garmin/attivita.csv --titolo "Attività sportive" --cartella <id> --converti sheet` e lo stesso per benessere.csv ("Benessere"); poi cestina le versioni precedenti con lo stesso titolo (se 403, annotalo).
9. CONTROLLO SONNO GARMIN: in well_raw.json conta i giorni degli ultimi 7 con `sleepSecs` valorizzato, e da quanti giorni non arriva alcun dato (né benessere né allenamenti). Serve al punto 13.

PARTE C — REPORT E AVVISO A MASSIMO
10. Genera SEMPRE il report in formato documento: `python3 strumenti/genera_report_doc.py <AAAA-MM-GG di oggi> tmp/report.md`. Prima aggiorna i testi delle sezioni 1-3 in strumenti/genera_report_doc.py se numeri o fatti salienti sono cambiati (italiano semplice, niente sigle non spiegate, mai i dati NON VALIDI). Il PDF (`genera_report.py`) solo se Federico lo chiede.
11. Rileggi tmp/report.md: numeri coerenti con i CSV, nessuna frase troncata, nessun valore escluso rientrato.
12. Pubblica: `carica tmp/report.md --titolo "dd.mm.yyyy_Report Salute Massimo Sunzini 🆕" --cartella 1MYOQz6jvyd59SkyRhJsugH65FJieO6PU --converti doc`. Verifica scaricandolo di nuovo (`scarica <id> tmp/verifica.md`) che contenga la frase finale del disclaimer. Poi rinomina il report precedente: togli ` 🆕` e metti il prefisso `⌛️ ` (se 403, annotalo). Se esiste già un report con la stessa data, cestina il precedente.
13. SOLO SE la pubblicazione è verificata, scrivi il corpo in tmp/mail.txt e invia con `python3 strumenti/gmail_send.py --a massimo.sunzini@forkey.it --cc federico.sunzini@widerview.it --oggetto "Nuovo report sulla tua salute pronto su Drive" --corpo-file tmp/mail.txt`. Regole del corpo (tutte vincolanti, dettagli in CLAUDE.md):
    - breve, italiano semplice: c'è una nuova versione del report, nome del file, link https://drive.google.com/open?id=1MYOQz6jvyd59SkyRhJsugH65FJieO6PU;
    - NIENTE valori, diagnosi o interpretazioni cliniche;
    - se qualcosa non va, dillo in una riga come consiglio pratico;
    - SONNO GARMIN: se negli ultimi 7 giorni nessuna notte ha il sonno, una riga che rimanda ai passi della mail dell'11/10/2026 (Garmin Connect → Altro → Impostazioni → App collegate → intervals.icu: il sonno è tra i dati condivisi? se no, su intervals.icu Settings → Garmin scollegare e ricollegare con tutte le caselle spuntate; Federico può aiutarlo). Se il sonno è tornato: niente, ma registralo in MEMORIA.md. Se da più di 3 giorni non arriva nessun dato, ricorda di aprire Garmin Connect per sincronizzare;
    - DOCUMENTI MANCANTI: una o due righe per quelli ancora assenti (operazione ai polmoni, TAC del torace, referti di visite recenti); non citare quelli arrivati;
    - firma "Miles - l'assistente di Federico" e chiusura "Messaggio automatico della cartella salute gestita da Federico, scritto da un assistente AI.";
    - una sola mail per report; se la pubblicazione fallisce, niente mail a Massimo.
14. Aggiungi il report a "Report generati" in MEMORIA.md — non indicizzarlo come scheda.

CHIUSURA
15. Aggiorna "Ultima scansione" e il "Registro scansioni" (scrivi che la scansione è girata sulla VPS). Verifica che nessun segreto sia finito nei file: `git diff | grep -iE "api_key|token|secret|password"` deve risultare vuoto (escluse le parole nel testo delle regole). Poi commit e `git push origin claude/drive-knowledge-base-setup-d7vccx` (le credenziali git sono già configurate dallo script di avvio). Niente pull request.
16. Riepilogo a Federico: scrivi il corpo in tmp/riepilogo.txt e invialo con gmail_send.py a federico.sunzini@widerview.it, oggetto "Salute papà: scansione settimanale del <data>". Corpo breve e SENZA valori clinici: novità trovate, esito del controllo sul sonno, report pubblicato (nome file), mail a Massimo inviata o no, eventuali cose "da fare a mano". Se non è cambiato nulla nei dati, dillo in una riga. Firma "Miles".
17. Cancella tmp/.
