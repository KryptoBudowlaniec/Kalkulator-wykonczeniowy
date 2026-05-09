from weasyprint import HTML
from datetime import datetime
import tempfile


def generuj_pdf(typ, dane):

    if typ == "malowanie":
        return _pdf_malowanie(dane)

    if typ == "koszyk":
        return _pdf_koszyk(dane)

    raise ValueError("Nieznany typ PDF")


# =====================================================
# 🎨 MALOWANIE
# =====================================================
def _pdf_malowanie(dane):

    data = datetime.now().strftime("%d.%m.%Y")

    html = f"""
    <html>
    <body>
        <h1>Kosztorys Malowania</h1>
        <h2>{dane.get("nazwa_projektu")}</h2>
        <p>Data: {data}</p>

        <h3>Podsumowanie</h3>
        <p>Robocizna: {dane.get("k_rob_total", 0):,.2f} zł</p>
        <p>Materiały: {dane.get("k_mat_sredni", 0):,.2f} zł</p>

        <h2>RAZEM: {dane.get("total_pro", 0):,.2f} zł</h2>
    </body>
    </html>
    """

    return _render(html)


# =====================================================
# 📦 KOSZYK / PODSUMOWANIA
# =====================================================
def _pdf_koszyk(dane):

    etapy_html = ""

    for e in dane.get("etapy", []):
        etapy_html += f"""
        <div>
            <h3>{e.get('nazwa_etapu')}</h3>
            <p>{e.get('koszt_robocizny', 0):,.2f} zł</p>
        </div>
        """

    html = f"""
    <html>
    <body>
        <h1>Podsumowanie Kosztorysów</h1>

        <p>Klient: {dane.get('nazwa_klienta','')}</p>

        {etapy_html}

        <h2>
        RAZEM: {dane.get('do_zaplaty',0):,.2f} zł
        </h2>
    </body>
    </html>
    """

    return _render(html)


# =====================================================
# 🔧 WSPÓLNY RENDER PDF
# =====================================================
def _render(html):

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    HTML(string=html, base_url=".").write_pdf(temp_file.name)

    return temp_file.name
