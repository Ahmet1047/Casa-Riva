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


def load_part(path):
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"inline_data": {"mime_type": mime, "data": data}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shoe", required=True, nargs="+", help="Neues Schuh-Produktfoto (mehrere = mehr Winkel)")
    ap.add_argument("--reference", default=os.path.join(os.path.dirname(__file__), "reference.png"))
    ap.add_argument("--out", default="ergebnis.png")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = ap.parse_args()

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
            print(f"Gespeichert: {args.out}")
            return
    sys.exit(f"Kein Bild in der Antwort. Roh-Antwort: {json.dumps(data)[:1000]}")


if __name__ == "__main__":
    main()
