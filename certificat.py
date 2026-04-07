"""
GSIF — Global Spiritual Identity Foundation
Generator Certificat Numerologic al Vietii
Versiunea 1.0 — Aprilie 2026
"Every Soul Has a Map"
"""

from fpdf import FPDF
from datetime import datetime
import os
import sys

FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD    = "C:/Windows/Fonts/arialbd.ttf"
FONT_ITALIC  = "C:/Windows/Fonts/ariali.ttf"

# ─────────────────────────────────────────────
#  DATE BAZA — TABELE NUMEROLOGICE
# ─────────────────────────────────────────────

MISIUNI = {
    1:  "Liderul & Pionierul — ai venit sa initiezi, sa conduci si sa deschizi drumuri noi.",
    2:  "Diplomatoul & Mediatorul — ai venit sa unesti, sa armonizezi si sa construiesti punti.",
    3:  "Creatorul & Exprimantul — ai venit sa creezi, sa inspiri si sa aduci bucurie in lume.",
    4:  "Constructorul & Organizatorul — ai venit sa construiesti fundatii durabile si ordine.",
    5:  "Exploratorul & Eliberatorul — ai venit sa traiesti libertatea si sa aduci schimbarea.",
    6:  "Vindecatorul & Ingrijitorul — ai venit sa iubesti, sa vindeci si sa servesti familia.",
    7:  "Inteleptul & Cautatorul — ai venit sa cauti adevarul si sa te conectezi cu Divinul.",
    8:  "Magistrul & Manifestantul — ai venit sa conduci in lumea materiala si sa manifesti abundenta.",
    9:  "Filantropul & Umanistul — ai venit sa servesti umanitatea si sa completezi cicluri.",
    11: "NUMAR MAESTRU — Iluminatul & Mesagerul — canal al Luminii Divine pentru trezirea colectiva.",
    22: "NUMAR MAESTRU — Maestrul Constructor — ai venit sa construiesti pentru intreaga umanitate.",
    33: "NUMAR MAESTRU — Maestrul Vindecator — ai venit sa vindeci colectiv si sa iubesti neconditionat.",
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
    1: "FOC — Pasiune, initiativa, transformare",
    2: "APA — Emotie, intuitie, vindecare",
    3: "AER — Minte, comunicare, libertate",
    4: "PAMANT — Stabilitate, materializare, rabdare",
    5: "ETER — Schimbare, libertate totala, conexiune divina",
    6: "APA — Iubire, ingrijire, armonie",
    7: "AER — Profunzime, analiza, cautare",
    8: "PAMANT — Putere, structura, manifestare",
    9: "FOC — Compasiune universala, finaluri, transformare",
    11: "LUMINA — Misiune superioara, canal divin",
    22: "LUMINA — Viziune si constructie la scara planetara",
    33: "LUMINA — Iubire divina si vindecare universala",
}

CHAKRE = {
    1: "Radacina (Muladhara) — Rosu — Siguranta si fundament",
    2: "Sacral (Svadhisthana) — Portocaliu — Creativitate si emotie",
    3: "Gatul (Vishuddha) — Albastru — Expresie si comunicare",
    4: "Inima (Anahata) — Verde — Iubire si compasiune",
    5: "Gatul (Vishuddha) — Albastru — Expresie si libertate",
    6: "Inima (Anahata) — Verde — Iubire si serviciu",
    7: "Al 3-lea Ochi (Ajna) — Indigo — Intuitie si viziune",
    8: "Coroana (Sahasrara) — Violet — Putere si constiinta",
    9: "Coroana (Sahasrara) — Violet — Constiinta universala",
    11: "Transpersonala — Alb Auriu — Canal divin pur",
    22: "Toate chakrele active — Curcubeu — Maestrul integrat",
    33: "Inima Cosmica — Roz Auriu — Iubire divina suprema",
}

