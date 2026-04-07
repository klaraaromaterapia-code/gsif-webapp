"""
GSIF — Configurare Email
========================
Rulează acest script o dată pentru a salva credențialele email.
Alternativ, setează variabilele de mediu:

  set SMTP_USER=adresa_ta@gmail.com
  set SMTP_PASS=parola_app_gmail

Pentru Gmail, ai nevoie de un "App Password":
  https://myaccount.google.com/apppasswords
  (Google Account → Security → 2-Step Verification → App passwords)
"""

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '.email_config.json')

def salveaza_config():
    print("\n" + "="*50)
    print("  GSIF — Configurare Email")
    print("="*50)
    print("\nPentru Gmail, folosește un App Password, nu parola normală.")
    print("https://myaccount.google.com/apppasswords\n")

    email = input("Adresa ta Gmail (sau alt SMTP): ").strip()
    parola = input("App Password Gmail: ").strip()
    smtp_host = input("SMTP Host [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP Port [587]: ").strip() or "587"

    config = {
        "SMTP_USER": email,
        "SMTP_PASS": parola,
        "SMTP_HOST": smtp_host,
        "SMTP_PORT": smtp_port,
    }

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config salvat în {CONFIG_FILE}")
    print("\nAcum poți porni aplicația cu start_gsif.bat")
    print("Certificatele vor fi trimise automat pe email!\n")

def incarca_config():
    """Încarcă config-ul în variabilele de mediu."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        for key, value in config.items():
            os.environ.setdefault(key, value)

# Auto-load la import
incarca_config()

def auto_config_din_env(env_path=None):
    """Configurare automată din fișierul .env — fără input manual."""
    from pathlib import Path
    if env_path is None:
        env_path = Path.home() / ".env"

    env = {}
    if Path(env_path).exists():
        for line in Path(env_path).read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")

    smtp_user = env.get("SMTP_USER") or env.get("GMAIL_USER") or env.get("EMAIL_USER", "")
    smtp_pass = env.get("SMTP_PASS") or env.get("GMAIL_PASS") or env.get("EMAIL_PASS", "")
    smtp_host = env.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = env.get("SMTP_PORT", "587")

    if smtp_user and smtp_pass:
        config = {
            "SMTP_USER": smtp_user,
            "SMTP_PASS": smtp_pass,
            "SMTP_HOST": smtp_host,
            "SMTP_PORT": smtp_port,
        }
        with open(CONFIG_FILE, 'w') as f:
            import json
            json.dump(config, f, indent=2)
        print(f"✅ Email configurat automat din .env: {smtp_user}")
        return True
    else:
        print("SMTP_USER/SMTP_PASS nu sunt in .env - ruleaza python config_email.py manual")
        print("   sau adauga in .env: SMTP_USER=email@gmail.com si SMTP_PASS=app_password")
        return False


if __name__ == '__main__':
    import sys
    if '--auto' in sys.argv:
        auto_config_din_env()
    else:
        salveaza_config()
