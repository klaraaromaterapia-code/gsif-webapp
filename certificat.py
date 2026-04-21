"""
GSIF — Global Spiritual Identity Foundation
Generator Certificat Numerologic — Single Page Premium v3.0
"Every Soul Has a Map"
"""

from fpdf import FPDF
from datetime import datetime
import os, sys, random, math

_DIR         = os.path.dirname(os.path.abspath(__file__))
_FONTS_DIR   = os.path.join(_DIR, "static", "fonts")
FONT_REGULAR = os.path.join(_FONTS_DIR, "arial.ttf")
FONT_BOLD    = os.path.join(_FONTS_DIR, "arialbd.ttf")
FONT_ITALIC  = os.path.join(_FONTS_DIR, "ariali.ttf")
FONT_FACE    = "Arial"
SIGNATURE_IMG = os.path.join(_DIR, "static", "signature.png")

# Paleta
C_BG      = (18,  4,  42)
C_BG2     = (36, 14,  68)
C_BG3     = (50, 20,  90)
C_GOLD    = (201, 168,  76)
C_LGOLD   = (238, 208, 128)
C_DGOLD   = (150, 120,  50)
C_TEXT    = (238, 228, 255)
C_TEXT2   = (168, 152, 208)
C_WHITE   = (255, 255, 255)
C_HBDR    = ( 46,  16,  88)
C_MAESTRU = (255, 215,  80)

# ── Tabele numerologice ───────────────────────────────────────────────────────

MISIUNI = {
    1:  "Liderul & Pionierul — initiaza, conduce si deschide drumuri noi.",
    2:  "Mediatorul — uneste, armonizeaza si construieste punti intre oameni.",
    3:  "Creatorul — inspira, exprima si aduce bucurie in lume prin arta.",
    4:  "Constructorul — edifice fundatii durabile cu rabdare si disciplina.",
    5:  "Exploratorul — traieste libertatea si aduce schimbarea necesara.",
    6:  "Vindecatorul — iubeste, ingrijeste si serveste cu devotament.",
    7:  "Inteleptul — cauta adevarul si se conecteaza cu Divinul.",
    8:  "Manifestantul — conduce in lumea materiala si manifesta abundenta.",
    9:  "Filantropul — serveste umanitatea si completeaza marile cicluri.",
    11: "NUMAR MAESTRU — Iluminatul, canal al Luminii Divine pentru trezire.",
    22: "NUMAR MAESTRU — Maestrul Constructor pentru intreaga umanitate.",
    33: "NUMAR MAESTRU — Maestrul Vindecator al colectivitatii.",
}

ARHETIPURI = {
    1: "Liderul / Pionierul",
    2: "Mediatorul / Partenerul",
    3: "Creatorul / Artistul",
    4: "Constructorul / Pragmaticul",
    5: "Exploratorul / Aventurierul",
    6: "Ingrijitorul / Vindecatorul",
    7: "Inteleptul / Misticul",
    8: "Magistrul / Manifestantul",
    9: "Filantropul / Umanistul",
    11: "Iluminatul / Mesagerul Divin",
    22: "Maestrul Constructor",
    33: "Maestrul Vindecator",
}

ELEMENTE = {
    1: "FOC",      2: "APA",      3: "AER",      4: "PAMANT",
    5: "ETER",     6: "APA",      7: "AER",      8: "PAMANT",
    9: "FOC",     11: "LUMINA",  22: "LUMINA",  33: "LUMINA",
}

CHAKRE = {
    1: "Radacina — Rosu",          2: "Sacral — Portocaliu",
    3: "Gatul — Albastru",         4: "Inima — Verde",
    5: "Gatul — Albastru",         6: "Inima — Verde",
    7: "Al 3-lea Ochi — Indigo",   8: "Coroana — Violet",
    9: "Coroana — Violet",        11: "Transpersonala — Alb Auriu",
   22: "Toate chakrele — Curcubeu",33: "Inima Cosmica — Roz Auriu",
}

