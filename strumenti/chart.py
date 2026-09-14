# -*- coding: utf-8 -*-
"""Grafici vettoriali nativi reportlab: compatti (pochi KB) e nitidi.
Palette validata dataviz: serie #2a78d6, riferimento #e34948."""
from reportlab.graphics.shapes import Drawing, Line, PolyLine, Circle, String, Rect, Group
from reportlab.lib import colors
from reportlab.lib.units import mm

SERIE = colors.HexColor("#2a78d6")
RIF = colors.HexColor("#e34948")
INK = colors.HexColor("#0b0b0b")
INK2 = colors.HexColor("#52514e")
GRID = colors.HexColor("#dcdcd8")

MESI_IT = {"01": "G", "02": "F", "03": "M", "04": "A", "05": "M", "06": "G",
           "07": "L", "08": "A", "09": "S", "10": "O", "11": "N", "12": "D"}


def _cornice(d, x0, y0, w, hh, vmin, vmax, tick_vals, mesi, titolo, sottotit, dec=0):
    """Assi, griglia orizzontale, etichette. Restituisce la funzione di mappatura y."""
    d.add(String(0, hh + y0 + 20, titolo, fontName="Helvetica-Bold", fontSize=8.6, fillColor=INK))
    d.add(String(0, hh + y0 + 10, sottotit, fontName="Helvetica", fontSize=6.4, fillColor=INK2))

    def sy(v):
        return y0 + (v - vmin) / (vmax - vmin) * hh

    for tv in tick_vals:
        y = sy(tv)
        d.add(Line(x0, y, x0 + w, y, strokeColor=GRID, strokeWidth=0.5))
        d.add(String(x0 - 3, y - 2.2, f"{tv:.{dec}f}".replace(".", ","),
                     fontName="Helvetica", fontSize=6, fillColor=INK2, textAnchor="end"))
    d.add(Line(x0, y0, x0, y0 + hh, strokeColor=GRID, strokeWidth=0.7))
    passo = w / max(len(mesi) - 1, 1)
    for i, m in enumerate(mesi):
        xx = x0 + i * passo
        d.add(String(xx, y0 - 8, MESI_IT[m[5:7]], fontName="Helvetica", fontSize=5.8,
                     fillColor=INK2, textAnchor="middle"))
        if m[5:7] == "01" or i == 0:
            d.add(String(xx, y0 - 15, m[:4], fontName="Helvetica-Bold", fontSize=5.6,
                         fillColor=INK2, textAnchor="middle"))
    return sy, passo


def _scala(vals, pad=0.22, n=4):
    lo, hi = min(vals), max(vals)
    marg = (hi - lo) * pad or 1
    vmin, vmax = lo - marg, hi + marg
    step = (vmax - vmin) / (n - 1)
    return vmin, vmax, [vmin + i * step for i in range(n)]


def linea(larg, alt, mesi, vals, titolo, sottotit, rif=None, rif_txt="", dec=0, evidenzia="max"):
    d = Drawing(larg, alt)
    x0, y0 = 24, 20
    w, hh = larg - x0 - 8, alt - y0 - 30
    tutti = list(vals) + ([rif] if rif is not None else [])
    vmin, vmax, ticks = _scala(tutti)
    sy, passo = _cornice(d, x0, y0, w, hh, vmin, vmax, ticks, mesi, titolo, sottotit, dec)

    if rif is not None:
        y = sy(rif)
        d.add(Line(x0, y, x0 + w, y, strokeColor=RIF, strokeWidth=1, strokeDashArray=[3, 2]))
        d.add(String(x0 + w * 0.5, y + 2.5, rif_txt, fontName="Helvetica-Bold", fontSize=5.8,
                     fillColor=RIF, textAnchor="middle"))

    punti = []
    for i, v in enumerate(vals):
        punti += [x0 + i * passo, sy(v)]
    d.add(PolyLine(punti, strokeColor=SERIE, strokeWidth=1.6,
                   strokeLineJoin=1, strokeLineCap=1))
    idx_ev = vals.index(max(vals)) if evidenzia == "max" else vals.index(min(vals))
    for i, v in enumerate(vals):
        xx, yy = x0 + i * passo, sy(v)
        d.add(Circle(xx, yy, 1.8, fillColor=SERIE, strokeColor=colors.white, strokeWidth=0.6))
        if i in (0, len(vals) - 1, idx_ev):
            d.add(String(xx, yy + 5, f"{v:.{dec}f}".replace(".", ","), fontName="Helvetica-Bold",
                         fontSize=6.3, fillColor=INK, textAnchor="middle"))
    return d


def barre(larg, alt, mesi, vals, etich, titolo, sottotit):
    d = Drawing(larg, alt)
    x0, y0 = 24, 20
    w, hh = larg - x0 - 8, alt - y0 - 30
    vmax = max(vals) * 1.18
    ticks = [vmax * i / 3 for i in range(4)]
    sy, passo = _cornice(d, x0, y0, w, hh, 0, vmax, ticks, mesi, titolo, sottotit, 0)
    bw = passo * 0.55
    for i, v in enumerate(vals):
        xx = x0 + i * passo
        h = sy(v) - y0
        d.add(Rect(xx - bw / 2, y0, bw, max(h, 0.4), fillColor=SERIE, strokeColor=None))
        d.add(String(xx, y0 + h + 2.5, str(etich[i]), fontName="Helvetica", fontSize=5.8,
                     fillColor=INK2, textAnchor="middle"))
    return d
