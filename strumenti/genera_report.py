# -*- coding: utf-8 -*-
# Report di consultazione — linguaggio semplice per non medici.
# Struttura (regole utente 23/08/2026): commenti -> tabella dati Garmin -> grafici -> fonti in fondo.
from reportlab import rl_config
rl_config.useA85 = 0  # il viewer Drive mobile non renderizza ASCII85
import csv
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether, PageBreak)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(REPO, "dati", "garmin")
# la data del report arriva da riga di comando: python3 genera_report.py 2026-08-23 /percorso/out.pdf
DATA = sys.argv[1] if len(sys.argv) > 1 else "2026-08-23"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"Report_Salute_Massimo_Sunzini_{DATA}.pdf"

BLU = colors.HexColor("#1f3a5f")
GRIGIO = colors.HexColor("#5a6472")
RIGA = colors.HexColor("#d9dee5")
FONDO = colors.HexColor("#eef2f7")
ROSSO = colors.HexColor("#b3261e")

ss = getSampleStyleSheet()
titolo = ParagraphStyle("titolo", parent=ss["Title"], fontName="Helvetica-Bold",
                        fontSize=19, textColor=BLU, spaceAfter=2, alignment=0)
sotto = ParagraphStyle("sotto", parent=ss["Normal"], fontSize=9.5, textColor=GRIGIO)
h = ParagraphStyle("h", parent=ss["Heading2"], fontName="Helvetica-Bold",
                   fontSize=12.5, textColor=BLU, spaceBefore=14, spaceAfter=5)
h2 = ParagraphStyle("h2", parent=h, fontSize=10.5, spaceBefore=10, spaceAfter=4)
corpo = ParagraphStyle("corpo", parent=ss["Normal"], fontSize=10, leading=14.5, alignment=TA_JUSTIFY)
puntato = ParagraphStyle("puntato", parent=corpo, leftIndent=10, bulletIndent=2,
                         spaceAfter=2, alignment=0)
cella = ParagraphStyle("cella", parent=ss["Normal"], fontSize=8, leading=10)
cellac = ParagraphStyle("cellac", parent=cella, alignment=1)
cellah = ParagraphStyle("cellah", parent=cella, fontName="Helvetica-Bold",
                        textColor=colors.white, alignment=1, fontSize=7.5)
cellahl = ParagraphStyle("cellahl", parent=cellah, alignment=0)
nota = ParagraphStyle("nota", parent=ss["Normal"], fontSize=8, leading=10.5, textColor=GRIGIO)

# ---------------------------------------------------------------- dati
ben = list(csv.DictReader(open(f"{DATI}/benessere.csv")))
att = list(csv.DictReader(open(f"{DATI}/attivita.csv")))

def n(r, k):
    v = r.get(k, "")
    try:
        return float(v) if v != "" else None
    except ValueError:
        return None

MESI = {"01": "gennaio", "02": "febbraio", "03": "marzo", "04": "aprile", "05": "maggio",
        "06": "giugno", "07": "luglio", "08": "agosto", "09": "settembre", "10": "ottobre",
        "11": "novembre", "12": "dicembre"}
MESI_BR = {k: v[:3].capitalize() for k, v in MESI.items()}

mesi = sorted({r["Data"][:7] for r in ben} | {r["Data"][:7] for r in att})

def media(mese, campo, righe):
    v = [n(r, campo) for r in righe if r["Data"].startswith(mese) and n(r, campo) is not None]
    return sum(v) / len(v) if v else None

def fmt(x, d=0):
    return "&mdash;" if x is None else (f"{x:.{d}f}".replace(".", ","))

# ---------------------------------------------------------------- documento
doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                        topMargin=15 * mm, bottomMargin=15 * mm,
                        title="Report Salute Massimo Sunzini", author="Knowledge Base Salute")
story = []

story.append(Paragraph("Report di consultazione &mdash; Salute Massimo Sunzini", titolo))
story.append(Paragraph("Generato il 23/08/2026 &middot; Documenti medici e dati sportivi Garmin "
                       "aggiornati al 22/08/2026", sotto))
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=1.2, color=BLU))

