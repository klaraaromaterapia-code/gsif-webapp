"""
GSIF — Global Spiritual Identity Foundation
Web Application — Flask MVP
"Every Soul Has a Map"
"""

import os
import sys
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, send_file, jsonify)

# ── Fix encoding Windows ─────────────────────────────
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# ── Directorul aplicației ────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from certificat import (
    genereaza_certificat,
    calculeaza_cifra_vietii,
    calculeaza_cifra_zilei,
    calculeaza_cifra_lunii,
    calculeaza_cifra_anului,
    calculeaza_contract,
    calculeaza_an_personal,
    ARHETIPURI, MISIUNI, CRISTALE, CHAKRE, ELEMENTE, CULORI
)

# ── Flask App ────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('GSIF_SECRET_KEY', 'gsif-every-soul-has-a-map-2026')

# URL-ul public al site-ului (setat în env pe Render, fallback local)
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')

# ── Configurare ──────────────────────────────────────
CERTS_DIR = os.path.join(BASE_DIR, 'certificates')
os.makedirs(CERTS_DIR, exist_ok=True)

# Email — configurează cu datele tale sau lasă gol
EMAIL_CONFIG = {
    'smtp_host':  os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
    'smtp_port':  int(os.environ.get('SMTP_PORT', 587)),
    'username':   os.environ.get('SMTP_USER', ''),       # ex: contact@gsif.org
    'password':   os.environ.get('SMTP_PASS', ''),       # App Password Gmail
    'from_name':  'GSIF — Every Soul Has a Map',
    'from_email': os.environ.get('SMTP_USER', 'contact@gsif.org'),
}

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('gsif')

# n8n webhook pentru automatizări (Telegram, email etc.)
N8N_WEBHOOK_URL = os.environ.get(
    'N8N_WEBHOOK_URL',
    'http://localhost:5678/webhook/gsif-certificate'
)


def _notifica_n8n(data: dict):
    """Trimite date către n8n webhook async (non-blocking)."""
    import threading, json as _json, urllib.request as _req
    def _send():
        try:
            body = _json.dumps(data).encode()
            r = _req.Request(N8N_WEBHOOK_URL, data=body,
                             headers={'Content-Type': 'application/json'})
            _req.urlopen(r, timeout=5)
        except Exception as ex:
            log.debug(f"n8n webhook skip: {ex}")
    threading.Thread(target=_send, daemon=True).start()


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════

def trimite_email_cu_certificat(dest_email: str, prenume: str, pdf_path: str, cifre: dict) -> bool:
    """Trimite certificatul PDF pe email. Returnează True dacă reușit."""
    if not EMAIL_CONFIG['username'] or not EMAIL_CONFIG['password']:
        log.info("Email nesolicitat — SMTP neconfigurat.")
        return False

    cv = cifre.get('cifra_vietii')
    arhetip = ARHETIPURI.get(cv, str(cv))
    misiune = MISIUNI.get(cv, '')

    salut = f"Dragă {prenume}," if prenume else "Bună ziua,"

    site_url = SITE_URL
    html_body = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#fff;">
      <div style="background:linear-gradient(135deg,#280f50,#3d1a7a);padding:40px;text-align:center;">
        <h1 style="color:#c9a84c;font-size:1.4rem;margin:0;letter-spacing:3px;">✦ GSIF</h1>
        <p style="color:rgba(255,255,255,0.7);margin:8px 0 0;font-style:italic;font-size:0.9rem;">Every Soul Has a Map</p>
      </div>
      <div style="padding:40px;">
        <p style="color:#280f50;font-size:1rem;">{salut}</p>
        <p style="color:#4a4060;line-height:1.7;">
          Certificatul tău Numerologic al Vieții este gata.
          Îl găsești atașat la acest email.
        </p>
        <div style="background:#f8f5ff;border-left:3px solid #c9a84c;padding:20px;margin:24px 0;border-radius:0 10px 10px 0;">
          <p style="margin:0 0 8px;font-size:0.8rem;color:#8a7aaa;letter-spacing:2px;text-transform:uppercase;">Harta ta</p>
          <p style="margin:0;color:#280f50;font-size:1.3rem;font-weight:bold;">Cifra Vieții: {cv}</p>
          <p style="margin:4px 0 0;color:#5e3a9e;font-style:italic;">{arhetip}</p>
          <p style="margin:8px 0 0;color:#4a4060;font-size:0.9rem;">{misiune}</p>
        </div>
        <p style="color:#4a4060;line-height:1.7;">
          Aceasta este harta sufletului tău — păstreaz-o, meditează la ea,
          și <strong style="color:#280f50;">încearcă să trăiești în acord cu misiunea ta</strong>.
        </p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{site_url}" style="background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#280f50;padding:12px 32px;border-radius:30px;text-decoration:none;font-weight:bold;font-size:0.9rem;">
            Vizitează everysoulhasamap.org
          </a>
        </div>
      </div>
      <div style="background:#f8f5ff;padding:20px;text-align:center;">
        <p style="color:#8a7aaa;font-size:0.78rem;margin:0;">
          © 2026 Global Spiritual Identity Foundation (GSIF)<br>
          Certificatul are valoare spirituală și educațională.
        </p>
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"✦ Certificatul tău Numerologic — Cifra Vieții {cv} · GSIF"
        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
        msg['To'] = dest_email

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Atașează PDF
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        pdf_filename = os.path.basename(pdf_path)
        part.add_header('Content-Disposition', f'attachment; filename="{pdf_filename}"')
        msg.attach(part)

        with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            server.sendmail(EMAIL_CONFIG['from_email'], dest_email, msg.as_string())

        log.info(f"Email trimis la {dest_email}")
        return True

    except Exception as e:
        log.error(f"Eroare trimitere email: {e}")
        return False


