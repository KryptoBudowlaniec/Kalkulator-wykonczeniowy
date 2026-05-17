from weasyprint import HTML
from datetime import datetime, timedelta
import tempfile
import os
import html


def _safe(value):
    return html.escape(str(value if value is not None else ""))


def _money(value):
    try:
        return f"{float(value):,.2f} PLN".replace(",", " ")
    except Exception:
        return "0,00 PLN"


def _asset(name):
    path = os.path.join(os.getcwd(), name)
    return path if os.path.exists(path) else ""


def _materials_rows(materialy):
    if not materialy:
        return "<p class='muted'>Brak pozycji materiałowych.</p>"

    rows = ""
    for mat in materialy:
        if isinstance(mat, dict):
            nazwa = mat.get("nazwa", "")
            ilosc = mat.get("ilosc", "")
            jed = mat.get("jed", "")
            wartosc = f"{ilosc} {jed}".strip()
        else:
            nazwa = str(mat)
            wartosc = ""

        rows += f"""
        <div class="mat-row">
            <span>{_safe(nazwa)}</span>
            <b>{_safe(wartosc)}</b>
        </div>
        """
    return rows


def _stage_rows(etapy):
    if not etapy:
        return ""

    rows = ""
    for etap in etapy:
        nazwa = etap.get("nazwa_etapu") or etap.get("branza") or "Etap"
        branza = etap.get("branza", "")
        koszt = etap.get("koszt_robocizny", etap.get("koszt_calkowity", 0))

        rows += f"""
        <tr>
            <td>{_safe(nazwa)} <span>({_safe(branza)})</span></td>
            <td>{_money(koszt)}</td>
        </tr>
        """
    return rows


def _param_rows(parametry):
    if not parametry:
        return ""

    rows = ""
    for p in parametry:
        rows += f"""
        <div class="info-pair">
            <span>{_safe(p.get("nazwa", ""))}</span>
            <b>{_safe(p.get("wartosc", ""))}</b>
        </div>
        """
    return rows


def generuj_pdf(typ_pdf, dane):
    logo = _asset("logo2.png")
    hero = _asset("hero_remont.png")
    qr = _asset("QR.png") or _asset("qr.png")

    nazwa = dane.get("nazwa_projektu", "Kosztorys")
    tytul = dane.get("tytul", "Oferta kosztorysowa")
    klient_nazwa = dane.get("klient_nazwa", "")
    klient_miasto = dane.get("klient_miasto", "")
    klient_telefon = dane.get("klient_telefon", "")
    klient_email = dane.get("klient_email", "")

    etapy = dane.get("etapy")
    if not etapy:
        etapy = [{
            "nazwa_etapu": nazwa,
            "branza": dane.get("branza", typ_pdf),
            "koszt_robocizny": dane.get("koszt_robocizny", dane.get("kwota_koncowa", 0)),
        }]

    materialy = (
        dane.get("materialy")
        or dane.get("materialy_lista")
        or dane.get("zbiorcza_lista_zakupow")
        or []
    )

    suma_rob = dane.get("koszt_robocizny", dane.get("suma_robocizna", 0))
    suma_mat = dane.get("koszt_materialow", dane.get("suma_materialy", 0))
    
    # Jeśli stare projekty nie mają sumy robocizny w głównym polu,
    # liczymy ją z etapów widocznych w tabeli.
    if not suma_rob and etapy:
        suma_rob = sum(
            float(etap.get("koszt_robocizny", etap.get("koszt_calkowity", 0)) or 0)
            for etap in etapy
        )
    
    if not suma_mat and etapy:
        suma_mat = sum(
            float(etap.get("koszt_materialow", 0) or 0)
            for etap in etapy
        )
    
    razem = dane.get("kwota_koncowa", dane.get("koszt_calkowity", dane.get("koszt_calkowity_projektu", 0)))
    
    if not razem:
        razem = suma_rob + suma_mat


    rabat = dane.get("rabat_kwota", 0)
    
    if rabat:
        razem = suma_rob + suma_mat - float(rabat or 0)


    data_wyst = datetime.now()
    data_wazna = data_wyst + timedelta(days=14)

    html_content = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4 portrait;
    margin: 0;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    color: #09274a;
    background: #eef2f6;
}}

.page {{
    width: 210mm;
    height: 297mm;
    background: white;
    page-break-after: always;
    position: relative;
    overflow: hidden;
}}

.grid {{
    display: block;
    min-height: calc(297mm - 12mm);
}}


.left {{
    border-right: 1px solid #d8e0ea;
}}

.hero {{
    height: 88mm;
    padding: 12mm;
    color: white;
    background:
        linear-gradient(90deg, rgba(4, 32, 62, .95), rgba(4, 32, 62, .62), rgba(4, 32, 62, .18)),
        url("{hero}");
    background-size: cover;
    background-position: center;
}}

.logo {{
    height: 16mm;
    object-fit: contain;
    margin-bottom: 20mm;
}}