CRISTALE = {
    1: "Rubin  *  Granat  *  Piatra Sangelui",
    2: "Piatra de Luna  *  Acvamarin  *  Roze Quartz",
    3: "Citrin  *  Ametist  *  Calcit Portocaliu",
    4: "Smarald  *  Jad  *  Turmalina Neagra",
    5: "Turcoaz  *  Lapis Lazuli  *  Acvamarin",
    6: "Roze Quartz  *  Aventurin Verde  *  Malachit",
    7: "Ametist  *  Lapis Lazuli  *  Selenit",
    8: "Pirita  *  Obsidian  *  Ochi de Tigru",
    9: "Ametist Violet  *  Fluorit  *  Sugilit",
   11: "Selenit  *  Diamant Herkimer  *  Opal Alb",
   22: "Labradorit  *  Piatra Soarelui  *  Alexandrit",
   33: "Roze Quartz  *  Danburit  *  Azeztulite",
}

CULORI = {
    1: "Rosu aprins  *  Auriu",      2: "Albastru pal  *  Argintiu",
    3: "Galben solar  *  Portocaliu",4: "Verde inchis  *  Maro pamantiu",
    5: "Turcoaz  *  Albastru electric",6:"Roz  *  Verde deschis",
    7: "Indigo  *  Violet",          8: "Negru  *  Auriu",
    9: "Violet  *  Alb",            11: "Alb Auriu  *  Indigo",
   22: "Auriu  *  Albastru regal",  33: "Roz Auriu  *  Alb pur",
}

PROFESII = {
    1:  "Antreprenoriat  *  Leadership  *  Sport  *  Armata",
    2:  "Diplomatie  *  Psihologie  *  Muzica  *  Mediere",
    3:  "Arte  *  Scriere  *  Publicitate  *  Coaching",
    4:  "Arhitectura  *  Inginerie  *  Drept  *  Administratie",
    5:  "Jurnalism  *  Turism  *  Vanzari  *  Marketing",
    6:  "Medicina  *  Asistenta sociala  *  Educatie  *  Nutritie",
    7:  "Cercetare  *  Filosofie  *  Spiritualitate  *  IT",
    8:  "Business  *  Finante  *  Management  *  Imobiliare",
    9:  "ONG  *  Arta sociala  *  Spiritualitate  *  Healing",
   11:  "Spiritualitate  *  Psihologie transpersonala  *  Vindecare",
   22:  "Arhitectura mondiala  *  Politica globala  *  Constructii",
   33:  "Terapie holistica  *  Spiritualitate inalta  *  Serviciu umanitar",
}

LECTII_KARMICE = {
    1: "Sa inveti colaborarea fara sa-ti pierzi independenta.",
    2: "Sa inveti curajul si sa te afirmi fara sa ranesti.",
    3: "Sa duci lucrurile la capat si sa construiesti disciplina.",
    4: "Sa inveti flexibilitatea si sa nu te rigidizezi in structuri.",
    5: "Sa inveti angajamentul si sa nu fugi de profunzime.",
    6: "Sa inveti sa te ingrijesti pe tine inainte de ceilalti.",
    7: "Sa ai incredere in viata si sa iesi din izolare.",
    8: "Sa folosesti puterea in serviciul colectivului.",
    9: "Sa inveti detasarea si sa lasi ciclurile sa se incheie.",
   11: "Sa iti asumi misiunea spirituala fara frica.",
   22: "Sa construiesti concret, nu doar sa visezi la scara mare.",
   33: "Sa vindeci mai intai ranile proprii pentru a vindeca cu adevarat.",
}

