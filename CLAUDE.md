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

## Report PDF

Su richiesta dell'utente verrà generato un report PDF di consultazione con struttura specifica (da definire); la fonte del report è esclusivamente `memoria/MEMORIA.md` e i file della cartella Drive sopra indicata.
