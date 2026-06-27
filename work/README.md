# Casa-Riva Schuh-Show Generator (Nano Banana)

Erzeugt TikTok-Produktbilder von Schuhen im festen Casa-Riva-Look:
Vintage-Teppich, ein Schuh top-down + einer von der Seite, 9:16.
Nur der Schuh wird getauscht, die Szene bleibt gleich.

## Nutzung
```bash
export GEMINI_API_KEY=AIza...      # Google AI Studio Key
python3 nano_banana.py --shoe schuh.jpg --out ergebnis.png
```

- `reference.png` = feste Vorlage (Teppich + Anordnung)
- Modell: `gemini-2.5-flash-image` (Nano Banana) via REST-API
- Abhängigkeiten: `requests`, `pillow`
