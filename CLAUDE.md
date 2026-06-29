# Casa-Riva — Projekt-Kontext für Claude

Dieses Repo erzeugt **TikTok-Schuh-Shows (9:16)** im festen Casa-Riva-Look mit
**Nano Banana / Gemini Image** (Google Generative Language API).

## WICHTIG: Zuerst die Knowledge Base lesen
Bevor du Bilder erzeugst oder Prompts schreibst/änderst, **lies und befolge**:

> **[`work/KNOWLEDGE_BASE.md`](work/KNOWLEDGE_BASE.md)** — Single Source of Truth
> (7 Kern-Prinzipien, Prompt-Bauplan, wiederverwendbare Blöcke, Workflow,
> Fehler→Gegenmittel-Tabelle).

Neue Erkenntnisse über gute Bilder **immer in `work/KNOWLEDGE_BASE.md` ergänzen**,
nicht im Code oder hier verstreuen.

## Schnell-Orientierung
- **Provider: fal.ai** (Standard). Generator `work/fal_banana.py`, Key aus `FAL_KEY`.
  GitHub-Workflow: `.github/workflows/generate-shoes.yml` (nutzt Secret `FAL_KEY`).
- Alternative: `work/nano_banana.py` (direkte Google-API, `GEMINI_API_KEY`).
- Modi bei beiden: `--mode swap` = neue Show/Produkt, `--mode recolor` =
  nur Farbe/Material tauschen.
- Eingabebilder: `work/inputs/` (Szenen-Anker `scene_rug.png` + Schuh-Referenzen).
- Modell-Prompts: `work/prompts/*.txt` (pro Modell eine Datei).
- Szenen-Anker: `work/reference.png` (Vintage-Teppich + Anordnung).

## Die wichtigsten Regeln in einem Satz
Eine eingefrorene Szene + EINE neue Variable; Produkt exakt reproduzieren statt
verschönern; Feature-by-Feature beschreiben; nicht cinematic; Schuh immer scharf;
beide Schuhe exakt gleich groß **und ein identisches Modell (kein Warping, keine
zwei verschiedenen Schuhe)**; Negatives mit Position benennen (z. B. **kein
Stern unten rechts**). Details: `work/KNOWLEDGE_BASE.md`.

## Arbeitsregel: immer aus dem Output lernen
Nach **jeder** Bildgenerierung den Output analysieren, gegen die Prinzipien
P1–P8 prüfen und bei Fehlern **die Prompt-Architektur, `work/KNOWLEDGE_BASE.md`
und diese Datei verbessern** — nicht nur das Bild neu würfeln. Bei Warping oder
„zwei verschiedene Schuhe": beide echten Ansichten (Top-down **und** Seite) als
Referenz mitgeben (Zwei-Ansichten-Swap, P8).

## Git
Auf dem aktuellen Feature-Branch entwickeln, committen und pushen. Keinen PR
erstellen, außer ich bitte explizit darum.
