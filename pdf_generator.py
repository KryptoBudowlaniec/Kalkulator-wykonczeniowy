from weasyprint import HTML
from datetime import datetime
import tempfile


# ==========================================
# GŁÓWNY GENERATOR PDF
# ==========================================
def generuj_pdf(typ_pdf, dane):

    if typ_pdf == "malowanie":
        return _pdf_malowanie(dane)

    elif typ_pdf == "koszyk":
        return _pdf_koszyk(dane)

    else:
        raise ValueError("Nieznany typ PDF")


# ==========================================
# PDF — MODUŁ MALOWANIA PREMIUM+
# ==========================================
def _pdf_malowanie(dane):

    data_wystawienia = datetime.now().strftime("%d.%m.%Y")

    nazwa_projektu = dane.get("nazwa_projektu", "Projekt")
    firma_nazwa = dane.get("firma_nazwa", "PROCALC")
    firma_adres = dane.get("firma_adres", "")
    firma_nip = dane.get("firma_nip", "")
    firma_kontakt = dane.get("firma_kontakt", "")

    m_uzytkowy = dane.get("m_uzytkowy", 0)

    total_pro = dane.get("total_pro", 0)
    k_rob_total = dane.get("k_rob_total", 0)
    k_mat_sredni = dane.get("k_mat_sredni", 0)

    l_biala = dane.get("l_biala", 0)
    l_kolor = dane.get("l_kolor", 0)
    l_grunt = dane.get("l_grunt", 0)
    szt_tasma = dane.get("szt_tasma", 0)
    szt_akryl = dane.get("szt_akryl", 0)
    mb_sztukaterii = dane.get("mb_sztukaterii", 0)

    html = f"""

    <html>

    <head>

    <meta charset="utf-8">

    <style>

    @page {{
        margin: 25px;
    }}

    body {{
        font-family: Arial, sans-serif;
        background: #edf2f7;
        color: #1e293b;
    }}

    .container {{

        background: white;

        border-radius: 28px;

        overflow: hidden;

        box-shadow:
            0 15px 50px rgba(0,0,0,0.08);
    }}

    .hero {{

        background:
            linear-gradient(
                135deg,
                #0f172a,
                #1e293b
            );

        color: white;

        padding: 60px;
    }}

    .hero-top {{

        display: flex;

        justify-content: space-between;

        align-items: center;
    }}

    .logo {{
        font-size: 34px;
        font-weight: bold;
    }}

    .hero h1 {{
        font-size: 52px;
        margin-top: 40px;
        margin-bottom: 10px;
    }}

    .hero p {{
        color: #cbd5e1;
        font-size: 18px;
    }}

    .price-box {{

        background:
            linear-gradient(
                135deg,
                #00D395,
                #00B67A
            );

        padding: 30px;

        border-radius: 24px;

        margin-top: 40px;
    }}

    .price-label {{
        font-size: 16px;
        opacity: 0.9;
    }}

    .price-value {{
        font-size: 52px;
        font-weight: bold;
        margin-top: 10px;
    }}

    .content {{
        padding: 45px;
    }}

    .section-title {{

        font-size: 14px;

        color: #64748b;

        text-transform: uppercase;

        margin-bottom: 20px;

        font-weight: bold;
    }}

    .card {{

        border: 1px solid #e2e8f0;

        border-radius: 22px;

        padding: 28px;

        margin-bottom: 24px;
    }}

    .grid {{

        display: flex;

        gap: 20px;
    }}

    .grid .card {{
        flex: 1;
    }}

    .big-number {{
        font-size: 34px;
        font-weight: bold;
        margin-top: 12px;
    }}

    .list-item {{

        display: flex;

        justify-content: space-between;

        padding: 14px 0;

        border-bottom: 1px solid #f1f5f9;
    }}

    .list-item:last-child {{
        border-bottom: none;
    }}

    .muted {{
        color: #64748b;
    }}

    .badge {{

        display: inline-block;

        padding: 8px 14px;

        border-radius: 999px;

        background: #dcfce7;

        color: #166534;

        font-size: 12px;

        font-weight: bold;

        margin-top: 15px;
    }}

    .clause-box {{

        background: #f8fafc;

        border: 1px solid #e2e8f0;

        border-radius: 20px;

        padding: 28px;

        margin-top: 30px;
    }}

    .clause-box li {{
        margin-bottom: 12px;
        line-height: 1.6;
    }}

    .signature-wrapper {{

        margin-top: 70px;

        display: flex;

        justify-content: space-between;
    }}

    .signature {{

        width: 42%;

        text-align: center;
    }}

    .line {{
        border-top: 1px solid #94a3b8;
        margin-bottom: 10px;
        padding-top: 10px;
    }}

    .footer {{

        margin-top: 50px;

        text-align: center;

        color: #94a3b8;

        font-size: 12px;
    }}

    </style>

    </head>

    <body>

    <div class="container">

        <div class="hero">

            <div class="hero-top">

                <div class="logo">
                    PROCALC
                </div>

                <div>
                    {data_wystawienia}
                </div>

            </div>

            <h1>
            Kosztorys<br>
            Prac Malarskich
            </h1>

            <p>
            Profesjonalna wycena wygenerowana
            w systemie ProCalc Premium+
            </p>

            <div class="price-box">

                <div class="price-label">
                Łączna wartość realizacji
                </div>

                <div class="price-value">
                {total_pro:,.2f} zł
                </div>

            </div>

        </div>

        <div class="content">

            <div class="section-title">
            Dane projektu
            </div>

            <div class="card">

                <h2>
                {nazwa_projektu}
                </h2>

                <p class="muted">
                Metraż użytkowy:
                {m_uzytkowy} m²
                </p>

                <div class="badge">
                    Oferta Premium PRO
                </div>

            </div>

            <div class="section-title">
            Dane wykonawcy
            </div>

            <div class="card">

                <strong>
                {firma_nazwa}
                </strong>

                <p>
                {firma_adres}
                </p>

                <p>
                NIP: {firma_nip}
                </p>

                <p>
                {firma_kontakt}
                </p>

            </div>

            <div class="section-title">
            Podsumowanie finansowe
            </div>

            <div class="grid">

                <div class="card">

                    <div class="muted">
                    Robocizna
                    </div>

                    <div class="big-number">
                    {k_rob_total:,.2f} zł
                    </div>

                </div>

                <div class="card">

                    <div class="muted">
                    Materiały
                    </div>

                    <div class="big-number">
                    {k_mat_sredni:,.2f} zł
                    </div>

                </div>

            </div>

            <div class="section-title" style="margin-top:40px;">
            Lista zakupów
            </div>

            <div class="card">

                <div class="list-item">
                    <div>Farba biała</div>
                    <strong>{round(l_biala,1)} L</strong>
                </div>

                <div class="list-item">
                    <div>Farba kolor</div>
                    <strong>{round(l_kolor,1)} L</strong>
                </div>

                <div class="list-item">
                    <div>Grunt</div>
                    <strong>{round(l_grunt,1)} L</strong>
                </div>

                <div class="list-item">
                    <div>Taśma malarska</div>
                    <strong>{round(szt_tasma)} szt.</strong>
                </div>

                <div class="list-item">
                    <div>Akryl szpachlowy</div>
                    <strong>{round(szt_akryl)} szt.</strong>
                </div>

                <div class="list-item">
                    <div>Sztukateria</div>
                    <strong>{round(mb_sztukaterii)} mb</strong>
                </div>

            </div>

            <div class="section-title" style="margin-top:40px;">
            Klauzule i zabezpieczenia wykonawcy
            </div>

            <div class="clause-box">

                <ul>

                    <li>
                    Wycena ma charakter orientacyjny i może ulec zmianie po oględzinach inwestycji.
                    </li>

                    <li>
                    Wszelkie dodatkowe prace nieujęte w kosztorysie wymagają osobnej akceptacji inwestora.
                    </li>

                    <li>
                    Cena nie obejmuje ukrytych wad podłoża oraz uszkodzeń niewidocznych podczas wyceny.
                    </li>

                    <li>
                    Termin realizacji uzależniony jest od dostępności materiałów oraz warunków technicznych inwestycji.
                    </li>

                    <li>
                    Materiały mogą różnić się ceną końcową w zależności od aktualnych cen rynkowych.
                    </li>

                </ul>

            </div>

            <div class="signature-wrapper">

                <div class="signature">

                    <div class="line"></div>

                    Wykonawca

                </div>

                <div class="signature">

                    <div class="line"></div>

                    Inwestor

                </div>

            </div>

            <div class="footer">

                Wygenerowano w systemie ProCalc Premium+<br>
                www.procalc.pl

            </div>

        </div>

    </div>

    </body>

    </html>
    """

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    HTML(
        string=html,
        base_url="."
    ).write_pdf(temp_file.name)

    return temp_file.name


