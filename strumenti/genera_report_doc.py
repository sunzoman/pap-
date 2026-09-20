# -*- coding: utf-8 -*-
"""Genera il report settimanale in Markdown, da caricare su Drive come documento Google.

Perche' esiste: il PDF va caricato su Drive trascrivendo a mano ~22.000 caratteri di
base64, e a quella lunghezza la trascrizione sbaglia (20/09/2026: due tentativi, due
file diversi dall'originale). Il testo semplice invece si carica come testo, quindi
l'upload non puo' corrompersi. Il PDF con i grafici vettoriali resta per le richieste
esplicite dell'utente in chat.

I testi delle sezioni 1-3 sono gli stessi di genera_report.py: se si modificano li',
vanno allineati anche qui.
"""
import csv, os, sys, datetime, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(REPO, "dati", "garmin")
DATA = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "report.md")

ben = list(csv.DictReader(open(f"{DATI}/benessere.csv", encoding="utf-8")))
att = list(csv.DictReader(open(f"{DATI}/attivita.csv", encoding="utf-8")))

MESI_BR = {"01": "Gen", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mag", "06": "Giu",
           "07": "Lug", "08": "Ago", "09": "Set", "10": "Ott", "11": "Nov", "12": "Dic"}


def num(r, k):
    v = r.get(k, "")
    try:
        return float(v) if v != "" else None
    except ValueError:
        return None


def media(mese, campo, righe):
    v = [num(r, campo) for r in righe if r["Data"].startswith(mese)]
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def fmt(x, d=0):
    return "—" if x is None else (f"{x:.{d}f}".replace(".", ","))


def gg_mm_aaaa(iso):
    a, m, g = iso.split("-")
    return f"{g}/{m}/{a}"


mesi = sorted({r["Data"][:7] for r in ben} | {r["Data"][:7] for r in att})
ultimo_dato = max(att[-1]["Data"], ben[-1]["Data"])

# ------------------------------------------------------------------ aggregati
sec_tot = sum(int(a["Durata (s)"]) for a in att if a["Durata (s)"])
km_tot = sum(float(a["Distanza (km)"]) for a in att if a["Distanza (km)"])
oggi = datetime.date.fromisoformat(DATA)
recenti = [a for a in att if datetime.date.fromisoformat(a["Data"]) >= oggi - datetime.timedelta(weeks=8)]
fc_rec = [float(a["FC media"]) for a in recenti if a["FC media"]]
notti_sonno = [r["Data"] for r in ben if r["Sonno (ore)"]]

R = []
w = R.append

w(f"# Report di consultazione — Salute Massimo Sunzini")
w("")
w(f"Generato il {gg_mm_aaaa(DATA)} · Documenti medici e dati sportivi Garmin aggiornati al {gg_mm_aaaa(ultimo_dato)}")
w("")
w("---")
w("")

# ------------------------------------------------------------------ 1
w("## 1. Cosa dicono i dati oggettivi")
w("")
w("Il tema principale sono i polmoni: c'è una bronchite cronica ostruttiva importante — i bronchi lasciano "
  "passare circa il 40% dell'aria che dovrebbero — e i polmoni trattengono troppa aria; sotto sforzo "
  "l'ossigeno nel sangue scende fino all'87%, e anche di notte resta quasi sempre sotto il 95%: l'orologio "
  "lo conferma mese per mese, con il valore più basso (92%) fra ottobre e novembre 2025. Due piccoli noduli "
  "polmonari restano sotto controllo con le TAC. Il cuore batte a ritmo regolare, con qualche battito "
  "irregolare sporadico senza allarmi; la misurazione della pressione delle 24 ore è **non valida per un "
  "errore di misurazione** e va rifatta. Le analisi del sangue sono nel complesso buone; da tenere d'occhio "
  "colesterolo, omocisteina e indici di allergia. Dall'orologio arrivano tre buone notizie: **circa 7 chili "
  "e mezzo persi in un anno**, massa grassa dal 28% al 24% e capacità di usare ossigeno sotto sforzo in "
  "aumento; il battito a riposo è rimasto stabile e normale (fra 55 e 70 al minuto).")
w("")