AFIRMATII = {
    1:  "Eu sunt Pionierul. Am curajul sa fiu primul si sa deschid drumuri noi.",
    2:  "Eu sunt Puntea. Armonia pe care o aduc incepe cu pacea din mine.",
    3:  "Eu sunt Creatorul. Prin expresia mea, lumea devine mai frumoasa.",
    4:  "Eu sunt Constructorul. Ceea ce construiesc dainuie peste generatii.",
    5:  "Eu sunt Exploratorul. Schimbarea pe care o aduc deschide orizonturi.",
    6:  "Eu sunt Vindecatorul. Iubirea mea este forta cea mai puternica.",
    7:  "Eu sunt Inteleptul. Adevarul pe care il caut ilumineaza calea altora.",
    8:  "Eu sunt Manifestantul. Abundenta pe care o creez serveste unui scop.",
    9:  "Eu sunt Filantropul. Daruind fara calcul, primesc mai mult decat am visat.",
   11:  "Eu sunt Iluminatul. Sunt canal al Luminii Divine pentru trezirea lumii.",
   22:  "Eu sunt Maestrul Constructor. Viziunile mele servesc intregii umanitati.",
   33:  "Eu sunt Maestrul Vindecator. Iubirea mea schimba lumea prin prezenta mea.",
}

CONTRACT_MESAJ = {
    1:  "Societatea iti cere sa fii lider si initiator al schimbarii.",
    2:  "Societatea iti cere sa fii mediator si constructor de punti.",
    3:  "Societatea iti cere sa fii creator si comunicator autentic.",
    4:  "Societatea iti cere sa fii constructor de structuri durabile.",
    5:  "Societatea iti cere sa fii agent al schimbarii si libertatii.",
    6:  "Societatea iti cere sa fii ingrijitor al familiei si comunitatii.",
    7:  "Societatea iti cere sa fii cercetator si impartasitor de adevar.",
    8:  "Societatea iti cere sa manifesti abundenta cu intelepciune.",
    9:  "Societatea iti cere sa servesti umanitatea si sa daruiesti.",
   11:  "Societatea iti cere sa fii un far spiritual pentru cei din jur.",
   22:  "Societatea iti cere sa construiesti la scara mare pentru generatii.",
   33:  "Societatea iti cere sa fii vindecatorul colectivitatii.",
}


# ── Calcule ───────────────────────────────────────────────────────────────────

def reduce_number(n, keep_master=True):
    while n > 9:
        if keep_master and n in (11, 22, 33):
            break
        n = sum(int(d) for d in str(n))
    return n

def calculeaza_cifra_vietii(zi, luna, an):
    return reduce_number(sum(int(d) for d in f"{zi:02d}{luna:02d}{an:04d}"))

def calculeaza_cifra_zilei(zi):
    return reduce_number(zi)

def calculeaza_cifra_lunii(luna):
    return reduce_number(luna)

def calculeaza_cifra_anului(an):
    return reduce_number(sum(int(d) for d in str(an)))

def calculeaza_contract(cod_fiscal):
    return reduce_number(sum(int(c) for c in str(cod_fiscal) if c.isdigit()))

def calculeaza_an_personal(zi, luna, an_curent=None):
    if an_curent is None:
        an_curent = datetime.now().year
    return reduce_number(sum(int(d) for d in f"{zi:02d}{luna:02d}{an_curent:04d}"))

def tensiune_descriere(viata, contract):
    if viata == contract:
        return "Armonie perfecta — natura ta si contractul social coincid."
    dif = abs(viata - contract)
    if dif <= 2:
        return "Armonie usoara — tensiune creativa care te forteaza sa cresti."
    if dif <= 5:
        return "Tensiune creativa — diferenta este sursa principalelor transformari."
    return "Tensiune puternica — rezolvarea contrastului reprezinta ascensiunea ta."

def nr_certificat(zi, luna, an):
    ts = datetime.now().strftime("%Y%m%d%H%M")
    return f"GSIF-{datetime.now().year}-{zi:02d}{luna:02d}{str(an)[-2:]}-{ts[-6:]}"


# ── Clasa PDF ─────────────────────────────────────────────────────────────────

