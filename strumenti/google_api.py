# -*- coding: utf-8 -*-
"""Accesso diretto a Google Drive e Gmail per l'esecuzione sulla VPS.

Sostituisce i connettori di claude.ai, che nelle sessioni automatiche richiedono
un'approvazione manuale per ogni scrittura (blocco dell'organizzazione). Solo
libreria standard: nessuna dipendenza da installare.

File di configurazione (permessi 600, MAI nel repository):
  ~/.config/salute/google_client.json   client OAuth "desktop" (fornito da Miles)
  ~/.config/salute/google_token.json    creato dal comando `auth`

Comandi:
  auth                                   autorizzazione iniziale (una volta sola)
  ls <cartella_id> [--ricorsivo]         elenco file in JSON, una riga per file
  info <file_id>                         metadati in JSON
  scarica <file_id> <destinazione>       scarica (Doc -> Markdown/testo, Sheet -> CSV)
  carica <file> --titolo T --cartella ID [--converti doc|sheet]
  rinomina <file_id> <nuovo_titolo>
  cestina <file_id>
"""
import base64, hashlib, json, os, secrets, sys, time
import urllib.error, urllib.parse, urllib.request

CONF = os.path.expanduser(os.environ.get("SALUTE_CONF_DIR", "~/.config/salute"))
CLIENT = os.path.join(CONF, "google_client.json")
TOKEN = os.path.join(CONF, "google_token.json")
SCOPES = os.environ.get(
    "SALUTE_GOOGLE_SCOPES",
    "https://www.googleapis.com/auth/drive.readonly "
    "https://www.googleapis.com/auth/drive.file "
    "https://www.googleapis.com/auth/gmail.send").split()
REDIRECT = "http://localhost:8765/"
DRIVE = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3"
CAMPI = "id,name,mimeType,modifiedTime,size,parents,trashed"
CONVERSIONI = {"doc": "application/vnd.google-apps.document",
               "sheet": "application/vnd.google-apps.spreadsheet"}
MIME = {".md": "text/markdown", ".csv": "text/csv", ".pdf": "application/pdf",
        ".txt": "text/plain"}


def errore(msg):
    sys.exit(f"ERRORE: {msg}")


def _client():
    if not os.path.exists(CLIENT):
        errore(f"manca {CLIENT} (client OAuth). Vedi vps/INSTALLAZIONE.md, passo 1.")
    dati = json.load(open(CLIENT))
    return dati.get("installed") or dati.get("web") or dati


def _scrivi_privato(percorso, dati):
    os.makedirs(os.path.dirname(percorso), mode=0o700, exist_ok=True)
    fd = os.open(percorso, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(dati, f)


def _post_form(url, campi):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(campi).encode())
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        errore(f"{url} -> {e.code} {e.read().decode(errors='replace')[:300]}")


def auth():
    """Flusso OAuth per server senza browser: si apre il link sul proprio computer,
    si autorizza, il browser finisce su una pagina localhost che non si carica:
    si copia l'indirizzo completo dalla barra e lo si incolla qui."""
    c = _client()
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    stato = secrets.token_urlsafe(16)
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
        "scope": " ".join(SCOPES), "access_type": "offline", "prompt": "consent",
        "code_challenge": challenge, "code_challenge_method": "S256", "state": stato})
    print("1) Apri questo link nel browser del tuo computer e autorizza con federico.sunzini@widerview.it:\n")
    print(url + "\n")
    print("2) Alla fine il browser mostra un errore su 'localhost': e' normale.")
    risposta = input("3) Copia l'indirizzo completo dalla barra del browser e incollalo qui: ").strip()
    q = urllib.parse.parse_qs(urllib.parse.urlparse(risposta).query)
    if q.get("state", [""])[0] != stato:
        errore("lo 'state' non corrisponde: ripeti il comando auth.")
    if "code" not in q:
        errore(f"nessun codice nell'indirizzo incollato ({q.get('error', ['?'])[0]}).")
    t = _post_form("https://oauth2.googleapis.com/token", {
        "code": q["code"][0], "client_id": c["client_id"], "client_secret": c.get("client_secret", ""),
        "redirect_uri": REDIRECT, "grant_type": "authorization_code", "code_verifier": verifier})
    if "refresh_token" not in t:
        errore("Google non ha restituito un refresh token: ripeti il comando auth.")
    _scrivi_privato(TOKEN, {"refresh_token": t["refresh_token"], "scope": t.get("scope", "")})
    print(f"OK: autorizzazione salvata in {TOKEN} (permessi 600). Scope: {t.get('scope', '')}")


_cache = {}


def access_token():
    if _cache.get("scade", 0) > time.time() + 60:
        return _cache["token"]
    if not os.path.exists(TOKEN):
        errore(f"manca {TOKEN}: eseguire prima `python3 strumenti/google_api.py auth`.")
    c = _client()
    r = _post_form("https://oauth2.googleapis.com/token", {
        "client_id": c["client_id"], "client_secret": c.get("client_secret", ""),
        "refresh_token": json.load(open(TOKEN))["refresh_token"], "grant_type": "refresh_token"})
    _cache.update(token=r["access_token"], scade=time.time() + r.get("expires_in", 3000))
    return _cache["token"]