.hero h1 {{
    font-size: 34pt;
    line-height: 1.05;
    margin: 0;
    letter-spacing: .5px;
    text-transform: uppercase;
}}

.hero-date {{
    margin-top: 15mm;
    font-size: 10pt;
    line-height: 1.5;
}}

.content {{
    padding: 9mm 10mm;
}}

.section-title {{
    font-size: 12pt;
    font-weight: 800;
    text-transform: uppercase;
    margin: 0 0 7mm;
    color: #003b78;
}}

.info-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6mm 10mm;
}}

.info-pair span {{
    display: block;
    font-size: 8pt;
    color: #5b6d80;
    margin-bottom: 2mm;
}}

.info-pair b {{
    display: block;
    font-size: 11pt;
    color: #082849;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4mm;
    margin: 8mm 0;
}}

.card {{
    border: 1px solid #dfe6ee;
    border-radius: 6px;
    padding: 5mm;
    min-height: 23mm;
    background: #f8fafc;
}}

.card.red {{
    background: #fff7f7;
}}

.card.green {{
    background: #f2fbf6;
}}

.card span {{
    display: block;
    font-size: 8pt;
    color: #5b6d80;
    margin-bottom: 2mm;
}}

.card b {{
    font-size: 12pt;
    color: #09274a;
}}

.card.red b {{
    color: #d71920;
}}

.card.green b {{
    color: #009a5b;
}}

.right {{
    padding: 17mm 10mm 0;
}}

.cost-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
}}

.cost-table th {{
    background: #f1f3f6;
    color: #003b78;
    text-align: left;
    padding: 4mm;
}}

.cost-table th:last-child,
.cost-table td:last-child {{
    text-align: right;
}}

.cost-table td {{
    padding: 3.6mm 4mm;
    border-bottom: 1px solid #eef2f6;
}}

.cost-table tr:nth-child(even) td {{
    background: #fafafa;
}}

.cost-table span {{
    color: #65758a;
}}

.total-box {{
    margin-top: 7mm;
    border: 1px solid #dbe3ec;
    border-radius: 6px;
    overflow: hidden;
}}

.total-row {{
    display: flex;
    justify-content: space-between;
    padding: 4mm 5mm;
    font-size: 12pt;
}}

.final-row {{
    display: flex;
    justify-content: space-between;
    padding: 5mm;
    background: #003b78;
    color: white;
    font-size: 16pt;
    font-weight: 800;
}}

.notice {{
    margin-top: 9mm;
    font-size: 9pt;
    line-height: 1.55;
}}

.footer {{
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 12mm;
    background: #f5f7fa;
    border-top: 1px solid #dce4ed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 11mm;
    font-size: 8pt;
    color: #37516c;
}}

.page2 {{
    padding: 13mm 12mm 27mm;
}}

.two-cols {{
    display: grid;
    grid-template-columns: 1.05fr .95fr;
    gap: 12mm;
}}

.mat-group {{
    margin-bottom: 5mm;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #e5ebf2;
}}

.mat-head {{
    background: #f1f3f6;
    padding: 3mm 4mm;
    font-weight: 800;
    color: #003b78;
}}

.mat-row {{
    display: flex;
    justify-content: space-between;
    padding: 2.7mm 4mm;
    border-top: 1px solid #edf1f5;
    font-size: 9pt;
}}

.note-box {{
    background: #f7f9fb;
    border-radius: 6px;
    padding: 7mm;
    font-size: 10pt;
    line-height: 1.8;
}}

.terms {{
    margin-top: 11mm;
}}

.term-row {{
    display: grid;
    grid-template-columns: 42mm 1fr;
    gap: 6mm;
    margin-bottom: 5mm;
    font-size: 10pt;
}}

.dark-footer {{
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 27mm;
    background: #082849;
    color: white;
    display: grid;
    grid-template-columns: 48mm 1fr 35mm 42mm;
    align-items: center;
    gap: 8mm;
    padding: 0 12mm;
    font-size: 9pt;
}}

.dark-footer img.logo-footer {{
    max-width: 40mm;
    max-height: 15mm;
}}

.dark-footer img.qr {{
    width: 22mm;
    height: 22mm;
    background: white;
    padding: 1.5mm;
}}

.muted {{
    color: #65758a;
}}
</style>
</head>

<body>

