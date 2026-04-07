import streamlit as st

# 1. KONFIGURACJA GŁÓWNA
st.set_page_config(page_title="Ekspert Wykończeń", layout="wide")

if 'widok' not in st.session_state:
    st.session_state.widok = "Start"

# --- HEADER: LOGO LEWA (WIĘKSZE) | MENU PRAWA ---
col_logo, col_nav = st.columns([1.5, 2.5]) # Zwiększyłem proporcję dla logo

with col_logo:
    try:
        # use_container_width sprawi, że logo zajmie całą dostępną przestrzeń kolumny
        st.image("logo2.png", use_container_width=True)
    except:
        st.error("Brak logo2.png")

with col_nav:
    # Owijamy pigułki w div, który w CSS ma ustawione wyrównanie do prawej
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    nawigacja = st.pills(
        "", 
        ["Start", "Kalkulatory", "Panel Inwestora", "Kontakt"],
        selection_mode="single",
        default="Start",
        key="main_nav"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- PODMENU (Pojawia się pod headerem tylko gdy wybrano Kalkulatory) ---
if nawigacja == "Kalkulatory":
    st.markdown("<br>", unsafe_allow_html=True)
    sub_nav_col = st.columns([1])[0]
    with sub_nav_col:
        branza = st.pills(
            "Wybierz branżę:", 
            ["Malowanie", "Szpachlowanie", "Tynkowanie", "Sucha Zabudowa", "Elektryka", "Łazienka", "Podłogi", "Drzwi"],
            selection_mode="single",
            default="Malowanie",
            key="sub_nav"
        )
else:
    branza = nawigacja


# --- 1. ZINTEGROWANE STYLE CSS (FIX: FAQ COLORS & NO ARROWS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* 1. Globalne */
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #FFFFFF !important; color: #1E1E1E !important; }

    /* Fix na nieszczęsne "arrow" - ukrywamy systemowe punktory */
    li::before { content: none !important; display: none !important; }

    [data-testid="stMarkdownContainer"] ul {
        list-style-type: none !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }

    [data-testid="stMarkdownContainer"] li {
        list-style-type: none !important;
    }

    /* 2. Ukrycie pseudo-elementów (tych strzałek), które Streamlit dodaje przed LI */
    [data-testid="stMarkdownContainer"] li::before {
        content: none !important;
        display: none !important;
    }

    /* 2. UNIWERSALNY KAFELEK (Dla obu sekcji) */
    .custom-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 12px !important;
        list-style: none !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
        
        /* TO GWARANTUJE IDEALNE ODSTĘPY MIĘDZY ELEMENTAMI */
        gap: 12px !important; 
        
        height: auto !important;
        min-height: 220px !important;
    }
    /* EFEKT RUCHU (Hover) */
    .custom-card:hover {
        transform: translateY(-5px) !important;
        border-color: #00D395 !important;
        box-shadow: 0px 8px 20px rgba(0, 211, 149, 0.1) !important;
    }

    .card-title {
        color: #00D395 !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        margin: 0 !important; 
        padding: 0 !important;
    }

    .card-text {
        color: #6C757D !important;
        font-size: 14px !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
    }

    .card-list {
        content: "• " !important;
        color: #00D395 !important;
        font-weight: bold !important;
        margin-right: 8px !important;
        list-style: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        width: 100% !important;
    }

    .card-list li {
        font-size: 13px !important;
        color: #495057 !important;
        margin-bottom: 4px !important; /* Odstęp między punktami listy */
        display: block !important;
    }

    .card-list li::before {
        content: "• " !important;
        color: #00D395 !important;
        font-weight: bold !important;
    }

    /* 3. FAQ i Przyciski */
    .faq-card-question { background: #FFF; border: 2px solid #00D395; border-radius: 15px 15px 0 0; padding: 20px; font-weight: 800; text-align: center; margin-top: 20px;}
    .faq-card-answer { background: #00D395; border-radius: 0 0 15px 15px; padding: 20px; color: #FFF !important; text-align: center; margin-bottom: 20px;}
    .faq-card-answer-blue { background: #0E172B; border-radius: 0 0 15px 15px; padding: 20px; color: #FFF !important; text-align: center; margin-bottom: 20px;}

    div.stButton > button {
        background-color: #00D395 !important;
        color: white !important;
        font-weight: 800 !important;
        height: 60px !important;
        border-radius: 15px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- STAN APLIKACJI ---
if 'pokoje_pro' not in st.session_state: st.session_state.pokoje_pro = []
if 'pokoje' not in st.session_state: st.session_state.pokoje = []

# --- MENU BOCZNE ---

if branza == "Start":
    # Nagłówki główne
    st.markdown("<h1 style='text-align: center; color: #00D395; font-size: 50px; margin-top: 0; font-weight: 800;'>Witaj w ProCalc</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 26px; margin-bottom: 50px; color: #495057;'>Twój Cyfrowy Kosztorysant Wykończeniowy</h3>", unsafe_allow_html=True)
    
    # 2. Kontener centralny (Dla kogo jest ProCalc)
    col_c1, col_center, col_c2 = st.columns([1, 4, 1])
    
    with col_center:
        st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 40px; font-weight: 800;'>Dla kogo jest ProCalc?</h2>", unsafe_allow_html=True)
        
        # Używamy ujednoliconej klasy custom-card z efektem hover
        benefity = [
            ["Inwestorzy", "Błyskawiczna analiza ROI i rentowności flipa. Podejmuj decyzje zakupowe w oparciu o twarde dane, a nie intuicję."],
            ["Ekipy Wykonawcze", "Precyzyjne listy materiałowe z dokładnością do jednego worka. Koniec z przestojami, błędami i zbędnymi kursami."],
            ["Klienci Prywatni", "Pełna kontrola nad budżetem remontowym. Wiesz dokładnie, ile zapłacisz za materiał i robociznę."]
        ]

        # POPRAWKA 1: Inicjalizacja kolumn, której brakowało
        cols_ben = st.columns(3)

        for i, (tytul, tekst) in enumerate(benefity):
            with cols_ben[i]:
                st.markdown(f"""
                <div class="custom-card">
                    <div class="card-title">{tytul}</div>
                    <div class="card-text">{tekst}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Przycisk w stylu PRO
        # Kontener centrujący dla przycisku i napisu pod nim
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        
        # Sam przycisk (Streamlit automatycznie go wycentruje w tym divie dzięki CSS w sekcji style)
        if st.button("ZAŁÓŻ DARMOWE KONTO I ZAPISUJ KOSZTORYSY", use_container_width=True):
            st.session_state.branza = "Rejestracja"
            st.rerun()

        st.markdown("""
            <div style='text-align: center; width: 100%; margin-top: 15px;'>
                <p style='font-size: 15px; color: #6c757d; font-weight: 600;'>
                    ✅ Rejestracja zajmie Ci 30 sekund. Nie wymaga podpięcia karty płatniczej.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Co oferują nasze kalkulatory?</h2>", unsafe_allow_html=True)
    
    oferta = [
        ["Malowanie", "Finalne wykończenie powierzchni.", ["Wydajność farb", "Obliczanie m2"]], 
        ["Szpachlowanie", "Przygotowanie gładzi.", ["Masy sypkie", "Zbrojenie narożników"]],
        ["Tynkowanie", "Prace tynkarskie.", ["Tynki maszynowe", "Listwy i narożniki"]],
        ["Sucha Zabudowa", "Konstrukcje GK.", ["Profile CD/UD", "Płyty i wkręty"]],
        ["Elektryka", "Instalacja prądowa.", ["mb przewodów", "Osprzęt i rozdzielnica"]],
        ["Łazienka", "Kompleksowy remont.", ["Płytki i izolacja", "Biały montaż"]],
        ["Podłogi", "Panele i winyle.", ["Metraż + naddatek", "Listwy i podkłady"]],
        ["Drzwi", "Stolarka wewnętrzna.", ["Bezprzylgowe", "Ościeżnice regulowane"]],
        ["Premium PRO", "Dla profesjonalistów.", ["Raporty PDF", "Kalkulator ROI"]]
    ]

    cols_oferta = st.columns(3)
    for i, item in enumerate(oferta):
        with cols_oferta[i % 3]:
            # dynamiczna ramka dla PRO
            style_extra = "border: 2px solid #00D395; background-color: #F0FFF4 !important;" if item[0] == "Premium PRO" else ""
            
            st.markdown(f"""
            <div class="custom-card" style="{style_extra}">
                <div class="card-title">{item[0]}</div>
                <div class="card-text">{item[1]}</div>
                <ul class="card-list">
                    <li>{item[2][0]}</li>
                    <li>{item[2][1]}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    
    st.markdown("""
        <div style='text-align: center; width: 100%; padding: 20px;'>
            <p style='font-size: 26px; font-weight: 800; color: #1E1E1E; margin-bottom: 10px;'>
                GOTOWY DO WYCENY?
            </p>
            <p style='font-size: 20px; color: #00D395; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>
                Wybierz sekcję z menu bocznego i zacznij liczyć!
            </p>
        </div>
    """, unsafe_allow_html=True)

   # --- SEKCJA ZAUFANIA (PUNKTY) ---
    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Dlaczego warto nam zaufać?</h2>", unsafe_allow_html=True)
    
    # Otwieramy główny kontener centrujący dla całego bloku zalet
    st.markdown('<div style="display: flex; justify-content: center; width: 100%;">', unsafe_allow_html=True)
    
    # Tworzymy 2 kolumny o równej szerokości, ale w węższym kontenerze (np. 800px)
    # Używamy st.columns([1, 1]) wewnątrz st.container(), by zachować kontrolę
    
    zalety = [
        ["NORMY", "Algorytmy oparte na realnych normach zużycia materiałów"],
        ["DOŚWIADCZENIE", "Ponad 10 000 m² zrealizowanych inwestycji"],
        ["CENY", "Bazy cenowe aktualizowane co 30 dni zgodnie z rynkiem"],
        ["PRECYZJA", "Listy zakupowe ograniczające odpady"],
        ["EKSPERCI", "Konsultacje merytoryczne z fachowcami"],
        ["NIEZALEŻNOŚĆ", "Nie faworyzujemy żadnej marki"]
    ]

    # Tworzymy bazowy układ kolumn (tym razem 3, gdzie środkowa jest szeroka i trzyma treść)
    _, col_main, _ = st.columns([1, 5, 1])

    with col_main:
        # Tu tworzymy wewnętrzne pod-kolumny
        sub_l, sub_r = st.columns(2)
        
        for i, (tytul, opis) in enumerate(zalety):
            target_col = sub_l if i % 2 == 0 else sub_r
            
            with target_col:
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: 30px; padding-left: 20px;">
                    <div style="color: #00D395; font-size: 24px; margin-right: 15px; font-weight: bold; margin-top: -2px; line-height: 1;">✔</div>
                    <div style="font-size: 15px; color: #495057; line-height: 1.4;">
                        <b style="color: #1E1E1E; font-size: 16px; display: block; margin-bottom: 2px; text-transform: uppercase;">{tytul}</b>
                        <span style="display: block; opacity: 0.8;">{opis}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Zamykamy główny div
    st.markdown("<br>", unsafe_allow_html=True)
        
    # Przycisk Demo wyśrodkowany
    if st.button("SPRAWDŹ DARMOWE DEMO (MALOWANIE)", use_container_width=True, key="btn_demo_main"):
        st.session_state.branza = "Malowanie"
        st.rerun()

    st.markdown("<p style='text-align: center; font-size: 14px; color: gray;'>Nie wymaga logowania. Sprawdź jak to działa w 15 sekund.</p>", unsafe_allow_html=True)

    # --- SEKCJA FAQ ---
    # POPRAWKA 3: Wyrównane wcięcia dla sekcji FAQ
    st.markdown("<br><br><h2 style='text-align: center;'>Często Zadawane Pytania</h2>", unsafe_allow_html=True)
    
    col_f1, col_faq, col_f2 = st.columns([1, 2.5, 1])
    
    with col_faq:
        # Pytanie 1
        st.markdown("""
            <div class="faq-card-question">Czy wyceny materiałów są aktualne?</div>
            <div class="faq-card-answer">Tak. Nasze bazy cenowe są aktualizowane raz w miesiącu na podstawie średnich cen rynkowych z największych marketów i hurtowni.</div>
        """, unsafe_allow_html=True)

        # Pytanie 2
        st.markdown("""
            <div class="faq-card-question">Czy mogę zapisać swój kosztorys?</div>
            <div class="faq-card-answer-blue">Funkcja zapisywania i edycji wielu projektów jest dostępna dla zalogowanych użytkowników w wersji <b>Premium PRO</b>.</div>
        """, unsafe_allow_html=True)

        # Pytanie 3
        st.markdown("""
            <div class="faq-card-question">Jak dokładne są listy zakupowe?</div>
            <div class="faq-card-answer">Algorytmy uwzględniają oficjalne normy zużycia producentów oraz standardowy naddatek 10% na odpady i docięcia.</div>
        """, unsafe_allow_html=True)
        
        # Pytanie 4: Formaty płytek (Ciemny niebieski)
        st.markdown("""
            <div class="faq-card-question">Czy format płytek wpływa na wycenę?</div>
            <div class="faq-card-answer-blue">Oczywiście. W sekcji Łazienka możesz wybrać format (np. 120x60), a system automatycznie podniesie stawkę za robociznę i zużycie kleju.</div>
        """, unsafe_allow_html=True)

        # Pytanie 5: Ukryte koszty
        st.markdown("""
            <div class="faq-card-question">Czy kalkulator uwzględnia tzw. drobnicę?</div>
            <div class="faq-card-answer">Tak. System dolicza szacunkowe koszty folii, taśm, kołków czy gruntów, o których inwestorzy często zapominają przy planowaniu budżetu.</div>
        """, unsafe_allow_html=True)

        # Pytanie 6: Eksport do PDF
        st.markdown("""
            <div class="faq-card-question">Czy otrzymam listę zakupów do sklepu?</div>
            <div class="faq-card-answer-blue">Tak. Po zakończeniu obliczeń możesz wygenerować gotowy raport z listą materiałów, którą wystarczy pokazać sprzedawcy w hurtowni.</div>
        """, unsafe_allow_html=True)

   # --- KONIEC SEKCJI OBLICZEŃ BRANŻY (np. Tynków) ---
        # Upewnij się, że poniższy kod NIE JEST wsunięty (nie ma spacji na początku linii)
        
        # --- SEKCJA ROZWOJU PROJEKTU (ROADMAP) - WIDOCZNA NA STAŁE ---
        st.markdown("---")
        st.header("Plan Rozwoju Aplikacji (Roadmap)")
        st.write("Budujemy najbardziej kompletne narzędzie dla nowoczesnych wykonawców. Sprawdź, nad czym obecnie pracujemy:")
        
        col_dev1, col_dev2 = st.columns(2)
        
        with col_dev1:
            st.markdown("#### W TRAKCIE (Koncept/Dev)")
            st.info("**Live Progress (CRM)**\n\nInteraktywna checklista etapów prac. Zamykasz etap jednym kliknięciem, a system przelicza % zaawansowania dla inwestora.")
            st.info("**Dokumentacja Foto**\n\nMożliwość wgrywania zdjęć z budowy przypisanych do konkretnych etapów – pełna przejrzystość.")
            st.info("**Kalkulator Łazienki PRO**\n\nKompleksowe wyliczanie hydroizolacji, taśm narożnikowych i tynków pod glazurę.")
        
        with col_dev2:
            st.markdown("#### DO ZROBIENIA (Plany)")
            st.success("**Efekty Dekoracyjne** – Beton architektoniczny, stiuk, trawertyn.")
            st.success("**System Linków** – Unikalny adres budowy dla inwestora.")
            st.success("**Baza Danych (Cloud)** – Integracja z Firebase (zapisywanie projektów).")
            st.success("**Panel Marży** – Ukryte ustawienia cen i narzutów.")
        
        st.markdown("""
        <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border-left: 5px solid #ff4b4b;">
            <strong>Masz pomysł na ulepszenie?</strong><br>
            Napisz do nas! Rozwijamy ten projekt razem z wykonawcami, aby ułatwić codzienną pracę na budowie.
        </div>
        """, unsafe_allow_html=True) # Poprawione na unsafe_allow_html=True
        
        # --- KONIEC SEKCJI ROADMAP ---

    # TERAZ ELIF KONTAKT (również od lewej krawędzi)
elif branza == "Kontakt":
    st.markdown("<h1 style='text-align: center; color: #00D395;'>Kontakt</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-card" style="text-align: center;">
        <p class="card-text">Masz pytania? Napisz do nas!</p>
        <h3 style="color: #0E172B;">biuro@procalc.pl</h3>
        <p class="card-text">Infolinia: +48 123 456 789</p>
    </div>
    """, unsafe_allow_html=True)



# --- INICJALIZACJA STANU ---
if 'pokoje_pro' not in st.session_state:
    st.session_state.pokoje_pro = []

# --- SEKCJA: MALOWANIE ---
if branza == "Malowanie":
    st.subheader("Kalkulator Malarski")
    tab_fast, tab_pro = st.tabs(["⚡ Szybka Wycena", "💎 Kosztorys PRO"])

    # --- BAZA WIEDZY ---
    baza_biale = {
        "Śnieżka Eko (Akryl)": 14, "Dekoral Polinak": 19, "Tikkurila Anti-Reflex 2": 38,
        "Bondex Super White": 28, "Magnat Ultra Matt": 34, "Greinplast Comfort": 24
    }
    baza_kolory = {
        "Dekoral Akrylit W": 24, "Beckers It's Simple": 38, "Tikkurila Optiva 5": 52,
        "Magnat Ceramic": 62, "Dulux Kolory Świata": 28, "Bondex Smart Paint": 44
    }
    baza_grunty = {
        "Unigrunt Atlas (Standard)": 7, "Mapei Primer G (Premium)": 15,
        "Knauf Tiefengrund (Specjalistyczny)": 19, "Grunt Marketowy (Eko)": 4
    }
    baza_tasmy = {
        "Żółta Papierowa (Market)": 12, "Solid (Niebieska)": 24,
        "Blue Dolphin (Profesjonalna)": 34, "Tesa Precision (Premium)": 52, "3M / Scotch": 58
    }
    
    with tab_fast:
        st.info("Pełne możliwości w Kosztorys PRO.")

    with tab_fast:
        st.header("⚡ Błyskawiczny szacunek kosztów")
        col_input, col_spacer = st.columns([1, 1])
        with col_input:
            st.write("Podaj metraż podłogi, aby otrzymać orientacyjne koszty malowania całego pomieszczenia (ściany + sufity).")
            
            # Suwak z metrażem i input dla stawki
            m2_podloga_fast = st.slider("Metraż mieszkania / pokoju (m2 podłogi):", 1, 1000, 50)
            stawka_rob_fast = st.number_input("Twoja stawka za m2 robocizny (malowanie):", value=35)
        
            # Logika uproszczona: 
            # Zakładamy, że powierzchnia malowania (ściany + sufit) to ok. 3.5x pow. podłogi
            pow_malowania_fast = m2_podloga_fast * 3.5
            estymacja_robocizny = pow_malowania_fast * stawka_rob_fast
            
            # Estymacja materiałów: średnio 14 zł za m2 powierzchni malowania (farba, grunt, folia, akcesoria)
            estymacja_materialow = pow_malowania_fast * 14 
            
            # Wyświetlanie wyników w kolumnach
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                st.metric("Szacowana Robocizna", f"{round(estymacja_robocizny)} zł")
            with c_f2:
                st.metric("Szacowane Materiały", f"{round(estymacja_materialow)} zł")
                
            st.success(f"### Przybliżony koszt całkowity: **{round(estymacja_robocizny + estymacja_materialow)} zł**")
            
            # Adnotacja o wersji PRO
            st.markdown("""
            ---
            ### 💎 Chcesz większej precyzji?
            Przejdź do zakładki **Kosztorys PRO**, aby uzyskać dostęp do:
            *   **Pełnej bazy materiałów:** Wybór konkretnych marek farb (kolor/biała), gruntów i taśm.
            *   **Precyzyjnego planowania:** Możliwość dodawania każdej ściany z osobna (szerokość x wysokość).
            *   **Sztukaterii:** Kalkulator listew ściennych i sufitowych wraz z klejami.
            *   **Listy zakupowej:** Gotowe zestawienie ile dokładnie litrów farby i sztuk akcesoriów musisz kupić.
            """)

    with tab_pro:
        st.header("💎 Profesjonalny Arkusz Kalkulacyjny")
        
        # --- SEKCJA 1: SZYBKI SZACUNEK (Otwarty) ---
        st.subheader("⚡ Szybki szacunek materiałów i robocizny")
        col_f1, col_f2 = st.columns([1, 1.2])

        with col_f1:
            m_uzytkowy = st.number_input("Metraż mieszkania (podłoga m2):", min_value=1.0, value=50.0, key="pro_m_fast")
            stan_f = st.selectbox("Stan lokalu:", ["Deweloperski", "Zamieszkały (meble)"], key="pro_s_fast")
            
            st.markdown("**Wybór Produktów**")
            f_biala = st.selectbox("Farba BIAŁA (Sufity):", list(baza_biale.keys()), key="pro_fb")
            f_kolor = st.selectbox("Farba KOLOR (Ściany):", list(baza_kolory.keys()), key="pro_fk")
            f_grunt = st.selectbox("Marka Gruntu:", list(baza_grunty.keys()), key="pro_fg")
            f_tasma = st.selectbox("Rodzaj Taśmy:", list(baza_tasmy.keys()), key="pro_ft")
            
            stawka = st.slider("Twoja stawka za m2 robocizny:", 1, 100, 35, key="pro_r_fast")

            st.markdown("---")
            st.subheader("Sztukateria")
            mb_sztukaterii = st.number_input("Łączna długość listew (mb):", min_value=0.0, value=0.0, step=1.0, key="pro_sz_fast")
            typ_sztukaterii = st.selectbox("Rodzaj listew:", ["Styropianowe (Eko)", "Poliuretanowe (Twarde)", "Gipsowe (Premium)"], key="pro_tsz_fast")

        # --- LOGIKA OBLICZEŃ (Stała) ---
        m2_sufit = m_uzytkowy * 1.0
        m2_sciany = m_uzytkowy * 2.5
        m2_razem = m2_sufit + m2_sciany
        mnoznik = 1.0 if stan_f == "Deweloperski" else 1.3

        l_biala = (m2_sufit / 10) * 2
        l_kolor = (m2_sciany / 10) * 2
        l_grunt = m2_razem * 0.15
        szt_akryl = m_uzytkowy / 12
        szt_tasma = (m_uzytkowy / 15) * mnoznik
        
        stawki_szt = {"Styropianowe (Eko)": 25, "Poliuretanowe (Twarde)": 45, "Gipsowe (Premium)": 65}
        koszt_rob_sztukateria = mb_sztukaterii * stawki_szt[typ_sztukaterii]
        koszt_mat_sztukateria = (mb_sztukaterii / 8 + 0.4) * 25
            
        k_mat_sredni = (l_biala * baza_biale[f_biala]) + (l_kolor * baza_kolory[f_kolor]) + \
                       (l_grunt * baza_grunty[f_grunt]) + (szt_tasma * baza_tasmy[f_tasma]) + \
                       koszt_mat_sztukateria + 150 
        
        k_rob_total = (m2_razem * stawka) + koszt_rob_sztukateria

        with col_f2:
            st.subheader("Wyniki i Lista zakupów")
            
            # Obliczenia końcowe
            total_pro = k_mat_sredni + k_rob_total
            
            # --- PANEL FINANSOWY ---
            st.success(f"### RAZEM: **{round(total_pro)} zł**")
            
            c_money1, c_money2 = st.columns(2)
            with c_money1:
                st.metric("Twoja Robocizna", f"{round(k_rob_total)} zł")
            with c_money2: # <--- TUTAJ BYŁ BŁĄD (było c_res2)
                st.metric("Materiały (ok.)", f"{round(k_mat_sredni)} zł")
            
            st.markdown("---")

            # --- LISTA ZAKUPÓW (Widoczna na wierzchu) ---
            st.markdown("###Twoja lista zakupów")
            
            st.write(f"**Farby i Grunt:**")
            st.write(f"- Biała ({f_biala}): **{round(l_biala, 1)}L**")
            st.write(f"- Kolor ({f_kolor}): **{round(l_kolor, 1)}L**")
            st.write(f"- Grunt ({f_grunt}): **{round(l_grunt, 1)}L**")
            
            st.write(f"**Akcesoria:**")
            st.write(f"- Taśma ({f_tasma}): **{round(szt_tasma + 0.5)} szt.**")
            st.write(f"- Akryl szpachlowy: **{round(szt_akryl + 0.5)} szt.**")
            
            if mb_sztukaterii > 0:
                st.write(f"**Sztukateria:**")
                st.write(f"- Robocizna (montaż): **{round(koszt_rob_sztukateria)} zł**")
                # Tutaj dodajemy nazwę kleju:
                st.write(f"- Klej: **Bostik Mamut** ({int(mb_sztukaterii/8 + 1)} szt.)")
            
            st.info("Kwoty materiałów zawierają doliczony margines bezpieczeństwa (10%) oraz 150 zł na folie i wałki.")

        st.markdown("---")

        # --- SEKCJA 2: DODAWANIE ŚCIAN (Na wierzchu, bez expandera) ---
        st.subheader("➕ Dodaj konkretną ścianę do projektu")
        c1, c2, c3 = st.columns([2, 1, 1])
        nazwa_p = c1.text_input("Nazwa / Pomieszczenie:", "Salon - Ściana TV", key="wall_name")
        szer = c2.number_input("Szerokość (m):", min_value=0.1, value=4.0, step=0.1, key="wall_w")
        wys = c3.number_input("Wysokość (m):", min_value=0.1, value=2.6, step=0.1, key="wall_h")
        
        kolor_hex = st.color_picker("Kolor tej ściany:", "#D3D3D3", key="wall_c")
        
        if st.button("ZATWIERDŹ I DODAJ ŚCIANĘ", use_container_width=True):
            st.session_state.pokoje_pro.append({
                "pokoj": nazwa_p, "szer": szer, "wys": wys, "kolor": kolor_hex
            })
            st.rerun()

        # --- WYKAZ DODANYCH ELEMENTÓW ---
        if st.session_state.pokoje_pro:
            st.markdown("### Zestawienie szczegółowe")
            total_m2_walls = 0
            for i, s in enumerate(st.session_state.pokoje_pro):
                p_m2 = s['szer'] * s['wys']
                total_m2_walls += p_m2
                st.write(f"{i+1}. **{s['pokoj']}**: {s['szer']}m x {s['wys']}m = **{round(p_m2, 2)} m²**")
            
            st.info(f"Łączna powierzchnia dodanych ścian: **{round(total_m2_walls, 1)} m²**")
            
            if st.button("WYCZYŚĆ LISTĘ ŚCIAN"):
                st.session_state.pokoje_pro = []
                st.rerun()
                
        st.markdown("---")
        
        st.subheader("Zarządzanie Projektem")
        
        c_btn1, c_btn2 = st.columns(2)

        with c_btn1:
            if st.button("Wyczyść projekt PRO", use_container_width=True):
                st.session_state.pokoje_pro = []
                st.rerun()

        
        with c_btn2:
            try:
                from fpdf import FPDF
                import os
                from datetime import datetime

                # 1. Inicjalizacja PDF
                pdf = FPDF()
                pdf.add_page()

                # 2. KONFIGURACJA CZCIONKI INTER
                font_path = "Inter-Regular.ttf"
                if os.path.exists(font_path):
                    # Rejestrujemy czcionkę (nazwa, styl, ścieżka)
                    pdf.add_font("Inter", "", font_path)
                    pdf.set_font("Inter", size=12)
                    font_exists = True
                else:
                    pdf.set_font("Arial", size=12)
                    font_exists = False
                    st.warning("⚠️ Nie znaleziono pliku Inter-Black.ttf. Używam czcionki zastępczej.")

                # --- NAGŁÓWEK ---
                if os.path.exists("logo.png"):
                    pdf.image("logo.png", x=10, y=8, w=35)
                
                # Używamy Inter do nagłówka (rozmiar 18 dla efektu 'Black')
                pdf.set_font("Inter" if font_exists else "Arial", size=18)
                pdf.cell(0, 15, "PROCALC - RAPORT KOSZTORYSOWY", ln=True, align='C')
                pdf.ln(10)

                # --- LINIA SEPARATORA ---
                pdf.set_draw_color(0, 0, 0)
                pdf.line(10, 35, 200, 35)
                pdf.ln(5)

                # --- DANE PROJEKTU ---
                pdf.set_font("Inter" if font_exists else "Arial", size=10)
                data_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                pdf.cell(0, 8, f"Data: {data_str} | Metraz: {m_uzytkowy} m2", ln=True)
                pdf.ln(5)

                # --- SEKCJA 1: FINANSE (Tabela) ---
                pdf.set_fill_color(230, 230, 230)
                pdf.set_font("Inter" if font_exists else "Arial", size=12)
                pdf.cell(0, 10, " 1. PODSUMOWANIE KOSZTOW", ln=True, fill=True)
                
                pdf.set_font("Inter" if font_exists else "Arial", size=11)
                pdf.cell(95, 10, " Twoja Robocizna:", 1)
                pdf.cell(95, 10, f" {round(k_rob_total)} PLN", 1, ln=True)
                
                pdf.cell(95, 10, " Szacowane Materialy:", 1)
                pdf.cell(95, 10, f" {round(k_mat_sredni)} PLN", 1, ln=True)
                
                pdf.set_font("Inter" if font_exists else "Arial", size=13)
                pdf.cell(95, 12, " SUMA CALKOWITA:", 1)
                pdf.cell(95, 12, f" {round(total_pro)} PLN", 1, ln=True)
                pdf.ln(10)

                # --- SEKCJA 2: LISTA ZAKUPOWA ---
                pdf.set_font("Inter" if font_exists else "Arial", size=12)
                pdf.cell(0, 10, " 2. SZCZEGOLOWA LISTA ZAKUPOW", ln=True, fill=True)
                pdf.set_font("Inter" if font_exists else "Arial", size=10)
                pdf.ln(2)

                # Przygotowanie listy z polskimi znakami (fpdf2 to obsłuży!)
                lista_pdf = {
                    "Farba Biała (Sufity)": f"{round(l_biala, 1)}L ({f_biala})",
                    "Farba Kolor (Ściany)": f"{round(l_kolor, 1)}L ({f_kolor})",
                    "Grunt głęboko penetrujący": f"{round(l_grunt, 1)}L ({f_grunt})",
                    "Taśma malarska": f"{round(szt_tasma + 0.5)} szt. ({f_tasma})",
                    "Akryl szpachlowy": f"{round(szt_akryl + 0.5)} szt."
                }
                
                if mb_sztukaterii > 0:
                    lista_pdf["Klej do listew"] = f"Bostik Mamut ({int(mb_sztukaterii/8 + 1)} szt.)"

                for produkt, opis in lista_pdf.items():
                    pdf.cell(0, 8, f"- {produkt}: {opis}", ln=True)

                # --- STOPKA ---
                pdf.set_y(-25)
                pdf.set_font("Inter" if font_exists else "Arial", size=8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, "Wygenerowano automatycznie przez proCalc. Kosztorys nie stanowi oferty handlowej.", 0, 0, 'C')

                # Generowanie PDF jako bytes (standard fpdf2)
                pdf_output = pdf.output()
                
                st.download_button(
                    label="Pobierz Raport PDF (Inter Black)",
                    data=bytes(pdf_output),
                    file_name=f"Kosztorys_proCalc_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Błąd PDF: {e}")

elif branza == "Szpachlowanie":
    st.header("Kalkulator Gładzi i Przygotowania Ścian")

    # 1. INICJALIZACJA BAZY DANYCH (Musi być na początku sekcji)
    baza_sypkie = {
        "Cekol C-45 (20kg)": {"cena": 58, "waga": 20},
        "FransPol GS-2 (20kg)": {"cena": 50, "waga": 20},
        "Dolina Nidy Omega (20kg)": {"cena": 37, "waga": 20},
        "Atlas Gipsar Uni (20kg)": {"cena": 52, "waga": 20}
    }
    baza_gotowe = {
        "Śmig A-2 (Wiadro 17kg)": {"cena": 63, "waga": 17},
        "Knauf Goldband Finish (18kg)": {"cena": 50, "waga": 18},
        "Knauf Goldband Finish (28kg)": {"cena": 72, "waga": 28},
        "Knauf Fill & Finish (20kg)": {"cena": 115, "waga": 20},
        "Sheetrock Blue (28kg)": {"cena": 145, "waga": 28},
        "Atlas GTA (20kg)": {"cena": 94, "waga": 20}
    }
    baza_grunty_szp = {
        "Atlas Unigrunt (Standard)": 7,
        "Knauf Tiefengrund (Premium)": 18,
        "Mapei Primer G": 15,
        "Ceresit CT 17": 11
    }

    if 'pokoje_szp' not in st.session_state:
        st.session_state.pokoje_szp = []

    tab_s1, tab_s2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    # ==========================================
    # ZAKŁADKA 1: SZYBKA WYCENA (MINIMALISTYCZNA)
    # ==========================================
    with tab_s1:
        st.subheader("Błyskawiczny szacunek kosztów")
        m2_podl_fast = st.number_input("Podaj metraż podłogi mieszkania (m2):", min_value=1.0, value=50.0)
        
        # Logika uproszczona: 3.5m2 ściany na 1m2 podłogi * średnia cena rynkowa (ok. 80 zł/m2 za wszystko)
        szacunek_total = m2_podl_fast * 3.5 * 80 
        
        st.success(f"### Szacowany koszt całkowity: **ok. {round(szacunek_total)} PLN**")
        st.write("W tym orientacyjnie:")
        st.write(f"- Robocizna: **{round(szacunek_total * 0.65)} PLN**")
        st.write(f"- Materiały: **{round(szacunek_total * 0.35)} PLN**")
        st.info("Aby wybrać konkretne gładzie, ustawić swoją stawkę i dodać pomieszczenia, przejdź do **Detale PRO**.")

    # ==========================================
    # ZAKŁADKA 2: DETALE PRO
    # ==========================================
    with tab_s2:
        st.subheader("Konfiguracja Wykonania (PRO)")
        
        # --- A. WYBÓR MATERIAŁÓW I STAWEK ---
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            typ_g_pro = st.radio("Rodzaj gładzi:", ["Gotowa (Wiadro)", "Sypka (Worek)"], horizontal=True, key="p_typ")
            if typ_g_pro == "Sypka (Worek)":
                wybrana_g = st.selectbox("Wybierz produkt:", list(baza_sypkie.keys()), key="p_syp")
                dane_g = baza_sypkie[wybrana_g]
                norma_g = 1.2
            else:
                wybrana_g = st.selectbox("Wybierz produkt:", list(baza_gotowe.keys()), key="p_got")
                dane_g = baza_gotowe[wybrana_g]
                norma_g = 1.8
            
            wybrany_grunt = st.selectbox("Wybierz Grunt:", list(baza_grunty_szp.keys()), key="p_gru")

        with col_c2:
            l_warstw = st.slider("Liczba warstw gładzi:", 1, 3, 2, key="p_war")
            stawka_szp = st.number_input("Twoja stawka za m2 (robocizna):", 1, 300, 50, key="p_sta")

        st.markdown("---")
        
        # --- B. DODAWANIE POMIESZCZEŃ (TERAZ ZAWSZE WIDOCZNE) ---
# --- B. WYBÓR METODY POMIARU ---
        st.subheader("📏 Metraż prac")
        metoda_pomiaru = st.radio(
            "Wybierz sposób podania metrażu:",
            ["Wpisz ogólny metraż ścian (Szybko)", "Dodaj konkretne pomieszczenia (Dokładnie)"],
            horizontal=True,
            key="metoda_szp"
        )

        m2_total = 0.0
        podl_total = 0.0

        if metoda_pomiaru == "Wpisz ogólny metraż ścian (Szybko)":
            # Opcja 1: Suwak
            m2_total = st.slider("Podaj łączny metraż ścian i sufitów (m2):", 5, 1000, 150, step=5)
            podl_total = m2_total / 3.5  # Szacunek podłogi pod dodatki (narożniki itp.)
            st.info(f"Przyjęto łączny metraż: {m2_total} m²")

        else:
            # Opcja 2: Dodawanie pomieszczeń
            cp1, cp2 = st.columns(2)
            with cp1:
                naz_p = st.text_input("Nazwa pomieszczenia:", placeholder="np. Kuchnia", key="p_naz")
                dl_p = st.number_input("Długość (m):", 0.0, 50.0, 4.0, key="p_dl")
                sz_p = st.number_input("Szerokość (m):", 0.0, 50.0, 3.0, key="p_sz")
            with cp2:
                wy_p = st.number_input("Wysokość (m):", 0.0, 10.0, 2.6, key="p_wy")
                suf_p = st.checkbox("Szpachlować sufit?", value=True, key="p_suf_check")
                ok_drz = st.number_input("Odliczenia okna/drzwi (m2):", 0.0, 50.0, 3.5, key="p_odlicz")

            if st.button("Zapisz i dodaj do listy", use_container_width=True):
                p_netto = (((dl_p + sz_p) * 2 * wy_p) + (dl_p * sz_p if suf_p else 0)) - ok_drz
                if p_netto > 0:
                    st.session_state.pokoje_szp.append({
                        "nazwa": naz_p or f"Pokój {len(st.session_state.pokoje_szp)+1}",
                        "netto": p_netto,
                        "podloga": dl_p * sz_p
                    })
                    st.rerun()

            # Wyświetlanie listy pokoi i sumowanie metrażu
            if st.session_state.pokoje_szp:
                st.markdown("---")
                for i, p in enumerate(st.session_state.pokoje_szp):
                    c_l, c_b = st.columns([5, 1])
                    c_l.info(f"**{p['nazwa']}**: {round(p['netto'], 1)} m²")
                    if c_b.button("Usuń", key=f"del_p_{i}"):
                        st.session_state.pokoje_szp.pop(i)
                        st.rerun()
                
                m2_total = sum(p["netto"] for p in st.session_state.pokoje_szp)
                podl_total = sum(p["podloga"] for p in st.session_state.pokoje_szp)

        # --- C. WYNIKI (Wykonują się RAZ na samym końcu) ---
        if m2_total > 0:
            # Obliczenia materiałowe
            kg_gladzi = m2_total * norma_g * l_warstw
            szt_gladzi = int((kg_gladzi / dane_g["waga"]) + 0.99)
            
            koszt_m_gladzi = szt_gladzi * dane_g["cena"]
            koszt_m_grunt = (m2_total * 0.2 / 5 + 0.99) * baza_grunty_szp[wybrany_grunt]
            koszt_m_dodatki = podl_total * 15 
            
            # Sumy końcowe
            robocizna_total = m2_total * stawka_szp
            materiały_total = koszt_m_gladzi + koszt_m_grunt + koszt_m_dodatki
            suma_total = robocizna_total + materiały_total
            
            # Wyświetlanie na stronie
            st.markdown("---")
            st.success(f"### WARTOŚĆ CAŁKOWITA: **{round(suma_total)} PLN**")
            
            res1, res2 = st.columns(2)
            res1.metric("Twoja Robocizna", f"{round(robocizna_total)} PLN")
            res2.metric("Materiały", f"{round(materiały_total)} PLN")
            
            # Tutaj wstaw kod przycisków PDF (with c_pdf1, c_pdf2 itd.)

            # Przycisk PDF (taki sam jak wcześniej)
            # ... (tutaj kod generatora PDF z poprzedniego kroku)
            # --- GENEROWANIE PDF ---
        st.markdown("---")
        c_pdf1, c_pdf2 = st.columns(2)
            
        with c_pdf1:
            if st.button("Wyczyść wszystko", use_container_width=True):
                st.session_state.pokoje_szp = []
                st.rerun()
                    
        with c_pdf2:
            try:
                from fpdf import FPDF
                import os
                from datetime import datetime

                pdf = FPDF()
                pdf.add_page()
                    
                # Czcionka Inter
                f_path = "Inter-Regular.ttf"
                if os.path.exists(f_path):
                    pdf.add_font("Inter", "", f_path)
                    pdf.set_font("Inter", size=12)
                    font_ok = True
                else:
                    pdf.set_font("Arial", size=12)
                    font_ok = False

                # Logo i Nagłówek
                if os.path.exists("logo.png"):
                    pdf.image("logo.png", x=10, y=8, w=35)
                    
                    pdf.set_font("Inter" if font_ok else "Arial", size=16)
                    pdf.cell(0, 15, "RAPORT SZPACHLOWANIA - PROCALC", ln=True, align='C')
                    pdf.ln(5)
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(10)

                    # Treść PDF
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font("Inter" if font_ok else "Arial", size=12)
                    pdf.cell(0, 10, " 1. PODSUMOWANIE KOSZTOW", ln=True, fill=True)
                    
                    pdf.set_font("Inter" if font_ok else "Arial", size=11)
                    pdf.cell(95, 10, " Robocizna:", 1)
                    pdf.cell(95, 10, f" {round(robocizna_total)} PLN", 1, ln=True)
                    pdf.cell(95, 10, " Materialy:", 1)
                    pdf.cell(95, 10, f" {round(materiały_total)} PLN", 1, ln=True)
                    
                    pdf.set_font("Inter" if font_ok else "Arial", size=12)
                    pdf.cell(95, 12, " RAZEM:", 1)
                    pdf.cell(95, 12, f" {round(suma_total)} PLN", 1, ln=True)
                    
                    pdf.ln(10)
                    pdf.set_font("Inter" if font_ok else "Arial", size=12)
                    pdf.cell(0, 10, " 2. SZCZEGOLY ZAMOWIENIA", ln=True, fill=True)
                    pdf.set_font("Inter" if font_ok else "Arial", size=10)
                    
                    # TUTA BYŁ BŁĄD - poprawione zmienne:
                    szt_gruntu = int(m2_total * 0.2 / 5 + 0.99) # Wyliczamy bańki gruntu dla PDF
                    
                    pdf.cell(0, 8, f"- Gladz: {wybrana_g} ({szt_gladzi} szt.)", ln=True)
                    pdf.cell(0, 8, f"- Grunt: {wybrany_grunt} ({szt_gruntu} baniek 5L)", ln=True)
                    pdf.cell(0, 8, f"- Liczba warstw: {l_warstw}", ln=True)
                    pdf.cell(0, 8, f"- Calkowita pow. netto: {round(m2_total, 1)} m2", ln=True)

                    pdf_bytes = pdf.output()
                    st.download_button(
                        label="Pobierz PDF (PRO)",
                        data=bytes(pdf_bytes),
                        file_name=f"Szpachlowanie_Raport_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Błąd PDF: {e}")

# --- SEKCJA: PODŁOGI ---
elif branza == "Podłogi":
    st.header("Kalkulator Podłóg: Panele, Deska i Płytki")
    tab_p1, tab_p2 = st.tabs(["⚡ Szybka Wycena", "💎 Szczegóły Montażu"])

    with tab_p1:
        col_p1, col_p2 = st.columns([1, 1.2])
        
        with col_p1:
            m2_p = st.number_input("Metraż podłogi (m2):", min_value=0.1, value=20.0, step=0.1, key="pod_m")
            
            system_montazu = st.radio("System montażu:", 
                                     ["Pływający (Na podkładzie)", 
                                      "Klejony (Na gruncie i kleju)", 
                                      "Płytki / Gres (System poziomujący)"])
            
            if system_montazu == "Płytki / Gres (System poziomujący)":
                st.markdown("---")
                st.subheader("Parametry płytek")
                c_pl1, c_pl2 = st.columns(2)
                dl_p = c_pl1.number_input("Długość płytki (cm):", 10, 200, 60)
                sz_p = c_pl2.number_input("Szerokość płytki (cm):", 10, 200, 60)
                typ_ukladania = "Płytki (10% zapasu)"
                m2_paczka = st.number_input("M2 w paczce płytek:", min_value=0.1, value=1.44, step=0.01)
            else:
                typ_ukladania = st.selectbox("Sposób układania:", ["Zwykły panel (7% zapasu)", "Jodełka (20% zapasu)"])
                m2_paczka = st.number_input("M2 w paczce paneli/desek:", min_value=0.1, value=2.22, step=0.01)
            
            st.markdown("---")
            domyslna_stawka = 120 if "Płytki" in system_montazu else (45 if "Zwykły" in typ_ukladania else 120)
            stawka_podl = st.slider("Twoja stawka za m2 montażu (zł):", 1, 250, domyslna_stawka)

        # --- LOGIKA OBLICZEŃ ---
        if "Płytki" in system_montazu:
            zapas = 0.10
        else:
            zapas = 0.07 if "Zwykły" in typ_ukladania else 0.20
            
        m2_z_zapasem = m2_p * (1 + zapas)
        paczki_szt = int(m2_z_zapasem / m2_paczka + 0.99)
        
        info_zakup = [] # Lista do przechowywania pozycji zakupowych

        if system_montazu == "Pływający (Na podkładzie)":
            wybrany_mat = st.selectbox("Rodzaj podkładu:", ["Premium (Rolka 8m2)", "Ecopor (Paczka 7m2)", "Standard (Pianka 10m2)"])
            wydajnosci = {"Premium (Rolka 8m2)": 8, "Ecopor (Paczka 7m2)": 7, "Standard (Pianka 10m2)": 10}
            ceny_p = {"Premium (Rolka 8m2)": 160, "Ecopor (Paczka 7m2)": 45, "Standard (Pianka 10m2)": 30}
            szt_podkladu = int(m2_p / wydajnosci[wybrany_mat] + 0.99)
            koszt_akc = szt_podkladu * ceny_p[wybrany_mat]
            info_zakup.append(f"Podkład {wybrany_mat}: {szt_podkladu} szt.")

        elif system_montazu == "Klejony (Na gruncie i kleju)":
            kg_kleju = m2_p * 1.2
            l_gruntu = m2_p * 0.15
            koszt_akc = m2_p * 55 
            info_zakup.append(f"Klej do podłóg (15kg): {int(kg_kleju/15 + 0.99)} wiader")
            info_zakup.append(f"Grunt do posadzki (5L): {int(l_gruntu/5 + 0.99)} baniek")

        else: # Płytki / Gres
            zuzycie_m2 = (1 / ((dl_p/100) * (sz_p/100))) * 4
            suma_klipsow = int(zuzycie_m2 * m2_p * 1.1)
            op_klipsy = int(suma_klipsow / 100 + 0.99)
            kg_kleju_gres = m2_p * 5.0
            worki_kleju = int(kg_kleju_gres / 25 + 0.99)
            
            koszt_akc = (op_klipsy * 35) + (worki_kleju * 65)
            info_zakup.append(f"System poziomujący (klipsy): {op_klipsy} op. (po 100 szt.)")
            info_zakup.append(f"Klej S1 (25kg): {worki_kleju} worków")
            info_zakup.append("Kliny do systemu: wielorazowe (sprawdzić stan)")

        k_robocizna = m2_p * stawka_podl
        total_mat = (paczki_szt * m2_paczka * 100) + koszt_akc 

        with col_p2:
            st.subheader("Podsumowanie Kosztorysu")
            
            # Obliczamy sumę BEZ ceny samych płytek/paneli (tylko Twoja praca + systemy/chemia)
            usluga_plus_chemia = k_robocizna + koszt_akc
            
            # Wyświetlamy główną kwotę jako koszt realizacji (robocizna + materiały pomocnicze)
            st.success(f"### KOSZT REALIZACJI: **{round(usluga_plus_chemia)} PLN**")
            st.caption("Cena obejmuje robociznę oraz niezbędną chemię/systemy montażowe. Nie zawiera ceny okładziny (płytek/paneli).")

            c1, c2 = st.columns(2)
            c1.metric("Twoja Robocizna", f"{round(k_robocizna)} zł")
            c2.metric("Chemia / Systemy", f"{round(koszt_akc)} zł")

            st.markdown("---")
            st.markdown("📦 **PEŁNA LISTA ZAKUPÓW (Co musi być na budowie):**")
            
            # 1. MATERIAŁ GŁÓWNY (WYKOŃCZENIOWY)
            cena_materialu_szacunek = paczki_szt * m2_paczka * 100 # szacunkowe 100zł/m2
            st.write(f"🛒 **Płytki/Panele:** {paczki_szt} paczek (ok. {round(paczki_szt * m2_paczka, 2)} m²)")
            st.caption(f"Szacowany koszt okładziny: ~{round(cena_materialu_szacunek)} zł (przyjęto ok. 100zł/m²)")

            # 2. MATERIAŁY POMOCNICZE (WLICZONE W WYCENĘ REALIZACJI)
            for item in info_zakup:
                st.write(f"🛠️ **{item.split(':')[0]}:** {item.split(':')[1] if ':' in item else ''}")
            
            if "Płytki" in system_montazu:
                st.info(f"Wyliczono system poziomujący dla formatu {dl_p}x{sz_p} cm: ok. {int(zuzycie_m2)} klipsów/m².")
            
            st.markdown("---")
            # Całkowity koszt inwestycji (z płytkami)
            suma_z_okladzina = usluga_plus_chemia + cena_materialu_szacunek
            st.warning(f"**Szacowany całkowity koszt inwestycji z materiałem:** ok. {round(suma_z_okladzina)} zł")
            
            # Czas pracy
            tempo = 8 if "Płytki" in system_montazu else (25 if "Pływający" in system_montazu else 12)
            st.write(f"⏱️ **Przewidywany czas prac:** ok. {round(m2_p/tempo + 1)} dni")

        # --- 5. GENERATOR PDF (PODŁOGI) ---
        st.markdown("---")
        if st.button("📄 Generuj Ofertę PDF (Podłoga)"):
            try:
                from fpdf import FPDF
                from datetime import datetime

                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                pdf.set_font('DejaVu', '', 16)
                
                # Nagłówek
                pdf.cell(200, 10, txt="KOSZTORYS PRAC PODŁOGOWYCH", ln=True, align='C')
                pdf.set_font('DejaVu', '', 10)
                pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align='C')
                pdf.ln(10)

                # Tabela parametrów
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(95, 10, "Parametr", 1, 0, 'L', fill=True)
                pdf.cell(95, 10, "Wartość", 1, 1, 'L', fill=True)
                
                pdf.cell(95, 10, "Metraż całkowity", 1)
                pdf.cell(95, 10, f"{m2_p} m2", 1, 1)
                pdf.cell(95, 10, "System montażu", 1)
                pdf.cell(95, 10, f"{system_montazu}", 1, 1)
                
                if "Płytki" in system_montazu:
                    pdf.cell(95, 10, "Format płytki", 1)
                    pdf.cell(95, 10, f"{dl_p}x{sz_p} cm", 1, 1)

                pdf.ln(10)

                # Podsumowanie Finansowe
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(200, 10, txt="PODSUMOWANIE KOSZTÓW:", ln=True, align='L')
                pdf.set_font('DejaVu', '', 10)
                
                pdf.cell(140, 10, "1. Robocizna (Montaż)", 1)
                pdf.cell(50, 10, f"{round(k_robocizna)} zł", 1, 1, 'R')
                
                pdf.cell(140, 10, "2. Materiały pomocnicze (Chemia/Systemy)", 1)
                pdf.cell(50, 10, f"{round(koszt_akc)} zł", 1, 1, 'R')
                
                pdf.set_font('DejaVu', '', 11)
                pdf.cell(140, 10, "ŁĄCZNIE DO ZAPŁATY (Usługa + Chemia):", 1, 0, 'L', fill=True)
                pdf.cell(50, 10, f"{round(usluga_plus_chemia)} zł", 1, 1, 'R', fill=True)
                
                pdf.ln(5)
                pdf.set_font('DejaVu', '', 9)
                pdf.multi_cell(190, 5, txt="UWAGA: Powyższa kwota nie zawiera kosztu zakupu okładziny (paneli/płytek). "
                                           "Koszt okładziny zależy od wybranego przez klienta modelu.")
                
                pdf.ln(10)
                
                # Lista zakupów
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(200, 10, txt="LISTA ZAKUPÓW (Do dostarczenia na budowę):", ln=True, align='L')
                pdf.set_font('DejaVu', '', 10)
                
                pdf.cell(190, 10, f"- Okładzina główna: {paczki_szt} paczek (z zapasem {int(zapas*100)}%)", ln=True)
                for item in info_zakup:
                    pdf.cell(190, 10, f"- {item}", ln=True)

                # Generowanie pliku
                pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button(
                    label="📥 Pobierz kosztorys PDF",
                    data=pdf_output,
                    file_name=f"Kosztorys_Podloga_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Błąd podczas generowania PDF: {e}")
                      
# --- SEKCJA: TYNKOWANIE ---
elif branza == "Tynkowanie":
    st.header("Kalkulator Tynków i Suchego Tynku")
    
    # --- BAZA DANYCH ---
    baza_masy = {
        "Knauf Uniflot (Premium)": 115, 
        "Knauf Vario (Bardzo elastyczna)": 95,
        "Dolina Nidy Start (Ekonomiczna)": 45,
        "Franspol (Standard)": 55
    }

    baza_tynkow = {
        "Knauf MP 75 (Maszynowy Gipsowy)": {"cena": 25, "waga": 30, "norma": 0.8, "typ": "mokry"},
        "Baumit MPI25 Cem-Wap ": {"cena": 27, "waga": 30, "norma": 1.4, "typ": "mokry"},
        "Wyklejanie Płytami GK (Suchy Tynk)": {"cena_plyta": 35, "cena_klej": 24, "typ": "drywall"}
    }
    
    baza_grunt_kwarc = {
        "Dolina Nidy Inter-Grunt (20kg)": 140, 
        "Knauf Betokontakt (20kg)": 200, 
        "Atlas Grunto-Plast (20kg)": 110
    }

    tab_t1, tab_t2 = st.tabs(["⚡ Szybka Wycena", "💎 Detale PRO"])

    # --- TAB 1: SZYBKA WYCENA ---
    with tab_t1:
        st.subheader("Błyskawiczny szacunek")
        m2_podl_fast = st.number_input("Metraż mieszkania (podłoga m2):", 1.0, 500.0, 50.0)
        
        # Uproszczona logika: Średnio 3x metraż podłogi, średnia cena 85 zł/m2 (robocizna + mat)
        szacunkowy_metraz = m2_podl_fast * 3.0
        szacunkowy_koszt = szacunkowy_metraz * 85
        
        st.metric("Przybliżony koszt całkowity", f"{round(szacunkowy_koszt)} PLN")
        st.caption(f"Szacowany metraż ścian i sufitów: ok. {round(szacunkowy_metraz)} m²")
        
        st.markdown("---")
        st.info("""
        **Co zyskujesz w wersji PRO?**
        * Wybór konkretnych systemów (Gipsowe, Cem-Wap, GK).
        * Precyzyjne ustawienie grubości tynku i stawek.
        * Pełna lista zakupów (liczba worków, wiader, płyt).
        * Profesjonalny raport PDF dla klienta.
        """)

    # --- TAB 2: DETALE PRO ---
    with tab_t2:
        col_t1, col_t2 = st.columns([1, 1.2])
        
        with col_t1:
            st.subheader("Konfiguracja")
            m2_podl_pro = st.number_input("Metraż podłogi (m2):", 1.0, 500.0, 50.0, key="tyn_m_pro")
            wybrany_tynk = st.selectbox("Wybierz system:", list(baza_tynkow.keys()))
            dane_t = baza_tynkow[wybrany_tynk]
            
            # Logika powierzchni PRO
            mnoznik = 3.5 if dane_t["typ"] == "mokry" else 2.5
            m2_rob_pro = m2_podl_pro * mnoznik
            st.warning(f"Powierzchnia obliczeniowa: **{round(m2_rob_pro, 1)} m²**")

            if dane_t["typ"] == "drywall":
                typ_tasmy = st.radio("Rodzaj zbrojenia łączy:", ["Wszystko Tuff-Tape (Pancerne)", "Tuff-Tape + Flizelina"])
                wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy.keys()))
                grubosc_t = 0 # Nie dotyczy GK
            else:
                wybrany_grunt_t = st.selectbox("Wybierz grunt kwarcowy:", list(baza_grunt_kwarc.keys()))
                grubosc_t = st.slider("Średnia grubość tynku (mm):", 10, 40, 15)
            
            stawka_rob_t = st.number_input("Stawka robocizny (zł/m2):", 10, 200, 50)

            st.markdown("---")
            st.subheader("Stolarka (Okna i Drzwi)")
            
            # 1. Definicja standardowych wymiarów (Szer x Wys w cm)
            std_okna = {
                "Własny wymiar": None,
                "60x60 (Łazienkowe)": (60, 60),
                "90x120 (Jednoskrzydłowe)": (90, 120),
                "120x120 (Standard)": (120, 120),
                "150x150 (Duże)": (150, 150),
                "90x210 (Balkonowe)": (90, 210),
                "180x210 (Balkonowe podwójne)": (180, 210),
                "240x210 (Tarasowe HS)": (240, 210),
                "100x210 (Drzwi wejściowe)": (100, 210)
            }

            wybor_okna = st.selectbox("Wybierz typ okna:", list(std_okna.keys()))
            
            col_o1, col_o2 = st.columns(2)
            if wybor_okna == "Własny wymiar":
                w_szer = col_o1.number_input("Szerokość (cm):", 10, 600, 100)
                w_wys = col_o2.number_input("Wysokość (cm):", 10, 600, 120)
            else:
                w_szer, w_wys = std_okna[wybor_okna]
                col_o1.info(f"Szer: {w_szer} cm")
                col_o2.info(f"Wys: {w_wys} cm")

            ile_okien = st.number_input("Liczba takich okien (szt.):", 1, 50, 1)

            if "lista_okien_tyn" not in st.session_state:
                st.session_state.lista_okien_tyn = []

            if st.button("➕ Dodaj okna do zestawienia", use_container_width=True):
                st.session_state.lista_okien_tyn.append({
                    "nazwa": wybor_okna,
                    "szer": w_szer,
                    "wys": w_wys,
                    "szt": ile_okien
                })
                st.rerun()

            # Wyświetlanie listy okien
            if st.session_state.lista_okien_tyn:
                for i, o in enumerate(st.session_state.lista_okien_tyn):
                    c_ok1, c_ok2 = st.columns([4, 1])
                    c_ok1.caption(f"{o['szt']}x {o['nazwa']} ({o['szer']}x{o['wys']})")
                    if c_ok2.button("🗑️", key=f"del_o_{i}"):
                        st.session_state.lista_okien_tyn.pop(i)
                        st.rerun()

        # --- OBLICZENIA PRO ---
        if dane_t["typ"] == "mokry":
            kg_na_m2_t = dane_t["norma"] * grubosc_t
            kg_razem_t = m2_rob_pro * kg_na_m2_t
            worki_t = int(kg_razem_t / dane_t["waga"] + 0.99)
            wiadra_gruntu = int((m2_rob_pro * 0.3) / 20 + 0.99)
            koszt_mat_t = (worki_t * dane_t["cena"]) + (wiadra_gruntu * baza_grunt_kwarc[wybrany_grunt_t]) + (m2_rob_pro * 5)
            lista_zakupow = [
                (f"Tynk {wybrany_tynk}", f"{worki_t} worków"),
                (f"Grunt {wybrany_grunt_t}", f"{wiadra_gruntu} wiader 20kg"),
                ("Narożniki i profile", "Zestaw")
            ]
        else:
            liczba_plyt = int((m2_rob_pro * 1.1) / 3.12 + 0.99)
            worki_kleju = int(liczba_plyt / 2.5 + 0.99)
            worki_masy = int((m2_rob_pro * 0.5) / 25 + 0.99)
            cena_tasmy = 150 if "Tuff-Tape" in typ_tasmy else 70
            koszt_mat_t = (liczba_plyt * dane_t["cena_plyta"]) + (worki_kleju * dane_t["cena_klej"]) + \
                          (worki_masy * baza_masy[wybrana_masa]) + cena_tasmy + (m2_rob_pro * 2)
            lista_zakupow = [
                ("Płyty GK (1.2x2.6m)", f"{liczba_plyt} szt."),
                ("Klej Perlfix", f"{worki_kleju} worków"),
                (f"Masa {wybrana_masa}", f"{worki_masy} szt."),
                ("Taśmy i zbrojenie", "Zgodnie z wyborem")
            ]
       # --- LOGIKA STOLARKI (OBLICZENIA) ---
        total_mb_naroznikow = 0.0
        total_m2_folii = 0.0
        total_mb_tasmy = 0.0

        for o in st.session_state.get("lista_okien_tyn", []):
            s = o["szer"] / 100 
            w = o["wys"] / 100
            szt = o["szt"]
            
            total_mb_naroznikow += (2 * w + s) * szt
            total_m2_folii += (s * w * szt) * 1.1
            total_mb_tasmy += (2 * s + 2 * w) * szt

        # Przeliczenie na opakowania (prawidłowe nazwy zmiennych)
        szt_naroznik_3m = int(total_mb_naroznikow / 3 + 0.99)
        rolki_tasmy_50m = int(total_mb_tasmy / 50 + 0.99)
        szt_folii_op = int(total_m2_folii / 20 + 0.99)

        koszt_stolarki = (szt_naroznik_3m * 8) + (rolki_tasmy_50m * 25) + (szt_folii_op * 15)

        # TO JEST KLUCZOWE MIEJSCE: Dodajemy do listy zakupów zanim wyświetlimy wyniki
        if total_mb_naroznikow > 0:
            lista_zakupow.append(("Narożniki aluminiowe (3m)", f"{szt_naroznik_3m} szt."))
            lista_zakupow.append(("Taśma tynkarska (50m)", f"{rolki_tasmy_50m} rolka/i"))
            lista_zakupow.append(("Folia ochronna", f"{szt_folii_op} op."))

        # Podsumowanie kosztów
        koszt_mat_t += koszt_stolarki
        koszt_rob_t = m2_rob_pro * stawka_rob_t
        suma_tynki = koszt_mat_t + koszt_rob_t

        with col_t2:
            st.subheader("💰 Wynik PRO")
            st.success(f"### RAZEM: **{round(suma_tynki)} PLN**")
            
            c1, c2 = st.columns(2)
            c1.metric("Robocizna", f"{round(koszt_rob_t)} zł")
            c2.metric("Materiały", f"{round(koszt_mat_t)} zł")

            st.markdown("---")
            st.subheader("📦 Lista materiałowa")
            for przedmiot, ilosc in lista_zakupow:
                st.write(f"• **{przedmiot}:** {ilosc}")
            
            st.markdown("---")
            # --- GENERATOR PDF TYNKI ---
            try:
                from fpdf import FPDF
                from datetime import datetime
                import os

                if st.button("📄 Generuj Raport PDF", use_container_width=True):
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Czcionka (zakładając Inter lub Arial)
                    f_path = "Inter-Regular.ttf"
                    if os.path.exists(f_path):
                        pdf.add_font("Inter", "", f_path)
                        pdf.set_font("Inter", size=12)
                    else:
                        pdf.set_font("Arial", size=12)

                    # Nagłówek
                    pdf.set_font(pdf.font_family, size=16)
                    pdf.cell(0, 15, "OFERTA: TYNKOWANIE / SUCHY TYNK", ln=True, align='C')
                    pdf.ln(5)

                    # Tabela podsumowania
                    pdf.set_fill_color(245, 245, 245)
                    pdf.set_font(pdf.font_family, size=12)
                    pdf.cell(95, 10, " Kategoria", 1, 0, 'L', True)
                    pdf.cell(95, 10, " Koszt", 1, 1, 'L', True)
                    
                    pdf.cell(95, 10, " Robocizna:", 1)
                    pdf.cell(95, 10, f" {round(koszt_rob_t)} PLN", 1, 1)
                    pdf.cell(95, 10, " Materialy:", 1)
                    pdf.cell(95, 10, f" {round(koszt_mat_t)} PLN", 1, 1)
                    pdf.set_font(pdf.font_family, size=13)
                    pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                    pdf.cell(95, 12, f" {round(suma_tynki)} PLN", 1, 1, 'L', True)

                    # Szczegóły
                    pdf.ln(10)
                    pdf.set_font(pdf.font_family, size=12)
                    pdf.cell(0, 10, "SZCZEGOLY TECHNICZNE:", ln=True)
                    pdf.set_font(pdf.font_family, size=10)
                    pdf.cell(0, 7, f"- System: {wybrany_tynk}", ln=True)
                    pdf.cell(0, 7, f"- Powierzchnia prac: {round(m2_rob_pro, 1)} m2", ln=True)
                    if grubosc_t > 0:
                        pdf.cell(0, 7, f"- Srednia grubosc: {grubosc_t} mm", ln=True)

                    # Lista zakupów w PDF
                    pdf.ln(5)
                    pdf.set_font(pdf.font_family, size=12)
                    pdf.cell(0, 10, "LISTA MATERIALOW:", ln=True)
                    pdf.set_font(pdf.font_family, size=10)
                    for przedmiot, ilosc in lista_zakupow:
                        pdf.cell(0, 7, f"- {przedmiot}: {ilosc}", ln=True)

                    pdf_bytes = pdf.output()
                    st.download_button(
                        label="⬇️ Pobierz gotowy PDF",
                        data=bytes(pdf_bytes),
                        file_name=f"Oferta_Tynki_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Problem z PDF: {e}")
                    
elif branza == "Sucha Zabudowa":
    st.header("Kompleksowe Systemy G-K")
    tab_gk1, tab_gk2 = st.tabs(["⚡ Szybka Wycena", "💎 Kosztorys PRO"])

    # --- BAZA CENOWA ---
    baza_mat_gk = {
        "Plyta GK 12.5mm (szt)": 35.0, "Profil CD60 (3mb)": 24.0, "Profil UD27 (3mb)": 15.0,
        "Profil CW50 (3mb)": 15.0, "Profil UW50 (3mb)": 12.0, "Profil UA50 (3mb)": 65.0,
        "Wieszak ES / Obrotowy (szt)": 2.5, "Wkrety TN25 (1000szt)": 45.0,
        "Wkrety TN35 (1000szt)": 55.0, "Kolki 8x60 (100szt)": 32.0, "Welna (m2)": 18.0
    }
    baza_masy_gk = {"Knauf Uniflot": 115, "Knauf Vario": 95, "Dolina Nidy Start": 45, "Franspol": 55}

    with tab_gk1:
        
        # --- WARTOŚCI DOMYŚLNE (Zapobiegają błędom NameError) ---
        m2_gk = 0
        robocizna = 0
        total_material = 0
        szer_profilu = 60
        laczniki_cd1 = 0    
        laczniki_cd2 = 0   
        laczniki_krzyzowe = 0
        szt_cd = 0          
        szt_ud = 0          
        szt_wieszaki = 0    
        
        col_g1, col_g2 = st.columns([1, 1.2])

        with col_g1:
            
            szer_profilu = 60 
            
            rodzaj_gk = st.radio("Co budujemy?", ["Sufit Podwieszany", "Ściana Działowa"], key="gk_type")
            dl_profilu_cd = 3.0
            
            if rodzaj_gk == "Sufit Podwieszany":
                c1, c2 = st.columns(2)
                dl_sufitu = c1.number_input("Długość sufitu (m):", min_value=0.1, value=5.0)
                sz_sufitu = c2.number_input("Szerokość sufitu (m):", min_value=0.1, value=4.0)
                m2_gk = dl_sufitu * sz_sufitu
                typ_stelaza = st.radio("Rodzaj stelaża:", ["Pojedynczy", "Krzyżowy"])
                
                # --- OBLICZENIA SUFIT ---
                rozstaw_cd1 = 0.40 if typ_stelaza == "Pojedynczy" else 1.10
                liczba_cd1 = int(sz_sufitu / rozstaw_cd1) + 1
                odcinki_cd1 = int(dl_sufitu / dl_profilu_cd)
                reszta_cd1 = dl_sufitu % dl_profilu_cd
                szt_cd1 = liczba_cd1 * (odcinki_cd1 + (1 if reszta_cd1 > 0 else 0))
                laczniki_cd1 = odcinki_cd1 * liczba_cd1

                if typ_stelaza == "Krzyżowy":
                    rozstaw_cd2 = 0.40
                    liczba_cd2 = int(dl_sufitu / rozstaw_cd2) + 1
                    odcinki_cd2 = int(sz_sufitu / dl_profilu_cd)
                    reszta_cd2 = sz_sufitu % dl_profilu_cd
                    szt_cd2 = liczba_cd2 * (odcinki_cd2 + (1 if reszta_cd2 > 0 else 0))
                    laczniki_cd2 = odcinki_cd2 * liczba_cd2
                    laczniki_krzyzowe = liczba_cd1 * liczba_cd2
                    szt_cd2 = laczniki_cd2 = laczniki_krzyzowe = 0
                else:
                    szt_cd2 = 0
                    laczniki_cd2 = 0
                    laczniki_krzyzowe = 0
                
                szt_cd = szt_cd1 + szt_cd2
                szt_ud = int(((dl_sufitu + sz_sufitu) * 2 * 1.1) / 3) + 1
                szt_wieszaki = int(m2_gk / 0.7) + 1 # Gęściej dla bezpieczeństwa
                szt_cw = szt_uw = szt_ua = 0

            else: # ŚCIANA DZIAŁOWA
                c1, c2 = st.columns(2)
                szer_sciany = c1.number_input("Długość ścianki (m):", min_value=0.1, value=4.0)
                wys_sciany = c2.number_input("Wysokość ścianki (m):", min_value=0.1, value=2.6)
                m2_gk = szer_sciany * wys_sciany
                szer_profilu = st.selectbox("Profil CW/UW:", [50, 75, 100], format_func=lambda x: f"{x} mm")
                plytowanie = st.radio("Płytowanie:", ["1xGK (Jednostronnie)", "2xGK (Dwustronnie)"])
                n_drzwi = st.number_input("Otwory drzwiowe (UA):", min_value=0, value=0)
                
                szt_uw = int((szer_sciany * 2 * 1.1) / 3) + 1
                szt_cw = int((szer_sciany / 0.6) * (wys_sciany / 3) + 1)
                szt_ua = n_drzwi * 2
                szt_cd = szt_ud = szt_wieszaki = laczniki_cd1 = laczniki_krzyzowe = 0

            izolacja_gk = st.checkbox("Wypełnienie wełną?")
            if izolacja_gk:
                # Ustawiamy domyślny indeks wełny na podstawie wybranego profilu
                opcje_welny = [50, 75, 100, 150]
                try:
                    domyslny_indeks = opcje_welny.index(szer_profilu)
                except ValueError:
                    domyslny_indeks = 0 # Jeśli profilu nie ma na liście (np. sufit), daj 50mm

                grubosc_welny = st.selectbox(
                    "Grubość wełny:",
                    opcje_welny,
                    index=domyslny_indeks,
                    format_func=lambda x: f"{x} mm"
                )
            else:
                grubosc_welny = None
            wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()))
            stawka_gk = st.slider("Stawka za robociznę (zł/m2):", 1, 250, 110)

        # --- LOGIKA MATERIAŁOWA ---
        naddatek = 1.10 # 10% zapasu na wszystko
        szt_plyt = int((m2_gk * naddatek) / 2.88) + 1
        wkret_25 = int(m2_gk * 20)
        
        koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
        koszt_profile = (szt_cd * baza_mat_gk["Profil CD60 (3mb)"]) + (szt_ud * baza_mat_gk["Profil UD27 (3mb)"]) + \
                        (szt_cw * baza_mat_gk.get(f"Profil CW{szer_profilu} (3mb)", 0)) + \
                        (szt_uw * baza_mat_gk.get(f"Profil UW{szer_profilu} (3mb)", 0)) + \
                        (szt_ua * baza_mat_gk.get(f"Profil UA{szer_profilu} (3mb)", 0))
        
        koszt_akcesoria = (szt_wieszaki * baza_mat_gk["Wieszak ES / Obrotowy (szt)"]) + \
                          (int(wkret_25/1000+1) * baza_mat_gk["Wkrety TN25 (1000szt)"])
        
        koszt_welny = (m2_gk * baza_mat_gk["Welna (m2)"]) if izolacja_gk else 0
        koszt_masy = (int(m2_gk * 0.5 / 25) + 1) * baza_masy_gk[wybrana_masa]
        # Pchełki do skręcania stelaża (średnio 10 szt / m2)
        szt_pchelki = int(m2_gk * 10 / 1000 + 1) 
        koszt_pchelki = szt_pchelki * 40.0 # ok 40 zł za paczkę 1000szt

        # Łączniki wzdłużne (tylko jeśli profil CD jest łączony)
        koszt_laczniki = (laczniki_cd1 + laczniki_cd2) * 1.50 # ok 1.50 zł/szt
        
        total_material = koszt_plyt + koszt_profile + koszt_akcesoria + koszt_welny + koszt_masy + koszt_pchelki + koszt_laczniki

        # --- 1. LOGIKA SPOINOWANIA (TAŚMY I MASY) ---
        st.markdown("---")
        st.subheader("Wykończenie spoin")
        c_sp1, c_sp2 = st.columns(2)
        
        typ_tasmy = c_sp1.radio("Zbrojenie:", ["Tuff-Tape (Całość)", "Flizelina + Tuff-Tape (Narożniki)"])
        wybrana_masa = c_sp2.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()), key="masa_wybor")

        # --- 2. OBLICZENIA ILOŚCI I KOSZTÓW ---
        naddatek = 1.10 
        szt_plyt = int((m2_gk * naddatek) / 2.88) + 1
        
        # Wkręty: TN25 (20 szt/m2) + Pchełki LN (10 szt/m2 sufitu)
        wkret_25 = int(m2_gk * 20 * naddatek)
        szt_pchelki = int(m2_gk * 12) if rodzaj_gk == "Sufit Podwieszany" else int(m2_gk * 5)

        # Taśmy i masy
        if typ_tasmy == "Tuff-Tape (Całość)":
            mb_tuff = m2_gk * 1.5
            mb_fliz = 0
        else:
            mb_tuff = m2_gk * 0.4 # Tylko narożniki
            mb_fliz = m2_gk * 1.1 # Połączenia płaskie
        
        koszt_tasm = (int(mb_tuff/30)+1)*120 + (int(mb_fliz/25)+1)*15
        worki_masy = int((m2_gk * 0.5) / 25 + 0.99)
        
        # Sumowanie kosztów
        koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
        koszt_pchelki = (int(szt_pchelki/1000)+1) * 45.0
        koszt_wkrety = (int(wkret_25/1000)+1) * baza_mat_gk["Wkrety TN25 (1000szt)"]
        koszt_masy = worki_masy * baza_masy_gk[wybrana_masa]
        
        total_material = koszt_plyt + koszt_profile + koszt_akcesoria + koszt_welny + koszt_masy + koszt_pchelki + koszt_wkrety + koszt_tasm
        robocizna = m2_gk * stawka_gk

        
            # --- 3. WYŚWIETLANIE (PRAWA KOLUMNA) ---
        with col_g2:
            st.subheader("💰 Podsumowanie")
            st.success(f"### RAZEM: **{round(total_material + robocizna)} zł**")
            
            with st.expander("📦 LISTA ZAKUPÓW", expanded=True):
                if rodzaj_gk == "Sufit Podwieszany":
                    st.write(f"• Profile CD60: {szt_cd} szt.")
                    st.write(f"• Profile UD27: {szt_ud} szt.")
                    st.write(f"• Wieszaki: {szt_wieszaki} szt.")
                    if laczniki_krzyzowe > 0: st.write(f"• Łączniki krzyżowe: {laczniki_krzyzowe} szt.")
                else:
                    st.write(f"• Profile CW{szer_profilu}: {szt_cw} szt.")
                    st.write(f"• Profile UW{szer_profilu}: {szt_uw} szt.")
                
                st.write(f"• Płyty GK (120x240): {szt_plyt} szt.")
                st.write(f"• Wkręty TN25: {int(wkret_25/1000)+1} op. (1000szt)")
                st.write(f"• Wkręty Pchełki LN: {int(szt_pchelki/1000)+1} op. (1000szt)")
                
                if mb_tuff > 0: st.write(f"• Taśma Tuff-Tape: {int(mb_tuff/30)+1} rolka (30mb)")
                if mb_fliz > 0: st.write(f"• Flizelina: {int(mb_fliz/25)+1} rolka (25mb)")
                
                st.write(f"• Masa ({wybrana_masa}): {worki_masy} worki/wiadra")
                if izolacja_gk: st.write(f"• Wełna ({grubosc_welny}mm): {round(m2_gk, 1)} m²")
            
