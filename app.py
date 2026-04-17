"""
GSIF — Global Spiritual Identity Foundation
Web Application — Flask MVP
"Every Soul Has a Map"
"""

import os
import sys
import json
import threading
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, send_file, jsonify, Response)

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

# URL-ul public al site-ului (setat în env pe Render)
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')

# ── Stripe ──────────────────────────────────────────
# Setează STRIPE_SECRET_KEY în Render env vars (sk_live_...)
# Fără această cheie, generarea funcționează direct (mod dev)
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PRICE_EUR  = int(os.environ.get('STRIPE_PRICE_EUR', '20'))

# ── Supabase Storage ─────────────────────────────────
SUPABASE_URL    = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY    = os.environ.get('SUPABASE_KEY', '')
SUPABASE_BUCKET = 'certificates'
_sb_client      = None

def _get_supabase():
    global _sb_client
    if _sb_client is None and SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            _sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            log.warning(f"Supabase client init error: {e}")
    return _sb_client

def upload_pdf_supabase(pdf_path: str, filename: str) -> str | None:
    """Urcă PDF-ul în Supabase Storage. Returnează URL public sau None."""
    sb = _get_supabase()
    if not sb:
        return None
    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()
        remote_path = f'pdfs/{filename}'
        sb.storage.from_(SUPABASE_BUCKET).upload(
            remote_path, data,
            file_options={'content-type': 'application/pdf', 'upsert': 'true'}
        )
        public_url = sb.storage.from_(SUPABASE_BUCKET).get_public_url(remote_path)
        log.info(f"Supabase upload OK → {public_url}")
        return public_url
    except Exception as e:
        log.error(f"Supabase upload error: {e}")
        return None

# ── Configurare ──────────────────────────────────────
CERTS_DIR = os.path.join(BASE_DIR, 'certificates')
os.makedirs(CERTS_DIR, exist_ok=True)

EMAIL_CONFIG = {
    'smtp_host':  os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
    'smtp_port':  int(os.environ.get('SMTP_PORT', 587)),
    'username':   os.environ.get('SMTP_USER', ''),
    'password':   os.environ.get('SMTP_PASS', ''),
    'from_name':  'GSIF — Every Soul Has a Map',
    'from_email': os.environ.get('SMTP_USER', 'contact@gsif.org'),
}

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('gsif')

# ── Counter persistent ───────────────────────────────
_COUNTER_SEED = int(os.environ.get('COUNTER_SEED', '1247'))
_COUNTER_FILE = os.path.join('/tmp' if sys.platform != 'win32' else os.environ.get('TEMP', 'C:/Temp'), 'gsif_counter.json')
_counter_lock = threading.Lock()

def get_counter() -> int:
    try:
        with open(_COUNTER_FILE) as f:
            return json.load(f).get('count', _COUNTER_SEED)
    except Exception:
        return _COUNTER_SEED

def increment_counter() -> int:
    with _counter_lock:
        count = get_counter() + 1
        try:
            with open(_COUNTER_FILE, 'w') as f:
                json.dump({'count': count}, f)
        except Exception as e:
            log.debug(f"Counter write skip: {e}")
        return count

# n8n webhook — setează N8N_WEBHOOK_URL în Render env vars
# ex: https://gsif-n8n.onrender.com/webhook/gsif-certificate
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

    cv      = cifre.get('cifra_vietii')
    arhetip = ARHETIPURI.get(cv, str(cv))
    misiune = MISIUNI.get(cv, '')
    salut   = f"Dragă {prenume}," if prenume else "Bună ziua,"
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
        msg['From']    = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
        msg['To']      = dest_email
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
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