# ══════════════════════════════════════════════════════
#  RUTE
# ══════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/certificat')
def certificat_page():
    return render_template('certificat.html')


@app.route('/manifest')
def manifest():
    return render_template('manifest.html')


@app.route('/despre')
def despre():
    return render_template('despre.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_sent = False
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', 'altele')
        message = request.form.get('message', '').strip()

        if name and email and message:
            # Loghează mesajul
            log.info(f"[CONTACT] De la: {name} <{email}> | Subiect: {subject}")
            log.info(f"[CONTACT] Mesaj: {message[:200]}")

            # Salvează în fișier local (până la configurare email)
            contacts_file = os.path.join(BASE_DIR, 'contacts.txt')
            with open(contacts_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write(f"Nume: {name}\nEmail: {email}\nSubiect: {subject}\n")
                f.write(f"Mesaj:\n{message}\n")

            # Trimite email dacă e configurat
            if EMAIL_CONFIG['username']:
                try:
                    msg = MIMEMultipart()
                    msg['Subject'] = f"[GSIF Contact] {subject} — {name}"
                    msg['From'] = EMAIL_CONFIG['from_email']
                    msg['To'] = EMAIL_CONFIG['from_email']
                    body = f"De la: {name} <{email}>\nSubiect: {subject}\n\n{message}"
                    msg.attach(MIMEText(body, 'plain', 'utf-8'))
                    with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as s:
                        s.starttls()
                        s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                        s.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['from_email'], msg.as_string())
                except Exception as e:
                    log.error(f"Eroare email contact: {e}")

            contact_sent = True
            flash('Mesajul tău a fost trimis! Te vom contacta în curând. ✦', 'success')

        else:
            flash('Te rugăm să completezi toate câmpurile obligatorii.', 'error')

    return render_template('contact.html', contact_sent=contact_sent)


@app.route('/genereaza', methods=['GET', 'POST'])
def genereaza():
    result = None
    form_data = None

    if request.method == 'POST':
        prenume      = request.form.get('prenume', '').strip()
        data_nastere = request.form.get('data_nastere', '').strip()
        cnp          = request.form.get('cnp', '').strip()
        email        = request.form.get('email', '').strip()

        form_data = {'prenume': prenume, 'data_nastere': data_nastere,
                     'cnp': cnp, 'email': email}

        # Validare
        try:
            zi, luna, an = map(int, data_nastere.split('.'))
            assert 1 <= zi <= 31 and 1 <= luna <= 12 and 1900 <= an <= 2026
        except Exception:
            flash('Format dată incorect. Folosește ZZ.LL.AAAA (ex: 01.07.1985)', 'error')
            return render_template('genereaza.html', result=None, form_data=form_data)

        if len(cnp.replace(' ', '')) < 4:
            flash('CNP-ul trebuie să aibă cel puțin 4 cifre.', 'error')
            return render_template('genereaza.html', result=None, form_data=form_data)

        try:
            # Generează PDF
            pdf_path = genereaza_certificat(zi, luna, an, cnp, output_dir=CERTS_DIR)

            # Calculează cifre pentru afișare
            cv  = calculeaza_cifra_vietii(zi, luna, an)
            czz = calculeaza_cifra_zilei(zi)
            cl  = calculeaza_cifra_lunii(luna)
            ca  = calculeaza_cifra_anului(an)
            cc  = calculeaza_contract(cnp)
            ap  = calculeaza_an_personal(zi, luna)

            cifre = {
                'cifra_vietii': cv, 'cifra_zi': czz, 'cifra_luna': cl,
                'cifra_an': ca, 'contract': cc, 'an_personal': ap
            }

            # Trimite pe email dacă completat
            email_sent = False
            if email:
                email_sent = trimite_email_cu_certificat(email, prenume, pdf_path, cifre)

            # Construiește URL de download
            filename = os.path.basename(pdf_path)
            download_url = url_for('download_cert', filename=filename)

            result = {
                'prenume':      prenume,
                'cifra_vietii': cv,
                'arhetip':      ARHETIPURI.get(cv, str(cv)),
                'misiune':      MISIUNI.get(cv, ''),
                'cifra_zi':     czz,
                'cifra_luna':   cl,
                'cifra_an':     ca,
                'contract':     cc,
                'an_personal':  ap,
                'email_sent':   email_sent,
                'download_url': download_url,
                'element':      ELEMENTE.get(cv, ''),
                'chakra':       CHAKRE.get(cv, ''),
                'cristale':     CRISTALE.get(cv, ''),
                'culori':       CULORI.get(cv, ''),
                'maestru':      cv in (11, 22, 33),
            }

            # Loghează
            log.info(f"Certificat generat: {filename} | CV={cv} | Email={email or 'N/A'}")

            # Notifică n8n webhook (Telegram + automații)
            _notifica_n8n({
                'prenume': prenume, 'cifra_vietii': cv,
                'arhetip': ARHETIPURI.get(cv, ''), 'email': email,
                'filename': filename,
            })

            form_data = None  # nu mai afișa formularul după succes

        except Exception as e:
            log.error(f"Eroare generare certificat: {e}", exc_info=True)
            flash(f'A apărut o eroare la generarea certificatului. Te rugăm să încerci din nou.', 'error')

    return render_template('genereaza.html', result=result, form_data=form_data)


@app.route('/download/<filename>')
def download_cert(filename):
    """Descarcă un certificat PDF generat."""
    # Sanitizare nume fișier
    filename = os.path.basename(filename)
    filepath = os.path.join(CERTS_DIR, filename)
    if not os.path.exists(filepath):
        flash('Certificatul nu a fost găsit. Te rugăm să generezi din nou.', 'error')
        return redirect(url_for('genereaza'))
    return send_file(filepath, as_attachment=True, download_name=filename,
                     mimetype='application/pdf')


@app.route('/api/calculeaza', methods=['POST'])
def api_calculeaza():
    """API endpoint pentru calcul cifre numerologice în timp real."""
    data = request.get_json(silent=True) or {}
    data_str = data.get('data_nastere', '')
    cnp = data.get('cnp', '')

    try:
        zi, luna, an = map(int, data_str.split('.'))
        cv  = calculeaza_cifra_vietii(zi, luna, an)
        czz = calculeaza_cifra_zilei(zi)
        cl  = calculeaza_cifra_lunii(luna)
        ca  = calculeaza_cifra_anului(an)
        cc  = calculeaza_contract(cnp) if len(cnp) >= 4 else None
        ap  = calculeaza_an_personal(zi, luna)

        return jsonify({
            'success': True,
            'cifra_vietii': cv,
            'arhetip': ARHETIPURI.get(cv, ''),
            'misiune': MISIUNI.get(cv, ''),
            'cifra_zi': czz,
            'cifra_luna': cl,
            'cifra_an': ca,
            'contract': cc,
            'an_personal': ap,
            'maestru': cv in (11, 22, 33),
            'element': ELEMENTE.get(cv, ''),
            'chakra': CHAKRE.get(cv, ''),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/sitemap.xml')
def sitemap():
    """Sitemap XML pentru SEO."""
    from flask import Response
    pages = ['', '/certificat', '/genereaza', '/manifest', '/despre', '/contact']
    # Use request URL if SITE_URL is localhost (not configured)
    configured = SITE_URL if 'localhost' not in SITE_URL else request.host_url.rstrip('/')
    base = configured.rstrip('/')
    items = '\n'.join(
        f'  <url><loc>{base}{p}</loc><changefreq>weekly</changefreq><priority>{"1.0" if p == "" else "0.8"}</priority></url>'
        for p in pages
    )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>'''
    return Response(xml, mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt')


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'app': 'GSIF', 'version': '1.0'})


# ══════════════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    print()
    print("═" * 55)
    print("  ✦  GSIF — Global Spiritual Identity Foundation")
    print("      Every Soul Has a Map")
    print("═" * 55)
    print(f"  URL local:   http://localhost:{port}")
    print(f"  Generează:   http://localhost:{port}/genereaza")
    print(f"  Debug:       {debug}")
    print("═" * 55)
    print()
    app.run(host='0.0.0.0', port=port, debug=debug)