# --- SEKCJA: ELEKTRYKA ---
elif branza == "Elektryka":
    st.header("Instalacja Elektryczna (Mieszkanie)")
    
    # Przeniesienie definicji kolumn do środka elif
    col_e1, col_e2 = st.columns([1, 1.2])

    # --- KONFIGURACJA MAREK OSPRZĘTU ---
    opcje_osprzetu = {
        "Ekonomiczny (np. Simon 10, Adelid)": 12,
        "Standard (np. Simon 54, Legrand Niloe)": 38,
        "Premium (np. Berker R.1, Jung, Gira)": 95
    }

    with col_e1:
        st.subheader("Parametry instalacji")
        m2_mieszkania = st.number_input("Metraż mieszkania (m²):", min_value=10, value=60)
        mnoznik_m2 = m2_mieszkania / 60
        st.markdown("---")
        sugerowane_punkty = int(m2_mieszkania * 0.75)
        n_punktow = st.slider("Liczba punktów (gniazda/włączniki):", 10, 150, sugerowane_punkty) 
        typ_scian = st.radio("Materiał ścian:", ["Gazobeton/Cegła", "Żelbet (Wielka Płyta)"])
        n_punkty_tele = 2
        wybrany_standard = st.selectbox("Marka osprzętu:", list(opcje_osprzetu.keys()), index=1)
        stawka_punkt = st.slider("Stawka montażu osprzętu (zł/szt):", 20, 60, 35)

    # --- OBLICZENIA (Te linie MUSZĄ być idealnie pod 'with') ---
    kabel_25 = 150 * mnoznik_m2
    kabel_15 = 100 * mnoznik_m2
    kabel_4x15 = 30 * mnoznik_m2
    kabel_tv = 30 * mnoznik_m2
    kabel_lan = 50 * mnoznik_m2
    
    szt_mocowania = int((kabel_25 + kabel_15 + kabel_4x15 + kabel_tv + kabel_lan) * 3)
    paczki_mocowania = int(szt_mocowania / 100) + 1
    
    srednia_cena_szt = opcje_osprzetu[wybrany_standard]
    koszt_rozdzielnicy_mat = 1500 

    mat_kable = (kabel_25 * 4.50) + (kabel_15 * 3.20) + (kabel_4x15 * 5.50) + (kabel_tv * 2.80) + (kabel_lan * 3.50)
    mat_osprzet = n_punktow * srednia_cena_szt
    mat_mocowania = paczki_mocowania * 22.0
    
    total_material_e = mat_kable + mat_osprzet + koszt_rozdzielnicy_mat + mat_mocowania

    # ROBOCIZNA (zgodnie z wytycznymi elektryka na 7-10 tys.)
    mnoznik_trudnosci = 1.4 if typ_scian == "Żelbet (Wielka Płyta)" else 1.0
    robocizna_baza = (m2_mieszkania * 90) # Podstawa za mb i bruzdy
    robocizna_osprzet = (n_punktow + n_punkty_tele) * stawka_punkt
    robocizna_rozdzielnica = 1200
    
    total_robocizna_e = (robocizna_baza + robocizna_osprzet + robocizna_rozdzielnica) * mnoznik_trudnosci

    with col_e2:
        st.subheader("💰 Kosztorys Elektryki")
        total_e = total_material_e + total_robocizna_e
        st.success(f"### RAZEM: **{round(total_e)} zł**")
        
        c1, c2 = st.columns(2)
        c1.metric("Materiały", f"{round(total_material_e)} zł")
        c2.metric("Robocizna", f"{round(total_robocizna_e)} zł")

        with st.expander("📦 WYKAZ MATERIAŁÓW DO KUPNA", expanded=True):
            st.write(f"• Kabel 3x2.5 (Gniazda): **{round(kabel_25)} mb**")
            st.write(f"• Kabel 3x1.5 (Światło): **{round(kabel_15)} mb**")
            st.write(f"• Kabel 4x1.5 (Schodowe/Siła): **{round(kabel_4x15)} mb**")
            st.write(f"• Rozdzielnica + 10 bezpieczników (Eaton/Hager): **1 kpl**")
            st.write(f"• Osprzęt: **{n_punktow} szt.** ({wybrany_standard})")
            st.write(f"• Uchwyty mocujące (paczki 100 szt.): **{paczki_mocowania} op.**")
            st.write(f"• Kabel antenowy RG6 (TV): **{round(kabel_tv)} mb**")
            st.write(f"• Kabel LAN kat. 6 (Internet): **{round(kabel_lan)} mb**")
            st.write(f"• Dodatkowe puszki/gniazda LAN/RTV: **{n_punkty_tele} szt.**")
            
            st.warning("⚠️ **UWAGA:** Wycena nie uwzględnia zakupu lamp (oprawy oświetleniowe).")
            st.info("Ilość kabla liczona szacunkowo dla instalacji prowadzonej w tynku/podłogach.")