CRISTALE = {
    1: "Rubin • Granat • Piatra Sangelui",
    2: "Piatra de Luna • Acvamarin • Roze Quartz",
    3: "Citrin • Ametist • Calcit Portocaliu",
    4: "Smarald • Jad • Turmalina Neagra",
    5: "Turcoaz • Lapis Lazuli • Acvamarin",
    6: "Roze Quartz • Aventurin Verde • Malachit",
    7: "Ametist • Lapis Lazuli • Selenit",
    8: "Pirita • Obsidian • Ochi de Tigru",
    9: "Ametist Violet • Fluorit • Sugilit",
    11: "Selenit • Diamant Herkimer • Opal Alb",
    22: "Labradorit • Piatra Soarelui • Alexandrit",
    33: "Roze Quartz • Danburit • Azeztulite",
}

CULORI = {
    1: "Rosu aprins • Auriu",
    2: "Albastru pal • Argintiu",
    3: "Galben solar • Portocaliu",
    4: "Verde inchis • Maro pamantiu",
    5: "Turcoaz • Albastru electric",
    6: "Roz • Verde deschis",
    7: "Indigo • Violet",
    8: "Negru • Auriu",
    9: "Violet • Alb",
    11: "Alb Auriu • Indigo",
    22: "Auriu • Albastru regal",
    33: "Roz Auriu • Alb pur",
}

PROFESII = {
    1:  "Antreprenoriat • Leadership • Sport de performanta • Armata • Explorare",
    2:  "Diplomatie • Psihologie • Muzica • Resurse Umane • Mediere",
    3:  "Arte • Scriere • Jurnalism • Publicitate • Entertainment • Coaching",
    4:  "Arhitectura • Inginerie • Contabilitate • Drept • Administratie",
    5:  "Jurnalism investigativ • Turism • Vanzari • Marketing • Diplomatie",
    6:  "Medicina • Asistenta sociala • Educatie • Nutritie • Design Interior",
    7:  "Cercetare • Filosofie • Spiritualitate • IT • Investigatii • Analiza",
    8:  "Business • Finante • Management • Politica • Imobiliare • Banca",
    9:  "ONG • Arta cu impact social • Spiritualitate • Filosofie • Healing",
    11: "Spiritualitate • Psihologie transpersonala • Arta sacra • Vindecare",
    22: "Arhitectura mondiala • Politica globala • Constructii la scara mare",
    33: "Terapie holistica • Spiritualitate inalta • Serviciu umanitar global",
}

LECTII_KARMICE = {
    1:  "Sa inveti sa colaborezi fara sa pierzi independenta.",
    2:  "Sa inveti sa ai curaj si sa te afirmi fara sa ranesti.",
    3:  "Sa duci lucrurile la capat si sa construiesti disciplina.",
    4:  "Sa inveti flexibilitatea si sa nu te rigidizezi in structuri.",
    5:  "Sa inveti angajamentul si sa nu fugi de profunzime.",
    6:  "Sa inveti sa te ingrijesti pe tine inainte de ceilalti.",
    7:  "Sa ai incredere in viata si sa iesi din izolare.",
    8:  "Sa folosesti puterea in serviciul colectivului, nu al egului.",
    9:  "Sa inveti detasarea si sa lasi ciclurile sa se incheie natural.",
    11: "Sa iti asumi misiunea spirituala fara frica de vizibilitate.",
    22: "Sa construiesti concret, nu doar sa visezi la scara mare.",
    33: "Sa vindeci mai intai ranile proprii pentru a vindeca cu adevarat.",
}

AFIRMATII = {
    1:  "Eu sunt Pionierul. Am curajul sa fiu primul si sa deschid drumuri noi pentru ceilalti.",
    2:  "Eu sunt Puntea. Armonia pe care o aduc in lume incepe cu pacea din interiorul meu.",
    3:  "Eu sunt Creatorul Iluminat. Prin expresia mea, lumea devine mai frumoasa si mai constienta.",
    4:  "Eu sunt Constructorul. Ceea ce construiesc cu rabdare si dedicare dainuie peste generatii.",
    5:  "Eu sunt Exploratorul Liber. Schimbarea pe care o aduc deschide noi orizonturi pentru umanitate.",
    6:  "Eu sunt Vindecatorul. Iubirea pe care o ofer este forta cea mai puternica din univers.",
    7:  "Eu sunt Inteleptul. Adevarul pe care il caut ilumineaza calea altora spre lumina.",
    8:  "Eu sunt Manifestantul. Abundenta pe care o creez serveste unui scop mai mare decat mine.",
    9:  "Eu sunt Filantropul. Daruind fara calcul, primesc mai mult decat am visat.",
    11: "Eu sunt Iluminatul. Sunt canal al Luminii Divine si misiunea mea este sa trezesc sufletele lumii.",
    22: "Eu sunt Maestrul Constructor. Viziunile mele devin realitate si servesc intregii umanitati.",
    33: "Eu sunt Maestrul Vindecator. Iubirea mea neconditionale schimba lumea prin simplul fapt ca exist.",
}

