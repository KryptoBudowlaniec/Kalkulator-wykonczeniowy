import os
import streamlit as st
from supabase import create_client, Client

# 1. KONFIGURACJA GŁÓWNA (Musi być absolutnie pierwsza!)
st.set_page_config(
    page_title="ProCalc | Profesjonalny kalkulator remontowy",
    page_icon="logo2.png", 
    layout="wide"
)

# ==========================================
# BANER COOKIES I PRYWATNOŚCI
# ==========================================
# Inicjalizacja stanu dla ciasteczek
if "cookies_accepted" not in st.session_state:
    st.session_state.cookies_accepted = False

# Wyświetlanie banera, dopóki użytkownik nie kliknie akceptacji
if not st.session_state.cookies_accepted:
    # Tworzymy ładny, wyróżniony kontener na samej górze
    with st.container(border=True):
        st.markdown("### 🍪 Szanujemy Twoją prywatność")
        st.write("""
        Serwis ProCalc wykorzystuje pliki cookies niezbędne do prawidłowego działania aplikacji (utrzymywanie sesji logowania, zapisywanie projektów) oraz w celach analitycznych. 
        Dalsze korzystanie z serwisu oznacza akceptację naszej [Polityki Prywatności](#).
        """)
        
        # Przycisk akceptacji
        col_btn, col_puste = st.columns([1, 3])
        with col_btn:
            if st.button("Zrozumiałem i Akceptuję ✅", type="primary", use_container_width=True, key="btn_cookies"):
                st.session_state.cookies_accepted = True
                st.rerun() # Przeładowuje stronę, aby baner natychmiast zniknął
    
    # Dodajemy delikatną linię oddzielającą baner od reszty aplikacji
    st.markdown("---")

# --- TRICK DLA SMS/WHATSAPP (OPEN GRAPH) ---
st.markdown(
    f"""
    <head>
        <meta property="og:title" content="ProCalc | Profesjonalny Kalkulator Inwestora" />
        <meta property="og:description" content="Kompleksowe kosztorysy, analiza ROI i listy zakupów w jednym miejscu." />
        <meta property="og:image" content="https://raw.githubusercontent.com/KryptoBudowlaniec/Kalkulator-wykonczeniowy/main/logo.png" />
        <meta property="og:type" content="website" />
    </head>
    """,
    unsafe_allow_html=True
) 

# 2. KULOODPORNE POŁĄCZENIE Z SUPABASE
supabase = None

# Pobieranie kluczy z uwzględnieniem bezpiecznego omijania błędów st.secrets
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Jeśli brak na Renderze, próbujemy bezpiecznie pobrać ze Streamlit Secrets (lokalnie)
if not url or not key:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass # Ignorujemy błąd braku pliku secrets.toml, żeby nie zepsuć aplikacji

# Inicjalizacja połączenia z bazą
if url and key:
    try:
        supabase: Client = create_client(url, key)
        
        # --- Przywracanie i automatyczne odświeżanie sesji ---
        if "access_token" in st.session_state and "refresh_token" in st.session_state:
            try:
                # Próbujemy przywrócić sesję
                session_data = supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                
                # BARDZO WAŻNE: Jeśli Supabase odświeżyło token, zapisujemy ten nowy do pamięci Streamlita!
                if session_data and session_data.user:
                    st.session_state.access_token = session_data.session.access_token
                    st.session_state.refresh_token = session_data.session.refresh_token
                    
            except Exception as auth_error:
                # Jeśli token całkowicie wygasł (Already Used), cicho wylogowujemy użytkownika
                st.session_state.zalogowany = False
                st.session_state.pop("access_token", None)
                st.session_state.pop("refresh_token", None)
                st.session_state.pop("user_id", None)
                
    except Exception as e:
        st.error(f"Błąd połączenia z bazą danych: {e}")
else:
    st.error("Błąd konfiguracji: Nie znaleziono kluczy do bazy danych (SUPABASE_URL lub SUPABASE_KEY). Sprawdź ustawienia na Renderze.")

# --- STAN APLIKACJI (INICJALIZACJA) ---
if 'zalogowany' not in st.session_state:
    st.session_state.zalogowany = False
if 'pakiet' not in st.session_state:
    st.session_state.pakiet = "Podstawowy"
if 'przekierowanie' not in st.session_state:
    st.session_state.przekierowanie = False
# --- NOWE: Zapamiętujemy maila ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# --- HEADER: LOGO LEWA | MENU PRAWA ---
col_logo, col_nav = st.columns([1.5, 2.5]) 

with col_logo:
    try:
        st.image("logo2.png", use_container_width=True)
    except:
        st.error("Brak logo2.png")