def send_email(name: str, email: str, subject: str, message: str) -> bool:
    """Trimite un mesaj de contact la adresa admin."""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"[GSIF Contact] {subject} — {name}"
        msg['From']    = EMAIL_CONFIG['from_email']
        msg['To']      = EMAIL_CONFIG['from_email']
        body = f"De la: {name} <{email}>\nSubiect: {subject}\n\n{message}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as s:
            s.starttls()
            s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            s.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['from_email'], msg.as_string())
        return True
    except Exception as e:
        log.error(f"Eroare email contact: {e}")
        return False


def _genera_certificat_pentru(prenume: str, data_nastere: str, cnp: str, email: str) -> dict:
    """Generează certificatul PDF și returnează result dict. Raise-ează la eroare."""
    zi, luna, an = map(int, data_nastere.split('.'))
    pdf_path = genereaza_certificat(zi, luna, an, cnp, output_dir=CERTS_DIR)

    cv  = calculeaza_cifra_vietii(zi, luna, an)
    czz = calculeaza_cifra_zilei(zi)
    cl  = calculeaza_cifra_lunii(luna)
    ca  = calculeaza_cifra_anului(an)
    cc  = calculeaza_contract(cnp)
    ap  = calculeaza_an_personal(zi, luna)

    cifre = {'cifra_vietii': cv, 'cifra_zi': czz, 'cifra_luna': cl,
             'cifra_an': ca, 'contract': cc, 'an_personal': ap}

    email_sent = False
    if email:
        email_sent = trimite_email_cu_certificat(email, prenume, pdf_path, cifre)

    filename     = os.path.basename(pdf_path)
    supabase_url = upload_pdf_supabase(pdf_path, filename)
    download_url = supabase_url if supabase_url else url_for('download_cert', filename=filename)

    increment_counter()
    log.info(f"Certificat generat: {filename} | CV={cv} | Email={email or 'N/A'}")

    _notifica_n8n({
        'prenume': prenume, 'cifra_vietii': cv,
        'arhetip': ARHETIPURI.get(cv, ''), 'email': email,
        'filename': filename,
    })

    return {
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


# ══════════════════════════════════════════════════════
#  RUTE
# ══════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template('index.html', counter=get_counter())


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
            log.info(f"[CONTACT] De la: {name} <{email}> | Subiect: {subject}")
            log.info(f"[CONTACT] Mesaj: {message[:200]}")

            contacts_file = os.path.join(BASE_DIR, 'contacts.txt')
            with open(contacts_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write(f"Nume: {name}\nEmail: {email}\nSubiect: {subject}\n")
                f.write(f"Mesaj:\n{message}\n")

            if EMAIL_CONFIG['username']:
                send_email(name, email, subject, message)

            contact_sent = True
            flash('Mesajul tău a fost trimis! Te vom contacta în curând. ✦', 'success')
        else:
            flash('Te rugăm să completezi toate câmpurile obligatorii.', 'error')

    return render_template('contact.html', contact_sent=contact_sent)


@app.route('/genereaza', methods=['GET', 'POST'])
def genereaza():
    result    = None
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
            return render_template('genereaza.html', result=None, form_data=form_data,
                                   stripe_enabled=bool(STRIPE_SECRET_KEY), price=STRIPE_PRICE_EUR)

        if len(cnp.replace(' ', '')) < 4:
            flash('CNP-ul trebuie să aibă cel puțin 4 cifre.', 'error')
            return render_template('genereaza.html', result=None, form_data=form_data,
                                   stripe_enabled=bool(STRIPE_SECRET_KEY), price=STRIPE_PRICE_EUR)

        # ── Stripe Checkout (activ când STRIPE_SECRET_KEY e setat) ──────────
        if STRIPE_SECRET_KEY:
            try:
                import stripe as _stripe
                _stripe.api_key = STRIPE_SECRET_KEY
                site = SITE_URL if 'localhost' not in SITE_URL else request.host_url.rstrip('/')
                checkout_session = _stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    locale='ro',
                    line_items=[{
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': 'Certificatul Numerologic al Vieții',
                                'description': 'Harta spirituală personalizată — GSIF · Every Soul Has a Map',
                            },
                            'unit_amount': STRIPE_PRICE_EUR * 100,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'{site}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=f'{site}/payment/cancel',
                    customer_email=email or None,
                    metadata={
                        'prenume':      prenume[:400],
                        'data_nastere': data_nastere,
                        'cnp':          cnp[:400],
                        'email':        email[:400] if email else '',
                    }
                )
                return redirect(checkout_session.url)
            except Exception as e:
                log.error(f"Stripe error: {e}")
                flash('Eroare la procesarea plății. Te rugăm să încerci din nou.', 'error')
                return render_template('genereaza.html', result=None, form_data=form_data,
                                       stripe_enabled=True, price=STRIPE_PRICE_EUR)

        # ── Generare directă (local / fără Stripe) ─────────────────────────
        try:
            result    = _genera_certificat_pentru(prenume, data_nastere, cnp, email)
            form_data = None
        except Exception as e:
            log.error(f"Eroare generare certificat: {e}", exc_info=True)
            flash('A apărut o eroare la generarea certificatului. Te rugăm să încerci din nou.', 'error')

    return render_template('genereaza.html', result=result, form_data=form_data,
                           stripe_enabled=bool(STRIPE_SECRET_KEY), price=STRIPE_PRICE_EUR)


# ── Plată Stripe — succes ────────────────────────────
def _meta_get(meta, key):
    """Accesează metadata Stripe compatibil cu SDK v5+/v7+ (StripeObject sau dict)."""
    if hasattr(meta, key):
        return getattr(meta, key) or ''
    if hasattr(meta, 'get'):
        return meta.get(key, '') or ''
    return ''

def _alerta_telegram_plata_esuata(session_id: str, eroare: str, meta: dict):
    """Trimite alertă Telegram când o plată e procesată dar generarea eșuează."""
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID   = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '6148595336')
    if not TELEGRAM_BOT_TOKEN:
        return
    import threading, urllib.request as _req, json as _json, urllib.parse as _parse
    def _send():
        try:
            prenume = _meta_get(meta, 'prenume') or 'necunoscut'
            email   = _meta_get(meta, 'email') or 'necunoscut'
            msg = (
                f"⚠️ PLATĂ PROCESATĂ — CERTIFICAT NEGENERAT\n\n"
                f"Session: {session_id[:30]}...\n"
                f"Prenume: {prenume}\n"
                f"Email: {email}\n"
                f"Eroare: {str(eroare)[:200]}\n\n"
                f"Retry: {SITE_URL}/admin/retry-payment/{session_id}"
            )
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = _json.dumps({'chat_id': TELEGRAM_CHAT_ID, 'text': msg}).encode()
            _req.urlopen(_req.Request(url, data=data,
                headers={'Content-Type': 'application/json'}), timeout=5)
        except Exception as ex:
            log.debug(f"Telegram alert skip: {ex}")
    threading.Thread(target=_send, daemon=True).start()


@app.route('/payment/success')
def payment_success():
    session_id = request.args.get('session_id', '')
    if not session_id or not STRIPE_SECRET_KEY:
        return redirect(url_for('genereaza'))
    try:
        import stripe as _stripe
        _stripe.api_key = STRIPE_SECRET_KEY
        cs = _stripe.checkout.Session.retrieve(session_id)

        payment_status = getattr(cs, 'payment_status', None) or cs.get('payment_status', '')
        if payment_status != 'paid':
            flash('Plata nu a fost finalizată. Contactează-ne dacă ai fost debitat.', 'error')
            return redirect(url_for('genereaza'))

        meta         = getattr(cs, 'metadata', None) or {}
        prenume      = _meta_get(meta, 'prenume')
        data_nastere = _meta_get(meta, 'data_nastere')
        cnp          = _meta_get(meta, 'cnp')
        email        = _meta_get(meta, 'email')

        result = _genera_certificat_pentru(prenume, data_nastere, cnp, email)
        flash('Plată confirmată ✦ Certificatul tău a fost generat!', 'success')
        return render_template('genereaza.html', result=result, form_data=None,
                               stripe_enabled=True, price=STRIPE_PRICE_EUR)

    except Exception as e:
        log.error(f"Payment success error: {e}", exc_info=True)
        try:
            _alerta_telegram_plata_esuata(session_id, e, getattr(cs, 'metadata', {}) if 'cs' in dir() else {})
        except Exception:
            pass
        flash('Plata a fost înregistrată dar a apărut o eroare la generare. Contactează-ne la klara.aromaterapia@gmail.com', 'error')
        return redirect(url_for('genereaza'))


@app.route('/admin/retry-payment/<session_id>')
def admin_retry_payment(session_id):
    """Rută admin: regenerează certificatul pentru o sesiune Stripe deja plătită."""
    admin_key = request.args.get('key', '')
    expected  = os.environ.get('ADMIN_KEY', 'gsif-admin-2026')
    if admin_key != expected:
        return 'Unauthorized', 403
    if not STRIPE_SECRET_KEY:
        return 'Stripe not configured', 500
    try:
        import stripe as _stripe
        _stripe.api_key = STRIPE_SECRET_KEY
        cs = _stripe.checkout.Session.retrieve(session_id)
        payment_status = getattr(cs, 'payment_status', None) or cs.get('payment_status', '')
        if payment_status != 'paid':
            return f'Payment status: {payment_status} — not paid', 400
        meta         = getattr(cs, 'metadata', None) or {}
        prenume      = _meta_get(meta, 'prenume')
        data_nastere = _meta_get(meta, 'data_nastere')
        cnp          = _meta_get(meta, 'cnp')
        email        = _meta_get(meta, 'email')
        result = _genera_certificat_pentru(prenume, data_nastere, cnp, email)
        return jsonify({'status': 'ok', 'cifra_vietii': result['cifra_vietii'],
                        'email_sent': result['email_sent'], 'download': result['download_url']})
    except Exception as e:
        log.error(f"Admin retry error: {e}", exc_info=True)
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ── Plată Stripe — anulare ───────────────────────────
@app.route('/payment/cancel')
def payment_cancel():
    flash('Plata a fost anulată. Poți reîncerca oricând. ✦', 'error')
    return redirect(url_for('genereaza'))


@app.route('/download/<filename>')
def download_cert(filename):
    """Descarcă un certificat PDF — local sau din Supabase."""
    filename = os.path.basename(filename)
    filepath = os.path.join(CERTS_DIR, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename,
                         mimetype='application/pdf')

    sb = _get_supabase()
    if sb:
        try:
            public_url = sb.storage.from_(SUPABASE_BUCKET).get_public_url(f'pdfs/{filename}')
            return redirect(public_url)
        except Exception as e:
            log.error(f"Supabase fallback download error: {e}")

    flash('Certificatul nu a fost găsit. Te rugăm să generezi din nou.', 'error')
    return redirect(url_for('genereaza'))


@app.route('/api/calculeaza', methods=['POST'])
def api_calculeaza():
    """API endpoint pentru calcul cifre numerologice în timp real."""
    data     = request.get_json(silent=True) or {}
    data_str = data.get('data_nastere', '')
    cnp      = data.get('cnp', '')

    try:
        zi, luna, an = map(int, data_str.split('.'))
        cv  = calculeaza_cifra_vietii(zi, luna, an)
        czz = calculeaza_cifra_zilei(zi)
        cl  = calculeaza_cifra_lunii(luna)
        ca  = calculeaza_cifra_anului(an)
        cc  = calculeaza_contract(cnp) if len(cnp) >= 4 else None
        ap  = calculeaza_an_personal(zi, luna)

        return jsonify({
            'success':      True,
            'cifra_vietii': cv,
            'arhetip':      ARHETIPURI.get(cv, ''),
            'misiune':      MISIUNI.get(cv, ''),
            'cifra_zi':     czz,
            'cifra_luna':   cl,
            'cifra_an':     ca,
            'contract':     cc,
            'an_personal':  ap,
            'maestru':      cv in (11, 22, 33),
            'element':      ELEMENTE.get(cv, ''),
            'chakra':       CHAKRE.get(cv, ''),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/sitemap.xml')
def sitemap():
    pages = ['', '/certificat', '/genereaza', '/manifest', '/despre', '/contact']
    configured = SITE_URL if 'localhost' not in SITE_URL else request.host_url.rstrip('/')
    base  = configured.rstrip('/')
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


@app.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')


# ── Stripe Webhook ───────────────────────────
# Setează STRIPE_WEBHOOK_SECRET în Render env vars după ce creezi webhook-ul în Stripe Dashboard
# Events: checkout.session.completed
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Webhook Stripe — backup pentru /payment/success.
    Dacă userul plătește dar browserul se închide înainte de redirect,
    certificatul se generează tot și emailul se trimite automat.
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', '')

    if not STRIPE_SECRET_KEY:
        return jsonify({'error': 'Stripe not configured'}), 400

    try:
        import stripe as _stripe
        _stripe.api_key = STRIPE_SECRET_KEY

        if STRIPE_WEBHOOK_SECRET:
            event = _stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            # Fără secret (dev) — parsăm direct dar nu verificăm semnătura
            import json as _json
            event = _stripe.Event.construct_from(
                _json.loads(payload), _stripe.api_key
            ) if hasattr(_stripe.Event, 'construct_from') else _stripe.Webhook.construct_event(
                payload, sig_header or 'none', 'whsec_test'
            )

        # stripe-python v5+ folosește acces prin atribute, nu dict
        event_type = getattr(event, 'type', None) or event.get('type', '')
        if event_type == 'checkout.session.completed':
            cs = getattr(getattr(event, 'data', None), 'object', None) or event['data']['object']
            payment_status = getattr(cs, 'payment_status', None) or cs.get('payment_status', '')
            if payment_status != 'paid':
                return jsonify({'status': 'ignored'}), 200

            meta = getattr(cs, 'metadata', None) or {}
            def _m(key):
                if hasattr(meta, key): return getattr(meta, key) or ''
                if hasattr(meta, 'get'): return meta.get(key, '') or ''
                return ''
            prenume      = _m('prenume')
            data_nastere = _m('data_nastere')
            cnp          = _m('cnp')
            email        = _m('email')

            if data_nastere and cnp:
                try:
                    _genera_certificat_pentru(prenume, data_nastere, cnp, email)
                    session_id = getattr(cs, 'id', '') or cs.get('id', '')
                    log.info(f"Webhook: certificat generat pentru {prenume or 'anonim'} | session={str(session_id)[:20]}")
                except Exception as e:
                    log.error(f"Webhook: eroare generare: {e}", exc_info=True)

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        log.error(f"Stripe webhook error: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'app': 'GSIF', 'version': '1.0',
                    'stripe': bool(STRIPE_SECRET_KEY)})


@app.route('/api/counter')
def counter_api():
    return jsonify({'count': get_counter()})


# ══════════════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════════════

if __name__ == '__main__':
    port  = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    print()
    print("═" * 55)
    print("  ✦  GSIF — Global Spiritual Identity Foundation")
    print("      Every Soul Has a Map")
    print("═" * 55)
    print(f"  URL local:   http://localhost:{port}")
    print(f"  Generează:   http://localhost:{port}/genereaza")
    print(f"  Stripe:      {'ACTIV' if STRIPE_SECRET_KEY else 'DEZACTIVAT (mod dev)'}")
    print(f"  Debug:       {debug}")
    print("═" * 55)
    print()
    app.run(host='0.0.0.0', port=port, debug=debug)
