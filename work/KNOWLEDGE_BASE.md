# Casa-Riva Bild-Knowledge-Base

Zentrale Sammlung aller Erkenntnisse, um mit **Nano Banana / Gemini Image**
zuverlässig gute Casa-Riva-Schuh-Shows zu erzeugen. Diese Datei ist die Single
Source of Truth für Prompts und Workflow. Bei neuen Lerneffekten: hier ergänzen,
nicht im Code verstreuen.

## Provider: fal.ai (Standard)
Bildgenerierung läuft über **fal.ai** (Modell `fal-ai/nano-banana/edit`, Gemini
Image mit mehreren Referenzbildern). Key kommt aus `FAL_KEY`.
- Script: `work/fal_banana.py` (gleicher Look, gleiche Modi wie unten).
- GitHub Actions: `.github/workflows/generate-shoes.yml` nutzt das Repo-Secret
  `FAL_KEY` und lädt die Bilder als Artifact hoch.
- Direkter Google-API-Weg (`work/nano_banana.py`, `GEMINI_API_KEY`) bleibt als
  Alternative bestehen.

**Wichtig:** Ein GitHub-Secret ist nur im Actions-Lauf verfügbar, NICHT in einer
Claude-Code-Web-Session. Für lokale Generierung muss `FAL_KEY` als Env-Variable
in der jeweiligen Umgebung gesetzt sein.

---

## 1. Was wir bauen

TikTok-Schuh-Shows im **festen Casa-Riva-Look** (9:16):

- Untergrund: ein **verblasster Vintage-Perser-/Orientteppich**, füllt das Bild.
- Anordnung: **zwei identische Schuhe** desselben Modells nebeneinander, mit Lücke.
  - **Linker Schuh:** flach auf der Sohle, **Top-down** (direkt von oben).
  - **Rechter Schuh:** auf der Außenseite liegend, **Seitenprofil**.
- Beide Schuhe **exakt gleich groß** und **gleiche Blickrichtung**.
- Licht: weiches, gleichmäßiges Tageslicht von oben, realistische Kontaktschatten.
- Look: **matt, gedämpfte natürliche Farben, NICHT cinematic, nicht Studio.**

Es gibt **zwei Aufgaben-Typen**:

| Typ | Was passiert | Modus im Skript |
|-----|--------------|-----------------|
| **Show / Product Creation** | Neues Schuhmodell zum ersten Mal in die Szene setzen | `--mode swap` (Standard) |
| **Recolor / Variante** | Fertige korrekte Show nehmen, nur Farbe/Material tauschen | `--mode recolor` |

---

## 2. Die 7 Kern-Prinzipien für gute Bilder

Diese Regeln sind aus den funktionierenden Prompts (`prompts/*.txt`) destilliert.
Jede neue Generierung sollte sie erfüllen.

### P1 — Verketten statt stapeln (eine eingefrorene Szene + EINE Variable)
Das **erste Bild ist der eingefrorene Szenen-Anker** (Teppich, Layout, Licht),
das zweite Bild ist die **einzige neue Variable** (der Schuh bzw. die Farbe).
Nie mehrere Dinge gleichzeitig ändern.
> „The FIRST image is a fixed scene template. The SECOND image is the new product."

### P2 — Produkt exakt reproduzieren, NICHT verschönern
Das Modell soll das Produkt studieren und 1:1 nachbauen, nicht idealisieren.
> „study … exactly reproduce … **Do not idealize, beautify, average or restyle.**"

