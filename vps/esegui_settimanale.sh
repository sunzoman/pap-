#!/usr/bin/env bash
# Avvio della scansione settimanale sulla VPS (utente federico, lanciato da cron).
# Legge le credenziali da ~/.config/salute/env (permessi 600), aggiorna il repository,
# lancia Claude Code in modalita' non interattiva e, se qualcosa va storto, avvisa Federico.
#
# Variabili utili:
#   SALUTE_PROVA=1   modalita' prova: nessuna mail a Massimo, nessun push, report con prefisso [PROVA]
set -uo pipefail
umask 077

CONF="$HOME/.config/salute"
REPO="${SALUTE_REPO:-$HOME/salute-papa}"
LOGDIR="$HOME/salute-papa-log"
BRANCH="claude/drive-knowledge-base-setup-d7vccx"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%Y-%m-%d_%H%M).log"
exec > >(tee -a "$LOG") 2>&1

avvisa() {  # $1 = testo breve, senza dati sanitari
  local corpo; corpo="$(mktemp)"
  printf '%s\n\nLog sulla VPS: %s\n\nMiles' "$1" "$LOG" > "$corpo"
  python3 "$REPO/strumenti/gmail_send.py" --a federico.sunzini@widerview.it \
    --oggetto "Salute papà: scansione settimanale NON riuscita" --corpo-file "$corpo" || true
  rm -f "$corpo"
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    curl -s -o /dev/null "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" --data-urlencode "text=Salute papà: $1" || true
  fi
}

# un solo job alla volta
exec 9>"$LOGDIR/.lock"
flock -n 9 || { echo "Un'altra esecuzione e' in corso, esco."; exit 0; }

[ -f "$CONF/env" ] || { echo "Manca $CONF/env"; exit 1; }
set -a; . "$CONF/env"; set +a
for v in CLAUDE_CODE_OAUTH_TOKEN INTERVALS_API_KEY GITHUB_TOKEN; do
  [ -n "${!v:-}" ] || { avvisa "manca la variabile $v nel file di configurazione."; exit 1; }
done

# credenziali git dalla variabile d'ambiente, mai scritte in .git/config
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=credential.helper
export GIT_CONFIG_VALUE_0='!f() { echo username=x-access-token; echo "password=${GITHUB_TOKEN}"; }; f'

cd "$REPO" || { avvisa "cartella del repository non trovata."; exit 1; }
git checkout -q "$BRANCH" && git pull -q --ff-only origin "$BRANCH" \
  || { avvisa "git pull non riuscito (conflitto o rete)."; exit 1; }

PROMPT="$(cat vps/prompt_settimanale.md)"
if [ "${SALUTE_PROVA:-0}" = "1" ]; then
  PROMPT="MODALITA' PROVA ATTIVA: (1) la mail del punto 13 va SOLO a federico.sunzini@widerview.it, senza Massimo, con oggetto che inizia con [PROVA]; (2) il report si carica con il titolo che inizia con [PROVA] e NON si rinominano ne' cestinano altri file su Drive; (3) niente aggiornamento degli Sheet; (4) niente commit ne' push: a fine lavoro annulla le modifiche locali con git checkout -- . e git clean -fd -e tmp/; (5) nel riepilogo scrivi che era una prova.

$PROMPT"
fi

echo "== $(date '+%F %T') avvio scansione (prova=${SALUTE_PROVA:-0})"
claude -p "$PROMPT" \
  --settings vps/settings-vps.json \
  --permission-mode dontAsk \
  --output-format text \
  --max-turns 200
ESITO=$?
rm -rf tmp
echo "== $(date '+%F %T') fine, codice $ESITO"
[ $ESITO -eq 0 ] || avvisa "Claude si e' fermato con codice $ESITO."

# log: si tengono le ultime 12 esecuzioni
ls -1t "$LOGDIR"/*.log 2>/dev/null | tail -n +13 | xargs -r rm -f
exit $ESITO