# ==========================================
# PDF — KOSZYK / OFERTA ZBIORCZA
# ==========================================
def _pdf_koszyk(dane):

    data_wystawienia = datetime.now().strftime("%d.%m.%Y")

    nazwa_klienta = dane.get("nazwa_klienta", "Klient")
    etapy = dane.get("etapy", [])
    do_zaplaty = dane.get("do_zaplaty", 0)

    etapy_html = ""

    for etap in etapy:

        nazwa = etap.get("nazwa_etapu", "Etap")
        kwota = etap.get("koszt_calkowity", 0)

        etapy_html += f"""

        <div style="
            border:1px solid #e2e8f0;
            border-radius:18px;
            padding:20px;
            margin-bottom:15px;
        ">

            <h3>{nazwa}</h3>

            <p>
            {kwota:,.2f} zł
            </p>

        </div>
        """

    html = f"""

    <html>

    <head>

    <meta charset="utf-8">

    <style>

    body {{
        font-family: Arial;
        padding: 40px;
        background:#f8fafc;
    }}

    .container {{
        background:white;
        border-radius:25px;
        padding:40px;
    }}

    h1 {{
        font-size:48px;
    }}

    .price {{
        font-size:42px;
        color:#00B67A;
        font-weight:bold;
    }}

    </style>

    </head>

    <body>

    <div class="container">

        <h1>
        Oferta zbiorcza
        </h1>

        <p>
        Klient:
        {nazwa_klienta}
        </p>

        <p>
        Data:
        {data_wystawienia}
        </p>

        <hr>

        {etapy_html}

        <hr>

        <div class="price">
        {do_zaplaty:,.2f} zł
        </div>

    </div>

    </body>

    </html>
    """

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    HTML(
        string=html,
        base_url="."
    ).write_pdf(temp_file.name)

    return temp_file.name
