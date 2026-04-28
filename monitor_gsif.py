"""
GSIF Monitor — pingează /api/health la fiecare 5 minute
Alertă Telegram dacă site-ul nu răspunde.
Rulat de Windows Task Scheduler la fiecare 5 minute.
Token-urile se citesc din .env sau variabile de mediu.
"""
import urllib.request
import urllib.error
import json
import sys
import os

# Citește .env dacă există (același director ca scriptul)
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_ENV_PATH):
    with open(_ENV_PATH) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

HEALTH_URL = os.environ.get("SITE_URL", "https://everysoulhasamap.org") + "/api/health"
BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID    = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "6148595336")
TIMEOUT    = 20

def telegram(msg: str):
    if not BOT_TOKEN:
        print("Telegram skip — BOT_TOKEN nelipsa.", file=sys.stderr)
        return
    try:
        data = json.dumps({"chat_id": CHAT_ID, "text": msg}).encode()
        req  = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)

def check():
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "GSIF-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = json.loads(r.read())
            if r.status == 200 and body.get("status") == "ok":
                print(f"OK — {HEALTH_URL}")
                return True
            else:
                raise ValueError(f"Status unexpected: {r.status} {body}")
    except Exception as e:
        msg = (
            f"\U0001f6a8 GSIF DOWN!\n{HEALTH_URL}\n"
            f"Eroare: {str(e)[:200]}\n\n"
            f"Render: https://dashboard.render.com/web/srv-d7akeq2dbo4c73aasb9g"
        )
        print(msg, file=sys.stderr)
        telegram(msg)
        return False

if __name__ == "__main__":
    ok = check()
    sys.exit(0 if ok else 1)