### P3 — Produkt Feature-by-Feature beschreiben
Statt „weißer Sneaker" → jedes Detail einzeln: Obermaterial, Farbblöcke,
Sohlenform (z. B. „scalloped / zigzag"), Schnürsenkel, Ösen, Zehenkappe,
Fersenkappe, Logos. Je präziser, desto wiedererkennbarer das Produkt.

### P4 — Anti-Cinematic / Anti-Halluzination
**Keine Qualitäts-Buzzwords** („cinematic", „8k", „professional photography"
mit Studio-Konnotation). Die ziehen Studio-Look + Artefakte rein.
> „Muted, natural, restrained colors. … not cinematic. No film grain, no color grading."

### P5 — Produkt ist der Star (Modus B)
Der Schuh bleibt **immer scharf und im Fokus**. Unschärfe oder Imperfektion
gehört **nur** auf Hintergrund/Licht — **nie** auf den Schuh.

### P6 — Negatives konkret und mit Position benennen
Nano Banana halluziniert gern Symbole/Sterne, besonders unten rechts.
Explizit verbieten:
> „NO star, NO colorful star or sparkle, NO emblem … — **especially NOT in the bottom-right corner**."
Ebenso: kein Schuhkarton, keine Hände, kein Text, kein Logo, kein Wasserzeichen.

### P7 — Konsistenz der zwei Schuhe erzwingen
Explizit wiederholen, sonst werden die zwei Schuhe ungleich gerendert:
> „BOTH shoes EXACTLY THE SAME SIZE … BOTH pointing in the SAME direction."

### P8 — Geometrie-/Identitäts-Lock (kein Warping, EIN Modell)
Häufigster Fehler: die zwei Schuhe **warpen** (verzogene Geometrie) oder werden
zu **zwei verschiedenen Schuhen**. Beide sind aber **ein einziges identisches
Modell aus zwei Blickwinkeln**. Immer erzwingen:
> „Both shoes are ONE single identical model … preserve the exact geometry …
> do NOT warp, stretch, melt, deform or redraw them, do NOT make two different shoes."

**Stärkstes Gegenmittel — Zwei-Ansichten-Referenz:** Wenn vorhanden, **beide
echten Ansichten** des Schuhs mitgeben (Top-down **und** Seitenprofil). Dann
bekommt jede Position ihre korrekte Geometrie:
- 1. Bild = Szenen-Anker (Teppich/Layout/Licht/9:16),
- 2. Bild = Schuh **top-down** → wird der linke Schuh,
- 3. Bild = Schuh **Seitenprofil** → wird der rechte Schuh.
Damit verschwinden Warping und „zwei verschiedene Schuhe" zuverlässig (so wurde
die Navy-Show korrekt erzeugt). Aufruf-Beispiel siehe Abschnitt 5.

---

## 3. Prompt-Bauplan (Schema)

Ein guter **Show-/Creation-Prompt** hat immer diese Blöcke in dieser Reihenfolge:

1. **Anker + Produkt-Referenz benennen** — „Place the [Modell] from the first
   reference image … on the rug from the LAST reference image."
2. **Produkt Feature-by-Feature** (P3) — Material, Farben, Sohle, Details.
3. **Anordnung exakt** (P7) — gleiche Größe, gleiche Richtung, links top-down /
   rechts Seitenprofil, Lücke dazwischen.
4. **Licht & Look** (P4/P5) — weiches Tageslicht von oben, matt, gedämpft,
   nicht cinematic, scharf im Fokus.
5. **Negatives** (P6) — keine Sterne/Symbole (v. a. unten rechts), kein Karton,
   keine Hände, kein Text/Logo/Watermark; Teppich füllt das Bild.
6. **Output** — „Photorealistic editorial product photography, shot from
   directly above, no people. Vertical 9:16 framing."

Ein guter **Recolor-Prompt** ändert das Schema:

1. **Erstes Bild = fertige korrekte Szene** — Komposition/Layout/Teppich/Licht/
   Schatten/Form/Größe/Position/Richtung/9:16 **exakt behalten**.
2. **Zweites Bild = Farb-/Material-Referenz** — „Change ONLY the [Teil]" und
   benennen, **was unverändert bleibt** (z. B. weiße Sohle, weiße Zehenkappe).
3. Look + Negatives + Output wie oben.

---

## 4. Wiederverwendbare Bausteine (copy-paste)

**Anordnungs-Block:**
```
Match this exact arrangement: the two shoes side by side with a clear gap between
them, BOTH shoes EXACTLY THE SAME SIZE and scale (do not make one larger than the
other), and BOTH pointing in the SAME direction.
- The LEFT shoe lies flat on its sole, seen from directly above (top-down).
- The RIGHT shoe rests on its outer side, showing the full side profile.
```

**Look-Block:**
```
Soft even natural top-down light, realistic contact shadows. Matte texture, the
shoe sharp and clearly in focus, muted natural restrained colors, not cinematic,
not staged, not a studio shoot.
```

**Negativ-Block:**
```
ONLY the two identical shoes on the rug — no shoebox, no other objects, no text,
no logos, no watermark, no hands, and NO star, NO colorful star or sparkle, NO
emblem or symbol anywhere — especially NOT in the bottom-right corner. The rug is
plain patterned vintage rug only and fills the frame.
```

**Output-Block:**
```
Photorealistic editorial product photography, shot from directly above, no people.
Vertical 9:16 framing.
```

---

## 5. Empfohlener Workflow (für stabile Serien)

1. **Basis-Show pro Modell** mit Feature-Prompt erzeugen:
   ```bash
   python3 nano_banana.py --shoe schuh.jpg \
     --prompt-file prompts/<modell>.txt --out output/<modell>.png
   ```
