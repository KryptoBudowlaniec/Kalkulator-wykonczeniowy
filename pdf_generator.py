from weasyprint import HTML
from datetime import datetime
import tempfile
from html import escape


def generuj_pdf(typ_pdf, dane):
    """
    Uniwersalny generator PDF dla wszystkich kalkulatorów ProCalc.
    Zachowuje stary format wywołania: generuj_pdf("malowanie", dane)
    """
    dane_pdf = _normalizuj_dane(typ_pdf, dane)
    return _pdf_uniwersalny(dane_pdf)


def _money(value):
    try:
        return f"{float(value):,.2f}".replace(",", " ").replace(".", ",")
    except Exception:
        return "0,00"


def _safe(value):
    return escape(str(value or ""))


def _normalizuj_dane(typ_pdf, dane):
    firma = {
        "firma_nazwa": dane.get("firma_nazwa", "PROCALC"),
        "firma_adres": dane.get("firma_adres", ""),
        "firma_nip": dane.get("firma_nip", ""),
        "firma_kontakt": dane.get("firma_kontakt", ""),
    }

    branza = dane.get("branza") or typ_pdf.replace("_", " ").title()

    tytuly = {
        "malowanie": "Kosztorys prac malarskich",
        "szpachlowanie": "Kosztorys prac szpachlarskich",
        "tynkowanie": "Kosztorys prac tynkarskich",
        "sucha_zabudowa": "Kosztorys suchej zabudowy",
        "elektryka": "Kosztorys instalacji elektrycznej",
        "lazienka": "Kosztorys łazienki",
        "łazienka": "Kosztorys łazienki",
        "podlogi": "Kosztorys podłóg",
        "podłogi": "Kosztorys podłóg",
        "drzwi": "Kosztorys montażu drzwi",
        "tapetowanie": "Kosztorys tapetowania",
        "efekty_dekoracyjne": "Kosztorys efektów dekoracyjnych",
        "koszyk": "Oferta zbiorcza",
        "panel_inwestora": "Kosztorys inwestorski",
    }

    koszt_robocizny = dane.get(
        "koszt_robocizny",
        dane.get("k_rob_total", dane.get("suma_robocizna", 0))
    )

    koszt_materialow = dane.get(
        "koszt_materialow",
        dane.get("k_mat_sredni", dane.get("suma_materialy", 0))
    )

    kwota_koncowa = dane.get(
        "kwota_koncowa",
        dane.get("total_pro", dane.get("koszt_calkowity", dane.get("do_zaplaty", 0)))
    )

    if not kwota_koncowa:
        kwota_koncowa = float(koszt_robocizny or 0) + float(koszt_materialow or 0)

    materialy = dane.get("materialy", dane.get("materialy_lista", []))
    parametry = dane.get("parametry", [])

    if typ_pdf == "malowanie" and not materialy:
        materialy = [
            {"nazwa": "Farba biała", "ilosc": f"{round(dane.get('l_biala', 0), 1)} L"},
            {"nazwa": "Farba kolor", "ilosc": f"{round(dane.get('l_kolor', 0), 1)} L"},
            {"nazwa": "Grunt", "ilosc": f"{round(dane.get('l_grunt', 0), 1)} L"},
            {"nazwa": "Taśma malarska", "ilosc": f"{round(dane.get('szt_tasma', 0))} szt."},
            {"nazwa": "Akryl szpachlowy", "ilosc": f"{round(dane.get('szt_akryl', 0))} szt."},
            {"nazwa": "Sztukateria", "ilosc": f"{round(dane.get('mb_sztukaterii', 0))} mb"},
        ]

    if typ_pdf == "malowanie" and not parametry:
        parametry = [
            {"nazwa": "Metraż użytkowy", "wartosc": f"{dane.get('m_uzytkowy', 0)} m²"},
        ]

    return {
        **firma,
        "typ_pdf": typ_pdf,
        "branza": branza,
        "tytul": dane.get("tytul", tytuly.get(typ_pdf, "Kosztorys ProCalc")),
        "nazwa_projektu": dane.get("nazwa_projektu", dane.get("nazwa_klienta", "Projekt")),
        "data_wystawienia": datetime.now().strftime("%d.%m.%Y"),
        "koszt_robocizny": koszt_robocizny,
        "koszt_materialow": koszt_materialow,
        "kwota_koncowa": kwota_koncowa,
        "parametry": parametry,
        "materialy": materialy,
        "etapy": dane.get("etapy", []),
        "uwagi": dane.get("uwagi", []),
        "klauzule": dane.get("klauzule", _domyslne_klauzule()),
    }