CONTRACT_MESAJ = {
    1:  "Societatea iti cere sa fii un lider si un initiator. Sa deschizi drumuri, nu sa urmezi turma.",
    2:  "Societatea iti cere sa fii un mediator. Sa construiesti punti si sa aduci armonie in colectiv.",
    3:  "Societatea iti cere sa fii un creator si un comunicator. Sa inspiri prin expresia ta autentica.",
    4:  "Societatea iti cere sa fii un constructor si un organizator. Sa creezi structuri durabile.",
    5:  "Societatea iti cere sa fii un agent al schimbarii. Sa aduci adaptabilitate si libertate.",
    6:  "Societatea iti cere sa fii un ingrijitor. Sa servesti familia si comunitatea cu iubire.",
    7:  "Societatea iti cere sa fii un cercetator al adevarului. Sa cauti si sa impartasesti intelepciunea.",
    8:  "Societatea iti cere sa fii un conductor in lumea materiala. Sa manifesti abundenta cu intelepciune.",
    9:  "Societatea iti cere sa fii un servant al umanissimului. Sa completezi cicluri si sa dăruiești.",
    11: "Societatea iti cere ceva EXCEPTIONAL: sa fii un far spiritual pentru cei din jur.",
    22: "Societatea iti cere ceva EXCEPTIONAL: sa construiesti la scara mare pentru generatii.",
    33: "Societatea iti cere ceva EXCEPTIONAL: sa fii un vindecator al colectivitatii.",
}


# ─────────────────────────────────────────────
#  CALCULE NUMEROLOGICE
# ─────────────────────────────────────────────

def reduce_number(n, keep_master=True):
    """Reduce un numar la o singura cifra, pastrand numerele maestru 11, 22, 33."""
    while n > 9:
        if keep_master and n in (11, 22, 33):
            break
        n = sum(int(d) for d in str(n))
    return n

def calculeaza_cifra_vietii(zi, luna, an):
    total = sum(int(d) for d in f"{zi:02d}{luna:02d}{an:04d}")
    return reduce_number(total)

def calculeaza_cifra_zilei(zi):
    return reduce_number(zi)

def calculeaza_cifra_lunii(luna):
    return reduce_number(luna)

def calculeaza_cifra_anului(an):
    total = sum(int(d) for d in str(an))
    return reduce_number(total)

def calculeaza_contract(cod_fiscal):
    """Calculeaza cifra contractului social din codul fiscal/CNP."""
    cifre = [int(c) for c in str(cod_fiscal) if c.isdigit()]
    total = sum(cifre)
    return reduce_number(total)

def calculeaza_an_personal(zi, luna, an_curent=None):
    if an_curent is None:
        an_curent = datetime.now().year
    total = sum(int(d) for d in f"{zi:02d}{luna:02d}{an_curent:04d}")
    return reduce_number(total)

def tensiune_descriere(viata, contract):
    if viata == contract:
        return "ARMONIE PERFECTA — Natura ta si contractul social coincid. Calea ta este clara si aliniata."
    dif = abs(viata - contract)
    if dif <= 2:
        return "ARMONIE USOARA — Exista o tensiune creativa intre natura ta si asteptarile sociale. Aceasta te forteaza sa cresti."
    if dif <= 5:
        return "TENSIUNE CREATIVA — Diferenta dintre natura ta si contractul social este sursa principalelor tale lectii si trasformari."
    return "TENSIUNE PUTERNICA — Contrastul dintre cine esti si ce cere lumea este lectia fundamentala a vietii tale. Rezolvarea ei = ascensiunea ta."

