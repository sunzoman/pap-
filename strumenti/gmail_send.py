# -*- coding: utf-8 -*-
"""Invio di una mail in testo semplice da Gmail (account autorizzato in google_api.py).

Uso:
  python3 strumenti/gmail_send.py --a dest@x.it [--cc altro@x.it ...] --oggetto "..." --corpo-file testo.txt

Il corpo si passa da file per evitare problemi di virgolette e a capo nella riga di comando.
"""
import argparse, base64, json, sys
from email.message import EmailMessage

sys.path.insert(0, __import__("os").path.dirname(__file__))
from google_api import chiama  # noqa: E402


def invia(a, cc, oggetto, corpo):
    m = EmailMessage()
    m["To"] = ", ".join(a)
    if cc:
        m["Cc"] = ", ".join(cc)
    m["Subject"] = oggetto
    m.set_content(corpo)
    raw = base64.urlsafe_b64encode(m.as_bytes()).decode()
    return chiama("POST", "https://gmail.googleapis.com/gmail/v1/users/me/messages/send", {"raw": raw})


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--a", action="append", required=True)
    p.add_argument("--cc", action="append", default=[])
    p.add_argument("--oggetto", required=True)
    p.add_argument("--corpo-file", required=True)
    x = p.parse_args()
    r = invia(x.a, x.cc, x.oggetto, open(x.corpo_file, encoding="utf-8").read())
    print(json.dumps({"inviata": True, "id": r.get("id"), "threadId": r.get("threadId")}))