def _domyslne_klauzule():
    return [
        "Wycena ma charakter orientacyjny i może ulec zmianie po oględzinach inwestycji.",
        "Wszelkie dodatkowe prace nieujęte w kosztorysie wymagają osobnej akceptacji inwestora.",
        "Cena nie obejmuje ukrytych wad podłoża oraz uszkodzeń niewidocznych podczas wyceny.",
        "Termin realizacji uzależniony jest od dostępności materiałów oraz warunków technicznych inwestycji.",
        "Materiały mogą różnić się ceną końcową w zależności od aktualnych cen rynkowych.",
    ]


def _render_materialy(materialy):
    if not materialy:
        return '<p class="muted">Brak pozycji materiałowych.</p>'

    html = ""

    for item in materialy:
        if isinstance(item, dict):
            nazwa = item.get("nazwa", "Materiał")
            if "ilosc" in item and "jed" in item:
                ilosc = f"{item.get('ilosc')} {item.get('jed')}"
            else:
                ilosc = item.get("ilosc", item.get("wartosc", ""))
        else:
            nazwa = str(item)
            ilosc = ""

        html += f"""
        <div class="list-item">
            <div>{_safe(nazwa)}</div>
            <strong>{_safe(ilosc)}</strong>
        </div>
        """

    return html


def _render_parametry(parametry):
    if not parametry:
        return ""

    rows = ""

    for item in parametry:
        if isinstance(item, dict):
            nazwa = item.get("nazwa", "Parametr")
            wartosc = item.get("wartosc", "")
        else:
            nazwa = str(item)
            wartosc = ""

        rows += f"""
        <div class="list-item">
            <div>{_safe(nazwa)}</div>
            <strong>{_safe(wartosc)}</strong>
        </div>
        """

    return f"""
    <div class="section-title" style="margin-top:40px;">Parametry projektu</div>
    <div class="card">
        {rows}
    </div>
    """


