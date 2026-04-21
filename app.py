"""
GSIF — Global Spiritual Identity Foundation
Web Application — Flask
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

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

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

# ── Flask ────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('GSIF_SECRET_KEY', 'gsif-every-soul-has-a-map-2026')

SITE_URL          = os.environ.get('SITE_URL', 'http://localhost:5000')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PRICE_EUR  = int(os.environ.get('STRIPE_PRICE_EUR', '20'))
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
ADMIN_KEY         = os.environ.get('ADMIN_KEY', 'gsif-admin-2026')

TELEGRAM_BOT_TOKEN     = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID', '6148595336')

SUPABASE_URL    = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY    = os.environ.get('SUPABASE_KEY', '')
SUPABASE_BUCKET = 'certificates'
_sb_client      = None

EMAIL_CONFIG = {
    'smtp_host':  os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
    'smtp_port':  int(os.environ.get('SMTP_PORT', 587)),
    'username':   os.environ.get('SMTP_USER', ''),
    'password':   os.environ.get('SMTP_PASS', ''),
    'from_name':  'GSIF — Every Soul Has a Map',
    'from_email': os.environ.get('SMTP_USER', 'auris6368@gmail.com'),
}

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('gsif')

# ── Paths ────────────────────────────────────────────
CERTS_DIR    = os.path.join(BASE_DIR, 'certificates')
PAYMENTS_LOG = os.path.join(BASE_DIR, 'payments_log.jsonl')
os.makedirs(CERTS_DIR, exist_ok=True)

# ── Counter ──────────────────────────────────────────
_COUNTER_SEED = int(os.environ.get('COUNTER_SEED', '1247'))
_COUNTER_FILE = os.path.join(
    '/tmp' if sys.platform != 'win32' else os.environ.get('TEMP', 'C:/Temp'),
    'gsif_counter.json'
)
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
        except Exception:
            pass
        return count


# ══════════════════════════════════════════════════════
#  PAYMENT LOG — idempotency + audit trail
# ══════════════════════════════════════════════════════

_log_lock = threading.Lock()

def _log_payment(session_id: str, status: str, data: dict):
    """Adaugă o intrare în payments_log.jsonl."""
    entry = {
        'ts':         datetime.now().isoformat(),
        'session_id': session_id,
        'status':     status,
        **data
    }
    with _log_lock:
        try:
            with open(PAYMENTS_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            log.error(f"Payment log write error: {e}")

def _load_payments() -> list:
    """Citește tot logul de plăți."""
    entries = []
    try:
        with open(PAYMENTS_LOG, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    except FileNotFoundError:
        pass
    return entries

def _is_session_processed(session_id: str) -> bool:
    """Returnează True dacă sesiunea a fost deja procesată cu succes."""
    for entry in _load_payments():
        if entry.get('session_id') == session_id and entry.get('status') == 'generated':
            return True
    return False


# ══════════════════════════════════════════════════════
#  STRIPE HELPERS
# ══════════════════════════════════════════════════════

def _meta_get(meta, key: str) -> str:
    """Accesează metadata Stripe compatibil cu toate versiunile SDK (StripeObject nu are .get())."""
    try:
        val = getattr(meta, key)
        return val if val else ''
    except AttributeError:
        pass
    if hasattr(meta, 'get'):
        return meta.get(key, '') or ''
    return ''


def _get_site_url() -> str:
    """Returnează URL-ul public al site-ului, corect și pentru HTTPS pe Render."""
    if 'localhost' not in SITE_URL:
        return SITE_URL.rstrip('/')
    # Pe Render, request.host_url poate veni ca http:// — forțăm https
    host = request.host_url.rstrip('/')
    if request.headers.get('X-Forwarded-Proto') == 'https':
        host = host.replace('http://', 'https://')
    return host


# ══════════════════════════════════════════════════════
#  SUPABASE
# ══════════════════════════════════════════════════════

def _get_supabase():
    global _sb_client
    if _sb_client is None and SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            _sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            log.warning(f"Supabase init error: {e}")
    return _sb_client

def _upload_pdf_supabase(pdf_path: str, filename: str) -> str | None:
    sb = _get_supabase()
    if not sb:
        return None
    try:
        with open(pdf_path, 'rb') as f:
            data = f.read()
        remote = f'pdfs/{filename}'
        sb.storage.from_(SUPABASE_BUCKET).upload(
            remote, data,
            file_options={'content-type': 'application/pdf', 'upsert': 'true'}
        )
        return sb.storage.from_(SUPABASE_BUCKET).get_public_url(remote)
    except Exception as e:
        log.error(f"Supabase upload error: {e}")
        return None


# ══════════════════════════════════════════════════════
#  NOTIFICATIONS
# ══════════════════════════════════════════════════════

def _telegram(text: str, pdf_path: str = None):
    """Trimite mesaj (și opțional PDF) pe Telegram, async."""
    if not TELEGRAM_BOT_TOKEN:
        return
    def _send():
        import urllib.request as _req
        base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        try:
            # text message
            data = json.dumps({'chat_id': TELEGRAM_ADMIN_CHAT_ID, 'text': text}).encode()
            _req.urlopen(_req.Request(f"{base}/sendMessage", data=data,
                headers={'Content-Type': 'application/json'}), timeout=8)
        except Exception as ex:
            log.debug(f"Telegram text skip: {ex}")
        if pdf_path and os.path.exists(pdf_path):
            try:
                boundary = 'GSIFBOUND'
                fname = os.path.basename(pdf_path)
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                body = (
                    f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n'
                    f'{TELEGRAM_ADMIN_CHAT_ID}\r\n'
                    f'--{boundary}\r\nContent-Disposition: form-data; name="document"; filename="{fname}"\r\n'
                    f'Content-Type: application/pdf\r\n\r\n'
                ).encode() + pdf_data + f'\r\n--{boundary}--\r\n'.encode()
                _req.urlopen(_req.Request(f"{base}/sendDocument", data=body,
                    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}), timeout=15)
            except Exception as ex:
                log.debug(f"Telegram PDF skip: {ex}")
    threading.Thread(target=_send, daemon=True).start()


def _notifica_n8n(data: dict):
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL',
        'http://localhost:5678/webhook/gsif-certificate')
    def _send():
        try:
            body = json.dumps(data).encode()
            import urllib.request as _req
            r = _req.Request(N8N_WEBHOOK_URL, data=body,
                headers={'Content-Type': 'application/json'})
            _req.urlopen(r, timeout=5)
        except Exception as ex:
            log.debug(f"n8n webhook skip: {ex}")
    threading.Thread(target=_send, daemon=True).start()


# ══════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════

def _trimite_email(dest_email: str, prenume: str, pdf_path: str, cifre: dict) -> bool:
    if not EMAIL_CONFIG['username'] or not EMAIL_CONFIG['password']:
        log.info("Email skip — SMTP neconfigurat.")
        return False
    cv      = cifre.get('cifra_vietii')
    arhetip = ARHETIPURI.get(cv, str(cv))
    misiune = MISIUNI.get(cv, '')
    salut   = f"Dragă {prenume}," if prenume else "Bună ziua,"
    html = f"""
    <div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;background:#fff;">
      <div style="background:linear-gradient(135deg,#280f50,#3d1a7a);padding:40px;text-align:center;">
        <h1 style="color:#c9a84c;font-size:1.4rem;margin:0;letter-spacing:3px;">✦ GSIF</h1>
        <p style="color:rgba(255,255,255,0.7);margin:8px 0 0;font-style:italic;font-size:0.9rem;">Every Soul Has a Map</p>
      </div>
      <div style="padding:40px;">
        <p style="color:#280f50;">{salut}</p>
        <p style="color:#4a4060;line-height:1.7;">Certificatul tău Numerologic al Vieții este gata. Îl găsești atașat.</p>
        <div style="background:#f8f5ff;border-left:3px solid #c9a84c;padding:20px;margin:24px 0;border-radius:0 10px 10px 0;">
          <p style="margin:0 0 8px;font-size:0.8rem;color:#8a7aaa;letter-spacing:2px;text-transform:uppercase;">Harta ta</p>
          <p style="margin:0;color:#280f50;font-size:1.3rem;font-weight:bold;">Cifra Vieții: {cv}</p>
          <p style="margin:4px 0 0;color:#5e3a9e;font-style:italic;">{arhetip}</p>
          <p style="margin:8px 0 0;color:#4a4060;font-size:0.9rem;">{misiune}</p>
        </div>
        <div style="text-align:center;margin:32px 0;">
          <a href="{SITE_URL}" style="background:linear-gradient(135deg,#c9a84c,#e8c97a);color:#280f50;padding:12px 32px;border-radius:30px;text-decoration:none;font-weight:bold;font-size:0.9rem;">
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
    </div>"""
    try:
        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"✦ Certificatul tău Numerologic — Cifra Vieții {cv} · GSIF"
        msg['From']    = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
        msg['To']      = dest_email
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(pdf_path)}"')
        msg.attach(part)
        port = EMAIL_CONFIG['smtp_port']
        if port == 465:
            with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_host'], port, timeout=15) as s:
                s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                s.sendmail(EMAIL_CONFIG['from_email'], dest_email, msg.as_string())
        else:
            with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], port, timeout=15) as s:
                s.ehlo(); s.starttls(); s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                s.sendmail(EMAIL_CONFIG['from_email'], dest_email, msg.as_string())
        log.info(f"Email trimis → {dest_email}")
        return True
    except Exception as e:
        log.error(f"Email error: {e}")
        return False

def _trimite_contact(name, email, subject, message) -> bool:
    if not EMAIL_CONFIG['username'] or not EMAIL_CONFIG['password']:
        return False
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"[GSIF Contact] {subject} — {name}"
        msg['From']    = EMAIL_CONFIG['from_email']
        msg['To']      = EMAIL_CONFIG['from_email']
        msg.attach(MIMEText(f"De la: {name} <{email}>\nSubiect: {subject}\n\n{message}", 'plain', 'utf-8'))
        port = EMAIL_CONFIG['smtp_port']
        if port == 465:
            with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_host'], port, timeout=15) as s:
                s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                s.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['from_email'], msg.as_string())
        else:
            with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], port, timeout=15) as s:
                s.starttls(); s.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                s.sendmail(EMAIL_CONFIG['from_email'], EMAIL_CONFIG['from_email'], msg.as_string())
        return True
    except Exception as e:
        log.error(f"Contact email error: {e}")
        return False


# ══════════════════════════════════════════════════════
#  CORE: GENERARE CERTIFICAT
# ══════════════════════════════════════════════════════

def _genera_certificat_pentru(prenume: str, data_nastere: str, cnp: str, email: str,
                               session_id: str = '') -> dict:
    """
    Generează certificatul PDF și trimite email.
    session_id este folosit pentru filename unic și idempotency.
    """
    zi, luna, an = map(int, data_nastere.strip().split('.'))

    # Filename unic: include suffix din session_id pentru a evita coliziunile
    suffix = ''
    if session_id:
        # Ultimele 8 caractere din session_id (după 'cs_live_' sau 'cs_test_')
        clean = session_id.replace('cs_live_', '').replace('cs_test_', '')
        suffix = f'_{clean[-8:]}' if len(clean) >= 8 else f'_{clean}'

    pdf_path = genereaza_certificat(zi, luna, an, cnp,
                                    output_dir=CERTS_DIR,
                                    filename_suffix=suffix)

    cv  = calculeaza_cifra_vietii(zi, luna, an)
    czz = calculeaza_cifra_zilei(zi)
    cl  = calculeaza_cifra_lunii(luna)
    ca  = calculeaza_cifra_anului(an)
    cc  = calculeaza_contract(cnp)
    ap  = calculeaza_an_personal(zi, luna)
    cifre = {'cifra_vietii': cv, 'cifra_zi': czz, 'cifra_luna': cl,
             'cifra_an': ca, 'contract': cc, 'an_personal': ap}

    # Email
    email_sent = False
    if email:
        email_sent = _trimite_email(email, prenume, pdf_path, cifre)

    # Supabase upload
    filename     = os.path.basename(pdf_path)
    supabase_url = _upload_pdf_supabase(pdf_path, filename)

    # Download URL — folosim _external=True pentru a nu depinde de request context
    try:
        download_url = supabase_url or url_for('download_cert', filename=filename, _external=True)
    except RuntimeError:
        download_url = supabase_url or f'{SITE_URL}/download/{filename}'

    increment_counter()
    log.info(f"Certificat generat: {filename} | CV={cv} | email={email or 'N/A'}")

    # Notificări
    _notifica_n8n({'prenume': prenume, 'cifra_vietii': cv,
                   'arhetip': ARHETIPURI.get(cv, ''), 'email': email,
                   'filename': filename, 'pdf_url': download_url})

    if not email_sent and email:
        _telegram(
            f"⚠️ EMAIL NEREUȘIT\nClient: {prenume} | {email}\nCV: {cv} — {ARHETIPURI.get(cv,'')}\n"
            f"PDF atașat — trimite manual!",
            pdf_path=pdf_path
        )

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
        'pdf_path':     pdf_path,
    }
    return result


# ══════════════════════════════════════════════════════
#  RUTE PUBLICE
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
            log.info(f"[CONTACT] {name} <{email}> | {subject}")
            contacts_file = os.path.join(BASE_DIR, 'contacts.txt')
            with open(contacts_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\nData: {datetime.now():%d.%m.%Y %H:%M}\n"
                        f"Nume: {name}\nEmail: {email}\nSubiect: {subject}\nMesaj:\n{message}\n")
            _trimite_contact(name, email, subject, message)
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
        form_data    = {'prenume': prenume, 'data_nastere': data_nastere, 'cnp': cnp, 'email': email}

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

        # Stripe Checkout
        if STRIPE_SECRET_KEY:
            try:
                import stripe as _stripe
                _stripe.api_key = STRIPE_SECRET_KEY
                site = _get_site_url()
                cs = _stripe.checkout.Session.create(
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
                _log_payment(cs.id, 'checkout_created', {
                    'prenume': prenume, 'email': email, 'amount': STRIPE_PRICE_EUR
                })
                return redirect(cs.url)
            except Exception as e:
                log.error(f"Stripe checkout error: {e}")
                flash('Eroare la procesarea plății. Te rugăm să încerci din nou.', 'error')
                return render_template('genereaza.html', result=None, form_data=form_data,
                                       stripe_enabled=True, price=STRIPE_PRICE_EUR)

        # Generare directă (fără Stripe)
        try:
            result    = _genera_certificat_pentru(prenume, data_nastere, cnp, email)
            form_data = None
        except Exception as e:
            log.error(f"Generare directă eroare: {e}", exc_info=True)
            flash('A apărut o eroare la generarea certificatului. Te rugăm să încerci din nou.', 'error')

    return render_template('genereaza.html', result=result, form_data=form_data,
                           stripe_enabled=bool(STRIPE_SECRET_KEY), price=STRIPE_PRICE_EUR)


# ══════════════════════════════════════════════════════
#  STRIPE — SUCCES / ANULARE
# ══════════════════════════════════════════════════════

def _procesa_sesiune_stripe(session_id: str) -> dict:
    """
    Recuperează sesiunea Stripe, verifică plata și generează certificatul.
    Idempotent — nu regenerează dacă session_id a fost deja procesat.
    Ridică excepție la orice eroare.
    """
    if _is_session_processed(session_id):
        log.info(f"Session {session_id[:20]} deja procesată — skip.")
        return {'already_processed': True}

    import stripe as _stripe
    _stripe.api_key = STRIPE_SECRET_KEY
    cs = _stripe.checkout.Session.retrieve(session_id)

    payment_status = _meta_get(cs, 'payment_status') or getattr(cs, 'payment_status', '')
    if payment_status != 'paid':
        raise ValueError(f"Payment status: {payment_status}")

    meta         = getattr(cs, 'metadata', {})
    prenume      = _meta_get(meta, 'prenume')
    data_nastere = _meta_get(meta, 'data_nastere')
    cnp          = _meta_get(meta, 'cnp')
    email        = _meta_get(meta, 'email')

    if not data_nastere or not cnp:
        raise ValueError(f"Metadata incompletă: data_nastere={data_nastere!r}, cnp={cnp!r}")

    result = _genera_certificat_pentru(prenume, data_nastere, cnp, email, session_id=session_id)

    _log_payment(session_id, 'generated', {
        'prenume':      prenume,
        'data_nastere': data_nastere,
        'email':        email,
        'cifra_vietii': result['cifra_vietii'],
        'email_sent':   result['email_sent'],
        'pdf':          os.path.basename(result['pdf_path']),
    })

    _telegram(
        f"✅ PLATĂ + CERTIFICAT\n"
        f"👤 {prenume or 'anonim'} | CV: {result['cifra_vietii']} — {result['arhetip']}\n"
        f"📧 {email or 'fără email'}\n"
        f"💳 {session_id[:25]}..."
    )
    return result


@app.route('/payment/success')
def payment_success():
    session_id = request.args.get('session_id', '')
    if not session_id or not STRIPE_SECRET_KEY:
        return redirect(url_for('genereaza'))
    try:
        result = _procesa_sesiune_stripe(session_id)
        if result.get('already_processed'):
            flash('Certificatul tău a fost deja generat. Verifică emailul sau contactează-ne. ✦', 'success')
            return redirect(url_for('genereaza'))
        flash('Plată confirmată ✦ Certificatul tău a fost generat!', 'success')
        return render_template('genereaza.html', result=result, form_data=None,
                               stripe_enabled=True, price=STRIPE_PRICE_EUR)
    except Exception as e:
        log.error(f"Payment success error: {e}", exc_info=True)
        _log_payment(session_id, 'failed', {'error': str(e)})
        _telegram(
            f"🚨 PLATĂ EȘUATĂ LA GENERARE\n"
            f"Session: {session_id[:30]}\n"
            f"Eroare: {str(e)[:200]}\n\n"
            f"Retry: {SITE_URL}/admin/retry/{session_id}?key={ADMIN_KEY}"
        )
        flash(
            'Plata a fost înregistrată dar a apărut o eroare la generare. '
            'Am fost notificați și te vom contacta în maxim 24h. '
            'Sau scrie-ne la klara.aromaterapia@gmail.com',
            'error'
        )
        return redirect(url_for('genereaza'))


@app.route('/payment/cancel')
def payment_cancel():
    flash('Plata a fost anulată. Poți reîncerca oricând. ✦', 'error')
    return redirect(url_for('genereaza'))


# ══════════════════════════════════════════════════════
#  STRIPE WEBHOOK — backup când browserul se închide
# ══════════════════════════════════════════════════════

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    if not STRIPE_SECRET_KEY:
        return jsonify({'error': 'Stripe not configured'}), 400

    payload    = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        import stripe as _stripe
        _stripe.api_key = STRIPE_SECRET_KEY

        if STRIPE_WEBHOOK_SECRET:
            event = _stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            # Fără secret — parsăm direct (dev / înainte de configurare webhook)
            event = json.loads(payload)

        event_type = event.get('type', '') if isinstance(event, dict) else getattr(event, 'type', '')
        if event_type != 'checkout.session.completed':
            return jsonify({'status': 'ignored'}), 200

        cs_data = (event.get('data', {}).get('object', {})
                   if isinstance(event, dict)
                   else getattr(getattr(event, 'data', None), 'object', None))
        if not cs_data:
            return jsonify({'status': 'no_session'}), 200

        payment_status = (cs_data.get('payment_status', '') if isinstance(cs_data, dict)
                          else getattr(cs_data, 'payment_status', ''))
        if payment_status != 'paid':
            return jsonify({'status': 'not_paid'}), 200

        session_id = (cs_data.get('id', '') if isinstance(cs_data, dict)
                      else getattr(cs_data, 'id', ''))

        # Procesăm în thread separat pentru a returna rapid 200 la Stripe
        def _process():
            try:
                result = _procesa_sesiune_stripe(session_id)
                if not result.get('already_processed'):
                    log.info(f"Webhook: certificat generat | session={session_id[:20]}")
            except Exception as e:
                log.error(f"Webhook generare eroare: {e}", exc_info=True)
                _log_payment(session_id, 'webhook_failed', {'error': str(e)})
                _telegram(
                    f"🚨 WEBHOOK EȘUAT\nSession: {session_id[:30]}\nEroare: {str(e)[:200]}\n"
                    f"Retry: {SITE_URL}/admin/retry/{session_id}?key={ADMIN_KEY}"
                )

        threading.Thread(target=_process, daemon=True).start()
        return jsonify({'status': 'processing'}), 200

    except Exception as e:
        log.error(f"Stripe webhook error: {e}")
        return jsonify({'error': str(e)}), 400


# ══════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════

def _check_admin():
    key = request.args.get('key', '')
    if key != ADMIN_KEY:
        return False
    return True


@app.route('/admin/retry/<session_id>')
def admin_retry(session_id):
    if not _check_admin():
        return 'Unauthorized — adaugă ?key=ADMIN_KEY în URL', 403
    if not STRIPE_SECRET_KEY:
        return 'Stripe not configured', 500
    try:
        result = _procesa_sesiune_stripe(session_id)
        if result.get('already_processed'):
            return jsonify({'status': 'already_processed'})
        return jsonify({
            'status':       'ok',
            'cifra_vietii': result['cifra_vietii'],
            'arhetip':      result['arhetip'],
            'email_sent':   result['email_sent'],
            'download':     result['download_url'],
        })
    except Exception as e:
        log.error(f"Admin retry error: {e}", exc_info=True)
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/admin/dashboard')
def admin_dashboard():
    if not _check_admin():
        return 'Unauthorized — adaugă ?key=ADMIN_KEY în URL', 403

    payments = list(reversed(_load_payments()))
    stats = {'total': 0, 'generated': 0, 'failed': 0, 'checkout_created': 0}
    for p in payments:
        s = p.get('status', '')
        if s in stats:
            stats[s] += 1
        stats['total'] += 1

    rows = ''
    for p in payments[:100]:
        sid   = p.get('session_id', '')[:30]
        ts    = p.get('ts', '')[:16]
        stat  = p.get('status', '')
        pren  = p.get('prenume', '')
        email = p.get('email', '')
        cv    = p.get('cifra_vietii', '')
        err   = p.get('error', '')
        color = '#2ecc71' if stat == 'generated' else ('#e74c3c' if 'fail' in stat else '#f39c12')
        retry_btn = ''
        if 'fail' in stat and p.get('session_id', '').startswith('cs_'):
            full_sid = p.get('session_id', '')
            retry_btn = f'<a href="/admin/retry/{full_sid}?key={ADMIN_KEY}" style="background:#c9a84c;color:#280f50;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:bold;text-decoration:none;">RETRY</a>'
        rows += f'''<tr>
            <td style="color:#888;font-size:12px;">{ts}</td>
            <td><span style="background:{color};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">{stat}</span></td>
            <td>{pren}</td><td>{email}</td>
            <td style="font-weight:bold;color:#c9a84c;">{cv}</td>
            <td style="font-size:11px;color:#888;">{sid}...</td>
            <td style="font-size:11px;color:#e74c3c;">{err[:60]}</td>
            <td>{retry_btn}</td>
        </tr>'''

    html = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>GSIF Admin Dashboard</title>
    <style>
        body{{font-family:sans-serif;background:#0d0d0d;color:#e0e0e0;padding:2rem;}}
        h1{{color:#c9a84c;}} table{{width:100%;border-collapse:collapse;font-size:13px;}}
        th{{background:#1a1a2e;color:#c9a84c;padding:8px;text-align:left;}}
        td{{padding:7px 8px;border-bottom:1px solid #222;}}
        tr:hover td{{background:#1a1a1a;}}
        .stat{{display:inline-block;background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:1rem 1.5rem;margin:0.5rem;text-align:center;}}
        .stat .n{{font-size:2rem;color:#c9a84c;font-weight:bold;}} .stat .l{{font-size:12px;color:#888;}}
    </style></head><body>
    <h1>✦ GSIF — Admin Dashboard</h1>
    <div>
        <div class="stat"><div class="n">{stats['total']}</div><div class="l">Total înregistrări</div></div>
        <div class="stat"><div class="n" style="color:#2ecc71">{stats['generated']}</div><div class="l">Certificate generate</div></div>
        <div class="stat"><div class="n" style="color:#e74c3c">{stats['failed']}</div><div class="l">Eșuate</div></div>
        <div class="stat"><div class="n" style="color:#f39c12">{stats['checkout_created']}</div><div class="l">Checkout inițiat</div></div>
    </div>
    <h2 style="color:#c9a84c;margin-top:2rem;">Ultimele 100 plăți</h2>
    <table><thead><tr>
        <th>Data</th><th>Status</th><th>Prenume</th><th>Email</th>
        <th>CV</th><th>Session ID</th><th>Eroare</th><th>Acțiune</th>
    </tr></thead><tbody>{rows}</tbody></table>
    <p style="color:#555;margin-top:2rem;font-size:12px;">
        Retry manual: <code>/admin/retry/SESSION_ID?key={ADMIN_KEY}</code>
    </p>
    </body></html>'''
    return html


# ══════════════════════════════════════════════════════
#  DOWNLOAD
# ══════════════════════════════════════════════════════

@app.route('/download/<filename>')
def download_cert(filename):
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
            log.error(f"Supabase download error: {e}")
    flash('Certificatul nu a fost găsit. Te rugăm să contactezi suportul.', 'error')
    return redirect(url_for('genereaza'))


# ══════════════════════════════════════════════════════
#  API
# ══════════════════════════════════════════════════════

@app.route('/api/calculeaza', methods=['POST'])
def api_calculeaza():
    data     = request.get_json(silent=True) or {}
    data_str = data.get('data_nastere', '')
    cnp      = data.get('cnp', '')
    try:
        zi, luna, an = map(int, data_str.split('.'))
        cv  = calculeaza_cifra_vietii(zi, luna, an)
        return jsonify({
            'success': True,
            'cifra_vietii': cv,
            'arhetip':      ARHETIPURI.get(cv, ''),
            'misiune':      MISIUNI.get(cv, ''),
            'cifra_zi':     calculeaza_cifra_zilei(zi),
            'cifra_luna':   calculeaza_cifra_lunii(luna),
            'cifra_an':     calculeaza_cifra_anului(an),
            'contract':     calculeaza_contract(cnp) if len(cnp) >= 4 else None,
            'an_personal':  calculeaza_an_personal(zi, luna),
            'maestru':      cv in (11, 22, 33),
            'element':      ELEMENTE.get(cv, ''),
            'chakra':       CHAKRE.get(cv, ''),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/health')
def health():
    return jsonify({
        'status':   'ok',
        'app':      'GSIF',
        'version':  '2.0',
        'stripe':   bool(STRIPE_SECRET_KEY),
        'email':    bool(EMAIL_CONFIG['username'] and EMAIL_CONFIG['password']),
        'supabase': bool(SUPABASE_URL),
        'telegram': bool(TELEGRAM_BOT_TOKEN),
        'webhook_secret': bool(STRIPE_WEBHOOK_SECRET),
    })


@app.route('/api/counter')
def counter_api():
    return jsonify({'count': get_counter()})


@app.route('/sitemap.xml')
def sitemap():
    pages = ['', '/certificat', '/genereaza', '/manifest', '/despre', '/contact']
    base  = SITE_URL.rstrip('/')
    items = '\n'.join(
        f'  <url><loc>{base}{p}</loc><changefreq>weekly</changefreq>'
        f'<priority>{"1.0" if p == "" else "0.8"}</priority></url>'
        for p in pages
    )
    return Response(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                    f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>',
                    mimetype='application/xml')


@app.route('/robots.txt')
def robots():
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt')


@app.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')


# ══════════════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════════════

if __name__ == '__main__':
    port  = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    print()
    print("═" * 55)
    print("  ✦  GSIF — Global Spiritual Identity Foundation")
    print("      Every Soul Has a Map — v2.0")
    print("═" * 55)
    print(f"  URL:      http://localhost:{port}")
    print(f"  Stripe:   {'✅ ACTIV' if STRIPE_SECRET_KEY else '❌ DEZACTIVAT'}")
    print(f"  Email:    {'✅ ACTIV' if EMAIL_CONFIG['password'] else '❌ SMTP_PASS lipsă'}")
    print(f"  Telegram: {'✅ ACTIV' if TELEGRAM_BOT_TOKEN else '❌ dezactivat'}")
    print(f"  Webhook:  {'✅ cu secret' if STRIPE_WEBHOOK_SECRET else '⚠️ fără secret'}")
    print(f"  Admin:    http://localhost:{port}/admin/dashboard?key={ADMIN_KEY}")
    print("═" * 55)
    print()
    app.run(host='0.0.0.0', port=port, debug=debug)