with col_nav:
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    nawigacja = st.pills(
        "", 
        ["Start", "Kalkulatory", "Panel Inwestora", "Kontakt", "Logowanie"],
        selection_mode="single",
        default="Start",
        key="main_nav"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA PRZEKIEROWANIA (Klucz do naprawy) ---
if st.session_state.przekierowanie:
    branza = "Logowanie"
else:
    branza = nawigacja

# --- PODMENU ---
if nawigacja == "Kalkulatory":
    st.markdown("<br>", unsafe_allow_html=True)
    sub_nav_col = st.columns([1])[0]
    with sub_nav_col:
        branza = st.pills(
            "Wybierz branżę:", 
            ["Malowanie", "Szpachlowanie", "Tynkowanie", "Sucha Zabudowa", "Elektryka", "Łazienka", "Podłogi", "Drzwi", "Efekty Dekoracyjne"],
            selection_mode="single",
            default="Malowanie",
            key="sub_nav"
        )
else:
    branza = nawigacja


# --- STYLE CSS (Twoje, nietknięte!) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #FFFFFF !important; color: #1E1E1E !important; }
    li::before { content: none !important; display: none !important; }
    [data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] li { list-style-type: none !important; padding-left: 0px !important; margin-left: 0px !important; }
    .custom-card { background-color: #FFFFFF !important; border: 1px solid #E9ECEF !important; border-radius: 12px !important; padding: 20px !important; margin-bottom: 15px !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: flex-start !important; text-align: center !important; gap: 12px !important; height: 100% !important; min-height: 240px !important; transition: 0.3s; }
    .custom-card:hover { transform: translateY(-5px) !important; border-color: #00D395 !important; box-shadow: 0px 8px 20px rgba(0, 211, 149, 0.1) !important; }
    .card-title { color: #00D395 !important; font-size: 18px !important; font-weight: 800 !important; text-transform: uppercase !important; margin: 0 !important; padding: 0 !important; }
    .card-text { color: #6C757D !important; font-size: 14px !important; margin: 0 !important; padding: 0 !important; line-height: 1.4 !important; }
    .card-list { display: block !important; text-align: center !important; padding: 0 !important; margin: 0 auto !important; border: none !important; width: 100% !important; }
    .card-list li { font-size: 13px !important; color: #495057 !important; margin-bottom: 6px !important; display: block !important; font-weight: 600 !important; text-align: center !important; }
    .card-list li::before { content: "✔ " !important; color: #00D395 !important; font-weight: bold !important; margin-right: 5px !important; }
    .pricing-card { background-color: #FFFFFF; border: 2px solid #E9ECEF; border-radius: 15px; padding: 30px 20px; text-align: center; height: 100%; transition: 0.3s; position: relative; }
    .pricing-pro { border-color: #00D395; background-color: #F0FFF4; box-shadow: 0px 10px 30px rgba(0, 211, 149, 0.15); }
    .pricing-badge { position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background-color: #00D395; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; white-space: nowrap; }
    .pricing-price { font-size: 42px; font-weight: 800; color: #1E1E1E; margin: 15px 0 5px 0; }
    .pricing-sub { font-size: 13px; color: #6C757D; margin-bottom: 20px; min-height: 35px; }
    .faq-card-question { background: #FFF; border: 2px solid #00D395; border-radius: 15px 15px 0 0; padding: 20px; font-weight: 800; text-align: center; margin-top: 20px;}
    .faq-card-answer, .faq-card-answer-blue { background: #00D395; border-radius: 0 0 15px 15px; padding: 20px; color: #FFF !important; text-align: center; margin-bottom: 20px;}
    .faq-card-answer-blue { background: #0E172B; }
    div.stButton > button { background-color: #00D395 !important; color: white !important; font-weight: 800 !important; height: 60px !important; border-radius: 15px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# GŁÓWNA LOGIKA WYŚWIETLANIA (IF / ELIF)
# ==========================================

if branza == "Start":
    # ---------------- EKRAN STARTOWY (Nietknięty!) ----------------
    st.markdown("<h1 style='text-align: center; color: #00D395; font-size: 50px; margin-top: 0; font-weight: 800;'>Witaj w ProCalc</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 26px; margin-bottom: 50px; color: #495057;'>Twój Cyfrowy Kosztorysant Wykończeniowy</h3>", unsafe_allow_html=True)
    
    col_c1, col_center, col_c2 = st.columns([1, 4, 1])
    with col_center:
        st.markdown("<h2 style='text-align: center; color: #000000; margin-bottom: 40px; font-weight: 800;'>Dla kogo jest ProCalc?</h2>", unsafe_allow_html=True)
        
        benefity = [
            ["Inwestorzy", "Błyskawiczna analiza ROI i rentowności flipa. Podejmuj decyzje zakupowe w oparciu o twarde dane, a nie intuicję."],
            ["Ekipy Wykonawcze", "Precyzyjne listy materiałowe z dokładnością do jednego worka. Koniec z przestojami, błędami i zbędnymi kursami."],
            ["Klienci Prywatni", "Pełna kontrola nad budżetem remontowym. Wiesz dokładnie, ile zapłacisz za materiał i robociznę."]
        ]

        cols_ben = st.columns(3)
        for i, (tytul, tekst) in enumerate(benefity):
            with cols_ben[i]:
                st.markdown(f'<div class="custom-card"><div class="card-title">{tytul}</div><div class="card-text">{tekst}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        _, col_btn_top, _ = st.columns([1, 2, 1])
        with col_btn_top:
            if st.button("ZAŁÓŻ DARMOWE KONTO I ZAPISUJ KOSZTORYSY", use_container_width=True):
                st.info("👆 Aby założyć konto, wybierz zakładkę 'Logowanie' z menu na samej górze strony!")

        st.markdown("<div style='text-align: center; width: 100%; margin-top: 15px;'><p style='font-size: 15px; color: #6c757d; font-weight: 600;'>✅ Rejestracja zajmie Ci 30 sekund. Nie wymaga podpięcia karty płatniczej.</p></div>", unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Co oferują nasze kalkulatory?</h2>", unsafe_allow_html=True)
    
    oferta = [
        ["Malowanie", "Finalne wykończenie powierzchni.", ["Wydajność farb z bazy", "Obliczanie m2 i zapasów", "Dobór gruntów", "Wycena drobnego sprzętu"]], 
        ["Szpachlowanie", "Przygotowanie gładzi.", ["Masy sypkie i gotowe", "Zbrojenie narożników", "Taśmy flizelinowe", "Oszacowanie dniówek"]],
        ["Tynkowanie", "Prace tynkarskie.", ["Tynki maszynowe i GK", "Listwy i narożniki", "Dokładne zużycie kleju", "Grunty kwarcowe"]],
        ["Sucha Zabudowa", "Konstrukcje GK.", ["Systemy profili CD/UD", "Wyliczanie sztuk płyt", "Zbrojenie łączy (Tuff-Tape)", "Wełna izolacyjna"]],
        ["Elektryka", "Instalacja prądowa.", ["Szacowanie mb przewodów", "Osprzęt i rozdzielnica", "Uchwyty montażowe", "Puszki rtv/lan"]],
        ["Łazienka", "Kompleksowy remont.", ["Płytki (format i zapas)", "Hydroizolacja i taśmy", "Biały montaż (ryczałt)", "Fugi i sylikony"]],
        ["Podłogi", "Panele i winyle.", ["Metraż i odpad (jodełka)", "Listwy i podkłady", "Systemy poziomujące", "Chemia posadzkowa"]],
        ["Drzwi", "Stolarka wewnętrzna.", ["Drzwi bezprzylgowe", "Ościeżnice regulowane", "Pianki montażowe", "Opaski maskujące"]],
        ["Premium PRO", "Dla profesjonalistów.", ["Zapisywanie projektów", "Eksport PDF do hurtowni", "Zarządzanie stawkami", "Analiza ROI (flipy)"]]
    ]

    cols_oferta = st.columns(3)
    for i, item in enumerate(oferta):
        with cols_oferta[i % 3]:
            style_extra = "border: 2px solid #00D395; background-color: #F0FFF4 !important;" if item[0] == "Premium PRO" else ""
            lista_html = "".join([f"<li>{punkt}</li>" for punkt in item[2]])
            st.markdown(f'<div class="custom-card" style="{style_extra}"><div class="card-title">{item[0]}</div><div class="card-text" style="margin-bottom: 10px !important;">{item[1]}</div><ul class="card-list">{lista_html}</ul></div>', unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; width: 100%; padding: 20px;'><p style='font-size: 26px; font-weight: 800; color: #1E1E1E; margin-bottom: 10px;'>GOTOWY DO WYCENY?</p><p style='font-size: 20px; color: #00D395; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;'>Wybierz sekcję z menu bocznego i zacznij liczyć!</p></div>", unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Dlaczego warto nam zaufać?</h2><br>", unsafe_allow_html=True)
    zalety = [
        ["NORMY", "Algorytmy oparte na realnych normach zużycia materiałów z kart technicznych."],
        ["DOŚWIADCZENIE", "Aplikacja stworzona przy współpracy z wieloletnimi wykonawcami."],
        ["CENY", "Bazy cenowe aktualizowane na bieżąco według największych hurtowni."],
        ["PRECYZJA", "Zminimalizujesz ryzyko przestojów z powodu braku 1 worka kleju."],
        ["LISTY ZAKUPÓW", "Gotowe raporty dla sklepów oszczędzają Twój czas."],
        ["NIEZALEŻNOŚĆ", "Nie jesteśmy sponsorowani - dobierasz producenta sam."]
    ]
    _, col_main, _ = st.columns([1, 4, 1])
    with col_main:
        sub_l, sub_m, sub_r = st.columns(3) 
        kolumny = [sub_l, sub_m, sub_r, sub_l, sub_m, sub_r]
        for i, (tytul, opis) in enumerate(zalety):
            with kolumny[i]:
                st.markdown(f'<div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 30px; padding: 0 10px;"><div style="color: #00D395; font-size: 28px; margin-bottom: 10px; font-weight: bold; line-height: 1;">✔</div><div style="font-size: 15px; color: #495057; line-height: 1.4;"><b style="color: #1E1E1E; font-size: 16px; display: block; margin-bottom: 5px; text-transform: uppercase;">{tytul}</b><span style="display: block; opacity: 0.8;">{opis}</span></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
        
    _, col_demo, _ = st.columns([1, 1.5, 1])
    with col_demo:
        if st.button("SPRAWDŹ DARMOWE DEMO (MALOWANIE)", use_container_width=True, key="btn_demo_main"):
            st.info("👆 Wybierz zakładkę 'Kalkulatory' na górze, a następnie 'Malowanie'!")

    st.markdown("<p style='text-align: center; font-size: 14px; color: gray; margin-top: 5px;'>Nie wymaga logowania. Sprawdź jak to działa w 15 sekund.</p>", unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center; font-weight: 800;'>Wybierz pakiet dla siebie</h2>", unsafe_allow_html=True)
    _, col_p1, col_p2, col_p3, _ = st.columns([0.5, 3, 3, 3, 0.5])
    with col_p1:
        st.markdown('<div class="pricing-card"><h3 style="color: #1E1E1E; font-weight: 800; margin-bottom: 0;">Podstawowy</h3><div class="pricing-price">0 zł</div><div class="pricing-sub">Zawsze za darmo</div><ul class="card-list" style="margin-top: 10px !important;"><li>Dostęp do Szybkich Wycen</li><li>Podstawowe algorytmy zużycia</li><li>Brak możliwości zapisu projektów</li><li>Brak generatora ofert PDF</li></ul></div>', unsafe_allow_html=True)
    with col_p2:
        st.markdown('<div class="pricing-card"><h3 style="color: #1E1E1E; font-weight: 800; margin-bottom: 0;">PRO (Miesiąc)</h3><div class="pricing-price">19 zł <span style="font-size: 20px; color: #6C757D;">/ mc</span></div><div class="pricing-sub">Elastyczna subskrypcja z możliwością rezygnacji</div><ul class="card-list" style="margin-top: 10px !important;"><li><b>Wszystko z wersji Podstawowej</b></li><li>Precyzyjne listy zakupowe PRO</li><li>Nielimitowane generowanie PDF</li><li>Zapisywanie i edycja kosztorysów</li><li>Zaawansowany kalkulator (ROI)</li></ul></div>', unsafe_allow_html=True)
    with col_p3:
        st.markdown('<div class="pricing-card pricing-pro"><div class="pricing-badge">NAJLEPSZY WYBÓR</div><h3 style="color: #00D395; font-weight: 800; margin-bottom: 0;">PRO (Rok)</h3><div class="pricing-price">190 zł <span style="font-size: 20px; color: #6C757D;">/ rok</span></div><div class="pricing-sub"><b>Oszczędzasz 38 zł</b><br>(2 miesiące całkowicie GRATIS!)</div><ul class="card-list" style="margin-top: 10px !important;"><li><b>Wszystko to, co w pakiecie Miesiąc</b></li><li>Gwarancja stałej, niższej ceny</li><li>Priorytetowe wsparcie mailowe</li><li>Wcześniejszy dostęp do nowości</li></ul></div>', unsafe_allow_html=True)

    st.markdown("<br><br><h2 style='text-align: center;'>Często Zadawane Pytania</h2>", unsafe_allow_html=True)
    col_f1, col_faq, col_f2 = st.columns([1, 2.5, 1])
    with col_faq:
        st.markdown('<div class="faq-card-question">Czy wyceny materiałów są aktualne?</div><div class="faq-card-answer">Tak. Nasze bazy cenowe są aktualizowane raz w miesiącu na podstawie średnich cen rynkowych z największych marketów i hurtowni.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Czy mogę zapisać swój kosztorys?</div><div class="faq-card-answer-blue">Funkcja zapisywania i edycji wielu projektów jest dostępna dla zalogowanych użytkowników w wersji <b>Premium PRO</b>.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Jak dokładne są listy zakupowe?</div><div class="faq-card-answer">Algorytmy uwzględniają oficjalne normy zużycia producentów oraz standardowy naddatek 10% na odpady i docięcia.</div>', unsafe_allow_html=True)
        st.markdown('<div class="faq-card-question">Czy format płytek wpływa na wycenę?</div><div class="faq-card-answer-blue">Oczywiście. W sekcji Łazienka możesz wybrać format (np. 120x60), a system automatycznie podniesie stawkę za robociznę i zużycie kleju.</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.header("Plan Rozwoju Aplikacji (Roadmap)")
        col_dev1, col_dev2 = st.columns(2)
        with col_dev1:
            st.markdown("#### W TRAKCIE (Koncept/Dev)")
            st.info("**Live Progress (CRM)**\n\nInteraktywna checklista etapów prac.")
            st.info("**Dokumentacja Foto**\n\nMożliwość wgrywania zdjęć z budowy.")
        with col_dev2:
            st.markdown("#### DO ZROBIENIA (Plany)")
            st.success("**Efekty Dekoracyjne** – Beton architektoniczny, stiuk.")
            st.success("**Baza Danych (Cloud)** – Integracja z Firebase (zapisywanie projektów).")

# ==========================================
# TUTAJ WCHODZI NASZ NOWY PANEL INWESTORA!
# ==========================================
elif branza == "Panel Inwestora":
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.zalogowany:
        st.warning("Ta sekcja dostępna jest wyłącznie dla zalogowanych użytkowników.")
        st.info("Przejdź do zakładki 'Logowanie' w górnym menu, aby założyć darmowe konto.")
    else:
        # Odpalamy Sidebar (Boczne Menu)
        with st.sidebar:
            st.title("Panel Zarządzania")
            st.markdown(f"Konto: **{st.session_state.user_email}**")
            
            opcja_panelu = st.radio(
                "Nawigacja",
                ["Nawigacja Główna", "Mój Profil", "Język i Region"]
            )
            
            st.markdown("---")
            if st.button("Wyloguj (Panel)"):
                st.session_state.zalogowany = False
                if supabase: supabase.auth.sign_out()
                st.rerun()

        # Odpalamy Zawartość w zależności od wyboru w boczku
        if opcja_panelu == "Nawigacja Główna":
            st.header("Twoje Kosztorysy i Projekty")
            st.info("Tutaj docelowo wyświetlą się Twoje wyceny i analiza ROI.")
            
        elif opcja_panelu == "Mój Profil":
            st.header("Mój Profil Inwestora")
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Imię i Nazwisko / Nazwa Firmy")
            with c2:
                st.number_input("Domyślny narzut na materiały (%)", value=10)
                st.number_input("Twoja stawka za roboczogodzinę (PLN/h)", value=60)
            if st.button("Zapisz ustawienia profilu"):
                st.success("Zapisano zmiany!")
                
        elif opcja_panelu == "Język i Region":
            st.header("Ustawienia Regionalne")
            st.selectbox("Wybierz język", ["Polski", "English"])
            st.selectbox("Domyślna waluta", ["PLN", "EUR", "USD"])
            if st.button("Zapisz region"):
                st.success("Zapisano zmiany!")

elif branza == "Kontakt":
    # ---------------- EKRAN KONTAKTU (Nietknięty!) ----------------
    st.markdown("<h1 style='text-align: center; color: #00D395;'>Kontakt</h1>", unsafe_allow_html=True)
    _, col_k, _ = st.columns([1, 2, 1])
    with col_k:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <p class="card-text">Masz pytania lub propozycję współpracy? Napisz do nas!</p>
            <h3 style="color: #0E172B; font-weight: 800; margin: 20px 0;">biuro@procalc.pl</h3>
            <p class="card-text">Infolinia (Pn-Pt 8:00-16:00): <b>+48 123 456 789</b></p>
        </div>
        """, unsafe_allow_html=True)

elif branza == "Logowanie":
    # ---------------- EKRAN LOGOWANIA (Tylko dodany zapis maila!) ----------------
    # Wyłączamy flagę, żeby "odblokować" menu
    st.session_state.przekierowanie = False
    
    # 1. SPRAWDZAMY CZY UŻYTKOWNIK JEST JUŻ ZALOGOWANY
    if not st.session_state.zalogowany:
        # WIDOK DLA NIEZALOGOWANYCH (Formularz)
        st.markdown("<br><br>", unsafe_allow_html=True)
        email = st.text_input("Adres e-mail", placeholder="jan.kowalski@budowa.pl")
        haslo = st.text_input("Hasło", type="password", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
            
        col_auth1, col_auth2 = st.columns(2)
            
        with col_auth1:
            if st.button("ZALOGUJ SIĘ", use_container_width=True):
                if supabase: 
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": haslo})
                        st.session_state.zalogowany = True
                        st.session_state.user_id = res.user.id
                        st.session_state.user_email = email # <-- TO JEST JEDYNA ZMIANA TUTAJ
                        st.session_state.pakiet = "PRO"
                        
                        # --- Zapisujemy tokeny sesji ---
                        st.session_state.access_token = res.session.access_token
                        st.session_state.refresh_token = res.session.refresh_token
                        
                        st.rerun() 
                    except Exception as e:
                        st.error("Odmowa dostępu: Sprawdź poprawność maila i hasła.")
                else:
                    st.error("Błąd: Brak połączenia z chmurą Supabase.")

        with col_auth2:
            if st.button("REJESTRACJA", use_container_width=True):
                if supabase: 
                    try:
                        res = supabase.auth.sign_up({"email": email, "password": haslo})
                        st.success("Konto założone pomyślnie! Kliknij teraz 'ZALOGUJ SIĘ'.")
                    except Exception as e:
                        st.error(f"Błąd rejestracji: {e}")
                else:
                    st.error("Błąd: Brak połączenia z chmurą Supabase.")
                    
    else:
        # 2. WIDOK PO POMYŚLNYM ZALOGOWANIU
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.success("✅ Jesteś pomyślnie zalogowany!")
        st.info("Twój aktywny pakiet: **Premium PRO** 💎")
        
        st.markdown("<p style='text-align: center; color: #6C757D;'>Możesz teraz przejść do Kalkulatorów, korzystać z zaawansowanych opcji i zapisywać swoje projekty w chmurze.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        _, col_logout, _ = st.columns([1, 1, 1])
        with col_logout:
            if st.button("WYLOGUJ SIĘ", use_container_width=True, type="secondary"):
                # Czyścimy dane sesji
                st.session_state.zalogowany = False
                st.session_state.pakiet = "Podstawowy"
                # Wylogowujemy z bazy danych
                if supabase:
                    supabase.auth.sign_out()
                st.rerun()
                
# --- INICJALIZACJA STANU ---
if 'pokoje_pro' not in st.session_state:
    st.session_state.pokoje_pro = []
                
# --- INICJALIZACJA STANU ---
if 'pokoje_pro' not in st.session_state:
    st.session_state.pokoje_pro = []



# --- SEKCJA: MALOWANIE ---
if branza == "Malowanie":
    st.subheader("Kalkulator Malarski")
    tab_fast, tab_pro = st.tabs([" Szybka Wycena", " Kosztorys PRO"])

    # --- BAZA WIEDZY (Ceny rynkowe zaktualizowane: za 1 Litr / 1 Sztukę) ---
    baza_biale = {
        "Śnieżka Eko (Ekonomiczna)": 7,          # ok. 70 zł / 10L
        "Dekoral Polinak (Standard)": 10,        # ok. 100 zł / 10L
        "Beckers Designer White (Standard+)": 14,# ok. 140 zł / 10L
        "Magnat Ultra Matt (Premium)": 18,       # ok. 180 zł / 10L
        "Tikkurila Anti-Reflex 2 (Premium+)": 28,# ok. 280 zł / 10L
        "Flugger Flutex Pro 5 (Top Premium)": 35 # ok. 350 zł / 10L
    }
    
    baza_kolory = {
        "Śnieżka Barwy Natury (Eko)": 17,        # ok. 85 zł / 5L
        "Dekoral Akrylit W (Standard)": 20,      # ok. 100 zł / 5L
        "Magnat Ceramic (Standard+)": 30,        # ok. 150 zł / 5L
        "Beckers Designer Colour (Premium)": 32, # ok. 160 zł / 5L
        "Tikkurila Optiva 5 (Premium+)": 50,     # ok. 250 zł / 5L
        "Flugger Dekso (Top Premium)": 70        # ok. 350 zł / 5L (z barwieniem)
    }
    
    baza_grunty = {
        "Grunt Marketowy (Eko)": 5,              # ok. 25 zł / 5L
        "Unigrunt Atlas (Standard)": 8,          # ok. 40 zł / 5L
        "Ceresit CT 17 (Klasyk)": 12,            # ok. 60 zł / 5L
        "Mapei Primer G Pro (Premium)": 17       # ok. 85 zł / 5L
    }
    
    baza_tasmy = {
        "Żółta Papierowa (Market)": 8,
        "Solid (Niebieska)": 14,
        "Blue Dolphin (Profesjonalna)": 18,
        "Tesa Precision (Premium)": 25,
        "3M / Scotch (Top)": 30
    }
    
    with tab_fast:
        st.header(" Błyskawiczny szacunek kosztów")
        st.info("Pełne możliwości, dokładne pomiary i wybór konkretnych marek farb znajdziesz w zakładce Kosztorys PRO.")
        
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
            
            # Estymacja materiałów: średnio 12 zł za m2 powierzchni malowania (farba, grunt, folia, akcesoria) 
            # (obniżone z 14 zł po aktualizacji rynkowej dla standardu)
            estymacja_materialow = pow_malowania_fast * 12 
            
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
            ###  Chcesz większej precyzji?
            Przejdź do zakładki **Kosztorys PRO**, aby uzyskać dostęp do:
            * **Pełnej bazy materiałów:** Wybór konkretnych marek farb (kolor/biała), gruntów i taśm.
            * **Precyzyjnego planowania:** Możliwość dodawania każdej ściany z osobna (szerokość x wysokość).
            * **Sztukaterii:** Kalkulator listew ściennych i sufitowych wraz z klejami.
            * **Listy zakupowej:** Gotowe zestawienie ile dokładnie litrów farby i sztuk akcesoriów musisz kupić.
            """)

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_pro:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Ta sekcja dostępna jest wyłącznie dla użytkowników z pakietem Premium PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True, key="btn_odblokuj_malowanie"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            st.header("Profesjonalny Arkusz Kalkulacyjny")
            
            # --- SEKCJA 1: SZYBKI SZACUNEK (Otwarty wewnątrz PRO) ---
            st.subheader(" Szybki szacunek materiałów i robocizny")
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
                with c_money2: 
                    st.metric("Materiały (ok.)", f"{round(k_mat_sredni)} zł")
                
                st.markdown("---")

                # --- LISTA ZAKUPÓW (Widoczna na wierzchu) ---
                st.markdown("### Twoja lista zakupów")
                
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
                        pdf.add_font("Inter", "", font_path)
                        pdf.set_font("Inter", size=12)
                        font_exists = True
                    else:
                        pdf.set_font("Arial", size=12)
                        font_exists = False

                    # --- NAGŁÓWEK ---
                    if os.path.exists("logo.png"):
                        pdf.image("logo.png", x=10, y=8, w=35)
                    
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

                    lista_pdf = {
                        "Farba Biała (Sufity)": f"{round(l_biala, 1)}L ({f_biala})",
                        "Farba Kolor (Ściany)": f"{round(l_kolor, 1)}L ({f_kolor})",
                        "Grunt głęboko penetrujący": f"{round(l_grunt, 1)}L ({f_grunt})",
                        "Taśma malarska": f"{round(szt_tasma + 0.5)} szt. ({f_tasma})",
                        "Akryl szpachlowy": f"{round(szt_akryl + 0.5)} szt."
                    }
                    
                    if mb_sztukaterii > 0:
                        lista_pdf["Klej do listew"] = f"Bostik Mamut ({int(mb_sztukaterii/8 + 1)} szt.)"

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    for produkt, opis in lista_pdf.items():
                        pdf.cell(0, 8, f"- {czysc_tekst(produkt)}: {czysc_tekst(opis)}", ln=True)

                    # --- STOPKA ---
                    pdf.set_y(-25)
                    pdf.set_font("Inter" if font_exists else "Arial", size=8)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(0, 10, "Wygenerowano automatycznie przez proCalc. Kosztorys nie stanowi oferty handlowej.", 0, 0, 'C')

                    pdf_output = pdf.output(dest="S")
                    
                    if isinstance(pdf_output, str):
                        safe_bytes = pdf_output.encode('latin-1', 'replace')
                    else:
                        safe_bytes = bytes(pdf_output)
                    
                    st.download_button(
                        label="Pobierz Raport PDF",
                        data=safe_bytes,
                        file_name=f"Kosztorys_Malowanie_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Błąd PDF: {e}")





elif branza == "Szpachlowanie":
    st.header("Kalkulator Gładzi i Przygotowania Ścian")

    # 1. INICJALIZACJA BAZY DANYCH (Musi być na początku sekcji)
    baza_sypkie = {
        "Cekol C-45 (20kg)": {"cena": 65, "waga": 20},
        "FransPol GS-2 (20kg)": {"cena": 45, "waga": 20},
        "Dolina Nidy Omega (20kg)": {"cena": 38, "waga": 20},
        "Atlas Gipsar Uni (20kg)": {"cena": 45, "waga": 20}
    }
    
    baza_gotowe = {
        "Śmig A-2 (Wiadro 20kg)": {"cena": 55, "waga": 20},
        "Knauf Goldband Finish (18kg)": {"cena": 60, "waga": 18},
        "Knauf Goldband Finish (28kg)": {"cena": 80, "waga": 28},
        "Knauf Fill & Finish Light (20kg)": {"cena": 120, "waga": 20},
        "Sheetrock Super Finish (28kg)": {"cena": 135, "waga": 28},
        "Atlas GTA (18kg)": {"cena": 70, "waga": 18},
        "Atlas GTA (25kg)": {"cena": 90, "waga": 25}
    }
    
    baza_grunty_szp = {
        "Atlas Unigrunt (Standard)": 8,        # ok. 40 zł za 5L
        "Ceresit CT 17 (Klasyk)": 12,          # ok. 60 zł za 5L
        "Knauf Tiefengrund (Premium)": 14,     # ok. 70 zł za 5L
        "Mapei Primer G Pro (Koncentrat)": 17  # ok. 85 zł za 5L
    }

    if 'pokoje_szp' not in st.session_state:
        st.session_state.pokoje_szp = []

    tab_s1, tab_s2 = st.tabs([" Szybka Wycena", " Detale PRO"])

    # ==========================================
    # ZAKŁADKA 1: SZYBKA WYCENA (MINIMALISTYCZNA)
    # ==========================================
    with tab_s1:
        st.subheader("Błyskawiczny szacunek kosztów")
        
        c_fast1, c_fast2 = st.columns(2)
        with c_fast1:
            m2_podl_fast = st.number_input("Podaj metraż podłogi mieszkania (m2):", min_value=1.0, value=50.0, key="fast_podl")
        with c_fast2:
            l_warstw_fast = st.slider("Liczba warstw gładzi:", 1, 3, 2, key="fast_warstwy", help="1 warstwa = odświeżenie, 2 = standard, 3 = bardzo krzywe ściany")
        
        st.markdown("---")
        
        # LOGIKA: 3.5m2 ściany na 1m2 podłogi
        m2_scian_fast = m2_podl_fast * 3.5
        
        # DYNAMICZNA CENA: 
        # Baza (gruntowanie/szlifowanie) = 20 zł
        # Każda warstwa gładzi (materiał + robota) = 30 zł
        # W efekcie: 1 warstwa = 50 zł/m2, 2 warstwy = 80 zł/m2, 3 warstwy = 110 zł/m2
        cena_za_m2_fast = 20 + (l_warstw_fast * 30)
        
        szacunek_total = m2_scian_fast * cena_za_m2_fast 
        
        st.success(f"### Szacowany koszt całkowity: **ok. {round(szacunek_total):,} PLN**".replace(",", " "))
        
        # Wyświetlanie rozbicia w ładnych kafelkach
        c_wynik1, c_wynik2 = st.columns(2)
        c_wynik1.metric("Szacowana Robocizna (~65%)", f"{round(szacunek_total * 0.65):,} PLN".replace(",", " "))
        c_wynik2.metric("Szacowane Materiały (~35%)", f"{round(szacunek_total * 0.35):,} PLN".replace(",", " "))
        
        st.info("💡 **Jak to policzyliśmy?** Przyjęto średnio 3.5 m² ścian na każdy metr podłogi. "
                f"Obecna stawka ryczałtowa to **{cena_za_m2_fast} zł/m²** (robocizna + materiał) za {l_warstw_fast} warstwy.")
        st.caption("Aby wybrać konkretny rodzaj gładzi (gotowa/sypka), ustawić własne stawki lub dodać precyzyjnie wymiary pomieszczeń, przejdź do zakładki **Detale PRO**.")

    # ==========================================
    # ZAKŁADKA 2: DETALE PRO
    # ==========================================
    with tab_s2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Ta sekcja dostępna jest wyłącznie dla użytkowników z pakietem Premium PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True, key="btn_odblokuj_szpachlowanie"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
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
                # 1. Obliczenia materiałowe
                kg_gladzi = m2_total * norma_g * l_warstw
                szt_gladzi = int((kg_gladzi / dane_g["waga"]) + 0.99)
                szt_gruntu = int(m2_total * 0.2 / 5 + 0.99) # Wyliczamy bańki (5L)
                szt_krazkow = max(int(podl_total / 10), 5) # 1 krążek na 10m2 podłogi (min. 5 szt.)
                
                # Obliczenia kosztów
                koszt_m_gladzi = szt_gladzi * dane_g["cena"]
                koszt_m_grunt = szt_gruntu * (baza_grunty_szp[wybrany_grunt] * 5) 
                koszt_m_dodatki = podl_total * 15 
                
                # Sumy końcowe
                robocizna_total = m2_total * stawka_szp
                materiały_total = koszt_m_gladzi + koszt_m_grunt + koszt_m_dodatki
                suma_total = robocizna_total + materiały_total
                
                # 2. Wyświetlanie wyników na stronie
                st.markdown("---")
                st.success(f"### WARTOŚĆ CAŁKOWITA: **{round(suma_total)} PLN**")
                
                res1, res2 = st.columns(2)
                res1.metric("Twoja Robocizna", f"{round(robocizna_total)} PLN")
                res2.metric("Materiały", f"{round(materiały_total)} PLN")
                
                # --- LISTA ZAKUPÓW NA WIERZCHU ---
                st.markdown("---")
                st.subheader(" Lista Zakupów")
                c_zak1, c_zak2 = st.columns(2)
                
                with c_zak1:
                    st.info("**MATERIAŁY GŁÓWNE**")
                    st.write(f"🔹 **Gładź ({wybrana_g}):** {szt_gladzi} szt.")
                    st.write(f"🔹 **Grunt ({wybrany_grunt}):** {szt_gruntu} baniek (5L)")
                with c_zak2:
                    st.warning("**MATERIAŁY ZUŻYWALNE**")
                    st.write(f" **Krążki ścierne P180:** {szt_krazkow} szt.")
                    st.write(f" **Narożniki / Akcesoria:** wliczono ryczałt (~{round(koszt_m_dodatki)} zł)")

                # --- GENEROWANIE PDF ---
                st.markdown("---")
                c_pdf1, c_pdf2 = st.columns(2)
                    
                with c_pdf1:
                    if st.button("Wyczyść wszystko", use_container_width=True, key="btn_wyczysc_szpachlowanie_pro"):
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
                            
                        # Funkcja do czyszczenia polskich znaków w PDF
                        def czysc_tekst(tekst):
                            pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                            for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                            return tekst.encode('latin-1', 'replace').decode('latin-1')
                            
                        pdf.cell(0, 8, f"- Gladz: {czysc_tekst(wybrana_g)} ({szt_gladzi} szt.)", ln=True)
                        pdf.cell(0, 8, f"- Grunt: {czysc_tekst(wybrany_grunt)} ({szt_gruntu} baniek 5L)", ln=True)
                        pdf.cell(0, 8, f"- Krazki scierne (zyrafa): {szt_krazkow} szt.", ln=True)
                        pdf.cell(0, 8, f"- Liczba warstw: {l_warstw}", ln=True)
                        pdf.cell(0, 8, f"- Calkowita pow. netto: {round(m2_total, 1)} m2", ln=True)

                        pdf_bytes = pdf.output(dest="S")
                        
                        # Konwersja do bezpiecznego formatu dla Streamlit
                        if isinstance(pdf_bytes, str):
                            safe_bytes = pdf_bytes.encode('latin-1', 'replace')
                        else:
                            safe_bytes = bytes(pdf_bytes)

                        st.download_button(
                            label="Pobierz PDF (PRO)",
                            data=safe_bytes,
                            file_name=f"Szpachlowanie_Raport_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Błąd PDF: {e}")
           

# --- SEKCJA: PODŁOGI ---
# --- SEKCJA: PODŁOGI ---
elif branza == "Podłogi":
    st.header("Kalkulator Podłóg: Panele, Deska i Płytki")
    
    # --- BAZA CENOWA CHEMII GLAZURNICZEJ ---
    baza_kleje_plytki = {
        "Atlas Geoflex (Żelowy S1) - 25kg": 75.0,
        "Mapei Keraflex Extra S1 - 25kg": 80.0,
        "Kerakoll Bioflex (Żelowy S1) - 25kg": 85.0,
        "Atlas Plus (Wysokoelastyczny S1) - 25kg": 105.0,
        "Kerakoll H40 No Limits (Top Żel) - 25kg": 125.0
    }

    tab_p1, tab_p2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_p1:
        st.subheader("Błyskawiczny szacunek kosztów")
        m2_fast_p = st.number_input("Metraż podłogi (m2):", min_value=1.0, value=20.0, step=1.0, key="pod_m_fast")
        typ_fast = st.radio("Typ posadzki:", ["Panele (Pływające)", "Płytki / Gres"])
        
        if typ_fast == "Panele (Pływające)":
            k_rob_fast = m2_fast_p * 45
            k_mat_fast = m2_fast_p * 15
        else:
            k_rob_fast = m2_fast_p * 120
            k_mat_fast = m2_fast_p * 45
            
        total_fast = k_rob_fast + k_mat_fast
        
        st.success(f"### Szacowany koszt realizacji: ok. {round(total_fast)} PLN")
        st.caption("Cena nie zawiera zakupu samych paneli/płytek.")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        c_f2.metric("Szacowana Chemia/Dodatki", f"{round(k_mat_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby wyliczyć zapasy, wybrać konkretny klej i wygenerować raport PDF.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_p2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Zaawansowane wyliczenia zużycia klejów, systemów poziomujących oraz generowanie PDF dostępne są w wersji PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_podlogi"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            col_p1, col_p2 = st.columns([1, 1.2])
            
            with col_p1:
                st.subheader("Konfiguracja posadzki")
                m2_p = st.number_input("Dokładny metraż podłogi (m2):", min_value=0.1, value=20.0, step=0.1, key="pod_m_pro")
                
                system_montazu = st.radio("System montażu:", 
                                         ["Pływający (Na podkładzie)", 
                                          "Klejony (Deska na kleju)", 
                                          "Płytki / Gres (System poziomujący)"])
                
                if system_montazu == "Płytki / Gres (System poziomujący)":
                    st.markdown("---")
                    st.write("**Parametry płytek i chemia**")
                    c_pl1, c_pl2 = st.columns(2)
                    dl_p = c_pl1.number_input("Długość płytki (cm):", 10, 200, 60)
                    sz_p = c_pl2.number_input("Szerokość płytki (cm):", 10, 200, 60)
                    typ_ukladania = "Płytki (10% zapasu)"
                    m2_paczka = st.number_input("M2 w paczce płytek:", min_value=0.1, value=1.44, step=0.01)
                    wybrany_klej_plytki = st.selectbox("Wybierz klej do gresu:", list(baza_kleje_plytki.keys()))
                else:
                    st.markdown("---")
                    st.write("**Parametry deski/paneli**")
                    typ_ukladania = st.selectbox("Sposób układania:", ["Zwykły panel (7% zapasu)", "Jodełka (20% zapasu)"])
                    m2_paczka = st.number_input("M2 w paczce paneli/desek:", min_value=0.1, value=2.22, step=0.01)
                
                st.markdown("---")
                domyslna_stawka = 120 if "Płytki" in system_montazu else (45 if "Zwykły" in typ_ukladania else 100)
                stawka_podl = st.number_input("Stawka za m2 montażu (zł):", 1, 300, domyslna_stawka)

            # --- LOGIKA OBLICZEŃ ---
            if "Płytki" in system_montazu:
                zapas = 0.10
            else:
                zapas = 0.07 if "Zwykły" in typ_ukladania else 0.20
                
            m2_z_zapasem = m2_p * (1 + zapas)
            paczki_szt = int(m2_z_zapasem / m2_paczka + 0.99)
            
            info_zakup = [] 
            koszt_akc = 0

            if system_montazu == "Pływający (Na podkładzie)":
                wybrany_mat = st.selectbox("Rodzaj podkładu:", ["Premium (Rolka 8m2)", "Ecopor (Paczka 7m2)", "Standard (Pianka 10m2)"])
                wydajnosci = {"Premium (Rolka 8m2)": 8, "Ecopor (Paczka 7m2)": 7, "Standard (Pianka 10m2)": 10}
                ceny_p = {"Premium (Rolka 8m2)": 180, "Ecopor (Paczka 7m2)": 55, "Standard (Pianka 10m2)": 35}
                szt_podkladu = int(m2_p / wydajnosci[wybrany_mat] + 0.99)
                koszt_akc = szt_podkladu * ceny_p[wybrany_mat]
                info_zakup.append((f"Podkład {wybrany_mat}", f"{szt_podkladu} szt."))

            elif system_montazu == "Klejony (Deska na kleju)":
                wiader_kleju = int(m2_p / 12 + 0.99) 
                baniek_gruntu = int(m2_p / 30 + 0.99) 
                koszt_akc = (wiader_kleju * 280) + (baniek_gruntu * 60) 
                info_zakup.append(("Klej poliuretanowy do podłóg (15kg)", f"{wiader_kleju} wiader"))
                info_zakup.append(("Grunt podkładowy (5L)", f"{baniek_gruntu} baniek"))

            else: # Płytki / Gres
                zuzycie_m2 = (1 / ((dl_p/100) * (sz_p/100))) * 4
                suma_klipsow = int(zuzycie_m2 * m2_p * 1.1)
                op_klipsy = int(suma_klipsow / 100 + 0.99)
                
                kg_kleju_gres = m2_p * 5.0
                worki_kleju = int(kg_kleju_gres / 25 + 0.99)
                
                cena_wybranego_kleju = baza_kleje_plytki[wybrany_klej_plytki]
                koszt_akc = (op_klipsy * 40) + (worki_kleju * cena_wybranego_kleju)
                info_zakup.append(("System poziomujący (klipsy)", f"{op_klipsy} op. (po 100 szt.)"))
                info_zakup.append((f"{wybrany_klej_plytki}", f"{worki_kleju} worków"))

            k_robocizna = m2_p * stawka_podl
            usluga_plus_chemia = k_robocizna + koszt_akc 

            with col_p2:
                st.subheader("Podsumowanie Kosztorysu")
                
                st.success(f"### KOSZT REALIZACJI: **{round(usluga_plus_chemia)} PLN**")
                st.caption("Cena obejmuje robociznę oraz niezbędną chemię. Nie zawiera ceny okładziny.")

                c1, c2 = st.columns(2)
                c1.metric("Robocizna", f"{round(k_robocizna)} PLN")
                c2.metric("Chemia / Podkłady", f"{round(koszt_akc)} PLN")

                st.markdown("---")
                st.subheader("Lista materiałowa")
                
                st.write(f"• **Okładzina główna:** {paczki_szt} paczek")
                st.caption(f"Powierzchnia z uwzględnieniem {int(zapas*100)}% zapasu: {round(m2_z_zapasem, 2)} m2")
                
                for nazwa, ilosc in info_zakup:
                    st.write(f"• **{nazwa}:** {ilosc}")
                
                if "Płytki" in system_montazu:
                    st.info(f"Wyliczono system poziomujący dla formatu {dl_p}x{sz_p} cm.")
                
                st.markdown("---")

                # --- GENERATOR PDF (PODŁOGI) ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os
                    import base64

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="pod_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: PRACE POSADZKOWE", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Metraz calkowity:", 1)
                        pdf.cell(95, 10, f" {m2_p} m2", 1, 1)
                        pdf.cell(95, 10, " System montazu:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(system_montazu)}", 1, 1)
                        
                        if "Płytki" in system_montazu:
                            pdf.cell(95, 10, " Format plytki:", 1)
                            pdf.cell(95, 10, f" {dl_p}x{sz_p} cm", 1, 1)

                        pdf.ln(10)
                        pdf.cell(95, 10, " Robocizna (Montaz):", 1)
                        pdf.cell(95, 10, f" {round(k_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Chemia i materialy:", 1)
                        pdf.cell(95, 10, f" {round(koszt_akc)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " LACZNIE REALIZACJA:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(usluga_plus_chemia)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA MATERIALOWA DO ZAMOWIENIA:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        
                        pdf.cell(0, 7, f"- Okladzina: {paczki_szt} paczek (zawiera {int(zapas*100)}% zapasu)", ln=True)
                        for nazwa, ilosc in info_zakup:
                            pdf.cell(0, 7, f"- {czysc_tekst(nazwa)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Kosztorys_Podloga.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Błąd PDF: {e}")
                      
# --- SEKCJA: TYNKOWANIE ---
elif branza == "Tynkowanie":
    st.header("Kalkulator Tynków i Suchego Tynku")
    
    # --- BAZA DANYCH (Zaktualizowane ceny rynkowe) ---
    baza_masy = {
        "Knauf Uniflott (25kg)": 140, 
        "Knauf Vario (5kg)": 45,
        "Dolina Nidy Start (20kg)": 50,
        "Franspol (20kg)": 60
    }

    baza_tynkow = {
        "Knauf MP 75 (Maszynowy Gipsowy)": {"cena": 34, "waga": 30, "norma": 0.8, "typ": "mokry"},
        "Baumit MPI25 Cem-Wap": {"cena": 32, "waga": 30, "norma": 1.4, "typ": "mokry"},
        "Wyklejanie Płytami GK (Suchy Tynk)": {"cena_plyta": 35, "cena_klej": 28, "typ": "drywall"}
    }
    
    baza_grunt_kwarc = {
        "Dolina Nidy Inter-Grunt (20kg)": 130, 
        "Knauf Betokontakt (20kg)": 220, 
        "Atlas Grunto-Plast (20kg)": 145
    }

    tab_t1, tab_t2 = st.tabs(["Szybka Wycena", "Detale PRO"])

    # --- TAB 1: SZYBKA WYCENA ---
    with tab_t1:
        st.subheader("Błyskawiczny szacunek")
        m2_podl_fast = st.number_input("Metraż mieszkania (podłoga m2):", 1.0, 500.0, 50.0, key="tyn_m_fast")
        
        # Uproszczona logika: Średnio 3x metraż podłogi, średnia cena 85 zł/m2 (robocizna + mat)
        szacunkowy_metraz = m2_podl_fast * 3.0
        szacunkowy_koszt = szacunkowy_metraz * 85
        
        st.metric("Przybliżony koszt całkowity", f"{round(szacunkowy_koszt)} PLN")
        st.caption(f"Szacowany metraż ścian i sufitów: ok. {round(szacunkowy_metraz)} m²")
        
        st.markdown("---")
        st.info("""
        **Co zyskujesz w wersji PRO?**
        * Wybór konkretnych systemów (Gipsowe, Cem-Wap, GK).
        * Precyzyjne obliczenia stolarki (okna, narożniki, folie).
        * Pełna lista zakupów (liczba worków, płyt, rolek taśm).
        * Profesjonalny raport PDF z normami zużycia.
        """)

    # --- TAB 2: DETALE PRO ---
    with tab_t2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Precyzyjne zestawienie materiałów dla tynków mokrych i suchych dostępne jest tylko dla użytkowników PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_tynki"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
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
                    grubosc_t = 0 
                else:
                    wybrany_grunt_t = st.selectbox("Wybierz grunt kwarcowy:", list(baza_grunt_kwarc.keys()))
                    grubosc_t = st.slider("Średnia grubość tynku (mm):", 10, 40, 15)
                
                stawka_rob_t = st.number_input("Stawka robocizny (zł/m2):", 10, 200, 50)

                st.markdown("---")
                st.subheader("Stolarka (Okna i Drzwi)")
                
                std_okna = {
                    "Własny wymiar": None,
                    "60x60 (Łazienkowe)": (60, 60),
                    "90x120 (Standard 1)": (90, 120),
                    "120x120 (Standard 2)": (120, 120),
                    "150x150 (Duże)": (150, 150),
                    "90x210 (Balkonowe)": (90, 210),
                    "240x210 (Tarasowe HS)": (240, 210),
                    "100x210 (Drzwi wejściowe)": (100, 210)
                }

                wybor_okna = st.selectbox("Wybierz typ okna:", list(std_okna.keys()))
                
                col_o1, col_o2 = st.columns(2)
                if wybor_okna == "Własny wymiar":
                    w_szer = col_o1.number_input("Szerokość (cm):", 10, 600, 100, key="w_szer_tyn")
                    w_wys = col_o2.number_input("Wysokość (cm):", 10, 600, 120, key="w_wys_tyn")
                else:
                    w_szer, w_wys = std_okna[wybor_okna]
                    col_o1.info(f"Szer: {w_szer} cm")
                    col_o2.info(f"Wys: {w_wys} cm")

                ile_okien = st.number_input("Liczba takich okien (szt.):", 1, 50, 1, key="ile_okien_tyn")

                if "lista_okien_tyn" not in st.session_state:
                    st.session_state.lista_okien_tyn = []

                if st.button("Dodaj okna do zestawienia", use_container_width=True, key="btn_add_okno_tyn"):
                    st.session_state.lista_okien_tyn.append({
                        "nazwa": wybor_okna,
                        "szer": w_szer,
                        "wys": w_wys,
                        "szt": ile_okien
                    })
                    st.rerun()

                if st.session_state.lista_okien_tyn:
                    for i, o in enumerate(st.session_state.lista_okien_tyn):
                        c_ok1, c_ok2 = st.columns([4, 1])
                        c_ok1.caption(f"{o['szt']}x {o['nazwa']} ({o['szer']}x{o['wys']})")
                        if c_ok2.button("Usuń", key=f"del_o_tyn_{i}"):
                            st.session_state.lista_okien_tyn.pop(i)
                            st.rerun()

            # --- OBLICZENIA PRO ---
            lista_zakupow = []
            if dane_t["typ"] == "mokry":
                kg_na_m2_t = dane_t["norma"] * grubosc_t
                kg_razem_t = m2_rob_pro * kg_na_m2_t
                worki_t = int(kg_razem_t / dane_t["waga"] + 0.99)
                wiadra_gruntu = int((m2_rob_pro * 0.3) / 20 + 0.99)
                koszt_mat_t = (worki_t * dane_t["cena"]) + (wiadra_gruntu * baza_grunt_kwarc[wybrany_grunt_t]) + (m2_rob_pro * 5)
                lista_zakupow = [
                    (f"Tynk {wybrany_tynk}", f"{worki_t} worków"),
                    (f"Grunt kwarcowy {wybrany_grunt_t}", f"{wiadra_gruntu} wiader 20kg")
                ]
            else:
                liczba_plyt = int((m2_rob_pro * 1.1) / 3.12 + 0.99)
                worki_kleju = int(liczba_plyt / 2.5 + 0.99)
                worki_masy = int((m2_rob_pro * 0.5) / 25 + 0.99)
                
                mb_laczen = m2_rob_pro * 1.5
                if typ_tasmy == "Wszystko Tuff-Tape (Pancerne)":
                    rolki_tuff = int(mb_laczen / 30 + 0.99)
                    cena_tasmy = rolki_tuff * 150
                    zbrojenie_lista = [("Taśma Tuff-Tape (30m)", f"{rolki_tuff} rolka/i")]
                else:
                    rolki_tuff = int((m2_rob_pro * 0.4) / 30 + 0.99)
                    rolki_fliz = int((m2_rob_pro * 1.1) / 25 + 0.99)
                    cena_tasmy = (rolki_tuff * 150) + (rolki_fliz * 20)
                    zbrojenie_lista = [
                        ("Taśma Tuff-Tape (30m)", f"{rolki_tuff} rolka/i"),
                        ("Taśma flizelina (25m)", f"{rolki_fliz} rolka/i")
                    ]

                koszt_mat_t = (liczba_plyt * dane_t["cena_plyta"]) + (worki_kleju * dane_t["cena_klej"]) + \
                              (worki_masy * baza_masy[wybrana_masa]) + cena_tasmy + (m2_rob_pro * 2)
                
                lista_zakupow = [
                    ("Płyty GK (1.2x2.6m)", f"{liczba_plyt} szt."),
                    ("Klej gipsowy do płyt", f"{worki_kleju} worków"),
                    (f"Masa spoinowa {wybrana_masa}", f"{worki_masy} szt.")
                ]
                lista_zakupow.extend(zbrojenie_lista)

            # --- LOGIKA STOLARKI ---
            total_mb_naroznikow = 0.0
            total_m2_folii = 0.0
            total_mb_tasmy = 0.0

            for o in st.session_state.get("lista_okien_tyn", []):
                s = o["szer"] / 100 
                w = o["wys"] / 100
                szt = o["szt"]
                mb_na_okno = (2 * w) + s
                total_mb_naroznikow += (mb_na_okno * 1.30) * szt
                total_m2_folii += (s * w * szt) * 1.15
                total_mb_tasmy += ((2 * s + 2 * w) * 1.10) * szt

            szt_naroznik_3m = int(total_mb_naroznikow / 3 + 0.99)
            rolki_tasmy_50m = int(total_mb_tasmy / 50 + 0.99)
            szt_folii_op = int(total_m2_folii / 20 + 0.99)

            koszt_stolarki = (szt_naroznik_3m * 8) + (rolki_tasmy_50m * 25) + (szt_folii_op * 15)

            if total_mb_naroznikow > 0:
                lista_zakupow.append(("Narożniki aluminiowe (3m)", f"{szt_naroznik_3m} szt."))
                lista_zakupow.append(("Taśma malarska (50m)", f"{rolki_tasmy_50m} rolka/i"))
                lista_zakupow.append(("Folia ochronna okienna", f"{szt_folii_op} op."))

            koszt_mat_t += koszt_stolarki
            koszt_rob_t = m2_rob_pro * stawka_rob_t
            suma_tynki = koszt_mat_t + koszt_rob_t

            with col_t2:
                st.subheader("Wynik PRO")
                st.success(f"### RAZEM: **{round(suma_tynki)} PLN**")
                
                c1, c2 = st.columns(2)
                c1.metric("Robocizna", f"{round(koszt_rob_t)} zł")
                c2.metric("Materiały", f"{round(koszt_mat_t)} zł")

                st.markdown("---")
                st.subheader("Zestawienie materiałowe")
                for przedmiot, ilosc in lista_zakupow:
                    st.write(f"• **{przedmiot}:** {ilosc}")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import base64
                    import os

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Raport PDF", use_container_width=True, key="btn_pdf_tyn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)

                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "OFERTA: TYNKOWANIE / SUCHY TYNK", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Powierzchnia prac:", 1)
                        pdf.cell(95, 10, f" {round(m2_rob_pro, 1)} m2", 1, 1)
                        pdf.cell(95, 10, " Robocizna:", 1)
                        pdf.cell(95, 10, f" {round(koszt_rob_t)} PLN", 1, 1)
                        pdf.cell(95, 10, " Materialy:", 1)
                        pdf.cell(95, 10, f" {round(koszt_mat_t)} PLN", 1, 1)
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_tynki)} PLN", 1, 1, 'L', True)

                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA MATERIALOW:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        for przedmiot, ilosc in lista_zakupow:
                            pdf.cell(0, 7, f"- {czysc_tekst(przedmiot)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Oferta_Tynki.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Problem z PDF: {e}")
                    
# --- SEKCJA: SUCHA ZABUDOWA ---
elif branza == "Sucha Zabudowa":
    st.header("Kompleksowe Systemy G-K")
    
    # --- BAZA CENOWA ---
    baza_mat_gk = {
        "Plyta GK 12.5mm (szt)": 32.0, 
        "Profil CD60 (3mb)": 16.0, 
        "Profil UD27 (3mb)": 11.0,
        "Profil CW50 (3mb)": 19.0, 
        "Profil UW50 (3mb)": 15.0, 
        "Profil CW75 (3mb)": 23.0, 
        "Profil UW75 (3mb)": 18.0, 
        "Profil CW100 (3mb)": 28.0, 
        "Profil UW100 (3mb)": 22.0, 
        "Profil UA50 (3mb)": 75.0,
        "Profil UA75 (3mb)": 85.0,
        "Profil UA100 (3mb)": 95.0,
        "Wieszak ES / Obrotowy (szt)": 1.5, 
        "Wkrety TN25 (1000szt)": 40.0,
        "Wkrety TN35 (1000szt)": 50.0, 
        "Kolki 8x60 (100szt)": 35.0, 
        "Welna (m2)": 16.0
    }
    
    baza_masy_gk = {
        "Knauf Uniflott (25kg)": 140, 
        "Rigips Vario (25kg)": 145, 
        "Dolina Nidy Start (20kg)": 60, 
        "Franspol GS-6(20kg)": 96
    }

    if "pokoje_sufit" not in st.session_state:
        st.session_state.pokoje_sufit = []

    tab_gk1, tab_gk2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_gk1:
        st.subheader("Blyskawiczny szacunek kosztow")
        m2_fast = st.number_input("Przyblizony metraz zabudowy (m2):", min_value=1.0, value=20.0, key="gk_fast_m2")
        
        # Uśrednione stawki: robota 120, materiał 75
        k_rob_fast = m2_fast * 120
        k_mat_fast = m2_fast * 75
        total_fast = k_rob_fast + k_mat_fast
        
        st.success(f"### Szacowany koszt calkowity: ok. {round(total_fast)} PLN")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        c_f2.metric("Szacowane Materialy", f"{round(k_mat_fast)} PLN")
        
        st.info("Powyzsza wycena jest usredniona. Przejdz do zakladki Kosztorys PRO, aby wyliczyc systemy CD/UD lub CW/UW i pobrac liste zakupow.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_gk2:
        # --- BLOKADA PRO ---
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            st.warning("Zaawansowane wyliczenia konstrukcji szkieletowych, wieszaków i izolacji dostępne są w wersji PRO.")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Logowanie)", use_container_width=True, key="btn_odblokuj_gk"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH PRO ---
            m2_gk = 0.0
            robocizna = 0
            total_material = 0
            szer_profilu = 60
            laczniki_cd1 = laczniki_cd2 = laczniki_krzyzowe = 0
            szt_cd = szt_ud = szt_wieszaki = 0
            szt_cw = szt_uw = szt_ua = 0
            grubosc_welny = None
            izolacja_gk = False
            plytowanie = "1xGK (Jednostronnie)"
            lista_z = []
            
            col_g1, col_g2 = st.columns([1, 1.2])

            with col_g1:
                st.subheader("Konfiguracja konstrukcji")
                rodzaj_gk = st.radio("Co budujemy?", ["Sufit Podwieszany", "Sciana Dzialowa"], key="gk_type_pro")
                dl_profilu_cd = 3.0
                
                if rodzaj_gk == "Sufit Podwieszany":
                    st.markdown("---")
                    st.write("**Dodaj pomieszczenia do zabudowy sufitu:**")
                    c1, c2, c3 = st.columns([2,1,1])
                    nazwa_suf = c1.text_input("Pomieszczenie:", placeholder="np. Salon", key="suf_n_pro")
                    dl_suf = c2.number_input("Dl. (m):", min_value=0.1, value=5.0, key="suf_d_pro")
                    sz_suf = c3.number_input("Szer. (m):", min_value=0.1, value=4.0, key="suf_s_pro")
                    typ_stelaza_suf = st.radio("Rodzaj stelaza dla tego pokoju:", ["Pojedynczy", "Krzyzowy"], horizontal=True, key="suf_typ_pro")

                    if st.button("Dodaj sufit do listy", use_container_width=True, key="btn_add_suf_pro"):
                        st.session_state.pokoje_sufit.append({
                            "nazwa": nazwa_suf if nazwa_suf else f"Pokoj {len(st.session_state.pokoje_sufit)+1}",
                            "dl": dl_suf,
                            "sz": sz_suf,
                            "typ": typ_stelaza_suf
                        })
                        st.rerun()

                    if st.session_state.pokoje_sufit:
                        for i, p in enumerate(st.session_state.pokoje_sufit):
                            cc1, cc2 = st.columns([4, 1])
                            pow_p = p['dl'] * p['sz']
                            cc1.caption(f"{p['nazwa']} ({p['dl']}x{p['sz']}m) - {round(pow_p, 1)} m2 [{p['typ']}]")
                            if cc2.button("Usun", key=f"del_suf_pro_{i}"):
                                st.session_state.pokoje_sufit.pop(i)
                                st.rerun()
                        
                        # Sumowanie
                        for p in st.session_state.pokoje_sufit:
                            p_dl, p_sz = p['dl'], p['sz']
                            p_m2 = p_dl * p_sz
                            m2_gk += p_m2
                            szt_ud += int(((p_dl + p_sz) * 2 * 1.1) / 3) + 1
                            szt_wieszaki += int(p_m2 / 0.7) + 1
                            rozstaw_cd1 = 0.40 if p['typ'] == "Pojedynczy" else 1.10
                            liczba_cd1 = int(p_sz / rozstaw_cd1) + 1
                            odcinki_cd1 = int(p_dl / dl_profilu_cd)
                            szt_cd += liczba_cd1 * (odcinki_cd1 + (1 if p_dl % dl_profilu_cd > 0 else 0))
                            laczniki_cd1 += odcinki_cd1 * liczba_cd1

                            if p['typ'] == "Krzyzowy":
                                liczba_cd2 = int(p_dl / 0.40) + 1
                                odcinki_cd2 = int(p_sz / dl_profilu_cd)
                                szt_cd += liczba_cd2 * (odcinki_cd2 + (1 if p_sz % dl_profilu_cd > 0 else 0))
                                laczniki_cd2 += odcinki_cd2 * liczba_cd2
                                laczniki_krzyzowe += (liczba_cd1 * liczba_cd2)
                else:
                    # Ściana Działowa
                    c1, c2 = st.columns(2)
                    szer_sciany = c1.number_input("Dlugosc scianki (m):", min_value=0.1, value=4.0, key="wall_l_gk")
                    wys_sciany = c2.number_input("Wysokosc scianki (m):", min_value=0.1, value=2.6, key="wall_h_gk")
                    m2_gk = szer_sciany * wys_sciany
                    szer_profilu = st.selectbox("Profil scianki (CW/UW):", [50, 75, 100], format_func=lambda x: f"{x} mm", key="wall_prof_gk")
                    plytowanie = st.radio("Plytowanie:", ["1xGK (Jednostronnie)", "2xGK (Dwustronnie)", "2xGK (Z obu stron - 4 warstwy)"], key="wall_ply_gk")
                    n_drzwi = st.number_input("Otwory drzwiowe (Profil UA):", min_value=0, value=0, key="wall_d_gk")
                    szt_uw = int((szer_sciany * 2 * 1.1) / 3) + 1
                    szt_cw = int((szer_sciany / 0.6) * (wys_sciany / 3) + 1)
                    szt_ua = n_drzwi * 2

                st.markdown("---")
                st.subheader("Izolacja i Wykonczenie")
                izolacja_gk = st.checkbox("Wypelnienie welna akustyczna", key="gk_izol_pro")
                if izolacja_gk:
                    opcje_welny = [50, 75, 100, 150]
                    idx = opcje_welny.index(szer_profilu) if szer_profilu in opcje_welny else 0
                    grubosc_welny = st.selectbox("Grubosc welny:", opcje_welny, index=idx, format_func=lambda x: f"{x} mm")

                typ_tasmy = st.radio("Zbrojenie laczy:", ["Tuff-Tape (Calosc)", "Flizelina + Tuff-Tape"], key="gk_tasma_pro")
                wybrana_masa = st.selectbox("Masa do spoinowania:", list(baza_masy_gk.keys()), key="gk_masa_pro")
                stawka_gk = st.number_input("Stawka robocizny (zl/m2):", 1, 300, 110, key="gk_rob_pro")

            # --- LOGIKA MATERIAŁOWA ---
            if m2_gk > 0:
                nad = 1.10
                mnoz_p = 2 if "Dwustronnie" in plytowanie else (4 if "4 warstwy" in plytowanie else 1)
                szt_plyt = int(((m2_gk * mnoz_p) * nad) / 3.12) + 1
                wkret_25 = int(m2_gk * 20 * mnoz_p * nad)
                szt_pchelki = int(m2_gk * 12) if rodzaj_gk == "Sufit Podwieszany" else int(m2_gk * 5)

                if "Calosc" in typ_tasmy:
                    mb_tuff, mb_fliz = (m2_gk * mnoz_p * 1.5), 0
                else:
                    mb_tuff, mb_fliz = (m2_gk * mnoz_p * 0.4), (m2_gk * mnoz_p * 1.1)
                
                rolki_tuff = int(mb_tuff / 30) + (1 if mb_tuff > 0 else 0)
                rolki_fliz = int(mb_fliz / 25) + (1 if mb_fliz > 0 else 0)
                worki_masy = int((m2_gk * 0.5 * mnoz_p) / 25 + 0.99)

                koszt_plyt = szt_plyt * baza_mat_gk["Plyta GK 12.5mm (szt)"]
                koszt_profile = (szt_cd * baza_mat_gk["Profil CD60 (3mb)"]) + (szt_ud * baza_mat_gk["Profil UD27 (3mb)"]) + \
                                (szt_cw * baza_mat_gk.get(f"Profil CW{szer_profilu} (3mb)", 0)) + \
                                (szt_uw * baza_mat_gk.get(f"Profil UW{szer_profilu} (3mb)", 0)) + \
                                (szt_ua * baza_mat_gk.get(f"Profil UA{szer_profilu} (3mb)", 0))
                
                total_material = koszt_plyt + koszt_profile + (szt_wieszaki * 1.5) + (m2_gk * 16 if izolacja_gk else 0) + \
                                 (worki_masy * baza_masy_gk[wybrana_masa]) + (rolki_tuff * 150) + (rolki_fliz * 20) + (m2_gk * 15)
                robocizna = m2_gk * stawka_gk

                # Lista zakupów
                if rodzaj_gk == "Sufit Podwieszany":
                    lista_z.append(("Profile CD60 (3m)", f"{szt_cd} szt."))
                    lista_z.append(("Profile UD27 (3m)", f"{szt_ud} szt."))
                    lista_z.append(("Wieszaki ES/Obrotowe", f"{szt_wieszaki} szt."))
                else:
                    lista_z.append((f"Profile CW{szer_profilu} (3m)", f"{szt_cw} szt."))
                    lista_z.append((f"Profile UW{szer_profilu} (3m)", f"{szt_uw} szt."))
                
                lista_z.append(("Plyty G-K 12.5mm", f"{szt_plyt} szt."))
                lista_z.append(("Wkrety TN25", f"{int(wkret_25/1000)+1} op."))
                lista_z.append((f"Masa ({wybrana_masa})", f"{worki_masy} szt."))

            with col_g2:
                st.subheader("Podsumowanie")
                st.success(f"### RAZEM: **{round(total_material + robocizna)} PLN**")
                c_r1, c_r2 = st.columns(2)
                c_r1.metric("Robocizna", f"{round(robocizna)} PLN")
                c_r2.metric("Materialy", f"{round(total_material)} PLN")
                
                st.markdown("---")
                st.subheader("Lista zakupow")
                if m2_gk > 0:
                    for poz, ilosc in lista_z:
                        st.write(f"• **{poz}:** {ilosc}")
                else:
                    st.info("Dodaj metraz, aby wygenerowac zestawienie.")
                
                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import base64
                    import os

                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="gk_pdf_btn_pro"):
                        if m2_gk > 0:
                            pdf = FPDF()
                            pdf.add_page()
                            f_path = "Inter-Regular.ttf"
                            if os.path.exists(f_path):
                                pdf.add_font("Inter", "", f_path)
                                pdf.set_font("Inter", size=12)
                            else:
                                pdf.set_font("Arial", size=12)
                            
                            pdf.set_font(pdf.font_family, size=16)
                            pdf.cell(0, 15, "OFERTA: SYSTEMY G-K (PRO)", ln=True, align='C')
                            pdf.ln(5)
                            pdf.set_fill_color(245, 245, 245)
                            pdf.cell(95, 10, " Metraz calkowity:", 1)
                            pdf.cell(95, 10, f" {round(m2_gk, 1)} m2", 1, 1)
                            pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                            pdf.cell(95, 12, f" {round(total_material + robocizna)} PLN", 1, 1, 'L', True)
                            pdf.ln(10)
                            pdf.set_font(pdf.font_family, size=12)
                            pdf.cell(0, 10, "LISTA MATERIALOWA:", ln=True)
                            pdf.set_font(pdf.font_family, size=10)
                            for poz, ilosc in lista_z:
                                pdf.cell(0, 7, f"- {czysc_tekst(poz)}: {czysc_tekst(ilosc)}", ln=True)

                            pdf_bytes = pdf.output(dest="S").encode('latin-1')
                            pdf_b64 = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Oferta_GK.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz Raport PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Problem z PDF: {e}")
            
# --- SEKCJA: ELEKTRYKA ---
elif branza == "Elektryka":
    st.header("Instalacja Elektryczna (Mieszkanie)")
    
    col_e1, col_e2 = st.columns([1, 1.2])

    # --- KONFIGURACJA MAREK OSPRZĘTU (Zaktualizowane) ---
    opcje_osprzetu = {
        "Ekonomiczny (np. Simon 10, Adelid)": 15,
        "Standard (np. Simon 54, Legrand Niloe)": 45,
        "Premium (np. Berker R.1, Jung, Gira)": 110
    }

    with col_e1:
        st.subheader("Parametry instalacji")
        m2_mieszkania = st.number_input("Metraz mieszkania (m2):", min_value=10, value=60)
        mnoznik_m2 = m2_mieszkania / 60
        st.markdown("---")
        sugerowane_punkty = int(m2_mieszkania * 0.75)
        n_punktow = st.slider("Liczba punktow (gniazda/wlaczniki):", 10, 150, sugerowane_punkty) 
        typ_scian = st.radio("Material scian:", ["Gazobeton/Cegla", "Zelbet (Wielka Plyta)"])
        n_punkty_tele = 2
        wybrany_standard = st.selectbox("Marka osprzetu:", list(opcje_osprzetu.keys()), index=1)
        stawka_punkt = st.slider("Stawka montazu osprzetu (zl/szt):", 1, 100, 45)

    # --- OBLICZENIA ---
    kabel_25 = 150 * mnoznik_m2
    kabel_15 = 100 * mnoznik_m2
    kabel_4x15 = 30 * mnoznik_m2
    kabel_tv = 30 * mnoznik_m2
    kabel_lan = 50 * mnoznik_m2
    
    szt_mocowania = int((kabel_25 + kabel_15 + kabel_4x15 + kabel_tv + kabel_lan) * 3)
    paczki_mocowania = int(szt_mocowania / 100) + 1
    
    srednia_cena_szt = opcje_osprzetu[wybrany_standard]
    koszt_rozdzielnicy_mat = 1800 

    mat_kable = (kabel_25 * 5.20) + (kabel_15 * 3.80) + (kabel_4x15 * 6.50) + (kabel_tv * 2.50) + (kabel_lan * 3.00)
    mat_osprzet = n_punktow * srednia_cena_szt
    mat_mocowania = paczki_mocowania * 25.0
    
    total_material_e = mat_kable + mat_osprzet + koszt_rozdzielnicy_mat + mat_mocowania

    # ROBOCIZNA
    mnoznik_trudnosci = 1.4 if typ_scian == "Zelbet (Wielka Plyta)" else 1.0
    robocizna_baza = (m2_mieszkania * 90) # Podstawa za mb i bruzdy
    robocizna_osprzet = (n_punktow + n_punkty_tele) * stawka_punkt
    robocizna_rozdzielnica = 1500
    
    total_robocizna_e = (robocizna_baza + robocizna_osprzet + robocizna_rozdzielnica) * mnoznik_trudnosci

    # PRZYGOTOWANIE LISTY ZAKUPÓW
    lista_zakupow_ele = [
        ("Kabel 3x2.5 (Gniazda)", f"{round(kabel_25)} mb"),
        ("Kabel 3x1.5 (Swiatlo)", f"{round(kabel_15)} mb"),
        ("Kabel 4x1.5 (Schodowe/Sila)", f"{round(kabel_4x15)} mb"),
        ("Kabel antenowy RG6 (TV)", f"{round(kabel_tv)} mb"),
        ("Kabel LAN kat. 6 (Internet)", f"{round(kabel_lan)} mb"),
        ("Rozdzielnica + 10-15 bezpiecznikow (Eaton/Hager)", "1 kpl"),
        (f"Osprzet ({wybrany_standard})", f"{n_punktow} szt."),
        ("Uchwyty mocujace (paczki 100 szt.)", f"{paczki_mocowania} op."),
        ("Dodatkowe puszki/gniazda LAN/RTV", f"{n_punkty_tele} szt.")
    ]

    with col_e2:
        st.subheader("Kosztorys Elektryki")
        total_e = total_material_e + total_robocizna_e
        st.success(f"### RAZEM: **{round(total_e)} PLN**")
        
        c1, c2 = st.columns(2)
        c1.metric("Materialy", f"{round(total_material_e)} PLN")
        c2.metric("Robocizna", f"{round(total_robocizna_e)} PLN")

        st.markdown("---")
        st.subheader("Wykaz materialow do kupna")
        
        for przedmiot, ilosc in lista_zakupow_ele:
            st.write(f"• **{przedmiot}:** {ilosc}")
            
        st.markdown("---")
        st.info("UWAGA: Wycena nie uwzglednia zakupu opraw oswietleniowych (lamp). Ilosc kabla liczona szacunkowo dla instalacji prowadzonej w tynku/podlogach.")

        # --- GENERATOR PDF ELEKTRYKA ---
        try:
            from fpdf import FPDF
            from datetime import datetime
            import os

            if st.button("Generuj Kosztorys PDF", use_container_width=True, key="ele_pdf_btn"):
                pdf = FPDF()
                pdf.add_page()
                
                f_path = "Inter-Regular.ttf"
                if os.path.exists(f_path):
                    pdf.add_font("Inter", "", f_path)
                    pdf.set_font("Inter", size=12)
                else:
                    pdf.set_font("Arial", size=12)

                pdf.set_font(pdf.font_family, size=16)
                pdf.cell(0, 15, "KOSZTORYS: INSTALACJA ELEKTRYCZNA", ln=True, align='C')
                pdf.ln(5)

                pdf.set_fill_color(245, 245, 245)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(95, 10, " Kategoria", 1, 0, 'L', True)
                pdf.cell(95, 10, " Koszt", 1, 1, 'L', True)
                
                pdf.cell(95, 10, " Robocizna:", 1)
                pdf.cell(95, 10, f" {round(total_robocizna_e)} PLN", 1, 1)
                pdf.cell(95, 10, " Materialy:", 1)
                pdf.cell(95, 10, f" {round(total_material_e)} PLN", 1, 1)
                pdf.set_font(pdf.font_family, size=13)
                pdf.cell(95, 12, " SUMA CALKOWITA:", 1, 0, 'L', True)
                pdf.cell(95, 12, f" {round(total_e)} PLN", 1, 1, 'L', True)

                pdf.ln(10)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(0, 10, "SZCZEGOLY PROJEKTU:", ln=True)
                pdf.set_font(pdf.font_family, size=10)
                pdf.cell(0, 7, f"- Metraz lokalu: {m2_mieszkania} m2", ln=True)
                pdf.cell(0, 7, f"- Typ scian: {typ_scian}", ln=True)
                pdf.cell(0, 7, f"- Liczba punktow do osadzenia: {n_punktow}", ln=True)

                pdf.ln(5)
                pdf.set_font(pdf.font_family, size=12)
                pdf.cell(0, 10, "LISTA MATERIALOW DO ZAKUPU:", ln=True)
                pdf.set_font(pdf.font_family, size=10)
                for przedmiot, ilosc in lista_zakupow_ele:
                    pdf.cell(0, 7, f"- {przedmiot}: {ilosc}", ln=True)
                
                pdf.ln(5)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 7, "* Wycena nie uwzglednia zakupu lamp i opraw oswietleniowych.", ln=True)

                pdf_bytes = pdf.output()
                
                if isinstance(pdf_bytes, (bytearray, bytes)):
                    safe_bytes = bytes(pdf_bytes)
                else:
                    safe_bytes = pdf_bytes.encode('latin-1', 'replace')

                st.download_button(
                    label="Pobierz gotowy PDF",
                    data=safe_bytes,
                    file_name=f"Kosztorys_Elektryka_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Problem z generowaniem PDF: {e}")

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
                  
        
        # --- 5. GENERATOR PDF (ŁAZIENKA PRO - CZCIONKA INTER) ---
        st.markdown("---")
        if st.button("📄 Generuj Pełny Kosztorys PDF (Łazienka)"):
            try:
                from fpdf import FPDF
                from datetime import datetime
        
                # 1. NAJPIERW TWORZYMY OBIEKT PDF
                pdf = FPDF()
                pdf.add_page()
                
                # 2. REJESTRACJA CZCIONKI
                pdf.add_font('Inter', '', 'Inter-Regular.ttf', uni=True)
                
                # 3. TREŚĆ DOKUMENTU
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
        
                # 4. NA SAMYM KOŃCU GENERUJEMY WYJŚCIE
                pdf_output = pdf.output()

        # Konwersja na format akceptowany przez Streamlit (standardowe bytes)
                if isinstance(pdf_output, (bytearray, bytes)):
                    pdf_bytes = bytes(pdf_output)
                elif isinstance(pdf_output, str):
                    pdf_bytes = pdf_output.encode('latin-1', 'replace')
                else:
                    pdf_bytes = pdf_output
        
                st.download_button(
                    label="📥 Pobierz Kosztorys PDF",
                    data=pdf_bytes,
                    file_name=f"Kosztorys_Lazienka_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Błąd PDF: {e}")
               
# --- SEKCJA: DRZWI ---
elif branza == "Drzwi":
    st.header("Kalkulator Montażu Drzwi Wewnętrznych")
    
    # Baza cenowa skrzydeł (średnia rynkowa: skrzydło + ościeżnica + klamka)
    baza_drzwi = {
        "Standardowe (Przylgowe)": 1200.0,
        "Bezprzylgowe (Ukryte zawiasy)": 1900.0,
        "Rewersyjne (Otwierane do wewnątrz)": 2300.0,
        "Ukryte (System zlicowany ze ścianą)": 1600.0
    }

    tab_d1, tab_d2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_d1:
        st.subheader("Błyskawiczny szacunek kosztów")
        szt_fast = st.number_input("Liczba drzwi (kompletów):", min_value=1, value=5, step=1, key="drzwi_fast")
        typ_fast = st.radio("Standard wykończenia:", ["Zwykłe (Przylgowe)", "Premium (Bezprzylgowe/Ukryte)"])
        
        # Uproszczone stawki
        if typ_fast == "Zwykłe (Przylgowe)":
            k_drzwi_fast = szt_fast * 1200
            k_rob_fast = szt_fast * 250
            k_chem_fast = szt_fast * 50
        else:
            k_drzwi_fast = szt_fast * 1800
            k_rob_fast = szt_fast * 350
            k_chem_fast = szt_fast * 60
            
        total_fast = k_drzwi_fast + k_rob_fast + k_chem_fast
        
        st.success(f"### Szacowany całkowity koszt inwestycji: ok. {round(total_fast)} PLN")
        st.caption("Cena zawiera szacunkowy koszt zakupu drzwi, chemię montażową oraz robociznę.")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowany zakup drzwi z chemią", f"{round(k_drzwi_fast + k_chem_fast)} PLN")
        c_f2.metric("Szacowana Robocizna", f"{round(k_rob_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby doliczyć podcięcia wentylacyjne, dopłaty za szeroki mur i wygenerować PDF.")

    # ==========================================
    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_d2:
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True):
                    st.session_state.przekierowanie = True  # Ustawiamy flagę
                    st.rerun()  # Wymuszamy przeładowanie kodu od góry
        
        else:
            # --- TUTAJKOD WYKONUJE SIĘ TYLKO DLA ZALOGOWANYCH ---
            col_d1, col_d2 = st.columns([1, 1.2])

            with col_d1:
                st.subheader("Parametry zamówienia")
                szt_drzwi = st.number_input("Liczba kompletów (skrzydło + ościeżnica):", min_value=1, value=5, key="drzwi_pro")
                
                wybrany_model = st.selectbox(
                    "Model i standard drzwi:", 
                    options=list(baza_drzwi.keys())
                )
                
                szerokosc_muru = st.radio("Szerokość muru (zakres):", ["Standard (do 140mm)", "Szeroki (powyżej 140mm)"])
                
                st.markdown("---")
                st.write("**Usługi dodatkowe**")
                podciecie = st.checkbox("Podcięcie wentylacyjne (np. do łazienki/pralni)")
                demontaz = st.checkbox("Demontaż starych ościeżnic")
                
                st.markdown("---")
                # Dynamiczna stawka domyślna w zależności od stopnia skomplikowania
                if "Ukryte" in wybrany_model or "Rewersyjne" in wybrany_model:
                    domyslna_stawka = 380
                elif "Bezprzylgowe" in wybrany_model:
                    domyslna_stawka = 320
                else:
                    domyslna_stawka = 250
                    
                stawka_montazu = st.number_input("Bazowa stawka za montaż 1 kpl. (zł):", 100, 1000, domyslna_stawka)

            # --- LOGIKA OBLICZEŃ (WCIĘTA!) ---
            cena_jednostkowa = baza_drzwi[wybrany_model]
            koszt_samych_drzwi = szt_drzwi * cena_jednostkowa
            
            ilosc_pianki = szt_drzwi 
            ilosc_akrylu = int(szt_drzwi / 2 + 0.99)
            ilosc_klinow = int(szt_drzwi / 3 + 0.99)
            
            koszt_chemii = (ilosc_pianki * 45) + (ilosc_akrylu * 20) + (ilosc_klinow * 35)
            
            info_zakup = [
                (f"Drzwi wewnętrzne ({wybrany_model})", f"{szt_drzwi} kpl."),
                ("Pianka montażowa niskoprężna", f"{ilosc_pianki} szt."),
                ("Akryl malarski (do opasek)", f"{ilosc_akrylu} szt."),
                ("Kliny montażowe tworzywowe", f"{ilosc_klinow} opk.")
            ]
            
            total_materialy = koszt_samych_drzwi + koszt_chemii
            
            doplata_szeroki = 50 if szerokosc_muru == "Szeroki (powyżej 140mm)" else 0
            doplata_podciecie = 35 if podciecie else 0
            doplata_demontaz = 120 if demontaz else 0
            
            robocizna_jednostkowa = stawka_montazu + doplata_szeroki + doplata_podciecie + doplata_demontaz
            total_robocizna = szt_drzwi * robocizna_jednostkowa

            with col_d2:
                st.subheader("Podsumowanie Kosztorysu")
                suma_calkowita = total_materialy + total_robocizna
                
                st.success(f"### KOSZT CAŁKOWITY: **{round(suma_calkowita)} PLN**")
                st.caption("Cena obejmuje zakup drzwi, chemię montażową oraz robociznę.")

                c1, c2 = st.columns(2)
                c1.metric("Materiał (Drzwi + Chemia)", f"{round(total_materialy)} PLN")
                c2.metric("Robocizna", f"{round(total_robocizna)} PLN")

                st.markdown("---")
                st.subheader("Lista materiałowa do zamówienia")
                
                for nazwa, ilosc in info_zakup:
                    st.write(f"• **{nazwa}:** {ilosc}")
                
                st.markdown("---")
                st.write("**Szczegóły robocizny (za 1 komplet):**")
                st.write(f"- Montaż bazowy: {stawka_montazu} PLN")
                if doplata_szeroki > 0: st.write(f"- Dopłata za szeroki mur: {doplata_szeroki} PLN")
                if doplata_podciecie > 0: st.write(f"- Podcięcie wentylacyjne: {doplata_podciecie} PLN")
                if doplata_demontaz > 0: st.write(f"- Demontaż starych drzwi: {doplata_demontaz} PLN")
                st.write(f"**Łącznie za 1 sztukę: {robocizna_jednostkowa} PLN**")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="drzwi_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: STOLARKA DRZWIOWA", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        pdf.cell(95, 10, " Liczba kompletów:", 1)
                        pdf.cell(95, 10, f" {szt_drzwi} szt.", 1, 1)
                        pdf.cell(95, 10, " Model drzwi:", 1)
                        pdf.cell(95, 10, f" {wybrany_model.split(' (')[0]}", 1, 1)
                        pdf.cell(95, 10, " Szerokość muru:", 1)
                        pdf.cell(95, 10, f" {szerokosc_muru}", 1, 1)

                        pdf.ln(10)
                        
                        pdf.cell(95, 10, " Robocizna (Montaż całości):", 1)
                        pdf.cell(95, 10, f" {round(total_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Koszt zakupu drzwi (szacunek):", 1)
                        pdf.cell(95, 10, f" {round(koszt_samych_drzwi)} PLN", 1, 1)
                        pdf.cell(95, 10, " Chemia i akcesoria:", 1)
                        pdf.cell(95, 10, f" {round(koszt_chemii)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " ŁĄCZNY KOSZT INWESTYCJI:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_calkowita)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA ZAKUPÓW:", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        for nazwa, ilosc in info_zakup:
                            pdf.cell(0, 7, f"- {nazwa}: {ilosc}", ln=True)

                        pdf_bytes = pdf.output()
                        safe_bytes = bytes(pdf_bytes) if isinstance(pdf_bytes, (bytearray, bytes)) else pdf_bytes.encode('latin-1', 'replace')

                        st.download_button(
                            label="Pobierz gotowy PDF",
                            data=safe_bytes,
                            file_name=f"Kosztorys_Drzwi_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Błąd podczas generowania PDF: {e}")

                st.markdown("---")
                st.subheader("💾 Zapisz Kosztorys w Chmurze")
                st.caption("Zapisz ten projekt, aby mieć do niego dostęp z dowolnego urządzenia.")
                
                nazwa_projektu = st.text_input("Nazwa projektu (np. Mieszkanie na Złotej 44):", key="nazwa_proj_drzwi")
                
                if st.button("Zapisz Projekt", use_container_width=True, type="primary"):
                    if not nazwa_projektu:
                        st.warning("⚠️ Podaj nazwę projektu przed zapisaniem.")
                    # --- DODANE ZABEZPIECZENIE ---
                    elif 'user_id' not in st.session_state or not st.session_state.user_id:
                        st.error("❌ Błąd krytyczny: Zgubiłeś sesję! Wyloguj się i zaloguj ponownie.")
                    # ---------------------------
                    else:
                        try:
                            # 1. Pakujemy wszystkie ważne dane
                            dane_do_zapisu = {
                                "szt_drzwi": szt_drzwi,
                                "wybrany_model": wybrany_model,
                                "szerokosc_muru": szerokosc_muru,
                                "podciecie": podciecie,
                                "demontaz": demontaz,
                                "koszt_materialow": total_materialy,
                                "koszt_robocizny": total_robocizna,
                                "suma_calkowita": suma_calkowita
                            }
                            
                            # 2. Wysyłamy paczkę do bazy Supabase
                            response = supabase.table("projekty").insert({
                                "user_id": st.session_state.user_id, 
                                "nazwa_projektu": nazwa_projektu,
                                "branza": "Drzwi",
                                "dane_json": dane_do_zapisu
                            }).execute()
                            
                            st.success(f"✅ Projekt '{nazwa_projektu}' został bezpiecznie zapisany w chmurze!")
                        except Exception as e:
                            st.error(f"❌ Wystąpił błąd podczas zapisywania: {e}")

# --- SEKCJA: EFEKTY DEKORACYJNE ---
elif branza == "Efekty Dekoracyjne":
    st.header("Kalkulator Efektów Dekoracyjnych")
    
    # Baza cenowa PRO (Podział na Efekt -> Marka/Półka cenowa)
    baza_dekoracji_pro = {
        "Beton architektoniczny": {
            "Jeger (Market - 1 warstwa)": {"mat": 50.0, "rob": 130.0},
            "Fox Dekorator (Profesjonalny - 2 warstwy)": {"mat": 85.0, "rob": 160.0},
            "Oikos (Premium Włoski)": {"mat": 140.0, "rob": 200.0}
        },
        "Stiuk wenecki": {
            "Magnat Style (Akrylowy)": {"mat": 60.0, "rob": 160.0},
            "Fox Dekorator (Wapienny Klasyczny)": {"mat": 95.0, "rob": 200.0},
            "San Marco (Premium - Prawdziwy marmur)": {"mat": 160.0, "rob": 250.0}
        },
        "Trawertyn": {
            "Primacol (Ekonomiczny)": {"mat": 55.0, "rob": 150.0},
            "Fox Dekorator (Profesjonalny)": {"mat": 80.0, "rob": 180.0},
            "Novacolor (Premium Włoski)": {"mat": 130.0, "rob": 220.0}
        },
        "Efekt rdzy": {
            "Jeger (Szybka rdza akrylowa)": {"mat": 70.0, "rob": 140.0},
            "Fox Dekorator (Prawdziwa rdza z aktywatorem)": {"mat": 110.0, "rob": 180.0}
        },
        "Farba strukturalna": {
            "Dekoral / Śnieżka (Market)": {"mat": 30.0, "rob": 80.0},
            "Fox Dekorator (Relief z piaskiem)": {"mat": 50.0, "rob": 120.0}
        }
    }

    tab_deko1, tab_deko2 = st.tabs(["Szybka Wycena", "Kosztorys PRO"])

    # ==========================================
    # TAB 1: SZYBKA WYCENA
    # ==========================================
    with tab_deko1:
        st.subheader("Błyskawiczny szacunek kosztów")
        
        c_fast1, c_fast2 = st.columns(2)
        with c_fast1:
            typ_fast = st.selectbox("Rodzaj efektu (Szybka wycena):", list(baza_dekoracji_pro.keys()), key="deko_typ_fast")
            m2_fast = st.number_input("Powierzchnia ściany (m2):", min_value=1.0, value=12.0, step=0.5, key="deko_m2_fast")
            
        # Szybka wycena bierze ŚREDNIĄ z dostępnych systemów dla danego efektu
        dostepne_systemy = baza_dekoracji_pro[typ_fast]
        srednia_mat = sum(sys["mat"] for sys in dostepne_systemy.values()) / len(dostepne_systemy)
        srednia_rob = sum(sys["rob"] for sys in dostepne_systemy.values()) / len(dostepne_systemy)
        
        k_mat_fast = m2_fast * srednia_mat
        k_rob_fast = m2_fast * srednia_rob
        total_fast = k_mat_fast + k_rob_fast
        
        st.success(f"### Szacowany całkowity koszt inwestycji: ok. {round(total_fast)} PLN")
        st.caption("Cena wyliczona na podstawie średniej rynkowej dla wybranego efektu (zawiera materiał i robociznę).")
        
        c_f1, c_f2 = st.columns(2)
        c_f1.metric("Szacowany Materiał (Średnia)", f"{round(k_mat_fast)} PLN")
        c_f2.metric("Szacowana Robocizna (Średnia)", f"{round(k_rob_fast)} PLN")
        
        st.info("Przejdź do zakładki Kosztorys PRO, aby wybrać konkretnego producenta (np. Fox, Oikos) i wygenerować PDF.")

    # ==========================================
    # TAB 2: KOSZTORYS PRO
    # ==========================================
    with tab_deko2:
        if not st.session_state.zalogowany or st.session_state.pakiet != "PRO":
            st.error("🔒 **Dostęp zablokowany**")
            _, col_k, _ = st.columns([1, 2, 1])
            with col_k:
                if st.button("Odblokuj dostęp (Przejdź do logowania)", use_container_width=True, key="btn_odblokuj_deko"):
                    st.session_state.przekierowanie = True  
                    st.rerun()  
        else:
            # --- TYLKO DLA ZALOGOWANYCH ---
            col_d1, col_d2 = st.columns([1, 1.2])

            with col_d1:
                st.subheader("Parametry zlecenia")
                m2_pro = st.number_input("Dokładna powierzchnia (m2):", min_value=1.0, value=12.0, step=0.1, key="deko_m2_pro")
                
                wybrany_efekt = st.selectbox(
                    "1. Wybierz rodzaj efektu:", 
                    options=list(baza_dekoracji_pro.keys()),
                    key="deko_typ_pro"
                )
                
                # Zależny dropdown - pokazuje marki tylko dla wybranego efektu
                wybrana_marka = st.selectbox(
                    "2. System / Producent:", 
                    options=list(baza_dekoracji_pro[wybrany_efekt].keys()),
                    key="deko_marka_pro"
                )
                
                st.markdown("---")
                st.write("**Stawki (PLN/m2)**")
                # Zaciągamy stawki dla KONKRETNEJ marki
                cena_mat_m2 = st.number_input("Koszt materiału za m2 (zł):", min_value=10.0, value=baza_dekoracji_pro[wybrany_efekt][wybrana_marka]["mat"])
                cena_rob_m2 = st.number_input("Stawka za wykonanie 1 m2 (zł):", min_value=50.0, value=baza_dekoracji_pro[wybrany_efekt][wybrana_marka]["rob"])

                st.markdown("---")
                st.write("**Usługi dodatkowe**")
                przygotowanie = st.checkbox("Wzmocnienie ściany (siatka + klej)")
                zabezpieczenie = st.checkbox("Dodatkowa warstwa wosku/lakieru (strefy mokre)")

            # --- LOGIKA OBLICZEŃ ---
            koszt_bazowy_mat = m2_pro * cena_mat_m2
            koszt_bazowy_rob = m2_pro * cena_rob_m2
            
            doplata_mat_dodatki = 0
            doplata_rob_dodatki = 0
            
            if przygotowanie:
                doplata_mat_dodatki += (m2_pro * 15) 
                doplata_rob_dodatki += (m2_pro * 30)
                
            if zabezpieczenie:
                doplata_mat_dodatki += (m2_pro * 10) 
                doplata_rob_dodatki += (m2_pro * 20)

            total_materialy = koszt_bazowy_mat + doplata_mat_dodatki
            total_robocizna = koszt_bazowy_rob + doplata_rob_dodatki
            suma_calkowita = total_materialy + total_robocizna

            # Wyciągamy samą nazwę producenta do wydruku (np. z "Fox Dekorator (Profesjonalny)" robi "Fox Dekorator")
            krotka_nazwa_systemu = wybrana_marka.split(" (")[0]

            # --- GENEROWANIE LISTY ZAKUPÓW NA PODSTAWIE NORM ---
            lista_zakupow = []
            if wybrany_efekt == "Beton architektoniczny":
                lista_zakupow = [
                    (f"Tynk mineralny beton ({krotka_nazwa_systemu})", f"{round(m2_pro * 2.0, 1)} kg"),
                    (f"Grunt kwarcowy podkładowy", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Lakier zabezpieczający matowy", f"{round(m2_pro * 0.15, 1)} L")
                ]
            elif wybrany_efekt == "Stiuk wenecki":
                lista_zakupow = [
                    (f"Masa stiukowa ({krotka_nazwa_systemu})", f"{round(m2_pro * 1.0, 1)} kg"),
                    (f"Grunt sczepny / podkład", f"{round(m2_pro * 0.15, 1)} L"),
                    (f"Wosk polerski impregnujący", f"{round(m2_pro * 0.05, 1)} kg")
                ]
            elif wybrany_efekt == "Trawertyn":
                lista_zakupow = [
                    (f"Tynk trawertyn w proszku ({krotka_nazwa_systemu})", f"{round(m2_pro * 1.5, 1)} kg"),
                    (f"Grunt z piaskiem kwarcowym", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Przecierka koloryzująca / Lakier", f"{round(m2_pro * 0.15, 1)} L")
                ]
            elif wybrany_efekt == "Efekt rdzy":
                lista_zakupow = [
                    (f"Farba podkładowa z opiłkami żelaza ({krotka_nazwa_systemu})", f"{round(m2_pro * 0.3, 1)} L"),
                    (f"Aktywator rdzy (spray/pędzel)", f"{round(m2_pro * 0.2, 1)} L"),
                    (f"Lakier odcinający reakcję", f"{round(m2_pro * 0.15, 1)} L")
                ]
            else:
                lista_zakupow = [
                    (f"Farba strukturalna ({krotka_nazwa_systemu})", f"{round(m2_pro * 0.4, 1)} L"),
                    (f"Grunt szczepny pod kolor", f"{round(m2_pro * 0.2, 1)} L")
                ]
                
            if przygotowanie: lista_zakupow.append(("Klej elastyczny + siatka z włókna", f"{round(m2_pro)} m2"))
            if zabezpieczenie: lista_zakupow.append(("Dodatkowa warstwa ochronna (wosk/lakier)", f"{round(m2_pro * 0.1, 1)} L"))

            with col_d2:
                st.subheader("Podsumowanie Kosztorysu")
                
                st.success(f"### KOSZT CAŁKOWITY: **{round(suma_calkowita)} PLN**")
                st.caption(f"Wycena dla systemu: **{wybrana_marka}**")

                c1, c2 = st.columns(2)
                c1.metric("Materiał (System + Grunt)", f"{round(total_materialy)} PLN")
                c2.metric("Robocizna", f"{round(total_robocizna)} PLN")

                st.markdown("---")
                st.subheader("Wymagane materiały (Normy zużycia)")
                for nazwa, ilosc in lista_zakupow:
                    st.write(f"• **{nazwa}:** {ilosc}")

                # --- GENERATOR PDF ---
                try:
                    from fpdf import FPDF
                    from datetime import datetime
                    import os
                    import base64

                    if st.button("Generuj Kosztorys PDF", use_container_width=True, key="deko_pdf_btn"):
                        pdf = FPDF()
                        pdf.add_page()
                        
                        f_path = "Inter-Regular.ttf"
                        if os.path.exists(f_path):
                            pdf.add_font("Inter", "", f_path)
                            pdf.set_font("Inter", size=12)
                        else:
                            pdf.set_font("Arial", size=12)
                        
                        pdf.set_font(pdf.font_family, size=16)
                        pdf.cell(0, 15, "KOSZTORYS: EFEKTY DEKORACYJNE", ln=True, align='C')
                        pdf.ln(5)

                        pdf.set_fill_color(245, 245, 245)
                        pdf.set_font(pdf.font_family, size=12)
                        
                        def czysc_tekst(tekst):
                            pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                            for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                            return tekst.encode('latin-1', 'replace').decode('latin-1')

                        pdf.cell(95, 10, " Wybrany system:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(wybrany_efekt)}", 1, 1)
                        pdf.cell(95, 10, " Producent / Klasa:", 1)
                        pdf.cell(95, 10, f" {czysc_tekst(wybrana_marka)}", 1, 1)
                        pdf.cell(95, 10, " Powierzchnia sciany:", 1)
                        pdf.cell(95, 10, f" {m2_pro} m2", 1, 1)

                        pdf.ln(10)
                        pdf.cell(95, 10, " Wycena Robocizny:", 1)
                        pdf.cell(95, 10, f" {round(total_robocizna)} PLN", 1, 1)
                        pdf.cell(95, 10, " Koszt materialow (System):", 1)
                        pdf.cell(95, 10, f" {round(total_materialy)} PLN", 1, 1)
                        
                        pdf.set_font(pdf.font_family, size=13)
                        pdf.cell(95, 12, " LACZNY KOSZT INWESTYCJI:", 1, 0, 'L', True)
                        pdf.cell(95, 12, f" {round(suma_calkowita)} PLN", 1, 1, 'L', True)
                        
                        pdf.ln(10)
                        pdf.set_font(pdf.font_family, size=12)
                        pdf.cell(0, 10, "LISTA ZAKUPOW (Normy producenta):", ln=True)
                        pdf.set_font(pdf.font_family, size=10)
                        
                        for nazwa, ilosc in lista_zakupow:
                            pdf.cell(0, 7, f"- {czysc_tekst(nazwa)}: {czysc_tekst(ilosc)}", ln=True)

                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="Kosztorys_Dekoracje_{datetime.now().strftime("%Y%m%d")}.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz gotowy PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Błąd podczas generowania PDF: {e}")

                st.markdown("---")
                st.subheader("💾 Zapisz Kosztorys w Chmurze")
                st.caption("Zapisz ten projekt, aby pobrać go później w Panelu Inwestora.")
                
                nazwa_projektu = st.text_input("Nazwa projektu (np. Ściana TV - Beton Fox):", key="nazwa_proj_deko")
                
                if st.button("Zapisz Projekt", use_container_width=True, type="primary", key="btn_zapisz_deko"):
                    if not nazwa_projektu:
                        st.warning("⚠️ Podaj nazwę projektu przed zapisaniem.")
                    elif 'user_id' not in st.session_state or not st.session_state.user_id:
                        st.error("❌ Błąd krytyczny: Zgubiłeś sesję! Wyloguj się i zaloguj ponownie.")
                    else:
                        try:
                            zakupy_do_bazy = [f"{n}: {i}" for n, i in lista_zakupow]
                            
                            dane_do_zapisu = {
                                "typ_efektu": wybrany_efekt,
                                "producent": wybrana_marka,
                                "powierzchnia_m2": m2_pro,
                                "koszt_materialow": total_materialy,
                                "koszt_robocizny": total_robocizna,
                                "suma_calkowita": suma_calkowita,
                                "lista_zakupow": {"MATERIAŁY (SYSTEM)": zakupy_do_bazy}
                            }
                            
                            supabase.table("projekty").insert({
                                "user_id": st.session_state.user_id, 
                                "nazwa_projektu": nazwa_projektu,
                                "branza": "Efekty Dekoracyjne",
                                "dane_json": dane_do_zapisu
                            }).execute()
                            
                            st.success(f"✅ Projekt '{nazwa_projektu}' został bezpiecznie zapisany w chmurze!")
                        except Exception as e:
                            st.error(f"❌ Wystąpił błąd podczas zapisywania: {e}")
# ==========================================
# TUTAJ WCHODZI NASZ NOWY PANEL INWESTORA!
# ==========================================
elif branza == "Panel Inwestora":
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.zalogowany:
        st.warning("Ta sekcja dostępna jest wyłącznie dla zalogowanych użytkowników.")
        st.info("Przejdź do zakładki 'Logowanie' w górnym menu, aby założyć darmowe konto.")
    else:
        # Odpalamy Sidebar (Boczne Menu) JEDEN RAZ!
        with st.sidebar:
            st.title("Panel Zarządzania")
            st.markdown(f"Konto: **{st.session_state.user_email}**")
            
            # Dodaliśmy 'key', aby wymusić unikalność ID dla Streamlita
            opcja_panelu = st.radio(
                "Nawigacja",
                ["Nawigacja Główna", "Mój Profil", "Język i Region"],
                key="panel_inwestora_nawigacja" 
            )
            
            st.markdown("---")
            if st.button("Wyloguj (Panel)", key="btn_wyloguj_panel"):
                st.session_state.zalogowany = False
                if supabase: supabase.auth.sign_out()
                st.rerun()

# ==========================================
        # 1. ZAWARTOSC: NAWIGACJA GŁÓWNA (TWOJA LOGIKA)
        # ==========================================
        if opcja_panelu == "Nawigacja Główna":
            
            # --- A. SEKCJA CHMURY: TWOJE PROJEKTY ---
            st.header("Twoje Zapisane Kosztorysy")
            if supabase:
                try:
                    response = supabase.table("projekty").select("*").eq("user_id", st.session_state.user_id).order("data_stworzenia", desc=True).execute()
                    zapisane_projekty = response.data
                    
                    if not zapisane_projekty:
                        st.info("Nie masz jeszcze żadnych zapisanych projektów w chmurze.")
                    else:
                        st.markdown("---")
                        col_nazwa, col_data, col_pobierz, col_usun = st.columns([3.5, 1.5, 1, 1])
                        col_nazwa.markdown("**Nazwa projektu / Kategoria**")
                        col_data.markdown("**Data utworzenia**")
                        col_pobierz.markdown("**Pobierz**")
                        col_usun.markdown("**Akcja**")
                        st.markdown("---")
                        
                        for projekt in zapisane_projekty:
                            data_utworzenia = projekt['data_stworzenia'][:10] 
                            nazwa = projekt['nazwa_projektu']
                            branza_proj = projekt['branza']
                            dane = projekt['dane_json']
                            id_projektu = projekt['id']
                            
                            # --- NOWOŚĆ: Piękne formatowanie pobieranego pliku z listą materiałów ---
                            dane_txt = f"=== PROJEKT: {nazwa.upper()} ===\n"
                            dane_txt += f"DATA ZAPISU: {data_utworzenia}\nKATEGORIA: {branza_proj}\n\n"
                            dane_txt += "--- PARAMETRY FINANSOWE ---\n"
                            
                            for klucz, wartosc in dane.items():
                                if klucz == "lista_zakupow":
                                    dane_txt += "\n--- WYGENEROWANA LISTA MATERIAŁÓW ---\n"
                                    for kategoria, lista_itemow in wartosc.items():
                                        if lista_itemow:
                                            dane_txt += f"\n[{kategoria}]\n"
                                            for item in lista_itemow:
                                                dane_txt += f" - {item}\n"
                                else:
                                    # Formatowanie kluczy na bardziej czytelne
                                    czysty_klucz = klucz.replace("_", " ").title()
                                    dane_txt += f"{czysty_klucz}: {wartosc}\n"
                            
                            c1, c2, c3, c4 = st.columns([3.5, 1.5, 1, 1])
                            
                            with c1:
                                st.markdown(f"<p style='margin-top: 10px; font-weight: 600;'>{nazwa} <br><span style='color: #00D395; font-size: 12px; font-weight: normal;'>({branza_proj})</span></p>", unsafe_allow_html=True)
                            with c2:
                                st.markdown(f"<p style='margin-top: 10px; color: #6C757D;'>{data_utworzenia}</p>", unsafe_allow_html=True)
                            with c3:
                                st.download_button(
                                    label="Pobierz",
                                    data=dane_txt,
                                    file_name=f"{nazwa}.txt",
                                    mime="text/plain",
                                    key=f"dl_btn_{id_projektu}"
                                )
                            with c4:
                                if st.button("Usuń", type="primary", key=f"del_btn_{id_projektu}"):
                                    try:
                                        supabase.table("projekty").delete().eq("id", id_projektu).execute()
                                        st.rerun() 
                                    except Exception as e:
                                        st.error(f"Błąd usuwania: {e}")
                                        
                            st.markdown("<hr style='margin: 0px; opacity: 0.2;'>", unsafe_allow_html=True)
                            
                except Exception as e:
                    st.error(f"Wystąpił błąd podczas pobierania danych: {e}")
            else:
                st.error("Brak połączenia z chmurą bazy danych.")
                
            st.markdown("<br><br>", unsafe_allow_html=True)

            # --- B. SEKCJA ANALITYCZNA: CHECKLISTA ---
            st.subheader("Checklista Przedzakupowa")
            c_ch1, c_ch2, c_ch3 = st.columns(3)
            with c_ch1:
                st.checkbox("Piony wod-kan (stan żeliwa/plastiku)", key="ch_piony")
                st.checkbox("Okna (szczelność/wiek/pakiet szyb)", key="ch_okna")
            with c_ch2:
                st.checkbox("Instalacja elek. (miedź vs alu)", key="ch_elek")
                st.checkbox("Możliwość wydzielenia pokoju", key="ch_pokoje")
            with c_ch3:
                st.checkbox("KW czysta (Dział III i IV)", key="ch_kw")
                st.checkbox("Przynależność piwnicy", key="ch_piwnica")

            st.markdown("---")

            # --- C. PARAMETRY I ANALIZA ROI ---
            col_params, col_roi = st.columns([1, 1.2])

            with col_params:
                st.subheader("Parametry Lokalu")
                nazwa_inwestycji = st.text_input("Nazwa Inwestycji (do zapisu):", value="Kawalerka na Start")
                m2_total = st.number_input("Metraż mieszkania (m2):", min_value=1.0, value=50.0)
                cena_zakupu = st.number_input("Cena zakupu lokalu (PLN):", value=350000, step=5000)
                cena_sprzedazy = st.number_input("Przewidywana cena sprzedaży (PLN):", value=550000, step=5000)
                standard = st.select_slider("Standard wykończenia:", options=["Ekonomiczny", "Standard", "Premium"])
                stan_lokalu = st.radio("Stan lokalu:", ["Deweloperski", "Rynek Wtórny (Do remontu)"])

            pow_scian = m2_total * 3.5
            mnoznik_std = 0.8 if standard == "Ekonomiczny" else (1.3 if standard == "Premium" else 1.0)
            koszt_transakcyjny = (cena_zakupu * 0.02) + 4500 
            
            bazowy_remont = (m2_total * 1200 * mnoznik_std) 
            if stan_lokalu == "Rynek Wtórny (Do remontu)": bazowy_remont *= 1.25
            
            calkowity_koszt_inwestycji = cena_zakupu + koszt_transakcyjny + bazowy_remont
            zysk_brutto = cena_sprzedazy - calkowity_koszt_inwestycji
            roi = (zysk_brutto / calkowity_koszt_inwestycji) * 100 if calkowity_koszt_inwestycji > 0 else 0

            with col_roi:
                st.subheader("Analiza Zysku (Live)")
                st.markdown(f"**Całkowity koszt inwestycji:** {round(calkowity_koszt_inwestycji):,} zł".replace(",", " "))
                
                r1, r2 = st.columns(2)
                r1.metric("ZYSK BRUTTO", f"{round(zysk_brutto):,} zł".replace(",", " "))
                r2.metric("ROI %", f"{round(roi, 1)} %")
                
                st.write(f"W tym szacowany remont: {round(bazowy_remont):,} zł")
                st.write(f"Koszty transakcyjne: {round(koszt_transakcyjny):,} zł")
                
                if roi < 12:
                    st.error("Słabe ROI! Negocjuj cenę zakupu.")
                elif roi < 20:
                    st.warning("Przeciętny deal. Pilnuj kosztów ekipy.")
                else:
                    st.success("Świetny deal! Można wchodzić.")

            st.markdown("---")

            # --- D. ZAKRES PRAC I LISTA ZAKUPÓW ---
            st.subheader("Zakres prac i Lista Zakupów")
            
            c_work1, c_work2, c_work3 = st.columns(3)
            with c_work1:
                do_elektryka = st.checkbox("Nowa Elektryka", value=True)
                do_malowanie = st.checkbox("Malowanie (Biała+Kolor)", value=True)
            with c_work2:
                do_lazienka = st.checkbox("Remont Łazienki", value=True)
                do_gk = st.checkbox("Sucha Zabudowa (Sufity)", value=False)
            with c_work3:
                do_szpachlowanie = st.checkbox("Szpachlowanie / Gładzie", value=True)
                szerokosc_pom = st.number_input("Szerokość pom. (m):", value=3.5)

            zakupy = {"ELEKTRYKA": [], "ŁAZIENKA": [], "G-K / SUFITY": [], "ŚCIANY / PODŁOGI": []}

            if do_elektryka:
                zakupy["ELEKTRYKA"].extend([
                    f"Kabel 3x2.5 (Gniazda): {int(m2_total * 2.5)} mb",
                    f"Kabel 3x1.5 (Światło): {int(m2_total * 1.5)} mb",
                    "Kabel 4x1.5 (Siła/Schodowe): 25 mb",
                    "Rozdzielnica + 10 bezpieczników (Eaton/Hager)",
                    f"Osprzęt (Gniazda/Włączniki): {int(m2_total*0.8)} szt.",
                    f"Uchwyty (paczki 100 szt.): {int(m2_total/15)+1} op.",
                    "Kabel LAN kat. 6 + Antenowy RG6: po 25 mb"
                ])

            if do_lazienka:
                m2_p = 5 * 1.12 
                m2_s = 22 * 1.12
                zakupy["ŁAZIENKA"].extend([
                    f"Płytki (Podłoga + Ściany): {round(m2_p + m2_s, 1)} m2",
                    f"Klej elastyczny S1 (25kg): {int((m2_p+m2_s)/5)+1} worków",
                    "Hydroizolacja: Folia 5kg + 10mb Taśmy + 2 Mankiety",
                    "Fuga (2kg) + Silikon sanitarny: 3 + 2 szt.",
                    "Grunt pod hydroizolację: 1 szt."
                ])

            if do_gk:
                dl_prof = 4 if szerokosc_pom > 4 else 3
                zakupy["G-K / SUFITY"].extend([
                    f"Płyty GK 12.5mm: {int(m2_total/2.5)+2} szt.",
                    f"Profil CD60 ({dl_prof}mb): {int(m2_total*0.9)+4} szt.",
                    f"Profil UD27 (3mb): {int(m2_total*0.5)+2} szt.",
                    f"Wieszaki ES: {int(m2_total*1.3)} szt.",
                    "Wkręty GK 3.5x25 (1000szt) + Pchełki (250szt)",
                    "Taśma TUFF-TAPE + Flizelina + Gips Uniflott"
                ])

            if do_malowanie or do_szpachlowanie:
                if do_szpachlowanie:
                    zakupy["ŚCIANY / PODŁOGI"].append(f"Gładź szpachlowa: {int(pow_scian*1.5/20)+1} wiader")
                if do_malowanie:
                    zakupy["ŚCIANY / PODŁOGI"].extend([
                        f"Farba Biała: {int(pow_scian*0.4/8)+1} L",
                        f"Farba Kolor: {int(pow_scian*0.6/9)+1} L",
                        f"Grunt: {int(pow_scian/50)+1} baniek (5L)"
                    ])

            buy_col1, buy_col2 = st.columns(2)
            for i, (cat, items) in enumerate(zakupy.items()):
                if items:
                    target_col = buy_col1 if i % 2 == 0 else buy_col2
                    with target_col:
                        st.info(f"**{cat}**")
                        for item in items:
                            st.write(f"- {item}")

            # --- E. PODSUMOWANIE (ZAPIS DO BAZY I GENERATOR PDF) ---
            st.markdown("---")
            st.subheader("💾 Zapis i Eksport")
            
            col_save, col_pdf = st.columns(2)
            
            # NOWOŚĆ: Przycisk Zapisu widzi teraz listę 'zakupy' i wysyła ją do bazy!
            with col_save:
                if st.button("Zapisz projekt do chmury", use_container_width=True, type="primary", key="zapisz_roi_btn"):
                    if supabase and st.session_state.user_id:
                        try:
                            dane_roi = {
                                "suma_calkowita": round(calkowity_koszt_inwestycji),
                                "koszt_materialow": round(bazowy_remont),
                                "zysk_brutto": round(zysk_brutto),
                                "roi_procent": round(roi, 1),
                                "lista_zakupow": zakupy # <--- LISTA MATERIAŁÓW LECI DO BAZY!
                            }
                            supabase.table("projekty").insert({
                                "user_id": st.session_state.user_id, 
                                "nazwa_projektu": nazwa_inwestycji,
                                "branza": "Analiza ROI z Materiałami",
                                "dane_json": dane_roi
                            }).execute()
                            st.success("✅ Zapisano! Odśwież widok by zobaczyć na liście.")
                        except Exception as e:
                            st.error(f"Błąd zapisu: {e}")

            # Eksport PDF
            with col_pdf:
                if st.button("Pobierz Listę Zakupów (PDF)", use_container_width=True, key="pobierz_pdf_btn"):
                    from fpdf import FPDF
                    import base64
                    def czysc_tekst(tekst):
                        pl_znaki = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
                        for pl, ang in pl_znaki.items(): tekst = tekst.replace(pl, ang)
                        return tekst.encode('latin-1', 'replace').decode('latin-1')
                    try:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.set_text_color(0, 211, 149) 
                        pdf.cell(200, 10, txt="PROCALC - LISTA ZAKUPOWA (PANEL INWESTORA)", ln=True, align='C')
                        pdf.ln(10)
                        pdf.set_text_color(30, 30, 30)
                        for cat, items in zakupy.items():
                            if items:
                                pdf.set_font("Arial", style="B", size=12)
                                pdf.cell(200, 10, txt=f"--- {czysc_tekst(cat)} ---", ln=True)
                                pdf.set_font("Arial", size=11)
                                for item in items:
                                    pdf.cell(200, 8, txt=f"* {czysc_tekst(item)}", ln=True)
                                pdf.ln(5)
                        pdf_bytes = pdf.output(dest="S").encode('latin-1')
                        pdf_b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="ProCalc_{nazwa_inwestycji}.pdf" style="display: block; text-align: center; padding: 15px; background-color: #00D395; color: white; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">Pobierz PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Błąd PDF: {e}")

import base64

# Funkcja generująca link do PDF w formacie Base64
def create_pdf_link(file_path, link_name):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # Dodany atrybut download wymusza bezpieczne zapisanie pliku
        return f'<a href="data:application/pdf;base64,{base64_pdf}" download="{file_path}" style="text-decoration:none; color:#6C757D;">{link_name}</a>'
    except Exception:
        return f'<span style="color:#e74c3c;">{link_name} (Brak pliku)</span>'
        
# Przygotowanie linków
link_reg = create_pdf_link("Regulamin_ProCalc_v1.pdf", "Regulamin serwisu")
link_rodo = create_pdf_link("Polityka_Prywatnosci_ProCalc_v2.pdf", "Polityka prywatności (RODO)")

# Wyświetlenie stopki
st.markdown(f"""
    <hr style="border:0; height:1px; background-image:linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.1), rgba(255,255,255,0)); margin-top:50px;">
    <div style="text-align:center; padding:20px; color:#6C757D; font-family:sans-serif; font-size:14px;">
        <p>© 2026 ProCalc. Wszystkie prawa zastrzeżone.</p>
        <p>
            {link_reg} &nbsp; | &nbsp; {link_rodo} &nbsp; | &nbsp; 
            <a href="mailto:biuro@procalc.pl" style="text-decoration:none; color:#6C757D;">Kontakt</a>
        </p>
    </div>
""", unsafe_allow_html=True)