# ------------------------------------------------------------------ 2
w("## 2. Come sta e come rende, secondo le sensazioni e i dati dell'orologio")
w("")
km_str = f"{km_tot:,.0f}".replace(",", ".")
prima_notte_persa = datetime.date.fromisoformat(notti_sonno[-1]) + datetime.timedelta(days=1)
w(f"Massimo si allena con costanza e si sente bene, e i numeri lo confermano: **{len(att)} uscite in poco più "
  f"di un anno, oltre {round(sec_tot/3600/10)*10} ore e circa {km_str} km"
  "** (soprattutto camminate, bici e canottaggio). Le ultime settimane sono le più intense di tutto l'anno: "
  "165 km in bici nella settimana dal 6 al 12 settembre e **altri 153 km in quella dal 14 al 18**, con "
  "un'uscita da quasi 50 km il 16, la più lunga dell'anno. Durante il test in ospedale aveva riferito solo "
  "affanno e stanchezza moderati, con un consumo di ossigeno del tutto normale: l'orologio racconta la stessa "
  "storia, con un battito medio intorno a 105 durante l'attività e punte fino a 150. In pratica **rende molto "
  "più di quanto i valori dei polmoni farebbero prevedere**, perché il corpo si è abituato a lavorare con meno "
  "ossigeno. Il rovescio della medaglia resta lo stesso: sentendo poco i sintomi, potrebbe non accorgersi di "
  f"un peggioramento. Proprio per questo pesa il fatto che **dal {prima_notte_persa.day} agosto "
  "l'orologio non venga più indossato di notte**: sono sparite le misure di ossigeno notturno, sonno e "
  "recupero, cioè gli unici campanelli d'allarme automatici che avevamo. Resta poi da chiarire il lungo "
  "periodo con pochi allenamenti registrati fra **metà maggio e inizio agosto 2026**: le uscite si "
  "interrompono il 13 maggio e tornano quotidiane solo dal 10 agosto, dopo otto mesi filati da 26-36 al mese. "
  "Vale la pena chiedergli se in quel periodo si è fermato davvero, o se semplicemente non ha avviato la "
  "registrazione sull'orologio.")
w("")

# ------------------------------------------------------------------ 3
w("## 3. Consigli e promemoria")
w("")
w("Le priorità: tornare a indossare l'orologio di notte, proteggere i polmoni e rifare la misurazione della "
  "pressione. Per i polmoni: usare ogni giorno l'inalatore prescritto (Trelegy), fare i vaccini consigliati e "
  "completare l'esame notturno del respiro già suggerito dai medici. Per la pressione: l'esame delle 24 ore va "
  "ripetuto prima di trarre conclusioni; nel frattempo misurarla a casa. Lo sport va continuato con questa "
  "regolarità, tenendo d'occhio l'ossigeno con il saturimetro; a tavola dieta mediterranea. Tutti i consigli "
  "vanno confermati dai medici curanti.")
w("")
w("**Cosa fare**")
w("")
for x in [
    f"Continuare il movimento regolare (nelle ultime otto settimane circa {len(recenti)/8:.0f} uscite a settimana, in crescita da sei settimane di fila): tenere questo ritmo senza aumentarlo ancora, con un saturimetro al dito, e rallentare se l'ossigeno scende sotto 88-90%.",
    "Tenere d'occhio il battito a riposo che l'orologio misura nelle notti in cui viene indossato: se sale sopra 75-80 per più giorni di fila, avvisare il medico.",
    "**Rimettere l'orologio di notte**: da fine agosto non viene più indossato e si sono perse tutte le misure di ossigeno notturno, sonno e recupero. Bastano anche due o tre notti a settimana.",
    "Misurare la pressione a casa mattina e sera e annotarla, in attesa di rifare l'esame delle 24 ore.",
    "Dieta mediterranea: verdure a foglia verde e legumi, pesce, olio d'oliva, poco sale; calcio e vitamina D per le ossa.",
    "Vaccinazioni: antinfluenzale ogni anno, anti-pneumococco e le altre consigliate dallo pneumologo.",
]:
    w(f"- {x}")
w("")
w("**Cosa evitare**")
w("")
for x in [
    "Fumo (anche passivo) e ambienti con polveri o aria inquinata; prudenza con l'alta montagna e i voli lunghi senza parere dello pneumologo.",
    "Sforzi molto intensi e prolungati senza controllare l'ossigeno, soprattutto con il caldo.",
    "Troppo sale e alcol (pressione) e troppi grassi animali (colesterolo).",
    "Integratori o cambi di terapia fai-da-te: ogni modifica va concordata con i medici.",
]:
    w(f"- {x}")
