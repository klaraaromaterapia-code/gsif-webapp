"""
GSIF — Generare imagini social media
=====================================
Folosește Pollinations.ai — GRATUIT, fără API key, fără credite.
Salvează 4 imagini în galeria/ pentru social media.
"""

import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent
GALERIA = BASE_DIR.parent / "galeria"
GALERIA.mkdir(exist_ok=True)

IMAGINI = [
    {
        "file": "social_1_soul_map.png",
        "prompt": "Sacred soul map golden sacred geometry symbols deep purple cosmic background numerology numbers glowing mystical spiritual certificate luxury branding Every Soul Has a Map cinematic lighting professional quality",
        "width": 1024,
        "height": 1024,
        "desc": "Soul Map — postare Instagram pătrată"
    },
    {
        "file": "social_2_newborn.png",
        "prompt": "Newborn baby hand holding glowing golden star map soft purple light sacred geometry spiritual numerology ethereal atmosphere divine light rays professional photography emotional",
        "width": 768,
        "height": 1360,
        "desc": "Newborn — story vertical Instagram/TikTok"
    },
    {
        "file": "social_3_motivational.png",
        "prompt": "Deep purple gold gradient background glowing sacred symbols Every Soul Has a Map sacred geometry mandala luxury spiritual social media post inspirational typography",
        "width": 1024,
        "height": 1024,
        "desc": "Motivational — postare Instagram"
    },
    {
        "file": "social_4_certificate.png",
        "prompt": "Ancient spiritual certificate parchment numerology symbols golden ink sacred chakra symbols crystals mystical purple light premium document aesthetic official elegant",
        "width": 768,
        "height": 1024,
        "desc": "Certificate — preview document"
    },
]


def genereaza_imagine(item, idx):
    prompt_enc = urllib.parse.quote(item["prompt"])
    seed = 42 + idx * 100  # seed fix pentru reproducibilitate
    url = (
        f"https://image.pollinations.ai/prompt/{prompt_enc}"
        f"?width={item['width']}&height={item['height']}"
        f"&model=flux&seed={seed}&nologo=true&enhance=true"
    )

    out_path = GALERIA / item["file"]
    print(f"\n[{idx+1}/4] {item['desc']}")
    print(f"  Generare... (poate dura 15-30 secunde)")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GSIF/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        out_path.write_bytes(data)
        size_kb = len(data) // 1024
        print(f"  ✅ Salvat: {out_path.name} ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"  ❌ Eroare: {e}")
        return False


def main():
    print("=" * 55)
    print("  GSIF — Generare imagini social media")
    print("  Powered by Pollinations.ai (gratuit)")
    print("=" * 55)

    succes = 0
    for i, item in enumerate(IMAGINI):
        if genereaza_imagine(item, i):
            succes += 1
        time.sleep(2)  # pauză între request-uri

    print(f"\n{'='*55}")
    print(f"  Rezultat: {succes}/{len(IMAGINI)} imagini generate")
    print(f"  Director: {GALERIA}")

    if succes > 0:
        print(f"\n  Imagini gata pentru social media:")
        for item in IMAGINI:
            path = GALERIA / item["file"]
            if path.exists():
                print(f"  ✦ {item['file']} — {item['desc']}")

    # Notificare Telegram dacă token disponibil
    try:
        env_file = Path.home() / ".env"
        env = {}
        if env_file.exists():
            for line in env_file.read_text(encoding='utf-8').splitlines():
                if '=' in line and not line.startswith('#'):
                    k, _, v = line.partition('=')
                    env[k.strip()] = v.strip().strip('"').strip("'")

        token = env.get("TELEGRAM_BOT_TOKEN")
        chat_id = env.get("TELEGRAM_CHAT_ID")

        if token and chat_id and succes > 0:
            import urllib.request, json
            msg = f"✦ GSIF — {succes} imagini social media generate!\n📁 galeria/social_1..4.png"
            data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=data, headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=10)
            print(f"\n  📱 Notificare Telegram trimisă!")
    except Exception:
        pass  # Telegram opțional


if __name__ == '__main__':
    main()
