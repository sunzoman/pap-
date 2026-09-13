# -*- coding: utf-8 -*-
"""Costruisce i CSV Garmin dai JSON grezzi scaricati da intervals.icu con curl.

Nota sulla FC a riposo: intervals.icu restituisce, nei giorni in cui l'orologio
non e' stato indossato di notte, valori non fisiologici (95-117 bpm) ripetuti
identici per giorni consecutivi. Non sono misure: vengono esclusi dalla colonna
validata e conservati nella colonna del dato grezzo.
"""
import json, csv, os, sys, time

SOGLIA_FC = 95  # bpm: sopra questa soglia il valore non e' una misura attendibile
ETA_MAX_ORE = 6  # oltre questa eta' un JSON e' considerato un residuo di una scansione precedente
D = os.environ.get("JSON_DIR", ".")  # cartella con acts_raw.json e well_raw.json scaricati via curl
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dati", "garmin")

def controlla(nome):
    """I JSON devono esistere ed essere freschi.

    Se si scaricano con un nome diverso da quello atteso, senza questo controllo
    lo script rigenera i CSV dai file della scansione precedente senza segnalare
    nulla: e' successo il 06/09/2026 e il 13/09/2026 (att.json/wel.json invece di
    acts_raw.json/well_raw.json).
    """
    percorso = os.path.join(D, nome)
    if not os.path.exists(percorso):
        presenti = sorted(f for f in os.listdir(D) if f.endswith(".json")) or ["nessuno"]
        sys.exit(f"ERRORE: manca {percorso}.\n"
                 f"JSON presenti in {D}: {', '.join(presenti)}.\n"
                 f"Scaricare con curl usando esattamente i nomi acts_raw.json e well_raw.json "
                 f"(vedi strumenti/README.md).")
    ore = (time.time() - os.path.getmtime(percorso)) / 3600
    if ore > ETA_MAX_ORE:
        sys.exit(f"ERRORE: {percorso} risale a {ore:.1f} ore fa, probabilmente e' un residuo "
                 f"di una scansione precedente. Riscaricarlo da intervals.icu prima di procedere.")
    return percorso

acts_json = controlla("acts_raw.json")
well_json = controlla("well_raw.json")

def hhmm(s):
    return f"{int(s)//3600:d}:{(int(s)%3600)//60:02d}" if s else ""

acts = json.load(open(acts_json))
acts.sort(key=lambda a: a.get("start_date_local") or "")
with open(f"{OUT}/attivita.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Data", "Ora", "Sport", "Nome", "Durata (h:mm)", "Durata (s)", "Distanza (km)",
                "FC media", "FC max", "Dislivello (m)", "Calorie", "Carico allenamento",
                "Sensazione (1-5)", "Dispositivo"])
    for a in acts:
        sd = a.get("start_date_local") or ""
        w.writerow([sd[:10], sd[11:16], a.get("type") or "", a.get("name") or "",
                    hhmm(a.get("moving_time")), a.get("moving_time") or "",
                    round(a["distance"] / 1000, 2) if a.get("distance") else "",
                    a.get("average_heartrate") or "", a.get("max_heartrate") or "",
                    round(a["total_elevation_gain"]) if a.get("total_elevation_gain") else "",
                    a.get("calories") or "", a.get("icu_training_load") or "",
                    a.get("feel") or "", a.get("device_name") or ""])

well = json.load(open(well_json))
well.sort(key=lambda g: g.get("id") or "")
righe = 0
with open(f"{OUT}/benessere.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Data", "FC a riposo", "FC a riposo (dato grezzo)", "HRV (rMSSD)",
                "Sonno (ore)", "Punteggio sonno", "SpO2 (%)", "Peso (kg)",
                "Massa grassa (%)", "VO2max", "Passi", "Forma (CTL)", "Fatica (ATL)"])
    for g in well:
        misure = [g.get(k) for k in ("restingHR", "hrv", "sleepSecs", "sleepScore",
                                     "spO2", "weight", "bodyFat", "vo2max", "steps")]
        if not any(v is not None for v in misure):
            continue
        righe += 1
        fc = g.get("restingHR")
        w.writerow([g.get("id") or "",
                    fc if (fc is not None and fc < SOGLIA_FC) else "",
                    fc if fc is not None else "",
                    g.get("hrv") or "",
                    round(g["sleepSecs"] / 3600, 1) if g.get("sleepSecs") else "",
                    g.get("sleepScore") or "", g.get("spO2") or "", g.get("weight") or "",
                    g.get("bodyFat") or "", g.get("vo2max") or "", g.get("steps") or "",
                    round(g["ctl"], 1) if g.get("ctl") is not None else "",
                    round(g["atl"], 1) if g.get("atl") is not None else ""])
scartati = sum(1 for g in well if (g.get("restingHR") or 0) >= SOGLIA_FC)
print(f"attivita: {len(acts)} righe")
print(f"benessere: {righe} giorni | FC a riposo scartate (>= {SOGLIA_FC} bpm): {scartati}")