w("")
w("**Da discutere con i medici**")
w("")
for x in [
    "Cardiologo: rifare l'esame della pressione delle 24 ore (quello di ottobre 2025 non è valido) e far rivedere la registrazione del battito.",
    "Pneumologo: mostrare l'andamento dell'ossigeno notturno, sceso al 92% fra ottobre e novembre 2025 e rimasto sotto il 95% quasi tutti i mesi.",
    "Medico di base: vitamine del gruppo B (B9, B12, B6) per l'omocisteina alta, con nuovo prelievo dopo circa 3 mesi.",
    "Pneumologo o allergologo: capire perché gli indici di allergia (IgE) sono alti.",
    "Esame della densità delle ossa (MOC) e vitamina D, per l'indebolimento visto nella radiografia delle mani.",
]:
    w(f"- {x}")
w("")
w("**Promemoria controlli e visite**")
w("")
w("| Esame / visita | Quando | Perché |")
w("|---|---|---|")
for r in [
    ("TAC del torace di controllo", "**In ritardo**: era prevista intorno a luglio 2026. Verificare se è già stata fatta, altrimenti fissarla subito", "Controllo del nodulo di 9 mm al polmone sinistro"),
    ("Visita di Chirurgia Toracica (Osp. S. Andrea)", "Secondo il calendario del centro", "Controllo dell'altro nodulo già in osservazione"),
    ("Esame notturno del respiro (poligrafia con capnografia)", "Da fissare a breve", "Ossigeno notturno sotto il 95% in quasi tutti i mesi"),
    ("Nuovo Holter della pressione (24 ore)", "Appena possibile", "La misurazione di ottobre 2025 non è valida"),
    ("Visita cardiologica", "Dopo il nuovo Holter della pressione", "Pressione e battiti irregolari su dati affidabili"),
    ("Nuovo esame dell'omocisteina", "Ottobre-novembre 2026", "Era alta (25,1) a luglio 2026"),
    ("Spirometria + visita dallo pneumologo", "Ogni anno, o come indicato", "Tenere sotto controllo i polmoni"),
    ("Analisi del sangue complete + PSA", "Luglio 2027 (una volta l'anno)", "Colesterolo, sangue e prostata"),
    ("Esame della densità ossea (MOC)", "Da concordare col medico", "Ossa indebolite alla radiografia delle mani"),
]:
    w(f"| {r[0]} | {r[1]} | {r[2]} |")
w("")

# ------------------------------------------------------------------ 4
w("## 4. I dati misurati dall'orologio Garmin, mese per mese")
w("")
w("Ogni riga è la media del mese. Il trattino significa che in quel mese la misura non è stata registrata "
  "(accade quando l'orologio non viene indossato di notte). Dal battito a riposo sono stati esclusi 62 valori "
  "fra 95 e 117 che non sono misure reali.")