elif branza == "Łazienka":
    # --- 1. INICJALIZACJA ZMIENNYCH (To naprawi NameError) ---
    m2_tynku = 0.0
    m2_scian_total = 0.0
    m2_podlogi = 0.0
    obwod = 0.0
    mb_tasma_hydro = 0.0
    m2_hydro_sciany = 0.0
    format_plytki = "Standardowe (np. 60x60, 30x60)" # domyślna wartość
    # ---------------------------------------------------------
    st.header("Kompleksowy Kalkulator: Łazienka PRO")
    st.write("Profesjonalna wycena prac łazienkowych uwzględniająca hydroizolację, format płytek i biały montaż.")

    # --- ZAKŁADKI KROKOWE ---
    tab_wym, tab_plytki, tab_inst, tab_wynik = st.tabs([
        "1. Wymiary", "2. Płytki i Hydro", "3. Instalacje", "4. Podsumowanie"
    ])

    with tab_wym:
        st.subheader("Wymiary pomieszczenia")
        c_w1, c_w2 = st.columns(2)
        m2_podlogi = c_w1.number_input("Powierzchnia podłogi (m2):", 1.0, 100.0, 5.0, step=0.5)
        wysokosc = c_w2.number_input("Wysokość łazienki (m):", 2.0, 4.0, 2.5, step=0.1)
        
        # --- AUTOMATYKA OBWODU ---
        # Zakładamy prostokąt, gdzie jeden bok to x, a drugi to 1.5x (typowa łazienka)
        import math
        bok_a = math.sqrt(m2_podlogi / 1.5)
        bok_b = bok_a * 1.5
        sugerowany_obwod = round(2 * (bok_a + bok_b), 1)
        
        obwod = st.number_input("Suma długości ścian (Obwód w metrach):", 2.0, 100.0, sugerowany_obwod, 
                               help=f"Dla {m2_podlogi}m2 typowy obwód to ok. {sugerowany_obwod}m")
        
        okna_drzwi = st.number_input("Otwory do odjęcia (drzwi/okna w m2):", 0.0, 10.0, 1.6, step=0.1)
        
        m2_scian_total = (obwod * wysokosc) - okna_drzwi
        st.info(f"Całkowita powierzchnia ścian do obróbki: **{round(m2_scian_total, 1)} m²**")
                
    with tab_plytki:
        st.subheader("Hydroizolacja (Strefy mokre)")
        c_h1, c_h2 = st.columns(2)
        m2_hydro_sciany = c_h1.number_input("Ściany pod prysznicem/wanną (m2):", 0.0, 50.0, 5.0, step=0.5)
        mb_tasma_hydro = c_h2.number_input("Długość taśm narożnikowych (mb):", 0.0, 100.0, 12.0, step=1.0)
        
        st.markdown("---")
        st.subheader("Płytki i Detale")
        format_plytki = st.selectbox("Format płytek ściennych:", ["Standardowe (np. 60x60, 30x60)", "Wielki Format (np. 120x60, 120x120)", "Mozaika / Małe płyki"])
        szerokosc_fugi = st.slider("Zakładana szerokość fugi (mm):", 1.0, 5.0, 2.0, step=0.5)
        
        c_p1, c_p2 = st.columns(2)
        mb_zacinania = c_p1.number_input("Zacinanie płytek 45° (mb):", 0.0, 100.0, 5.0, step=0.5)
        mb_listwy = c_p2.number_input("Listwy narożne ozdobne (mb):", 0.0, 100.0, 0.0, step=0.5)

    with tab_inst:
        st.subheader("Prace instalacyjne i Biały Montaż")
        c_i1, c_i2 = st.columns(2)
        szt_wc = c_i1.number_input("Zabudowa stelaża WC (szt.):", 0, 5, 1)
        szt_odplyw = c_i2.number_input("Odpływ liniowy z kopertą (szt.):", 0, 5, 1)
        
        szt_podejscia = c_i1.number_input("Punkty wodne (mankiety uszczelniające):", 0, 20, 6)
        szt_wneki = c_i2.number_input("Półki / wnęki podświetlane (szt.):", 0, 10, 1)
        mb_led = st.number_input("Montaż profili LED w płytkach (mb):", 0.0, 50.0, 0.0, step=1.0)

    with tab_wynik:
        st.subheader("Cennik Wykonawcy (Dostosuj stawki)")
        c_c1, c_c2, c_c3 = st.columns(3)
        stawka_m2_plytek = c_c1.number_input("Układanie płytek (zł/m2):", 50, 400, 150 if "Wielki Format" not in format_plytki else 220)
        stawka_mb_45 = c_c2.number_input("Zacinanie 45° (zł/mb):", 50, 300, 120)
        stawka_wc = c_c3.number_input("Zabudowa WC (zł/szt):", 100, 1500, 450)
        
        # --- 1. DEFINICJA WYMIARÓW PŁYTEK DO WZORU ---
        if "Wielki Format" in format_plytki:
            dl_p, szer_p, grub_p = 1200, 600, 10
        elif "Standardowe" in format_plytki:
            dl_p, szer_p, grub_p = 600, 600, 9
        else: # Mozaika / Małe / Drewnopodobne
            dl_p, szer_p, grub_p = 600, 170, 8

        # --- 2. OBLICZENIA MATERIAŁOWE (Z DODANYM ZAPASEM PŁYTEK) ---
        m2_plytek_total = m2_scian_total + m2_podlogi
        m2_hydro_total = m2_podlogi + m2_hydro_sciany
        
        # LOGIKA ZAPASU DLA INWESTORA
        procent_zapasu = 1.15 if "Wielki" in format_plytki or "Mozaika" in format_plytki else 1.10
        m2_plytek_z_zapasem = round(m2_plytek_total * procent_zapasu, 1)

        # Hydroizolacja i reszta chemii
        kg_folii = m2_hydro_total * 1.2
        op_folii_5kg = int(kg_folii / 5 + 0.99)
        mb_tasmy = int(mb_tasma_hydro * 1.1)
        szt_mankiety = szt_podejscia * 2 
        op_gruntu_5l = int((m2_scian_total * 0.2) / 5 + 0.99)

        zuzycie_kleju = 5.5 if "Wielki" in format_plytki else 4.0
        worki_kleju_25kg = int((m2_plytek_total * zuzycie_kleju) / 25 + 0.99)
        
        wspolczynnik_fugi = ((dl_p + szer_p) / (dl_p * szer_p)) * grub_p * szerokosc_fugi * 1.6
        kg_fugi = m2_plytek_total * wspolczynnik_fugi * 1.1 
        op_fugi_2kg = int(kg_fugi / 2 + 0.99)
        if op_fugi_2kg == 0: op_fugi_2kg = 1

        szt_silikon = int((mb_tasma_hydro + obwod) / 10 + 0.99)
        worki_tynku = int((m2_tynku * 15) / 25 + 0.99)

        # --- 3. OBLICZENIA FINANSOWE ---
        # BAZA: 2000 zł za każdy m2 podłogi (pokrywa standard prac)
        stawka_bazowa_m2 = 2000 
        robocizna_baza = m2_podlogi * stawka_bazowa_m2
        
        # DODATKI (Płatne ekstra poza bazą)
        koszt_zacinania = mb_zacinania * stawka_mb_45
        koszt_listwy = mb_listwy * 100  # Przykład: 100 zł/mb listwy ozdobnej
        koszt_odplywu = szt_odplyw * 800 # Odpływ jest trudniejszy niż standardowy brodzik
        koszt_wneki = szt_wneki * 500
        koszt_led = mb_led * 120
        koszt_wc = szt_wc * 500
        
        # Suma całkowita robocizny
        robocizna_suma = (robocizna_baza + koszt_zacinania + koszt_listwy + 
                          koszt_odplywu + koszt_wneki + koszt_led + koszt_wc)

        # --- DODANY BLOK: OBLICZENIA KOSZTÓW MATERIAŁÓW (Naprawia NameError) ---
        mat_folia = op_folii_5kg * 90
        mat_tasma = mb_tasmy * 6
        mat_klej = worki_kleju_25kg * 65
        mat_fuga_sil = (op_fugi_2kg * 45) + (szt_silikon * 35)
        mat_tynk = worki_tynku * 30
        materialy_suma = mat_folia + mat_tasma + mat_klej + mat_fuga_sil + mat_tynk + 250
        # ------------------------------------------------------------------------

        # --- 4. WYŚWIETLANIE WYNIKÓW (WERSJA BIZNESOWA) ---
        st.markdown("---")
        
        # Główny wynik
        st.success(f"### ŁĄCZNA KWOTA ROBOCIZNY: **{round(robocizna_suma)} PLN**")
        
        # Rozbicie na Baza vs Dodatki
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Pakiet Bazowy (Łazienka)", f"{round(robocizna_baza)} zł", help="Obejmuje standardowe układanie płytek, hydroizolację i przygotowanie.")
        with c2:
            suma_dodatkow = robocizna_suma - robocizna_baza
            st.metric("Suma dodatków (Detale)", f"{round(suma_dodatkow)} zł", delta="Ekstra za trudność")

        st.markdown("---")
        
        # SZCZEGÓŁOWA LISTA DODATKÓW
        st.subheader("🛠️ Wycena detali (Poza pakietem bazowym)")
        
        detale = []
        if mb_zacinania > 0: detale.append({"Zadanie": "Szlifowanie narożników 45°", "Ilość": f"{mb_zacinania} mb", "Koszt": f"{round(koszt_zacinania)} zł"})
        if mb_listwy > 0: detale.append({"Zadanie": "Montaż listew ozdobnych", "Ilość": f"{mb_listwy} mb", "Koszt": f"{round(koszt_listwy)} zł"})
        if szt_wneki > 0: detale.append({"Zadanie": "Wykonanie wnęk/półek", "Ilość": f"{szt_wneki} szt", "Koszt": f"{round(koszt_wneki)} zł"})
        if mb_led > 0: detale.append({"Zadanie": "Montaż profili LED", "Ilość": f"{mb_led} mb", "Koszt": f"{round(koszt_led)} zł"})
        if szt_odplyw > 0: detale.append({"Zadanie": "Odpływ liniowy (koperta)", "Ilość": f"{szt_odplyw} szt", "Koszt": f"{round(koszt_odplywu)} zł"})
        
        if detale:
            st.table(detale)
        else:
            st.info("Brak dodatkowych detali - łazienka w standardzie prostym.")

        # --- DEFINICJA LISTY ---
        lista_zakupow_lazienka = [
            ("PŁYTKI (łącznie z zapasem)", f"{m2_plytek_z_zapasem} m²"),
            ("Klej elastyczny S1 (25kg)", f"{worki_kleju_25kg} worków"),
            ("Folia w płynie (5kg)", f"{op_folii_5kg} wiader"),
            ("Taśma uszczelniająca", f"{mb_tasmy} mb"),
            ("Mankiety ścienne", f"{szt_mankiety} szt."),
            ("Fuga elastyczna (2kg)", f"{op_fugi_2kg} op."),
            ("Silikon sanitarny", f"{szt_silikon} szt."),
            ("Grunt pod hydroizolację", f"{op_gruntu_5l} wiader 5L"),
        ]
        if worki_tynku > 0:
            lista_zakupow_lazienka.append(("Tynk wyrównawczy (25kg)", f"{worki_tynku} worków"))

        # --- WYŚWIETLANIE WYNIKÓW I ANALIZA RENTOWNOŚCI ---
        st.markdown("---")
        
        # Obliczenie wskaźnika na m2 podłogi
        cena_za_m2_podlogi = robocizna_suma / m2_podlogi
        
        # Główne podsumowanie finansowe
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.success(f"### RAZEM ROBOCIZNA\n**{round(robocizna_suma)} PLN**")
        with c_res2:
            st.info(f"### CHEMIA BUDOWLANA\n**~{round(materialy_suma)} PLN**")

        # KONTROLA PRZEDZIAŁU 2000-3000 zł/m2
        st.subheader("Analiza rynkowa wyceny")
        
        col_metric1, col_metric2 = st.columns([2, 1])
        
        with col_metric1:
            if 2000 <= cena_za_m2_podlogi <= 3000:
                st.write(f"Twoja wycena to **{round(cena_za_m2_podlogi)} zł/m²** podłogi. Mieścisz się w standardowym przedziale rynkowym.")
            elif cena_za_m2_podlogi < 2000:
                st.error(f"Uwaga: Wycena wynosi **{round(cena_za_m2_podlogi)} zł/m²** podłogi. To może być za mało przy wysokim standardzie!")
            else:
                st.warning(f"💎 Standard Premium: Wycena wynosi **{round(cena_za_m2_podlogi)} zł/m²** podłogi. Upewnij się, że Inwestor akceptuje te stawki.")

        with col_metric2:
            st.metric("Cena / m² podłogi", f"{round(cena_za_m2_podlogi)} zł")

        st.markdown("---")
        
        # SEKCJA PŁYTEK I CIĘCIA 45°
        st.subheader("Zapotrzebowanie i Detale")
        cp1, cp2, cp3 = st.columns(3)
        cp1.metric("Płytki do zakupu", f"{m2_plytek_z_zapasem} m²")
        cp2.metric("Cięcie 45° (mb)", f"{mb_zacinania} mb")
        cp3.metric("Koszt cięcia", f"{round(koszt_zacinania)} PLN")
        
        st.info(f"💡 **Cięcie 45°:** Uwzględniono {mb_zacinania} mb szlifowania krawędzi w stawce {stawka_mb_45} zł/mb.")
        st.warning("💡 **Wskazówka:** Powyższy metraż uwzględnia docinki i ryzyko pęknięć.")

        # Wyświetlanie listy zakupów
        st.markdown("---")
        st.subheader("Wykaz Chemii Budowlanej (Lista Zakupów)")
        
        col_list1, col_list2 = st.columns(2)
        half = len(lista_zakupow_lazienka) // 2 + 1
        
        with col_list1:
            for przedmiot, ilosc in lista_zakupow_lazienka[:half]:
                st.write(f"• **{przedmiot}:** {ilosc}")
        with col_list2:
            for przedmiot, ilosc in lista_zakupow_lazienka[half:]:
                st.write(f"• **{przedmiot}:** {ilosc}")
                  
        # --- 5. GENERATOR PDF (ŁAZIENKA PRO) ---
        # --- 5. GENERATOR PDF (ŁAZIENKA PRO - CZCIONKA INTER) ---
        st.markdown("---")
        if st.button("📄 Generuj Pełny Kosztorys PDF (Łazienka)"):
            try:
                from fpdf import FPDF
                from datetime import datetime

                pdf = FPDF()
                pdf.add_page()
                
                # REJESTRACJA CZCIONKI INTER
                pdf.add_font('Inter', '', 'Inter-Regular.ttf', uni=True)
                
                # NAGŁÓWEK
                pdf.set_font('Inter', '', 16)
                pdf.cell(190, 10, txt="KOSZTORYS WYKONAWCZY: ŁAZIENKA", ln=True, align='C')
                pdf.set_font('Inter', '', 10)
                pdf.cell(190, 10, txt=f"Data wystawienia: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align='C')
                pdf.ln(10)

                # SEKCJA 1: PODSUMOWANIE FINANSOWE
                pdf.set_font('Inter', '', 12)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(190, 10, txt="1. PODSUMOWANIE KOSZTÓW", ln=True, align='L', fill=True)
                pdf.ln(2)
                
                pdf.set_font('Inter', '', 10)
                pdf.cell(140, 8, txt="Pakiet Bazowy (Robocizna + przygotowanie)", border=1)
                pdf.cell(50, 8, txt=f"{round(robocizna_baza)} zł", border=1, ln=True, align='R')
                
                pdf.cell(140, 8, txt="Suma dodatków i detali", border=1)
                pdf.cell(50, 8, txt=f"{round(suma_dodatkow)} zł", border=1, ln=True, align='R')
                
                pdf.cell(140, 8, txt="Szacowany koszt chemii budowlanej", border=1)
                pdf.cell(50, 8, txt=f"{round(materialy_suma)} zł", border=1, ln=True, align='R')
                
                pdf.set_font('Inter', '', 11)
                pdf.cell(140, 10, txt="RAZEM DO ZAPŁATY (Usługa + Chemia):", border=1, fill=True)
                pdf.cell(50, 10, txt=f"{round(robocizna_suma + materialy_suma)} zł", border=1, ln=True, align='R', fill=True)
                pdf.ln(5)

                # SEKCJA 2: TABELA DETALI
                if detale:
                    pdf.set_font('Inter', '', 12)
                    pdf.cell(190, 10, txt="2. WYCENA ELEMENTÓW DODATKOWYCH", ln=True, align='L', fill=True)
                    pdf.set_font('Inter', '', 9)
                    pdf.cell(100, 8, "Zadanie / Detal", 1, 0, 'C')
                    pdf.cell(40, 8, "Ilość", 1, 0, 'C')
                    pdf.cell(50, 8, "Koszt", 1, 1, 'C')
                    for d in detale:
                        pdf.cell(100, 8, d["Zadanie"], 1)
                        pdf.cell(40, 8, d["Ilość"], 1, 0, 'C')
                        pdf.cell(50, 8, d["Koszt"], 1, 1, 'R')
                    pdf.ln(5)

                # SEKCJA 3: LISTA ZAKUPÓW
                pdf.set_font('Inter', '', 12)
                pdf.cell(190, 10, txt="3. WYKAZ MATERIAŁÓW (Do dostarczenia)", ln=True, align='L', fill=True)
                pdf.set_font('Inter', '', 10)
                pdf.ln(2)
                for przedmiot, ilosc in lista_zakupow_lazienka:
                    pdf.cell(190, 7, txt=f"- {przedmiot}: {ilosc}", ln=True)

                # STOPKA I GENEROWANIE
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button(
                    label="📥 Pobierz Kosztorys PDF",
                    data=pdf_bytes,
                    file_name=f"Kosztorys_Lazienka_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Błąd PDF: {e}. Sprawdź czy plik Inter-Regular.ttf jest w folderze.")
               
elif branza == "Drzwi":
    st.header("Kalkulator Montażu Drzwi Wewnętrznych")
    
    col_d1, col_d2 = st.columns([1, 1.2])
    
    # --- CENNIK ZAKUPU ---
    ceny_zakupu = {
        "Standard (np. Porta, DRE - przylgowe)": 1200,
        "Bezprzylgowe (ukryte zawiasy)": 1900,
        "Rewersyjne (otwierane do wewnątrz)": 2300,
        "Ukryte (do pomalowania / Discret)": 1600
    }

    with col_d1:
        st.subheader("Parametry zamówienia")
        szt_drzwi = st.number_input("Liczba kompletów (skrzydło + ościeżnica):", min_value=1, value=5)
        
        wybrany_model = st.selectbox(
            "Model i standard drzwi:", 
            options=list(ceny_zakupu.keys())
        )
        
        szerokosc_muru = st.radio("Szerokość muru (zakres):", ["Standard (do 140mm)", "Szeroki (140mm+ dopłata)"])
        
        st.markdown("---")
        st.subheader("Dodatki")
        podciecie = st.checkbox("Podcięcie wentylacyjne / tuleje?")
        demontaz = st.checkbox("Demontaż starych drzwi/ościeżnic?")
        
        # Koszt montażu na sztywno
        stawka_montazu = 250 

    # --- LOGIKA OBLICZEŃ ---
    cena_jednostkowa = ceny_zakupu[wybrany_model]
    
    # Koszt materiałów (drzwi + pianka 40zł/szt)
    koszt_pianki = szt_drzwi * 40
    total_zakup = (szt_drzwi * cena_jednostkowa) + koszt_pianki
    
    # Koszt robocizny
    doplata_szeroki = 50 if szerokosc_muru == "Szeroki (140mm+ dopłata)" else 0
    doplata_podciecie = 30 if podciecie else 0
    doplata_demontaz = 100 if demontaz else 0
    
    robocizna_jednostkowa = stawka_montazu + doplata_szeroki + doplata_podciecie + doplata_demontaz
    total_robocizna_d = szt_drzwi * robocizna_jednostkowa

    with col_d2:
        st.subheader("💰 Kosztorys Stolarki")
        suma_d = total_zakup + total_robocizna_d
        st.success(f"### RAZEM: **{round(suma_d)} zł**")
        
        c1, c2 = st.columns(2)
        c1.metric("Zakup + Materiały", f"{round(total_zakup)} zł")
        c2.metric("Montaż (Suma)", f"{round(total_robocizna_d)} zł")

        with st.expander("📦 SZCZEGÓŁY ZAMÓWIENIA", expanded=True):
            st.write(f"• Wybrany model: **{wybrany_model}**")
            st.write(f"• Liczba skrzydeł i ościeżnic: **{szt_drzwi} kpl.**")
            st.write(f"• Pianka montażowa (1 puszka/szt): **{szt_drzwi} szt.**")
            if demontaz:
                st.write(f"• Usługa demontażu starych drzwi: **TAK**")
            st.write(f"• Koszt montażu za sztukę: **{robocizna_jednostkowa} zł**")
            
            st.info("Cena zakupu drzwi jest orientacyjna (średnia rynkowa z klamką i rozetą).")


elif branza == "Panel Inwestora":
    st.title("Panel Inwestora - Kompleksowy Kosztorys Flipu")
    
    with st.expander("CHECKLISTA PRZEDZAKUPOWA (Inspekcja lokalu)", expanded=False):
        st.write("Sprawdź te punkty przed finalną decyzją o zakupie:")
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            st.checkbox("Piony wod-kan (stan żeliwa/plastiku)", key="ch_piony")
            st.checkbox("Okna (szczelność/wiek/pakiet szyb)", key="ch_okna")
            st.checkbox("Stan instalacji elektrycznej (miedź vs aluminium)", key="ch_elek")
        with c_ch2:
            st.checkbox("Możliwość wydzielenia dodatkowego pokoju", key="ch_pokoje")
            st.checkbox("KW bez wpisów w dziale III i IV", key="ch_kw")
            st.checkbox("Przynależność piwnicy / komórki lokatorskiej", key="ch_piwnica")
            st.info("💡 Wszystkie punkty odznaczone? Możesz przejść do kalkulacji kosztów.")

    col_inv1, col_inv2 = st.columns([1, 1.5])
    
    with col_inv1:
        st.subheader("Parametry Nieruchomości")
        m2_total = st.number_input("Metraż mieszkania (m2):", min_value=1.0, value=50.0)
        standard = st.select_slider("Standard wykończenia:", options=["Ekonomiczny", "Standard", "Premium"])
        stan_lokalu = st.radio("Stan lokalu:", ["Deweloperski", "Rynek Wtórny (Do remontu)"])
        
        # --- DEFINICJA TECHNOLOGII (Wszystko przesunięte w prawo pod 'with') ---
        if standard == "Ekonomiczny":
            opis_std = "Gładź 2 warstwy (tania), brak sufitów G-K, farby marketowe."
            mnoznik_mat = 0.8
            technologia_gk = "Brak sufitów (tylko szpachlowanie)"
            technologia_spoin = "Flizelina (najtaniej)"
            marka_farby = "Śnieżka / Dekoral"
        elif standard == "Standard":
            opis_std = "Sufity podwieszane korytarz/łazienka, Tuff-Tape w narożnikach, farby lateksowe."
            mnoznik_mat = 1.1
            technologia_gk = "Sufity G-K w ciągach komunikacyjnych"
            technologia_spoin = "Tuff-Tape (narożniki) + Flizelina"
            marka_farby = "Beckers / Magnat"
        else: # Premium
            opis_std = "Pełne sufity podwieszane, Gładź polimerowa, Tuff-Tape wszędzie, farby ceramiczne."
            mnoznik_mat = 1.6
            technologia_gk = "Pełne sufity podwieszane w całym mieszkaniu"
            technologia_spoin = "Tuff-Tape na całości (brak pęknięć)"
            marka_farby = "Flugger / Benjamin Moore"

        st.info(f"📋 **Wybrana technologia:** {opis_std}")
        
        st.markdown("---")
        st.subheader("🛠️ Zakres prac (Dodaj elementy):")
        do_elektryka = st.checkbox("Nowa Elektryka (kompletna)", value=True)
        do_szpachlowanie = st.checkbox("Szpachlowanie / Gładzie", value=True)
        do_malowanie = st.checkbox("Malowanie (2x biała/kolor)", value=True)
        do_gk = st.checkbox("Suche Zabudowy (Sufity/Ścianki)", value=False)
        do_podlogi = st.checkbox("Podłogi (panele + listwy)", value=True)
        do_drzwi = st.number_input("Liczba drzwi do wymiany (szt):", min_value=0, value=4)
        do_lazienka = st.checkbox("Remont Łazienki", value=True)

    # --- 2. LOGIKA MATEMATYCZNA PRO (Wyrównana do poziomu col_inv1) ---
    mnoznik_std = 0.8 if standard == "Ekonomiczny" else (1.3 if standard == "Premium" else 1.0)
    wtórny = 1.25 if stan_lokalu == "Rynek Wtórny (Do remontu)" else 1.0
    
    koszty = {}
    
    if do_elektryka:
        n_pkt = int(m2_total * 0.75)
        koszty["Elektryka"] = ((m2_total * 90) + (n_pkt * 35) + 2000) * wtórny * mnoznik_std

    if do_szpachlowanie:
        # Szpachlowanie liczone po powierzchni ścian (m2_total * 3.5)
        koszty["Szpachlowanie"] = (m2_total * 3.5) * 55 * mnoznik_std

    if do_malowanie:
        # Malowanie liczone po powierzchni ścian
        koszty["Malowanie"] = (m2_total * 3.5) * 40 * mnoznik_std

    if do_gk:
        # Szacunkowy koszt G-K dla flipera (zabudowy rur, sufity w łazience/korytarzu)
        koszty["Sucha Zabudowa"] = (m2_total * 120) * mnoznik_std

    if do_podlogi:
        koszty["Podłogi"] = m2_total * (110 * mnoznik_std)

    if do_lazienka:
        koszty["Łazienka"] = 15000 * wtórny * mnoznik_std

    if do_drzwi > 0:
        cena_drzwi = 1400 if standard == "Ekonomiczny" else 2100
        koszty["Stolarka"] = do_drzwi * (cena_drzwi + 250 + 40)

    # --- 3. WYNIKI I ROI ---
        total_remont = sum(koszty.values())
        bufor = total_remont * 0.12 
        
        st.success(f"### SZACOWANY KOSZT REMONTU: **{round(total_remont + bufor)} zł**")
        
        # --- ZBIORCZA LISTA ZAKUPÓW (DYNAMICZNA) ---
        with st.expander("📦 KOMPLETNA LISTA MATERIAŁÓW (Dla Inwestora)", expanded=True):
            c_z1, c_z2 = st.columns(2)
            
            with c_z1:
                if do_szpachlowanie:
                    pow_scian = m2_total * 3.5
                    st.write(f"**GŁADZIE ({marka_farby} standard):**")
                    st.write(f"- Masa: {int(pow_scian * 1.5 / 20) + 1} wiader")
                    st.write(f"- Zbrojenie: {technologia_spoin}")
                    if standard != "Ekonomiczny":
                        st.write(f"- Taśma Tuff-Tape (rolki): {int(m2_total/15)+1} szt.")

                if do_gk:
                    st.write(f"**SUCHA ZABUDOWA ({technologia_gk}):**")
                    # Rozszerzona lista G-K
                    st.write(f"- Płyty GK: {int(m2_total * 0.5)+2} szt.")
                    st.write(f"- Profil CD60 (3mb): {int(m2_total * 0.8)+4} szt.")
                    st.write(f"- Profil UD27 (3mb): {int(m2_total * 0.4)+2} szt.")
                    st.write(f"- Wieszaki ES/Obrotowe: {int(m2_total * 1.2)} szt.")
                    st.write(f"- Wkręty pchełki (op.): 1 szt.")

            with c_z2:
                if do_malowanie:
                    st.write(f"**MALOWANIE (Marka: {marka_farby}):**")
                    st.write(f"- Farba biała: {int(m2_total / 8)+1} L")
                    st.write(f"- Farba kolor: {int((m2_total * 2.5) / 10)+1} L")
                    st.write("- Akcesoria: folie, taśmy malarskie BLUE, wałki")

                if do_elektryka:
                    st.write("**ELEKTRYKA:**")
                    st.write(f"- Rozdzielnica: {'Plastikowa' if standard == 'Ekonomiczny' else 'Eaton/Hager'}")
                    st.write(f"- Osprzęt: {int(m2_total * 0.75)} szt. ({standard})")

                if do_lazienka:
                    st.write("**ŁAZIENKA:**")
                    st.write("- Stelaż WC podtynkowy: 1 kpl.")
                    st.write(f"- Płytki: {round(25 * mnoznik_mat / mnoznik_mat)} m²") # korekta m2
                    
        st.markdown("---")
        st.subheader("Kalkulator ROI")
        c_a, c_b = st.columns(2)
        cena_zakupu = c_a.number_input("Cena zakupu mieszkania:", value=350000, step=5000)
        prowizje_notariusz = c_b.number_input("Koszty transakcyjne (PCC/Notariusz):", value=18000)
        
        cena_sprzedazy = st.number_input("Przewidywana cena sprzedaży:", value=550000, step=5000)
        
        wszystkie_koszty = cena_zakupu + prowizje_notariusz + total_remont + bufor
        zysk_brutto = cena_sprzedazy - wszystkie_koszty
        
        podatek = max(0, zysk_brutto * 0.19)
        zysk_netto = zysk_brutto - podatek
        roi = (zysk_netto / wszystkie_koszty) * 100 if wszystkie_koszty > 0 else 0

        res1, res2 = st.columns(2)
        res1.metric("ZYSK NETTO (po podatku)", f"{round(zysk_netto)} zł")
        res2.metric("ROI", f"{round(roi, 1)} %")

        if zysk_netto < 30000:
            st.warning("⚠️ Niski zysk! Rozważ negocjację ceny lub optymalizację kosztów.")
        else:
            st.success("💰 Inwestycja wygląda obiecująco!")


st.markdown("<br><hr>", unsafe_allow_html=True)

# Tworzymy 3 kolumny, żeby logo było idealnie na środku
col_l, col_logo_bottom, col_r = st.columns([2, 1, 2])

with col_logo_bottom:
    try:
        # Pamiętaj o poprawnym wcięciu wewnątrz 'with'
        st.image("logo3.png", use_container_width=True)
    except:
        # Jeśli pliku nie ma, nic nie robimy
        pass 

# Tekst praw autorskich pod logo
st.markdown("""
    <p style='text-align: center; color: #BDC3C7; font-size: 14px; margin-top: 10px;'>
        © 2024 ProCalc. Wszelkie prawa zastrzeżone.
    </p>
    <br><br>
""", unsafe_allow_html=True)