# ---------------------------------------------------------------- 1
story.append(Paragraph("1. Cosa dicono i dati oggettivi", h))
story.append(Paragraph(
    "Il tema principale sono i polmoni: c'&egrave; una bronchite cronica ostruttiva importante &mdash; i bronchi "
    "lasciano passare circa il 40% dell'aria che dovrebbero &mdash; e i polmoni trattengono troppa aria; sotto "
    "sforzo l'ossigeno nel sangue scende fino all'87%, e anche di notte resta quasi sempre sotto il 95%: "
    "l'orologio lo conferma mese per mese, con il valore pi&ugrave; basso (92%) fra ottobre e novembre 2025. "
    "Due piccoli noduli polmonari restano sotto controllo con le TAC. Il cuore batte a ritmo regolare, con "
    "qualche battito irregolare sporadico senza allarmi; la misurazione della pressione delle 24 ore &egrave; "
    "<b>non valida per un errore di misurazione</b> e va rifatta. Le analisi del sangue sono nel complesso buone; "
    "da tenere d'occhio colesterolo, omocisteina e indici di allergia. Dall'orologio arrivano tre buone notizie: "
    "<b>circa 7 chili persi in un anno</b>, massa grassa dal 28% al 24,5% e capacit&agrave; di usare ossigeno sotto "
    "sforzo in aumento; il battito a riposo &egrave; rimasto stabile e normale (fra 55 e 70 al minuto).", corpo))

# ---------------------------------------------------------------- 2
story.append(Paragraph("2. Come sta e come rende, secondo le sensazioni e i dati dell'orologio", h))
story.append(Paragraph(
    "Massimo si allena con costanza e si sente bene, e ora abbiamo i numeri che lo confermano: <b>304 uscite "
    "in un anno, quasi 400 ore e circa 4.000 km</b> (soprattutto camminate, bici e canottaggio), con giornate "
    "impegnative come quella del 22 agosto, "
    "con quasi due ore di mountain bike al mattino e oltre un'ora di canottaggio a mezzogiorno. Durante il test "
    "in ospedale aveva riferito solo affanno e stanchezza moderati, con un consumo di ossigeno del tutto normale: "
    "l'orologio racconta la stessa storia, con un battito medio di circa 115 durante l'attivit&agrave; e punte "
    "vicine al suo massimo. In pratica <b>rende molto pi&ugrave; di quanto i valori dei polmoni farebbero prevedere</b>, "
    "perch&eacute; il corpo si &egrave; abituato a lavorare con meno ossigeno. Il rovescio della medaglia resta lo "
    "stesso: sentendo poco i sintomi, potrebbe non accorgersi di un peggioramento. Per questo il battito a riposo "
    "misurato ogni notte &egrave; il campanello d'allarme pi&ugrave; semplice da tenere d'occhio &mdash; e per ora resta "
    "tranquillo. L'unica cosa da chiarire &egrave; la lunga pausa di <b>giugno e luglio 2026</b>: una sola uscita a "
    "giugno e due a luglio, dopo otto mesi filati da 26-36 sedute al mese. &Egrave; un'interruzione netta, non un calo "
    "graduale: vale la pena chiedere a Massimo se sia stata una scelta (caldo, viaggi, impegni) o un periodo in cui "
    "non si sentiva bene.", corpo))

# ---------------------------------------------------------------- 3
story.append(Paragraph("3. Consigli e promemoria", h))
story.append(Paragraph(
    "Le due priorit&agrave;: proteggere i polmoni e rifare la misurazione della pressione. Per i polmoni: usare ogni "
    "giorno l'inalatore prescritto (Trelegy), fare i vaccini consigliati e completare l'esame notturno del respiro "
    "gi&agrave; suggerito dai medici &mdash; l'ossigeno notturno quasi sempre sotto il 95% lo rende ancora pi&ugrave; utile. "
    "Per la pressione: l'esame delle 24 ore va ripetuto prima di trarre conclusioni; nel frattempo misurarla a casa. "
    "Lo sport va continuato con questa regolarit&agrave;, tenendo d'occhio l'ossigeno con il saturimetro; a tavola dieta "
    "mediterranea. Tutti i consigli vanno confermati dai medici curanti.", corpo))
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Cosa fare</b>", puntato))
for x in [
    "Continuare il movimento regolare come sta gi&agrave; facendo (2-3 uscite a settimana), con un saturimetro al dito: rallentare se l'ossigeno scende sotto 88-90%.",
    "Tenere d'occhio il battito a riposo che l'orologio misura ogni notte: se sale sopra 75-80 per pi&ugrave; giorni di fila, avvisare il medico.",
    "Indossare l'orologio anche di notte: &egrave; cos&igrave; che vengono misurati ossigeno, recupero e sonno.",
    "Misurare la pressione a casa mattina e sera e annotarla, in attesa di rifare l'esame delle 24 ore.",
    "Dieta mediterranea: verdure a foglia verde e legumi, pesce, olio d'oliva, poco sale; calcio e vitamina D per le ossa.",
    "Vaccinazioni: antinfluenzale ogni anno, anti-pneumococco e le altre consigliate dallo pneumologo.",
]:
    story.append(Paragraph(x, puntato, bulletText="•"))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>Cosa evitare</b>", puntato))
