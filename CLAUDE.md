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
- Generator: `work/nano_banana.py` (Modi: `--mode swap` = neue Show/Produkt,
  `--mode recolor` = nur Farbe/Material tauschen).
- Modell-Prompts: `work/prompts/*.txt` (pro Modell eine Datei).
- Szenen-Anker: `work/reference.png` (Vintage-Teppich + Anordnung).

## Die wichtigsten Regeln in einem Satz
Eine eingefrorene Szene + EINE neue Variable; Produkt exakt reproduzieren statt
verschönern; Feature-by-Feature beschreiben; nicht cinematic; Schuh immer scharf;
beide Schuhe exakt gleich groß; Negatives mit Position benennen (z. B. **kein
Stern unten rechts**). Details: `work/KNOWLEDGE_BASE.md`.

## Git
Auf dem aktuellen Feature-Branch entwickeln, committen und pushen. Keinen PR
erstellen, außer ich bitte explizit darum.