<section class="page">
    <div class="grid">
        <div class="left">
            <div class="hero">
                {"<img class='logo' src='" + logo + "'>" if logo else ""}
                <h1>Oferta<br>Kosztorysowa</h1>
                <div class="hero-date">
                    Data wystawienia:<br>
                    <b>{data_wyst.strftime("%d.%m.%Y")}</b>
                </div>
            </div>

            <div class="content">
                <h2 class="section-title">Dane inwestycji</h2>
                <div class="info-grid">
                    <div class="info-pair">
                        <span>Nazwa inwestycji:</span>
                        <b>{_safe(nazwa)}</b>
                    </div>
                    <div class="info-pair">
                        <span>Zakres prac:</span>
                        <b>{_safe(dane.get("branza", typ_pdf))}</b>
                    </div>
                    <div class="info-pair">
                        <span>Klient:</span>
                        <b>{_safe(klient_nazwa or "Nie przypisano")}</b>
                    </div>
                    <div class="info-pair">
                        <span>Lokalizacja:</span>
                        <b>{_safe(klient_miasto or "Do ustalenia")}</b>
                    </div>
                    {_param_rows(dane.get("parametry", [])[:4])}
                </div>

                <h2 class="section-title" style="margin-top: 10mm;">Podsumowanie oferty</h2>
                <div class="cards">
                    <div class="card">
                        <span>Suma robocizny:</span>
                        <b>{_money(suma_rob)}</b>
                    </div>
                    <div class="card red">
                        <span>Udzielony rabat:</span>
                        <b>{_safe(rabat)}</b>
                    </div>
                    <div class="card green">
                        <span>Łącznie do zapłaty:</span>
                        <b>{_money(razem)}</b>
                    </div>
                </div>

                <h2 class="section-title">Zakres prac</h2>
                <p class="muted">Oferta obejmuje etapy i branże wyszczególnione w zestawieniu kosztów.</p>
            </div>
        </div>

        <div class="right">
            <h2 class="section-title">Zestawienie kosztów</h2>
            <table class="cost-table">
                <thead>
                    <tr>
                        <th>Etap / Branża</th>
                        <th>Wartość</th>
                    </tr>
                </thead>
                <tbody>
                    {_stage_rows(etapy)}
                </tbody>
            </table>

            <div class="total-box">
                <div class="total-row">
                    <span>Suma robocizny:</span>
                    <b>{_money(suma_rob)}</b>
                </div>
                <div class="total-row" style="color:#d71920;">
                    <span>Udzielony rabat:</span>
                    <b>{_safe(rabat)}</b>
                </div>
                <div class="final-row">
                    <span>Łącznie do zapłaty:</span>
                    <span>{_money(razem)}</span>
                </div>
            </div>

            <div class="notice">
                <b>Ważne informacje</b><br>
                Oferta obejmuje zakres prac wskazany w kosztorysie.
                Materiały i ilości mają charakter orientacyjny, chyba że ustalono inaczej.
            </div>
        </div>
    </div>

    <div class="footer">
        <span>Dziękujemy za zaufanie. W razie pytań jesteśmy do dyspozycji.</span>
        <span>procalc.pl | kontakt@procalc.pl</span>
        <span>Strona 1 z 2</span>
    </div>
</section>

<section class="page page2">
    <div class="two-cols">
        <div>
            <h2 class="section-title">Logistyka i zapotrzebowanie materiałowe</h2>
            <div class="mat-group">
                <div class="mat-head">Materiały i akcesoria</div>
                {_materials_rows(materialy)}
            </div>
        </div>

        <div>
            <h2 class="section-title">Notatki i uwagi</h2>
            <div class="note-box">
                <p>Podane ilości materiałów mają charakter orientacyjny i mogą się różnić po weryfikacji na budowie.</p>
                <p>Zalecamy zakup materiałów z 5-10% zapasem.</p>
                <p>Przed rozpoczęciem prac zalecamy weryfikację wszystkich wymiarów na miejscu.</p>
                <p>Prace wykonywane są zgodnie ze sztuką budowlaną oraz obowiązującymi normami.</p>
            </div>

            <div class="terms">
                <h2 class="section-title">Warunki współpracy</h2>
                <div class="term-row"><span>Termin realizacji:</span><b>Do ustalenia</b></div>
                <div class="term-row"><span>Płatność:</span><b>Zaliczka 30%, reszta po zakończeniu prac</b></div>
                <div class="term-row"><span>Oferta ważna do:</span><b>{data_wazna.strftime("%d.%m.%Y")}</b></div>
                <div class="term-row"><span>Gwarancja:</span><b>24 miesiące na wykonane prace</b></div>
            </div>
        </div>
    </div>

    <div class="dark-footer">
        {"<img class='logo-footer' src='" + logo + "'>" if logo else "<b>PROCALC</b>"}
        <div>
            <b>Masz pytania? Skontaktuj się z nami!</b><br>
            +48 600 123 456 &nbsp;&nbsp; kontakt@procalc.pl &nbsp;&nbsp; procalc.pl
        </div>
        {"<img class='qr' src='" + qr + "'>" if qr else ""}
        <div>Zeskanuj kod QR<br>i zobacz kalkulator online</div>
        <div style="position:absolute;right:8mm;bottom:4mm;font-size:8pt;">Strona 2 z 2</div>
    </div>
</section>

</body>
</html>
"""

    output_path = os.path.join(
        tempfile.gettempdir(),
        f"procalc_{typ_pdf}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    )

    HTML(string=html_content, base_url=os.getcwd()).write_pdf(output_path)
    return output_path
