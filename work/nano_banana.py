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

MODEL = "gemini-2.5-flash-image"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

DEFAULT_PROMPT = (
    "Use the FIRST image as a fixed scene template and the SECOND image as the new product. "
    "Recreate the first image EXACTLY: the same vintage Persian/Oriental rug, the same colors, "
    "the same soft top-down studio lighting, the same vertical 9:16 framing, and the same composition "
    "of two shoes -- one shoe photographed from directly above (top-down) on the left, and the other "
    "shoe shown from the side on the right. "
    "Replace ONLY the shoes with the shoe shown in the second image. Keep the new shoe's exact design, "
    "materials, colors, logos and proportions faithful to the product photo. "
    "Do not change the rug, background, lighting, camera angle or layout. Photorealistic, high detail, "
    "clean e-commerce / TikTok product-show look. Output a single 9:16 vertical image."
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
    ap.add_argument("--shoe", required=True, help="Neues Schuh-Produktfoto")
    ap.add_argument("--reference", default=os.path.join(os.path.dirname(__file__), "reference.png"))
    ap.add_argument("--out", default="ergebnis.png")
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("Fehler: GEMINI_API_KEY (oder GOOGLE_API_KEY) ist nicht gesetzt.")

    body = {
        "contents": [{
            "parts": [
                {"text": args.prompt},
                load_part(args.reference),
                load_part(args.shoe),
            ]
        }],
        # 9:16 hochformat fuer TikTok
        "generationConfig": {"imageConfig": {"aspectRatio": "9:16"}},
    }

    resp = requests.post(
        ENDPOINT,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=180,
    )
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
