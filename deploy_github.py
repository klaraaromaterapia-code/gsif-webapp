"""
GSIF — Deploy automat pe GitHub + Render.com
=============================================
Citește automat GITHUB_PERSONAL_ACCESS_TOKEN din C:/Users/35193/.env
"""

import subprocess
import sys
import os
from pathlib import Path

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def load_env(env_path=None):
    """Citește variabile din fișierul .env"""
    if env_path is None:
        env_path = Path.home() / ".env"
    env = {}
    if Path(env_path).exists():
        for line in Path(env_path).read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def deploy():
    env = load_env()

    GITHUB_TOKEN = env.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = input("GitHub Personal Access Token: ").strip()

    GITHUB_USER = env.get("GITHUB_USERNAME", "")
    if not GITHUB_USER:
        # Detectează automat username-ul din token
        r = requests.get("https://api.github.com/user",
                         headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if r.status_code == 200:
            GITHUB_USER = r.json()["login"]
            print(f"GitHub user detectat: {GITHUB_USER}")
        else:
            GITHUB_USER = input("Username GitHub: ").strip()

    REPO_NAME = "gsif-webapp"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    print(f"\n📦 Creez repo '{REPO_NAME}' pe GitHub...")
    r = requests.post("https://api.github.com/user/repos", headers=headers, json={
        "name": REPO_NAME,
        "description": "GSIF — Every Soul Has a Map | Certificatul Numerologic al Vieții",
        "private": False,
        "has_issues": True,
    })

    if r.status_code == 201:
        print(f"✅ Repo creat: https://github.com/{GITHUB_USER}/{REPO_NAME}")
    elif r.status_code == 422:
        print(f"ℹ️  Repo deja există: https://github.com/{GITHUB_USER}/{REPO_NAME}")
    else:
        print(f"❌ Eroare: {r.status_code} — {r.text}")
        return False

    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", repo_url])

    # Adaugă fișierele nestaged
    subprocess.run(["git", "add", "config_email.py", "deploy_github.py",
                    "start_gsif.bat", "generate_social_images.py"], capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add deploy, email config and image generation scripts"],
                   capture_output=True)

    print("\n📤 Push pe GitHub...")
    result = subprocess.run(["git", "push", "-u", "origin", "master"],
                            capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n✅ SUCCES! Cod pe GitHub:")
        print(f"   https://github.com/{GITHUB_USER}/{REPO_NAME}")
        print(f"\n🚀 Deploy pe Render.com (GRATUIT):")
        print(f"   1. render.com → New Web Service → Connect GitHub")
        print(f"   2. Selectează: {REPO_NAME}")
        print(f"   3. render.yaml e detectat automat")
        print(f"   4. Adaugă: SMTP_USER + SMTP_PASS în Environment")
        print(f"   5. Deploy!")
        print(f"\n🌐 URL: https://{REPO_NAME}.onrender.com")
        return True
    else:
        print(f"❌ Eroare push:\n{result.stderr}")
        return False


if __name__ == '__main__':
    deploy()
