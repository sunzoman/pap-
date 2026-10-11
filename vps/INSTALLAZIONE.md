# Installazione della scansione settimanale sulla VPS «miles»

Obiettivo: far girare la scansione della domenica come utente `federico`, con credenziali proprie, senza le approvazioni manuali dei connettori di claude.ai. Tempo stimato: 30-40 minuti, una volta sola.

Regola generale: **i segreti non si incollano mai in chat** (né con Claude né con Miles). Vanno solo nei file indicati, con permessi 600.

---

## Passo 0 — Cosa fa Miles (aios) per te

Chiedi a Miles, testualmente:

> Copia il client OAuth Google di IntelOS (il file JSON del client "desktop", non i token) in `/home/federico/.config/salute/google_client.json`, proprietario federico, permessi 600, cartella `/home/federico/.config/salute` con permessi 700. Non leggermene il contenuto in chat.

## Passo 1 — Cartelle private

Entra sulla VPS come `federico` e lancia:

```bash
mkdir -p ~/.config/salute ~/salute-papa-log
chmod 700 ~/.config/salute ~/salute-papa-log
ls -l ~/.config/salute/google_client.json   # deve esistere, -rw------- federico
```

## Passo 2 — Token GitHub (solo per questo repository)

1. Da browser: GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
2. Nome `salute-papa-vps`, scadenza 1 anno, Repository access: **Only select repositories → sunzoman/pap-**.
3. Permissions → Repository permissions → **Contents: Read and write** (il resto resta su No access).
4. Copia il token: serve al passo 4.

## Passo 3 — Accesso a Claude (posto Team)

```bash
claude setup-token
```

Segui il link, accedi con il tuo account Claude (posto Team) e copia il token che compare alla fine: serve al passo 4. Non lanciarlo come `aios`.

## Passo 4 — File delle credenziali

```bash
nano ~/.config/salute/env
```

Contenuto (sostituisci i valori, senza spazi attorno all'uguale):

```
CLAUDE_CODE_OAUTH_TOKEN=...token del passo 3...
GITHUB_TOKEN=...token del passo 2...
INTERVALS_API_KEY=...chiave dal file Drive Dati Garmin/_chiave_intervals_icu.txt...
# facoltativo, per gli avvisi di errore su Telegram con un bot personale:
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_CHAT_ID=...
```

Poi:

```bash
chmod 600 ~/.config/salute/env
```

## Passo 5 — Clonare il repository

```bash
cd ~
set -a; . ~/.config/salute/env; set +a
git -c credential.helper='!f() { echo username=x-access-token; echo "password=${GITHUB_TOKEN}"; }; f' \
  clone -b claude/drive-knowledge-base-setup-d7vccx https://github.com/sunzoman/pap-.git salute-papa
chmod 700 ~/salute-papa
setfacl -R -b ~/salute-papa ~/.config/salute ~/salute-papa-log 2>/dev/null || true
cd ~/salute-papa
git config user.name "Miles (salute papà)"
git config user.email "federico.sunzini@widerview.it"
chmod +x vps/esegui_settimanale.sh
```

`setfacl -b` toglie i permessi extra che `aios` eredita sulla tua home: non ferma chi ha sudo, ma evita letture casuali.

## Passo 6 — Autorizzazione Google (una volta sola)

```bash
cd ~/salute-papa
python3 strumenti/google_api.py auth
```

Apri il link sul tuo computer, accedi con **federico.sunzini@widerview.it**, autorizza. Il browser finirà su una pagina "localhost" che non si carica: è previsto. Copia l'indirizzo completo dalla barra e incollalo nel terminale. Deve comparire `OK: autorizzazione salvata`.

Permessi richiesti: lettura di Drive, scrittura solo sui file creati dallo script, invio mail. Lo script non può cancellare o modificare altri file tuoi o dell'azienda.

## Passo 7 — Verifiche rapide

```bash
cd ~/salute-papa
python3 strumenti/google_api.py ls 1MYOQz6jvyd59SkyRhJsugH65FJieO6PU | head -3     # elenca la cartella
printf 'Prova di invio dalla VPS.\n\nMiles' > /tmp/prova.txt
python3 strumenti/gmail_send.py --a federico.sunzini@widerview.it --oggetto "Prova VPS salute" --corpo-file /tmp/prova.txt
claude -p "rispondi solo: ok" --settings vps/settings-vps.json --permission-mode dontAsk
```

Devono arrivare: tre righe di file, la mail di prova, la parola "ok".

## Passo 8 — Prova completa (domenica 18 ottobre)

```bash
crontab -e
```

Aggiungi questa riga (ora di Roma, fuori dalla fascia degli agenti notturni di Miles):

```
30 7 18 10 * SALUTE_PROVA=1 /home/federico/salute-papa/vps/esegui_settimanale.sh
```

In modalità prova: report con prefisso `[PROVA]`, mail solo a te, niente push. Quel giorno la Routine di claude.ai gira comunque alle 4:00 e manda la mail vera a papà.

## Passo 9 — Passaggio definitivo

Se la prova va bene:

1. Cestina su Drive il report `[PROVA]`.
2. **Una tantum, a mano su Drive**: rinomina l'ultimo report 🆕 con il prefisso `⌛️ ` e cestina i due vecchi Sheet in `Dati Garmin`. Lo script non può farlo perché quei file li ha creati il connettore di claude.ai, non lui.
3. Sostituisci la riga di cron con:
   ```
   30 7 * * 0 /home/federico/salute-papa/vps/esegui_settimanale.sh
   ```
4. Scrivi in chat a Claude di **disattivare la Routine** "Scansione KB Salute + report settimanale", così non partono due mail.

## Se qualcosa va storto

- Ti arriva una mail "scansione settimanale NON riuscita" (e su Telegram, se configurato).
- I log stanno in `~/salute-papa-log/` (ultimi 12, permessi 600): contengono dati sanitari, non inoltrarli.
- Per rilanciare a mano: `~/salute-papa/vps/esegui_settimanale.sh`.