for x in [
    "Fumo (anche passivo) e ambienti con polveri o aria inquinata; prudenza con l'alta montagna e i voli lunghi senza parere dello pneumologo.",
    "Sforzi molto intensi e prolungati senza controllare l'ossigeno, soprattutto con il caldo (nelle uscite recenti si sono superati i 30 gradi).",
    "Troppo sale e alcol (pressione) e troppi grassi animali (colesterolo).",
    "Integratori o cambi di terapia fai-da-te: ogni modifica va concordata con i medici.",
]:
    story.append(Paragraph(x, puntato, bulletText="•"))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>Da discutere con i medici</b>", puntato))
for x in [
    "Cardiologo: rifare l'esame della pressione delle 24 ore (quello di ottobre 2025 non &egrave; valido) e far rivedere la registrazione del battito.",
    "Pneumologo: mostrare il grafico dell'ossigeno notturno, sceso al 92% fra ottobre e novembre 2025 e rimasto sotto il 95% quasi tutti i mesi.",
    "Medico di base: vitamine del gruppo B (B9, B12, B6) per l'omocisteina alta, con nuovo prelievo dopo circa 3 mesi.",
    "Pneumologo o allergologo: capire perch&eacute; gli indici di allergia (IgE) sono alti.",
    "Esame della densit&agrave; delle ossa (MOC) e vitamina D, per l'indebolimento visto nella radiografia delle mani.",
]:
    story.append(Paragraph(x, puntato, bulletText="•"))
story.append(Spacer(1, 8))

story.append(Paragraph("<b>Promemoria controlli e visite</b>", corpo))
story.append(Spacer(1, 3))
rem = [[Paragraph("Esame / visita", cellahl), Paragraph("Quando", cellahl), Paragraph("Perch&eacute;", cellahl)]]
for r in [
    ("TAC del torace di controllo", "Era prevista a ~6 mesi da gennaio 2026: verificare se gi&agrave; fatta, altrimenti fissarla subito", "Controllo del nodulo di 9 mm al polmone sinistro"),
    ("Visita di Chirurgia Toracica (Osp. S. Andrea)", "Secondo il calendario del centro", "Controllo dell'altro nodulo gi&agrave; in osservazione"),
    ("Esame notturno del respiro (poligrafia con capnografia)", "Da fissare a breve", "Ossigeno notturno sotto il 95% in quasi tutti i mesi"),
    ("Nuovo Holter della pressione (24 ore)", "Appena possibile", "La misurazione di ottobre 2025 non &egrave; valida"),
    ("Visita cardiologica", "Dopo il nuovo Holter della pressione", "Pressione e battiti irregolari su dati affidabili"),
    ("Nuovo esame dell'omocisteina", "Ottobre-novembre 2026", "Era alta (25,1) a luglio 2026"),
    ("Spirometria + visita dallo pneumologo", "Ogni anno, o come indicato", "Tenere sotto controllo i polmoni"),
    ("Analisi del sangue complete + PSA", "Luglio 2027 (una volta l'anno)", "Colesterolo, sangue e prostata"),
    ("Esame della densit&agrave; ossea (MOC)", "Da concordare col medico", "Ossa indebolite alla radiografia delle mani"),
]:
    rem.append([Paragraph(c, cella) for c in r])
