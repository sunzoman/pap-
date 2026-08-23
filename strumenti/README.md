# Strumenti della knowledge base

Script usati dalla scansione e dalla generazione del report. Le regole operative
stanno in `../CLAUDE.md`; qui c'è solo il codice.

| File | Cosa fa |
|---|---|
| `costruisci_csv.py` | Trasforma i JSON grezzi di intervals.icu nei due CSV in `dati/garmin/`. Applica il filtro di plausibilità sulla FC a riposo (esclude i valori ≥ 95 bpm, che non sono misure). |
| `chart.py` | Grafici vettoriali nativi reportlab (linea e barre). Compatti: tengono il PDF sotto i 20 KB. |
| `genera_report.py` | Costruisce il PDF del report nella struttura definita dall'utente. |

## Come si usa

```bash
# 1. scaricare i dati (le credenziali stanno SOLO sul file Drive, mai qui)
curl -s -u "API_KEY:<chiave>" \
  "https://intervals.icu/api/v1/athlete/i685995/activities?oldest=2015-01-01&newest=<oggi>" -o acts_raw.json
curl -s -u "API_KEY:<chiave>" \
  "https://intervals.icu/api/v1/athlete/i685995/wellness?oldest=2025-08-22&newest=<oggi>" -o well_raw.json

# 2. rigenerare i CSV
JSON_DIR=. python3 strumenti/costruisci_csv.py

# 3. generare il PDF
python3 strumenti/genera_report.py 2026-08-23 /tmp/report.pdf

# 4. controllare a occhio il risultato prima di pubblicarlo
python3 -c "import pypdfium2 as p; d=p.PdfDocument('/tmp/report.pdf'); [d[i].render(scale=1.4).to_pil().save(f'pg{i+1}.png') for i in range(len(d))]"
```

Usare `curl`: `urllib` di Python non attraversa il proxy dell'ambiente e riceve 403.