class CertificatPDF(FPDF):
    PW = 210
    PH = 297
    M  = 12   # margine

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=False)
        self.add_font(FONT_FACE, '',  FONT_REGULAR)
        self.add_font(FONT_FACE, 'B', FONT_BOLD)
        self.add_font(FONT_FACE, 'I', FONT_ITALIC)

    def header(self):
        # Fundal cosmic
        self.set_fill_color(*C_BG)
        self.rect(0, 0, self.PW, self.PH, 'F')
        # Stele
        rng = random.Random(42)
        try:
            self.set_alpha(0.32)
        except Exception:
            pass
        self.set_fill_color(*C_WHITE)
        for _ in range(100):
            x = rng.uniform(self.M + 2, self.PW - self.M - 2)
            y = rng.uniform(self.M + 2, self.PH - self.M - 2)
            s = rng.choice([0.25, 0.35, 0.45, 0.55, 0.65])
            self.ellipse(x, y, s, s, 'F')
        try:
            self.set_alpha(1.0)
        except Exception:
            pass
        # Glow central subtil (nebula)
        try:
            self.set_alpha(0.10)
        except Exception:
            pass
        self.set_fill_color(100, 40, 180)
        self.ellipse(60, 60, 90, 60, 'F')
        try:
            self.set_alpha(1.0)
        except Exception:
            pass
        # Chenar dublu
        self.set_draw_color(*C_GOLD)
        self.set_line_width(1.8)
        self.rect(self.M - 5, self.M - 5, self.PW - 2*self.M + 10, self.PH - 2*self.M + 10)
        self.set_line_width(0.32)
        self.rect(self.M - 1.5, self.M - 1.5, self.PW - 2*self.M + 3, self.PH - 2*self.M + 3)
        # Ornamente colturi
        self.set_line_width(1.0)
        sz = 11
        for cx, cy, dx, dy in [
            (self.M + 2, self.M + 2,  1,  1),
            (self.PW - self.M - 2, self.M + 2, -1,  1),
            (self.M + 2, self.PH - self.M - 2,  1, -1),
            (self.PW - self.M - 2, self.PH - self.M - 2, -1, -1),
        ]:
            self.line(cx, cy, cx + dx*sz, cy)
            self.line(cx, cy, cx, cy + dy*sz)
        self.set_xy(self.M, self.M)

    def footer(self):
        yf = self.PH - self.M - 9
        self.set_draw_color(*C_GOLD)
        self.set_line_width(0.32)
        self.line(self.M + 3, yf, self.PW - self.M - 3, yf)
        self.set_font(FONT_FACE, 'I', 5.8)
        self.set_text_color(*C_TEXT2)
        self.set_xy(self.M, yf + 1.5)
        self.cell(0, 3.8,
            'Global Spiritual Identity Foundation (GSIF)  |  everysoulhasamap.org  |  "Every Soul Has a Map"',
            align='C')
        self.set_font(FONT_FACE, '', 5.2)
        self.set_xy(self.M, yf + 5.2)
        self.cell(0, 3.5,
            'Metodologie: Numerologie Pitagoreica Clasica  |  Document cu valoare spirituala si educationala',
            align='C')

    def hline(self, y, lw=0.38):
        self.set_draw_color(*C_GOLD)
        self.set_line_width(lw)
        self.line(self.M + 3, y, self.PW - self.M - 3, y)

    def card(self, x, y, w, h, bg=None):
        self.set_fill_color(*(bg or C_BG2))
        self.set_draw_color(*C_GOLD)
        self.set_line_width(0.25)
        self.rect(x, y, w, h, 'DF')

    def sec_bar(self, x, y, w, title, fs=6.5):
        h = 5.8
        self.set_fill_color(*C_HBDR)
        self.rect(x, y, w, h, 'F')
        self.set_fill_color(*C_GOLD)
        self.rect(x, y, 2.2, h, 'F')
        self.set_font(FONT_FACE, 'B', fs)
        self.set_text_color(*C_GOLD)
        self.set_xy(x + 2.5, y + 0.7)
        self.cell(w - 5, 4.5, title.upper(), align='C')

    def lv2(self, x, y, lbl, val, lw=38, fw=None, fs=6.5):
        """Label:Value pe doua campuri; returneaza y final."""
        fw = fw or (self.PW - self.M - x - lw)
        self.set_font(FONT_FACE, '', fs)
        self.set_text_color(*C_TEXT2)
        self.set_xy(x, y)
        self.cell(lw, 4.5, lbl + ':', ln=False)
        self.set_font(FONT_FACE, 'B', fs)
        self.set_text_color(*C_TEXT)
        self.set_xy(x + lw, y)
        self.multi_cell(fw, 4.5, str(val))
        return self.get_y()