t = Table(rem, colWidths=[52 * mm, 63 * mm, 63 * mm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLU),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
    ("GRID", (0, 0), (-1, -1), 0.4, RIGA),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(t)

# ---------------------------------------------------------------- 4. tabella Garmin
story.append(PageBreak())
story.append(Paragraph("4. I dati misurati dall'orologio Garmin, mese per mese", h))
story.append(Paragraph(
    "Ogni riga &egrave; la media del mese. Il trattino significa che in quel mese la misura non &egrave; stata "
    "registrata (accade quando l'orologio non viene indossato di notte). Dal battito a riposo sono stati "
    "esclusi 62 valori fra 95 e 117 che non sono misure reali: comparivano solo nelle notti senza orologio, "
    "ripetuti identici per giorni di fila e alternati a valori normali.", nota))
story.append(Spacer(1, 4))

intest = ["Mese", "Battito a riposo", "Recupero (HRV)", "Ossigeno notte", "Sonno", "Peso",
          "Massa grassa", "VO2max", "Sedute", "Ore attivit&agrave;", "Battito medio in attivit&agrave;"]
tg = [[Paragraph(c, cellah) for c in intest]]
for m in mesi:
    aa = [r for r in att if r["Data"].startswith(m)]
    ore = sum(n(r, "Durata (s)") or 0 for r in aa) / 3600
    fcs = [n(r, "FC media") for r in aa if n(r, "FC media")]
    spo2 = media(m, "SpO2 (%)", ben)
    fcrip = media(m, "FC a riposo", ben)
    riga = [
        Paragraph(f"{MESI_BR[m[5:7]]} {m[2:4]}", cellac),
        Paragraph(fmt(fcrip), cellac), Paragraph(fmt(media(m, "HRV (rMSSD)", ben)), cellac),
        Paragraph(fmt(spo2, 1), cellac), Paragraph(fmt(media(m, "Sonno (ore)", ben), 1), cellac),
        Paragraph(fmt(media(m, "Peso (kg)", ben), 1), cellac),
        Paragraph(fmt(media(m, "Massa grassa (%)", ben), 1), cellac),
        Paragraph(fmt(media(m, "VO2max", ben)), cellac),
        Paragraph(str(len(aa)) if aa else "&mdash;", cellac),
        Paragraph(fmt(ore, 1) if aa else "&mdash;", cellac),
        Paragraph(fmt(sum(fcs) / len(fcs)) if fcs else "&mdash;", cellac),
    ]
    tg.append(riga)
tab = Table(tg, colWidths=[14 * mm] + [17 * mm] * 7 + [13 * mm, 15 * mm, 21 * mm], repeatRows=1)
st = [
    ("BACKGROUND", (0, 0), (-1, 0), BLU),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
    ("GRID", (0, 0), (-1, -1), 0.4, RIGA),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]
# evidenzia in rosso i mesi con battito a riposo elevato
for i, m in enumerate(mesi, start=1):
    v = media(m, "FC a riposo", ben)
    if v and v >= 78:
        st.append(("TEXTCOLOR", (1, i), (1, i), ROSSO))
        st.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))
tab.setStyle(TableStyle(st))
story.append(tab)
story.append(Spacer(1, 3))
story.append(Paragraph(
    "Nessun mese supera la soglia di attenzione di 78 battiti a riposo (verrebbe evidenziato in rosso). "
    "Recupero (HRV) &egrave; la variabilit&agrave; del battito: pi&ugrave; alto significa organismo pi&ugrave; riposato. "
    "VO2max stima quanto ossigeno il corpo riesce a usare sotto sforzo.", nota))

# ---------------------------------------------------------------- 5. grafici
story.append(Paragraph("5. L'andamento nell'ultimo anno", h))
LG, AL = 86 * mm, 52 * mm

def serie(campo, dec=0):
    mm_ = [m for m in mesi if media(m, campo, ben) is not None]
    return mm_, [media(m, campo, ben) for m in mm_], dec

m1, v1, _ = serie("FC a riposo")
m2, v2, _ = serie("SpO2 (%)")
m3, v3, _ = serie("Peso (kg)")
ore_m, ore_v, ore_n = [], [], []
for m in mesi:
    aa = [r for r in att if r["Data"].startswith(m)]
    if aa:
        ore_m.append(m); ore_v.append(sum(n(r, "Durata (s)") or 0 for r in aa) / 3600); ore_n.append(len(aa))

g = [
    [chart.linea(LG, AL, m1, v1, "Battito a riposo",
                 "media mensile - piu' basso = cuore piu' efficiente", evidenzia="max"),
     chart.linea(LG, AL, m2, v2, "Ossigeno nel sangue di notte",
                 "media mensile - sotto 95% e' considerato basso", rif=95,
                 rif_txt="soglia 95%", dec=1, evidenzia="min")],
    [chart.linea(LG, AL, m3, v3, "Peso corporeo", "media mensile", dec=1, evidenzia="min"),
     chart.barre(LG, AL, ore_m, ore_v, ore_n, "Attivita' fisica svolta",
                 "ore al mese (sopra la barra: n. di sedute)")],
]
tg2 = Table(g, colWidths=[LG + 3 * mm, LG + 3 * mm], rowHeights=[AL + 5 * mm, AL + 5 * mm])
tg2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                         ("LEFTPADDING", (0, 0), (-1, -1), 0),
                         ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                         ("TOPPADDING", (0, 0), (-1, -1), 2),
                         ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