def nr_certificat(zi, luna, an):
    ts = datetime.now().strftime("%Y%m%d%H%M")
    return f"GSIF-{datetime.now().year}-{zi:02d}{luna:02d}{str(an)[-2:]}-{ts[-6:]}"


# ─────────────────────────────────────────────
#  GENERARE PDF
# ─────────────────────────────────────────────

class CertificatPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(auto=True, margin=25)
        self.add_font("Arial",  "",  FONT_REGULAR)
        self.add_font("Arial",  "B", FONT_BOLD)
        self.add_font("Arial",  "I", FONT_ITALIC)

    def header(self):
        # Linie aurie sus
        self.set_draw_color(201, 168, 76)  # auriu
        self.set_line_width(1.0)
        self.line(15, 12, 195, 12)
        self.set_line_width(0.3)
        self.line(15, 15, 195, 15)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(201, 168, 76)
        self.set_line_width(0.3)
        self.line(15, -15, 195, -15)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(150, 130, 80)
        self.cell(0, 5, 'Global Spiritual Identity Foundation (GSIF)  |  "Every Soul Has a Map"  |  gsif.org', align='C')

    def titlu_sectiune(self, text):
        self.ln(4)
        self.set_fill_color(40, 15, 80)  # violet inchis
        self.set_text_color(201, 168, 76)  # auriu
        self.set_font('Arial', 'B', 9)
        self.cell(0, 7, f'  {text.upper()}', fill=True, ln=True)
        self.ln(2)
        self.set_text_color(30, 30, 30)

    def rand_info(self, eticheta, valoare, bold_val=True):
        lbl_w = 62
        val_w = 108
        self.set_font('Arial', 'B', 8)
        self.set_text_color(80, 60, 120)
        self.cell(lbl_w, 6, eticheta + ':', ln=False)
        self.set_font('Arial', 'B' if bold_val else '', 8)
        self.set_text_color(20, 20, 20)
        x_save = self.get_x()
        self.multi_cell(val_w, 6, valoare)
        self.set_x(20)

    def text_bloc(self, text, italic=False):
        self.set_font('Arial', 'I' if italic else '', 8)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(1)