2. **Qualität prüfen** gegen die 7 Prinzipien (besonders P6: kein Stern unten rechts,
   P7: beide Schuhe gleich groß). Wenn nicht ok → Prompt-Detail schärfen, neu rendern.
3. **Farbvarianten** aus der korrekten Basis ableiten (Form bleibt 100 % stabil):
   ```bash
   python3 nano_banana.py --mode recolor \
     --reference output/<modell>.png --shoe varianten/<farbe>.jpg \
     --prompt-file prompts/<modell>_<farbe>.txt --out output/<modell>_<farbe>.png
   ```
4. Für jedes neue Modell eine **eigene Prompt-Datei** unter `prompts/` anlegen
   (siehe `num_base.txt`, `valentino.txt` als Vorlagen).

**Bei Warping / zwei verschiedenen Schuhen → recolor + Zwei-Ansichten (P8/P9):**
**Immer `--mode recolor`** verwenden — der friert die exakte Anordnung des
Anker-Bildes ein. Beide echten Ansichten (Top-down + Seite) nur als **Farb-/
Material-Referenz** mitgeben, plus expliziten Anordnungs-Satz im Prompt:
```bash
python3 nano_banana.py --mode recolor \
  --reference inputs/scene_rug.png \
  --shoe inputs/<modell>_top.jpeg inputs/<modell>_side.jpeg \
  --out output/<modell>.png
```
> **Wichtig (P9): `--mode swap` NICHT für Anordnungstreue benutzen.** Swap
> komponiert die Szene frei neu und zieht die Schuhe oft diagonal auseinander.
> Für „exakt wie das Referenzbild" ist recolor Pflicht; die zwei Ansichten lösen
> Warping/Identität, der eingefrorene Anker löst die Platzierung.

### Technik-Defaults (Zuverlässigkeit)
- Modell: `gemini-2.5-flash-image` (Nano Banana). Schärfer: `--model gemini-3-pro-image`.
- Format wird über `imageConfig.aspectRatio: "9:16"` erzwungen (mit Auto-Fallback
  für ältere Modelle).
- Bilder kommen über **Datei-Pfad oder URL** rein (`--shoe "https://…"`),
  nicht über in den Chat geklebte Bilder.
- Jede Generierung schreibt zusätzlich eine kleine `.jpg`-Preview zum Teilen.

---

## 6. Häufige Fehler → Gegenmittel

| Problem | Ursache | Fix |
|---------|---------|-----|
| Bunter Stern / Symbol unten rechts | Nano-Banana-Tic | Negativ-Block mit „especially NOT in the bottom-right corner" (P6) |
| Die zwei Schuhe unterschiedlich groß | fehlende Constraint | „EXACTLY THE SAME SIZE … SAME direction" wiederholen (P7) |
| Schuh sieht generisch / falsch aus | zu vage beschrieben | Feature-by-Feature schärfen (P3), „do not idealize" (P2) |
| Bild wirkt wie Studio/Werbung | Quality-Buzzwords | Anti-Cinematic-Wording, gedämpfte Farben (P4) |
| Recolor ändert auch die Form | Anker nicht eingefroren | Im Recolor-Prompt „Change ONLY …" + behaltene Teile listen |
| Form/Layout instabil über Varianten | aus Produktfoto statt Basis gerendert | Varianten immer per `--mode recolor` aus korrekter Basis |
| Schuhe **warpen** / verzogene Geometrie | Recolor zeichnet Schuh neu | Geometrie-Lock (P8): „preserve exact geometry, do not warp/redraw" |
| **Zwei verschiedene Schuhe** statt einem Modell | nur eine Ansicht als Referenz | Zwei-Ansichten-Swap (P8): Top-down **und** Seite mitgeben |
| Nur EIN Schuh wird umgefärbt | „BOTH" fehlt | explizit „recolor BOTH shoes … both to <Farbe>" |
| Schuhe **falsch angeordnet** / diagonal auseinandergezogen | `swap` komponiert frei | **`--mode recolor`** nutzen (friert Anker-Anordnung ein) + Platzierungs-Satz (P9) |

---

## 7. Arbeitsregel (immer)

**Nach jeder Generierung den Output analysieren**, gegen die Prinzipien P1–P8
prüfen, und bei Abweichungen **die Prompt-Architektur (Skripte/Prompts), diese
Knowledge Base UND `CLAUDE.md` verbessern** — nicht nur das Einzelbild neu
würfeln. So werden die Prompts mit jeder Iteration besser statt den gleichen
Fehler zu wiederholen.