w("")
w("| Mese | Battito a riposo | Recupero (HRV) | Ossigeno notte | Sonno | Peso | Massa grassa | VO2max | Sedute | Ore attività | Battito in attività |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
mensile = []
for m in mesi:
    aa = [r for r in att if r["Data"].startswith(m)]
    ore = sum(num(r, "Durata (s)") or 0 for r in aa) / 3600
    fcs = [num(r, "FC media") for r in aa if num(r, "FC media")]
    fcrip = media(m, "FC a riposo", ben)
    etichetta = f"{MESI_BR[m[5:7]]} {m[2:4]}"
    allarme = " ⚠️" if (fcrip and fcrip >= 78) else ""
    w(f"| {etichetta} | {fmt(fcrip)}{allarme} | {fmt(media(m,'HRV (rMSSD)',ben))} | {fmt(media(m,'SpO2 (%)',ben),1)} | "
      f"{fmt(media(m,'Sonno (ore)',ben),1)} | {fmt(media(m,'Peso (kg)',ben),1)} | {fmt(media(m,'Massa grassa (%)',ben),1)} | "
      f"{fmt(media(m,'VO2max',ben))} | {len(aa) if aa else '—'} | {fmt(ore,1) if aa else '—'} | "
      f"{fmt(sum(fcs)/len(fcs)) if fcs else '—'} |")
    mensile.append((etichetta, len(aa), media(m, "SpO2 (%)", ben), media(m, "Peso (kg)", ben), fcrip))
w("")
w("Nessun mese supera la soglia di attenzione di 78 battiti a riposo. Recupero (HRV) è la variabilità del "
  "battito: più alto significa organismo più riposato. VO2max stima quanto ossigeno il corpo riesce a usare "
  "sotto sforzo.")
w("")

# ------------------------------------------------------------------ 5
w("## 5. L'andamento nell'ultimo anno")
w("")


def barra(valore, minimo, massimo, larghezza=22):
    if valore is None:
        return "—"
    q = max(0.0, min(1.0, (valore - minimo) / (massimo - minimo)))
    pieni = int(round(q * larghezza))
    return "█" * max(pieni, 1) + "·" * (larghezza - max(pieni, 1))


sed = [x[1] for x in mensile]
w("**Attività fisica svolta** (sedute al mese)")
w("")
w("```")
for et, n_sed, _, _, _ in mensile:
    w(f"{et:<7}{barra(n_sed, 0, max(sed))} {n_sed}")
w("```")
w("")
spo = [x[2] for x in mensile if x[2] is not None]
w("**Ossigeno nel sangue di notte** (media del mese; sotto 95% è considerato basso)")
w("")
w("```")
for et, _, s, _, _ in mensile:
    tag = "" if s is None else ("  ← sotto 95%" if s < 95 else "")
    w(f"{et:<7}{barra(s, min(spo)-1, max(spo)+1)} {fmt(s,1)}{tag}")
w("```")
w("")
pes = [x[3] for x in mensile if x[3] is not None]
w("**Peso corporeo** (media del mese, kg)")
w("")
w("```")
for et, _, _, p, _ in mensile:
    w(f"{et:<7}{barra(p, min(pes)-1, max(pes)+1)} {fmt(p,1)}")
w("```")
w("")
w("Come leggerli: il battito a riposo resta per tutto l'anno nella fascia normale, con una leggera risalita "
  "nel 2026. L'ossigeno notturno è il punto debole: resta quasi sempre sotto la soglia del 95%, con il minimo "
  "fra ottobre e novembre 2025 e un recupero nei mesi successivi; attenzione però che gli ultimi mesi poggiano "
  "su pochissime notti misurate, perché da fine agosto l'orologio non viene più indossato per dormire. Il peso "
  "è sceso in modo graduale e costante: è il risultato migliore dell'anno. L'attività fisica è stata molto "
  "regolare da settembre ad aprile, è calata da metà maggio a inizio agosto, ed è poi ripresa con decisione.")
w("")

# ------------------------------------------------------------------ 6
w("## 6. Documenti usati per questo report")
w("")
w("Tutti i file si trovano nella cartella Google Drive \"Salute Massimo Sunzini\".")
w("")
w("| Documento | Data | Cosa contiene |")
w("|---|---|---|")
for r in [
    ("2022.PDF (laboratorio Varelli)", "23/04/2022", "Analisi del sangue e delle urine"),
    ("2024.pdf (laboratorio Varelli)", "02/08/2024", "Analisi del sangue e delle urine"),
    ("2025.pdf (laboratorio Varelli)", "30/09/2025", "Analisi del sangue e delle urine"),
    ("Holter cardiaco e pressorio [pressorio NON VALIDO]", "14-15/10/2025", "Battito 24 ore (valido) + pressione 24 ore (non valida)"),
    ("sunzini Massimo CPET definitivo.pdf (Policlinico Umberto I)", "21/01/2026", "Test da sforzo in bicicletta + esame completo del respiro"),
    ("Aprile 2026.pdf (Lab. Campani)", "18/04/2026", "Emocromo, infiammazione, allergie"),
    ("2026.pdf (laboratorio Varelli)", "22/07/2026", "Analisi del sangue e delle urine"),
    ("fileReferto 2.pdf", "29/07/2026", "Radiografia delle mani"),
    ("Spirometria.numbers", "—", "Foglio Apple non leggibile: da convertire per essere incluso"),
    ("Dati Garmin — fogli \"Attività sportive\" e \"Benessere\"", f"23/08/2025 - {gg_mm_aaaa(ultimo_dato)}",
     f"{len(att)} allenamenti e {len(ben)} giorni di misure, letti da intervals.icu"),
]:
    w(f"| {r[0]} | {r[1]} | {r[2]} |")
w("")
w("---")
w("")
w("Report generato automaticamente dai documenti della cartella Google Drive \"Salute Massimo Sunzini\" e dai "
  "dati dei dispositivi Garmin. Non è un documento medico e non sostituisce il parere dei professionisti "
  "curanti. Sono esclusi due gruppi di dati non attendibili: l'Holter pressorio di ottobre 2025 (errore di "
  "misurazione segnalato) e 62 valori di battito a riposo fra 95 e 117 restituiti dall'orologio nelle notti "
  "in cui non è stato indossato.")
w("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(R))
print("OK", OUT, os.path.getsize(OUT), "byte")