def _render_etapy(etapy):
    if not etapy:
        return ""

    rows = ""

    for etap in etapy:
        nazwa = etap.get("nazwa_etapu", "Etap")
        branza = etap.get("branza", "")
        kwota = etap.get("koszt_robocizny", etap.get("koszt_calkowity", 0))

        rows += f"""
        <tr>
            <td>{_safe(nazwa)}</td>
            <td>{_safe(branza)}</td>
            <td class="right">{_money(kwota)} zł</td>
        </tr>
        """

    return f"""
    <div class="section-title" style="margin-top:40px;">Zakres prac</div>
    <table>
        <thead>
            <tr>
                <th>Etap</th>
                <th>Branża</th>
                <th>Kwota</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def _pdf_uniwersalny(dane):
    materialy_html = _render_materialy(dane.get("materialy", []))
    parametry_html = _render_parametry(dane.get("parametry", []))
    etapy_html = _render_etapy(dane.get("etapy", []))

    klauzule_html = "".join(
        f"<li>{_safe(k)}</li>"
        for k in dane.get("klauzule", [])
    )

    uwagi = dane.get("uwagi", [])
    uwagi_html = ""
    if uwagi:
        uwagi_html = """
        <div class="section-title" style="margin-top:40px;">Uwagi</div>
        <div class="card">
        """
        for uwaga in uwagi:
            uwagi_html += f'<p class="muted">• {_safe(uwaga)}</p>'
        uwagi_html += "</div>"

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">

    <style>
    @page {{
        size: A4;
        margin: 18mm;
    }}

    body {{
        font-family: Arial, sans-serif;
        background: #edf2f7;
        color: #1e293b;
        margin: 0;
    }}

    .container {{
        background: white;
        border-radius: 20px;
        overflow: hidden;
    }}

    .hero {{
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
        padding: 48px;
    }}

    .hero-top {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        font-size: 13px;
        color: #cbd5e1;
    }}

    .logo {{
        font-size: 30px;
        font-weight: bold;
        color: white;
    }}

    .hero h1 {{
        font-size: 44px;
        line-height: 1.05;
        margin: 42px 0 12px;
    }}

    .hero p {{
        color: #cbd5e1;
        font-size: 16px;
        max-width: 560px;
    }}

    .price-box {{
        background: linear-gradient(135deg, #00D395, #00B67A);
        padding: 26px;
        border-radius: 18px;
        margin-top: 34px;
    }}

    .price-label {{
        font-size: 14px;
        opacity: 0.9;
    }}

    .price-value {{
        font-size: 42px;
        font-weight: bold;
        margin-top: 8px;
    }}

    .content {{
        padding: 38px;
    }}

    .section-title {{
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 14px;
        font-weight: bold;
        letter-spacing: .6px;
    }}

    .card {{
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 22px;
    }}

    .grid {{
        display: flex;
        gap: 18px;
    }}

    .grid .card {{
        flex: 1;
    }}

    .big-number {{
        font-size: 28px;
        font-weight: bold;
        margin-top: 10px;
    }}

    .muted {{
        color: #64748b;
        line-height: 1.5;
    }}

    .badge {{
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-size: 11px;
        font-weight: bold;
        margin-top: 12px;
    }}

    .list-item {{
        display: flex;
        justify-content: space-between;
        gap: 20px;
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
    }}

    .list-item:last-child {{
        border-bottom: none;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
    }}

    th {{
        background: #f8fafc;
        color: #64748b;
        text-transform: uppercase;
        font-size: 11px;
        text-align: left;
        padding: 12px;
    }}

    td {{
        padding: 12px;
        border-top: 1px solid #e2e8f0;
    }}

    .right {{
        text-align: right;
        font-weight: bold;
    }}

    .clause-box {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        margin-top: 26px;
    }}

    .clause-box li {{
        margin-bottom: 10px;
        line-height: 1.55;
    }}

    .signature-wrapper {{
        margin-top: 60px;
        display: flex;
        justify-content: space-between;
    }}

    .signature {{
        width: 42%;
        text-align: center;
        color: #475569;
    }}

    .line {{
        border-top: 1px solid #94a3b8;
        margin-bottom: 10px;
        padding-top: 10px;
    }}

    .footer {{
        margin-top: 45px;
        text-align: center;
        color: #94a3b8;
        font-size: 11px;
    }}
    </style>
    </head>

    <body>
    <div class="container">

        <div class="hero">
            <div class="hero-top">
                <div class="logo">PROCALC</div>
                <div>{_safe(dane["data_wystawienia"])}</div>
            </div>

            <h1>{_safe(dane["tytul"])}</h1>

            <p>
                Profesjonalna wycena wygenerowana w systemie ProCalc Premium+.
            </p>

            <div class="price-box">
                <div class="price-label">Łączna wartość realizacji</div>
                <div class="price-value">{_money(dane["kwota_koncowa"])} zł</div>
            </div>
        </div>

        <div class="content">

            <div class="section-title">Dane projektu</div>
            <div class="card">
                <h2>{_safe(dane["nazwa_projektu"])}</h2>
                <p class="muted">Branża: {_safe(dane["branza"])}</p>
                <div class="badge">Oferta Premium PRO</div>
            </div>

            <div class="section-title">Dane wykonawcy</div>
            <div class="card">
                <strong>{_safe(dane["firma_nazwa"])}</strong>
                <p>{_safe(dane["firma_adres"])}</p>
                <p>NIP: {_safe(dane["firma_nip"])}</p>
                <p>{_safe(dane["firma_kontakt"])}</p>
            </div>

            <div class="section-title">Podsumowanie finansowe</div>
            <div class="grid">
                <div class="card">
                    <div class="muted">Robocizna</div>
                    <div class="big-number">{_money(dane["koszt_robocizny"])} zł</div>
                </div>

                <div class="card">
                    <div class="muted">Materiały</div>
                    <div class="big-number">{_money(dane["koszt_materialow"])} zł</div>
                </div>
            </div>

            {etapy_html}

            {parametry_html}

            <div class="section-title" style="margin-top:40px;">Lista zakupów</div>
            <div class="card">
                {materialy_html}
            </div>

            {uwagi_html}

            <div class="section-title" style="margin-top:40px;">
                Klauzule i zabezpieczenia wykonawcy
            </div>

            <div class="clause-box">
                <ul>
                    {klauzule_html}
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

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    HTML(
        string=html,
        base_url="."
    ).write_pdf(temp_file.name)

    return temp_file.name