def chiama(metodo, url, corpo=None, tipo="application/json", grezzo=False):
    dati = corpo if isinstance(corpo, (bytes, type(None))) else json.dumps(corpo).encode()
    for tentativo in range(4):
        req = urllib.request.Request(url, data=dati, method=metodo, headers={
            "Authorization": f"Bearer {access_token()}", "Content-Type": tipo})
        try:
            r = urllib.request.urlopen(req, timeout=120).read()
            return r if grezzo else (json.loads(r) if r else {})
        except urllib.error.HTTPError as e:
            testo = e.read().decode(errors="replace")
            # quota e errori temporanei: si riprova con attesa crescente
            if e.code in (429, 500, 502, 503) or "exhausted" in testo.lower():
                time.sleep(15 * (tentativo + 1))
                continue
            if e.code in (403, 404):
                errore(f"{e.code} su {url.split('?')[0]}: permesso negato o file non trovato. "
                       f"Con lo scope drive.file si possono modificare solo i file creati da questo script: "
                       f"gli altri vanno rinominati o cestinati a mano. Dettaglio: {testo[:200]}")
            errore(f"{metodo} {url.split('?')[0]} -> {e.code} {testo[:300]}")
    errore(f"{metodo} {url.split('?')[0]}: ancora errori temporanei dopo 4 tentativi.")


def ls(cartella, ricorsivo=False, percorso=""):
    token = None
    while True:
        q = {"q": f"'{cartella}' in parents and trashed=false", "fields": f"nextPageToken,files({CAMPI})",
             "pageSize": "1000", "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"}
        if token:
            q["pageToken"] = token
        r = chiama("GET", f"{DRIVE}/files?" + urllib.parse.urlencode(q))
        for f in r.get("files", []):
            f["percorso"] = f"{percorso}{f['name']}"
            print(json.dumps(f, ensure_ascii=False))
            if ricorsivo and f["mimeType"] == "application/vnd.google-apps.folder":
                ls(f["id"], True, f"{percorso}{f['name']}/")
        token = r.get("nextPageToken")
        if not token:
            break


def info(fid):
    return chiama("GET", f"{DRIVE}/files/{fid}?fields={CAMPI}&supportsAllDrives=true")


def scarica(fid, dest):
    m = info(fid)["mimeType"]
    if m == "application/vnd.google-apps.document":
        try:
            dati = chiama("GET", f"{DRIVE}/files/{fid}/export?mimeType=text/markdown", grezzo=True)
        except SystemExit:
            dati = chiama("GET", f"{DRIVE}/files/{fid}/export?mimeType=text/plain", grezzo=True)
    elif m == "application/vnd.google-apps.spreadsheet":
        dati = chiama("GET", f"{DRIVE}/files/{fid}/export?mimeType=text/csv", grezzo=True)
    else:
        dati = chiama("GET", f"{DRIVE}/files/{fid}?alt=media&supportsAllDrives=true", grezzo=True)
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    open(dest, "wb").write(dati)
    print(json.dumps({"id": fid, "salvato": dest, "byte": len(dati)}))


def carica(file, titolo, cartella, converti=None):
    contenuto = open(file, "rb").read()
    tipo = MIME.get(os.path.splitext(file)[1].lower(), "application/octet-stream")
    meta = {"name": titolo, "parents": [cartella]}
    if converti:
        meta["mimeType"] = CONVERSIONI[converti]
    confine = "salute" + secrets.token_hex(8)
    corpo = (f"--{confine}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
             f"{json.dumps(meta)}\r\n--{confine}\r\nContent-Type: {tipo}\r\n\r\n").encode() \
        + contenuto + f"\r\n--{confine}--\r\n".encode()
    r = chiama("POST", f"{UPLOAD}/files?uploadType=multipart&supportsAllDrives=true&fields={CAMPI}",
               corpo, tipo=f"multipart/related; boundary={confine}")
    r["byte_locali"] = len(contenuto)
    print(json.dumps(r, ensure_ascii=False))


def rinomina(fid, titolo):
    print(json.dumps(chiama("PATCH", f"{DRIVE}/files/{fid}?supportsAllDrives=true&fields={CAMPI}",
                            {"name": titolo}), ensure_ascii=False))


def cestina(fid):
    print(json.dumps(chiama("PATCH", f"{DRIVE}/files/{fid}?supportsAllDrives=true&fields={CAMPI}",
                            {"trashed": True}), ensure_ascii=False))


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd, resto = a[0], a[1:]
    if cmd == "auth":
        auth()
    elif cmd == "ls" and resto:
        ls(resto[0], "--ricorsivo" in resto)
    elif cmd == "info" and resto:
        print(json.dumps(info(resto[0]), ensure_ascii=False))
    elif cmd == "scarica" and len(resto) == 2:
        scarica(*resto)
    elif cmd == "carica" and resto:
        opz = dict(zip(resto[1::2], resto[2::2]))
        if "--titolo" not in opz or "--cartella" not in opz:
            sys.exit("Uso: carica <file> --titolo T --cartella ID [--converti doc|sheet]")
        carica(resto[0], opz["--titolo"], opz["--cartella"], opz.get("--converti"))
    elif cmd == "rinomina" and len(resto) == 2:
        rinomina(*resto)
    elif cmd == "cestina" and resto:
        cestina(resto[0])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