# ── Generator ─────────────────────────────────────────────────────────────────

def genereaza_certificat(zi, luna, an, cod_fiscal, prenume='',
                         output_dir=None, filename_suffix=''):
    """Genereaza Certificatul Numerologic pe O SINGURA PAGINA A4 si returneaza calea."""

    cv  = calculeaza_cifra_vietii(zi, luna, an)
    czz = calculeaza_cifra_zilei(zi)
    cl  = calculeaza_cifra_lunii(luna)
    ca  = calculeaza_cifra_anului(an)
    cc  = calculeaza_contract(cod_fiscal)
    ap  = calculeaza_an_personal(zi, luna)
    nr  = nr_certificat(zi, luna, an)

    data_nastere  = f"{zi:02d}.{luna:02d}.{an}"
    data_emitere  = datetime.now().strftime("%d.%m.%Y")
    tensiune      = tensiune_descriere(cv, cc)
    maestru_cv    = cv in (11, 22, 33)
    maestru_cc    = cc in (11, 22, 33)
    maestru_ca    = ca in (11, 22, 33)
    maestru_ap    = ap in (11, 22, 33)

    pdf = CertificatPDF()
    pdf.add_page()

    M   = pdf.M
    PW  = pdf.PW
    CW  = PW - 2 * M        # 186 mm latime continut
    CX  = M                 # 12 mm x start

    # ─── ANTET GSIF ──────────────────────────────────────────────────────────
    # Banda superioara aurie + text
    pdf.set_fill_color(*C_BG3)
    pdf.rect(CX, M, CW, 8, 'F')
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(CX, M, CW, 1.5, 'F')
    pdf.rect(CX, M + 6.5, CW, 1.5, 'F')
    pdf.set_font(FONT_FACE, 'B', 7)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(CX, M + 1.8)
    pdf.cell(CW, 4.5, 'El  *  G S I F   *   G L O B A L   S P I R I T U A L   I D E N T I T Y   F O U N D A T I O N', align='C')

    # ─── TITLUL CERTIFICATULUI ────────────────────────────────────────────────
    pdf.set_font(FONT_FACE, 'B', 14)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(CX, M + 11)
    pdf.cell(CW, 7.5, 'CERTIFICATUL NUMEROLOGIC AL VIETII', align='C')

    pdf.set_font(FONT_FACE, 'I', 7.5)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(CX, M + 19)
    pdf.cell(CW, 5, '"Documentul Sacru al Sufletului  *  Every Soul Has a Map"', align='C')

    pdf.hline(M + 25, lw=0.55)

    # ─── DATE IDENTIFICARE ────────────────────────────────────────────────────
    pdf.set_font(FONT_FACE, '', 6.8)
    pdf.set_text_color(*C_TEXT2)
    Y_ID = M + 27
    pdf.set_xy(CX + 3, Y_ID)
    if prenume:
        pdf.cell(50, 4.5, f'Titular:  {prenume}', ln=False)
    else:
        pdf.cell(50, 4.5, '', ln=False)
    pdf.set_xy(CX + CW//2 - 20, Y_ID)
    pdf.cell(40, 4.5, f'Data nasterii:  {data_nastere}', ln=False)
    pdf.set_xy(CX + CW - 2, Y_ID)
    pdf.cell(0, 4.5, f'Nr: {nr}  |  Emis: {data_emitere}', align='R')

    pdf.hline(M + 33, lw=0.35)

    # ─── NUMARUL VIETII — cercul sacru central ────────────────────────────────
    Y_HERO = M + 36
    cx_c   = PW / 2        # centru orizontal
    cy_c   = Y_HERO + 14   # centru cerc
    r      = 12.5

    # Glow
    try:
        pdf.set_alpha(0.18)
    except Exception:
        pass
    pdf.set_fill_color(140, 60, 210)
    pdf.ellipse(cx_c - r - 7, cy_c - r - 7, 2*(r + 7), 2*(r + 7), 'F')
    try:
        pdf.set_alpha(1.0)
    except Exception:
        pass
    # Cerc principal
    pdf.set_fill_color(*C_BG3)
    pdf.set_draw_color(*C_GOLD)
    pdf.set_line_width(1.4)
    pdf.ellipse(cx_c - r, cy_c - r, 2*r, 2*r, 'DF')
    pdf.set_line_width(0.3)
    pdf.ellipse(cx_c - r + 2.5, cy_c - r + 2.5, 2*r - 5, 2*r - 5)

    # Numar mare
    fs_n = 28 if cv < 10 else 22
    pdf.set_font(FONT_FACE, 'B', fs_n)
    pdf.set_text_color(*C_MAESTRU if maestru_cv else C_LGOLD)
    num_h = fs_n / 2.835
    pdf.set_xy(cx_c - r, cy_c - num_h / 2)
    pdf.cell(2 * r, num_h, str(cv), align='C')

    # Eticheta sub cerc
    pdf.set_font(FONT_FACE, 'B', 6.5)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(CX, cy_c + r + 1.5)
    pdf.cell(CW, 5, 'CIFRA VIETII (LIFE PATH NUMBER)', align='C')

    # Arhetip
    pdf.set_font(FONT_FACE, 'I', 8.5)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(CX, cy_c + r + 7)
    arh_txt = ARHETIPURI.get(cv, '')
    if maestru_cv:
        arh_txt = '*** NUMAR MAESTRU ***  ' + arh_txt
    pdf.cell(CW, 5.5, arh_txt, align='C')

    # Misiunea (sub arhetip)
    pdf.set_font(FONT_FACE, 'I', 7.2)
    pdf.set_text_color(*C_TEXT2)
    pdf.set_xy(CX + 15, cy_c + r + 13.5)
    pdf.multi_cell(CW - 30, 4.5, MISIUNI.get(cv, ''), align='C')

    pdf.hline(cy_c + r + 23, lw=0.5)

    # ─── GRILA PRINCIPALA — 3 coloane x 2 randuri ────────────────────────────
    Y_GRID = cy_c + r + 26

    GAP   = 2.5
    COL3  = (CW - 2 * GAP) / 3     # ~59.8 mm per coloana
    ROW_H = 26                      # inaltime rand

    def mini_card(col_idx, row_idx, title, rows_data):
        """Deseneaza un mini-card in grila 3x2."""
        x = CX + col_idx * (COL3 + GAP)
        y = Y_GRID + row_idx * (ROW_H + GAP)
        pdf.card(x, y, COL3, ROW_H)
        pdf.sec_bar(x, y, COL3, title, fs=5.8)
        for i, (lbl, val) in enumerate(rows_data):
            pdf.set_font(FONT_FACE, '', 5.8)
            pdf.set_text_color(*C_TEXT2)
            pdf.set_xy(x + 2.5, y + 7 + i * 6)
            pdf.cell(22, 4, lbl + ':', ln=False)
            pdf.set_font(FONT_FACE, 'B', 5.8)
            pdf.set_text_color(*C_TEXT)
            pdf.set_xy(x + 24.5, y + 7 + i * 6)
            pdf.multi_cell(COL3 - 27, 4, str(val))

    # Rand 1
    mini_card(0, 0, 'Cifra Zilei — Talent Nativ', [
        ('Cifra', str(czz)),
        ('Arhetip', ARHETIPURI.get(czz, '')),
        ('Element', ELEMENTE.get(czz, '')),
    ])
    mini_card(1, 0, 'Cifra Lunii — Lectie Emotionala', [
        ('Cifra', str(cl)),
        ('Arhetip', ARHETIPURI.get(cl, '')),
        ('Chakra', CHAKRE.get(cl, '')),
    ])
    mini_card(2, 0, 'Cifra Anului Nasterii', [
        ('Cifra', f'{ca}' + (' *** MAESTRU ***' if maestru_ca else '')),
        ('Arhetip', ARHETIPURI.get(ca, '')),
        ('Culori', CULORI.get(ca, '')),
    ])

    # Rand 2
    mini_card(0, 1, 'Contract Social', [
        ('Cifra', f'{cc}' + (' *** MAESTRU ***' if maestru_cc else '')),
        ('Mesaj', CONTRACT_MESAJ.get(cc, '')),
        ('Tensiune', tensiune),
    ])
    mini_card(1, 1, 'Chakra  &  Cristale', [
        ('Chakra', CHAKRE.get(cv, '')),
        ('Cristale', CRISTALE.get(cv, '')),
        ('Element', ELEMENTE.get(cv, '')),
    ])
    mini_card(2, 1, f'An Personal {datetime.now().year}', [
        ('Cifra', f'{ap}' + (' *** MAESTRU ***' if maestru_ap else '')),
        ('Arhetip', ARHETIPURI.get(ap, '')),
        ('Profesii', PROFESII.get(cv, '')),
    ])

    # ─── AFIRMATIA SACRA ──────────────────────────────────────────────────────
    Y_AFF = Y_GRID + 2 * (ROW_H + GAP) + 3

    AFF_H = 19
    pdf.set_fill_color(44, 16, 82)
    pdf.set_draw_color(*C_GOLD)
    pdf.set_line_width(0.9)
    pdf.rect(CX, Y_AFF, CW, AFF_H, 'DF')
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(CX, Y_AFF, CW, 1.8, 'F')
    pdf.rect(CX, Y_AFF + AFF_H - 1.8, CW, 1.8, 'F')

    pdf.set_font(FONT_FACE, 'B', 6.2)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(CX, Y_AFF + 2.5)
    pdf.cell(CW, 4.5, 'AFIRMATIA SACRA A VIETII TALE', align='C')

    pdf.set_font(FONT_FACE, 'I', 8.2)
    pdf.set_text_color(*C_WHITE)
    pdf.set_xy(CX + 8, Y_AFF + 7.5)
    pdf.multi_cell(CW - 16, 5, f'"{AFIRMATII.get(cv, "")}"', align='C')

    # ─── SEMNATURA ────────────────────────────────────────────────────────────
    Y_SIG = Y_AFF + AFF_H + 3

    SIG_H  = 24
    LEFT_W = CW * 0.52

    # Linie superioara semnatura
    pdf.set_draw_color(*C_GOLD)
    pdf.set_line_width(0.32)
    pdf.line(CX, Y_SIG, CX + CW, Y_SIG)

    # Semnatura stanga
    if os.path.exists(SIGNATURE_IMG):
        try:
            pdf.image(SIGNATURE_IMG, x=CX + 4, y=Y_SIG + 3, h=13)
        except Exception:
            pass
        sig_name_y = Y_SIG + 18
    else:
        pdf.set_font(FONT_FACE, 'I', 14)
        pdf.set_text_color(*C_LGOLD)
        pdf.set_xy(CX + 4, Y_SIG + 4)
        pdf.cell(LEFT_W - 8, 9, 'KLARA V.D.')
        sig_name_y = Y_SIG + 15

    # Linie pentru semnatura
    pdf.set_draw_color(*C_DGOLD)
    pdf.set_line_width(0.3)
    pdf.line(CX + 4, sig_name_y - 0.5, CX + LEFT_W - 4, sig_name_y - 0.5)

    pdf.set_font(FONT_FACE, '', 6)
    pdf.set_text_color(*C_TEXT2)
    pdf.set_xy(CX + 4, sig_name_y + 1)
    pdf.cell(LEFT_W - 8, 4, 'KLARA V.D.  |  Fondatoare GSIF')
    pdf.set_xy(CX + 4, sig_name_y + 5)
    pdf.cell(LEFT_W - 8, 4, 'k****a@gmail.com')

    # Sigiliu dreapta
    RX_SIG = CX + LEFT_W + 4
    RW_SIG = CW - LEFT_W - 4

    # Cerc sigiliu
    cx_sig = RX_SIG + RW_SIG / 2
    cy_sig = Y_SIG + SIG_H / 2
    r_sig  = 9
    pdf.set_draw_color(*C_GOLD)
    pdf.set_line_width(0.8)
    pdf.set_fill_color(*C_BG3)
    pdf.ellipse(cx_sig - r_sig, cy_sig - r_sig, 2*r_sig, 2*r_sig, 'DF')
    pdf.set_line_width(0.25)
    pdf.ellipse(cx_sig - r_sig + 1.5, cy_sig - r_sig + 1.5, 2*r_sig - 3, 2*r_sig - 3)

    pdf.set_font(FONT_FACE, 'B', 6)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(cx_sig - r_sig, cy_sig - 5)
    pdf.cell(2*r_sig, 4, 'GSIF', align='C')
    pdf.set_font(FONT_FACE, '', 4.8)
    pdf.set_text_color(*C_TEXT2)
    pdf.set_xy(cx_sig - r_sig, cy_sig - 1.5)
    pdf.cell(2*r_sig, 3.5, '* CERTIFICAT *', align='C')
    pdf.set_xy(cx_sig - r_sig, cy_sig + 1.8)
    pdf.cell(2*r_sig, 3.5, 'SPIRITUAL', align='C')
    pdf.set_xy(cx_sig - r_sig, cy_sig + 5)
    pdf.cell(2*r_sig, 3.5, data_emitere, align='C')

    pdf.line(CX, Y_SIG + SIG_H, CX + CW, Y_SIG + SIG_H)

    # ─── LECTIA KARMICA (banda finala subtila) ────────────────────────────────
    Y_LK = Y_SIG + SIG_H + 2
    LK_H = 9
    pdf.set_fill_color(*C_HBDR)
    pdf.rect(CX, Y_LK, CW, LK_H, 'F')
    pdf.set_font(FONT_FACE, 'B', 5.8)
    pdf.set_text_color(*C_GOLD)
    pdf.set_xy(CX, Y_LK + 1.2)
    pdf.cell(CW, 3.8, f'Lectia Karmica: {LECTII_KARMICE.get(cv,"")}', align='C')
    pdf.set_font(FONT_FACE, '', 5.5)
    pdf.set_text_color(*C_TEXT2)
    pdf.set_xy(CX, Y_LK + 5)
    pdf.cell(CW, 3.5, f'Profesii armonioase: {PROFESII.get(cv,"")}', align='C')

    # ─── Salvare ──────────────────────────────────────────────────────────────
    if output_dir is None:
        output_dir = _DIR
    os.makedirs(output_dir, exist_ok=True)
    fn = f"Certificat_GSIF_{zi:02d}{luna:02d}{an}{filename_suffix}.pdf"
    fp = os.path.join(output_dir, fn)
    pdf.output(fp)
    return fp


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  GSIF — Generator Certificat Numerologic v3.0")
    print("  Single Page Premium Design")
    print("="*60 + "\n")

    if len(sys.argv) >= 3:
        data_str = sys.argv[1]
        cod_fisc = sys.argv[2]
        prenume  = sys.argv[3] if len(sys.argv) > 3 else ''
    else:
        data_str = input("  Data nasterii (ZZ.LL.AAAA): ").strip()
        cod_fisc = input("  Cod Fiscal / CNP:           ").strip()
        prenume  = input("  Prenume (optional):          ").strip()

    try:
        zi, luna, an = map(int, data_str.split('.'))
    except Exception:
        print("  [EROARE] Format incorect. Foloseste ZZ.LL.AAAA")
        sys.exit(1)

    out_dir  = os.path.join(_DIR, "certificate_generate")
    filepath = genereaza_certificat(zi, luna, an, cod_fisc, prenume=prenume, output_dir=out_dir)

    cv = calculeaza_cifra_vietii(zi, luna, an)
    print(f"\n  Cifra Vietii: {cv} — {ARHETIPURI.get(cv,'')}")
    print(f"  Salvat: {filepath}\n")
    print("  'Every Soul Has a Map'\n" + "="*60)

    if sys.platform == 'win32':
        os.startfile(filepath)
    return filepath


if __name__ == '__main__':
    main()
