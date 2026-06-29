#!/usr/bin/env python3
"""
Casa-Riva Schuh-Show Generator (Nano Banana / Gemini 2.5 Flash Image)

Nimmt ein Referenzbild (Teppich + Anordnung) und ein neues Schuh-Produktfoto
und erzeugt ein Bild im exakt gleichen Stil -- nur der Schuh wird getauscht.

Aufruf:
    GEMINI_API_KEY=... python3 nano_banana.py --shoe schuh.jpg --out ergebnis.png
"""
import argparse
import base64
import json
import mimetypes
import os
import sys

import requests

DEFAULT_MODEL = "gemini-2.5-flash-image"  # = Nano Banana; alt: gemini-3-pro-image (Nano Banana 2)

# Prompt nach dem Casa-Riva Prompt-Engineering-Guide:
# - Verketten statt stapeln: 1. Bild = eingefrorener Szenen-Anker, nur EINE neue Variable (der Schuh)
# - "study ... do not idealize/beautify/average" -> Produkt exakt reproduzieren
# - Anti-Cinematic: keine Quality-Woerter; muted natural colors
# - Modus B (Produkt ist der Star): Schuh immer scharf & sauber ausgeleuchtet,
#   Imperfektionen NUR auf Licht/Hintergrund, NIEMALS auf den Schuh
DEFAULT_PROMPT = (
    "The FIRST image is a fixed scene template. The SECOND image is the new product (a shoe). "
    "Carefully study the second image before generating. Analyze and exactly reproduce the shoe's "
    "specific design: the precise colors and color blocking, the materials and textures (leather, "
    "suede, mesh, rubber), the sole shape and color, the stitching, the laces, and any logos, "
    "branding or details. Do not idealize, beautify, average or restyle the shoe -- it must be "
    "recognizable as the exact same product from the reference. "
    "Recreate the first image exactly: keep the identical vintage Persian/Oriental rug, the same "
    "rug colors and pattern, the same soft even top-down daylight, the same vertical 9:16 framing, "
    "and the same layout of two shoes -- one shoe seen from directly above (top-down) on the upper "
    "left, the other shoe shown from the side, heel toward upper-right. "
    "Replace ONLY the shoes with the shoe from the second image; both shown shoes are this same model. "
    "Do not change the rug, background, camera angle, shadows or composition. "
    "The shoe stays sharp and clearly in focus, materials and details crisp, well-lit and flattering, "
    "colors true to the product. Any softness or imperfection belongs only to the background, never "
    "to the shoe. "
    "Muted, natural, restrained colors. An ordinary clean product photo, not staged, not a studio "
    "shoot, not cinematic. No film grain, no color grading, no text, no watermark. "
    "Output a single vertical 9:16 image."
)

# Recolor-Modus: 1. Bild = bereits korrekte Szene+Schuhform, 2. Bild = Farb-/Material-Referenz.
# Nur Farbe/Material wird getauscht, die Form bleibt exakt erhalten.
RECOLOR_PROMPT = (
    "The FIRST image is a finished, correct scene: two identical sneakers on a vintage rug, one shown "
    "top-down and one from the side. Keep its composition, layout, rug, lighting, shadows, shoe SHAPE "
    "and proportions, and 9:16 framing exactly as they are -- do not change the shape or arrangement. "
    "The SECOND image is a color/material reference. Carefully study it and recolor BOTH sneakers in "
    "the first image to exactly match that shoe: the same suede upper color and texture, the same sole "
    "color, the same laces, toe cap and details. Change ONLY the colors and materials, nothing about "
    "the shape, pose or scene. "
    "The shoe stays sharp and in focus, materials crisp, well-lit, colors true to the reference. "
    "Plain insole with NO text and NO logo. Muted natural colors, not cinematic, no watermark, no text. "
    "Output a single vertical 9:16 image."
)


def load_part(path):
    # URL oder lokaler Pfad -> beides wird unterstuetzt
    if path.startswith("http://") or path.startswith("https://"):
        r = requests.get(path, timeout=60)
        r.raise_for_status()
        raw = r.content
        mime = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
    else:
        mime, _ = mimetypes.guess_type(path)
        mime = mime or "image/png"
        with open(path, "rb") as f:
            raw = f.read()
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(raw).decode()}}


def make_preview(png_path):
    """Leichte JPG-Variante fuer den Versand (kleiner, gleiche Optik)."""
    from PIL import Image
    im = Image.open(png_path).convert("RGB")
    im.thumbnail((1280, 1280))
    jpg = os.path.splitext(png_path)[0] + ".jpg"
    im.save(jpg, "JPEG", quality=85, optimize=True)
    return jpg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shoe", required=True, nargs="+", help="Neues Schuh-Produktfoto (mehrere = mehr Winkel)")
    ap.add_argument("--reference", default=os.path.join(os.path.dirname(__file__), "reference.png"))
    ap.add_argument("--out", default="ergebnis.png")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mode", choices=["swap", "recolor"], default="swap",
                    help="swap = neuen Schuh in die Szene; recolor = Form behalten, nur umfaerben")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--prompt-file", dest="prompt_file", default=None,
                    help="Pfad zu einer Datei mit dem vollstaendigen Prompt (ueberschreibt --prompt)")
    ap.add_argument("--details", default=None,
                    help="Zusatztext, der an den Basis-Prompt angehaengt wird (schuh-spezifische Details)")
    args = ap.parse_args()
    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            args.prompt = f.read()
    elif args.prompt is None:
        args.prompt = RECOLOR_PROMPT if args.mode == "recolor" else DEFAULT_PROMPT
    if args.details:
        args.prompt = args.prompt + "\n\n" + args.details

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("Fehler: GEMINI_API_KEY (oder GOOGLE_API_KEY) ist nicht gesetzt.")

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{args.model}:generateContent"
    parts = [{"text": args.prompt}, load_part(args.reference)]
    for shoe in args.shoe:
        parts.append(load_part(shoe))
    body = {
        "contents": [{"parts": parts}],
        # 9:16 hochformat fuer TikTok
        "generationConfig": {"imageConfig": {"aspectRatio": "9:16"}},
    }

    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    resp = requests.post(endpoint, headers=headers, data=json.dumps(body), timeout=180)
    # Fallback: aeltere Modelle kennen imageConfig nicht
    if resp.status_code == 400 and "imageConfig" in resp.text:
        body["generationConfig"].pop("imageConfig", None)
        resp = requests.post(endpoint, headers=headers, data=json.dumps(body), timeout=180)
    if resp.status_code != 200:
        sys.exit(f"API-Fehler {resp.status_code}: {resp.text[:1000]}")

    data = resp.json()
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            with open(args.out, "wb") as f:
                f.write(base64.b64decode(inline["data"]))
            jpg = make_preview(args.out)
            print(f"Gespeichert: {args.out}")
            print(f"Preview (klein): {jpg}")
            return
    sys.exit(f"Kein Bild in der Antwort. Roh-Antwort: {json.dumps(data)[:1000]}")


if __name__ == "__main__":
    main()