def genereaza_certificat(zi, luna, an, cod_fiscal, output_dir=None):
    """
    Genereaza Certificatul Numerologic al Vietii ca PDF.
    Returneaza calea catre fisierul generat.
    """

    # ── Calcule ──────────────────────────────
    cv  = calculeaza_cifra_vietii(zi, luna, an)
    czz = calculeaza_cifra_zilei(zi)
    cl  = calculeaza_cifra_lunii(luna)
    ca  = calculeaza_cifra_anului(an)
    cc  = calculeaza_contract(cod_fiscal)
    ap  = calculeaza_an_personal(zi, luna)
    nr  = nr_certificat(zi, luna, an)

    data_nastere = f"{zi:02d}.{luna:02d}.{an}"
    data_emitere = datetime.now().strftime("%d.%m.%Y")
    tensiune     = tensiune_descriere(cv, cc)

    maestru_cv = cv in (11, 22, 33)
    maestru_cc = cc in (11, 22, 33)
    maestru_ca = ca in (11, 22, 33)

    # ── PDF ──────────────────────────────────
    pdf = CertificatPDF()
    pdf.add_page()

    # ── ANTET ─────────────────────────────────
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(40, 15, 80)
    pdf.ln(8)
    pdf.cell(0, 10, 'CERTIFICATUL NUMEROLOGIC AL VIETII', align='C', ln=True)

    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(201, 168, 76)
    pdf.cell(0, 6, 'Documentul Sacru al Sufletului', align='C', ln=True)

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(120, 100, 160)
    pdf.cell(0, 5, '"Every Soul Has a Map"', align='C', ln=True)
    pdf.ln(3)

    # Linie decorativa
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    # Date identificare
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(95, 5, f'Data nasterii: {data_nastere}', align='L', ln=False)
    pdf.cell(95, 5, f'Nr. Certificat: {nr}', align='R', ln=True)
    pdf.cell(95, 5, f'Cod Fiscal: {"*" * (len(str(cod_fiscal))-3) + str(cod_fiscal)[-3:]}', align='L', ln=False)
    pdf.cell(95, 5, f'Data emiterii: {data_emitere}', align='R', ln=True)
    pdf.ln(2)

    pdf.set_draw_color(201, 168, 76)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())

    # ── SEC 1: IDENTITATE SACRA ───────────────
    pdf.titlu_sectiune('I. Identitatea Sacra')

    maestru_txt = "  *** NUMAR MAESTRU ***" if maestru_cv else ""
    pdf.rand_info("Cifra Vietii (Life Path)", f"{cv}{maestru_txt}")
    pdf.rand_info("Arhetipul Spiritual", ARHETIPURI.get(cv, str(cv)))
    pdf.rand_info("Misiunea Sufletului", MISIUNI.get(cv, ''))

    pdf.ln(1)
    maestru_cc_txt = "  *** NUMAR MAESTRU ***" if maestru_cc else ""
    pdf.rand_info("Cifra Contractului Social", f"{cc}{maestru_cc_txt}")
    pdf.rand_info("Mesajul Contractului", CONTRACT_MESAJ.get(cc, ''))

    pdf.ln(1)
    pdf.rand_info("Tensiunea Divina (Viata vs Contract)", tensiune, bold_val=False)

    # ── SEC 2: PORTRET VIBRATOR ───────────────
    pdf.titlu_sectiune('II. Portretul Vibrator')
    pdf.rand_info("Element Primar", ELEMENTE.get(cv, ''))
    pdf.rand_info("Culori de Putere", CULORI.get(cv, ''))
    maestru_ca_txt = "  *** NUMAR MAESTRU ***" if maestru_ca else ""
    pdf.rand_info("Contextul Cosmic al Venirii (Anul)", f"{ca}{maestru_ca_txt} — Generatia ta poarta aceasta energie.")

    # ── SEC 3: CHAKRE & INSTRUMENTE ──────────
    pdf.titlu_sectiune('III. Harta Chakrelor & Instrumente Spirituale')
    pdf.rand_info("Chakra Dominanta la Nastere", CHAKRE.get(cv, ''))
    pdf.rand_info("Cristalele Sacre", CRISTALE.get(cv, ''))

    # ── SEC 4: TALENTE & LECTII ───────────────
    pdf.titlu_sectiune('IV. Talente, Lectii si Karma')
    pdf.rand_info("Talentul Nativ (Cifra Zilei)", f"{czz} — {ARHETIPURI.get(czz, '')}")
    pdf.rand_info("Lectia Emotionala (Cifra Lunii)", f"{cl} — {ARHETIPURI.get(cl, '')}")
    pdf.rand_info("Lectia Karmica Principala", LECTII_KARMICE.get(cv, ''))

    # ── SEC 5: PROFESII ───────────────────────
    pdf.titlu_sectiune('V. Profesii Armonioase cu Sufletul')
    pdf.text_bloc(PROFESII.get(cv, ''))

    # ── SEC 6: AN PERSONAL ────────────────────
    pdf.titlu_sectiune(f'VI. Mesajul Anului Personal {datetime.now().year}')
    pdf.rand_info(f"Numarul Anului Personal", f"{ap} — {ARHETIPURI.get(ap, '')}")
    pdf.text_bloc(f"Energia anului {datetime.now().year} in viata ta: {MISIUNI.get(ap, '')}", italic=True)

    # ── SEC 7: AFIRMATIA SACRA ────────────────
    pdf.titlu_sectiune('VII. Afirmatia Sacra a Vietii Tale')
    pdf.ln(2)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(40, 15, 80)

    afirmatie = AFIRMATII.get(cv, '')
    # Box decorativ pentru afirmatie
    y_start = pdf.get_y()
    pdf.set_fill_color(245, 240, 255)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    # Scriem textul
    pdf.multi_cell(0, 6, f'"{afirmatie}"', align='C')
    pdf.ln(2)

    # ── FOOTER CERTIFICAT ─────────────────────
    pdf.ln(3)
    pdf.set_draw_color(201, 168, 76)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(3)

    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(150, 130, 80)
    pdf.multi_cell(0, 4,
        'Emis de: Global Spiritual Identity Foundation (GSIF)  |  Metodologie: Numerologie Pitagoreica Clasica v1.0\n'
        'Acest certificat are valoare spirituala si educationala. Nu inlocuieste niciun document juridic oficial.\n'
        'gsif.org  |  contact@gsif.org  |  "Every Soul Has a Map"',
        align='C'
    )

    # ── SALVARE ───────────────────────────────
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(output_dir, exist_ok=True)
    filename = f"Certificat_GSIF_{zi:02d}{luna:02d}{an}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath


# ─────────────────────────────────────────────
#  INTERFATA UTILIZATOR (CLI)
# ─────────────────────────────────────────────

def main():
    print()
    print("=" * 60)
    print("  GSIF — Global Spiritual Identity Foundation")
    print("  Generator Certificat Numerologic al Vietii")
    print("  'Every Soul Has a Map'")
    print("=" * 60)
    print()

    # Date intrare
    if len(sys.argv) >= 3:
        data_str  = sys.argv[1]   # ZZ.LL.AAAA
        cod_fisc  = sys.argv[2]
    else:
        data_str = input("  Data nasterii (ZZ.LL.AAAA): ").strip()
        cod_fisc = input("  Cod Fiscal / CNP:           ").strip()

    try:
        zi, luna, an = map(int, data_str.split('.'))
    except Exception:
        print("\n  [EROARE] Format data incorect. Foloseste ZZ.LL.AAAA")
        sys.exit(1)

    print()
    print("  Calculez harta numerologica...")

    cv  = calculeaza_cifra_vietii(zi, luna, an)
    czz = calculeaza_cifra_zilei(zi)
    cl  = calculeaza_cifra_lunii(luna)
    ca  = calculeaza_cifra_anului(an)
    cc  = calculeaza_contract(cod_fisc)
    ap  = calculeaza_an_personal(zi, luna)

    print()
    print("─" * 60)
    print(f"  CIFRA VIETII (Life Path):       {cv}  — {ARHETIPURI.get(cv,'')}")
    print(f"  CIFRA ZILEI (Talent Nativ):     {czz} — {ARHETIPURI.get(czz,'')}")
    print(f"  CIFRA LUNII (Lectie Emotionala):{cl}  — {ARHETIPURI.get(cl,'')}")
    print(f"  CIFRA ANULUI NASTERII:          {ca}  {'✦ NUMAR MAESTRU ✦' if ca in (11,22,33) else ''}")
    print(f"  CIFRA CONTRACTULUI SOCIAL:      {cc}  {'✦ NUMAR MAESTRU ✦' if cc in (11,22,33) else ''}")
    print(f"  NUMAR AN PERSONAL {datetime.now().year}:        {ap}")
    print("─" * 60)

    if cv in (11, 22, 33):
        print(f"\n  ✦ ATENTIE: Portati un NUMAR MAESTRU — configuratie rara!")

    if ca in (11, 22, 33) or cc in (11, 22, 33):
        nr_maestru = sum(1 for x in [cv, ca, cc] if x in (11, 22, 33))
        if nr_maestru >= 2:
            print(f"  ✦ {nr_maestru} NUMERE MAESTRU in harta ta — configuratie EXCEPTIONALA (<2% din populatie)!")

    print()
    print("  Generez certificatul PDF...")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificate_generate")
    filepath = genereaza_certificat(zi, luna, an, cod_fisc, output_dir)

    print(f"\n  ✓ Certificat generat cu succes!")
    print(f"  ✓ Salvat la: {filepath}")
    print()
    print("  'Every Soul Has a Map'")
    print("=" * 60)
    print()

    # Deschide automat PDF-ul pe Windows
    if sys.platform == 'win32':
        os.startfile(filepath)

    return filepath


if __name__ == '__main__':
    main()