story.append(tg2)
story.append(Spacer(1, 3))
story.append(Paragraph(
    "Come leggerli: il battito a riposo resta per tutto l'anno nella fascia normale, con una leggera risalita "
    "da 58 a circa 63-67 nel 2026. L'ossigeno notturno &egrave; il punto debole: resta quasi sempre sotto la soglia "
    "del 95%, con il minimo del 92% fra ottobre e novembre 2025 e un recupero nei mesi successivi. Il peso &egrave; "
    "sceso di circa 7 chili in modo graduale e costante: &egrave; il risultato migliore dell'anno. L'attivit&agrave; "
    "fisica &egrave; stata molto regolare da settembre ad aprile (26-36 uscite al mese), &egrave; calata a maggio, si &egrave; "
    "fermata quasi del tutto a giugno e luglio ed &egrave; ripresa con decisione ad agosto.", nota))

# ---------------------------------------------------------------- 6. fonti
testa6 = [Paragraph("6. Documenti usati per questo report", h),
          Paragraph("Tutti i file si trovano nella cartella Google Drive &ldquo;Salute Massimo Sunzini&rdquo;.", nota),
          Spacer(1, 4)]
inv = [[Paragraph("Documento", cellahl), Paragraph("Data", cellahl), Paragraph("Cosa contiene", cellahl)]]
for r in [
    ("2022.PDF (laboratorio Varelli)", "23/04/2022", "Analisi del sangue e delle urine"),
    ("2024.pdf (laboratorio Varelli)", "02/08/2024", "Analisi del sangue e delle urine"),
    ("2025.pdf (laboratorio Varelli)", "30/09/2025", "Analisi del sangue e delle urine"),
    ("Holter cardiaco e pressorio [pressorio NON VALIDO]", "14-15/10/2025", "Battito 24 ore (valido) + pressione 24 ore (non valida)"),
    ("sunzini Massimo CPET definitivo.pdf (Policlinico Umberto I)", "21/01/2026", "Test da sforzo in bicicletta + esame completo del respiro"),
    ("Aprile 2026.pdf (Lab. Campani)", "18/04/2026", "Emocromo, infiammazione, allergie"),
    ("2026.pdf (laboratorio Varelli)", "22/07/2026", "Analisi del sangue e delle urine"),
    ("fileReferto 2.pdf", "29/07/2026", "Radiografia delle mani"),
    ("Spirometria.numbers", "&mdash;", "Foglio Apple non leggibile: da convertire per essere incluso"),
    ("Dati Garmin &mdash; fogli &ldquo;Attivit&agrave; sportive&rdquo; e &ldquo;Benessere&rdquo; (cartella Dati Garmin)", "23/08/2025 - 22/08/2026", "304 allenamenti (circa 395 ore e 4.000 km) e 366 giorni di misure di salute, letti da intervals.icu"),
]:
    inv.append([Paragraph(c, cella) for c in r])
ti = Table(inv, colWidths=[78 * mm, 26 * mm, 74 * mm], repeatRows=1)
ti.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLU),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
    ("GRID", (0, 0), (-1, -1), 0.4, RIGA),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(KeepTogether(testa6 + [ti]))

story.append(KeepTogether([
    Spacer(1, 10),
    HRFlowable(width="100%", thickness=0.6, color=RIGA),
    Spacer(1, 3),
    Paragraph(
        "Report generato automaticamente dai documenti della cartella Google Drive &ldquo;Salute Massimo Sunzini&rdquo; "
        "e dai dati dei dispositivi Garmin. Non &egrave; un documento medico e non sostituisce il parere dei professionisti "
        "curanti. Sono esclusi due gruppi di dati non attendibili: l'Holter pressorio di ottobre 2025 (errore di "
        "misurazione segnalato) e 62 valori di battito a riposo fra 95 e 117 restituiti dall'orologio nelle notti "
        "in cui non &egrave; stato indossato.", nota),
]))

doc.build(story)
print("OK", OUT)
