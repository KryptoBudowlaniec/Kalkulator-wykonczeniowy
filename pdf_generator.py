from weasyprint import HTML
from datetime import datetime
import tempfile


def generuj_premium_pdf(nazwa_klienta, etapy, suma_rob, rabat, do_zaplaty):

    data_wystawienia = datetime.now().strftime("%d.%m.%Y")

    etapy_html = ""

    for etap in etapy:

        nazwa = etap.get("nazwa_etapu", "Etap")
        kwota = etap.get("koszt_robocizny", 0)

        etapy_html += f"""
        <div class="etap-card">

            <div class="left">

                <div class="icon">
                    🔨
                </div>

                <div>
                    <div class="title">{nazwa}</div>
                    <div class="subtitle">
                        Zakres prac remontowych
                    </div>
                </div>

            </div>

            <div class="price">
                {kwota:,.2f} zł
            </div>

        </div>
        """

    html = f"""

    <html>

    <head>

    <meta charset="utf-8">

    <style>

    body {{
        font-family: Arial;
        background: #edf2f7;
        padding: 40px;
    }}

    .container {{

        background: white;

        border-radius: 30px;

        overflow: hidden;

        box-shadow:
            0 20px 60px rgba(0,0,0,0.1);
    }}

    .hero {{

        background:
            linear-gradient(
                135deg,
                #111827,
                #1f2937
            );

        padding: 70px;

        color: white;
    }}

    .logo {{
        width: 180px;
        margin-bottom: 30px;
    }}

    h1 {{
        font-size: 58px;
        margin: 0;
    }}

    .hero p {{
        color: #cbd5e1;
        font-size: 18px;
    }}

    .content {{
        padding: 40px;
    }}

    .section-title {{
        font-size: 14px;
        color: #64748b;
        margin-bottom: 20px;
        text-transform: uppercase;
    }}

    .card {{

        border: 1px solid #e2e8f0;

        border-radius: 20px;

        padding: 25px;

        margin-bottom: 20px;
    }}

    .big-price {{
        font-size: 38px;
        font-weight: bold;
        color: #00B67A;
    }}

    .etap-card {{

        border: 1px solid #e2e8f0;

        border-radius: 20px;

        padding: 20px;

        margin-bottom: 15px;

        display: flex;

        justify-content: space-between;

        align-items: center;
    }}

    .left {{
        display: flex;
        gap: 15px;
        align-items: center;
    }}

    .icon {{

        width: 50px;
        height: 50px;

        background: #ecfdf5;

        border-radius: 15px;

        display: flex;

        justify-content: center;

        align-items: center;

        font-size: 22px;
    }}

    .title {{
        font-weight: bold;
        font-size: 18px;
    }}

    .subtitle {{
        color: #94a3b8;
        font-size: 13px;
    }}

    .price {{
        font-size: 24px;
        font-weight: bold;
    }}

    .total-box {{

        background:
            linear-gradient(
                135deg,
                #00D395,
                #00B67A
            );

        color: white;

        padding: 35px;

        border-radius: 25px;

        margin-top: 30px;
    }}

    .total-price {{
        font-size: 44px;
        font-weight: bold;
    }}

    </style>

    </head>

    <body>

    <div class="container">

        <div class="hero">

            <img src="logo.png" class="logo">

            <h1>
            Oferta<br>
            Kosztorysowa
            </h1>

            <p>
            Profesjonalna wycena wygenerowana
            w systemie ProCalc Premium
            </p>

        </div>

        <div class="content">

            <div class="section-title">
            Projekt
            </div>

            <div class="card">

                <h2>
                {nazwa_klienta}
                </h2>

                <p>
                Data wystawienia:
                {data_wystawienia}
                </p>

            </div>

            <div class="section-title">
            Zakres prac
            </div>

            {etapy_html}

            <div class="total-box">

                <div>
                Łączna kwota
                </div>

                <div class="total-price">
                {do_zaplaty:,.2f} zł
                </div>

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
