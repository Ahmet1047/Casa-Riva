#!/usr/bin/env python3
"""
Casa-Riva Schuh-Show Generator über fal.ai (Nano Banana / Gemini Image Edit).

Gleicher Casa-Riva-Look wie nano_banana.py, aber der Bild-Aufruf läuft über
fal.ai statt direkt über die Google-API. Der Key kommt aus FAL_KEY
(z. B. als GitHub-Secret oder Environment-Variable).

Aufruf:
    FAL_KEY=...  python3 fal_banana.py \
        --scene inputs/scene_rug.png \
        --shoe inputs/shoe_navy.jpeg \
        --out output/navy.png

--scene = eingefrorener Szenen-Anker (Teppich + Anordnung, 1. Bild)
--shoe  = neue Variable (Schuh-Farb-/Material-Referenz, 2. Bild); mehrfach erlaubt
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time

import requests

# fal.ai Nano-Banana Edit-Endpoint (Gemini Image, mehrere Referenzbilder).
# Sync-Endpoint wartet auf das Ergebnis; bei 202 wird via queue gepollt.
FAL_MODEL = "fal-ai/nano-banana/edit"
SYNC_URL = f"https://fal.run/{FAL_MODEL}"

# Recolor: 1. Bild = fertige korrekte Szene (Schuhe schon auf dem Teppich),
# 2. Bild = Farb-/Material-Referenz. Nur Farbe/Material wird getauscht.
RECOLOR_PROMPT = (
    "The FIRST image is a finished, correct scene: two identical sneakers on a "
    "faded vintage Persian/Oriental rug -- one shoe seen from directly above "
    "(top-down) on the left, one shoe in side profile on the right, both EXACTLY "
    "the same size and both pointing in the same direction. Keep its composition, "
    "layout, rug, lighting, shadows, both shoe shapes, sizes, positions, the gap "
    "between them and the 9:16 framing EXACTLY as they are. Do not change the "
    "arrangement, the shape or the sole. "
    "The SECOND image shows the SAME German Army Trainer / Replica sneaker model "
    "in a different colorway. Carefully study it and recolor BOTH sneakers in the "
    "first image to exactly match that shoe: the same upper color, the smooth "
    "leather panels and the suede overlays (toe, side stripe, heel), the same "
    "laces and the same gum/cream rubber sole. Change ONLY the colors and "
    "materials, nothing about the shape, pose or scene. "
    "Both shoes are ONE single identical sneaker model shown from two angles; they "
    "must match each other exactly in shape, proportions and details. Preserve the "
    "exact geometry of the shoes from the first image and only repaint their "
    "surfaces -- do NOT warp, stretch, melt, deform or redraw them, and do NOT turn "
    "them into two different shoes. "
    "The shoe stays sharp and clearly in focus, materials crisp, well-lit, colors "
    "true to the reference. Muted, natural, restrained colors, not cinematic, not "
    "staged, not a studio shoot. No film grain, no color grading. "
    "No star, no colorful star or sparkle, no symbol, no text, no logo and no "
    "watermark anywhere -- especially NOT in the bottom-right corner. The rug "
    "fills the frame. Output a single vertical 9:16 image."
)

# Swap: neuen Schuh erstmals in die Szene setzen (1. Bild Teppich, 2. Bild Schuh).
SWAP_PROMPT = (
    "The FIRST image is a fixed scene template (a faded vintage Persian/Oriental "
    "rug, soft even top-down daylight, vertical 9:16). The SECOND image is the new "
    "product: a German Army Trainer / Replica sneaker. Carefully study the second "
    "image and exactly reproduce the shoe's colors, the smooth leather panels and "
    "suede overlays, the laces, and the gum/cream rubber sole. Do not idealize, "
    "beautify, average or restyle it. "
    "Place TWO identical copies of this shoe on the rug: both EXACTLY the same size "
    "and pointing in the same direction, with a clear gap between them. The LEFT "
    "shoe lies flat on its sole seen from directly above (top-down); the RIGHT shoe "
    "rests on its outer side showing the full side profile. "
    "Both shoes are ONE single identical model and must match each other exactly in "
    "shape and details; do NOT warp, stretch, deform or redraw them and do NOT make "
    "two different shoes. If a top-down and a side reference are both given, the "
    "left shoe matches the top-down reference and the right shoe the side reference. "
    "Soft even natural top-down light, realistic contact shadows, the shoe sharp "
    "and clearly in focus, muted natural restrained colors, not cinematic, not "
    "staged, not a studio shoot. "
    "ONLY the two identical shoes on the rug -- no shoebox, no other objects, no "
    "hands, no text, no logo, no watermark, and NO star or sparkle anywhere, "
    "especially NOT in the bottom-right corner. The rug fills the frame. "
    "Output a single vertical 9:16 image."
)


def to_data_uri(path):
    """Lokaler Pfad oder URL -> fal akzeptiert beides als image_url (Data-URI fuer lokal)."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="Szenen-Anker (Teppich/fertige Show), 1. Bild")
    ap.add_argument("--shoe", required=True, nargs="+", help="Schuh-/Farbreferenz, 2. Bild (mehrere erlaubt)")
    ap.add_argument("--out", default="ergebnis.png")
    ap.add_argument("--mode", choices=["swap", "recolor"], default="recolor",
                    help="recolor = Szene behalten, nur umfaerben (Standard); swap = neuen Schuh setzen")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--prompt-file", dest="prompt_file", default=None)
    ap.add_argument("--aspect", default="9:16", help="Seitenverhaeltnis (Default 9:16)")
    args = ap.parse_args()

    if args.prompt_file:
        with open(args.prompt_file, encoding="utf-8") as f:
            args.prompt = f.read()
    elif args.prompt is None:
        args.prompt = RECOLOR_PROMPT if args.mode == "recolor" else SWAP_PROMPT

    key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
    if not key:
        sys.exit("Fehler: FAL_KEY (oder FAL_API_KEY) ist nicht gesetzt.")

    image_urls = [to_data_uri(args.scene)] + [to_data_uri(s) for s in args.shoe]
    body = {
        "prompt": args.prompt,
        "image_urls": image_urls,
        "num_images": 1,
        "output_format": "png",
        "aspect_ratio": args.aspect,
    }
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}

    resp = requests.post(SYNC_URL, headers=headers, data=json.dumps(body), timeout=300)
    # Fallback: manche Modelle kennen aspect_ratio nicht
    if resp.status_code == 422 and "aspect_ratio" in resp.text:
        body.pop("aspect_ratio", None)
        resp = requests.post(SYNC_URL, headers=headers, data=json.dumps(body), timeout=300)
    # Queue-Antwort (202) -> auf status_url pollen
    if resp.status_code == 202:
        loc = resp.json()
        status_url, resp_url = loc.get("status_url"), loc.get("response_url")
        for _ in range(60):
            time.sleep(3)
            st = requests.get(status_url, headers=headers, timeout=60).json()
            if st.get("status") == "COMPLETED":
                resp = requests.get(resp_url, headers=headers, timeout=120)
                break
        else:
            sys.exit("Timeout: fal.ai-Job nicht rechtzeitig fertig.")
    if resp.status_code != 200:
        sys.exit(f"fal.ai-Fehler {resp.status_code}: {resp.text[:1000]}")

    data = resp.json()
    images = data.get("images") or []
    if not images:
        sys.exit(f"Kein Bild in der Antwort: {json.dumps(data)[:1000]}")

    img_url = images[0]["url"]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    if img_url.startswith("data:"):
        raw = base64.b64decode(img_url.split(",", 1)[1])
    else:
        raw = requests.get(img_url, timeout=120).content
    with open(args.out, "wb") as f:
        f.write(raw)
    print(f"Gespeichert: {args.out}")


if __name__ == "__main__":
    main()
