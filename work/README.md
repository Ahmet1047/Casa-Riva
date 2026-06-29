# Casa-Riva Schuh-Show Generator (Nano Banana / Gemini 2.5 Flash Image)

Erzeugt TikTok-Schuh-Shows (9:16) im festen Casa-Riva-Look: Vintage-Teppich,
ein Schuh top-down + einer von der Seite. Nur der Schuh wird getauscht, die
Szene bleibt identisch.

> **Für gute Bilder zuerst die [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) lesen** –
> sie enthält die 7 Kern-Prinzipien, den Prompt-Bauplan und den Workflow.

## Setup
```bash
export GEMINI_API_KEY="AIza..."   # Google AI Studio Key (Generative Language API)
```
Abhängigkeiten: `requests`, `pillow`. Vorlage: `reference.png`.

## Nutzung

**Neuen Schuh in die Szene setzen (Standard):**
```bash
python3 nano_banana.py --shoe pfad/zum/schuh.jpg --out output/show.png
# Schuhfoto kann auch eine URL sein:
python3 nano_banana.py --shoe "https://shop.de/sneaker.jpg" --out output/show.png
```

**Nur umfärben (Form einer bereits korrekten Show behalten):**
```bash
python3 nano_banana.py --mode recolor \
  --reference output/show_schwarz.png \
  --shoe sneakers/grau.jpg \
  --out output/show_grau.png
```

Optionen: `--model gemini-3-pro-image` (schärfere Details), `--prompt "..."`.

## Bilder reinbekommen (ohne ZIP)
Inline in den Chat **eingefügte** Bilder werden nicht als Datei gespeichert und
können nicht verarbeitet werden. Funktioniert:
- **Bild-URL / Produkt-Link** -> `--shoe "<url>"` lädt direkt herunter (bequemster Weg).
- Datei-Anhang (Büroklammer) oder ZIP -> landet als echte Datei.

## Output zu groß für den Chat?
Jede Generierung schreibt zusätzlich eine komprimierte `.jpg` (max 1280px, ~300 KB)
neben die PNG. Die JPG zum Teilen nutzen; fertige Bilder nie unnötig erneut laden.
